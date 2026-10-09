#!/usr/bin/env bash
# Dotfiles installer
# Usage: bash install.sh [--dry-run] [--agents-only] [--tools=claude,codex,opencode,copilot,gemini,amp,grok]
set -euo pipefail

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DRY_RUN=false
AGENTS_ONLY=false
PREVIEW_MIGRATIONS=()
TOOLS=claude,grok
PACKAGE_MANAGER=""

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
    claude|codex|opencode|copilot|gemini|amp|grok) ;;
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
GROK_DIR="${GROK_HOME:-$HOME/.grok}"

source "$DOTFILES_DIR/install/common.sh"
source "$DOTFILES_DIR/install/agent-config.sh"
source "$DOTFILES_DIR/install/packages.sh"
source "$DOTFILES_DIR/install/shell.sh"

source "$DOTFILES_DIR/install/agents.sh"

# Main
main() {
  echo ""
  echo "  Dotfiles installer"
  echo "  =================="
  $DRY_RUN && warn "Dry-run mode — no changes will be made"
  echo ""

  if ! $AGENTS_ONLY; then
    select_package_manager
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
  if $DRY_RUN; then
    success "Dry run complete."
    return
  fi
  success "Done! Agent configuration installed."
  $AGENTS_ONLY && return
  info "Start a new zsh session to load everything."
  info "On first launch, antidote will clone all plugins (takes ~10s)."
  info "Tip: ~/.zshrc is untracked — machine-specific lines (installer PATH appends, etc.) belong there."
  echo ""
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  main "$@"
fi
