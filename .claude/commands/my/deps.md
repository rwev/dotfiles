---
description: >-
  Explain a dependency — why it's here and what uses it.
  TRIGGER — invoke whenever the user asks about a specific third-party
  package/library: why it's there, what uses it, or whether it's needed (e.g.
  "why do we have X", "what uses this package", "can we remove X").
argument-hint: [dependency name]
---

Investigate the dependency: $ARGUMENTS

1. Confirm where it's declared (manifest/lockfile) and what version/range.
2. Find where it's actually used in the codebase (imports/usages), with `file:line` refs.
3. Explain what it provides and why the project needs it.
4. Assess: is it a direct dependency or transitive? Actively used or dead weight? Is
   there a lighter/std-library alternative, or would removing it break something?

Be factual and cite real usages. If it looks unused or replaceable, say so, but don't
remove or change anything unless I ask.
