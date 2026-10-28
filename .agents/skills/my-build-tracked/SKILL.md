---
name: my-build-tracked
description: >-
  my-build with saved run state, checkpoints, and baselines under
  `.agents/work/`.
  TRIGGER — invoke only when the user asks for a tracked, resumable, or
  persisted build, or names a `.agents/work` run to resume. SKIP otherwise —
  use my-build.
compatibility: Requires native subagents and _my-implementer and _my-reviewer roles.
---

Follow [my-build](~/.agents/skills/my-build/SKILL.md) in full. Read
[durable progress](~/.agents/references/progress.md) before you start or
resume. Add its rules:

- **Plan** — Load a matching run, or save the `my-plan-tracked` handoff, or
  explore and save a new run.
- **Check** — Record identity, authorization, and task status in `state.md`.
  Capture each task baseline before writers start.
- **Implement** — Persist phases, claims, native IDs, and `Files:`. Add the
  tracked payload items to each dispatch.
- **Resume** — Follow Run recovery before new dispatch.
