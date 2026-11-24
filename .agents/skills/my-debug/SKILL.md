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
offer it. Do not form a theory until a tight loop exists.

1. Build a tight feedback loop first. Name one command, run it at least
   once, and show its output (redact secrets). The command must go red
   on this exact symptom, give the same verdict each run, finish in
   seconds, and be runnable without a human. If the bug is intermittent,
   raise the reproduction rate until it is debuggable; do not claim a
   clean repro. If you cannot build this loop, stop, list what you
   tried, and say what you need. Do not hypothesise without it.
2. Once the loop is red, shrink the repro one element at a time until
   every remaining piece is load-bearing.
3. Read the full error, stack trace, or failing assertion. If this looks
   like a regression, check what changed recently (`git log`, `git blame`,
   `git diff`) in the relevant area. If it is not a regression, consider
   environment and config causes too — versions, env vars, platform
   differences, data-dependent state.
4. Generate 3–5 ranked, falsifiable hypotheses before you test any. Each
   must state a prediction: "If X is the cause, then changing Y will make
   the bug disappear." Show the list, then proceed with your ranking
   unless the user reorders it.
5. Temporary diagnostic instrumentation is fine — the only reason to
   edit code here. Instrument to test one prediction at a time. Prefer
   a debugger. Tag every debug log with a unique prefix such as
   `[DEBUG-a4f2]`. For a performance regression, measure a baseline
   first, then bisect.
6. Confirm the theory: show the tight loop go green when the
   hypothesized cause is addressed in isolation. If a correct public
   seam exists for a regression test, name it in the recommendation. If
   the only seam is too shallow, report that as a finding. Do not write
   the fix or the test.
7. Remove all your own instrumentation before reporting. `git diff` must
   come back clean of it, including every tagged debug log — leave the
   tree as you found it.

Report: the tight-loop command, root cause (`file:line` + mechanism),
the evidence that confirms it, the hypothesis that held, and a
described (not applied) fix recommendation. Diagnose only — leave
applying the fix to me, or to `my-build` for anything non-trivial, unless
I've explicitly asked you to fix it yourself.
