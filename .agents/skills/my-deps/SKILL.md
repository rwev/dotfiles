---
name: my-deps
description: >-
  Explain a dependency — why it's here and what uses it.
  TRIGGER — invoke whenever the user asks about a specific third-party
  package/library: why it's there, what uses it, or whether it's needed (e.g.
  "why do we have X", "what uses this package", "can we remove X").
---

Investigate the dependency the user named. Do not remove or change anything
unless asked.

## Process

1. When `_my-explorer` is available, dispatch lanes per
   [Parallel fan-out](~/.agents/references/orchestration.md#parallel-fan-out)
   (run inline if narrow or unavailable):
   - **Codebase lane(s):** manifest/lockfile declaration and version range
     across workspace packages (do not assume root), `file:line` usages,
     direct vs. transitive status, and stdlib/repo alternatives.
   - **Upstream lane:** what the package provides, maintenance status,
     lighter alternatives, and known security advisories for the declared
     version.
2. Merge findings into a factual summary citing real `file:line` usages
   and sources, noting if the package appears unused or replaceable.
