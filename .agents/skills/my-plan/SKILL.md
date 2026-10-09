---
name: my-plan
description: >-
  Scope a task before any code is written: explore how it currently works,
  surface every open decision — including ones never raised — ask them, and
  flag consequential risks.
  TRIGGER — invoke whenever the user wants a task explored, scoped, or
  planned before code is written (e.g. "how would we approach X", "plan this
  out", "what would it take to do X", "scope this change", "plan this out in
  depth", "what do we need to decide before starting X"). SKIP when they want
  it built — use my-build instead.
compatibility: Requires native subagent delegation with codebase read access.
---

Task: the thing the user just asked about.

Before scoping, check native subagent support. If unavailable, report
`Unsupported: my-plan requires native subagents` and stop. Do not substitute
inline exploration for the required subagent.

Do not edit product files or write code. When the harness permits writes,
write only run artifacts under `.agents/work/`. Follow
[durable progress](~/.agents/references/progress.md) for run selection,
checkpoints, and fingerprint-validated knowledge. Load a linked or
unambiguous matching run before new exploration. Reuse its decisions and
validate relevant cards before trusting them.

If writes are prohibited, return an artifact-ready plan and distilled
exploration handoff for `my-build` to persist at startup.

1. Use a narrowly scoped native explorer; add others for useful independent
   questions. Follow
   [Scheduling](~/.agents/references/progress.md#scheduling) for distinct
   questions and stable evidence; do not repeat an investigation. Resume the
   recorded explorer for each scope. Follow recovery rules before replacement.
   Give each explorer the full task context and its scope. Have it report
   how the code works today: real `file:line` locations and patterns to reuse.
   Keep raw search noise out of your context; work from its distilled report.
   Record each scope and native ID immediately when writes are allowed.
   Persist important discoveries and source fingerprints before final handoff.
2. Enumerate every open decision the task leaves unresolved — including ones
   never raised. Hunt across each category:
   - **Technical** — approach, libraries, patterns, data model/API shape.
   - **Behavioral** — edge cases, defaults, error handling, invalid input.
   - **Scope** — what is in vs. out; adjacent work that must not be touched.
   - **Consequence** — hard-to-reverse or high blast-radius choices
     (schema/API changes, deleted data, breaking changes, security/perf).
3. Triage each decision: **if this is wrong, how hard is rework later?**
   Score importance and rework cost.
   - **High importance + high rework cost** → must ask.
   - **Low on either axis** → decide yourself. Note the choice and a
     one-line reason. Do not ask just to be thorough.
   When unsure which bucket applies, ask.
4. For each decision that cleared the bar, have a recommended answer ready
   with a one-line reason, plus realistic alternatives and trade-offs.
5. Use the native question tool when available. Batch questions within its
   limits and list your recommendation first. Otherwise ask in conversation.
   Wait for answers before proceeding. If an answer reveals another
   high-bar decision, ask that too.
6. Separately, call out risks that need no decision but should be known
   before work starts (perf cliffs, migration pain, security exposure).
7. Once every decision is resolved, write the finalized scope: files that
   would change, decisions made (asked and autonomous) with reasons, and an
   ordered step list for `my-build`. When writes are allowed, save
   `plan.md`, `state.md`, and relevant knowledge cards. Include the absolute
   run path. Otherwise include the same content for startup persistence.

Keep it concrete. If the task is trivial once explored, say so and skip
ceremony rather than manufacturing decisions.
