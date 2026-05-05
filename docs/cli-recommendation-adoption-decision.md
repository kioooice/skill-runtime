# CLI Recommendation Adoption Decision

Date: 2026-05-06

## Adoption Question

Should README and the relevant runbook formally recommend `capture-trajectory --render-recommendation text` as the operator path for governed follow-up?

This question is narrow:

- one command path only
- one opt-in flag only
- no runtime-decision change
- no default behavior change

## Evidence For Adoption

Current evidence is sufficient for narrow adoption:

- the CLI surface is implemented and limited to `capture-trajectory`
- acceptance artifacts exist for a real run
- `stdout` JSON audit output remains unchanged
- `stderr` text is operator-readable
- the accepted run did not execute `recommended_host_operation`
- the accepted run did not promote or apply anything

Relevant evidence sources:

- `docs/cli-recommendation-presentation-summary.md`
- `docs/cli-recommendation-presentation-acceptance.md`
- `docs/fixtures/cli-recommendation-presentation/`

## Risks And Reasons Not To Over-Adopt

This should not be over-adopted because:

- only `capture-trajectory` has been accepted
- there is no evidence that all recommendation-bearing commands need the same surface
- there is no evidence that the flag should become default-on
- there is no dashboard or host UI adoption evidence
- raw JSON still remains the audit source of truth

So the adoption should stay narrow and explicit.

## Decision

Decision: adopt narrowly.

Recommendation:

- README may recommend `--render-recommendation text` for the `capture-trajectory` governed follow-up operator path
- the relevant runbook may recommend the same path

Boundary:

- opt-in only
- `capture-trajectory` only
- text goes to `stderr`
- JSON audit payload remains on `stdout`
- this does not execute `recommended_host_operation`
- this does not promote or apply anything

## Exact README / Runbook Wording

Recommended wording:

> Optional operator view: add `--render-recommendation text` to `capture-trajectory` when you want a human-readable governed follow-up summary on `stderr`. This is opt-in and `capture-trajectory`-only. The JSON audit payload remains on `stdout`, and the command does not execute `recommended_host_operation`, promote a skill, or apply an evolution candidate.

## Non-Goals

This decision does not:

- recommend the flag for all CLI commands
- make the flag default
- change JSON payload shape
- change runtime recommendation decisions
- change service behavior
- add dashboard behavior
- widen `default-in`

## Why This Does Not Justify Widening `default-in`

This decision is only about operator-facing documentation for one accepted CLI path.

It does not prove:

- broader runtime-entry safety
- broader governed automation safety
- broader workflow coverage
- any reason to widen `default-in`
