---
description: Reviews one task's diff for logic, regressions, and test coverage.
mode: subagent
permissions:
  - { action: edit, resource: "*", effect: deny }
  - { action: shell, resource: "*", effect: allow }
  - { action: shell, resource: "git commit*", effect: deny }
  - { action: shell, resource: "git checkout*", effect: deny }
  - { action: shell, resource: "git reset*", effect: deny }
  - { action: shell, resource: "git stash*", effect: deny }
  - { action: subagent, resource: "*", effect: deny }
---
