---
name: my-wip
description: >-
  Checkpoint current work-in-progress with a labeled stash.
  TRIGGER — invoke whenever the user wants to save or checkpoint in-progress
  work without committing it (e.g. "save my progress", "checkpoint this",
  "stash this for now", "let me park this and switch branches").
---

Save the current work as a checkpoint I can return to.

1. Show `git status` so I can see what's in play.
2. Create a labeled stash that includes untracked files:
   `git stash push --include-untracked -m "wip: <label>"` — use a label the user gave,
   otherwise a short summary of what's changed.
3. Confirm the stash was created and remind me how to restore it
   (`git stash list`, `git stash pop`).

This is a safe checkpoint, not a discard — never use `git checkout`/`reset --hard` or
otherwise throw away changes here.
