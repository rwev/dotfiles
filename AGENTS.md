# AGENTS.md

Instructions for agents that edit this checkout. People start at
[README.md](README.md).

This repository installs a minimal zsh setup and a shared agent layer.
Thin adapters install that layer for Claude, OpenCode, Copilot, and Grok.

## Instruction files

Keep these files separate.

| File                | Role                                      |
| ------------------- | ----------------------------------------- |
| `AGENTS.md`         | How to work inside this checkout.         |
| `.agents/AGENTS.md` | Personal defaults for every project.      |

The installer copies `.agents/AGENTS.md` into each harness home. It leaves
this file in the checkout. Generated global instructions already load the
personal defaults. Leave those rules in `.agents/AGENTS.md`.

Leave this checkout without a root `CLAUDE.md`. Grok loads `AGENTS.md` and
`CLAUDE.md` from the same directory, and both occupy context.

Install flags, harness homes, and the specialist tool matrix live in the
README. Read them there when you change installer behavior.

## Commands

Run these from the checkout. Python 3.11 or newer runs the tests.
Installation uses Bash and jq.

```bash
bash install.sh --help
bash install.sh --agents-only --dry-run
for file in install.sh install/*.sh .grok/*.sh; do bash -n "$file"; done
zsh -n .zshrc
python3 -m unittest discover -s tests -v
python3 -m unittest tests.test_docs
```

`tests/test_docs.py` lints Markdown under `.agents/` against
`.agents/references/terms.md`. It does not lint this file.

Ask before a real install into `$HOME`. The suite uses isolated homes.
A dry run changes nothing.

## Where to edit

The human map is [File layout](README.md#file-layout). Edit these sources:

- Shared specialist bodies live in `.agents/agents/_my-*.md`. Each body
  has `name` and `description` only. Harness templates add frontmatter.
- Skills live in `.agents/skills/my-*/SKILL.md`. `my-ai-toolkit` stays in
  this repo. The installer does not link it into `$HOME`.
- Scheduling and tokens live in `.agents/references/orchestration.md` and
  `.agents/references/terms.md`.
- Installer code lives in `install.sh` and `install/`. Agent install
  logic lives in `install/agents.sh`.

Edit one source for each fact. Point at it from other files. When you
change toolkit docs, follow `.agents/skills/my-ai-toolkit/SKILL.md` and
use the tokens in `terms.md`.

## Workflow architecture

Skills and references own the loop. This section is the map. Follow the
linked files for the rules.

`my-build` is the implementation loop:

1. **Plan.** Use a `## Plan` block from `my-plan` when one exists.
   Otherwise dispatch `_my-explorer`. `my-research` answers a question
   and stops. Start `my-plan` only when asked.
2. **Approve.** Show the task list and wait. That go-ahead authorizes
   one commit per finished task. The rule is in
   `.agents/skills/my-build/SKILL.md`.
3. **Implement.** Dispatch `_my-implementer` for each ready task. It
   writes one task, test first, and reports changed paths. It does not
   commit. See `.agents/agents/_my-implementer.md`.
4. **Review.** Dispatch a fresh `_my-reviewer` on each new or changed
   diff.
5. **Enforce.** After that reviewer approves, dispatch a fresh
   `_my-enforcer`.
6. **Commit.** As soon as the task is completed, follow
   `.agents/skills/my-commit/SKILL.md`. Do not wait for the other tasks,
   and do not ask again. The gate is
   [task-commit](.agents/references/orchestration.md#task-commit).
7. **Hand off.** Point at `my-pr`. Do not push. Leave the pull request
   unopened.

`my-build` requires `_my-explorer`, `_my-implementer`, `_my-reviewer`,
and `_my-enforcer`. Stop when one is missing. Do not replace that review
with your own.

`my-security` audits with `_my-security-reviewer`. It sits outside the
`my-build` required set. `my-tidy` may clean a diff inline when
`_my-enforcer` is missing. `my-build` stops instead.

Caps, status tokens, and verdict tokens are in
`.agents/references/terms.md`. Scheduling, fan-out, recovery, and the
review brief are in `.agents/references/orchestration.md`. The loop
steps are in `.agents/skills/my-build/SKILL.md`.

`my-write` is the document loop. One drafter writes after an approved brief
and outline. A fresh editor follows, then claim checkers, then a tightener.
The steps are in `.agents/skills/my-write/SKILL.md`.

## Checkout constraints

- Ask before you install into `$HOME`, push, open a pull request, or
  delete files.
- Follow commit and push approval in `.agents/AGENTS.md`.
- Keep tests and checks as strong as you found them.
- Match the surrounding style. Make the smallest change that solves the
  task.
- Personal defaults in `.agents/AGENTS.md` still apply with this file.
