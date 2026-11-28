---
description: Cuts repetition, unifies terms, and flags a missing citation in an approved draft.
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
