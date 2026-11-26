---
name: my-build
description: >-
  Break a task into a reviewed, subagent-executed build loop.
  TRIGGER — invoke whenever the user wants a non-trivial task actually
  implemented end-to-end, not just planned (e.g. "build X", "implement X",
  "add feature X", "let's get this done"). SKIP for read-only planning — use
  my-plan instead.
compatibility: Requires native subagents and _my-explorer, _my-implementer, _my-reviewer, and _my-enforcer roles.
---

Task: the thing the user just asked to have built.

Before building, check native subagents and `_my-explorer`,
`_my-implementer`, `_my-reviewer`, and `_my-enforcer`. If any are missing,
report `Unsupported: my-build requires native subagents and its explorer,
implementer, reviewer, and enforcer roles` and stop. Do not replace
delegation with sequential inline work or self-review.

Follow [orchestration](~/.agents/references/orchestration.md).

## Phase checklist

1. **Plan** — Use the `## Plan` block from `my-plan` if present. Otherwise
   dispatch `_my-explorer` lanes per
   [Parallel fan-out](~/.agents/references/orchestration.md#parallel-fan-out)
   to map target code, callers, and test seams. Resolve only
   high-importance, high-rework decisions with the user.
2. **Approve** — Show the task list and get go-ahead before product edits.
   Implementation approval does not authorize commits.
3. **Implement batch** — Dispatch `_my-implementer` for dependency-ready
   tasks in blocker order under
   [Scheduling](~/.agents/references/orchestration.md#scheduling).
4. **Review** — Dispatch a fresh `_my-reviewer` for each new or changed
   diff. Always review, even small tasks.
5. **Final review** — Once all tasks finish, review the full range over the
   union of task-owned paths (split via
   [Parallel fan-out](~/.agents/references/orchestration.md#parallel-fan-out)
   when broad).
6. **Hand off** — Point me at `my-pr`. Do not open the PR yourself.

## Dispatch payloads

- `_my-explorer`: task text, global constraints, and its scoped question.
- `_my-implementer`: task requirements, agreed seams, global constraints,
  approval status, relevant findings, owned paths, resource limits, and
  notice that peers exist.
- `_my-reviewer` and `_my-enforcer`: pass the shell-less brief from
  [Parallel fan-out](~/.agents/references/orchestration.md#parallel-fan-out).

## Rules

- Right-size tasks; one small deliverable may stay one task.
- Keep going between tasks until all finish or one blocks.
