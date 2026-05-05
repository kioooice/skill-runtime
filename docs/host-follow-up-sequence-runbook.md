# Host Follow-Up Sequence Runbook

## Purpose

Walk one operator through the three current follow-up recommendation families without widening automation:

1. `background_hint`
2. `distill_trajectory`
3. `review_evolution_candidate`

This is a host-integration runbook, not a dashboard task.

## Sequence

### Step 1 - Reuse hint without automatic execution

Use a strong reusable task with one required input missing.

Expected result:

- reuse decision stays `background_hint`
- top-level recommendation is `execute_skill`
- missing inputs remain explicit

### Step 2 - Capture a real maintainer workflow

Capture an observed maintainer task record such as `demo/maintainer_review_cleanup/observed_task.json`.

Expected result:

- capture succeeds
- top-level recommendation is `distill_trajectory`
- alternate promote operations remain available but are not automatic

### Step 3 - Finalize a concrete existing-skill gap

Finalize a successful task payload that contains explicit `skill_gap.evidence` and `skill_gap.proposed_changes`.

Expected result:

- learning decision becomes `improve_existing_skill_candidate`
- top-level recommendation is `review_evolution_candidate`
- the review action remains manual and confirmation-backed

## Acceptance Standard

The sequence passes when the host can render one concrete next step at each stage without reading nested payload-specific shapes.

## Non-Goals

- Do not auto-execute the hinted skill in Step 1
- Do not auto-promote the captured workflow in Step 2
- Do not auto-apply the evolution candidate in Step 3
