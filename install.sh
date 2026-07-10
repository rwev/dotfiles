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

# Merge a tracked JSON config with whatever real, machine-local JSON already
# lives at dest, instead of symlinking over it — same idea as ~/.zshrc
# sourcing .zshrc.core, but merged at install time since JSON has no
# "source". local_override always wins on conflicting keys; the tracked file
# fills in anything it doesn't set. dest ends up a plain generated file,
# never a symlink.
merge_json_file() {
  local dotfiles_src="$1"
  local dest="$2"
  local local_override="$3"

  run mkdir -p "$(dirname "$dest")"

  # Old-style direct symlink from a prior install.sh: drop it so the capture
  # check below can't mistake the tracked file's own content, read through
  # the symlink, for machine-local customization.
  if [[ -L "$dest" ]]; then
    info "Removing old symlink at $dest"
    run rm "$dest"
  fi

  # First run only: capture whatever real content is already there as the
  # machine-local baseline, before it gets replaced by a generated file.
  if [[ -e "$dest" && ! -e "$local_override" ]]; then
    info "Preserving existing $dest → $local_override"
    run cp "$dest" "$local_override"
  fi

  [[ -e "$local_override" ]] || run bash -c "echo '{}' > '$local_override'"
  jq empty "$local_override" 2>/dev/null || run bash -c "echo '{}' > '$local_override'"

  info "Merging $dotfiles_src + $local_override → $dest"
  run bash -c "jq -s '.[0] * .[1]' '$dotfiles_src' '$local_override' > '$dest.tmp' && mv '$dest.tmp' '$dest'"
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
  merge_json_file "$DOTFILES_DIR/.claude/settings.json" "$HOME/.claude/settings.json" "$HOME/.claude/settings.local.json"
  link_file "$DOTFILES_DIR/.claude/CLAUDE.md"     "$HOME/.claude/CLAUDE.md"
  link_file "$DOTFILES_DIR/.claude/statusline.sh" "$HOME/.claude/statusline.sh"
  link_file "$DOTFILES_DIR/.claude/commands"      "$HOME/.claude/commands"
  link_file "$DOTFILES_DIR/.claude/agents"        "$HOME/.claude/agents"
  link_file "$DOTFILES_DIR/.claude/output-styles" "$HOME/.claude/output-styles"
}

# Symlink OpenCode config, reusing Claude Code's tracked config where the
# schemas line up (rules file, /my:* commands) and adding OpenCode-native
# files only where the frontmatter schema genuinely differs (agents).
symlink_opencode() {
  run mkdir -p "$HOME/.config/opencode/command"
  link_file "$DOTFILES_DIR/.claude/CLAUDE.md"       "$HOME/.config/opencode/AGENTS.md"
  merge_json_file "$DOTFILES_DIR/.opencode/opencode.json" "$HOME/.config/opencode/opencode.json" "$HOME/.config/opencode/opencode.local.json"
  link_file "$DOTFILES_DIR/.opencode/agents"        "$HOME/.config/opencode/agents"
  link_file "$DOTFILES_DIR/.claude/commands/my"     "$HOME/.config/opencode/command/my"
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
  symlink_opencode
  set_default_shell
  install_antidote

  echo ""
  success "Done! Start a new zsh session to load everything."
  info "On first launch, antidote will clone all plugins (takes ~10s)."
  info "Tip: ~/.zshrc is untracked — machine-specific lines (installer PATH appends, etc.) belong there."
  echo ""
}

main "$@"
