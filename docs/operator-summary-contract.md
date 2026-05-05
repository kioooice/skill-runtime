# Operator Summary Contract

## Purpose

`operator-summary` is the v1 read-only Operator Workbench summary for the local runtime.

Primary command:

```bash
python -m skill_runtime.cli --root . operator-summary
```

Optional persisted gate-status refresh:

```bash
python -m skill_runtime.cli --root . operator-summary --refresh-operator-status
```

Optional export refresh:

```bash
python -m skill_runtime.cli --root . operator-summary --refresh-dashboard-export
```

It is designed to be a stable data source for future operator surfaces, including the existing read-only dashboard, without requiring the dashboard to depend on ad hoc or unstable runtime files directly.

## Dashboard Export Subset

The repository also exposes a stable dashboard-oriented subset through:

```bash
python scripts/export_operator_summary_for_dashboard.py --root .
```

This export writes `.skill_runtime/dashboard/operator-summary.json`.

The export is intentionally narrower than the full CLI/service `operator-summary` payload. It keeps stable summary fields only and adds explicit freshness-policy metadata so downstream collectors can evaluate whether the exported summary is still current enough to trust.

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
- `operator_status_refresh`
- `dashboard_export`

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
- `operator_status_refresh`
- `dashboard_export`

Stable `operator_status_refresh` fields are:

- `refreshed`
- `gates`
- `generated_at`

Stable `dashboard_export` fields are:

- `refreshed`
- `available`
- `freshness_status`
- `output_path`
- `generated_at`

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

The current collector/export path is even narrower:

- `export_operator_summary_for_dashboard.py` writes a stable subset to `.skill_runtime/dashboard/operator-summary.json`
- `collect_dashboard_data(...)` reads that file when present
- `collect_global_dashboard_data(...)` reads that file per project when present
- collector code computes freshness from `generated_at` plus exported policy fields instead of letting page code infer staleness ad hoc

## Freshness Semantics For The Dashboard Export

The dashboard export now carries stable freshness-policy inputs:

- top-level `generated_at`
- top-level `freshness_policy`
- per-gate `generated_at`
- per-gate `freshness_policy`

Stable `freshness_policy` fields are:

- `basis`
- `stale_after_seconds`

Current policy values:

- exported operator-summary snapshot: `stale_after_seconds = 86400`
- persisted quality-gate snapshots: `stale_after_seconds = 259200`

These policy values are exported so collector/data consumers can compute freshness without relying on hidden constants.

## Collector-Computed Freshness Metadata

When the existing collector layer reads the dashboard export, it computes freshness metadata in memory.

Stable collector-facing freshness fields are:

- top-level `freshness.status`
- top-level `freshness.age_seconds`
- top-level `freshness.stale_after_seconds`
- top-level `freshness.reason`
- per-gate `freshness.status`
- per-gate `freshness.age_seconds`
- per-gate `freshness.stale_after_seconds`
- per-gate `freshness.reason`

Current freshness states are:

- `fresh`
- `stale`
- `unknown`

`unknown` is used when freshness cannot be evaluated honestly, for example when `generated_at` is missing or invalid.

The global collector also exposes project-level freshness summary metadata:

- `operator_summary_freshness_status`
- `operator_quality_gate_freshness_statuses`

This remains collector/data-layer state only. Dashboard pages still do not render it yet.

## What Will Not Execute Automatically

`operator-summary` is read-only.

It will not:

- execute a host operation
- run an evaluator script
- promote a skill
- promote a global Codex skill
- apply an evolution candidate
- archive duplicate candidates

`--refresh-operator-status` is the one explicit exception to the fully passive path: it refreshes only the persisted local gate-status files under `.skill_runtime/operator_status/` so the summary can show current gate status without requiring three separate manual script invocations.

Refreshing the dashboard export does not change the lifecycle boundary. `--refresh-dashboard-export` writes only the stable `.skill_runtime/dashboard/operator-summary.json` snapshot for downstream read-only consumers.

It is a visibility surface, not a lifecycle executor.

## Why This Does Not Widen `default-in`

Better visibility does not justify broader automatic entry into the runtime lane.

This contract only improves operator understanding of:

- what the runtime currently contains
- what local gate status has been persisted
- what explicit next steps are available
- what remains intentionally non-automatic

That is useful precisely because it keeps the boundary inspectable before any future change to runtime entry policy. There is still no evidence here that supports widening `default-in`.
