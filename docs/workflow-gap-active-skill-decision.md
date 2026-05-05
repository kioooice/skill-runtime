# Workflow Gap Active Skill Decision

Date: 2026-05-05

## Purpose

Decide whether the two current workflow-search expected gaps should become active workflow-search metadata now, or remain explicit gaps.

Scope:

- `maintainer_review_cleanup`
- `governed_learning_follow_up`

This decision does not change runtime behavior, ranking, query coverage, active metadata, active skills, or baselines.

## Current Baseline Position

`docs/workflow-search-quality-baseline.json` currently treats both queries as `expected_gap`:

- `maintainer_review_cleanup`
- `governed_learning_follow_up`

That means the workflow search evaluator expects no recommended active workflow skill for either query. The baseline is honest if those capabilities exist somewhere else but are not owned by active workflow search.

## A. `maintainer_review_cleanup`

Query:

`turn review comments into a cleanup plan`

### Where The Capability Exists Today

The capability exists in three places:

- Maintainer demo documentation:
  - `docs/maintainer-review-cleanup-demo.md`
  - `docs/maintainer-review-cleanup-mainline-acceptance.md`
  - `docs/maintainer-review-cleanup-mainline-runbook.md`
- Demo fixtures:
  - `demo/maintainer_review_cleanup/review_comments.json`
  - `demo/maintainer_review_cleanup/expected_cleanup_plan.md`
  - `demo/maintainer_review_cleanup/observed_task.json`
- Provider quality positive control:
  - `review_cleanup_demo_provider_success`
  - `examples/providers/review_cleanup_fallback_provider.py`

It does not currently exist as an active workflow skill. The active workflow fixture set used by `scripts/evaluate_workflow_search_quality.py` does not include a review-cleanup skill, and `skill_store/active` does not contain review-cleanup metadata.

### Current Classification

Current status: demo plus provider positive control.

It is not only a toy demo, because the positive provider control can generate executable workflow code that reads structured review comments and writes a grouped cleanup plan. It is still not an active workflow skill, because that executable behavior is provider-loop evidence, not an approved active search surface.

### If It Became An Active Workflow Skill

An active workflow skill should be narrow and maintainer-facing:

- read structured pull request review comments from an explicit input path
- group comments into required fixes and follow-up items
- write a cleanup plan artifact to an explicit output path
- optionally write structured metadata to an explicit metadata path
- return produced artifacts and counts
- keep missing required inputs explicit

It should be search-owned only for the planning artifact workflow, not for open-ended review reasoning.

### What It Should Not Do

It should not:

- rewrite source files
- apply code fixes
- resolve review comments
- infer merge approval
- decide that a pull request is ready to merge
- promote, apply, or evolve skills
- widen `default-in`
- treat provider positive-control success as general review automation

### Required Metadata And Boundary

Before entering active workflow search, it would need explicit metadata such as:

- skill name: `maintainer_review_cleanup` or `maintainer_review_cleanup_workflow`
- summary: convert structured review comments into a maintainer cleanup plan
- input schema:
  - `input_path: str`
  - `output_path: str`
  - optional `metadata_path: str`
- output schema:
  - `status: str`
  - `artifacts: list[str]`
  - `required_fix_count: int`
  - `follow_up_count: int`
- tags:
  - `maintainer`
  - `review`
  - `cleanup`
  - `pull-request`
  - `planning`
  - `workflow`
- rule reason:
  - manually approved as a bounded maintainer planning workflow, not as automatic review resolution
- scope policy:
  - may read explicit structured review input
  - may write only explicit artifact paths
  - must not mutate repository source files or external review state

Because active workflow skills in this project usually act as thin adapters to authoritative global Codex skills, the cleaner promotion path would be:

1. create or approve a global workflow skill for this exact bounded cleanup-plan behavior
2. add a thin active adapter and metadata only after the boundary is accepted
3. then update workflow search baseline expectations in a separate change

### Active Workflow Search Fit

Decision: needs more evidence before active workflow search.

Reason:

- There is real maintainer value.
- There is a passing constrained provider positive control.
- There is mainline documentation.
- But there is not yet an approved global workflow skill or active adapter boundary.
- The current docs still emphasize that review cleanup remains conservative and should not be mistaken for silent review automation.

The workflow baseline should keep `maintainer_review_cleanup` as an expected gap for now.

## B. `governed_learning_follow_up`

Query:

`decide whether to distill or review a skill candidate`

### Where The Capability Exists Today

The capability exists as host-facing lifecycle and recommendation operations:

- README lifecycle:
  - `search -> execute -> distill -> audit -> promote -> reuse`
  - `search -> execute -> observed task record -> capture/distill`
- Explicit lifecycle recommendations:
  - `log_trajectory -> distill_trajectory`
  - `capture_trajectory -> distill_trajectory`
  - `distill_trajectory -> audit_skill`
  - `audit_skill -> promote_skill`
  - `promote_skill -> execute_skill`
- Host follow-up contract:
  - `docs/host-follow-up-recommendation-contract.md`
  - `docs/host-follow-up-recommendation-dogfood.md`
  - `docs/host-follow-up-sequence-runbook.md`

The current dogfood evidence shows top-level recommendations for:

- `background_hint -> execute_skill`
- `new_skill_candidate -> distill_trajectory`
- `improve_existing_skill_candidate -> review_evolution_candidate`

### Current Classification

Current status: host follow-up operation.

This is not a normal active skill. It is a governed host operation sequence exposed through CLI/MCP/service contracts.

### Should `distill_trajectory` Or `review_evolution_candidate` Be Searchable Active Skills?

No.

`distill_trajectory` and `review_evolution_candidate` should remain lifecycle operations, not active workflow-search skills.

Reasons:

- They operate on runtime governance artifacts, not ordinary maintainer task inputs.
- They are already exposed as direct host operations with explicit arguments.
- Their sequencing depends on the prior result state:
  - captured trajectory
  - staged candidate
  - evolution candidate
  - audit result
- Wrapping them as search-owned active skills would blur the boundary between "find a reusable workflow" and "continue the governed lifecycle."
- It could make governed follow-up look like ordinary skill reuse, which is exactly the boundary the current docs preserve.

### Should The Workflow Baseline Keep This As An Expected Gap?

Yes.

The query intentionally asks for a decision between lifecycle follow-up operations. Search should not invent an active skill owner for that. The correct product surface is host-facing docs and top-level `recommended_host_operation`, not active workflow metadata.

### Is Better Host-Facing Documentation Needed?

Possibly, but the fix is documentation and presentation clarity, not active skill metadata.

Useful host-facing documentation improvements would be:

- a short decision table for `observed_only`, `new_skill_candidate`, and `improve_existing_skill_candidate`
- clearer wording that `distill_trajectory` and `review_evolution_candidate` are lifecycle operations
- examples showing when hosts should render the top-level recommendation instead of asking search again

Those improvements should stay in host integration docs or runbooks.

### Active Workflow Search Fit

Decision: keep as host follow-up.

The workflow baseline should keep `governed_learning_follow_up` as an expected gap.

## Final Recommendations

### Review Cleanup

Recommendation: needs more evidence.

Do not promote to active workflow skill metadata in this round.

Keep the workflow baseline gap until there is an approved bounded global workflow skill or active adapter with explicit read/write boundaries. The strongest future case is a narrow cleanup-plan skill, not automatic code cleanup.

### Governed Learning Follow-Up

Recommendation: keep as host follow-up.

Do not promote `distill_trajectory`, `review_evolution_candidate`, or their routing logic into active workflow search. Keep them as governed lifecycle operations surfaced through `recommended_host_operation`.

## Baseline Implication

Both expected gaps should remain:

- `maintainer_review_cleanup`
- `governed_learning_follow_up`

Expected workflow baseline summary should remain:

- `query_count = 5`
- `expectation_met_count = 5`
- `expected_gap_confirmed_count = 2`

No evidence in this review supports widening `default-in`.
