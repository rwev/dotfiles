---
name: my-commit
description: >-
  Stage changes and write a concise conventional-commit message.
  TRIGGER — invoke whenever the user asks to commit, save, or check in changes,
  including as one step of a larger instruction (e.g. "commit this", "make sure
  changes are committed", "commit and push", "commit then do X") or when asking
  to reword/rewrite a commit message. Prefer this over running `git commit`
  directly.
---

Review the current working-tree changes and create a git commit.

1. Run `git status` and `git diff` (and `git diff --staged`) to see what changed.
2. If nothing is staged, stage the relevant changes with `git add`. Don't stage
   unrelated files, build artifacts, or secrets.
3. Write a concise message in conventional-commit form: `type(scope): summary`
   (types: feat, fix, refactor, docs, test, chore, perf, build, ci). Keep the
   summary under ~72 chars, imperative mood. Add a short body only if the "why"
   isn't obvious from the diff.
4. Show me the message and the staged file list, then commit.

Do not push. If the changes span multiple unrelated concerns, suggest splitting
them into separate commits instead of one.
