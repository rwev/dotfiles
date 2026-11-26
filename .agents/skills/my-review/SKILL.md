---
name: my-review
description: >-
  Review a diff for logic, regressions, and test coverage.
  TRIGGER — invoke whenever the user wants a review of the
  current diff or a named range (e.g. "review this", "code review",
  "check this for bugs"). SKIP for security-only audits — use
  my-security; this is logic and coverage, not a security audit.
compatibility: Requires native subagents and the _my-reviewer role.
---

Before reviewing, check native subagents and `_my-reviewer`. If either is
missing, report
`Unsupported: my-review requires native subagents and its reviewer role`
and stop. Do not substitute inline review or self-review.

Target: the working-tree diff (`git diff` plus staged), or a `base..head`
range the user named.

Dispatch fresh `_my-reviewer` lane(s) per
[Parallel fan-out](~/.agents/references/orchestration.md#parallel-fan-out).

1. Split broad diffs by cohesive module cluster (pair each changed file
   with its tests).
2. Give each lane the shell-less brief from `Parallel fan-out`, plus what
   changed and why and the overall file list.
3. Merge findings per `Parallel fan-out`.
4. Relay findings (`file:line`, description, severity) and final verdict.
   Wait for explicit go-ahead before editing anything.
