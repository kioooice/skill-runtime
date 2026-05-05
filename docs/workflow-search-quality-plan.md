# Workflow Search Quality Plan

Date: 2026-05-06

## Goal

Create a workflow-focused search and reuse baseline that measures whether maintainer-oriented workflow intents can find the right workflow skill without changing ranking behavior, widening `default-in`, or mixing utility controls into the same gate.

## Why Utility Skills Remain Fixtures

Utility skills still belong in the repository because they are useful as:

- deterministic search smoke fixtures
- execution smoke fixtures
- narrow control cases for local retrieval behavior
- the existing utility-focused search baseline in `docs/search-quality-baseline.json`

They are no longer the main product proof.

Their role is now:

- keep local retrieval measurable
- keep low-risk execution smoke coverage
- act as false-neighbor and negative-query controls

They should not be treated as the main showcase for maintainer value.

## Why Workflow Skills Are The Real Product Value

The project thesis is maintainer workflow governance, not generic file manipulation.

The higher-value questions are now:

- can a maintainer find the right continuation or review workflow
- can the system distinguish workflow help from unrelated utility work
- can governed follow-up stay explicit without pretending that open-ended maintainer work is already automatic

That is closer to the public product story:

- handoff continuation
- pre-implementation direction review
- maintainer review cleanup
- governed learning follow-up such as `distill_trajectory` and `review_evolution_candidate`

## Workflow Fixture Strategy

The workflow search evaluator should import only workflow-oriented active fixtures into a temporary runtime root.

Initial workflow fixture set:

- `session_handoff_maintenance`
- `pre_implementation_workflow_review`
- `runtime_gate_workflow`
- `runtime_verification_selector`
- `repo_impact_analysis`
- `deployment_strategy_review`
- `auto_mode_stage_runner`
- `nontechnical_stage_report`

This keeps the baseline focused on workflow routing and avoids overfitting against utility skill neighbors.

## Proposed Workflow Query Set

### Positive should-match queries

- `continue from handoff and update tasks decisions`
  Expected skill: `session_handoff_maintenance`

- `review the plan before coding`
  Expected skill: `pre_implementation_workflow_review`

### Positive expected-gap queries

- `turn review comments into a cleanup plan`
  Expected current result: no active workflow search skill should be recommended yet
  Reason: review cleanup is a real maintainer workflow and demo path, but it is not currently represented as an active workflow search skill

- `decide whether to distill or review a skill candidate`
  Expected current result: no active workflow search skill should be recommended yet
  Reason: `distill_trajectory` and `review_evolution_candidate` currently exist as governed follow-up operations, not active search-owned workflow skills

### Negative query

- `merge text files into markdown`
  Expected current result: no workflow skill should be recommended
  Purpose: confirm that a utility task is not miscounted as workflow search success

## Expected Workflow Skills

Current expected workflow hits:

- handoff continuation -> `session_handoff_maintenance`
- pre-implementation review -> `pre_implementation_workflow_review`

Current honest gaps:

- maintainer review cleanup
- governed learning follow-up around distillation vs evolution review

Those gaps should be recorded as workflow coverage gaps, not hidden with ranking changes.

## Negative Workflow Queries

The first negative control should stay simple:

- a utility merge request should not recommend workflow adapters in the workflow-only fixture set

Later negative controls can broaden into unrelated product or external-system asks, but that is not necessary for the first slice.

## What This Proves

- workflow-oriented search can be evaluated separately from utility controls
- maintainer workflow routing can be regression-tested locally
- honest workflow coverage gaps can be recorded without changing the retrieval algorithm
- the product story can move back toward workflow value instead of utility demos

## What This Does Not Prove

- it does not prove semantic retrieval
- it does not prove general maintainer-intent understanding
- it does not prove that review cleanup is solved as a reusable active skill
- it does not prove that governed learning follow-up should become a search-owned active skill without more metadata or product design work
- it does not prove that retrieval is good enough across the full active library

## Why This Does Not Justify Widening Default-In

- search quality measures retrieval and reuse fit, not runtime-entry safety
- workflow demos such as review cleanup still depend on explicit maintainer judgment
- expected-gap workflow queries are evidence of incomplete workflow search coverage, not of lane safety
- no part of this baseline answers whether broader automatic runtime entry would improve outcomes

There is still no evidence here that supports widening `default-in`.

## First-Round Judgment

The first workflow baseline should allow expected failure.

If review cleanup or governed learning queries do not produce an active workflow match, the right next move is:

- tighten or add workflow metadata where a real active workflow skill should exist
- or keep the gap explicit if the capability still belongs to demos or host follow-up operations

The wrong next move would be:

- tuning ranking weights
- adding embedding or external retrieval
- forcing utility skills back into the main product story
