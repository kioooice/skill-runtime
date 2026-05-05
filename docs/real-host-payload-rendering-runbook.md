# Real Host Payload Rendering Runbook

Date: 2026-05-05

## Goal

Validate that a real host or operator can capture a recommendation payload from the current service or orchestration flow, save the actual payload object as `payload.json`, and render it through the existing presentation layer.

This runbook stays narrow:

- no UI work
- no `RuntimeService` changes
- no recommendation-decision changes
- no automatic host operation execution
- no automatic promotion
- no automatic evolution apply

## Real Payload Sources

Use an existing runtime command that already returns recommendation fields.

Stable first target from the current README quick path:

```powershell
python -m skill_runtime.cli --root ./.tmp_real_payload_demo capture-trajectory --file demo/maintainer_review_cleanup/observed_task.json --task-id real_payload_demo --session-id real_payload_demo
```

That command already returns a real service payload with:

- `recommended_next_action`
- `recommended_reason`
- `recommended_host_operation`
- `available_host_operations`

Other real sources are also acceptable if they already return the same top-level recommendation contract, for example:

- `python -m skill_runtime.cli --root <root> search ...`
- `python -m skill_runtime.cli --root <root> execute ...`
- `python -m skill_runtime.cli --root <root> codex-run ...`
- `python -m skill_runtime.cli --root <root> codex-finalize ...`

Use whichever command matches the validation scenario. The important part is that the payload must come from the current service/orchestration flow, not from a fixture or demo constructor.

## Capture The Raw Response

Save the full CLI JSON response first:

```powershell
python -m skill_runtime.cli --root ./.tmp_real_payload_demo capture-trajectory --file demo/maintainer_review_cleanup/observed_task.json --task-id real_payload_demo --session-id real_payload_demo > raw-response.json
```

Current CLI commands print an envelope shaped like:

```json
{
  "status": "ok",
  "data": {
    "...": "real payload fields live here"
  }
}
```

The renderer expects the inner payload object, not the outer CLI envelope.

## Save `payload.json`

Extract the `.data` object into `payload.json`:

```powershell
$raw = Get-Content raw-response.json -Raw | ConvertFrom-Json
$raw.data | ConvertTo-Json -Depth 50 | Set-Content payload.json
```

Check that `payload.json` now contains the actual recommendation fields at the top level:

- `recommended_next_action`
- `recommended_host_operation`
- `available_host_operations`

If your host or orchestration layer already logs the inner payload object directly, you can skip the extraction step and save that object as `payload.json` as-is.

## Render The Payload

Render plain text:

```powershell
python scripts/render_recommendation_presentation.py --input payload.json --format text
```

Render structured output:

```powershell
python scripts/render_recommendation_presentation.py --input payload.json --format json
```

This is rendering only. It does not:

- call `RuntimeService`
- execute the recommended host operation
- promote a skill
- apply an evolution candidate
- modify `payload.json`

## Operator Checklist

For each real payload, confirm:

- the payload came from a real service/orchestration command, not a fixture
- `payload.json` contains the inner payload object, not the outer `status/data` wrapper
- `recommended_next_action` is visible and matches the intended next step
- `recommended_host_operation.tool_name` is visible and specific
- `missing_inputs` is visible when the action cannot safely run yet
- `requires_confirmation` is visible when manual confirmation is required
- the rendered output still says that execution, promotion, or apply is not automatic when that boundary matters

## What To Look For

Inspect these fields and their rendered interpretation:

- `recommended_next_action`
- `recommended_host_operation.tool_name`
- `missing_inputs`
- `requires_confirmation`
- wording that keeps `no automatic execution`, `no automatic promotion`, or `no automatic apply` explicit

## Known Ambiguity

Raw `requires_confirmation=false` must not be read as permission to auto-run a lifecycle operation.

The renderer exists to keep that boundary readable:

- `execute_skill` from a `background_hint` is still not automatic execution when inputs are missing
- `distill_trajectory` is still not automatic promotion
- `review_evolution_candidate` is still not automatic apply

## Success Criteria

This validation succeeds if:

- a real service/orchestration response is captured successfully
- the inner payload can be saved cleanly as `payload.json`
- the renderer output makes the next step understandable
- the operator can tell whether inputs or confirmation are still required
- governance boundaries stay explicit in the rendered text or card output

## Failure Criteria

This validation fails if:

- the only available artifact is a fixture rather than a real response
- the saved file is only the outer CLI envelope and cannot be rendered meaningfully
- the operator cannot tell what the next tool is
- missing inputs or confirmation boundaries are hidden
- the rendered output makes a governed step look automatic

## What Will Not Change

This runbook does not:

- add an active skill
- add a workflow query
- change ranking
- widen `default-in`
- change service recommendation decisions
- expand the presentation helper
- execute host operations automatically
- promote automatically
- apply evolution candidates automatically

## Why This Does Not Justify Widening `default-in`

This runbook only validates that a real recommendation payload can be captured and rendered clearly.

It does not prove:

- broader runtime-entry safety
- broader workflow search coverage
- broader lifecycle automation safety
- that lifecycle steps should become ordinary search skills
- that more task families should enter `default-in`

No evidence here supports widening `default-in`.
