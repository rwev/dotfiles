# =============================================================================
# Plugin Manager: antidote
# https://antidote.sh
# =============================================================================
ANTIDOTE_HOME="${XDG_DATA_HOME:-$HOME/.local/share}/antidote"

# Bootstrap antidote if missing
if [[ ! -d "$ANTIDOTE_HOME" ]]; then
  git clone --depth=1 https://github.com/mattmc3/antidote.git "$ANTIDOTE_HOME"
fi

source "$ANTIDOTE_HOME/antidote.zsh"

# Load plugins from .zsh_plugins.txt (uses a compiled static file for speed)
antidote load "${ZDOTDIR:-$HOME}/.zsh_plugins.txt"

# =============================================================================
# Prompt: pure
# https://github.com/sindresorhus/pure
# =============================================================================
autoload -U promptinit && promptinit
PURE_PROMPT_SYMBOL='$'
prompt pure

# Pure tweaks: show prompt on a new line, async git
zstyle ':prompt:pure:prompt:*' color 142   # gruvbox bright green
zstyle ':prompt:pure:git:*' color 109     # gruvbox blue

# =============================================================================
# Completion
# =============================================================================
autoload -U compinit

# Rebuild completion cache at most once per day
_comp_cache="${XDG_CACHE_HOME:-$HOME/.cache}/zsh/zcompdump"
mkdir -p "${_comp_cache:h}"
if [[ -n ${_comp_cache}(#qN.mh+24) ]]; then
  compinit -d "$_comp_cache"
else
  compinit -C -d "$_comp_cache"
fi
unset _comp_cache

# Completion style
zstyle ':completion:*' menu select                   # Arrow-key navigable menu
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Z}'  # Case-insensitive matching
zstyle ':completion:*' list-colors "${(s.:.)LS_COLORS}"
zstyle ':completion:*:descriptions' format '%F{214}-- %d --%f'   # gruvbox yellow
zstyle ':completion:*:warnings' format '%F{167}No matches%f'    # gruvbox red
zstyle ':completion:*' group-name ''                 # Group by category

# =============================================================================
# History
# =============================================================================
HISTFILE="$HOME/.zsh_history"
HISTSIZE=100000
SAVEHIST=100000

setopt SHARE_HISTORY          # Share history across all sessions
setopt HIST_IGNORE_ALL_DUPS   # Don't record duplicates
setopt HIST_IGNORE_SPACE      # Don't record commands starting with a space
setopt HIST_VERIFY            # Show substituted command before executing
setopt HIST_REDUCE_BLANKS     # Trim extra blanks from history entries
setopt EXTENDED_HISTORY       # Save timestamp + duration in history

# =============================================================================
# fzf — fuzzy finder
# https://github.com/junegunn/fzf
# =============================================================================
if command -v fzf &>/dev/null; then
  # Shell integration (key bindings + completion)
  if [[ -f /usr/share/doc/fzf/examples/key-bindings.zsh ]]; then
    source /usr/share/doc/fzf/examples/key-bindings.zsh
  fi
  if [[ -f /usr/share/doc/fzf/examples/completion.zsh ]]; then
    source /usr/share/doc/fzf/examples/completion.zsh
  fi
  # Fallback: fzf installed via git
  [[ -f "$HOME/.fzf.zsh" ]] && source "$HOME/.fzf.zsh"

  export FZF_DEFAULT_OPTS="
    --height=40%
    --layout=reverse
    --border=rounded
    --info=inline
    --bind 'ctrl-/:toggle-preview'
    --color=fg:#ebdbb2,bg:#282828,hl:#b8bb26
    --color=fg+:#fbf1c7,bg+:#3c3836,hl+:#fabd2f
    --color=info:#83a598,prompt:#b8bb26,pointer:#fb4934
    --color=marker:#fe8019,spinner:#d3869b,header:#83a598
  "

  # Ctrl-R: fuzzy history search (overrides default)
  export FZF_CTRL_R_OPTS="--preview 'echo {}' --preview-window=down:3:hidden:wrap"

  # Ctrl-T: fuzzy file picker — use fd if available, else find
  if command -v fd &>/dev/null; then
    export FZF_DEFAULT_COMMAND='fd --type f --hidden --follow --exclude .git'
    export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"
  fi

  # Alt-C: fuzzy cd
  export FZF_ALT_C_OPTS="--preview 'ls -la {}'"
fi

# =============================================================================
# Key Bindings
# =============================================================================
bindkey -e  # Emacs key map (default; readline-compatible)

# History substring search (zsh-users/zsh-history-substring-search)
# Up/down arrow search history for what you've typed so far
bindkey '^[[A' history-substring-search-up
bindkey '^[[B' history-substring-search-down
bindkey '^P'   history-substring-search-up
bindkey '^N'   history-substring-search-down

# Ctrl-arrows for word navigation
bindkey '^[[1;5C' forward-word
bindkey '^[[1;5D' backward-word

# =============================================================================
# zsh-z configuration
# https://github.com/agkozak/zsh-z
# =============================================================================
ZSHZ_DATA="${XDG_DATA_HOME:-$HOME/.local/share}/z/data"
mkdir -p "${ZSHZ_DATA:h}"
ZSHZ_CASE=smart   # Smart case: lowercase matches case-insensitively
ZSHZ_ECHO=1       # Print directory before jumping

# =============================================================================
# zsh-autosuggestions configuration
# =============================================================================
ZSH_AUTOSUGGEST_STRATEGY=(history completion)
ZSH_AUTOSUGGEST_BUFFER_MAX_SIZE=20
bindkey '^ ' autosuggest-accept   # Ctrl-Space to accept suggestion

# =============================================================================
# General Shell Options
# =============================================================================
setopt AUTO_CD            # Type a directory name to cd into it
setopt CORRECT            # Suggest corrections for mistyped commands
setopt INTERACTIVE_COMMENTS  # Allow comments in interactive shell
setopt GLOB_DOTS          # Include dotfiles in glob patterns
setopt NO_BEEP            # Silence the bell

# =============================================================================
# Environment
# =============================================================================
export EDITOR="${EDITOR:-vim}"
export VISUAL="${VISUAL:-vim}"
export PAGER="${PAGER:-less}"
export LESS='-R --quit-if-one-screen --no-init'

# Local bin
[[ -d "$HOME/.local/bin" ]] && export PATH="$HOME/.local/bin:$PATH"

# =============================================================================
# Aliases
# =============================================================================
alias ls='ls --color=auto'
alias ll='ls -lah --color=auto'
alias la='ls -A --color=auto'
alias grep='grep --color=auto'
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'

# Safety nets
alias rm='rm -i'
alias cp='cp -i'
alias mv='mv -i'

# Git shortcut (aliases live in .gitconfig)
alias g='git'

# Claude Code — skip permission prompts (pairs with skipDangerousModePermissionPrompt).
# Named 'cld' rather than 'cc' to avoid shadowing the C compiler.
alias cld='claude --dangerously-skip-permissions'
alias cldc='claude --continue --dangerously-skip-permissions'   # continue most recent session
alias cldr='claude --resume --dangerously-skip-permissions'     # pick a session to resume
