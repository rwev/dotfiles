---
name: my-tidy
description: >-
  Clean up the current diff without changing behavior.
  TRIGGER — invoke whenever the user wants the current diff cleaned up or
  polished before committing (e.g. "clean this up", "tidy the diff", "polish
  this before I commit"). SKIP when they want a correctness/bug review — that's
  /code-review, not this.
---

Review only the changes in the current working tree (`git diff` and staged) and
tidy them up — behavior must stay identical.

Look for and fix:
- Dead or unreachable code, commented-out blocks, leftover debug prints/logs.
- Stray TODOs or notes that were meant to be temporary.
- Comments that just restate the code (remove them); keep comments that explain "why".
- Inconsistent naming or formatting versus the surrounding code.
- Obvious small duplications that a local helper would remove.

Do NOT refactor unrelated code, change public APIs, or alter logic. When done,
summarize what you changed and confirm behavior is unchanged. Run the formatter/linter
if the project has one.
