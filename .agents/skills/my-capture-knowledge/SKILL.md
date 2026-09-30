---
name: my-capture-knowledge
description: >-
  Capture the current session's work — analysis, learnings, investigation,
  root causes, architecture, and change set — into a well-organized local
  markdown file, always at ./ (project/cwd relative). TRIGGER — invoke
  whenever the user wants the current session's work preserved (e.g. "capture
  this knowledge", "write this up", "save what we learned", "document this
  investigation before we lose it"). SKIP for routine code comments or commit
  messages — this is for standalone knowledge capture, not code changes.
---

Distill everything of substance from this conversation — analysis, investigation,
root causes, architecture, decisions, and any change set — into a single
well-organized markdown file in the current directory (`./`), not a subdirectory.

1. Pick a filename: `kebab-case-topic.md` describing the subject (e.g.
   `auth-token-refresh-bug.md`). If the user gave a name or one was implied,
   use it. If a file with that name already exists in `./`, ask whether to
   append a dated section or overwrite — don't silently clobber it.
2. Review the full conversation and pull out only what has lasting value —
   skip tool-call noise, dead ends abandoned without a reason, and anything
   the user can already see by reading the code or git history. Never copy
   secrets, credentials, or tokens into the file, even if they appeared
   verbatim in logs or output during the session.
3. Write the file with whatever subset of these sections actually has content
   — omit any section with nothing to say, don't pad:
   - **Title** — one line, the topic.
   - **Summary** — 2-4 sentences: what was investigated/built and the outcome.
   - **Background** — why this came up, what problem or question started it.
   - **Investigation / Findings** — what was explored, what was learned, with
     `file:line` references where relevant.
   - **Root Cause(s)** — for bugs/incidents, the mechanism, stated plainly.
   - **Architecture / Design** — how the relevant system works or was designed,
     if that was part of the work.
   - **Changes Made** — files touched and what changed, if code was written.
   - **Open Questions / Follow-ups** — anything left unresolved or deferred.
4. Follow this repo's prose conventions: sparse bold/italics, bulleted lists
   over long paragraphs, sections/subsections, padded markdown tables where
   tables are used.
5. Confirm the file path once written. Don't commit it — that's a separate ask.
