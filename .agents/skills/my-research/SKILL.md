---
name: my-research
description: >-
  Answer a research question and brainstorm the possibilities around it.
  TRIGGER — invoke whenever the user wants a question researched, options
  explored, or approaches compared (e.g. "research X", "look into X",
  "what are the options for X", "brainstorm X", "compare approaches to X",
  "find out how X works"). SKIP for one file, symbol, or concept — use
  my-explain. SKIP for one dependency — use my-deps. SKIP for a bug or
  test failure — use my-debug. SKIP when they want work scoped before
  coding — use my-plan. SKIP when they want it built — use my-build.
compatibility: Requires native subagents and the _my-explorer role.
---

Question: the thing the user just asked about.

Before research, check native subagent support and the `_my-explorer` role.
If either is unavailable, report
`Unsupported: my-research requires native subagents and its explorer role`
and stop. Do not substitute inline research for the required subagent.

Do not edit files or write code. Follow
[orchestration](~/.agents/references/orchestration.md).

1. Restate the question in one sentence. When two readings would send the
   investigation different ways, ask once which reading to follow.
2. Brainstorm before you dispatch. List the distinct sub-questions and the
   possibilities worth checking. A possibility is a competing explanation,
   an approach, or an option. Send one `_my-explorer` per distinct
   question. Use one explorer when the question has one evidence target.
   Use fewer when fewer questions cover the topic. Use at most six, and
   merge related questions to stay inside that limit. Start them together
   so they run at the same time. Follow
   [Scheduling](~/.agents/references/orchestration.md#scheduling) for
   distinct questions and stable evidence; do not repeat an investigation.
   After an interruption, resume the same explorer under
   [Recovery](~/.agents/references/orchestration.md#recovery).
3. Give each explorer the full question and its narrow scope, including
   where to look: this codebase, the web, or both. You brainstorm. The
   explorer only checks its scope and reports evidence. Keep raw search
   noise out of your context. Work from its distilled report.
4. On `NEEDS_CONTEXT`, answer what you can, then resume that explorer. Ask
   the user only when you cannot answer.
5. Judge each possibility from the reports. Supported means the evidence
   agrees with it. Ruled out means the evidence contradicts it. Open means
   the evidence does not decide it. An idea you did not check stays open.

Write this block in the conversation:

```
## Answer
<direct answer to the question>

## Possibilities
| Possibility | Result                        | Why        |
| ----------- | ----------------------------- | ---------- |
| <name>      | supported, open, or ruled out | <evidence> |

## Evidence
- <confirmed finding — file:line or URL>

## Open
<unresolved questions, or "none">
```

Omit the Possibilities table when the question has no real alternatives.
Stop after the answer. Start `my-plan` only when the user asks to scope
the work.
