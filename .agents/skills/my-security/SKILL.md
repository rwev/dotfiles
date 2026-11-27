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
[Parallel fan-out](~/.agents/references/orchestration.md#parallel-fan-out).

## Process

1. Split a broad audit one way: by component cluster, or by category
   bundle (auth/IDOR; input/injection/output; secrets/crypto/deps/config).
2. Give each lane the
   [review brief](~/.agents/references/orchestration.md#review-brief),
   plus what changed and why and the overall file list.
3. Merge findings per
   [lane merge](~/.agents/references/orchestration.md#lane-merge). Check auth and dataflow across
   clusters during that merge.
4. Relay findings (`file:line`, exploit scenario, severity) and verdict.
   Wait for explicit go-ahead before fixing anything.
