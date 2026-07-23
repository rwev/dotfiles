---
name: my-pr
description: >-
  Summarize the branch and open a pull request (with confirmation).
  TRIGGER — invoke whenever the user asks to open/create a pull request or put
  a branch up for review (e.g. "open a PR", "make a pull request", "ship this
  branch", "put this up for review").
---

Prepare a pull request for the current branch.

1. Determine the base branch (use one the user named, else the repo's default) and
   review the full diff against it (`git diff <base>...HEAD`, `git log`).
2. Draft a PR title (concise, imperative) and a body: a short "what & why" summary,
   notable changes as bullets, and any testing notes or follow-ups.
3. Show me the title and body first. Only after I confirm, push the branch if needed
   and open the PR with `gh pr create`.

Never push or open the PR without my explicit confirmation. Don't include secrets or
internal-only notes in the PR body.
