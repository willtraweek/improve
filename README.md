# improve

A lean fork of [shadcn/improve](https://github.com/shadcn/improve): audit a codebase, judge what is worth changing, and write plans another agent can execute independently. The plan is the product.

This fork keeps the advisor workflow and every invocation mode, removes generic audit tutorials and repeated rules, and replaces the long plan template with a compact handoff contract. It trusts the model's judgment about depth, delegation, and implementation detail.

## Install for Claude Code, Codex, and Grok

Requires Python 3.9+ and a Unix-like filesystem.

```sh
git clone https://github.com/willtraweek/improve.git
cd improve
python3 scripts/install.py          # preview
python3 scripts/install.py --apply  # replace the prior version
python3 scripts/install.py --check  # verify the installed snapshot
```

The installer copies only `skills/improve/` to `~/.agents/skills/improve`, creates Claude and Grok links, removes the separate legacy Codex copy, and removes Improve's obsolete skills CLI tracking entry. Old payloads are archived outside skill discovery under `~/.local/state/improve/backups/`. Other skills and their tracking entries are preserved. Failed filesystem operations trigger rollback.

Codex discovers the shared directory directly; Claude and Grok use their personal skill directories. The installed snapshot is independent of this checkout. Rerun the installer after updating the fork, then start fresh agent sessions to reload skills. `--home /path/to/test-home` supports isolated installation.

Alternatively, install through the [Agent Skills CLI](https://github.com/vercel-labs/skills):

```sh
npx skills add willtraweek/improve
```

That uses the CLI's own host selection and update management; the local installer above additionally migrates the old installation layout. Use one method for ongoing updates.

## Use

In Claude Code and Grok, invoke `/improve`. In Codex, invoke `$improve`.

| Request | Result |
|---|---|
| `improve` | Evidence-based audit, prioritized findings, then selected plans |
| `improve quick` / `improve deep` | Narrow hotspots / broader coverage |
| `improve security` (or another focus) | Focused assessment |
| `improve branch` | Branch changes and callers, with introduced vs. pre-existing findings |
| `improve next` / `features` / `roadmap` | Grounded product options |
| `improve plan <description>` | Investigate and specify one change |
| `improve review-plan <file>` | Verify and tighten a plan against current code |
| `improve execute <plan>` | Separate executor in a worktree, followed by advisor review |
| `improve reconcile` | Refresh evidence, dependencies, and completion status |
| `improve ... --issues` | Publish selected plans to GitHub with explicit authorization |

The advisor writes only plan documents. Plans include evidence, scope, decisions, an execution sequence, actual verification commands, and a baseline for detecting drift. Existing plan backlogs are reconciled. Product directions stay separate from defects.

Give the advisor your desired scope and authority: “Audit this repo and choose the top two improvements to plan” permits it to select without another check-in. An ordinary audit asks which findings should become plans.

The [upstream example](examples/001-extract-shadow-config-resolution.md) remains as provenance. It illustrates a detailed handoff; its older rigid template and status conventions are not requirements for this fork.

## Size and validation

The installed skill contains one entrypoint and two references, loaded when planning or following through. Research notes, tests, examples, and installer code are not installed as prompt resources.

See [modernization notes](docs/modernization.md) for primary sources, measurements, design decisions, and validation limits.

```sh
python3 scripts/measure.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

## License

MIT © shadcn. Fork maintained by willtraweek; upstream history and attribution are preserved.
