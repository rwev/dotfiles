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
compatibility: Requires native subagents and the _my-explorer role.
---

Task: the thing the user just asked about.

Before scoping, check native subagent support and the `_my-explorer` role.
If either is unavailable, report
`Unsupported: my-plan requires native subagents and its explorer role` and
stop. Do not substitute inline exploration for the required subagent.

Do not write product code. You may create or update `GLOSSARY.md` or an ADR
as specified below. Follow
[orchestration](~/.agents/references/orchestration.md).

1. Dispatch one `_my-explorer` per distinct, useful question, each with a
   narrow scope. Follow
   [Scheduling](~/.agents/references/orchestration.md#scheduling) for distinct
   questions and stable evidence; do not repeat an investigation. After an
   interruption, resume the same explorer under
   [Recovery](~/.agents/references/orchestration.md#recovery).
   Give each explorer the full task context and its scope. Have it report
   how the code works today: real `file:line` locations and patterns to reuse.
   Keep raw search noise out of your context; work from its distilled report.
2. Treat the work as a design tree. The frontier is every unresolved
   decision whose prerequisites are already settled. Hunt across each
   category, including decisions never raised:
   - **Technical** — approach, libraries, patterns, data model/API shape.
   - **Behavioral** — edge cases, defaults, error handling, invalid input.
   - **Scope** — what is in vs. out; adjacent work that must not be touched.
   - **Consequence** — hard-to-reverse or high blast-radius choices
     (schema/API changes, deleted data, breaking changes, security/perf).
3. Triage each frontier decision: **if this is wrong, how hard is rework later?**
   Score importance and rework cost.
   - **High importance + high rework cost** → must ask.
   - **Low on either axis** → decide yourself. Note the choice and a
     one-line reason. Do not ask just to be thorough.
   When unsure which bucket applies, ask.
   Finding facts is your job. Dispatch or resume an explorer for anything
   you can look up. Do not ask the user for a fact you can find. A running
   exploration only blocks questions that depend on it.
4. For each decision that cleared the bar, have a recommended answer ready
   with a one-line reason, plus realistic alternatives and trade-offs.
   Ask the whole askable frontier in one round. Number each question and
   list your recommendation first. Word each question so "yes" accepts
   that recommendation. Use the native question tool when available, and
   batch within its limits. Otherwise ask in conversation. Wait for
   answers before the next round. Then recompute the frontier. If an
   answer reveals another high-bar decision, include it in the next round.
5. If the repo has a `GLOSSARY.md`, use its terms and challenge a conflict
   at once. When a term resolves, write it there immediately — create the
   file at the repo root if it does not exist. Write only the term, a short
   definition, and a term to avoid if one exists. Do not put implementation
   detail in it. Offer an ADR under `docs/adr/` only when the decision is
   hard to reverse, surprising without context, and the result of a real
   trade-off. Otherwise leave the decision in the plan. Never write these
   files under an `.agents` path.
6. Separately, call out risks that need no decision but should be known
   before work starts (perf cliffs, migration pain, security exposure).
7. Once the frontier is empty, write a `## Plan` block in the conversation
   for `my-build`. Use this shape:

   ```
   ## Plan

   ### Decisions
   - <decision>: <choice> — <one-line reason>

   ### Seams
   - <public boundary to test at>: <what it catches>

   ### Slices
   | ID | Slice | Demo | Blocked by | Owned paths |
   | -- | ----- | ---- | ---------- | ----------- |
   | 1  | <name> | <end-to-end behaviour> | none | <paths> |

   ### Glossary
   - <term>: <short definition> (or "none")

   ### Findings
   - <file:line> — <fact>

   ### Risks
   - <risk, or "none">
   ```

   Each slice is a narrow, complete path through every layer this change
   touches. It must be demoable on its own. Size it to one implementer
   task. Give it the slices that must finish first. Put prefactoring
   first. For a wide mechanical refactor, use expand, then migrate in
   batches, then contract — not a vertical slice. Prefer existing seams
   to new ones, and the highest seam that still catches the behaviour.
   Confirm seams with the user before you close the plan.

Keep it concrete. If the task is trivial once explored, say so and skip
ceremony rather than manufacturing decisions.
