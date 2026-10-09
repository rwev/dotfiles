---
name: my-build
description: >-
  Break a task into a reviewed, subagent-executed build loop.
  TRIGGER — invoke whenever the user wants a non-trivial task actually
  implemented end-to-end, not just planned (e.g. "build X", "implement X",
  "add feature X", "let's get this done"). SKIP for read-only planning — use
  my-plan instead.
compatibility: Requires native subagents and _my-implementer and _my-reviewer roles.
---

Task: the thing the user just asked to have built.

Before building, check native subagents and both `_my-implementer` and
`_my-reviewer` roles. If any are unavailable, report
`Unsupported: my-build requires native subagents and both roles` and stop.
Do not replace delegation with sequential inline work or self-review.
Only you, the coordinator, commit. Commit only if the user explicitly
authorized commits. Commit a task only after review approves; stage its
implementer's `Files:` paths explicitly. Otherwise keep all tasks
uncommitted and review their working diffs, including untracked product
files.

Follow [durable progress](~/.agents/references/progress.md) for run
artifacts, checkpoint ownership, baselines, knowledge validation, and native
recovery. Read that reference before starting or resuming work. Use its
[Scheduling](~/.agents/references/progress.md#scheduling) and
[Build loop detail](~/.agents/references/progress.md#build-loop-detail)
rules.

## Phase checklist

1. **Plan** — Load a matching run, or accept a `my-plan` handoff, or explore.
   Resolve only high-importance, high-rework decisions with the user.
2. **Approve** — Show the task list. Get go-ahead before product edits.
   Implementation approval does not authorize commits.
3. **Baselines** — Confirm branch and repo state. Record identity and
   authorization. Capture each task baseline before writers start.
4. **Implement batch** — Dispatch `_my-implementer` for dependency-ready
   tasks under scheduling rules. Persist phases, claims, and IDs.
5. **Join** — Join writers. Freeze review inputs. Run required shared checks.
6. **Review** — Dispatch a fresh `_my-reviewer` for each new or changed
   diff. Resume the same reviewer only for an interrupted review or a
   `Needs context` verdict on the same diff. Always review, even small tasks.
7. **Fix loop** — On Critical/Important findings, resume the same implementer,
   then re-review. After two failed attempts on the same finding, ask.
8. **Final review** — When all tasks are done, review the full range over
   the union of task-owned paths.
9. **Hand off** — Point me at `my-pr`. Do not open the PR yourself.

## Dispatch payloads

Give each role a full brief; it has no other context.

- `_my-implementer`: task text and requirements, global constraints, and
  approval status (it never commits). Add the absolute run dir, its
  checkpoint and progress-reference paths, relevant knowledge cards, owned
  paths and resource limits, and a notice that it is not alone.
- `_my-reviewer`: the same context, plus a `base..head` range if committed.
  Otherwise supply the task baseline and the staged, unstaged, and untracked
  changes scoped to its owned paths. Start it fresh, with no conversation
  history forked or inherited from you.

## Rules

- Keep resumed run task IDs and status. Right-size tasks; one small deliverable
  may stay one task.
- Hold global constraints yourself and paste them into every dispatch.
- Persist run artifacts when the harness permits writes.
- Do not pause between tasks to ask "should I continue?" Keep going until
  every task is done or something is blocked.
- Follow the Build loop detail for `NEEDS_CONTEXT` (read its `Question:`),
  `BLOCKED`, `DONE_WITH_CONCERNS`, and reviewer `Verdict: Needs context`.
- Record each implementer's `Files:` in state.
