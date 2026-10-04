# Durable progress

Use native recovery first. Files support recovery; they do not guarantee that
an entire native agent tree can be restored. Respect harness write limits,
explicit user stops, and approval gates.

At the project root, use `.agents/work/YYYYMMDD-HHMMSS-task-slug/`. If the
name exists, append a numeric suffix. Create only needed folders. Retain run
files; do not clean them up automatically.

- `plan.md`: scope, decisions and reasons, constraints, ordered task IDs.
- `state.md`: repository and worktree paths, branch, initial SHA, authorization,
  task status, native agent IDs, and checkpoint pointers.
- `tasks/T001.md`: phase, discoveries, changed files, verification evidence,
  unresolved issues, and the exact next action.
- `knowledge/subsystem-slug.md`: task-scoped findings and their sources.
- `baselines/T001/`: original task SHA, staged and unstaged patches, plus
  relevant pre-existing untracked evidence. Never save secrets.

The coordinator owns plan, state, baselines, and shared knowledge. Each
implementer owns its checkpoint. Reviewers stay read-only; the coordinator
persists their reports. Write updates with a temporary file and rename.
Save native IDs immediately after dispatch. Save applicable phases:
discovery, failing test, implementation, verification, and review. Save
important findings immediately and final broad-review status too.

Runtime files are not product changes. Exclude `.agents/work/` from baseline
capture, product diffs, untracked product discovery, review, and normal
commit candidates. Stage explicit product paths only; never use broad
`git add`. Do not restore baseline patches automatically.

## Scheduling

- Keep small tasks on one agent. Parallelize only distinct, independent work.
- Before dispatch, record each task ID, goal, dependencies, real write paths
  (including generated files, fixtures, and checkpoints), read dependencies,
  and shared resources. Include Git index/HEAD, lockfiles, caches/build dirs,
  databases, services, or ports when relevant.
- Start only dependency-ready tasks. Prove no write/write or write/read
  conflicts or overlapping mutable resource use. Otherwise serialize;
  unresolved ownership or unapproved dependencies also require serialization.
- Give each agent its ownership limits. Say it is not alone and must not
  overwrite or revert peer changes. Reassign expanded scope only after the prior
  claimant stops. Hold claims until agents and tool writers are confirmed stopped.
- On resume, recover running or unknown agents before new dispatch.
- Disjoint tasks may share a tree; do not create worktrees or change native
  settings automatically. Parallel workers must not stage, commit, checkout,
  branch, reset, or stash. The coordinator alone commits with authorization,
  serially, after all writers stop and reviews approve.
- Join and freeze batch writers before review or shared verification. Scope
  task baselines/diffs to owned product paths and supplied context, not peer work.
- Parallel read-only agents need distinct questions/targets and stable evidence;
  they may read common immutable sources. Do not duplicate investigations.
- Tests can write resources. Parallel focused tests need safe inputs/resources
  or isolation. The coordinator runs broad/shared checks serially after joining;
  share required verification once per stable batch, without skipping checks.
- Approve tests and review before unlocking dependents. Apply the same claims
  and gates to fixes; never overlap a review with writers on its evidence.

## Knowledge cards

Record each finding's classification (confirmed, hypothesis, or rejected)
and reasons, relevant task IDs, evidence, and unresolved questions. Include
source paths/symbols and SHA256 fingerprints of source files and supporting
dependencies used as evidence.

Validate fingerprints before trusting a card. Re-read stale evidence and
update the finding; reuse unchanged evidence. A hypothesis is not a fact.
Send only cards relevant to the assigned task. The coordinator merges
important findings from task checkpoints and reviewer messages into cards.

## Recovery

Before replanning, load the explicitly linked run or an unambiguous matching
run. Compare task scope, repository/worktree identity, and branch. Ask if
selection is ambiguous; never choose the newest run blindly. Reuse recorded
approval and decisions within their scope. Reconcile checkpoints with the
actual files, Git state, native status, and verification evidence. Continue
at the first unfinished phase. Skip completed tasks only if their evidence
is still valid; preserve original baselines.

Resume the existing task agent after interruptions or context gaps, and
resume the existing implementer for review fixes. Use its recorded native ID and task checkpoint. Do not replace
it until native recovery is unavailable and the prior writer cannot still
write. A continuing usage or quota error does not prove recovery is
unavailable. If these conditions cannot be established, stop and report the
blocker. Resume a recorded reviewer for an interrupted review of the same
diff. Use fresh independent reviewers for new review rounds or changed diffs.

Inspect an interrupted operation's unknown outcome before replaying it.
A planned next action is not evidence of success.
