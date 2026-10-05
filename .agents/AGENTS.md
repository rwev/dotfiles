# Global rules

Use these personal defaults in every project. Follow applicable project
instructions and the harness instruction hierarchy. Explicit user instructions
override these defaults.

## Naming

- `_my-*` files are specialist agent roles. Dispatch them as native subagents.
- `my-*` directories are skills. Invoke them as workflows.
- `my-build`, `my-security`, `my-plan`, and `my-review` need native subagents.
- Stop as unsupported when a required role or subagent is missing.
- Do not replace independent review with self-review.

## Working style

- Be concise. Lead with the answer; skip preamble and restating the question.
- Do what was asked — no more, no less. Don't add scope, options, or "while I'm here" changes.
- When unsure about intent or a hard-to-reverse choice, ask instead of guessing.
- Report outcomes honestly: if something failed, was skipped, or is unverified, say so plainly.

## Writing code

- Match the surrounding code: its naming, structure, formatting, and idioms.
- Reuse what already exists (helpers, patterns, dependencies) before writing anything new.
- Don't add comments that just restate the code. Comment only non-obvious "why".
- Prefer the smallest change that solves the problem. Don't refactor unrelated code.
- Don't leave dead code, TODOs, or commented-out blocks behind.

## Writing prose

- Applies to documentation, prompts, and any other markdown or text files.
- Write in ASD-STE100 (Simplified Technical English): short sentences, one idea
  each, active voice, imperative mood for instructions, consistent terms.
- Also write with humanity — like a person talking to a person, not a manual
  talking to a machine.
- Use italics and bold sparingly.
- Prefer bulleted lists over large run-on paragraphs.
- Use sections and subsections to organize content.
- Format tables for correct markdown rendering, and pad columns so the raw source is also readable.

## Safety

- Ask before destructive or hard-to-undo actions (deleting files, dropping data, force-push, `rm -rf`).
- Ask before outward-facing actions (pushing, opening/commenting on PRs, deploying, sending anything external).
- Never commit or push unless explicitly asked. Never commit secrets, tokens, or credentials.
- Don't disable, skip, or weaken tests/checks to make something pass.

## Verifying

- Prefer running the code, tests, or linters over asserting it works.
- When you change behavior, check the change actually does what was intended before calling it done.
