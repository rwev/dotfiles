---
description: >-
  Explain a file, symbol, or concept at a high level.
  TRIGGER — invoke whenever the user asks what something is or does, or how it
  works (e.g. "what does X do", "explain this function", "how does X work",
  "walk me through this file"). SKIP when the question is specifically about a
  third-party package/library — use my:deps instead.
argument-hint: [file, symbol, or topic]
---

Explain: $ARGUMENTS

Give a high-level explanation aimed at someone new to this code:

1. **What it is / does** — the purpose in one or two sentences.
2. **How it fits** — where it sits in the larger flow and what calls or depends on it.
3. **Key pieces** — the important functions, types, or steps, and what each is responsible for.
4. **Gotchas** — anything non-obvious, surprising, or easy to get wrong.

Read the relevant code before answering. Prefer concrete references
(`file:line`) over generalities. Keep it tight — clarity over completeness.
