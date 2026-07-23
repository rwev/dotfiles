---
name: my-test
description: >-
  Find the project's test runner and run tests for the current change.
  TRIGGER — invoke whenever the user asks to run tests, check whether tests
  pass, or verify a change via its test suite (e.g. "run the tests", "do the
  tests pass", "verify this works").
---

Run the tests relevant to the current change.

1. Detect the test setup from the project (e.g. package.json scripts, pyproject/pytest,
   cargo, go, Makefile). Don't assume — check what this repo actually uses.
2. If the user named a specific test or path, focus there. Otherwise run the tests
   covering the files changed in the working tree; fall back to the full suite if
   scoping is unclear.
3. Report pass/fail concisely. For failures, show the relevant output and pinpoint the
   likely cause (`file:line`).
4. Do not "fix" failures by weakening or skipping tests. If a fix is needed, explain it
   first and wait unless I've asked you to fix.
