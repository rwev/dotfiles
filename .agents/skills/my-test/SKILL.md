---
name: my-test
description: >-
  Find the project's test runner and run tests for the current change.
  TRIGGER — invoke whenever the user asks to run tests, check whether tests
  pass, or verify a change via its test suite (e.g. "run the tests", "do the
  tests pass", "verify this works").
---

Run the tests relevant to the current change directly.

1. Detect the test setup from the project (e.g. `package.json`, `pyproject`,
   `cargo`, `go`, `Makefile`). Parallelize independent suites only when
   mutable inputs and resources are isolated per
   [Scheduling](~/.agents/references/orchestration.md#scheduling); otherwise
   run serially.
2. Focus on a named test/path, else tests covering changed working-tree
   files, falling back to the full suite if scoping is unclear.
3. Report pass/fail concisely with failure excerpts and likely `file:line`
   cause. Rerun an apparently flaky failure once before calling it real.
4. Never weaken or skip tests to pass. Explain needed fixes and wait unless
   asked to fix.
