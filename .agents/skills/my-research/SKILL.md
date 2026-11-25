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

Before research, check native subagent support and `_my-explorer`. If
either is missing, report
`Unsupported: my-research requires native subagents and its explorer role`
and stop. Do not substitute inline research.

Do not edit files or write code. Follow
[orchestration](~/.agents/references/orchestration.md).

1. Restate the question in one sentence. Ask once if two readings diverge.
2. Brainstorm distinct sub-questions and competing possibilities, then
   dispatch `_my-explorer` lanes per
   [Parallel fan-out](~/.agents/references/orchestration.md#parallel-fan-out).
   Give each lane the full question, its single scope, and where to look
   (codebase, web, or both).
3. On `NEEDS_CONTEXT`, answer what you can and resume that explorer; ask
   the user only when blocked.
4. Judge each possibility from merged evidence: `supported` (evidence
   agrees), `ruled out` (evidence contradicts), or `open` (undecided or
   unchecked).

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

Omit the Possibilities table when there are no real alternatives. Stop
after the answer; start `my-plan` only if asked.
