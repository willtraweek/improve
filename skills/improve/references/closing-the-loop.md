# Follow-through

Read the section for the requested mode.

## Execute

Dispatch implementation only when explicitly requested. Confirm the plan, completed dependencies, and current code match; include working-tree drift, not just changes since its recorded commit. Reconcile stale assumptions first. If isolation or a separate executor is unavailable, provide the handoff and explain the limitation.

Create an isolated worktree at a recorded base commit, without disturbing the user's branch. If the plan depends on uncommitted source changes, resolve that baseline before dispatch; do not silently omit or commit them. Give one executor the complete plan (it may be uncommitted), worktree path, relevant project instructions, and scope. Use the user's model choice when supported; otherwise choose an available suitable executor without assuming provider-specific model names or tool syntax.

The executor may edit and commit only inside its worktree; it must report changed files, checks and actual results, deviations, and blockers. The advisor owns the plan index. Dependency setup and verification may run inside the worktree; external side effects still need authorization.

Review the complete change against the recorded base, including committed, staged, unstaged, and untracked files. Read the code and tests, verify scope and intent, and rerun the done criteria in isolation. A clean working-tree diff after a commit is not proof of no changes.

Render APPROVE, REVISE, or BLOCK with evidence. Send specific revision requests to the executor; after two unsuccessful revision rounds, mark BLOCKED and explain. Documented, in-scope adaptations are judged against the intended outcome. Approval marks REVIEWED, with worktree/branch and verification results; DONE requires verification in the target branch. Leave integration to the user's authorized workflow. Do not merge or push as part of this mode.

## Reconcile

Read the index and relevant plans. Check whether REVIEWED work actually landed before marking DONE, and whether DONE criteria still hold. Investigate BLOCKED work; flag abandoned IN PROGRESS work. Recheck TODO evidence and baselines, refresh drifted assumptions, and retire findings fixed elsewhere. Preserve history and report what is ready to execute, changed, or still blocked. Use checks that respect the advisor's working-tree boundary.

## Issues

Publish only with `--issues` or equivalent explicit authorization. Check authentication, target repository, and visibility. Public disclosure of vulnerability details or credential locations needs specific authorization; prepare local plans while it is unresolved. Do not ask again if that disclosure was already authorized.

Reuse issue URLs already recorded in plans; check for matching existing issues before creating any. Publish each selected plan using a structured body or `gh issue create --body-file`, then record its URL in the plan and index. If publication fails, preserve the local artifacts and report what remains. Do not silently change an existing issue's content or visibility.
