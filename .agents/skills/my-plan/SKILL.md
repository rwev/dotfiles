---
name: my-plan
description: >-
  Scope a task before any code is written: explore how it currently works,
  surface every open decision — including ones never raised — ask them, and
  flag consequential risks.
  TRIGGER — invoke whenever the user wants a task explored, scoped, or
  planned before code is written (e.g. "how would we approach X", "plan this
  out", "what would it take to do X", "scope this change", "plan this out in
  depth", "what do we need to decide before starting X"). SKIP when they want
  it built — use my-build instead.
compatibility: Requires native subagents and the _my-explorer role.
---

Task: the thing the user just asked about.

Before scoping, check native subagent support and `_my-explorer`. If either
is missing, report
`Unsupported: my-plan requires native subagents and its explorer role` and
stop. Do not substitute inline exploration.

Do not edit files or write code. Follow
[orchestration](~/.agents/references/orchestration.md).

1. Dispatch `_my-explorer` lanes in parallel per
   [Parallel fan-out](~/.agents/references/orchestration.md#parallel-fan-out)
   with full task context and non-overlapping scopes (for example: target
   code and patterns, callers and integration boundaries, existing tests and
   seams, external docs). Merge findings before deciding.
2. Enumerate every open decision across:
   - **Technical** — approach, libraries, patterns, data model/API shape.
   - **Behavioral** — edge cases, defaults, error handling, invalid input.
   - **Scope** — in vs. out; adjacent work that must not be touched.
   - **Consequence** — hard-to-reverse or high blast-radius choices.
3. Triage each decision by importance and rework cost:
   - **High importance + high rework cost** → must ask.
   - **Low on either axis** → decide yourself with a one-line reason.
   When unsure, ask.
4. For each question to ask, prepare a recommended answer with a one-line
   reason, plus realistic alternatives and trade-offs.
5. Batch questions in the native question tool (recommendation first), else
   in conversation, and wait for answers. Ask any follow-on high-bar
   decisions revealed by an answer.
6. Call out consequential risks that need no decision (perf, migration,
   security).
7. Emit a `## Plan` block for `my-build`: files to change, decisions made
   (asked and autonomous) with reasons, ordered tasks with owned paths,
   blockers, test seams, and key `file:line` findings.

Skip ceremony for trivial tasks once explored.
