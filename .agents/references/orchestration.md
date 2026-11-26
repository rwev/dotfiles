# Orchestration

Use these rules from `my-plan`, `my-build`, and related skills.

## Build loop detail

- Before dispatch: confirm branch, note a dirty tree, and check whether tests
  already pass.
- On `NEEDS_CONTEXT`: resolve low-stakes questions yourself. Ask only when
  importance and rework cost are both high.
- On `BLOCKED`: stop and report the technical failure.
- On `DONE_WITH_CONCERNS`: read the concerns. Resolve them, or send them to
  review as findings.
- On reviewer or enforcer `Verdict: Needs context`: supply the missing
  context, then resume the same agent.
- Join writers and freeze review inputs before review, enforcement, or
  shared checks.
- Send Critical/Important reviewer findings or enforcer `Needs shrinks`
  to the same implementer, then to a fresh reviewer. Enforce only after
  that reviewer Approves: dispatch a fresh enforcer on the task's
  updated frozen diff. After two failed fix attempts on the same
  finding, ask. Do not retry silently.
- Mark a task completed only after tests pass, review approves, and the
  enforcer approves.
- Only the coordinator commits. Implementers never stage or commit; they
  report changed paths in `Files:`. When commits are authorized, stage those
  paths explicitly. Commit serially after writers stop, review approves,
  and the enforcer approves. Write a concise conventional-commit message
  scoped to the task.

## Scheduling

- Keep small tasks on one agent. Parallelize only distinct, independent work.
- Before dispatch, know each task ID, goal, dependencies, real write paths
  (including generated files and fixtures), read dependencies, and shared
  resources. Include Git index/HEAD, lockfiles, caches/build dirs, databases,
  services, or ports when relevant.
- Start only dependency-ready tasks. Prove no write/write or write/read
  conflicts or overlapping mutable resource use. Otherwise serialize.
  Unresolved ownership or unapproved dependencies also require serialization.
- Give each agent its ownership limits. Say it is not alone and must not
  overwrite or revert peer changes. Reassign expanded scope only after the
  prior claimant stops. Hold claims until agents and tool writers stop.
- Disjoint tasks may share a tree. Do not create worktrees or change native
  settings automatically. Subagents must not stage, commit, checkout, branch,
  reset, or stash.
- Scope task diffs to owned product paths and supplied context, not peer work.
- Tests can write resources. Parallel focused tests need safe inputs and
  resources, or isolation. The coordinator runs broad or shared checks
  serially after joining. Run required verification once per stable batch.
  Do not skip checks.
- Approve tests, review, and enforcement before you unlock dependents. Apply the same claims
  and gates to fixes. Never overlap a review or enforcement with writers on its evidence.

## Parallel fan-out

- Only the coordinator spawns subagents. Subagents never invoke `my-*` skills
  or spawn nested agents.
- Cap parallel agents at 5 across all skills. Spawn fewer when scope or
  assessed effort is small. Use one lane when a split adds no value. Stay
  inline only when that skill says the role is optional. A skill that stops
  as unsupported still stops.
- Split into non-overlapping lanes: distinct questions, hypotheses, file
  clusters (pair source with its tests), or audit categories. Start lanes
  together and do not repeat an investigation.
- Give each lane the overall goal, full target list, its narrow scope, and
  the global constraints. The brief is the whole context. Do not pass the
  parent chat.
- For `_my-reviewer`, `_my-enforcer`, and `_my-security-reviewer`, include
  task requirements, global constraints, the task baseline, and test results.
  The full scoped diff includes untracked product files. For the reviewer,
  also include agreed seams and pre-existing changes to ignore. For the
  enforcer, also include owned paths, `Files:`, and reviewer findings. A
  commit range may label the diff. It does not replace the diff or the test
  output.
- On `NEEDS_CONTEXT` or `Verdict: Needs context`, supply the missing context,
  then resume that same lane under [Recovery](#recovery). After an
  interruption, resume that same lane under Recovery too.
- Read-only roles (`_my-explorer`, `_my-reviewer`, `_my-enforcer`,
  `_my-security-reviewer`) may share common immutable sources over stable
  evidence. Prompt rules do not replace the harness sandbox. Parallel
  `_my-implementer` writers must follow `## Scheduling` for disjoint paths
  and resources.
- Merge inside one role. Resume any context lane first. Deduplicate by
  `file:line` and issue, check cross-boundary interfaces across clusters,
  and resolve or flag contradictions. Take the strictest verdict on that
  role's scale: reviewer `Approved`, then `Needs fixes`; enforcer
  `Approved`, then `Needs shrinks`; security `Ship as-is`, then `Ship with
  fixes`, then `Do not ship`. If the resumed lane still lacks context, the
  wave verdict is `Needs context`.

## Recovery

- After an interruption or a context gap, resume the same native agent
  (explorer, implementer, reviewer, or enforcer). Do this also when no state is on disk.
- Resume the same implementer for review or enforcer fixes.
- Resume a reviewer or enforcer only for an interrupted pass of the same
  diff. Use a fresh independent agent for a new round or a changed diff.
- Replace an agent only when native resume is not available and the prior
  writer cannot still write. A continuing usage or quota error does not prove
  that resume is not available. If you cannot establish this, stop and report
  the blocker.
- Recover running or unknown agents before new dispatch.
- Examine an interrupted operation's unknown outcome before you replay it.
  A planned next action is not evidence of success.
