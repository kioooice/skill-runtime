# Host Integration Dogfood Plan

Date: 2026-05-05

## Goal

Validate whether a real host or operator can consume the current recommendation contract, formatter, fixture demo, and payload renderer CLI without needing new presentation features or runtime decision changes.

## Why This Is Next

The presentation layer now exists:

- `skill_runtime/presentation/recommendation.py`
- `scripts/demo_recommendation_presentation.py`
- `scripts/render_recommendation_presentation.py`

The next open question is no longer "can we render a recommendation payload?" It is "can an operator understand the next step and the governance boundary from the current rendering output?"

## Dogfood Scenarios

The first dogfood round covers three scenarios:

- `background_hint -> execute_skill` with missing inputs
- `new_skill_candidate -> distill_trajectory`
- `improve_existing_skill_candidate -> review_evolution_candidate`

These are the current governed follow-up families that matter most for host/operator comprehension.

## Required Payload Sources

The first round uses checked-in fixture payloads under:

- `docs/fixtures/recommendation-payloads/`

Each fixture must be shaped like a service/orchestration result and must include the recommendation fields that a host would actually consume.

## Operator Validation Checklist

For each scenario, validate whether the operator can answer:

- What happened?
- What is the recommended next action?
- Which tool would the host call?
- Is the action automatic?
- Does the action require human confirmation?
- Is the governance boundary still explicit?

Also validate that:

- the fixture payload can be rendered without calling runtime
- the rendering output is stable enough for CLI or host display
- the fixture file itself is not modified

## Success Criteria

This round succeeds if:

- all selected fixture payloads render successfully
- the dogfood output makes the next action understandable for each scenario
- the output keeps "not automatic execution", "not automatic promotion", and "not automatic apply" boundaries visible
- no new helper capability is required to interpret the three scenarios

## Failure Criteria

This round fails if:

- a fixture payload cannot be rendered cleanly
- the operator cannot tell the next step from the current output
- the output blurs lifecycle review into automatic execution
- the output hides missing inputs or confirmation boundaries
- a genuine ambiguity requires changing helper behavior instead of just documenting it

## What Will Not Change

This dogfood round will not:

- add an active skill
- add a workflow query
- change ranking
- widen `default-in`
- change runtime recommendation decisions
- auto-promote a skill
- auto-apply an evolution candidate
- redesign the dashboard
- expand presentation helper behavior unless the dogfood evidence proves a real gap

## Why This Does Not Justify Widening `default-in`

This dogfood validates operator comprehension of existing recommendation payloads.

It does not prove:

- broader runtime-entry safety
- broader search coverage
- more task families should enter the runtime lane
- lifecycle steps should become automatic

No evidence from this dogfood round can justify widening `default-in`.
