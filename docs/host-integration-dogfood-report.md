# Host Integration Dogfood Report

Date: 2026-05-05

## Purpose

Record the first host/operator dogfood round for the current recommendation presentation layer.

This round uses checked-in recommendation payload fixtures and validates whether the current formatter and renderer make the next governed step understandable without changing runtime decision logic.

## Inputs

Dogfood payload fixtures:

- [background_hint_execute_skill_missing_inputs.json](D:/02-Projects/vibe/docs/fixtures/recommendation-payloads/background_hint_execute_skill_missing_inputs.json)
- [new_skill_candidate_distill_trajectory.json](D:/02-Projects/vibe/docs/fixtures/recommendation-payloads/new_skill_candidate_distill_trajectory.json)
- [improve_existing_skill_candidate_review_evolution.json](D:/02-Projects/vibe/docs/fixtures/recommendation-payloads/improve_existing_skill_candidate_review_evolution.json)

Dogfood command:

```powershell
python scripts/dogfood_recommendation_presentation.py
```

## Scenario 1

Input payload:

- [background_hint_execute_skill_missing_inputs.json](D:/02-Projects/vibe/docs/fixtures/recommendation-payloads/background_hint_execute_skill_missing_inputs.json)

Rendered output summary:

- title: `Reuse candidate found`
- action: `execute_skill`
- missing inputs: `output_path`
- boundary: not automatic execution

Operator interpretation:

- The operator can tell there is a plausible reusable skill.
- The operator can also tell the call should not run automatically because the missing output path is still explicit.

Ambiguity found:

- Minor residual ambiguity only at the raw payload level: `requires_confirmation=false` could be misread without the formatter text.
- The current helper already resolves this by rendering the non-automatic execution boundary.

Current helper sufficient:

- Yes

Next action:

- Keep the current helper behavior and validate the same wording in a real host integration surface.

## Scenario 2

Input payload:

- [new_skill_candidate_distill_trajectory.json](D:/02-Projects/vibe/docs/fixtures/recommendation-payloads/new_skill_candidate_distill_trajectory.json)

Rendered output summary:

- title: `Distill captured workflow`
- action: `distill_trajectory`
- boundary: staging candidate only, no automatic promotion

Operator interpretation:

- The operator can tell the successful workflow should move into staging first.
- The operator can also tell this is not active promotion and not automatic lifecycle continuation.

Ambiguity found:

- No blocking ambiguity found in the rendered text or card output.

Current helper sufficient:

- Yes

Next action:

- Keep the current helper behavior and validate whether a real host UI or CLI presents the same distinction clearly enough for operators.

## Scenario 3

Input payload:

- [improve_existing_skill_candidate_review_evolution.json](D:/02-Projects/vibe/docs/fixtures/recommendation-payloads/improve_existing_skill_candidate_review_evolution.json)

Rendered output summary:

- title: `Review existing-skill improvement`
- action: `review_evolution_candidate`
- confirmation: review before editing any global skill
- boundary: does not apply automatically

Operator interpretation:

- The operator can tell the next step is manual review of an evolution candidate.
- The operator can also tell this is not automatic apply and that later apply remains confirmation-backed.

Ambiguity found:

- No blocking ambiguity found in the rendered text or card output.

Current helper sufficient:

- Yes

Next action:

- Keep the helper unchanged and validate how a real host consumes the review recommendation in practice.

## Overall Result

The current helper is sufficient for this first dogfood round.

What it proved:

- the three current governed follow-up families can be rendered from service/orchestration-shaped payload fixtures
- the operator can understand the next step from current card/text output
- the no-automatic-execution, no-automatic-promotion, and no-automatic-apply boundaries remain visible

What it did not prove:

- real host integration ergonomics
- broader lifecycle automation
- any need to widen `default-in`

## Recommended Next Action

Recommended next action: validate the same payloads and boundaries in a real host integration or operator flow.

Do not expand the presentation helper yet. No evidence from this round shows that the current helper is insufficient.
