# Maintainer Release Readiness Demo

## Purpose

This demo shows how Skill Runtime can support a release-prep workflow for open-source maintainers. It turns repository readiness inputs into a checklist that separates ready items, blockers, follow-ups, verification commands, and the release decision.

It is local-only and does not require API keys or network access.

## Files

- Input fixture: `demo/maintainer_release_readiness/release_inputs.json`
- Expected maintainer output: `demo/maintainer_release_readiness/expected_release_checklist.md`
- Observed task record: `demo/maintainer_release_readiness/observed_task.json`

## What It Demonstrates

- Release readiness can be represented as a repeatable maintainer workflow.
- Missing community files and verification gaps can be turned into clear blockers.
- The result maps to a maintainer decision: tag now, hold release, or create follow-up work.
- The workflow can be captured as a trajectory without promoting an unreviewed skill.

## Verify The Fixture

```powershell
python -m json.tool demo/maintainer_release_readiness/release_inputs.json > $null
python -m json.tool demo/maintainer_release_readiness/observed_task.json > $null
```

## Capture The Workflow

Use a temporary runtime root:

```powershell
New-Item -ItemType Directory -Force .tmp_release_readiness_demo | Out-Null
python -m skill_runtime.cli --root .tmp_release_readiness_demo capture-trajectory --file demo/maintainer_release_readiness/observed_task.json --task-id maintainer_release_readiness_demo --session-id demo_release_readiness
```

Expected result:

- the command succeeds
- `.tmp_release_readiness_demo/trajectories/maintainer_release_readiness_demo.json` exists
- no active skill is promoted

Optional cleanup:

```powershell
Remove-Item -Recurse -Force .tmp_release_readiness_demo
```

## Maintainer Value

This demo supports the open-source application story by showing how Codex-assisted release prep can be made repeatable and reviewable instead of living only in chat. It also directly exposes remaining public-readiness blockers.
