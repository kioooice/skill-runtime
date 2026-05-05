# Real Host Payload Rendering Report

Date: 2026-05-05

## Purpose

Record one real operator-validation run of the host recommendation presentation flow using an actual CLI service response instead of a checked-in fixture payload.

## Command Used

```powershell
python -m skill_runtime.cli --root ./.tmp_real_payload_demo capture-trajectory --file demo/maintainer_review_cleanup/observed_task.json --task-id real_payload_demo --session-id real_payload_demo
```

## Artifacts

Raw response:

- [raw-response.capture-trajectory.json](D:/02-Projects/vibe/docs/fixtures/real-host-payload-rendering/raw-response.capture-trajectory.json)

Extracted payload:

- [payload.capture-trajectory.json](D:/02-Projects/vibe/docs/fixtures/real-host-payload-rendering/payload.capture-trajectory.json)

Rendered text:

- [rendered.capture-trajectory.txt](D:/02-Projects/vibe/docs/fixtures/real-host-payload-rendering/rendered.capture-trajectory.txt)

Rendered JSON:

- [rendered.capture-trajectory.json](D:/02-Projects/vibe/docs/fixtures/real-host-payload-rendering/rendered.capture-trajectory.json)

## Response Shape Check

The real command was a valid first target.

It returned the expected recommendation fields:

- `recommended_next_action`
- `recommended_reason`
- `recommended_host_operation`
- `available_host_operations`

The saved raw response correctly preserves the outer CLI envelope:

- top-level `status`
- inner `data`

The saved payload file correctly contains only the inner `.data` object expected by the renderer.

## Operator-Facing Result

- `recommended_next_action`: `distill_trajectory`
- `recommended_host_operation.tool_name`: `distill_trajectory`
- primary rendered title: `Distill captured workflow`

Rendered interpretation:

- the operator can tell that the observed workflow was captured successfully
- the operator can tell that the next step is distillation into staging
- the operator can tell that this is not active promotion and not automatic lifecycle continuation

## Visibility Check

`missing_inputs`:

- not present in this payload
- rendered output remains understandable without it

`requires_confirmation`:

- visible in the payload as `false`
- rendered output does not convert that into automatic execution

Governance boundary wording:

- visible in both rendered text and rendered JSON card
- current wording is: distillation creates a staging candidate and does not promote an active skill automatically

## Operator Interpretation

For this real payload, the operator can understand the next step without reading raw nested internals:

- keep the captured trajectory as the current artifact
- call `distill_trajectory` if they want to move into staging
- do not treat this as automatic promotion

## Ambiguity Found

One residual ambiguity remains at the raw payload level:

- `requires_confirmation=false` could still be over-read if someone looks only at the raw host operation and ignores the rendered boundary text

That ambiguity is already handled by the existing renderer output. No new helper behavior is required from this run.

## Does The Helper Need Change?

No.

This run validates that the current helper is sufficient for at least one real CLI payload path:

- real command output was captured successfully
- payload extraction worked as documented
- text rendering was readable
- JSON rendering preserved the same governance boundary

## Why This Does Not Justify Widening `default-in`

This validation proves only that one real CLI recommendation payload can be captured, extracted, and rendered clearly.

It does not prove:

- broader runtime-entry safety
- broader workflow retrieval quality
- broader lifecycle automation safety
- that distillation should become automatic
- that more task families should enter `default-in`

No evidence here supports widening `default-in`.
