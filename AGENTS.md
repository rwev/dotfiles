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

The installer inlines `.agents/AGENTS.md` into the generated instruction
file for each harness selected on that run. The default selection is Claude
and Grok. It leaves this file in the checkout. Persona placement is in the
README. Generated global instructions already load the personal defaults.
Leave those rules in `.agents/AGENTS.md`.

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

`tests/test_docs.py` checks schemas and tokens in Markdown under `.agents/`
against `.agents/references/terms.md`. The same test checks anchors, links,
and skill-agent duplication. It does not lint this file.

Ask before a real install into `$HOME`. The suite uses isolated homes.
A dry run writes nothing.

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

`my-build` is the implementation loop. The steps are in
`.agents/skills/my-build/SKILL.md`. This map uses that order:

1. **Plan.** Use a `## Plan` block from `my-plan` when one exists.
   Otherwise dispatch `_my-explorer`. `my-research` answers a question
   and stops. Start `my-plan` only when asked.
2. **Approve.** Show the task list and wait. That go-ahead authorizes
   one commit per finished task. The rule is in
   `.agents/skills/my-build/SKILL.md`.
3. **Implement.** Dispatch `_my-implementer` for each ready task. It
   writes one task and reports changed paths. It writes a failing test
   first when the task has testable behavior. Docs, config, and
   scaffolding are implemented directly. It does not commit. See
   `.agents/agents/_my-implementer.md`.
4. **Review.** Dispatch a fresh `_my-reviewer` on each new or changed
   diff. Then follow
   [fix-cap](.agents/references/orchestration.md#fix-cap). A fresh
   `_my-enforcer` runs only after that reviewer approves.
5. **Commit.** As soon as the task is completed, follow
   `.agents/skills/my-commit/SKILL.md`. Do not wait for the other tasks,
   and do not ask again. The gate is
   [task-commit](.agents/references/orchestration.md#task-commit).
6. **Final review.** After every task is committed, review the full
   range. A fix from that pass is a new task. Run steps 3 to 5 for it.
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
review brief are in `.agents/references/orchestration.md`.

`my-write` is the document loop. Agree a brief first. When no sources were
supplied, the loop also requires `_my-explorer`. One drafter writes the
outline, then the piece, after you approve the outline. Reference sections
that do not refer to each other use one drafter each. A fresh editor
follows. The drafter applies substance findings, and a fresh editor runs
again. Claim checkers follow. The tightener runs only after the editor
returns `Approved`. Outline approval is not commit approval. The loop does
not commit. The steps are in `.agents/skills/my-write/SKILL.md`.

## Checkout constraints

- Ask before you install into `$HOME`, push, open a pull request, or
  delete files.
- Follow commit and push approval in `.agents/AGENTS.md`.
- Keep tests and checks as strong as you found them.
- Match the surrounding style. Make the smallest change that solves the
  task.
- Personal defaults in `.agents/AGENTS.md` still apply with this file.
