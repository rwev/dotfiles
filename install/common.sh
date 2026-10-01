info()    { printf '\e[1;34m[info]\e[0m  %s\n' "$*"; }
success() { printf '\e[1;32m[ok]\e[0m    %s\n' "$*"; }
warn()    { printf '\e[1;33m[warn]\e[0m  %s\n' "$*"; }
error()   { printf '\e[1;31m[error]\e[0m %s\n' "$*" >&2; }
run()     { $DRY_RUN && echo "  (dry-run) $*" || "$@"; }

# File and directory operations
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
