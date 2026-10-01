# Install required packages
select_package_manager() {
  if command -v apt-get &>/dev/null; then
    PACKAGE_MANAGER=apt-get
  elif command -v brew &>/dev/null; then
    PACKAGE_MANAGER=brew
  elif command -v dnf &>/dev/null; then
    PACKAGE_MANAGER=dnf
  elif command -v pacman &>/dev/null; then
    PACKAGE_MANAGER=pacman
  fi
}

install_with_package_manager() {
  case "$PACKAGE_MANAGER" in
    apt-get) run sudo apt-get install -y "$@" ;;
    brew) run brew install "$@" ;;
    dnf) run sudo dnf install -y "$@" ;;
    pacman) run sudo pacman -S --noconfirm "$@" ;;
    *) return 1 ;;
  esac
}

install_packages() {
  local packages=()

  command -v zsh &>/dev/null  || packages+=(zsh)
  command -v fzf &>/dev/null  || packages+=(fzf)
  command -v git &>/dev/null  || packages+=(git)
  command -v jq  &>/dev/null  || packages+=(jq)   # required by agent installation

  if [[ ${#packages[@]} -eq 0 ]]; then
    success "zsh, fzf, git, and jq are already installed"
    return
  fi

  info "Installing: ${packages[*]}"
  if [[ -z "$PACKAGE_MANAGER" ]]; then
    error "No supported package manager found. Install zsh, fzf, git, and jq manually."
    exit 1
  fi
  if [[ "$PACKAGE_MANAGER" == apt-get ]]; then
    run sudo apt-get update -qq || warn "apt-get update failed — attempting install anyway"
  fi
  if ! install_with_package_manager "${packages[@]}"; then
    error "$PACKAGE_MANAGER install failed — install required packages manually"
    exit 1
  fi
}

# Install optional display tools
install_pretty_print_tools() {
  local packages=()

  command -v bat &>/dev/null || command -v batcat &>/dev/null || packages+=(bat)

  if [[ ${#packages[@]} -eq 0 ]]; then
    success "bat already installed"
  else
    info "Installing: ${packages[*]}"
    if [[ -n "$PACKAGE_MANAGER" ]]; then
      install_with_package_manager "${packages[@]}" || warn "Failed to install ${packages[*]} — install manually if wanted"
    else
      warn "No supported package manager found — install bat manually if wanted"
    fi
  fi

  if command -v glow &>/dev/null; then
    success "glow already installed"
    return
  fi

  info "Installing glow (markdown renderer)"
  if [[ "$PACKAGE_MANAGER" == brew || "$PACKAGE_MANAGER" == pacman || "$PACKAGE_MANAGER" == dnf ]]; then
    install_with_package_manager glow || warn "Failed to install glow — install manually: https://github.com/charmbracelet/glow"
  elif command -v snap &>/dev/null; then
    # Not in Debian/Ubuntu's apt archives; Charm ships it via snap instead.
    run sudo snap install glow || warn "Failed to install glow via snap — install manually: https://github.com/charmbracelet/glow"
  else
    warn "glow not available via a supported package manager — install manually: https://github.com/charmbracelet/glow"
  fi
}
