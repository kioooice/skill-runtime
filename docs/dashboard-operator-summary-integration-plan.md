# Dashboard Operator Summary Integration Plan

## Current Dashboard Data Flow

The existing read-only `dashboard` and `global-dashboard` surfaces already read local runtime state directly through collector functions:

- `skill_runtime.dashboard.collector.collect_dashboard_data(...)`
- `skill_runtime.dashboard.collector.collect_global_dashboard_data(...)`

Today the collector builds dashboard data from:

- `skill_store/*` metadata and `skill_store/index.json`
- `.skill_runtime/runtime_lane_events.jsonl`
- governance report data from `RuntimeService.governance_report()`
- platform inventory
- capability collections
- evolution candidate records

The current HTML pages render that collector output directly. They still do not render `operator-summary`, but the collector layer can now optionally read the exported `operator-summary` payload.

## Stable Operator Summary v1 Fields

`operator-summary` v1 is now the stable read-only lifecycle summary contract for operator-facing consumption.

Stable fields relevant to dashboard integration are:

- `generated_at`
- `freshness_policy`
- `active_skills.count`
- `staging_candidates.count`
- `trajectories.count`
- `recommended_host_operations.count`
- `quality_gates.provider_quality`
- `quality_gates.utility_search_quality`
- `quality_gates.workflow_search_quality`
- `safe_next_steps`
- `intentionally_not_automatic`
- `missing_or_unavailable`
- `non_automatic_explanation`

These are stable enough for a collector-level export because they express operator state without forcing the dashboard to depend on low-level storage layout.

## Fields Dashboard Can Safely Consume

The lowest-risk dashboard-facing subset is:

- `generated_at`
- top-level freshness-policy inputs for the exported summary
- count-only inventory summaries for active / staging / trajectories / recommended host operations
- quality-gate availability and persisted report summaries
- quality-gate freshness-policy inputs
- `safe_next_steps`
- `intentionally_not_automatic`
- `missing_or_unavailable`
- `non_automatic_explanation`

This is enough for the current collector layer to carry operator workbench state without pulling in the full `operator-summary` inventory item lists yet.

## Fields Dashboard Should Not Consume Yet

For now, dashboard should avoid taking a hard dependency on:

- full `active_skills.items`
- full `staging_candidates.items`
- full `trajectories.items`
- full `recent_runtime_events.items`
- full `recommended_host_operations.items`
- any field that exists only in ad hoc low-level files instead of the documented `operator-summary` contract

Those fields are useful for CLI inspection, but this slice does not need the dashboard page layer to depend on them yet.

## Why This Slice Does Not Change Page UI

The current product risk is not missing HTML. It is unstable cross-surface data coupling.

Changing dashboard pages now would:

- create avoidable UI churn
- make it easier to bind a page to fields we may still want to tighten
- blur the boundary between collector work and presentation work

This slice therefore stops at the collector/export layer. Existing dashboard pages remain unchanged.

## Minimal Collector Integration

This slice adopts the lowest-risk path: a read-only export surface.

Added pieces:

- `skill_runtime.dashboard.collector.collect_dashboard_operator_summary_data(...)`
- `skill_runtime.dashboard.collector.export_dashboard_operator_summary_data(...)`
- `scripts/export_operator_summary_for_dashboard.py`

The export flow is:

1. call `RuntimeService.operator_summary()`
2. keep only the stable subset intended for dashboard/operator workbench consumption
3. write it to `.skill_runtime/dashboard/operator-summary.json`

This export does not change existing dashboard HTML generation.

The current collector implementation now does two read-only things:

- `collect_dashboard_data(...)` includes `operator_summary` when `.skill_runtime/dashboard/operator-summary.json` exists
- `collect_global_dashboard_data(...)` annotates discovered projects with exported operator-summary availability and gate-status metadata when present

It now also computes freshness metadata at the collector layer:

- local collector enriches `operator_summary` with top-level and per-gate `freshness`
- global collector adds `operator_summary_freshness_status`
- global collector adds `operator_quality_gate_freshness_statuses`

This keeps freshness semantics out of page templates and avoids forcing UI code to interpret timestamps on its own.

## Consumption Direction

The current relationship is:

- current dashboard pages continue using their existing collector payloads and ignore the new operator-summary fields
- collector/data consumers can read `.skill_runtime/dashboard/operator-summary.json` through the existing collector layer
- a later page/UI slice can decide whether to render those fields

That keeps the page layer decoupled from unstable implementation details while letting `operator-summary` become the stable data source first.

## Boundaries

This integration remains read-only.

It does not:

- execute a host operation
- run evaluator scripts
- promote a skill
- apply an evolution candidate
- widen `default-in`

The export only improves lifecycle visibility. It is not evidence for broader automatic runtime entry.
