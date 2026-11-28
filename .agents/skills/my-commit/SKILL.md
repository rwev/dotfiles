---
name: my-commit
description: >-
  Stage changes and write a concise conventional-commit message.
  TRIGGER — invoke whenever the user asks to commit, save, or check in changes,
  including as one step of a larger instruction (e.g. "commit this", "make sure
  changes are committed", "commit and push", "commit then do X") or when asking
  to reword/rewrite a commit message, or when `my-build` finishes a task
  and authorizes its commit. Prefer this over running `git commit`
  directly.
---

Review the current working-tree changes and create a git commit.

## Process

1. Run `git status` and `git diff` (and `git diff --staged`) to see what changed.
2. If nothing is staged, stage the relevant changes with `git add`. When a
   skill names paths, stage only those paths. If that list is none, or nothing
   in it changed, stop without a commit. Don't stage unrelated files, build
   artifacts, or secrets — scan the diff for anything that looks like a
   credential, key, or token before staging it, and flag rather than commit
   it if you find one.
3. Write a concise message in conventional-commit form: `type(scope): summary`
   (types: feat, fix, refactor, docs, test, chore, perf, build, ci). Keep the
   summary under ~72 chars, imperative mood. Add a short body only if the "why"
   isn't obvious from the diff. If the user gave a message, use it.
4. Commit now. The request to commit is the approval. So is a skill that
   already authorized this commit. Do not ask again.

## Rules

Push only when the user asked to push. Then push. Do not ask again. If the
changes span multiple unrelated concerns, make a separate commit for each.
If a pre-commit hook fails, fix the underlying issue and commit again — don't
bypass it with `--no-verify` and don't amend a prior commit to paper over it,
unless the user explicitly asks for either. Every commit uses this skill.
Link here from the caller. Do not copy these steps.
