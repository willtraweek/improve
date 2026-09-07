# Modernizing Improve

## Evidence and intent

Forked from [shadcn/improve at 03369ee](https://github.com/shadcn/improve/tree/03369ee6d7cafbfcecc4346539b05b3dc0a603bb), inspected September 7, 2026. Preserve its central idea: capable advice produces self-contained plans for another executor.

Anthropic reports removing over 80% of Claude Code's system prompt for advanced Claude 5 models without measurable loss on its coding evaluations. Its recommendations include fewer blanket rules, less repeated guidance, and context loaded when needed. That is evidence for revisiting old scaffolding, not proof that shortening this skill improves every model. [Official article, July 24, 2026](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models)

Compound Engineering's [v3.23.0 release, August 22, 2026](https://github.com/EveryInc/compound-engineering-plugin/releases/tag/compound-engineering-v3.23.0) reduced several entrypoints by 71–91%, largely by moving procedures into references. Its [follow-up findings](https://github.com/EveryInc/compound-engineering-plugin/blob/main/docs/solutions/skill-design/size-driven-skill-restructure.md) distinguish entrypoint savings from full-task consumption: models sometimes read references upfront, and full paths may consume the same text. Conditional rules also regressed when compressed into absolutes. Accordingly, this fork measures the entire installed skill and preserves operational conditions instead of chasing a fixed percentage.

## Changes

- Removed the generic audit playbook. The entrypoint retains audit breadth and criteria for accepting findings.
- Replaced scripted phases, fixed agent counts, repeated prohibitions, and provider-specific executor names with outcomes and decision criteria.
- Replaced the 1,359-word plan template with a small contract. Plans still need evidence, scope, decisions, a sequence, baseline, and verification; their detail scales to the change.
- Kept execution, reconciliation, and publication guidance conditional. Normal assessment does not request that reference.
- Preserved the advisor boundary, secret redaction, fresh-context handoffs, dependency ordering, existing-backlog reconciliation, and evidence verification.
- Resolved instruction conflicts: applicable project guidance remains useful, user-authorized prioritization does not trigger another selection gate, and equivalent in-scope implementation choices are allowed.
- Corrected review semantics: compare the whole change against the worktree base, consider uncommitted drift, and distinguish REVIEWED work from DONE work in the target branch.

All original modes remain. `deep` now promises broader coverage with explicit limits rather than automatic exhaustive coverage. Planning produces a task-specific handoff rather than an identical set of sections for every change.

## Reproducible measurements

Run `python3 scripts/measure.py`. The default baseline is pinned to the upstream commit above. Counts are UTF-8 bytes, not tokens; no model-specific tokenizer or latency estimate is implied.

| Resource | Upstream bytes | Fork bytes | Reduction |
|---|---:|---:|---:|
| SKILL.md | 15,092 | 4,495 | 70.2% |
| references/audit-playbook.md | 13,343 | 0 | 100.0% |
| references/closing-the-loop.md | 7,317 | 3,078 | 57.9% |
| references/plan-template.md | 8,493 | 2,111 | 75.1% |
| **Total installed skill** | **44,245** | **9,684** | **78.1%** |

The normal audit used to explicitly load the entrypoint and playbook (28,435 bytes). The fork's assessment entrypoint is 4,495 bytes, an 84.2% reduction. Planning adds only its handoff contract. These are resource sizes, not measured session-token counts.

## Validation

- Skill Creator's frontmatter/scaffold validator passed; all skill reference links and Claude plugin JSON parsed successfully.
- Seven installer tests passed: preview/check are read-only; fresh/repeated install; migration and obsolete-reference removal; preservation of unrelated files/lock entries; safe replacement of symlinks; malformed lock and symlinked-root rejection; rollback after a simulated installation failure.
- A fresh agent used the skill on a disposable copy of `tests/fixtures/stockroom`, with the request: “Improve this small codebase with a quick audit. Choose the highest-value finding yourself and write one implementation plan for another agent. Keep the existing API decisions.” It found the negative-reservation defect, preserved zero-unit preview behavior and the single-process decision, ran the 3 passing baseline tests, and added only a plan and index. Tracked source remained unchanged.
- Independent contract review caught missing Git authority in standalone plans; the contract was corrected. A subsequent `review-plan` pass added the explicit authorization boundary while keeping status TODO.
- A second fresh agent received only the resulting plan and fixture, with explicit authorization to implement in that disposable copy. It needed no additional context. The added negative-reservation regression failed before the fix (4 tests, 2 failing subtests); after the guard and exact-stock test, all 5 tests passed. It preserved unknown-SKU precedence and the existing insufficient-stock behavior. No commit, publication, or integration was performed.
- The real installation passed `scripts/install.py --check`. Native `codex debug prompt-input` and `grok inspect --json` each listed exactly one updated Improve entry. Claude's personal skill path resolved to the same payload; no old Improve plugin was registered there.

These exercises covered quick assessment, automatic selection when authorized, plan writing/review, and a standalone execution handoff. They did not exercise every mode, live issue publication, or the complete `execute` orchestration. To repeat the behavioral exercise, copy the fixture to a disposable repository, initialize/commit its baseline, and give a fresh agent the request above and the skill path. Give another fresh agent only the resulting plan and a separate copy of that baseline.

Structural checks and small behavioral exercises cannot establish cross-model quality or performance. No Claude/Grok model A/B benchmark was run. The installer verifies discovery paths and exact payloads separately from model behavior.

## Installation design

Codex's documented shared skill root is `~/.agents/skills`; duplicate names can both appear, so the old separate `~/.codex/skills/improve` copy is removed. [Codex skill documentation](https://learn.chatgpt.com/docs/build-skills)

Claude uses `~/.claude/skills`. [Claude skill documentation](https://code.claude.com/docs/en/skills)

The installed Grok CLI's bundled documentation and `grok inspect --json` confirm personal/shared discovery, and inspection identifies the Improve path under `~/.grok/skills`. Claude and Grok retain links to the canonical snapshot. The installer backs up both old copies outside discovery, removes only Improve's stale skills CLI lock entry, and does not modify unrelated host configuration.
