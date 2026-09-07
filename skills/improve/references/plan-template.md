# Handoff contract

A plan plus the repo must be sufficient for a fresh executor. Use the structure that makes this clear; omit irrelevant fields, not necessary context.

Include:

- **Outcome and evidence:** why the change matters, current behavior, exact paths/symbols, and concise excerpts where they prevent ambiguity. Verify citations from your own reads. Include relevant decisions, conventions, and a representative implementation/test to follow.
- **Baseline:** date, full commit SHA when available, and any relevant uncommitted state. An absent Git history is a stated limitation, not an invented SHA.
- **Scope and sequence:** files or components to change, important exclusions, dependencies, ordered implementation steps, and any load-bearing design decisions. Inline prerequisite outcomes so another plan need not supply missing context. State authorized Git/integration actions; the plan itself grants no permission to push, publish, or merge.
- **Verification:** exact repository commands with expected results, tests for the behavior being changed, and measurable done criteria. Identify commands not run and existing failures. Specify checks at meaningful milestones; don't invent a passing baseline or add tests that only mirror implementation.
- **Reconsideration conditions:** assumptions or scope changes that require reassessment, known risks, and material maintenance implications. Give the executor room for equivalent implementation choices within these boundaries.

Before execution, compare the baseline with current code, including staged, unstaged, and relevant untracked files. A committed diff alone misses working-tree drift. Refresh a plan when its assumptions no longer hold; a line-number shift alone need not block work.

The index records each plan's title, priority, dependencies, status, and relevant rejection/supersession rationale. Distinguish TODO, IN PROGRESS, BLOCKED, REVIEWED (approved in an isolated worktree), and DONE (verified in the target branch). Retain evidence links or review/worktree references when useful. Never infer that approval means integration.
