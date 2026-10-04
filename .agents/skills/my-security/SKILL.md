---
name: my-security
description: >-
  Audit code for security vulnerabilities before it ships.
  TRIGGER — invoke whenever the user wants a security review of the current
  diff or a named area (e.g. "security review this", "is this safe to
  ship", "audit this for vulnerabilities", "check this for security
  issues"). SKIP for general code quality — use my-tidy or a code-quality review;
  this is security-specific, not a substitute for either.
compatibility: Requires native subagents and the _my-security-reviewer role.
---

Before auditing, check native subagents and the `_my-security-reviewer`
role. If either is unavailable, report
`Unsupported: my-security requires native subagents and its reviewer role`
and stop. Do not replace delegation with an inline audit or self-review.

Target: the diff or area the user named. Default to the current working-tree
diff (`git diff` plus staged) if nothing specific was named.

Dispatch the `_my-security-reviewer` agent with that target rather than
auditing inline. Require a read-only audit. Native permissions enforce only
the restrictions that the harness supports. Prompt instructions are not a
sandbox or a substitute for native permissions.

1. Give it the target (diff range, or the file(s)/feature named) — it has no
   other context, so include anything it needs to know about what changed
   and why. Within its scope, it checks categories (injection, auth, secrets, input
   validation, output handling, crypto, dependencies, configuration).
2. Relay its findings as-is: `file:line`, exploit scenario, severity, and
   its final verdict (`Ship as-is` / `Ship with fixes` / `Do not ship`).
3. Do not apply fixes yourself unless I explicitly ask — its report
   describes them; wait for my go-ahead before touching anything.

For a large audit, use parallel reviewers for distinct target clusters or
independent questions when useful. Follow
[Scheduling](../my-build/references/progress.md#scheduling); avoid overlapping
audits and keep evidence stable. As coordinator, merge findings and check
cross-boundary auth and dataflow coverage. Standalone audits need no build
run artifacts.
