---
name: my-debug
description: >-
  Root-cause-first investigation of a bug, test failure, or unexpected
  behavior. Reports the mechanism and a fix recommendation; does not apply
  the fix. TRIGGER — invoke whenever the user wants a bug or failure
  diagnosed (e.g. "why is X broken", "debug this", "figure out why this
  test fails", "root-cause this"). SKIP once the cause is already known and
  they just want it fixed — implement directly, or use my-build for
  non-trivial fixes.
---

Bug/failure: the thing the user just asked about.

No fix without a confirmed root cause. A fix without one is a guess — don't
offer it.

1. Reproduce the failure reliably. If it's intermittent, note the
   reproduction rate honestly rather than claiming a clean repro; if you
   can't reproduce it at all, say so and report what you'd need (logs,
   exact repro steps) rather than guessing.
2. Read the full error/stack trace/failing assertion before forming a theory
   — don't skip past it.
3. If this looks like a regression, check what changed recently (`git log`,
   `git blame`, `git diff`) in the relevant area. If it isn't a regression
   (works nowhere, or "worked on my machine"), consider environment/config
   causes too — versions, env vars, platform differences, data-dependent
   state — not just recent code changes.
4. For multi-component failures, temporary diagnostic instrumentation is
   fine — the only reason to edit code here. Add targeted logging at
   component boundaries, narrow down the failure one hypothesis at a time.
5. Once you can point at the exact `file:line` and mechanism, confirm the
   theory: show the failure disappears (or the assertion flips) when your
   hypothesized cause is addressed in isolation.
6. Remove all your own instrumentation before reporting. `git diff` must come
   back clean of it — leave the tree as you found it.

Report: root cause (`file:line` + mechanism), the evidence that confirms it,
and a described (not applied) fix recommendation. Diagnose only — leave
applying the fix to me, or to `/my-build` for anything non-trivial, unless
I've explicitly asked you to fix it yourself.
