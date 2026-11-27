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

No fix or theory without a confirmed failure. First name one tight
command, run it, and show it fails on this exact symptom.

## Process

1. Reproduce reliably and report intermittent rates honestly. If you cannot
   reproduce, state what inputs or logs are needed and stop.
2. Read the full error, stack trace, or failing assertion.
3. When the cause is not obvious from the failure output, dispatch parallel
   `_my-explorer` lanes per
   [Parallel fan-out](~/.agents/references/orchestration.md#parallel-fan-out)
   — one distinct hypothesis or angle per lane (recent regressions via
   `git log`/`blame`/`diff`, control/data flow at failing `file:line`, or
   env/config/data state). Pass the repro command, full error output, and
   single hypothesis. Investigate directly if `_my-explorer` is unavailable.
4. Merge explorer reports. For multi-component cases that still need proof,
   add temporary diagnostic logging at boundaries yourself (never in
   explorers), narrow down one hypothesis at a time, and remove all
   instrumentation before reporting (`git diff` clean).
5. Confirm the exact `file:line` and mechanism by showing the repro command
   passes when the cause is addressed in isolation.

## Report back

Report root cause (`file:line` + mechanism), confirming evidence, and a
described (not applied) fix recommendation. Leave applying the fix to the
user or `my-build`.
