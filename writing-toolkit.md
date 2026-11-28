# Writing toolkit

## Summary

The code workflow is a poor fit for documentation, reference guides,
briefings, and research reports. A writing loop should parallelize source
gathering and claim checks, and keep the outline, the draft, the structural
edit, and the tightening pass on one thread. The built shape is `my-write`
plus `_my-drafter`, `_my-editor`, `_my-checker`, and `_my-tightener`.

## Background

Skills and specialist roles in this repo have settled around source code:
diffs, tests, and clean-code rules. Prose today is a global style rule plus
reports the coordinator writes in the conversation. The request was a writing
toolkit with the same kind of architecture — parallel lanes, a review phase,
and an enforcer — using fresh contexts so each role sees only what it needs.

## Investigation / Findings

Published long-form systems split research from writing. They parallelize
research, or sometimes isolated section drafts. A later single writer owns
voice and consistency.

- STORM runs perspective research in parallel. Each writer sees the topic,
  its own perspective, and its own history. One outline is curated afterward.
  Dropping that outline collapses quality. A later pass deletes repeats.
  Verifiability still did not beat outline-driven retrieval.
  https://arxiv.org/html/2402.14207v2
- Anthropic's research system gives each worker its own context and takes
  back a short digest. Tasks that need one shared context are a poor fit.
  A citation pass sees the finished report and the source documents.
  https://www.anthropic.com/engineering/multi-agent-research-system
- LangChain's open deep research kept multi-agent work on research. Parallel
  section writers produced pieces that disagreed.
  https://www.langchain.com/blog/open-deep-research
- A serial long-form drafter that can read earlier paragraphs beat a parallel
  plan-only variant on quality (91.6 vs 88.9) and coherence (93.3 vs 88.5).
  https://arxiv.org/abs/2408.07055
- Editors Canada puts structural editing first (audience, organization,
  missing substance). Stylistic editing cuts wording. Copy editing unifies
  terms and flags a missing citation.
  https://editors.ca/publications/professional-editorial-standards/structural-editing/
- FActScore and SAFE judge one standalone fact against evidence. FACTS
  Grounding fails a response on a single unsupported claim. A short vague
  answer must not be able to game that score.
  https://arxiv.org/html/2305.14251
  https://arxiv.org/html/2403.18802
  https://arxiv.org/html/2501.03200
- Showing a judge an unfaithful chain of thought can swing the verdict.
  Rewriting only the reasoning, with the actions held fixed, raised false
  positives by up to 90%. https://arxiv.org/html/2601.14691v2
- Debate can beat one sample on facts. Equal-budget sampling often matches
  it, and agents sometimes drop a correct claim in order to agree.
  https://proceedings.mlr.press/v235/smit24a.html
  https://arxiv.org/abs/2509.05396
- ASD-STE100 is a controlled language for procedural technical text. It is
  not the right sheet for a briefing or general correspondence.
  https://asd-ste100.org/STE_faq.html

This repo already constrains a new skillset:

- Prose rules live in `.agents/AGENTS.md`. `my-capture-knowledge` writes one
  session note and uses no subagent. `my-write` is the prose review loop.
- A new role needs `name` and `description`, then `Process`, optional
  `Rules`, and `Report back`. New tokens go in `.agents/references/terms.md`
  first. Fan-out is 5. The lane brief is the whole context.
  `.agents/references/terms.md`, `.agents/references/orchestration.md`
- The installer emits a native agent only when all four harness templates
  exist. Install tests name nine roles. `install/agents.sh`,
  `tests/test_install.py`
- `_my-reviewer` and `_my-enforcer` expect a diff, tests, and code-cruft
  rules. They should stay on that work.

## Architecture / Design

`my-write` is the coordinator. Detail stays in the role files, so the skill
and the roles do not repeat each other. `my-capture-knowledge` stays the
session note.

The brief is the contract. It names the audience, the purpose, the genre
(procedure, reference, report, or briefing), the length, the term sheet, and
the questions the piece must answer. Approve that brief before a draft
exists.

Loop:

1. Source lanes return short packs: a claim, a URL or `file:line`, and a
   quote. They do not write the piece.
2. One outline call reads those packs and freezes the section list.
3. One drafter writes from the brief, the outline, the term sheet, and the
   assigned sources.
4. A fresh editor checks audience, structure, and missing substance.
5. The same drafter applies substance fixes. A fresh editor runs again.
   Stop and ask after two failed attempts on the same finding.
6. Checker lanes split the approved draft into standalone claims. Each lane
   sees one claim and the passage it cites.
7. The drafter fixes unsupported claims.
8. A fresh tightener cuts repetition, unifies terms, and flags a missing
   citation. It does not add facts or move sections.
9. The drafter applies the cuts. The tightener runs only after the editor
   has approved.

A procedure uses the existing plain-technical rules, including ASD-STE100
where the text is procedural. A briefing or a report uses a plain-language
sheet: lead with the point, and use one term per meaning.

What each role is given:

| Role      | Sees                                             | Left out                                              |
| --------- | ------------------------------------------------ | ----------------------------------------------------- |
| Source    | One question, the output schema, where to look  | Other lanes and the draft                             |
| Drafter   | Approved brief, outline, term sheet, its sources | Search traces and the parent chat                     |
| Editor    | Brief, outline, full draft, source list          | Drafter's reasoning and any hoped-for verdict         |
| Checker   | One atomic claim and the cited passage           | The rest of the draft and the drafter's reasoning     |
| Tightener | Approved draft, term sheet, genre style sheet    | New facts, section moves, and the drafter's reasoning |

The checker scale in `.agents/references/terms.md` is `Grounded` and
`Ungrounded` because `supported` is already a research-result label.
`Needs context` is off the scale for every verdict role.

| Role      | Scale                         |
| --------- | ----------------------------- |
| Editor    | `Approved`, `Needs substance` |
| Tightener | `Approved`, `Needs cuts`      |
| Checker   | `Grounded`, `Ungrounded`      |

Independent reference pages may use parallel drafters after the outline is
frozen. One editor then reads the full text and removes repeats. That path
is optional. It is a poor fit for a briefing or any piece that has to hold
one voice.

Designs that the sources do not support:

| Design                                                               | Result    | Why                                                                                |
| -------------------------------------------------------------------- | --------- | ---------------------------------------------------------------------------------- |
| Parallel research, one drafter, then editor, checkers, and tightener | supported | Matches the research, editing, and claim-check sources above.                      |
| Parallel section writers as the default                              | ruled out | Coherence drops, and the sections disagree.                                        |
| Reuse the code reviewer and enforcer                                 | ruled out | Those roles judge diffs, tests, and code cruft.                                    |
| Self-critique in the drafter's context                               | ruled out | The critic shares the draft, and a reasoning trace can swing a judge.              |
| Debate until the writers agree                                       | ruled out | Equal-budget sampling often matches it, and agreement can drop a true claim.       |
| STE for every genre                                                  | ruled out | STE is for procedural technical text.                                              |
| One `my-write` skill, detail in the roles                            | supported | Matches this repo's schema. An overlap of role text fails doc lint.                |
| Reuse `_my-explorer` as the claim checker                            | open      | It can fetch a source. Its prompt answers one question and does not judge a claim. |
| Diataxis as a required outline                                       | open      | No studied pipeline used it. The brief may still name it.                          |

## Open Questions / Follow-ups

- No opened study separates "hide the generation prompt" from "hide the
  chain of thought."
- No opened study shows a final editor fully repairing parallel section
  drafts.
- Whether `_my-explorer` can check claims without a prompt change is
  untested.
- The ASD-STE100 rule text itself was not opened. The FAQ was.
- The skill, the roles, the harness templates, and the `terms.md` rows
  are in the repo. This note keeps the research.
