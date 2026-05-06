# Maintainer Review Cleanup Mainline Runbook

Date: 2026-05-05

## Purpose

Exercise the second maintainer mainline end to end using the existing review cleanup demo.

This runbook follows:

- `docs/maintainer-review-cleanup-mainline-acceptance.md`

The goal is to prove the governed workflow:

`review comments -> maintainer cleanup plan -> explicit runtime boundary -> governed learning artifact`

## What This Runbook Uses

- Demo input: `demo/maintainer_review_cleanup/review_comments.json`
- Expected plan: `demo/maintainer_review_cleanup/expected_cleanup_plan.md`
- Observed task: `demo/maintainer_review_cleanup/observed_task.json`

## Expected Current Boundary

At the time this runbook was written, review cleanup remains outside the phase-one Codex default runtime lane.

That means:

- the Codex-facing runtime gate should still be callable
- current classification may return:
  - `bucket: default-out`
  - `runtime_lane_status: skipped`
- this is acceptable for the current product boundary

The value here is governed support for maintainer workflow learning, not silent review automation.

## Step 1 - Validate The Demo Inputs

From the repository root:

```powershell
python -m json.tool demo/maintainer_review_cleanup/review_comments.json > $null
python -m json.tool demo/maintainer_review_cleanup/observed_task.json > $null
```

Expected result:

- both commands succeed

## Step 2 - Review The Maintainer-Facing Expected Output

Open:

- `demo/maintainer_review_cleanup/expected_cleanup_plan.md`

Check that the plan contains:

- grouped cleanup items
- maintainer-facing wording
- required fixes
- follow-up work
- no unreviewed implementation mutation

If the output is not useful to a maintainer, the workflow is not useful.

## Step 3 - Check The Runtime Gate Boundary

Run the Codex-facing gate in a temporary runtime root:

```powershell
$repoRoot = (Get-Location).Path
New-Item -ItemType Directory -Force .tmp_review_cleanup_mainline | Out-Null
python -m skill_runtime.cli --root .tmp_review_cleanup_mainline codex-run --task-description "Group pull request review comments into a maintainer cleanup plan." --working-directory "$repoRoot" --risk-level low --task-kind workflow --disable-silent-reuse
```

Expected current result:

- command succeeds
- output includes a `task_classification`
- current boundary may return:
  - `bucket: default-out`
  - `runtime_lane_status: skipped`
- the reason should explain that the task is dominated by open-ended reasoning

Interpretation:

- this is acceptable today
- it means the runtime is intentionally conservative around review judgment
- it does not make the maintainer workflow invalid

## Step 4 - Prove The Learning Capture Path

Use the observed task demo to capture the workflow:

```powershell
python -m skill_runtime.cli --root .tmp_review_cleanup_mainline capture-trajectory --file demo/maintainer_review_cleanup/observed_task.json --task-id maintainer_review_cleanup_mainline_demo --session-id demo_review_cleanup_mainline
```

Expected result:

- command succeeds
- `.tmp_review_cleanup_mainline/trajectories/maintainer_review_cleanup_mainline_demo.json` exists
- the output recommends `distill_trajectory`
- no active skill is silently promoted

Interpretation:

- the workflow already leaves a governed learning artifact
- the project can support real maintainer review work without widening the silent runtime lane

## Step 5 - Judge The Mainline

This runbook passes if all of these are true:

1. The demo inputs are valid.
2. The expected cleanup plan is useful to a maintainer.
3. The runtime gate remains explicit, even if it stays conservative.
4. The observed task can be captured into a trajectory.
5. The follow-up remains explicit instead of silently mutating the library.

## Optional Step 6 - Prove A Generated Workflow Skill, Not Only A Captured Trajectory

If you want to verify that the current provider-backed loop can go all the way to a generated, promoted, and reusable workflow skill for this maintainer task, run:

```powershell
python scripts/smoke_review_cleanup_provider_loop.py
```

Expected result:

- command exits successfully
- output JSON includes:
  - `"promoted": true`
  - `"audit_status": "passed"`
  - `"execute_status": "completed"`
  - `active_skill_file`
  - `reuse_output_path`
- the sandbox contains:
  - generated staging skill
  - promoted active skill
  - reused cleanup-plan artifact
  - reused metadata artifact

Interpretation:

- this proves the repository can generate one real maintainer-facing workflow skill instead of only stopping at `capture -> recommendation`
- it still does **not** mean `maintainer_review_cleanup` should automatically become a default active workflow-search skill in the repository
- it remains a bounded positive control for a useful generated workflow

## What A Failure Looks Like

Treat the run as failed if any of these happen:

- the cleanup plan is only a raw comment dump
- the next maintainer action is unclear
- the runtime gate crashes or gives no useful explanation
- capture fails or does not create a trajectory
- the flow silently promotes a skill

## Current Conclusion

With the current product boundary, this mainline already proves:

- Skill Runtime can support a real maintainer review workflow
- governed learning still works even when the runtime lane should remain conservative

What it does not prove yet:

- that review cleanup belongs in `default-in`
- that silent reuse should take over open-ended review planning

That is acceptable for now.

## Optional Cleanup

```powershell
Remove-Item -Recurse -Force .tmp_review_cleanup_mainline
```
