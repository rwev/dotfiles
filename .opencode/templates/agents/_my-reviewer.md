---
description: Reviews one task's diff for spec compliance and code quality. Dispatch with the task's requirements and a base..head SHA range or uncommitted diff — it has no other context.
mode: subagent
permission:
  edit: deny
  bash:
    "*": allow
    "git commit*": deny
    "git checkout*": deny
    "git reset*": deny
    "git stash*": deny
---
