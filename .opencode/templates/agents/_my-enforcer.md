---
description: Enforce clean-code principles on one task's diff: shrink cruft and bloat. Dispatch with the task, seams, owned paths, Files:, the frozen diff, and reviewer findings — it has no other context.
mode: subagent
permission:
  edit: deny
  bash:
    "*": allow
    "git commit*": deny
    "git checkout*": deny
    "git reset*": deny
    "git stash*": deny
  task: deny
---
