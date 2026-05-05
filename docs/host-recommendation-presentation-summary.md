# Host Recommendation Presentation Summary

Date: 2026-05-05

## Purpose

Summarize the current host-facing recommendation presentation layer and its boundary.

This summary covers the completed formatter, fixture demo, and payload renderer CLI. It does not change runtime behavior, recommendation decisions, ranking, workflow queries, active skills, baselines, or `default-in`.

## Completed Capabilities

The current presentation layer provides three completed pieces:

- formatter helpers in `skill_runtime/presentation/recommendation.py`
- a fixture-driven demo in `scripts/demo_recommendation_presentation.py`
- a real payload renderer CLI in `scripts/render_recommendation_presentation.py`

Together, they let a host or operator render governed follow-up recommendations without re-implementing wording or governance warnings from raw payload fields.

## How To Use The Formatter

The formatter layer exposes:

- `format_recommendation_card(payload)`
- `format_recommendation_text(payload)`

Expected input:

- an existing recommendation payload shaped like the current service / orchestration result

Outputs:

- a structured card dictionary for host rendering
- a plain text rendering for CLI or logs

The formatter is presentation-only:

- it does not mutate the input payload
- it does not call `RuntimeService`
- it does not execute a host operation
- it does not promote a skill
- it does not apply an evolution candidate
- it does not alter the underlying recommendation decision

## How To Use `demo_recommendation_presentation.py`

Run:

```powershell
python scripts/demo_recommendation_presentation.py
```

What it does:

- constructs fixture payloads locally
- runs them through `format_recommendation_card`
- runs them through `format_recommendation_text`
- prints JSON examples for inspection

What it does not do:

- it does not read real service output
- it does not call a provider
- it does not execute a host operation
- it does not promote
- it does not apply

## How To Use `render_recommendation_presentation.py`

Run text rendering:

```powershell
python scripts/render_recommendation_presentation.py --input payload.json --format text
```

Run JSON rendering:

```powershell
python scripts/render_recommendation_presentation.py --input payload.json --format json
```

Default:

- `--format text`

What it does:

- reads an existing payload JSON file
- validates that the file exists
- validates that the JSON is valid
- validates that the payload is a JSON object
- renders the payload through the formatter

What it does not do:

- it does not call `RuntimeService`
- it does not execute the recommended operation
- it does not promote
- it does not apply
- it does not modify the input file

## Covered Recommendation Scenarios

The current presentation layer explicitly covers:

- `observed_only`
- `background_hint -> execute_skill`
- `new_skill_candidate -> distill_trajectory`
- `improve_existing_skill_candidate -> review_evolution_candidate`

These scenarios correspond to the current governed follow-up boundary:

- keep an observation without automatic lifecycle progress
- show a reusable match as a non-automatic suggestion
- show distillation as a staging step, not as active promotion
- show evolution review as manual review, not as automatic apply

## Confirmation And Governance Boundaries

The current presentation layer keeps these boundaries visible:

- `background_hint` is not automatic execution
- `distill_trajectory` creates a staging candidate only
- `review_evolution_candidate` is review only
- any later `apply_evolution_candidate` remains explicit and confirmation-backed
- lack of `requires_confirmation` on a low-risk operation is not permission for silent execution

This is the main value of the presentation layer: it keeps lifecycle intent readable without flattening governance into ordinary skill execution.

## What This Does Not Do

This work does not:

- add an active skill
- add a workflow query
- change ranking
- change runtime recommendation logic
- change `recommended_next_action`
- change `recommended_host_operation`
- widen `default-in`
- add automatic promotion
- add automatic evolution apply
- redesign the dashboard
- integrate directly with a real host UI

It remains a presentation layer only.

## Why This Does Not Justify Widening `default-in`

The presentation layer proves that existing governed follow-up payloads can be rendered clearly.

It does not prove:

- broader runtime-entry safety
- stronger retrieval coverage
- broader maintainer workflow automation
- automatic lifecycle continuation
- automatic promotion or automatic apply

No evidence here supports widening `default-in`.

## Recommended Next Core Slice

Recommended next slice: real host integration dogfood / operator validation.

Reason:

- the presentation layer now exists
- the missing evidence is no longer formatter or renderer availability
- the next useful question is whether a real host or operator can use the current payload, formatter, demo, and renderer clearly enough in practice

That next slice should stay narrow:

- validate real host/operator consumption of current recommendation payloads
- check whether the wording and boundaries are sufficient in actual operator flow
- keep lifecycle operations explicit

Non-goals:

- no new presentation feature surface
- no dashboard expansion
- no runtime decision changes
- no active-skill wrapping of lifecycle operations
- no `default-in` expansion
