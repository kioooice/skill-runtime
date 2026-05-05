# Host Recommendation Presentation Plan

Date: 2026-05-05

## Purpose

Improve how a host or operator presents governed follow-up recommendations without changing the underlying recommendation decisions.

This plan follows:

- `docs/v0.2-core-quality-summary.md`
- `docs/workflow-gap-active-skill-decision.md`
- `docs/host-follow-up-recommendation-contract.md`
- `docs/host-follow-up-recommendation-dogfood.md`
- `docs/host-follow-up-sequence-runbook.md`

## Why Governed Learning Follow-Up Stays Host-Facing

`governed_learning_follow_up` should stay host-facing because it is not a reusable workflow skill.

The relevant operations are lifecycle operations:

- `distill_trajectory`
- `audit_skill`
- `promote_skill`
- `review_evolution_candidate`
- `apply_evolution_candidate`
- `rollback_evolution_candidate`

These operate on runtime governance artifacts such as trajectories, staging files, evolution candidates, reviews, and backups. They are not ordinary task workflows that should be rediscovered through active skill search.

Keeping them host-facing preserves the boundary:

- search finds active reusable skills
- host recommendations continue governed lifecycle steps
- lifecycle steps remain explicit and auditable
- promotion and apply operations do not happen silently

## Current Recommendation Fields

The current contract exposes these top-level fields:

- `recommended_next_action`
- `recommended_reason`
- `recommended_host_operation`
- `available_host_operations`

The host operation includes fields such as:

- `tool_name`
- `display_label`
- `effect_summary`
- `risk_level`
- `requires_confirmation`
- `confirmation_message`
- `arguments`
- `argument_schema`

The related orchestration context can include:

- `reuse_decision.decision`
- `reuse_decision.missing_inputs`
- `learning_decision.decision`
- `learning_decision.reason`
- `learning_capture_payload`
- `runtime_lane_status`
- `runtime_lane_reason`

## Current Presentation Gap

The current JSON and runbooks are enough for maintainers who already know the lifecycle contract.

They are not enough as the final host/operator presentation because:

- hosts still need to translate raw decision names into user-facing wording
- `observed_only` and `new_skill_candidate` are easy to confuse
- `review_evolution_candidate` must be shown as manual review, not as automatic apply
- `requires_confirmation=false` can still be misunderstood as "safe to auto-run" unless the text says this is a host/operator choice
- each host would otherwise reimplement similar wording and could drift from the governance boundary

The gap is presentation, not decision logic.

## Target Operator-Facing Display

The target display should be a compact card or plain-text block that answers:

1. What happened?
2. What is the recommended next action?
3. Why is this the next action?
4. Is it automatic?
5. Does it require human confirmation?
6. Which tool would the host call if the operator chooses to continue?

The display should be derived from the existing payload and must not mutate it.

## Example Displays

### `observed_only`

Scenario:

- a task succeeded
- there is enough value to keep a record
- the signal is not strong enough to distill or evolve automatically

Example card:

```text
Follow-up: Keep as observation
Why: The task completed, but the evidence is not strong enough to create or evolve a skill automatically.
Recommended action: No automatic lifecycle action.
Boundary: Human review is required before turning this observation into a reusable workflow.
```

If the payload includes a capture recommendation such as `capture_trajectory`, the card should show that host operation as an optional explicit action.

### `background_hint -> execute_skill`

Scenario:

- search found a plausible reusable skill
- required inputs or output alignment are incomplete
- the runtime did not auto-execute

Example card:

```text
Follow-up: Reuse candidate found
Why: A plausible skill match exists, but required inputs are missing or need operator review.
Recommended action: execute_skill
Tool: execute_skill
Missing inputs: output_path
Boundary: This is not automatic execution. The operator must provide the missing inputs or confirm the call.
```

### `new_skill_candidate -> distill_trajectory`

Scenario:

- a successful under-covered workflow produced concrete outputs
- the runtime captured a trajectory
- the next governed step is distillation into staging

Example card:

```text
Follow-up: Distill captured workflow
Why: This task produced a concrete workflow pattern that may be reusable.
Recommended action: distill_trajectory
Tool: distill_trajectory
Boundary: This creates a staging candidate. It does not promote an active skill automatically.
```

### `improve_existing_skill_candidate -> review_evolution_candidate`

Scenario:

- a successful task exposed a concrete gap in an existing skill
- the runtime created an evolution candidate
- the next governed step is manual review

Example card:

```text
Follow-up: Review existing-skill improvement
Why: The task exposed a concrete gap in an existing skill.
Recommended action: review_evolution_candidate
Tool: review_evolution_candidate
Boundary: This only reviews the proposed change. It does not apply the change automatically.
Confirmation: A human must review before any later apply operation.
```

## Confirmation Boundaries

Presentation must keep these boundaries visible:

- `execute_skill` from `background_hint` is a suggestion, not automatic execution.
- `distill_trajectory` creates a staging candidate path, not an active skill.
- `review_evolution_candidate` creates a review or diff proposal, not a global skill edit.
- `apply_evolution_candidate` requires explicit confirmation.
- `rollback_evolution_candidate` requires explicit confirmation.
- Lack of `requires_confirmation` on a low-risk host operation does not mean the host should execute it without operator intent.

## What Will Not Change

This work will not:

- add an active skill
- add a workflow query
- change ranking
- change metadata
- widen `default-in`
- automatically promote a skill
- automatically apply an evolution candidate
- redesign the dashboard
- wrap `distill_trajectory` or `review_evolution_candidate` as ordinary search skills
- change recommendation decisions
- execute recommended host operations

## Is Current CLI / JSON / Runbook Enough?

Current CLI, JSON, and runbooks are enough to validate the contract manually.

They are not enough as a reusable host/operator presentation layer. A host still has to infer the user-facing wording and governance warning from several payload fields. That creates avoidable inconsistency.

Smallest useful implementation:

- add a pure formatter/helper
- input: an existing result payload or `AgentOrchestrationResult`-shaped dictionary
- output: operator-facing structured card and plain text
- no mutation of the input payload
- no execution
- no recommendation decision changes

## Proposed Minimal Helper

Add:

- `skill_runtime/presentation/recommendation.py`

Suggested public functions:

- `format_recommendation_card(payload: dict) -> dict`
- `format_recommendation_text(payload: dict) -> str`

The structured card should include:

- `title`
- `status`
- `recommended_action`
- `tool_name`
- `reason`
- `boundary`
- `requires_confirmation`
- `confirmation_message`
- `missing_inputs`

## Test Plan

Add focused tests for:

- `observed_only` produces a "keep as observation" card and says the next step is not automatic
- `background_hint -> execute_skill` shows the suggested execution and missing inputs, with an explicit not-automatic boundary
- `new_skill_candidate -> distill_trajectory` shows distillation and says it does not promote automatically
- `improve_existing_skill_candidate -> review_evolution_candidate` shows review and says it does not apply automatically
- formatter output does not mutate the original payload

## Why This Does Not Justify Widening Default-In

Presentation clarity is not runtime-entry safety.

This work only makes existing recommendations easier for a host or operator to understand. It does not prove that broader tasks should enter the runtime lane, and it does not change the conservative boundary around maintainer judgment or governed lifecycle operations.

No evidence here supports widening `default-in`.
