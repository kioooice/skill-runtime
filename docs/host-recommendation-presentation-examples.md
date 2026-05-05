# Host Recommendation Presentation Examples

Date: 2026-05-05

## Purpose

Show how `scripts/demo_recommendation_presentation.py` renders governed follow-up fixture payloads through:

- `format_recommendation_card`
- `format_recommendation_text`

The demo is presentation-only. It does not call a provider, execute a host operation, promote a skill, apply an evolution candidate, or change service recommendation decisions.

## How To Run

```powershell
python scripts/demo_recommendation_presentation.py
```

The script constructs four fixture payloads and prints JSON containing both a structured card and plain text for each example.

## Render A Real Payload File

Use `scripts/render_recommendation_presentation.py` when a host or operator already has a real recommendation payload file and only needs to render it for display.

Text output:

```powershell
python scripts/render_recommendation_presentation.py --input payload.json --format text
```

JSON output:

```powershell
python scripts/render_recommendation_presentation.py --input payload.json --format json
```

`--format text` is the default, so this is equivalent:

```powershell
python scripts/render_recommendation_presentation.py --input payload.json
```

The renderer only reads the input payload and calls `format_recommendation_card` / `format_recommendation_text`. It does not call `RuntimeService`, execute a host operation, promote a skill, apply an evolution candidate, or modify the input file.

## Example 1 - `observed_only`

Plain text output:

```text
Follow-up: Keep as observation
Status: The task can be recorded, but should not become a skill automatically.
Why: task succeeded, but the evidence was too weak for immediate distillation
Boundary: The evidence is not strong enough for automatic distillation or evolution. Human review is required before turning this observation into a reusable workflow.
```

Why this is not automatic:

- There is no `recommended_next_action`.
- There is no `recommended_host_operation`.
- The formatter says the evidence is not strong enough for automatic distillation or evolution.

Human confirmation:

- No tool confirmation is needed because no tool call is recommended.
- Human review is still required before turning the observation into a reusable workflow.

## Example 2 - `background_hint -> execute_skill`

Plain text output:

```text
Follow-up: Reuse candidate found
Status: A reusable skill may help, but the host should not run it automatically.
Why: a plausible reusable match exists, but the agent should keep solving normally
Recommended action: execute_skill
Tool: execute_skill
Missing inputs: output_path
Boundary: This is not automatic execution. The operator must provide missing inputs or confirm the call.
```

Why this is not automatic:

- The decision is `background_hint`, not `auto_execute`.
- The payload still has a missing required input: `output_path`.
- The formatter explicitly says the host should not run it automatically.

Human confirmation:

- The fixture operation has `requires_confirmation=false`, but the operator still needs to provide the missing input or choose to run the call.
- Hosts should not interpret `requires_confirmation=false` as permission to auto-run from a `background_hint`.

## Example 3 - `new_skill_candidate -> distill_trajectory`

Plain text output:

```text
Follow-up: Distill captured workflow
Status: A successful workflow may be reusable.
Why: task succeeded with a concrete under-covered workflow pattern
Recommended action: distill_trajectory
Tool: distill_trajectory
Boundary: This creates a staging candidate; it does not promote an active skill and is not automatic promotion.
```

Why this is not automatic:

- The recommendation is to distill a captured trajectory into staging.
- It does not promote an active skill.
- It does not execute the generated candidate.

Human confirmation:

- The fixture operation has `requires_confirmation=false` because distillation itself is low-risk.
- Promotion remains a later governed lifecycle step and must stay explicit.

## Example 4 - `improve_existing_skill_candidate -> review_evolution_candidate`

Plain text output:

```text
Follow-up: Review existing-skill improvement
Status: A concrete existing-skill gap should be reviewed manually.
Why: task exposed a concrete existing-skill gap
Recommended action: review_evolution_candidate
Tool: review_evolution_candidate
Boundary: This only reviews the proposed change; it does not apply it automatically. Human confirmation is required before any later apply operation.
Confirmation: Review before editing any global skill.
```

Why this is not automatic:

- The recommendation is review, not apply.
- The formatter says it does not apply the change automatically.
- Any later apply operation remains separate and confirmation-backed.

Human confirmation:

- The fixture marks this review recommendation as requiring confirmation.
- A later `apply_evolution_candidate` operation also requires explicit confirmation.

## How Hosts Should Use The Helper

Hosts should:

- pass the existing result payload to `format_recommendation_card` or `format_recommendation_text`
- render the returned title, reason, boundary, missing inputs, and confirmation fields
- prefer the top-level `recommended_host_operation` when offering a next action
- keep nested recommendations as provenance
- keep no-operation states visible instead of sending the user back to search

Hosts should not:

- execute the returned operation just because a card exists
- treat lifecycle operations as active searchable skills
- auto-promote after distillation
- auto-apply after evolution review
- hide `missing_inputs`
- hide `requires_confirmation`

## Action And Decision Priority

The formatter uses the current payload shape:

- top-level `recommended_next_action` and `recommended_host_operation` identify the action the host can render
- `learning_decision.decision` and `reuse_decision.decision` explain why that action appears

If both action and decision are present, the formatter treats them as complementary presentation context. This documents the current helper behavior only; it does not change service recommendation logic.

## Why This Is Not Default-In Evidence

These examples only prove that existing recommendation payloads can be presented more clearly.

They do not prove:

- broader task-entry safety
- automatic runtime entry for new task families
- arbitrary maintainer workflow automation
- automatic promotion
- automatic skill evolution apply

No evidence here supports widening `default-in`.
