---
name: my-explain
description: >-
  Explain a file, symbol, or concept at a high level.
  TRIGGER — invoke whenever the user asks what something is or does, or how it
  works (e.g. "what does X do", "explain this function", "how does X work",
  "walk me through this file"). SKIP when the question is specifically about a
  third-party package/library — use my-deps instead.
---

Explain the file, symbol, or concept the user named.

1. For cross-cutting topics spanning multiple modules when `_my-explorer`
   is available, dispatch lanes per
   [Parallel fan-out](~/.agents/references/orchestration.md#parallel-fan-out)
   (keep single-file or single-symbol questions inline):
   - Entry points and callers.
   - Core implementation, state, and types.
   - Tests, config, and edge-case behavior.
2. Always include tests when reading code — they clarify intent.
3. Synthesize a tight explanation with concrete `file:line` references:
   - **What it is / does** — purpose in one or two sentences.
   - **How it fits** — role in the larger flow and callers/dependents.
   - **Key pieces** — core functions, types, or steps.
   - **Gotchas** — non-obvious constraints or failure modes.
