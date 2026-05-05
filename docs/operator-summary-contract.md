# Operator Summary Contract

## Purpose

`operator-summary` is the v1 read-only Operator Workbench summary for the local runtime.

Primary command:

```bash
python -m skill_runtime.cli --root . operator-summary
```

It is designed to be a stable data source for future operator surfaces, including the existing read-only dashboard, without requiring the dashboard to depend on ad hoc or unstable runtime files directly.

## v1 Top-Level Fields

`operator-summary` v1 returns these top-level fields:

- `root`
- `generated_at`
- `active_skills`
- `staging_candidates`
- `trajectories`
- `recent_runtime_events`
- `recommended_host_operations`
- `quality_gates`
- `safe_next_steps`
- `intentionally_not_automatic`
- `missing_or_unavailable`
- `non_automatic_explanation`

## Stable v1 Fields

These fields should be treated as stable for v1 consumers:

- top-level field names listed above
- `active_skills.count`
- `active_skills.items`
- `staging_candidates.count`
- `staging_candidates.items`
- `trajectories.count`
- `trajectories.items`
- `recent_runtime_events.count`
- `recent_runtime_events.items`
- `recommended_host_operations.count`
- `recommended_host_operations.items`
- `quality_gates.recent_audits.count`
- `quality_gates.recent_audits.items`
- `quality_gates.provider_quality`
- `quality_gates.utility_search_quality`
- `quality_gates.workflow_search_quality`
- `safe_next_steps`
- `intentionally_not_automatic`
- `missing_or_unavailable`
- `non_automatic_explanation`

For each persisted gate-status object under `quality_gates.*`, these fields are stable:

- `label`
- `status`
- `file_path`
- `report_status`
- `generated_at`
- `command`
- `summary`
- `baseline_comparison`
- `reason`

`status` is the availability state for operator consumption:

- `available`
- `unavailable`

`report_status` is the persisted evaluation result currently written by the evaluator scripts, such as `ok`.

## Fields That May Be Unavailable

Some v1 fields are intentionally allowed to be unavailable when local persisted state does not exist yet.

The main cases are:

- `quality_gates.provider_quality`
- `quality_gates.utility_search_quality`
- `quality_gates.workflow_search_quality`

When unavailable:

- `status` is `unavailable`
- `reason` explains why
- `file_path` is `null`
- `report_status` is `null`
- `generated_at` is `null`
- `command` is `null`
- `summary` is `null`
- `baseline_comparison` is `null`

This is an honest missing-state contract. `operator-summary` must not invent a pass result.

## Persisted Gate Status Input

`operator-summary` v1 reads local persisted gate-status files from:

- `.skill_runtime/operator_status/provider_quality.json`
- `.skill_runtime/operator_status/search_quality.json`
- `.skill_runtime/operator_status/workflow_search_quality.json`

These files are written only when the corresponding evaluator is run with `--write-operator-status`.

Evaluator scripts do not change their default behavior. Without the flag, they still print the same JSON report to stdout and do not write these operator-status files.

## Text Output Contract

The optional text form:

```bash
python -m skill_runtime.cli --root . operator-summary --format text
```

must express the same state groups as the JSON summary. It is not a separate narrative mode.

That means the text output should continue to reflect:

- skill inventory
- trajectory inventory
- recent runtime events
- recommended host operations
- recent audits
- persisted gate status availability and summary
- safe next steps
- intentionally non-automatic boundaries

## Dashboard Consumption Rule

The repository already has read-only local and global dashboard surfaces. v1 does not require rewriting them.

Future dashboard or operator-workbench consumption should follow this rule:

- consume stable `operator-summary` fields
- avoid depending on ad hoc or unstable low-level file shapes when a summary field already exists
- avoid depending on fields marked unavailable unless the UI explicitly handles that state

In practice, the lowest-risk future connection is:

- dashboard collector calls or merges `RuntimeService.operator_summary()`
- page rendering consumes the stable v1 fields above
- dashboard pages remain unchanged until the summary contract is stable enough to rely on

## What Will Not Execute Automatically

`operator-summary` is read-only.

It will not:

- execute a host operation
- run an evaluator script
- promote a skill
- promote a global Codex skill
- apply an evolution candidate
- archive duplicate candidates

It is a visibility surface, not a lifecycle executor.

## Why This Does Not Widen `default-in`

Better visibility does not justify broader automatic entry into the runtime lane.

This contract only improves operator understanding of:

- what the runtime currently contains
- what local gate status has been persisted
- what explicit next steps are available
- what remains intentionally non-automatic

That is useful precisely because it keeps the boundary inspectable before any future change to runtime entry policy. There is still no evidence here that supports widening `default-in`.
