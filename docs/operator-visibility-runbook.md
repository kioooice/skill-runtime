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
  - also reports the current dashboard export state under `dashboard_export`
- `dashboard`
  - visual read-only inspection
  - renders local or global HTML
  - may refresh the stable export first when explicitly asked
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
- `dashboard_export.available`
- `dashboard_export.freshness_status`
- `dashboard_export.output_path`
- `dashboard_export.generated_at`
- `dashboard_export.refreshed`

Use this first when you want a scriptable answer and do not need HTML.

### 2. Refresh The Stable Dashboard Export Without Rendering HTML

```bash
python -m skill_runtime.cli operator-summary --refresh-dashboard-export
```

Use this when:

- you want the stable `.skill_runtime/dashboard/operator-summary.json` export refreshed
- you do not need the dashboard page yet

This remains read-only with respect to runtime lifecycle actions. It only refreshes the stable dashboard summary export.

### 3. Render The Dashboard

```bash
python -m skill_runtime.cli dashboard --open
```

Use this when you want the visual read-only surface and the current export is already good enough.

### 4. Refresh Then Render The Dashboard

```bash
python -m skill_runtime.cli dashboard --refresh-operator-summary --open
```

Use this when you want the visual surface and also want the stable export refreshed in the same step.

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

## Recommended Default Order

For local operator checks, use this order:

1. `operator-summary`
2. `operator-summary --refresh-dashboard-export` if the export is missing or stale
3. `dashboard --open` or `dashboard --refresh-operator-summary --open`
4. `runtime-events` only when you need event-level evidence

## Boundary

This runbook does not:

- run evaluator scripts
- execute host operations
- promote skills
- apply evolution candidates
- turn dashboard into a control plane

It standardizes visibility only.
