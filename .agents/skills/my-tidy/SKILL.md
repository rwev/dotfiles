---
name: my-tidy
description: >-
  Clean up the current diff without changing behavior.
  TRIGGER — invoke whenever the user wants the current diff cleaned up or
  polished before committing (e.g. "clean this up", "tidy the diff", "polish
  this before I commit"). SKIP for a logic or coverage review — use
  my-review. my-build already runs the enforcer for clean-code checks.
---

Review only the changes in the current working tree (`git diff` and staged) and
tidy them up — behavior must stay identical.

Look for and fix:
- Dead or unreachable code, commented-out blocks, leftover debug prints/logs.
- Stray TODOs or notes that were meant to be temporary. Keep a well-formed `shortcut: <limit>, <when to upgrade>` comment. A marker with no upgrade trigger is a TODO.
- Remove comments that restate the code, narrate the next line, repeat the name or signature, draw a banner or section line, or record who changed the code or why the change was made.
- Keep a comment that explains a non-obvious "why".
- Shorten a kept comment to one sentence. Keep a second sentence only when it states a constraint the code cannot show, such as a unit, an order, a lifetime, or a rejected alternative.
- Inconsistent naming or formatting versus the surrounding code.
- Obvious small duplications that a local helper would remove.

Do NOT refactor unrelated code, change public APIs, or alter logic. Run the
formatter/linter if the project has one. If tests exist, run them (or use
my-test) before and after — don't just assert behavior is unchanged, confirm
it. When done, summarize what you changed.
