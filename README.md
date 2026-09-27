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

`~/.claude/settings.json` isn't a symlink — Claude Code's own `settings.local.json`
layering only applies inside a project's `.claude/`, there's no global equivalent, so
`install.sh` does the merging itself. On first run, any real pre-existing
`~/.claude/settings.json` is captured verbatim into `~/.claude/settings.local.json`;
every run after, `install.sh` regenerates `settings.json` as `.claude/settings.json`
(tracked) deep-merged with `settings.local.json` (local), with local winning any
conflicting key — same idea as `~/.zshrc` sourcing `.zshrc.core`, just merged at
install time instead of sourced at shell-start. `settings.local.json` lives outside
this repo and is hand-editable any time; edits take effect on the next `install.sh`
run. To try a different output style on one machine, set `"outputStyle"` there or
just run `/output-style` in a session.

## OpenCode

[OpenCode](https://opencode.ai) config is version-controlled here too and wired
into `~/.config/opencode/` by `install.sh`, reusing the Claude Code config above
rather than duplicating it:

| Link | What it reuses |
|---|---|
| `~/.config/opencode/AGENTS.md` → `.claude/CLAUDE.md` | Same global working-style/safety rules |
| `~/.config/opencode/command/my` → `.claude/commands/my` | Same `/my:*` commands — the frontmatter/`$ARGUMENTS` syntax is compatible as-is |
| `~/.config/opencode/agents` → `.opencode/agents/` | Native OpenCode versions of `_my-implementer`/`_my-debugger`/`_my-reviewer`, same prose, translated to OpenCode's `mode`/`permission` schema (Claude's `tools:` list has no OpenCode equivalent) |
| `~/.config/opencode/opencode.json` | Generated from `.opencode/opencode.json` merged with `~/.config/opencode/opencode.local.json` — same merge mechanism as `settings.json` above, not a symlink. Folds in the `my-humble-servant` output style via `instructions` and mirrors the secret-file read denies from `.claude/settings.json` |

Not ported: Claude-specific runtime settings with no OpenCode equivalent
(statusline, auto-memory, theme) and marketplace plugins (`code-review`, `verify`,
etc.) — those live outside this repo.

## Codex

`install.sh` also configures [Codex](https://developers.openai.com/codex) from the
same tracked prompts. It preserves Codex's session and authentication files.

| Codex path | Shared source |
|---|---|
| `~/.codex/config.toml` | Fills missing settings from `.codex/config.toml`. Existing values remain in place. |
| `~/.codex/AGENTS.md` | Generated from `.claude/CLAUDE.md` and `.claude/output-styles/my-humble-servant.md`. A pre-existing file is saved as `~/.codex/AGENTS.local.md` and appended. |
| `~/.agents/skills/my-*` | Symlinks to `.claude/skills/my-*`, so changes to a shared skill reach Codex. Invoke one with `$my-commit`, for example. |
| `~/.codex/agents/_my-*.toml` | Generated from `.opencode/agents/_my-*.md` with Codex's agent format. Existing files of the same name are saved with a `.bak` suffix. |

The tracked TOML selects GPT-6 Sol with high reasoning, matching the preference
for strong coding and planning in Claude's settings. It selects workspace
sandboxing, notifications, a dark theme, the alternate-screen TUI,
and a compact status line. The footer shows model and reasoning, working
directory, Git branch, context used, and the five-hour and weekly usage limits
when available.
Codex's native footer does not show general session cost or changed-line counts
like the Claude statusline script. The config disables memories. The shared
output style in `AGENTS.md` sets the persona. The `cxd` alias bypasses Codex's
sandbox and approval prompts for that launch.

Run `install.sh` again after changing the shared global instructions, output
style, agent prompts, or TOML defaults. Existing values in `~/.codex/config.toml`
win over tracked defaults, including values saved by Codex's `/model`, `/theme`,
and `/statusline` commands. Skill edits take effect through the symlinks. If you
already set `project_doc_fallback_filenames`, add `CLAUDE.md` to that list to
reuse project-level Claude instructions. Put Codex-only global instructions in
`~/.codex/AGENTS.local.md`. Claude and OpenCode's JSON file-read deny rules do
not transfer to Codex; those require a separate Codex permissions profile.

Shell alias (in `.zshrc`): `cxd` starts Codex with
`--dangerously-bypass-approvals-and-sandbox`.

## File layout

```
dotfiles/
├── install.sh          # Bootstrap: installs zsh, fzf, antidote; symlinks files
├── .zshrc              # Main zsh config (symlinked to ~/.zshrc.core; ~/.zshrc loads it)
├── .zsh_plugins.txt    # antidote plugin list
├── .claude/            # Claude Code config (settings, CLAUDE.md, statusline, commands, agents, output styles)
├── .opencode/          # OpenCode config (opencode.json, agents) — reuses .claude/ where schemas allow
└── .codex/             # Codex config defaults; installer reuses Claude and OpenCode prompts
```

## Updating plugins

```bash
antidote update
```
