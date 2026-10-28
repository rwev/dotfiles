# Durable progress

Use with [orchestration](~/.agents/references/orchestration.md). This file adds
only saved run state for the `-tracked` skills.

Use native recovery first. Files support recovery; they do not guarantee that
an entire native agent tree can be restored. Respect harness write limits,
explicit user stops, and approval gates.

At the project root, use `.agents/work/YYYYMMDD-HHMMSS-task-slug/`. If the
name exists, add a numeric suffix. Create only needed folders. Keep run
files; do not clean them up automatically.

- `plan.md`: scope, decisions and reasons, constraints, ordered task IDs.
- `state.md`: repository and worktree paths, branch, initial SHA, authorization,
  task status, native agent IDs, implementer `Files:`, and checkpoint pointers.
- `tasks/T001.md`: phase, discoveries, changed files, verification evidence,
  unresolved issues, and the exact next action.
- `knowledge/subsystem-slug.md`: task-scoped findings and their sources.
- `baselines/T001/`: original task SHA, staged and unstaged patches, and
  relevant pre-existing untracked evidence. Never save secrets.

The coordinator owns plan, state, baselines, and shared knowledge. Each
implementer owns its checkpoint. Reviewers and explorers stay read-only; the
coordinator persists their reports. Write updates to a temporary file, then
rename. Save native IDs immediately after dispatch. Save applicable phases:
discovery, failing test, implementation, verification, and review. Save
important findings immediately, and the final broad-review status.

Runtime files are not product changes. Exclude `.agents/work/` from baseline
capture, product diffs, untracked product discovery, review, and normal
commit candidates. Stage explicit product paths only; never use broad
`git add`. Do not restore baseline patches automatically.

## Tracked build additions

- Before dispatch, record identity, authorization, and task status in
  `state.md`. Record checkpoints in each task's write paths.
- Capture each task baseline once before writers start: SHA, staged and
  unstaged patches, and relevant untracked product evidence on owned paths.
- Give implementers the absolute run dir, their checkpoint path, this file's
  path, and relevant knowledge cards. Give reviewers the task baseline.
- Keep resumed run task IDs and status.

## Knowledge cards

Record each finding's classification (confirmed, hypothesis, or rejected)
and reasons, relevant task IDs, evidence, and unresolved questions. Include
source paths and symbols, and SHA256 fingerprints of source files and
supporting dependencies used as evidence. Tell explorers to report
fingerprints.

Validate fingerprints before you trust a card. Read stale evidence again and
update the finding; reuse unchanged evidence. A hypothesis is not a fact.
Send only cards relevant to the assigned task. The coordinator merges
important findings from task checkpoints and reviewer messages into cards.

## Run recovery

Before replanning, load the explicitly linked run or an unambiguous matching
run. Compare task scope, repository/worktree identity, and branch. Ask if
selection is ambiguous; never choose the newest run blindly. Reuse recorded
approval and decisions within their scope. Compare checkpoints with the
actual files, Git state, native status, and verification evidence. Continue
at the first unfinished phase. Skip completed tasks only if their evidence
is still valid. Keep original baselines.

Use the recorded native ID and task checkpoint to resume an agent, under the
recovery rules in orchestration.
