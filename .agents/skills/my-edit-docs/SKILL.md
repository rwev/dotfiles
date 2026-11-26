---
name: my-edit-docs
description: >-
  Edit agent, skill, reference, or rule markdown by section and anchor, then
  run the doc lint.
  TRIGGER — invoke whenever the user wants agent instructions, skills,
  references, or other `~/.agents` docs changed (e.g. "reword the reviewer",
  "add a rule to my-build", "rename this verdict"). SKIP for code changes.
---

Edit the docs the user named. Keep the meaning unless the user asked to
change it. Edit in the dotfiles repo that `~/.agents` links to.

## Process

1. Find the target by heading or `<a id>` anchor, not by matching prose.
   Read the whole section before you edit it.
2. Search the repo for the heading slug, the anchor, and each token you
   change. Edit the one source. Fix links; do not copy text.
3. Use the exact tokens in [Terms](~/.agents/references/terms.md). To add or
   rename a token, edit that file in the same change.
4. Keep each file on its [schema](~/.agents/references/terms.md#schemas).
   Follow [Anchors](~/.agents/references/terms.md#anchors).
5. Keep role detail in the agent file. A skill states intent, agents, lanes,
   and merge, and links to the rest.
6. Write per [Writing prose](~/.agents/AGENTS.md#writing-prose).
7. Run `python3 -m unittest tests.test_docs` from the repo root. Fix each
   failure, then run the full suite.

## Report back

List the changed sections by file and anchor, and the lint result.
