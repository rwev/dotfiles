---
description: Read-only codebase and web research for one scoped question. Dispatch with the full task context and the scope — it has no other context.
mode: subagent
permission:
  edit: deny
  bash:
    "*": allow
    "git commit*": deny
    "git checkout*": deny
    "git reset*": deny
    "git stash*": deny
  webfetch: allow
  task: deny
---
