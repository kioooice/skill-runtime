# CLI Recommendation Presentation Integration Plan

Date: 2026-05-06

## Goal

Add the smallest safe CLI/operator text surface for recommendation presentation without changing JSON payload shape, runtime recommendation decisions, or governed follow-up boundaries.

## Current Evidence

The current evidence already covers:

- fixture payload dogfood
- real payload rendering runbook
- one real CLI payload capture and rendering path
- placement decision favoring CLI/operator text before dashboard placement

That is enough to justify a narrow CLI integration. It is not evidence for dashboard-first work, runtime-decision changes, or wider `default-in`.

## Chosen Surface

Chosen first surface:

- CLI/operator text output

Audit companion:

- keep the original JSON payload unchanged and available

## Proposed CLI Behavior

Default behavior stays the same:

- CLI commands continue to print the normal JSON response to `stdout`

New optional behavior:

- when the operator explicitly requests recommendation rendering, CLI prints human-readable recommendation text to `stderr`

Why `stderr`:

- it preserves `stdout` as the machine-readable audit payload
- it avoids changing command result shape
- it gives operators a readable next-step surface in the same CLI flow

## Flag Design

Recommended flag for the first slice:

```powershell
--render-recommendation text
```

Scope for the first slice:

- only `capture-trajectory`

Rationale:

- `capture-trajectory` already has a real validated recommendation-bearing path
- this keeps the integration narrow and avoids a cross-command CLI redesign

## Acceptance Criteria

- default CLI JSON output remains unchanged
- explicit flag adds operator-facing recommendation text without replacing JSON
- operator can see `recommended_next_action`
- operator can see `recommended_host_operation.tool_name`
- `missing_inputs` is visible when present
- `requires_confirmation=true` is visible when present
- no automatic execution/promotion/apply boundary stays visible
- raw `requires_confirmation=false` is not presented as permission to auto-run
- the command does not execute `recommended_host_operation`
- the command does not promote a skill
- the command does not apply an evolution candidate

## Non-Goals

This slice does not:

- change runtime recommendation logic
- change JSON result shape
- add a new presentation helper
- add a dashboard integration
- add payload fixtures
- widen `default-in`
- automate promote/apply/host execution

## Why This Does Not Justify Widening `default-in`

This work only adds an optional rendering surface for already-produced recommendation payloads.

It does not prove:

- broader runtime-entry safety
- broader lifecycle automation safety
- broader workflow coverage
- any reason to widen `default-in`
