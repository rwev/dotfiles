#!/usr/bin/env bash
# Dotfiles installer
# Usage: bash install.sh --help
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

# Module flags, in run order: flag:variable:help. The parser and --help both
# read this list.
MODULES=(
  "packages:RUN_PACKAGES:Install zsh, fzf, git, jq, and other missing packages"
  "pretty:RUN_PRETTY:Install pretty-print tools"
  "zshrc:RUN_ZSHRC:Link zsh config files and add the ~/.zshrc loader"
  "git:RUN_GIT:Link the git config"
  "agents:RUN_AGENTS:Install agent rules, skills, and roles for --tools harnesses"
  "shell:RUN_SHELL:Set zsh as the default login shell"
  "antidote:RUN_ANTIDOTE:Clone the antidote zsh plugin manager"
)

usage() {
  local entry name
  cat <<'USAGE'
Usage: bash install.sh [options] [module flags]

With no module flags, all modules run. With module flags, only those run,
always in the order below.

Module flags:
USAGE
  for entry in "${MODULES[@]}"; do
    name="${entry%%:*}"
    entry="${entry#*:}"
    printf '  --%-16s %s\n' "$name" "${entry#*:}"
  done
  cat <<'USAGE'

Options:
  --agents-only      Run only the agents module. Use with no other module flag.
  --tools=LIST       Agent harnesses, comma-separated: claude, opencode,
                     copilot, grok. Default: claude,grok. Use "universal"
                     alone for the shared ~/.agents layer only. Needs the
                     agents module.
  --dry-run          Print what would change. Change nothing.
  -h, --help         Show this help and exit.

Environment:
  HOME               Install target for links and config.
  CLAUDE_CONFIG_DIR  Claude config dir (default: $HOME/.claude).
  COPILOT_HOME       Copilot config dir (default: $HOME/.copilot).
  XDG_CONFIG_HOME    OpenCode config is $XDG_CONFIG_HOME/opencode
                     (default: $HOME/.config/opencode).
  GROK_HOME          Grok config dir (default: $HOME/.grok).
  XDG_DATA_HOME      antidote dir is $XDG_DATA_HOME/antidote
                     (default: $HOME/.local/share/antidote).
  SHELL              The shell module skips chsh if this is already zsh.

Examples:
  bash install.sh --dry-run
  bash install.sh --git --zshrc
  bash install.sh --agents-only
  bash install.sh --agents --tools=claude,opencode,copilot,grok
USAGE
}

select_module() {
  local entry var
  for entry in "${MODULES[@]}"; do
    if [[ "$1" == "${entry%%:*}" ]]; then
      var="${entry#*:}"
      printf -v "${var%%:*}" true
      MODULE_SELECTED=true
      return 0
    fi
  done
  return 1
}

for arg in "$@"; do
  case "$arg" in
    -h|--help) usage; exit 0 ;;
  esac
done

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    --agents-only) AGENTS_ONLY=true; RUN_AGENTS=true; MODULE_SELECTED=true ;;
    --tools=*) TOOLS="${arg#--tools=}"; TOOLS_GIVEN=true ;;
    --*) select_module "${arg#--}" || {
      printf 'Unknown argument: %s\nRun bash install.sh --help for options.\n' "$arg" >&2; exit 1; } ;;
    *) printf 'Unknown argument: %s\nRun bash install.sh --help for options.\n' "$arg" >&2; exit 1 ;;
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
