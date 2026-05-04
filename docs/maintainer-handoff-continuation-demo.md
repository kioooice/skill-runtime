# Maintainer Handoff Continuation Demo

## Purpose

This demo shows how Skill Runtime supports long-running open-source maintenance work by turning durable project state into a concise continuation brief for the next Codex session.

It demonstrates why repository state files are more reliable than chat-only memory for ongoing maintainer workflows.

## Files

- Input fixture: `demo/maintainer_handoff_continuation/handoff_inputs.json`
- Expected maintainer output: `demo/maintainer_handoff_continuation/expected_continuation_brief.md`
- Observed task record: `demo/maintainer_handoff_continuation/observed_task.json`

## What It Demonstrates

- Long-running project work can be resumed from durable repository state.
- The brief captures goal, stage, completed work, next action, gaps, and decision status.
- The workflow is understandable without loading prior chat history.
- The workflow can be captured as a trajectory without promoting an unreviewed skill.

## Verify The Fixture

```powershell
python -m json.tool demo/maintainer_handoff_continuation/handoff_inputs.json > $null
python -m json.tool demo/maintainer_handoff_continuation/observed_task.json > $null
```

## Capture The Workflow

Use a temporary runtime root:

```powershell
New-Item -ItemType Directory -Force .tmp_handoff_continuation_demo | Out-Null
python -m skill_runtime.cli --root .tmp_handoff_continuation_demo capture-trajectory --file demo/maintainer_handoff_continuation/observed_task.json --task-id maintainer_handoff_continuation_demo --session-id demo_handoff_continuation
```

Expected result:

- the command succeeds
- `.tmp_handoff_continuation_demo/trajectories/maintainer_handoff_continuation_demo.json` exists
- no active skill is promoted

Optional cleanup:

```powershell
Remove-Item -Recurse -Force .tmp_handoff_continuation_demo
```

## Maintainer Value

Maintainers often pause and resume work across days, review cycles, or release windows. This demo shows how Codex can use durable repository context to continue work accurately, while Skill Runtime captures the pattern for future governance.
