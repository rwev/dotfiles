---
description: Read-only codebase and web research for one scoped question. Dispatch with the full task context and the scope — it has no other context.
mode: subagent
permissions:
  - { action: edit, resource: "*", effect: deny }
  - { action: shell, resource: "*", effect: allow }
  - { action: shell, resource: "git commit*", effect: deny }
  - { action: shell, resource: "git checkout*", effect: deny }
  - { action: shell, resource: "git reset*", effect: deny }
  - { action: shell, resource: "git stash*", effect: deny }
  - { action: webfetch, resource: "*", effect: allow }
  - { action: subagent, resource: "*", effect: deny }
---
