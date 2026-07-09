#!/usr/bin/env bash
# =============================================================================
# Dotfiles installer
# Usage: bash install.sh [--dry-run]
# =============================================================================
set -euo pipefail

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DRY_RUN=false

for arg in "$@"; do
  [[ "$arg" == "--dry-run" ]] && DRY_RUN=true
done

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
    run sudo apt-get update -qq
    run sudo apt-get install -y "${packages[@]}"
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
# 2. Symlink dotfiles
# =============================================================================
link_file() {
  local src="$1"
  local dest="$2"

  if [[ -e "$dest" && ! -L "$dest" ]]; then
    warn "Backing up existing $dest → ${dest}.bak"
    run mv "$dest" "${dest}.bak"
  fi

  if [[ -L "$dest" && "$(readlink "$dest")" == "$src" ]]; then
    success "Already linked: $dest"
    return
  fi

  info "Linking $dest → $src"
  run ln -sf "$src" "$dest"
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
  local zshrc="$HOME/.zshrc"
  local marker='source "$HOME/.zshrc.core"'

  if [[ -L "$zshrc" ]]; then
    warn "Removing legacy symlink at $zshrc"
    run rm "$zshrc"
  fi

  if [[ ! -e "$zshrc" ]]; then
    info "Creating $zshrc loader"
    run bash -c "printf '%s\n' '$marker' > '$zshrc'"
    return
  fi

  if grep -qF "$marker" "$zshrc" 2>/dev/null; then
    success "$zshrc already sources .zshrc.core"
    return
  fi

  info "Prepending loader line to existing $zshrc"
  run bash -c "printf '%s\n\n%s\n' '$marker' \"\$(cat '$zshrc')\" > '$zshrc.tmp' && mv '$zshrc.tmp' '$zshrc'"
}

# Symlink Claude Code config individually — never symlink all of ~/.claude,
# which also holds runtime data (sessions, cache, tokens, auto-memory).
symlink_claude() {
  run mkdir -p "$HOME/.claude"
  link_file "$DOTFILES_DIR/.claude/settings.json" "$HOME/.claude/settings.json"
  link_file "$DOTFILES_DIR/.claude/CLAUDE.md"     "$HOME/.claude/CLAUDE.md"
  link_file "$DOTFILES_DIR/.claude/statusline.sh" "$HOME/.claude/statusline.sh"
  link_file "$DOTFILES_DIR/.claude/commands"      "$HOME/.claude/commands"
  link_file "$DOTFILES_DIR/.claude/agents"        "$HOME/.claude/agents"
  link_file "$DOTFILES_DIR/.claude/output-styles" "$HOME/.claude/output-styles"
}

# =============================================================================
# 3. Set zsh as the default shell
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
# 4. Bootstrap antidote (plugin manager)
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

  install_packages
  symlink_dotfiles
  ensure_zshrc_loader
  symlink_claude
  set_default_shell
  install_antidote

  echo ""
  success "Done! Start a new zsh session to load everything."
  info "On first launch, antidote will clone all plugins (takes ~10s)."
  info "Tip: ~/.zshrc is untracked — machine-specific lines (installer PATH appends, etc.) belong there."
  echo ""
}

main "$@"
