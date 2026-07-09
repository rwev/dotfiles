---
description: Break a task into a reviewed, subagent-executed build loop
argument-hint: [what you want to build]
---

Task: $ARGUMENTS

1. Explore like `/my:scope` does: check the current project state, reference
   real `file:line`s, note reused patterns and any risks or ambiguities. Ask
   clarifying questions one at a time if the shape of the work isn't obvious.
2. Break the result into right-sized tasks — each a small, independently
   testable deliverable. Fold setup/config into whichever task needs it;
   split only where a task could be reviewed and approved on its own. Note
   any global constraints (versions, naming, dependency limits) every task
   must respect — hold these yourself, you'll paste them into every dispatch
   below verbatim.
3. Show the task list and get a go-ahead before touching anything. This is
   the approval gate before autonomous, multi-commit work starts.
4. On approval: confirm we're not on `main`/`master` without explicit OK,
   then create a todo list with one item per task.
5. For each task, in order — never in parallel, it's the same working tree:
   a. Mark it in-progress. Record the current SHA as this task's base.
      Dispatch the `_my-implementer` agent with just that task's text plus
      the constraints block.
   b. If it reports `NEEDS_CONTEXT`, answer and redispatch. If `BLOCKED`,
      stop and ask a precise question — don't silently retry.
   c. Dispatch the `_my-reviewer` agent with the task text, the constraints
      block, and the base..head SHA range. Always review, even trivial
      tasks — a small diff makes for a cheap review, and the discipline is
      what catches tasks that only looked trivial.
   d. On Critical or Important findings, redispatch `_my-implementer` with
      the findings to fix, then re-review. Loop until Approved.
   e. Mark the todo completed, move to the next task.
6. Don't pause between tasks to ask "should I continue?" — keep going until
   every task is done or you hit something genuinely blocked.
7. When all tasks are done, dispatch `_my-reviewer` once more against the
   full range (first task's base SHA to current `HEAD`) as one broad pass
   over the whole branch. Then point me at `/my:pr` to open the PR — don't
   do that part yourself.
