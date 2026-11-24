# Writing skills

Use this when you create or edit a skill, a role, `AGENTS.md`, or a
doc that an agent reads. The default fix is to delete, not to explain.

## Loads

- **Context load** is the cost of always-loaded text: an `AGENTS.md`
  line, or a skill description. Pay it only when the agent must reach
  the material on its own.
- **Cognitive load** is the cost of remembering a document exists. A
  user-invoked skill (`disable-model-invocation: true`) pays this
  instead. Use it when only the user should start the flow.

A **context pointer** names out-of-context material and when to load
it. Front-load the trigger. One trigger per distinct case.

## Levers

- Put ordered actions in the main file. Push branch-only reference
  behind a pointer.
- End each step on a clear completion criterion: the agent must tell
  done from not-done, and the criterion must demand enough work.
- Prefer a short leading word the model already knows (`tight`,
  `red`, `frontier`, `seam`) over a restated phrase.
- Keep each meaning in one place. Do not restate what the environment
  already shows (`--help`, a config file, a directory layout).
- Delete a sentence that does not change behaviour versus the model
  default (a **no-op**). Prompt the target behaviour. Do not steer by
  prohibition unless you cannot phrase a positive rule.
