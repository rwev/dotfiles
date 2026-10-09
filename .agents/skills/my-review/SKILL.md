---
name: my-review
description: >-
  Review a diff for spec compliance and code quality.
  TRIGGER — invoke whenever the user wants a code-quality review of the
  current diff or a named range (e.g. "review this", "code review",
  "check this for quality issues"). SKIP for security-only audits — use
  my-security; this is quality and spec compliance, not a security audit.
compatibility: Requires native subagents and the _my-reviewer role.
---

Before reviewing, check native subagents and the `_my-reviewer` role.
If either is unavailable, report
`Unsupported: my-review requires native subagents and its reviewer role`
and stop. Do not replace delegation with an inline review or self-review.

Target: the working-tree diff (`git diff` plus staged), or a `base..head`
range the user named.

Dispatch a fresh `_my-reviewer` agent with that target, with no
conversation history forked or inherited from you. Require a read-only
review. Native permissions enforce only the restrictions that the harness
supports. Prompt instructions are not a sandbox.

1. Give it the target — it has no other context. Include task requirements,
   constraints, and anything it needs about what changed and why.
2. Relay its findings as-is: `file:line`, description, severity, and its
   final verdict (`Approved` / `Needs fixes` / `Needs context`). On
   `Needs context`, supply the missing input and resume the same reviewer
   if you can; otherwise relay its request.
3. Do not apply fixes yourself unless I explicitly ask. Wait for my
   go-ahead before touching anything.

For a large review, use parallel reviewers for distinct target clusters when
useful. Follow [Scheduling](~/.agents/references/progress.md#scheduling);
avoid overlapping reviews and keep evidence stable. As coordinator, merge
findings. Standalone reviews need no build run artifacts.
