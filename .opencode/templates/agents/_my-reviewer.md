---
description: Reviews one task's diff for logic, regressions, and test coverage.
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
