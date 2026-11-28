---
description: Security-focused audit of a diff or named code area — injection, auth, secrets, unsafe deserialization, crypto, dependencies, configuration. Read-only by instruction; some harnesses also grant a shell.
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
