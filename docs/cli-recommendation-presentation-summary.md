# CLI Recommendation Presentation Summary

Date: 2026-05-06

## Purpose

Summarize the accepted `capture-trajectory --render-recommendation text` CLI/operator surface.

This summary does not change runtime logic, recommendation decisions, ranking, workflow queries, active skills, or `default-in`.

## Completed Implementation

The current implementation is narrow by design:

- `capture-trajectory` supports an opt-in `--render-recommendation text` flag
- the flag renders operator-facing recommendation text
- the output stays presentation-only

Scope boundary:

- only `capture-trajectory` supports this flag today
- this work does not extend the flag to other commands

## Default stdout JSON Behavior

Default CLI behavior remains unchanged:

- command output still goes to `stdout` as JSON
- the outer `status` / inner `data` envelope remains intact
- `recommended_next_action`, `recommended_host_operation`, and `available_host_operations` remain available for audit or machine consumption

The text surface does not replace the JSON audit payload.

## Opt-In stderr Text Behavior

When the operator explicitly passes:

```powershell
--render-recommendation text
```

the CLI prints human-readable recommendation text to `stderr`.

For the accepted `capture-trajectory` path, that text includes:

- `Follow-up: Distill captured workflow`
- `Recommended action: distill_trajectory`
- `Tool: distill_trajectory`
- the boundary that this creates a staging candidate and is not automatic promotion

## Acceptance Artifacts

The accepted real-run artifacts are:

- [stdout.capture-trajectory.json](D:/02-Projects/vibe/docs/fixtures/cli-recommendation-presentation/stdout.capture-trajectory.json)
- [stderr.capture-trajectory.txt](D:/02-Projects/vibe/docs/fixtures/cli-recommendation-presentation/stderr.capture-trajectory.txt)
- [cli-recommendation-presentation-acceptance.md](D:/02-Projects/vibe/docs/cli-recommendation-presentation-acceptance.md)

These artifacts come from a real local CLI run, not a hand-written example.

## No Execution / No Promote / No Apply Evidence

The acceptance run showed:

- one trajectory file was created
- no staging skill directory was created
- no global skill directory was created

That is enough evidence that:

- the recommended host operation was not executed
- no promote path ran
- no evolution apply path ran

## Current Residual Ambiguity

One residual ambiguity remains at the raw JSON layer:

- `recommended_host_operation.requires_confirmation=false` can still be over-read if someone inspects only the raw payload

Current assessment:

- the operator-facing `stderr` text keeps the boundary clear enough for this accepted slice
- this is not a reason to expand the feature surface yet

## What This Proves

This slice proves:

- `capture-trajectory` now has an acceptable CLI/operator text surface
- the text surface can coexist with unchanged JSON audit output
- operator-readable recommendation text can be shown without executing the recommendation
- the current surface is acceptable for the validated command path

## What This Does Not Prove

This slice does not prove:

- that all CLI commands should support the same flag
- that dashboard integration is done
- that host UI adoption is done
- that README or runbooks should already treat this flag as the default operator path
- that broader runtime-entry or lifecycle automation is safe
- that `default-in` should widen

## Recommended Next Core Slice

Recommended next slice:

- real host/operator adoption decision:
  should README/runbook recommend `--render-recommendation text` as the default operator path?

That next slice should stay narrow:

- decide whether this accepted CLI surface is the recommended operator path
- update README/runbook only if that adoption decision is justified
- avoid expanding the feature itself unless adoption work exposes a real gap

## Why This Does Not Justify Widening `default-in`

This work proves only that one opt-in CLI presentation surface is acceptable for one validated command path.

It does not prove:

- broader runtime-entry safety
- broader governed automation safety
- broader workflow coverage
- any reason to widen `default-in`
