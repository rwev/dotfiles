---
description: Implements one well-defined task via TDD (failing test, minimal code, pass, changed-file report). Dispatch with a single task's requirements plus scene-setting context — it has no other context.
mode: subagent
permissions:
  - { action: edit, resource: "*", effect: allow }
  - { action: shell, resource: "*", effect: allow }
  - { action: subagent, resource: "*", effect: deny }
---
