---
name: my-scope
description: >-
  Explore and plan a change without editing anything.
  TRIGGER — invoke whenever the user wants a change explored or planned before
  code is written (e.g. "how would we approach X", "plan this out", "what
  would it take to do X", "scope this change"). SKIP when the user wants the
  work actually implemented — use my-build instead.
---

Task: the thing the user just asked about.

Plan this before writing any code. Do NOT edit files — this is scoping only.

1. Explore the relevant code and understand how it currently works.
2. List the files that would need to change, and what changes each needs.
3. Note anything that reuses existing patterns/utilities rather than adding new code.
4. Call out risks, edge cases, and anything ambiguous that needs a decision from me.
5. End with a short, ordered step list I could hand back to you to implement.

Keep it concrete — reference real `file:line` locations. If the task is trivial,
say so and skip the ceremony.
