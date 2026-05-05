# Host Follow-Up Recommendation Contract

## Purpose

Keep operator-facing follow-up actions consistent across reuse planning, runtime participation, and learning capture.

The host should not need to inspect nested payloads or special-case each workflow family to decide what to render next.

## Top-Level Fields

Every `AgentOrchestrationResult` may expose these top-level fields:

- `recommended_next_action`
- `recommended_reason`
- `recommended_host_operation`
- `available_host_operations`

These fields are the host-facing contract for "what should happen next".

## Current Rules

### Reuse planning

- `auto_execute`
  - No follow-up is required before execution because the reusable skill has already been selected and run.
- `background_hint`
  - Bubble a top-level `execute_skill` recommendation.
  - The host can render the recommended skill directly without searching nested search payloads.
- `skip`
  - No follow-up recommendation is required.

### Learning capture

- `observed_only`
  - No top-level recommendation unless the capture payload itself emits one.
- `new_skill_candidate`
  - Bubble the captured trajectory follow-up to the top level.
  - Current preferred next action: `distill_trajectory`.
- `improve_existing_skill_candidate`
  - Bubble the evolution review follow-up to the top level.
  - Current preferred next action: `review_evolution_candidate`.

### Evolution lifecycle

- After `review_evolution_candidate`
  - Preferred next action: `apply_evolution_candidate`.
- After `apply_evolution_candidate`
  - Preferred next action: `rollback_evolution_candidate`.
  - `governance_report` remains available as an alternate follow-up.
- After `rollback_evolution_candidate`
  - Preferred next action: `governance_report`.

## Host Rendering Rule

The host should prefer the top-level recommendation fields whenever they are present.

Nested payload recommendations remain useful as provenance, but they are no longer the primary rendering contract.

## Non-Goals

- This contract does not widen automatic execution.
- This contract does not authorize write operations without explicit confirmation where confirmation is already required.
- This contract does not force every result to carry a recommendation; `None` is valid when no concrete next action is warranted.
