---
name: my-tidy
description: >-
  Clean up the current diff without changing behavior.
  TRIGGER — invoke whenever the user wants the current diff cleaned up or
  polished before committing (e.g. "clean this up", "tidy the diff", "polish
  this before I commit"). SKIP for a logic or coverage review — use
  my-review. my-build already runs the enforcer for clean-code checks.
---

Clean up only the working-tree diff (`git diff` plus staged) without
changing behavior.

1. Inspect the working-tree diff. Run the project's formatter/linter and
   tests (via `my-test`) to establish a clean baseline.
2. When `_my-enforcer` is available, dispatch fresh `_my-enforcer` lane(s)
   per [Parallel fan-out](~/.agents/references/orchestration.md#parallel-fan-out)
   (split by disjoint file clusters when broad). Supply the frozen diff
   and note there are no prior reviewer findings.
3. Apply Important and Minor shrink findings without changing logic or
   public APIs — apply small cuts yourself, or dispatch `_my-implementer`
   on disjoint file sets under
   [Scheduling](~/.agents/references/orchestration.md#scheduling) (mark the
   brief non-behavioral: preserve behavior, add no new test seams).
4. If subagents or `_my-enforcer` are unavailable, apply the code and prose
   rules in `~/.agents/AGENTS.md` to the diff directly.
5. Re-run the formatter/linter and tests to confirm behavior is unchanged,
   then summarize what changed.
