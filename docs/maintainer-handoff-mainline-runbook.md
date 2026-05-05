# Maintainer Handoff Mainline Runbook

Date: 2026-05-05

## Purpose

Exercise the first real maintainer mainline end to end using the existing handoff continuation demo.

This runbook follows the acceptance path defined in:

- `docs/maintainer-mainline-acceptance.md`

The goal is not to prove dashboard behavior. The goal is to prove the core workflow:

`continuation request -> runtime gate check -> maintainer-facing continuation brief -> governed learning artifact`

## What This Runbook Uses

- Demo input: `demo/maintainer_handoff_continuation/handoff_inputs.json`
- Expected brief: `demo/maintainer_handoff_continuation/expected_continuation_brief.md`
- Observed task: `demo/maintainer_handoff_continuation/observed_task.json`

## Expected Current Boundary

At the time this runbook was written, the current Codex-facing runtime lane does **not** silently take over handoff continuation as a phase-one default-in family.

That means:

- the runtime gate should still be callable
- the gate may classify this task as `guarded-in`
- `runtime_lane_status: skipped` is acceptable for the current boundary
- this is not a failure of the mainline

The core acceptance check is that the workflow remains governed and explicit, not that every phase is already auto-executed.

## Step 1 - Validate The Demo Inputs

From the repository root:

```powershell
python -m json.tool demo/maintainer_handoff_continuation/handoff_inputs.json > $null
python -m json.tool demo/maintainer_handoff_continuation/observed_task.json > $null
```

Expected result:

- both commands succeed

## Step 2 - Review The Maintainer-Facing Expected Output

Open:

- `demo/maintainer_handoff_continuation/expected_continuation_brief.md`

Check that the brief contains:

- current goal
- current plan position
- completed work
- next action
- open gaps
- current decision status

This is the user-visible value of the mainline. If this brief is not useful, the workflow is not useful.

## Step 3 - Check The Runtime Gate Boundary

Create a temporary runtime root and run the Codex-facing gate:

```powershell
New-Item -ItemType Directory -Force .tmp_handoff_mainline_runbook | Out-Null
python -m skill_runtime.cli --root .tmp_handoff_mainline_runbook codex-run --task-description "Continue from HANDOFF.md and produce a continuation brief for the next Codex session." --working-directory "D:\02-Projects\vibe" --risk-level low --task-kind workflow --disable-silent-reuse
```

Expected current result:

- command succeeds
- output includes a `task_classification`
- current boundary may return:
  - `bucket: guarded-in`
  - `runtime_lane_status: skipped`
- the reason should explain that the task looks local and reusable, but does not yet match a phase-one default-in family

Interpretation:

- this is acceptable today
- it means the runtime gate observed the task boundary
- it does **not** mean the maintainer workflow is invalid

## Step 4 - Prove The Learning Capture Path

Use the observed task demo to capture the workflow into a temporary runtime root:

```powershell
python -m skill_runtime.cli --root .tmp_handoff_mainline_runbook capture-trajectory --file demo/maintainer_handoff_continuation/observed_task.json --task-id maintainer_handoff_continuation_demo --session-id demo_handoff_continuation
```

Expected result:

- command succeeds
- `.tmp_handoff_mainline_runbook/trajectories/maintainer_handoff_continuation_demo.json` exists
- the output recommends `distill_trajectory`
- no active skill is silently promoted

Interpretation:

- the task can already leave a governed learning artifact
- the lifecycle remains explicit
- the workflow is captured without pretending that promotion should happen automatically

## Step 5 - Judge The Mainline

The runbook passes if all of these are true:

1. The demo inputs are valid.
2. The expected continuation brief is clearly maintainer-facing.
3. The runtime gate can be checked explicitly, even if the current lane classification is conservative.
4. The observed task can be captured into a trajectory.
5. The follow-up remains explicit instead of silently mutating the library.

## What A Failure Looks Like

Treat the run as failed if any of these happen:

- the brief is only an internal runtime dump
- the next action is vague or missing
- the gate crashes or produces no usable explanation
- capture fails or does not create a trajectory
- the flow silently promotes a skill

## Current Conclusion

With the current product boundary, this mainline already proves two important things:

- Skill Runtime can support a real maintainer continuation workflow without relying on chat memory
- the lifecycle after success is still governed and explicit

What it does **not** prove yet:

- that handoff continuation already belongs in automatic phase-one default-in reuse
- that the finalizer path for this workflow is fully host-driven instead of demonstrated through `capture-trajectory`

That is acceptable for now. The next step is to decide whether this task family should remain `guarded-in`, or whether later evidence justifies moving it into a stricter default-in family.

## Optional Cleanup

```powershell
Remove-Item -Recurse -Force .tmp_handoff_mainline_runbook
```
