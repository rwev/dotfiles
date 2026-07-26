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
---

Task: the thing the user just asked about.

Do NOT edit files or write code — this is scoping only.

1. Dispatch a subagent (fork yourself, or the Explore agent type with full
   task context — it starts cold) to investigate the codebase and report
   back how it currently works: real `file:line` locations, existing
   patterns/utilities to reuse. Keep the raw search/read noise out of your
   own context; work from its distilled report for the rest of this process.
2. Enumerate every open decision the task leaves unresolved — including ones
   the master never raised or hinted at. Don't limit yourself to what was
   asked; actively hunt across each category:
   - **Technical** — approach, libraries, patterns, data model/API shape.
   - **Behavioral** — edge cases, defaults, error handling, what happens on
     invalid input.
   - **Scope** — what's in vs. explicitly out; anything adjacent that looks
     related but shouldn't be touched.
   - **Consequence** — anything hard to reverse or with blast radius beyond
     this change (schema/API changes, deleted data, breaking changes,
     security/perf implications, things other code or people depend on).
3. Triage every decision found in step 2 against one test: **if this is
   decided now and turns out wrong, how hard is it to rework later?**
   Score each on both importance (how much it shapes the outcome) and
   rework cost (effort/risk to undo or change course after the fact).
   - **High importance + high rework cost** → must ask. This is the bar for
     everything in step 4 — an unraised decision that clears it belongs in
     the questions just as much as one the master already flagged.
   - **Low on either axis** (cheap to change later, or barely affects the
     outcome) → decide it yourself. Pick the sensible default, note the
     choice and a one-line reason in the writeup, and move on — don't ask
     just to be thorough. Judgment calls like this are the autonomy the
     master is trusting you with.
   When genuinely unsure which bucket a decision falls in, ask — the cost of
   one extra question is far lower than building on the wrong foundation.
4. For each decision that cleared the bar, have a recommended answer ready
   with a one-line reason, plus the realistic alternative(s) and their
   trade-off.
5. Ask all of them via `AskUserQuestion`, batched (max 4 per call, your
   recommendation listed first). Anything that doesn't fit multiple choice,
   ask directly as plain text in the same pass. Wait for answers before
   proceeding — don't assume. If an answer reveals a new decision that also
   clears the bar in step 3, ask that one too — don't treat the first batch
   as final just because it was first.
6. Separately, call out risks and consequences that don't need a decision but
   the master should know about before work starts (perf cliffs, migration
   pain, security exposure, things likely to surprise them later).
7. Once every decision is resolved, write the finalized scope: files that
   would change and what each needs, the decisions made — both the ones
   asked and the ones you made autonomously, with reasons — and an ordered
   step list ready to hand to `/my-build`.

Keep it concrete throughout — no vague hand-waving, no ambiguity left
unresolved without either an answer or a stated reason it didn't need one.
If the task turns out to be trivial once explored, say so and skip the
ceremony rather than manufacturing decisions.
