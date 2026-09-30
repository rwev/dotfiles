#!/usr/bin/env bash
# =============================================================================
# Dotfiles installer
# Usage: bash install.sh [--dry-run] [--agents-only] [--tools=claude,codex,opencode,copilot]
# =============================================================================
set -euo pipefail

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DRY_RUN=false
AGENTS_ONLY=false
PREVIEW_MIGRATIONS=()
TOOLS=claude,codex,opencode,copilot

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    --agents-only) AGENTS_ONLY=true ;;
    --tools=*) TOOLS="${arg#--tools=}" ;;
    *) printf 'Unknown argument: %s\n' "$arg" >&2; exit 1 ;;
  esac
done
[[ -n "$TOOLS" && "$TOOLS" != ,* && "$TOOLS" != *, && "$TOOLS" != *,,* ]] || {
  printf 'Invalid tool list: %s\n' "$TOOLS" >&2; exit 1;
}
IFS=, read -r -a SELECTED_TOOLS <<< "$TOOLS"
for tool in "${SELECTED_TOOLS[@]}"; do
  case "$tool" in
    claude|codex|opencode|copilot|gemini|amp) ;;
    universal) [[ "$TOOLS" == universal ]] || { printf 'universal must be used alone\n' >&2; exit 1; } ;;
    *) printf 'Unknown tool: %s\n' "$tool" >&2; exit 1 ;;
  esac
done
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
CODEX_DIR="${CODEX_HOME:-$HOME/.codex}"
COPILOT_DIR="${COPILOT_HOME:-$HOME/.copilot}"
OPENCODE_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/opencode"
AMP_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/amp"
GEMINI_DIR="${GEMINI_CLI_HOME:-$HOME}/.gemini"

info()    { printf '\e[1;34m[info]\e[0m  %s\n' "$*"; }
success() { printf '\e[1;32m[ok]\e[0m    %s\n' "$*"; }
warn()    { printf '\e[1;33m[warn]\e[0m  %s\n' "$*"; }
error()   { printf '\e[1;31m[error]\e[0m %s\n' "$*" >&2; }
run()     { $DRY_RUN && echo "  (dry-run) $*" || "$@"; }

# =============================================================================
# 1. Install zsh and fzf
# =============================================================================
install_packages() {
  local packages=()

  command -v zsh &>/dev/null  || packages+=(zsh)
  command -v fzf &>/dev/null  || packages+=(fzf)
  command -v git &>/dev/null  || packages+=(git)
  command -v jq  &>/dev/null  || packages+=(jq)   # used by the Claude Code statusline

  if [[ ${#packages[@]} -eq 0 ]]; then
    success "zsh, fzf, git, and jq are already installed"
    return
  fi

  info "Installing: ${packages[*]}"
  if command -v apt-get &>/dev/null; then
    run sudo apt-get update -qq || warn "apt-get update failed — attempting install anyway"
    run sudo apt-get install -y "${packages[@]}" || {
      error "apt-get install failed — you may need to fix APT repository config or install packages manually"
      exit 1
    }
  elif command -v brew &>/dev/null; then
    run brew install "${packages[@]}"
  elif command -v dnf &>/dev/null; then
    run sudo dnf install -y "${packages[@]}"
  elif command -v pacman &>/dev/null; then
    run sudo pacman -S --noconfirm "${packages[@]}"
  else
    error "No supported package manager found. Install zsh, fzf, git, and jq manually."
    exit 1
  fi
}

# =============================================================================
# 2. Install pretty-print tools (nice-to-have; failures warn, not fatal)
# =============================================================================
install_pretty_print_tools() {
  local packages=()

  command -v bat &>/dev/null || command -v batcat &>/dev/null || packages+=(bat)

  if [[ ${#packages[@]} -eq 0 ]]; then
    success "bat already installed"
  else
    info "Installing: ${packages[*]}"
    if command -v apt-get &>/dev/null; then
      run sudo apt-get install -y "${packages[@]}" || warn "Failed to install ${packages[*]} — install manually if wanted"
    elif command -v brew &>/dev/null; then
      run brew install "${packages[@]}"
    elif command -v dnf &>/dev/null; then
      run sudo dnf install -y "${packages[@]}" || warn "Failed to install ${packages[*]} — install manually if wanted"
    elif command -v pacman &>/dev/null; then
      run sudo pacman -S --noconfirm "${packages[@]}" || warn "Failed to install ${packages[*]} — install manually if wanted"
    else
      warn "No supported package manager found — install bat manually if wanted"
    fi
  fi

  if command -v glow &>/dev/null; then
    success "glow already installed"
    return
  fi

  info "Installing glow (markdown renderer)"
  if command -v brew &>/dev/null; then
    run brew install glow
  elif command -v pacman &>/dev/null; then
    run sudo pacman -S --noconfirm glow || warn "Failed to install glow — install manually: https://github.com/charmbracelet/glow"
  elif command -v dnf &>/dev/null; then
    run sudo dnf install -y glow || warn "glow not found via dnf — install manually: https://github.com/charmbracelet/glow"
  elif command -v snap &>/dev/null; then
    # Not in Debian/Ubuntu's apt archives; Charm ships it via snap instead.
    run sudo snap install glow || warn "Failed to install glow via snap — install manually: https://github.com/charmbracelet/glow"
  else
    warn "glow not available via a supported package manager — install manually: https://github.com/charmbracelet/glow"
  fi
}

# =============================================================================
# 3. Symlink dotfiles
# =============================================================================
# Keep backups collision-safe, including dangling links.
backup_file() {
  local dest="$1" backup="${1}.bak" backup_base index=1
  if [[ "$(basename "$(dirname "$dest")")" == skills ]]; then
    # A backup inside skills is still discoverable. Keep it outside that tree.
    backup="$HOME/.agents/backups/skills/$(basename "$dest").bak"
    ensure_directory "$(dirname "$backup")"
  fi
  backup_base="$backup"
  while [[ -e "$backup" || -L "$backup" ]]; do
    backup="${backup_base}.$index"
    index=$((index + 1))
  done
  warn "Preserving $dest → $backup"
  run mv "$dest" "$backup"
}

# Only migrate directory links created by this installer. Never write through
# an unknown directory link, including links in parent directories.
ensure_directory() {
  local dest="$1" legacy="${2:-}" entry name migration
  if [[ -L "$dest" ]]; then
    if $DRY_RUN; then
      for migration in "${PREVIEW_MIGRATIONS[@]}"; do
        [[ "$migration" != "$dest" ]] || return 0
      done
    fi
    if [[ -z "$legacy" || "$(readlink "$dest")" != "$legacy" ]]; then
      error "Refusing to write through directory symlink: $dest"
      return 1
    fi
    if $DRY_RUN; then
      info "Migrating managed directory link $dest"
      PREVIEW_MIGRATIONS+=("$dest")
      return
    fi
    backup_file "$dest"
    mkdir "$dest"
    for entry in "$legacy"/* "$legacy"/.[!.]* "$legacy"/..?*; do
      [[ -e "$entry" || -L "$entry" ]] || continue
      name="$(basename "$entry")"
      case "$legacy" in
        "$DOTFILES_DIR/.claude/skills")
          [[ -d "$DOTFILES_DIR/.agents/skills/$name" ]] && continue ;;
        "$DOTFILES_DIR/.claude/agents"|"$DOTFILES_DIR/.opencode/agents")
          [[ -f "$DOTFILES_DIR/.agents/agents/$name" ]] && continue ;;
        "$DOTFILES_DIR/.claude/output-styles")
          [[ "$name" == my-humble-servant.md ]] && continue ;;
      esac
      ln -s "$entry" "$dest/$name"
    done
    return
  fi
  [[ ! -e "$dest" || -d "$dest" ]] || { error "Not a directory: $dest"; return 1; }
  [[ "$dest" == / || "$dest" == . ]] && return
  ensure_directory "$(dirname "$dest")"
  run mkdir -p "$dest"
}

link_file() {
  local src="$1" dest="$2"
  if [[ -L "$dest" && "$(readlink "$dest")" == "$src" ]]; then
    success "Already linked: $dest"
    return
  fi
  ensure_directory "$(dirname "$dest")"
  [[ ! -e "$dest" && ! -L "$dest" ]] || backup_file "$dest"
  info "Linking $dest → $src"
  run ln -s "$src" "$dest"
}

# Native JSON overrides stay local. Invalid input is backed up, not discarded.
merge_json_file() {
  local dotfiles_src="$1" dest="$2" local_override="$3" kind="${4:-}" base tmp captured=""
  ensure_directory "$(dirname "$dest")"
  if $DRY_RUN; then
    info "Merging $dotfiles_src + $local_override → $dest"
    return
  fi
  if [[ -L "$dest" ]]; then
    if [[ "$(readlink "$dest")" != "$dotfiles_src" && -f "$dest" ]]; then
      captured="$(cat "$dest")"
    fi
    backup_file "$dest"
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
    if printf '%s' "$captured" | jq -e -s 'length == 1 and (.[0] | type == "object")' >/dev/null 2>&1 && jq -e -s 'length == 1 and (.[0] | type == "object")' "$local_override" >/dev/null 2>&1; then
      printf '%s' "$captured" | jq --slurpfile local "$local_override" '. * $local[0]' > "$tmp"
      mv "$tmp" "$local_override"
    else
      rm "$tmp"
    fi
  fi
  if ! jq -e -s 'length == 1 and (.[0] | type == "object")' "$local_override" >/dev/null 2>&1; then
    backup_file "$local_override"
    tmp="$(mktemp "${local_override}.tmp.XXXXXX")"
    printf '{}\n' > "$tmp"
    mv "$tmp" "$local_override"
  fi
  if [[ "$kind" == opencode ]]; then
    tmp="$(mktemp "${local_override}.tmp.XXXXXX")"
    jq 'if (.instructions | type) == "array" then .instructions |= map(if . == "~/.claude/output-styles/my-humble-servant.md" then "~/.agents/personas/my-humble-servant.md" else . end) else . end' "$local_override" > "$tmp"
    mv "$tmp" "$local_override"
  fi
  base="$(mktemp "${dest}.base.XXXXXX")"
  if [[ "$kind" == claude && "$CLAUDE_DIR" != "$HOME/.claude" ]]; then
    local status_command
    printf -v status_command '%q' "$CLAUDE_DIR/statusline.sh"
    jq --arg command "$status_command" '.statusLine.command = $command' "$dotfiles_src" > "$base"
  else
    cp "$dotfiles_src" "$base"
  fi
  tmp="$(mktemp "${dest}.tmp.XXXXXX")"
  jq -s '.[0] * .[1]' "$base" "$local_override" > "$tmp"
  rm "$base"
  if [[ -f "$dest" ]] && cmp -s "$tmp" "$dest"; then
    rm "$tmp"
  else
    [[ ! -e "$dest" && ! -L "$dest" ]] || backup_file "$dest"
    mv "$tmp" "$dest"
  fi
}

symlink_dotfiles() {
  link_file "$DOTFILES_DIR/.zshrc"           "$HOME/.zshrc.core"
  link_file "$DOTFILES_DIR/.zsh_plugins.txt" "$HOME/.zsh_plugins.txt"
  link_file "$DOTFILES_DIR/.gitconfig"       "$HOME/.gitconfig"
}

# ~/.zshrc is left as a real (untracked) file that sources .zshrc.core.
# Installers universally append PATH/init lines to ~/.zshrc by convention —
# keeping it untracked means that churn never touches the repo.
ensure_zshrc_loader() {
  local zshrc="$HOME/.zshrc" tmp
  local marker='source "$HOME/.zshrc.core"'

  if [[ -L "$zshrc" ]]; then
    backup_file "$zshrc"
  fi
  if [[ -f "$zshrc" ]] && grep -qF "$marker" "$zshrc"; then
    success "$zshrc already sources .zshrc.core"
    return
  fi
  info "Adding loader line to $zshrc"
  $DRY_RUN && return
  tmp="$(mktemp "${zshrc}.tmp.XXXXXX")"
  {
    printf '%s\n' "$marker"
    if [[ -f "$zshrc" ]]; then
      printf '\n'
      cat "$zshrc"
    fi
  } > "$tmp"
  mv "$tmp" "$zshrc"
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
    if [[ -z "$section" ]]; then
      awk -v new_line="$line" '
        /^\[/ && !added { print new_line; added = 1 }
        { print }
        END { if (!added) print new_line }
      ' "$dest" > "$tmp"
    elif grep -q "^\[$section\]$" "$dest"; then
      awk -v header="[$section]" -v new_line="$line" '
        $0 == header { in_section = 1 }
        in_section && /^\[/ && $0 != header { print new_line; in_section = 0 }
        { print }
        END { if (in_section) print new_line }
      ' "$dest" > "$tmp"
    else
      { cat "$dest"; printf '\n[%s]\n%s\n' "$section" "$line"; } > "$tmp"
    fi
    mv "$tmp" "$dest"
  done < "$src"
}

markdown_body() {
  awk 'NR == 1 && $0 == "---" { front = 1; next } front && $0 == "---" { front = 0; next } !front { print }' "$1"
}

preserve_generated_destination() {
  local dest="$1" legacy="${2:-}"
  if [[ -L "$dest" ]]; then
    if [[ -n "$legacy" && "$(readlink "$dest")" == "$legacy" ]]; then
      run rm "$dest"
    else
      backup_file "$dest"
    fi
  elif [[ -e "$dest" ]] && ! grep -q -e '^<!-- Generated by dotfiles/install.sh -->$' -e '^# Generated by dotfiles/install.sh$' "$dest"; then
    backup_file "$dest"
  fi
}

install_instructions() {
  local dest="$1" persona="$2" optional="${3:-false}" local_override="${1%.md}.local.md" old="" tmp
  ensure_directory "$(dirname "$dest")"
  if $DRY_RUN; then
    info "Generating $dest from neutral rules"
    return
  fi
  # These links pointed at tracked rules, not personal overrides.
  if [[ -L "$dest" && ( "$(readlink "$dest")" == "$DOTFILES_DIR/.claude/CLAUDE.md" || "$(readlink "$dest")" == "$DOTFILES_DIR/.agents/AGENTS.md" ) ]]; then
    rm "$dest"
  elif [[ -f "$dest" ]] && ! grep -q '^<!-- Generated by dotfiles/install.sh -->$' "$dest"; then
    old="$(cat "$dest")"
    backup_file "$dest"
  elif [[ -d "$dest" || -L "$dest" ]]; then
    backup_file "$dest"
  fi
  if [[ -d "$local_override" ]]; then
    backup_file "$local_override"
  fi
  if [[ -n "$old" ]]; then
    tmp="$(mktemp "${local_override}.tmp.XXXXXX")"
    [[ ! -f "$local_override" ]] || cat "$local_override" > "$tmp"
    printf '\n%s\n' "$old" >> "$tmp"
    [[ ! -L "$local_override" ]] || backup_file "$local_override"
    mv "$tmp" "$local_override"
  fi
  tmp="$(mktemp "${dest}.tmp.XXXXXX")"
  {
    printf '<!-- Generated by dotfiles/install.sh -->\n\n'
    cat "$DOTFILES_DIR/.agents/AGENTS.md"
    if [[ "$persona" == true ]]; then
      printf '\n'
      cat "$DOTFILES_DIR/.agents/personas/my-humble-servant.md"
    fi
    if [[ "$optional" == true ]]; then
      printf '\n## Unsupported workflows\n\n'
      printf 'This adapter does not install specialist roles. Do not run my-build or\nmy-security without their required specialist roles. Run my-plan only when\nthe harness provides independent exploration subagents.\n'
    fi
    if [[ -f "$local_override" ]]; then
      printf '\n'
      cat "$local_override"
    fi
  } > "$tmp"
  mv "$tmp" "$dest"
}

install_native_agents() {
  local harness="$1" dir="$2" src name dest template description tmp
  case "$harness" in
    claude) ensure_directory "$dir" "$DOTFILES_DIR/.claude/agents" ;;
    opencode) ensure_directory "$dir" "$DOTFILES_DIR/.opencode/agents" ;;
    *) ensure_directory "$dir" ;;
  esac
  for src in "$DOTFILES_DIR"/.agents/agents/_my-*.md; do
    name="$(basename "$src" .md)"
    template=""
    case "$harness" in
      claude|opencode) dest="$dir/$name.md"; template="$DOTFILES_DIR/.$harness/templates/agents/$name.md" ;;
      copilot) dest="$dir/$name.agent.md"; template="$DOTFILES_DIR/.copilot/agents/$name.agent.md" ;;
      codex) dest="$dir/$name.toml" ;;
    esac
    if $DRY_RUN; then
      info "Generating $dest from $src"
      continue
    fi
    preserve_generated_destination "$dest" "$template"
    tmp="$(mktemp "${dest}.tmp.XXXXXX")"
    if [[ "$harness" == codex ]]; then
      description="$(sed -n 's/^description: //p' "$src" | head -n 1)"
      {
        printf '# Generated by dotfiles/install.sh\n'
        printf 'name = %s\n' "$(printf '%s' "$name" | jq -Rs .)"
        printf 'description = %s\n' "$(printf '%s' "$description" | jq -Rs .)"
        [[ "$name" == _my-implementer ]] || printf 'sandbox_mode = "read-only"\n'
        printf 'developer_instructions = %s\n' "$(markdown_body "$src" | jq -Rs .)"
      } > "$tmp"
    else
      {
        cat "$template"
        printf '\n<!-- Generated by dotfiles/install.sh -->\n\n'
        markdown_body "$src"
      } > "$tmp"
    fi
    mv "$tmp" "$dest"
  done
}

install_shared_agents() {
  local skill src tmp dest="$HOME/.agents/exports/default.md"
  ensure_directory "$HOME/.agents"
  link_file "$DOTFILES_DIR/.agents/AGENTS.md" "$HOME/.agents/AGENTS.md"
  ensure_directory "$HOME/.agents/personas"
  link_file "$DOTFILES_DIR/.agents/personas/my-humble-servant.md" "$HOME/.agents/personas/my-humble-servant.md"
  ensure_directory "$HOME/.agents/agents"
  for src in "$DOTFILES_DIR"/.agents/agents/_my-*.md; do
    link_file "$src" "$HOME/.agents/agents/$(basename "$src")"
  done
  ensure_directory "$HOME/.agents/skills"
  for skill in "$DOTFILES_DIR"/.agents/skills/my-*; do
    link_file "$skill" "$HOME/.agents/skills/$(basename "$skill")"
  done
  ensure_directory "$HOME/.agents/exports"
  if $DRY_RUN; then
    info "Generating manual export $dest"
    return
  fi
  preserve_generated_destination "$dest"
  tmp="$(mktemp "${dest}.tmp.XXXXXX")"
  {
    printf '<!-- Generated by dotfiles/install.sh -->\n\n'
    cat "$DOTFILES_DIR/.agents/AGENTS.md"
    printf '\n'
    cat "$DOTFILES_DIR/.agents/personas/my-humble-servant.md"
    printf '\n## Skills\n\nLoad each skill file explicitly if the harness has no native skill discovery.\n\n'
    for skill in "$DOTFILES_DIR"/.agents/skills/my-*; do
      printf -- '- `%s`: `%s/SKILL.md`' "$(basename "$skill")" "$HOME/.agents/skills/$(basename "$skill")"
      case "$(basename "$skill")" in
        my-build) printf ' — requires implementation and review subagents with specialist roles.' ;;
        my-security) printf ' — requires an independent read-only security-reviewer role.' ;;
        my-plan) printf ' — requires independent exploration subagents.' ;;
      esac
      printf '\n'
    done
  } > "$tmp"
  mv "$tmp" "$dest"
}

install_claude() {
  local skill dest="$CLAUDE_DIR/output-styles/my-humble-servant.md" tmp
  ensure_directory "$CLAUDE_DIR"
  merge_json_file "$DOTFILES_DIR/.claude/settings.json" "$CLAUDE_DIR/settings.json" "$CLAUDE_DIR/settings.local.json" claude
  install_instructions "$CLAUDE_DIR/CLAUDE.md" false
  link_file "$DOTFILES_DIR/.claude/statusline.sh" "$CLAUDE_DIR/statusline.sh"
  ensure_directory "$CLAUDE_DIR/skills" "$DOTFILES_DIR/.claude/skills"
  for skill in "$DOTFILES_DIR"/.agents/skills/my-*; do
    link_file "$skill" "$CLAUDE_DIR/skills/$(basename "$skill")"
  done
  install_native_agents claude "$CLAUDE_DIR/agents"
  ensure_directory "$CLAUDE_DIR/output-styles" "$DOTFILES_DIR/.claude/output-styles"
  if $DRY_RUN; then
    info "Generating $dest"
    return
  fi
  preserve_generated_destination "$dest" "$DOTFILES_DIR/.claude/templates/output-styles/my-humble-servant.md"
  tmp="$(mktemp "${dest}.tmp.XXXXXX")"
  {
    cat "$DOTFILES_DIR/.claude/templates/output-styles/my-humble-servant.md"
    printf '\n<!-- Generated by dotfiles/install.sh -->\n\n'
    cat "$DOTFILES_DIR/.agents/personas/my-humble-servant.md"
  } > "$tmp"
  mv "$tmp" "$dest"
}

install_opencode() {
  ensure_directory "$OPENCODE_DIR"
  install_instructions "$OPENCODE_DIR/AGENTS.md" false
  merge_json_file "$DOTFILES_DIR/.opencode/opencode.json" "$OPENCODE_DIR/opencode.json" "$OPENCODE_DIR/opencode.local.json" opencode
  install_native_agents opencode "$OPENCODE_DIR/agents"
}

install_codex() {
  ensure_directory "$CODEX_DIR"
  install_codex_config "$CODEX_DIR/config.toml"
  install_instructions "$CODEX_DIR/AGENTS.md" true
  install_native_agents codex "$CODEX_DIR/agents"
}

install_copilot() {
  ensure_directory "$COPILOT_DIR"
  install_instructions "$COPILOT_DIR/copilot-instructions.md" true
  install_native_agents copilot "$COPILOT_DIR/agents"
}

install_optional() {
  local tool="$1" dir="$2" file="$3" skill
  ensure_directory "$dir"
  install_instructions "$dir/$file" true true
  if [[ "$tool" == gemini && "$GEMINI_DIR" != "$HOME/.gemini" ]]; then
    ensure_directory "$dir/skills"
    for skill in "$DOTFILES_DIR"/.agents/skills/my-*; do
      link_file "$skill" "$dir/skills/$(basename "$skill")"
    done
  fi
}

install_agents() {
  local tool
  command -v jq &>/dev/null || { error "jq is required for agent installation"; return 1; }
  install_shared_agents
  for tool in "${SELECTED_TOOLS[@]}"; do
    case "$tool" in
      claude) install_claude ;;
      codex) install_codex ;;
      opencode) install_opencode ;;
      copilot) install_copilot ;;
      gemini) install_optional gemini "$GEMINI_DIR" GEMINI.md ;;
      amp) install_optional amp "$AMP_DIR" AGENTS.md ;;
    esac
  done
}

# =============================================================================
# 4. Set zsh as the default shell
# =============================================================================
set_default_shell() {
  local zsh_path
  zsh_path="$(command -v zsh)"

  if [[ -z "$zsh_path" ]]; then
    error "zsh not found in PATH after install — cannot set as default shell"
    exit 1
  fi

  # Add to /etc/shells if missing
  if ! grep -qxF "$zsh_path" /etc/shells 2>/dev/null; then
    info "Adding $zsh_path to /etc/shells"
    run sudo sh -c "echo '$zsh_path' >> /etc/shells"
  fi

  if [[ "$SHELL" == "$zsh_path" ]]; then
    success "Default shell is already zsh ($zsh_path)"
    return
  fi

  info "Changing default shell to $zsh_path (will prompt for password)"
  run chsh -s "$zsh_path"
  success "Default shell set to $zsh_path — re-login to apply"
}

# =============================================================================
# 5. Bootstrap antidote (plugin manager)
# =============================================================================
install_antidote() {
  local antidote_dir="${XDG_DATA_HOME:-$HOME/.local/share}/antidote"

  if [[ -d "$antidote_dir" ]]; then
    success "antidote already installed at $antidote_dir"
    return
  fi

  info "Installing antidote plugin manager"
  run git clone --depth=1 https://github.com/mattmc3/antidote.git "$antidote_dir"
}

# =============================================================================
# Main
# =============================================================================
main() {
  echo ""
  echo "  Dotfiles installer"
  echo "  =================="
  $DRY_RUN && warn "Dry-run mode — no changes will be made"
  echo ""

  if ! $AGENTS_ONLY; then
    install_packages
    install_pretty_print_tools
    symlink_dotfiles
    ensure_zshrc_loader
  fi
  install_agents
  if ! $AGENTS_ONLY; then
    set_default_shell
    install_antidote
  fi

  echo ""
  success "Done! Agent configuration installed."
  $AGENTS_ONLY && return
  info "Start a new zsh session to load everything."
  info "On first launch, antidote will clone all plugins (takes ~10s)."
  info "Tip: ~/.zshrc is untracked — machine-specific lines (installer PATH appends, etc.) belong there."
  echo ""
}

main "$@"
