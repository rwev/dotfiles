# Native JSON overrides stay local. Invalid input is backed up, not discarded.
json_is_object() {
  jq -e -s 'length == 1 and (.[0] | type == "object")' "$@" >/dev/null 2>&1
}

merge_json_file() {
  local dotfiles_src="$1" dest="$2" local_override="$3" kind="${4:-}" tmp captured="" status_command=""
  ensure_directory "$(dirname "$dest")"
  if $DRY_RUN; then
    info "Merging $dotfiles_src + $local_override → $dest"
    return
  fi
  if ! json_is_object "$dotfiles_src"; then
    error "Expected one JSON object in $dotfiles_src"
    return 1
  fi
  if [[ -L "$dest" ]]; then
    if [[ "$(readlink "$dest")" != "$dotfiles_src" && -f "$dest" ]]; then
      captured="$(cat "$dest")"
    fi
  elif [[ -f "$dest" && ! -e "$local_override" && ! -L "$local_override" ]]; then
    captured="$(cat "$dest")"
  fi
  if [[ -L "$local_override" ]]; then
    [[ ! -f "$local_override" ]] || captured="$(cat "$local_override")"
    backup_file "$local_override"
  fi
  if [[ ! -e "$local_override" ]]; then
    tmp="$(mktemp "${local_override}.tmp.XXXXXX")"
    printf '%s\n' "${captured:-\{\}}" > "$tmp"
    mv "$tmp" "$local_override"
  elif [[ -n "$captured" ]]; then
    # Preserve both sources when an override already exists.
    tmp="$(mktemp "${local_override}.tmp.XXXXXX")"
    if printf '%s' "$captured" | json_is_object && json_is_object "$local_override"; then
      if ! printf '%s' "$captured" | jq --slurpfile local "$local_override" '. * $local[0]' > "$tmp"; then
        rm "$tmp"
        return 1
      fi
      mv "$tmp" "$local_override" || { rm "$tmp"; return 1; }
    else
      rm "$tmp"
    fi
  fi
  if ! json_is_object "$local_override"; then
    backup_file "$local_override"
    tmp="$(mktemp "${local_override}.tmp.XXXXXX")"
    printf '{}\n' > "$tmp"
    mv "$tmp" "$local_override"
  fi
  if [[ "$kind" == opencode ]]; then
    tmp="$(mktemp "${local_override}.tmp.XXXXXX")"
    if ! jq 'if (.instructions | type) == "array" then .instructions |= map(if . == "~/.claude/output-styles/my-humble-servant.md" then "~/.agents/personas/my-humble-servant.md" else . end) else . end' "$local_override" > "$tmp"; then
      rm "$tmp"
      return 1
    fi
    mv "$tmp" "$local_override" || { rm "$tmp"; return 1; }
  fi
  if [[ "$kind" == claude && "$CLAUDE_DIR" != "$HOME/.claude" ]]; then
    printf -v status_command '%q' "$CLAUDE_DIR/statusline.sh"
  fi
  tmp="$(mktemp "${dest}.tmp.XXXXXX")"
  if ! jq -s --arg command "$status_command" 'if $command != "" then .[0].statusLine.command = $command else . end | .[0] * .[1]' "$dotfiles_src" "$local_override" > "$tmp"; then
    rm "$tmp"
    return 1
  fi
  if [[ ! -L "$dest" && -f "$dest" ]] && cmp -s "$tmp" "$dest"; then
    rm "$tmp"
  else
    if [[ -e "$dest" || -L "$dest" ]]; then
      backup_file "$dest" || { rm "$tmp"; return 1; }
    fi
    mv "$tmp" "$dest" || { rm "$tmp"; return 1; }
  fi
}

# Add tracked Codex defaults without replacing values written by Codex itself
# (for example, /model, /theme, and /statusline choices).
codex_config_has_key() {
  local file="$1" section="$2" key="$3"
  awk -v wanted_section="$section" -v wanted_key="$key" '
    /^[[:space:]]*\[[^]]+\]/ {
      section = $0
      sub(/^[[:space:]]*\[/, "", section)
      sub(/\].*$/, "", section)
      next
    }
    section == wanted_section && $0 ~ "^[[:space:]]*" wanted_key "[[:space:]]*=" { found = 1; exit }
    END { exit !found }
  ' "$file"
}

codex_insert_default() {
  DOTFILES_TOML_DEFAULT="$3" awk -v section="$2" '
    BEGIN { line = ENVIRON["DOTFILES_TOML_DEFAULT"] }
    /^[[:space:]]*\[[^]]+\][[:space:]]*(#.*)?$/ {
      table = $0
      sub(/^[[:space:]]*\[/, "", table)
      sub(/\].*$/, "", table)
      if (section == "" && !added) { print line; added = 1 }
      if (section != "" && inside && table != section) { print line; inside = 0 }
      if (section != "" && table == section) { inside = 1; found = 1 }
    }
    { print }
    END {
      if (section == "" && !added) print line
      if (section != "" && inside) print line
      if (section != "" && !found) {
        print ""
        print "[" section "]"
        print line
      }
    }
  ' "$1"
}

install_codex_config() {
  local dest="${1:-$HOME/.codex/config.toml}"
  local src="$DOTFILES_DIR/.codex/config.toml"
  local section="" key line tmp

  ensure_directory "$(dirname "$dest")"
  if [[ -L "$dest" ]] && ! $DRY_RUN; then
    local saved=""
    [[ ! -f "$dest" ]] || saved="$(cat "$dest")"
    backup_file "$dest"
    [[ -z "$saved" ]] || printf '%s\n' "$saved" > "$dest"
  fi
  if [[ ! -e "$dest" ]]; then
    info "Installing $dest"
    run cp "$src" "$dest"
    return
  fi

  while IFS= read -r line; do
    if [[ "$line" =~ ^\[([a-z_]+)\]$ ]]; then
      section="${BASH_REMATCH[1]}"
      continue
    fi
    [[ "$line" =~ ^([a-z_]+)[[:space:]]*= ]] || continue
    key="${BASH_REMATCH[1]}"
    codex_config_has_key "$dest" "$section" "$key" && continue
    if [[ "$key" == sandbox_mode ]] && codex_config_has_key "$dest" "" default_permissions; then
      continue
    fi

    local setting_name="$key"
    [[ -z "$section" ]] || setting_name="$section.$key"
    info "Adding Codex default $setting_name to $dest"
    if $DRY_RUN; then
      continue
    fi
    tmp="$(mktemp "${dest}.tmp.XXXXXX")"
    if ! codex_insert_default "$dest" "$section" "$line" > "$tmp"; then
      rm "$tmp"
      return 1
    fi
    mv "$tmp" "$dest"
  done < "$src"
}

# The bare-table helpers cannot safely merge alternate TOML forms.
grok_config_can_add_defaults() {
  awk '
    FNR == NR {
      if ($0 ~ /^\[[a-z_][a-z_0-9.]*\]$/) {
        table = substr($0, 2, length($0) - 2)
        defaults[table] = 1
      }
      next
    }
    /^[[:space:]]*\[/ {
      if ($0 !~ /^[[:space:]]*\[[a-z_][a-z_0-9]*(\.[a-z_][a-z_0-9]*)*\][[:space:]]*(#.*)?$/) unsafe = 1
      section = $0
      sub(/^[[:space:]]*\[/, "", section)
      sub(/\].*$/, "", section)
      next
    }
    /"""|\047\047\047/ { unsafe = 1 }
    /^[^=]*["\047][^=]*=/ { unsafe = 1 }
    /^[[:space:]]*[a-z_][a-z_0-9.[:space:]]*=/ {
      key = $0
      sub(/=.*/, "", key)
      gsub(/[[:space:]]/, "", key)
      if (index(key, ".")) unsafe = 1
      value = $0
      sub(/^[^=]*=[[:space:]]*/, "", value)
      if (value ~ /^\{/) unsafe = 1
      path = section == "" ? key : section "." key
      for (table in defaults) {
        if (path == table || index(table, path ".") == 1) unsafe = 1
      }
    }
    END { exit unsafe }
  ' "$2" "$1"
}

install_grok_config() {
  local dest="$1" src="$DOTFILES_DIR/.grok/config.toml" tmp section="" key line continuation status_command="" command_path
  if [[ "$GROK_DIR" != "$HOME/.grok" ]]; then
    command_path="$GROK_DIR/statusline.sh"
    command_path="${command_path//\'/\'\\\'\'}"
    status_command="$(printf "'%s'" "$command_path" | jq -Rs .)" || return
  fi
  ensure_directory "$(dirname "$dest")"
  if [[ ! -e "$dest" && ! -L "$dest" ]]; then
    info "Installing $dest"
    if [[ -z "$status_command" ]]; then
      run cp "$src" "$dest"
    elif ! $DRY_RUN; then
      tmp="$(mktemp "${dest}.tmp.XXXXXX")" || return
      if ! GROK_STATUS_COMMAND="$status_command" awk '
        $0 == "command = \"~/.grok/statusline.sh\"" { print "command = " ENVIRON["GROK_STATUS_COMMAND"]; next }
        { print }
      ' "$src" > "$tmp"; then
        rm "$tmp"
        return 1
      fi
      mv "$tmp" "$dest" || { rm "$tmp"; return 1; }
    fi
    return
  fi
  [[ -f "$dest" ]] || { error "Not a config file: $dest"; return 1; }
  if ! grok_config_can_add_defaults "$dest" "$src"; then
    warn "Preserving alternate Grok TOML syntax; add missing tracked defaults locally"
    return
  fi
  while IFS= read -r line; do
    if [[ "$line" =~ ^\[([a-z_][a-z_0-9.]*)\]$ ]]; then
      section="${BASH_REMATCH[1]}"
      continue
    fi
    [[ "$line" =~ ^([a-z_][a-z_0-9]*)[[:space:]]*= ]] || continue
    key="${BASH_REMATCH[1]}"
    if [[ "$line" =~ =[[:space:]]*\[[[:space:]]*$ ]]; then
      while IFS= read -r continuation; do
        line+=$'\n'"$continuation"
        [[ "$continuation" =~ ^[[:space:]]*\][[:space:]]*$ ]] && break
      done
    fi
    codex_config_has_key "$dest" "$section" "$key" && continue
    if [[ "$section" == ui.status_line && "$key" == command && -n "$status_command" ]]; then
      line="command = $status_command"
    fi
    info "Adding Grok default $section.$key to $dest"
    $DRY_RUN && continue
    tmp="$(mktemp "${dest}.tmp.XXXXXX")"
    if ! codex_insert_default "$dest" "$section" "$line" > "$tmp"; then
      rm "$tmp"
      return 1
    fi
    if [[ -L "$dest" ]]; then
      backup_file "$dest" || { rm "$tmp"; return 1; }
    fi
    mv "$tmp" "$dest" || { rm "$tmp"; return 1; }
  done < "$src"
}
