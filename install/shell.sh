symlink_dotfiles() {
  link_file "$DOTFILES_DIR/.zshrc"           "$HOME/.zshrc.core"
  link_file "$DOTFILES_DIR/.zsh_plugins.txt" "$HOME/.zsh_plugins.txt"
  link_file "$DOTFILES_DIR/.gitconfig"       "$HOME/.gitconfig"
}

# Keep ~/.zshrc untracked so other installers can append PATH and init lines.
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

# Set zsh as the default shell
set_default_shell() {
  local zsh_path
  zsh_path="$(command -v zsh || true)"

  if [[ -z "$zsh_path" ]]; then
    if $DRY_RUN; then
      info "Changing default shell to zsh after installation (dry-run)"
      return
    fi
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
  $DRY_RUN || success "Default shell set to $zsh_path — re-login to apply"
}

# Bootstrap antidote
install_antidote() {
  local antidote_dir="${XDG_DATA_HOME:-$HOME/.local/share}/antidote"

  if [[ -d "$antidote_dir" ]]; then
    success "antidote already installed at $antidote_dir"
    return
  fi

  info "Installing antidote plugin manager"
  run git clone --depth=1 https://github.com/mattmc3/antidote.git "$antidote_dir"
}
