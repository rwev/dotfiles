---
name: my-plan-tracked
description: >-
  my-plan with saved run state under `.agents/work/`.
  TRIGGER — invoke only when the user asks for a tracked, resumable, or
  persisted plan, or names a `.agents/work` run to resume. SKIP otherwise —
  use my-plan.
compatibility: Requires native subagents and the _my-explorer role.
---

Follow [my-plan](~/.agents/skills/my-plan/SKILL.md) in full. Add the rules in
[durable progress](~/.agents/references/progress.md):

- Before exploration, load a linked or unambiguous matching run. Reuse its
  decisions. Validate relevant knowledge cards before you trust them.
- Give each explorer relevant cards. Tell it to report SHA256 fingerprints.
- Record each explorer scope and native ID immediately after dispatch.
- Persist important findings and fingerprints as knowledge cards.
- With the `## Plan` block, save `plan.md` and `state.md`. Give the absolute
  run path.
- If writes are prohibited, return the same content for `my-build-tracked`
  to save at startup.
