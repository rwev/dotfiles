---
name: my-security
description: >-
  Audit code for security vulnerabilities before it ships.
  TRIGGER — invoke whenever the user wants a security review of the current
  diff or a named area (e.g. "security review this", "is this safe to
  ship", "audit this for vulnerabilities", "check this for security
  issues"). SKIP for general code quality — use my-tidy or my-review;
  this is security-specific, not a substitute for either.
compatibility: Requires native subagents and the _my-security-reviewer role.
---

Before auditing, check native subagents and `_my-security-reviewer`. If
either is missing, report
`Unsupported: my-security requires native subagents and its reviewer role`
and stop. Do not substitute inline audit or self-review.

Target: the named diff or area, else the working-tree diff (`git diff` plus
staged).

Dispatch fresh `_my-security-reviewer` lane(s) per
[Parallel fan-out](~/.agents/references/orchestration.md#parallel-fan-out),
with no inherited chat history. Require a read-only audit (prompt rules do
not replace harness sandboxing).

1. Split broad audits either by component cluster (plus a cross-boundary
   auth and dataflow lane) or by category bundle (auth/IDOR;
   input/injection/output; secrets/crypto/deps/config).
2. Give each lane what changed and why, overall file list, and its scoped
   target.
3. Merge findings, verify cross-boundary auth/dataflow coverage, and take
   the strictest verdict per `Parallel fan-out` (resume on `Needs context`
   per [Recovery](~/.agents/references/orchestration.md#recovery), else
   relay).
4. Relay findings (`file:line`, exploit scenario, severity) and verdict.
   Wait for explicit go-ahead before fixing anything.
