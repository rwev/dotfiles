---
description: Security-focused audit of a diff or named code area — injection, auth, secrets, unsafe deserialization, crypto, dependencies, configuration. Dispatch with the target (diff range or file/feature) — it has no other context. Read-only, with no edit/write tools.
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
