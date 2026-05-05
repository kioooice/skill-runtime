# CLI Recommendation Presentation Acceptance

Date: 2026-05-06

## Command Used

```powershell
python -m skill_runtime.cli --root ./.tmp_cli_recommendation_demo capture-trajectory --file demo/maintainer_review_cleanup/observed_task.json --task-id cli_recommendation_demo --session-id cli_recommendation_demo --render-recommendation text
```

The checked-in artifacts were captured from that command without changing CLI logic.

## Captured Artifacts

- stdout artifact:
  [stdout.capture-trajectory.json](D:/02-Projects/vibe/docs/fixtures/cli-recommendation-presentation/stdout.capture-trajectory.json)
- stderr artifact:
  [stderr.capture-trajectory.txt](D:/02-Projects/vibe/docs/fixtures/cli-recommendation-presentation/stderr.capture-trajectory.txt)

The stdout artifact keeps the full CLI JSON envelope with outer `status` and inner `data`.

The stderr artifact keeps the operator-facing rendered recommendation text only.

## Default JSON Behavior Unchanged

Default CLI behavior remains unchanged:

- the normal command result is still emitted as JSON on `stdout`
- the JSON payload still contains `recommended_next_action`
- the JSON payload still contains `recommended_host_operation`
- the JSON payload still contains `available_host_operations`

The optional text surface does not replace or reshape the JSON audit payload.

## stderr Text Behavior

With `--render-recommendation text`, the operator sees:

- `Follow-up: Distill captured workflow`
- `Recommended action: distill_trajectory`
- `Tool: distill_trajectory`
- boundary wording that says this creates a staging candidate and is not automatic promotion

This is the intended minimal CLI/operator text surface.

## Acceptance Criteria Checklist

- [x] operator can see `recommended_next_action`
- [x] operator can see `recommended_host_operation.tool_name`
- [x] original JSON payload remains available for audit
- [x] stderr text is opt-in, not default
- [x] stderr text keeps the governed boundary visible
- [x] raw `requires_confirmation=false` is not presented as permission to auto-run
- [x] recommendation text does not replace the CLI JSON response

Not applicable in this concrete example:

- `missing_inputs` visibility, because this payload does not contain missing inputs
- `requires_confirmation=true` visibility, because this payload does not require explicit confirmation

## Execution Boundary Validation

The command recommended `distill_trajectory`, but it did not execute it.

Observed side effects under `./.tmp_cli_recommendation_demo`:

- one captured trajectory file exists:
  `./.tmp_cli_recommendation_demo/trajectories/cli_recommendation_demo.json`
- no staging skill directory was created
- no global skill directory was created

That is sufficient evidence that the CLI surface rendered the recommendation but did not execute the recommended host operation.

## No Promote / No Apply Confirmation

No automatic promotion happened:

- no staging skill files were created
- no active skill promotion happened
- no global Codex skill promotion happened

No evolution apply happened:

- this command path does not call `apply_evolution_candidate`
- no evolution candidate output was created

## Residual Ambiguity

One residual ambiguity remains at the raw payload layer:

- `recommended_host_operation.requires_confirmation=false` still exists in the JSON payload

Current assessment:

- this is acceptable for the current slice
- the stderr text does not frame that field as permission to auto-run
- the operator-facing wording remains clear enough for this command

## Path Note

The captured artifacts include local absolute paths such as:

- `D:\02-Projects\vibe\.tmp_cli_recommendation_demo\trajectories\cli_recommendation_demo.json`

Those paths are acceptable in this acceptance artifact because this is a real local CLI capture. They are not a cross-machine fixture requirement.

## Conclusion

The minimal CLI/operator text surface passes acceptance for `capture-trajectory`.

It provides:

- readable operator text on `stderr`
- unchanged JSON audit output on `stdout`
- no automatic execution of the recommended host operation
- no promote/apply side effects

No CLI logic change is required from this acceptance run.

## Why This Does Not Justify Widening `default-in`

This acceptance only proves that one opt-in CLI presentation surface is usable for one recommendation-bearing command.

It does not prove:

- broader runtime-entry safety
- broader governed automation safety
- broader workflow coverage
- any reason to widen `default-in`
