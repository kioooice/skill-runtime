# Maintainer Review Cleanup Demo

## Purpose

This demo shows how Skill Runtime can support a real open-source maintenance workflow: turning pull request review comments into a grouped cleanup plan that a maintainer can review before merge.

It is intentionally local-only. It does not require API keys, GitHub access, or a remote model.

## Files

- Input fixture: `demo/maintainer_review_cleanup/review_comments.json`
- Expected maintainer output: `demo/maintainer_review_cleanup/expected_cleanup_plan.md`
- Observed task record: `demo/maintainer_review_cleanup/observed_task.json`

## What It Demonstrates

- Review comments can be normalized into required fixes and follow-up work.
- The output is a maintainer-facing action plan, not an unreviewed code change.
- The workflow can be captured as a trajectory through `capture-trajectory`.
- Capturing the workflow does not automatically promote a skill.

## Verify The Fixture

From the repository root:

```powershell
python -m json.tool demo/maintainer_review_cleanup/review_comments.json > $null
python -m json.tool demo/maintainer_review_cleanup/observed_task.json > $null
```

## Capture The Workflow

Use a temporary runtime root so the demo does not write into the repository's real `trajectories/` directory:

```powershell
New-Item -ItemType Directory -Force .tmp_review_cleanup_demo | Out-Null
python -m skill_runtime.cli --root .tmp_review_cleanup_demo capture-trajectory --file demo/maintainer_review_cleanup/observed_task.json --task-id maintainer_review_cleanup_demo --session-id demo_review_cleanup
```

Expected result:

- the command succeeds
- `.tmp_review_cleanup_demo/trajectories/maintainer_review_cleanup_demo.json` exists
- no active skill is promoted

Optional cleanup:

```powershell
Remove-Item -Recurse -Force .tmp_review_cleanup_demo
```

## Maintainer Value

This is the first open-source readiness demo because it maps directly to the Codex for Open Source story: maintainers spend real time reviewing pull requests, resolving comments, and deciding what must happen before merge. Skill Runtime gives that repeated workflow a governed path from observed work to reusable skill candidate, while keeping review and promotion explicit.
