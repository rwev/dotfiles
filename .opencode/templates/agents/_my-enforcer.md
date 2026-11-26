---
description: Enforce clean-code principles on one task's diff: shrink cruft and bloat.
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
