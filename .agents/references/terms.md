# Terms

Use these exact tokens in agents, skills, and references. Do not paraphrase
them. Add a token here before you use it. `tests/test_docs.py` checks this file
against the others.

## Roles

| Token                   | Meaning                                                    |
| ----------------------- | ---------------------------------------------------------- |
| `coordinator`           | The main agent. It spawns lanes, merges reports, commits.  |
| `lane`                  | One subagent with one narrow scope in a fan-out.           |
| `_my-explorer`          | Read-only research for one scoped question.                |
| `_my-implementer`       | Writes one task, test first.                               |
| `_my-reviewer`          | Read-only review of logic, regressions, and coverage.      |
| `_my-enforcer`          | Read-only clean-code review that shrinks the diff.         |
| `_my-security-reviewer` | Read-only security audit.                                  |

## Statuses

`_my-explorer` and `_my-implementer` end with `Status:` and one of `DONE`,
`DONE_WITH_CONCERNS`, `BLOCKED`, or `NEEDS_CONTEXT`. The explorer uses only
`DONE` and `NEEDS_CONTEXT`.

## Verdicts

Read-only roles end with `Verdict:`. Each scale goes from least to most
strict. `Needs context` is off the scale: missing input blocks the work.

| Role                    | Scale                                          |
| ----------------------- | ---------------------------------------------- |
| `_my-reviewer`          | `Approved`, `Needs fixes`                      |
| `_my-enforcer`          | `Approved`, `Needs shrinks`                    |
| `_my-security-reviewer` | `Ship as-is`, `Ship with fixes`, `Do not ship` |
| all three               | `Needs context`                                |

## Severities

`Critical`, `Important`, `Minor`, most severe first. Each role file defines
them for its job. A finding starts with `file:line`.

## Caps

| Cap          | Value | Rule                                                                 |
| ------------ | ----- | -------------------------------------------------------------------- |
| fan-out      | 5     | [fanout-cap](~/.agents/references/orchestration.md#fanout-cap)       |
| fix attempts | 2     | [fix-cap](~/.agents/references/orchestration.md#fix-cap)             |

## Schemas

| Files            | Frontmatter                             | `##` headings, in order                          |
| ---------------- | --------------------------------------- | ------------------------------------------------ |
| `_my-*.md`       | `name`, `description`                   | `Process`, `Rules?`, `Report back`               |
| `my-*/SKILL.md`  | `name`, `description`, `compatibility?` | `Process`, `Dispatch?`, `Rules?`, `Report back?` |

`?` marks an optional item. Use no other `##` heading. Put the scope and
guards before the first heading.

## Anchors

- A heading is an anchor. Link to it as `path#github-slug`.
- To link to one rule, start it with `<a id="kebab-id"></a>`. Give an ID only
  to a rule that another file links to. Do not renumber or reuse an ID.
