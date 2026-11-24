---
name: my-retro
description: >-
  Look back on a coding session and propose improvements to the agent
  environment, not the product code.
  TRIGGER — invoke whenever the user wants a retrospective on a session
  (e.g. "retro this", "what should we change so this goes better next
  time", "improve the agent environment"). SKIP for a code-quality
  review of a diff — use my-review. SKIP for capturing session notes —
  use my-capture-knowledge.
---

Session: the current conversation, or a session log the user named.

Read [writing-skills](~/.agents/references/writing-skills.md) before you
propose a steering-file or skill change. Do not edit files. Propose
candidates, then wait.

1. Read the session record. Every candidate must point at a specific
   moment in it. Discard generic advice.
2. Look only in these categories, and only when the session showed the
   problem:
   - **Navigation** — the agent took too long to find a file or fact.
     Propose a pointer from a file it already reads.
   - **Checks** — a mistake a tool could have caught, or no lint, type,
     test, or CI guardrail. Prefer a deterministic check over a prose
     rule. If a check exists but is unwired, say to wire it.
   - **Reviewer standards** — the reviewer missed a judgement call.
     Propose a rule for the reviewer, not the implementer, and not a
     new always-loaded `AGENTS.md` line.
   - **No-ops** — a steering line that did not change behaviour.
     Propose to delete it.
   - **Access** — the agent needed information it could not reach.
     Propose a concrete way to expose it.
3. Present candidates, most severe first. For each: the moment, the
   proposal, and where it would live. Nothing changes until the user
   picks one.
