---
description: Security-focused audit of a diff or named code area — injection, auth, secrets, unsafe deserialization, crypto, dependencies, configuration. Dispatch with the target (diff range or file/feature) and what changed and why — it has no other context. Read-only by instruction; some harnesses also grant a shell.
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
