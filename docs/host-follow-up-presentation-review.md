# Host Follow-Up Presentation Review

Date: 2026-05-05

## Verdict

`manual_validation_first`

## Proposed Direction

Build a narrower host UI / CLI presentation layer for the follow-up recommendation sequence:

- `background_hint`
- `distill_trajectory`
- `review_evolution_candidate`

Target user:

- the operator or host integration layer consuming runtime decisions

Intended outcome:

- make the next step easier to read than raw JSON while preserving the governed workflow boundaries

## Why This Matters

The recommendation contract is now coherent enough to support one next step across reuse and learning paths. If the current raw JSON presentation is still too awkward, a narrow presentation layer could reduce integration friction without widening automation.

## Evidence Used

- top-level recommendation contract has been unified
- targeted dogfood passed for the three recommendation families
- sequence acceptance now shows those three actions can form one explicit operator flow

## Assumptions

- operators may want a narrower presentation than raw JSON
- current runbooks plus top-level fields may already be sufficient

Those assumptions are not yet validated strongly enough to justify code immediately.

## Current Alternatives

- consume the top-level recommendation fields directly from JSON
- use the runbooks:
  - `docs/host-follow-up-recommendation-contract.md`
  - `docs/host-follow-up-recommendation-dogfood.md`
  - `docs/host-follow-up-sequence-runbook.md`
- keep dashboard as a read-only observation surface rather than a write/action surface

## Risk Flags

- building a presentation layer too early would duplicate what the host can already derive from the top-level contract
- a CLI/UI surface could become another product lane before the operator pain is clear
- it would be easy to drift back into dashboard-style packaging work instead of core workflow value

## Smallest Closed-Loop Validation

Use the current JSON contract and runbooks in 2-3 real maintainer flows, then answer one question:

Does the operator still need a narrower display layer after the top-level recommendation fields and runbooks are available?

If yes, capture exactly what is missing:

- too verbose
- too nested
- too hard to compare
- too hard to render consistently

## Stop Condition Before Implementation

Do not build a new host UI / CLI presentation layer until at least one real operator flow shows that:

1. the top-level contract is not enough on its own, and
2. the missing value is specifically presentation, not another workflow boundary problem
