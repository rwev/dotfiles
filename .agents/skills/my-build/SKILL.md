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
Commit only if the user explicitly authorized commits. Otherwise keep all
tasks uncommitted and review their working diffs, including untracked product
files. Follow [durable progress](references/progress.md) for run artifacts,
checkpoint ownership, baselines, knowledge validation, and native recovery.
Read that reference before starting or resuming work.

1. Load a linked or unambiguous matching run before replanning. Reconcile
   its state with actual files and native agents. Reuse its scope, decisions,
   and approval. Validate relevant knowledge fingerprints; re-read only
   stale evidence. If no run exists, check whether this task has a resolved
   scope handed off from `my-plan` (files, decisions, ordered steps). Those
   decisions are settled — don't re-ask them, and go straight to step 2.
   If no prior scoping exists, explore it yourself: check the current
   project state, reference real `file:line`s, note reused patterns. For any
   open decision you find, apply the same test `my-plan` uses —
   **importance × rework cost**: ask the master only if it's both
   high-importance and hard to walk back later. Everything else, research
   the codebase/conventions and resolve it yourself; note the choice and a
   one-line reason when you write up the task list in step 2.
2. Keep a resumed run's task IDs and status. If no task list exists, break
   the result into right-sized tasks — each a small, independently
   testable deliverable. If the whole thing is genuinely one small
   deliverable, one task is fine — don't force artificial splits. Fold
   setup/config into whichever task needs it; split only where a task could
   be reviewed and approved on its own. Note
   any global constraints (versions, naming, dependency limits) every task
   must respect — hold these yourself, you'll paste them into every dispatch
   below verbatim.
3. Create or update the run artifacts when the harness permits writes.
   Persist an artifact-ready planning handoff and its discoveries at startup.
   Show the task list before editing product files. Get a go-ahead if the user
   has not already approved this scope. Implementation approval does not
   authorize commits.
4. On approval: confirm we're not on `main`/`master` without explicit OK.
   Check the repo is otherwise in a known-good state before dispatching
   anything — working tree clean (or note what's already dirty and why),
   and whether the test suite is already passing, so a later failure can be
   correctly attributed to the new work rather than pre-existing breakage.
   Record repository/worktree identity, branch, initial SHA, authorization,
   and task status in `state.md`. Then create one task-list item per task.
   Use the native task tool when available; otherwise track it in conversation.
5. Continue at the first unfinished phase. Skip completed tasks only when
   their evidence is still valid. Work in order, never in parallel; agents
   share the working tree.
   a. Mark it in-progress in state. Capture its original baseline once:
      current SHA, staged and unstaged patches, and relevant pre-existing
      untracked evidence. Exclude runtime artifacts and secrets.
      Resume its existing `_my-implementer` if one is recorded. Otherwise
      dispatch that role with the task text, constraints, approval and commit
      authorization, absolute run/checkpoint/progress-reference paths, and
      relevant validated knowledge. Record its native ID immediately.
      Save phase checkpoints and merge important findings as work proceeds.
   b. If it reports `NEEDS_CONTEXT`, try to resolve it yourself first: check
      the scope/decisions log, research the codebase and conventions, and
      apply the same importance × rework-cost test. If it's low-stakes or
      cheap to change later, decide it, note the choice, and resume the same
      implementer without interrupting. Only surface a question to the master if it's a
      genuine gap the planning phase missed — high-importance and hard to
      rework. If `BLOCKED`, stop and report what's blocking you — that's a
      technical failure, not a decision, so ask directly rather than guessing.
   c. Resume the recorded reviewer for an interrupted review of the same
      diff. For a new round or changed diff, dispatch a fresh `_my-reviewer`.
      Supply the task text, constraints,
      approval, absolute run/checkpoint/progress-reference paths, relevant
      validated knowledge, and base..head SHA range if committed. Otherwise
      supply the task baseline and all uncommitted product changes.
      Record its ID immediately. Persist its intermediate review checkpoints
      and discoveries; the reviewer must not write them itself. Always review,
      even trivial tasks — a small diff makes for a cheap review, and the discipline is
      what catches tasks that only looked trivial.
   d. On Critical or Important findings, resume the same `_my-implementer`
      with the findings to fix, then re-review with a fresh reviewer. Apply
      the progress reference's recovery gate before any replacement. Loop until
      Approved. If the same finding survives two fix attempts, stop and ask me rather than
      looping again — a third silent retry rarely fixes what two didn't.
   e. Save verification evidence and review verdict in the checkpoint and
      state. Mark the task completed, then move to the next task.
6. Don't pause between tasks to ask "should I continue?" — keep going until
   every task is done or you hit something genuinely blocked.
7. When all tasks are done, resume an interrupted final review of the same
   diff, or dispatch a fresh `_my-reviewer` for a new round. Review the
   full range (first task's base SHA to current `HEAD`) if committed.
   Otherwise supply the first baseline and all uncommitted product changes.
   Include the same dispatch context as task reviews and record the ID.
   Run one broad pass over the complete work; resolve required findings
   through the same fix-and-review loop. Persist its status and verdict.
   Then point me at `my-pr` for a later PR request. Do not open the PR yourself.
