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
   review the full diff against it (`git diff <base>...HEAD`, `git log`). Check
   whether the base has moved since the branch diverged; flag likely conflicts
   rather than opening a PR that won't merge cleanly. If there's no remote or
   `gh` isn't authenticated, say so rather than failing partway through.
2. Draft a PR title (concise, imperative) and a body in this shape:

   ```
   ## Summary

   <the smallest tree, pseudocode, or call flow that makes the change clear>

   ## Why

   <one short paragraph or bullets>

   ## Evidence

   - **Before:** <failing test, command output, or behaviour>
   - **After:** <passing test, command output, or behaviour>

   ## Merge danger

   - **Door:** one-way or two-way
   - **Blast radius:** <one or two words, plus a line if needed>
   ```

   Note testing and follow-ups only when they exist. Use terms from
   `GLOSSARY.md` when that file exists.
3. Show me the title and body first. Only after I confirm, push the branch if needed
   and open the PR with `gh pr create`.

Never push or open the PR without my explicit confirmation, and never force-push to
update it without asking first — even for a branch only this PR uses. Don't include
secrets or internal-only notes in the PR body.
