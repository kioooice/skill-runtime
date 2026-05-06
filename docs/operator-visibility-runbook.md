# Operator Visibility Runbook

## Purpose

This runbook keeps the operator-facing visibility path narrow and explicit.

Use it to answer three questions:

1. is there a current local operator summary?
2. if there is, is the exported dashboard snapshot fresh enough to trust?
3. if not, which read-only command should refresh or inspect the state next?

## Entry Roles

Use these commands for different jobs:

- `operator-summary`
  - summary-first local inspection
  - returns the full local operator summary
  - can explicitly refresh persisted local gate-status snapshots
  - also reports the current dashboard export state under `dashboard_export`
- `dashboard`
  - visual read-only inspection
  - renders local or global HTML
  - may refresh persisted gate-status snapshots and the stable export first when explicitly asked
- `runtime-events`
  - raw event-log inspection
  - answers whether the runtime lane participated and what follow-up it suggested

These are complementary, not competing surfaces.

## Standard Local Path

### 1. Inspect Current Summary State

```bash
python -m skill_runtime.cli operator-summary
```

This returns:

- the current local summary payload
- `operator_status_refresh.refreshed`
- `operator_status_refresh.gates`
- `operator_status_refresh.generated_at`
- `quality_gates.*.freshness.status`
- `dashboard_export.available`
- `dashboard_export.freshness_status`
- `dashboard_export.output_path`
- `dashboard_export.generated_at`
- `dashboard_export.refreshed`

Use this first when you want a scriptable answer and do not need HTML.

If a persisted gate snapshot is already present, use `quality_gates.provider_quality.freshness.status`, `quality_gates.utility_search_quality.freshness.status`, and `quality_gates.workflow_search_quality.freshness.status` to decide whether a gate-status refresh is actually needed.

### 2. Refresh Persisted Gate Status Before Returning The Summary

```bash
python -m skill_runtime.cli operator-summary --refresh-operator-status
```

Use this when:

- provider, utility-search, or workflow-search status is unavailable or stale
- you want `.skill_runtime/operator_status/*.json` refreshed from the current evaluator baselines
- you want the returned summary to reflect those refreshed gate snapshots immediately

This is explicit. It does not promote skills, apply evolution candidates, or execute recommended host operations.

### 3. Refresh The Stable Dashboard Export Without Rendering HTML

```bash
python -m skill_runtime.cli operator-summary --refresh-dashboard-export
```

Use this when:

- you want the stable `.skill_runtime/dashboard/operator-summary.json` export refreshed
- you do not need the dashboard page yet

This remains read-only with respect to runtime lifecycle actions. It only refreshes the stable dashboard summary export.

### 4. Refresh Gate Status And Dashboard Export Together

```bash
python -m skill_runtime.cli operator-summary --refresh-operator-status --refresh-dashboard-export
```

Use this when you want the summary command itself to refresh both the local gate-status index and the stable dashboard export before returning.

### 5. Render The Dashboard

```bash
python -m skill_runtime.cli dashboard --open
```

Use this when you want the visual read-only surface and the current export is already good enough.

### 6. Refresh Then Render The Dashboard

```bash
python -m skill_runtime.cli dashboard --refresh-operator-summary --open
```

Use this when you want the visual surface and also want the stable export refreshed in the same step.

### 7. Refresh Gate Status, Refresh Export, Then Render The Dashboard

```bash
python -m skill_runtime.cli dashboard --refresh-operator-status --refresh-operator-summary --open
```

Use this when you want the visual path itself to refresh both the persisted gate-status snapshots and the stable export before rendering HTML.

## Runtime Event Path

Use `runtime-events` when the question is about lane participation rather than inventory or freshness:

```bash
python -m skill_runtime.cli runtime-events --limit 20
```

This is the right entry for questions such as:

- did the runtime lane participate?
- was the task used, entered, or skipped?
- what next action did the runtime recommend?

## Global Visual Path

```bash
python -m skill_runtime.cli dashboard --global --scan-root D:\02-Projects --open
```

Use the global dashboard when the question is cross-workspace visibility rather than local runtime state.

When `--global` is combined with `--refresh-operator-status` or `--refresh-operator-summary`, those refreshes still apply only to the current root passed through `--root`. Scanned sibling projects are rendered from whatever local files they already expose.

## Recommended Default Order

For local operator checks, use this order:

1. `operator-summary`
2. `operator-summary --refresh-operator-status` if gate status is missing or stale
3. `operator-summary --refresh-dashboard-export` if the export is missing or stale
4. `operator-summary --refresh-operator-status --refresh-dashboard-export` if you want both refreshed in one command
5. `dashboard --open` if current status is already good enough
6. `dashboard --refresh-operator-status --refresh-operator-summary --open` if you want one visual refresh path
7. `runtime-events` only when you need event-level evidence

## Boundary

This runbook does not:

- execute host operations
- promote skills
- apply evolution candidates
- turn dashboard into a control plane

It standardizes visibility and explicit local status refresh only.
