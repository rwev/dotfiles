---
name: my-write
description: >-
  Write a document with isolated research, drafting, editing, and tightening.
  TRIGGER — invoke whenever the user wants a document written (e.g. "write
  the guide", "draft a briefing", "produce a research report", "write this
  up for readers"). SKIP for a session note — use my-capture-knowledge.
  SKIP for a code change — use my-build.
compatibility: Requires native subagents and the _my-drafter, _my-editor, _my-checker, and _my-tightener roles.
---

Document: the piece the user just asked for.

Before any lane, check native subagents and `_my-drafter`, `_my-editor`,
`_my-checker`, and `_my-tightener`. If any are missing, report
`Unsupported: my-write requires native subagents and its drafter, editor,
checker, and tightener roles` and stop. Do not draft, edit, or tighten
in this chat.

When no sources were supplied, also require `_my-explorer`. If it is
missing, stop as unsupported and name that role. Do not research in this
chat.

Follow [Parallel fan-out](~/.agents/references/orchestration.md#parallel-fan-out)
and the attempt limit in
[fix-cap](~/.agents/references/orchestration.md#fix-cap).

## Process

1. Agree the brief before a lane starts. It records audience, purpose,
   genre (procedure, reference, report, or briefing), length, terms, the
   questions to answer, a path outside `.agents`, and a style sheet. A
   procedure points at the global
   [Writing prose](~/.agents/AGENTS.md#writing-prose) rules. Any other
   genre says to lead with the point and use one wording for one meaning.
2. If the user already supplied sources, skip the lanes and pass that
   set. Otherwise ask each `_my-explorer` a question whose answer holds
   one claim, one locator, and one quote, and read those from its normal
   report. Do not invent a merge.
3. Ask a fresh `_my-drafter` for the outline alone. Show it and wait.
   Outline approval is not commit approval.
4. Ask a fresh `_my-drafter` to compose at the brief's path. Use one
   drafter for the whole piece, except when the genre is reference and
   the approved outline says sections do not refer to each other. Then
   use one drafter per section, at most 5 section drafters at once.
5. Ask a fresh `_my-editor` to read the full text. Resume `_my-drafter`
   for substance findings, then ask a fresh editor again.
6. Break the accepted text into one-sentence claims with pronouns filled
   in. Dispatch `_my-checker` lanes. Resume `_my-drafter` for an
   `Ungrounded` claim, limited to evidence already returned, then check
   just those claims.
7. Ask a fresh `_my-tightener` only after the editor ended `Approved`.
   Resume `_my-drafter` to apply the shorter replacements. Leave the pull
   request unopened. Do not commit.

## Dispatch

- `_my-explorer`: the question, and where to look. Omit the piece and
  the other lanes.
- Outline writer: the brief, the style sheet, and the source list.
  Pass: outline. See
  [`_my-drafter`](~/.agents/agents/_my-drafter.md).
- Composition writer: the accepted brief, the style sheet, the approved
  outline, and the source list. Pass: draft.
  Each section brief includes the line `Independent reference sections`.
- `_my-editor`: the brief, the outline, the full text, and the source
  list. See [`_my-editor`](~/.agents/agents/_my-editor.md).
- `_my-checker`: one sentence and the passage it cites. Omit the piece.
  See [`_my-checker`](~/.agents/agents/_my-checker.md).
- `_my-tightener`: the accepted text, the style sheet, the terms, the
  genre, and the editor `Approved` line. See
  [`_my-tightener`](~/.agents/agents/_my-tightener.md).

## Rules

- Keep `_my-reviewer`, `_my-enforcer`, and `_my-implementer` off this loop.
- Two failed repairs of one finding end in a question to the user. That
  count is the
  [fix-cap](~/.agents/references/orchestration.md#fix-cap). This loop
  resumes `_my-drafter`. It does not send the retry to the code reviewer,
  enforcer, or implementer named in that anchor.
- Omit this chat, search logs, a writer diary, and any preferred ending
  from every lane.
- Do not attach the article, even though fan-out gives other lanes a
  target list.
- Checkers do not extract those sentences.

## Report back

Give the path, the editor verdict, any claim still `Ungrounded`, and the
tightener verdict.
