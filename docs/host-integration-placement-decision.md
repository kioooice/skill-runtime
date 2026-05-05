# Host Integration Placement Decision

Date: 2026-05-06

## Purpose

Decide where the current recommendation renderer output should appear first in a real host/operator flow.

This is a decision document only. It does not change runtime behavior, service recommendation logic, ranking, workflow queries, active skills, `default-in`, dashboard behavior, or presentation helper behavior.

## Current Evidence Boundary

The current evidence chain is:

- fixture payload dogfood
- real payload rendering runbook
- one real CLI payload capture and rendering path

That evidence proves the renderer output is understandable.

It does not prove that any existing UI surface is already the right operator-facing placement.

## Candidate Surfaces

### CLI Text Output

What it is:

- operator reads rendered plain text produced from a saved payload or directly from a documented CLI follow-up path

Pros:

- already validated by the current real payload run
- lowest integration risk
- keeps governance boundary wording visible
- easy to compare against raw JSON during operator review
- no dashboard or host UI changes required

Cons:

- requires the operator to explicitly run or reference the renderer step
- not embedded into a richer product surface
- less discoverable than an in-product message or card

### CLI JSON Companion Field

What it is:

- keep raw JSON as the audit surface and pair it with a renderer command reference or rendered companion artifact

Pros:

- preserves the original payload for audit
- works well for logs, automation handoff, and debugging
- keeps the decision contract explicit and machine-readable

Cons:

- still requires an operator to know where to look
- raw JSON alone does not solve presentation ambiguity
- not as immediately readable as rendered text

### Dashboard Card

What it is:

- render recommendation output inside the existing dashboard or trigger-log related surfaces

Pros:

- potentially more discoverable for operators who already use the dashboard
- can align with existing governance and trigger-log browsing

Cons:

- current evidence does not validate dashboard placement or ergonomics
- risks mixing a narrow recommendation decision with a larger surface decision
- would start UI placement work before operator acceptance criteria are settled
- easy to over-scope into dashboard redesign

### Codex/Host Message

What it is:

- emit rendered recommendation text inside the host-facing conversational or operator message stream

Pros:

- high visibility at the moment the recommendation matters
- keeps next-step guidance close to the triggering task
- likely the most direct operator-facing surface if done carefully

Cons:

- current validation has not yet decided the right host message contract
- risks coupling presentation decisions to a specific host integration too early
- requires stronger operator acceptance criteria before integration

### Runbook-Only

What it is:

- keep renderer usage documented, but do not choose a first integration surface yet

Pros:

- zero implementation risk
- preserves the current validation state cleanly

Cons:

- does not answer the actual placement question
- leaves operator flow undecided
- delays the next product decision without creating new evidence

## Recommended First Integration Surface

Recommended first integration surface:

- CLI/operator text output, with the original JSON payload retained for audit
- optionally paired with a documented renderer command reference

## Why That Surface Is First

This surface should come first because:

- the current evidence already proves rendering works in a CLI payload flow
- the real validated path is a CLI service response, not a dashboard interaction
- it preserves the narrow governance boundary without forcing a UI placement decision too early
- it keeps auditability strong because the raw JSON payload remains available
- it avoids turning a recommendation-placement decision into a dashboard project

In practical terms, this means the first real integration should prefer:

- rendered operator-facing text as the immediate recommendation view
- raw JSON payload as the audit companion

Not:

- dashboard-first integration
- broader host UI redesign

## Why Not Dashboard First

Dashboard should not be first because the current evidence does not prove dashboard ergonomics.

What has been validated:

- payload shape
- renderer wording
- operator comprehension from fixture and real CLI paths

What has not been validated:

- which dashboard view should own the recommendation
- whether operators expect this recommendation in a dashboard at all
- whether recommendation placement there would improve or dilute the current workflow

Starting with dashboard would solve the wrong question first.

## Acceptance Criteria

The first real integration surface should meet all of these:

- operator can see `recommended_next_action`
- operator can see `recommended_host_operation.tool_name`
- `missing_inputs` is visible when present
- `requires_confirmation` is visible when `true`
- `no automatic execution`, `no automatic promotion`, or `no automatic apply` boundary is visible when relevant
- raw `requires_confirmation=false` is not presented as permission to auto-run
- the original JSON payload remains available for audit or debugging

Additional acceptance criteria for this slice:

- the operator does not need to infer the next step from nested payload internals
- the recommendation surface remains clearly separate from actually executing the host operation
- the chosen first surface can be used without changing runtime decision logic

## Non-Goals

This decision does not aim to:

- change runtime recommendation logic
- change `recommended_next_action`
- change `recommended_host_operation`
- redesign the dashboard
- add a new presentation helper
- add a new capture helper script
- add active workflow skill metadata
- expand `default-in`
- automate promotion
- automate evolution apply

## Recommended Next Step After This Decision

Recommended next step:

- define operator flow acceptance criteria for the chosen first surface in a narrow real host integration plan

That follow-up should stay focused on:

- where the rendered text appears
- when the operator sees it
- how the raw payload remains available

It should not default into:

- more fixture generation
- dashboard expansion
- runtime behavior changes

## Why This Does Not Justify Widening `default-in`

This decision is about placement of already-generated recommendation output.

It does not prove:

- broader runtime-entry safety
- broader autonomous lifecycle safety
- broader workflow coverage
- that more task families should enter `default-in`

No evidence here supports widening `default-in`.
