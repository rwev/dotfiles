---
name: my-security
description: >-
  Audit code for security vulnerabilities before it ships.
  TRIGGER — invoke whenever the user wants a security review of the current
  diff or a named area (e.g. "security review this", "is this safe to
  ship", "audit this for vulnerabilities", "check this for security
  issues"). SKIP for general code quality — use my-tidy or /code-review;
  this is security-specific, not a substitute for either.
---

Target: the diff or area the user named. Default to the current working-tree
diff (`git diff` plus staged) if nothing specific was named.

Dispatch the `_my-security-reviewer` agent with that target rather than
auditing inline. Its tools exclude Edit/Write, so the read-only boundary is
enforced by its permissions, not just an instruction — nothing it finds can
accidentally get "fixed" mid-review.

1. Give it the target (diff range, or the file(s)/feature named) — it has no
   other context, so include anything it needs to know about what changed
   and why. It runs its own category walk (injection, auth, secrets, input
   validation, output handling, crypto, dependencies, configuration).
2. Relay its findings as-is: `file:line`, exploit scenario, severity, and
   its final verdict (`Ship as-is` / `Ship with fixes` / `Do not ship`).
3. Do not apply fixes yourself unless I explicitly ask — its report
   describes them; wait for my go-ahead before touching anything.

For a large or whole-repo audit, it's fine to dispatch more than one pass —
e.g. one per category cluster — and merge the findings, rather than expecting
a single agent to hold the entire surface at once.
