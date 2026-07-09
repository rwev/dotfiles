# dotfiles

Minimal, fast zsh configuration.

## What's included

| Component | What it does |
|---|---|
| **[pure](https://github.com/sindresorhus/pure)** | Minimal async prompt — shows git status, last command duration, virtualenv |
| **[zsh-autosuggestions](https://github.com/zsh-users/zsh-autosuggestions)** | Fish-like inline suggestions from history |
| **[zsh-syntax-highlighting](https://github.com/zsh-users/zsh-syntax-highlighting)** | Highlight valid commands green, bad commands red |
| **[zsh-history-substring-search](https://github.com/zsh-users/zsh-history-substring-search)** | Type part of a command, use ↑/↓ to search matching history |
| **[zsh-completions](https://github.com/zsh-users/zsh-completions)** | Hundreds of extra tab-completion definitions |
| **[zsh-z](https://github.com/agkozak/zsh-z)** | Jump to frecent directories: `z proj` |
| **[fzf](https://github.com/junegunn/fzf)** | Fuzzy search: Ctrl-R (history), Ctrl-T (files), Alt-C (cd) |
| **[antidote](https://antidote.sh)** | Fast static plugin manager |

## Install

```bash
git clone https://github.com/you/dotfiles.git ~/dotfiles
bash ~/dotfiles/install.sh
```

Re-login (or `exec zsh`) to start using zsh.

### Dry run first

```bash
bash ~/dotfiles/install.sh --dry-run
```

## Key bindings

| Key | Action |
|---|---|
| `↑` / `↓` | Search history by what you've typed (substring search) |
| `Ctrl-P` / `Ctrl-N` | Same as ↑/↓ |
| `Ctrl-Space` | Accept autosuggestion |
| `Ctrl-R` | Fuzzy search command history (fzf) |
| `Ctrl-T` | Fuzzy insert file path |
| `Alt-C` | Fuzzy cd into a directory |
| `Ctrl-→` / `Ctrl-←` | Jump forward/backward by word |

## Usage tips

### z — directory jumping

```bash
# After visiting ~/projects/my-app a few times:
z my-app        # jumps there
z app           # partial match
z -l            # list all frecent dirs
```

### Machine-local config

`install.sh` symlinks the tracked config to `~/.zshrc.core`, and leaves
`~/.zshrc` as a real, untracked file that just does `source
"$HOME/.zshrc.core"`. That's deliberate: installers (nvm, bun, etc.)
universally append PATH exports and init lines to `~/.zshrc` by convention —
since it's untracked, that churn never touches the repo. Anything you want to
add by hand (tokens, work-specific paths) goes there too.

## Claude Code

Global [Claude Code](https://claude.com/claude-code) config is version-controlled here
and symlinked into `~/.claude/` by `install.sh`. Only portable config is tracked — the
runtime state in `~/.claude/` (sessions, cache, `~/.claude.json` OAuth tokens,
auto-memory, plugin mirror) is intentionally left untracked.

| File | What it does |
|---|---|
| `.claude/settings.json` | Model, theme, cleanup window, secret-file deny rules, auto-memory, statusline wiring |
| `.claude/CLAUDE.md` | Universal rules — **loaded into every session on the machine**, so kept lean |
| `.claude/statusline.sh` | Footer showing model · dir · git branch · session cost · lines changed |
| `.claude/commands/my/` | Custom slash commands, namespaced `/my:*` so it's clear they come from here — drop in a `.md` file to add more |
| `.claude/agents/` | Custom subagents, namespaced `_my-*` (underscore = dispatched by a command, not invoked directly) — drop a `_my-*.md` file here to add more |
| `.claude/output-styles/` | The `my-humble-servant` output style (set as the default in `settings.json`) |

Commands: `/my:commit`, `/my:explain`, `/my:scope`, `/my:tidy`, `/my:test`,
`/my:pr`, `/my:wip`, `/my:deps`, `/my:build`.

Agents: `_my-implementer`, `_my-reviewer`, `_my-debugger` — a slim,
subagent-driven-development loop inspired by the `superpowers` plugin.
`/my:build <task>` explores, proposes a task breakdown, and on approval
dispatches `_my-implementer`/`_my-reviewer` per task (TDD, fresh-eyes review,
fix-and-re-review). `_my-debugger` root-causes bugs standalone, isolated from
the main thread.

Shell aliases (in `.zshrc`): `cld` = `claude --dangerously-skip-permissions`,
`cldc` = continue last session, `cldr` = pick a session to resume.

### Machine-local overrides

Anything you don't want committed — a per-machine `model`, work-only permission rules,
or an override of any committed setting — goes in `~/.claude/settings.local.json`. It's
gitignored and merges over `settings.json`. To try a different output style on one
machine without editing the tracked file, set `"outputStyle"` there or just run
`/output-style` in a session.

## File layout

```
dotfiles/
├── install.sh          # Bootstrap: installs zsh, fzf, antidote; symlinks files
├── .zshrc              # Main zsh config (symlinked to ~/.zshrc.core; ~/.zshrc loads it)
├── .zsh_plugins.txt    # antidote plugin list
└── .claude/            # Claude Code config (settings, CLAUDE.md, statusline, commands, agents, output styles)
```

## Updating plugins

```bash
antidote update
```
