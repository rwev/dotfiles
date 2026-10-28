#!/usr/bin/env bash
# Dotfiles installer
# Usage: bash install.sh [--dry-run] [--packages] [--pretty] [--zshrc] [--git] [--agents] [--shell] [--antidote] [--agents-only] [--tools=claude,opencode,copilot,grok]
set -euo pipefail

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DRY_RUN=false
AGENTS_ONLY=false
TOOLS_GIVEN=false
PREVIEW_MIGRATIONS=()
TOOLS=claude,grok
PACKAGE_MANAGER=""
RUN_PACKAGES=false
RUN_PRETTY=false
RUN_ZSHRC=false
RUN_GIT=false
RUN_AGENTS=false
RUN_SHELL=false
RUN_ANTIDOTE=false
MODULE_SELECTED=false

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    --agents-only) AGENTS_ONLY=true; RUN_AGENTS=true; MODULE_SELECTED=true ;;
    --tools=*) TOOLS="${arg#--tools=}"; TOOLS_GIVEN=true ;;
    --packages) RUN_PACKAGES=true; MODULE_SELECTED=true ;;
    --pretty) RUN_PRETTY=true; MODULE_SELECTED=true ;;
    --zshrc) RUN_ZSHRC=true; MODULE_SELECTED=true ;;
    --git) RUN_GIT=true; MODULE_SELECTED=true ;;
    --agents) RUN_AGENTS=true; MODULE_SELECTED=true ;;
    --shell) RUN_SHELL=true; MODULE_SELECTED=true ;;
    --antidote) RUN_ANTIDOTE=true; MODULE_SELECTED=true ;;
    *) printf 'Unknown argument: %s\n' "$arg" >&2; exit 1 ;;
  esac
done

if ! $MODULE_SELECTED; then
  RUN_PACKAGES=true
  RUN_PRETTY=true
  RUN_ZSHRC=true
  RUN_GIT=true
  RUN_AGENTS=true
  RUN_SHELL=true
  RUN_ANTIDOTE=true
fi

if $AGENTS_ONLY; then
  if $RUN_PACKAGES || $RUN_PRETTY || $RUN_ZSHRC || $RUN_GIT || $RUN_SHELL || $RUN_ANTIDOTE; then
    printf '%s\n' '--agents-only cannot be combined with other module flags' >&2
    exit 1
  fi
fi

if $RUN_AGENTS || $TOOLS_GIVEN; then
  [[ -n "$TOOLS" && "$TOOLS" != ,* && "$TOOLS" != *, && "$TOOLS" != *,,* ]] || {
    printf 'Invalid tool list: %s\n' "$TOOLS" >&2; exit 1;
  }
  IFS=, read -r -a SELECTED_TOOLS <<< "$TOOLS"
  for tool in "${SELECTED_TOOLS[@]}"; do
    case "$tool" in
      claude|opencode|copilot|grok) ;;
      universal) [[ "$TOOLS" == universal ]] || { printf 'universal must be used alone\n' >&2; exit 1; } ;;
      *) printf 'Unknown tool: %s\n' "$tool" >&2; exit 1 ;;
    esac
  done
fi

if $TOOLS_GIVEN && ! $RUN_AGENTS; then
  printf '%s\n' '--tools requires the agents module' >&2
  exit 1
fi

CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
COPILOT_DIR="${COPILOT_HOME:-$HOME/.copilot}"
OPENCODE_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/opencode"
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

  if $RUN_PACKAGES || $RUN_PRETTY; then
    select_package_manager
  fi
  if $RUN_PACKAGES; then
    install_packages
  fi
  if $RUN_PRETTY; then
    install_pretty_print_tools
  fi
  if $RUN_ZSHRC; then
    link_zshrc_files
    ensure_zshrc_loader
  fi
  if $RUN_GIT; then
    link_gitconfig
  fi
  if $RUN_AGENTS; then
    install_agents
  fi
  if $RUN_SHELL; then
    set_default_shell
  fi
  if $RUN_ANTIDOTE; then
    install_antidote
  fi

  local modules=""
  if $RUN_PACKAGES; then modules+="${modules:+, }packages"; fi
  if $RUN_PRETTY; then modules+="${modules:+, }pretty"; fi
  if $RUN_ZSHRC; then modules+="${modules:+, }zshrc"; fi
  if $RUN_GIT; then modules+="${modules:+, }git"; fi
  if $RUN_AGENTS; then modules+="${modules:+, }agents"; fi
  if $RUN_SHELL; then modules+="${modules:+, }shell"; fi
  if $RUN_ANTIDOTE; then modules+="${modules:+, }antidote"; fi

  echo ""
  if $DRY_RUN; then
    info "Would install modules: $modules"
    success "Dry run complete."
    return
  fi
  success "Installed modules: $modules"
  if $RUN_AGENTS; then
    success "Done! Agent configuration installed."
  else
    success "Done."
  fi
  if $RUN_ZSHRC; then
    info "Start a new zsh session to load everything."
    info "On first launch, antidote will clone all plugins (takes ~10s)."
    info "Tip: ~/.zshrc is untracked — machine-specific lines (installer PATH appends, etc.) belong there."
    echo ""
  fi
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  main "$@"
fi
