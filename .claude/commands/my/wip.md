---
description: Checkpoint current work-in-progress with a labeled stash
argument-hint: [optional: short label]
---

Save the current work as a checkpoint I can return to.

1. Show `git status` so I can see what's in play.
2. Create a labeled stash that includes untracked files:
   `git stash push --include-untracked -m "wip: <label>"` — use $ARGUMENTS as the label
   if given, otherwise a short summary of what's changed.
3. Confirm the stash was created and remind me how to restore it
   (`git stash list`, `git stash pop`).

This is a safe checkpoint, not a discard — never use `git checkout`/`reset --hard` or
otherwise throw away changes here.
