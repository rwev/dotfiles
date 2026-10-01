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

## AI agent configuration

Shared content lives in `.agents/`. Thin adapters install it in each CLI's native
format. The installer does not install AI tools or manage credentials, sessions,
caches, or other runtime state. It does not link whole harness directories.

### What is portable

No global directory is read by every AI CLI. Project-root `AGENTS.md` is a shared
working-instruction convention. Our `~/.agents/AGENTS.md` is a canonical source,
not a universally discovered global instruction file.

Skills use the standard `SKILL.md` format: YAML metadata followed by Markdown.
The specification defines the format, not one mandatory installation path.
The integration guide recommends `.agents/skills` for shared discovery.
See the [Agent Skills specification](https://agentskills.io/specification) and
[integration guide](https://agentskills.io/client-implementation/adding-skills-support).

| CLI           | Global instruction destination               | Shared skill discovery                                                                                                 |
| ------------- | -------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Claude Code   | `~/.claude/CLAUDE.md`                        | Installer links skills into `~/.claude/skills`. [Docs](https://code.claude.com/docs/en/skills).                        |
| Codex         | `~/.codex/AGENTS.md`                         | Reads `~/.agents/skills`. [Docs](https://learn.chatgpt.com/docs/build-skills).                                         |
| OpenCode      | `~/.config/opencode/AGENTS.md`               | Reads `~/.agents/skills`. [Docs](https://opencode.ai/docs/skills/).                                                    |
| Copilot CLI   | `~/.copilot/copilot-instructions.md`         | Reads `~/.agents/skills`. [Docs](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills). |
| Gemini CLI    | `~/.gemini/GEMINI.md`                        | Reads `~/.agents/skills`. [Docs](https://geminicli.com/docs/cli/skills/).                                              |
| Amp           | `~/.config/amp/AGENTS.md`                    | Reads `~/.agents/skills`. [Docs](https://ampcode.com/docs/customize/skills).                                           |

Native instruction loading differs. See [Claude memory](https://code.claude.com/docs/en/memory),
[Codex AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md),
[OpenCode rules](https://opencode.ai/docs/rules/),
[Copilot instructions](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions),
[Gemini context](https://geminicli.com/docs/cli/gemini-md/), and
[Amp instructions](https://ampcode.com/docs/customize/agents-md).

Personas and specialist roles have no common discovery format. Their prompt
bodies are shared; the installer generates native files. Portable content does
not imply equal capabilities or permission enforcement.

### Install or update agents only

Require Bash and jq. Run from this checkout:

```bash
# Install shared content and the four default adapters.
bash install.sh --agents-only

# Preview without changing files.
bash install.sh --agents-only --dry-run

# Install shared content only, for explicit loading.
bash install.sh --agents-only --tools=universal

# Install optional adapters and shared content.
bash install.sh --agents-only --tools=gemini,amp

# Install all six adapters.
bash install.sh --agents-only --tools=claude,codex,opencode,copilot,gemini,amp
```

`--agents-only` skips packages, shell changes, and unrelated dotfiles.
`--tools` also selects adapters during the normal full bootstrap. Omit it to
select Claude, Codex, OpenCode, and Copilot. Every selection installs the shared
layer. Use `universal` alone. No common launch wrapper is installed.

The installer honors `CLAUDE_CONFIG_DIR`, `CODEX_HOME`, and `COPILOT_HOME`.
OpenCode and Amp use `XDG_CONFIG_HOME`. `GEMINI_CLI_HOME` replaces Gemini's home
root: its config destination is `$GEMINI_CLI_HOME/.gemini`, not the variable
itself. A custom Gemini home also receives individual native skill links.

### Sources and defaults

| Source                                      | Purpose                                                      |
| ------------------------------------------- | ------------------------------------------------------------ |
| `.agents/AGENTS.md`                         | Concise working rules, safety defaults, and verification.    |
| `.agents/skills/my-*/SKILL.md`              | Twelve portable workflows.                                   |
| `.agents/personas/my-humble-servant.md`     | Plain Markdown persona body.                                 |
| `.agents/agents/_my-*.md`                   | Three shared specialist instruction bodies.                  |
| `.claude/templates/`                        | Native role and output-style metadata, outside discovery.    |
| `.opencode/templates/agents/`               | Native role metadata, outside discovery.                     |
| `.copilot/agents/`                          | Native Copilot role metadata.                                |
| `.claude/settings.json`                     | Existing Claude runtime defaults and statusline wiring.      |
| `.opencode/opencode.json`                   | Existing permissions and neutral persona instruction path.   |
| `.codex/config.toml`                        | Existing Codex runtime defaults.                             |

Rules keep changes small, reuse existing code, require verification, and report
failures honestly. Explicit user instructions override these personal defaults.

The default persona is `my-humble-servant`. Each adapter supplies it once:

- Claude uses a generated native output style; global instructions contain rules only.
- OpenCode loads the neutral persona through its `instructions` setting.
- Codex, Copilot, Gemini, and Amp receive rules plus the persona in global instructions.

Existing model, reasoning, permission, memory, plugin, and UI defaults stay in
place. Copilot, Gemini, and Amp keep vendor runtime defaults. The installer adds
no authentication or model configuration for them.

### Skills and specialist roles

| Skill                    | Purpose                                          |
| ------------------------ | ------------------------------------------------ |
| `my-build`               | Implement tasks with subagents and review.       |
| `my-capture-knowledge`   | Save session findings in project Markdown.       |
| `my-commit`              | Stage and commit with a concise message.         |
| `my-debug`               | Diagnose a failure without applying a fix.       |
| `my-deps`                | Explain a dependency and its uses.               |
| `my-explain`             | Explain code or a concept.                       |
| `my-plan`                | Explore and scope work before coding.            |
| `my-pr`                  | Prepare and open a pull request with approval.   |
| `my-security`            | Audit code with an independent reviewer.         |
| `my-test`                | Find and run the project's tests.                |
| `my-tidy`                | Clean the current diff without behavior changes. |
| `my-wip`                 | Save work in a labeled stash.                    |

Use native invocation syntax: `/my-commit` in Claude, `$my-commit` in Codex,
or ask the CLI to use the named skill. Syntax depends on the harness.

The four default adapters install `_my-implementer`, `_my-reviewer`, and
`_my-security-reviewer`. Reviewer profiles omit native edit tools or restrict
edit permissions. Claude, OpenCode, and Copilot reviewers still have shell
access; those settings and prompts are not enforced filesystem isolation.
Codex reviewer profiles request a native read-only sandbox. Parent runtime
settings can affect the effective sandbox.

`my-plan`, `my-build`, and `my-security` check required capabilities before work.
They stop as unsupported when their required subagents or roles are absent.
They do not replace independent review with self-review or sequential execution.
Gemini and Amp adapters supply no specialist roles. `my-plan` needs actual
independent exploration subagents even on those tools.

### Local overrides and migration

Generated files are installed individually. Shared skills, rules, persona, and
role sources are linked into `~/.agents`. Skill edits reach native discovery
through live links. Rerun the installer after rule, persona, role, template, or
runtime-default changes to regenerate native outputs and the manual export.

Claude and OpenCode JSON settings are deep-merged with machine-local files.
Local keys win; local arrays replace default arrays. Existing real settings
are captured on first installation. Edit `~/.claude/settings.local.json` or
`~/.config/opencode/opencode.local.json`, then rerun the installer.
Codex fills only missing TOML defaults. Existing values remain in place.

Global instruction overrides are appended from these machine-local files:

| CLI           | Local instruction file                                    |
| ------------- | --------------------------------------------------------- |
| Claude Code   | `~/.claude/CLAUDE.local.md`                               |
| Codex         | `~/.codex/AGENTS.local.md`                                |
| OpenCode      | `~/.config/opencode/AGENTS.local.md`                      |
| Copilot CLI   | `~/.copilot/copilot-instructions.local.md`                |
| Gemini CLI    | `~/.gemini/GEMINI.local.md`                               |
| Amp           | `~/.config/amp/AGENTS.local.md`                           |

These paths follow custom native homes when set. Pre-existing unmanaged global
instructions are saved and imported into the local instruction file.

Migration replaces known legacy directory links with real directories while
preserving unrelated runtime entries. Unknown directory symlinks are rejected;
the installer does not write through them. Conflicts use `.bak`, then `.bak.1`,
`.bak.2`, and so on. Skill backups live in
`~/.agents/backups/skills/<skill>.bak[.N]`, outside skill-discovery paths.
Unrelated skills and runtime files remain untouched.

Existing shell aliases are unchanged: `cld` runs
`claude --dangerously-skip-permissions`; `cldc` continues a session; `cldr`
selects one to resume. `cxd` runs Codex with
`--dangerously-bypass-approvals-and-sandbox`.

### Manual loading for other tools

`~/.agents/exports/default.md` contains rules, the persona, and a skill index
with capability requirements. Attach it using the tool's explicit read-file or
prompt-file option. For example, [Aider supports `--read`](https://aider.chat/docs/usage/conventions.html):

```bash
aider --read "$HOME/.agents/exports/default.md"
```

Load a full `~/.agents/skills/<name>/SKILL.md` separately when needed.
This fallback does not add native skill discovery, subagents, or permissions.

### Verification

Run the isolated installer suite with Python 3.11 or newer. Python is a test
requirement only; installation uses Bash and jq.

```bash
for file in install.sh install/*.sh; do bash -n "$file"; done
python3 -m unittest discover -s tests -v
```

The suite covers clean installs, repeat runs, target selection, custom homes,
dry runs, local overrides, migration, backups, invalid JSON, and untouched
runtime files. It also checks generated profiles and skill metadata.

Check native discovery after installation:

- Claude: inspect `/memory`, `/context`, and available skills.
- Codex: inspect loaded instructions and `/skills`.
- Copilot: inspect `/instructions`, `copilot skill list`, and custom agents.
- Gemini: inspect `/memory show` and skill discovery.
- Amp: inspect instruction sources and skill listings.

Implementation validation passed the 26 isolated tests. Codex's debug prompt
input showed the rules, one persona, and all twelve skills; all three generated
Codex profiles parsed as TOML. Actual specialist execution and interactive
Claude discovery remain unverified. OpenCode, Copilot, Gemini, and Amp were not
installed on the validation machine, so their runtime discovery is unverified.

## File layout

```text
dotfiles/
├── install.sh          # Installer options and task order
├── install/
│   ├── common.sh       # Shared file helpers
│   ├── agent-config.sh # JSON merges and Codex TOML defaults
│   ├── packages.sh     # Package installation
│   ├── shell.sh        # Dotfile links and shell setup
│   └── agents.sh       # Per-tool agent adapters
├── .zshrc              # ~/.zshrc.core; local ~/.zshrc loads it
├── .zsh_plugins.txt    # Antidote plugin list
├── .agents/            # Canonical rules, skills, persona, and specialist bodies
├── .claude/            # Native settings, statusline, and metadata templates
├── .opencode/          # Native settings and metadata templates
├── .codex/             # Native TOML defaults
├── .copilot/agents/    # Native specialist metadata
└── tests/              # Isolated installer checks
```

## Updating plugins

```bash
antidote update
```
