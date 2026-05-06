# Workflow Gap Active Skill Decision

Date: 2026-05-06

## Purpose

Decide whether the two workflow-search gaps should stay as explicit gaps or move into active workflow ownership.

Scope:

- `maintainer_review_cleanup`
- `governed_learning_follow_up`

## Current Decision

### `maintainer_review_cleanup`

Decision: approve active workflow ownership now.

Reason:

- the repository now has a bounded positive control that really generates, audits, promotes, and reuses a maintainer review-cleanup workflow skill
- the useful boundary is narrow and stable
- the global-skill source-of-truth policy already defines the right promotion path for this kind of reusable workflow

Approved boundary:

- read structured review comments from an explicit input path
- group them into required fixes and follow-up work
- write a cleanup-plan artifact to an explicit output path
- optionally write structured metadata to an explicit metadata path
- return artifact paths and counts

Not approved:

- source-file mutation
- automatic code fixes
- review resolution
- merge judgment
- widening `default-in`
- treating one provider-backed positive control as proof that open-ended review automation is solved

Ownership shape:

1. authoritative global Codex skill: `maintainer-review-cleanup`
2. thin runtime adapter: `maintainer_review_cleanup`
3. workflow-search baseline updated to expect this bounded workflow match

### `governed_learning_follow_up`

Decision: keep as host follow-up.

Reason:

- `distill_trajectory` and `review_evolution_candidate` are lifecycle operations, not normal reusable maintainer workflows
- they depend on runtime governance state, not ordinary task inputs
- surfacing them through `recommended_host_operation` remains the right product boundary

## Baseline Implication

Workflow search should now treat:

- `maintainer_review_cleanup` as `should_match`
- `governed_learning_follow_up` as `expected_gap`

Expected summary after this decision:

- `query_count = 5`
- `expectation_met_count = 5`
- `expected_gap_confirmed_count = 1`

## Notes

This decision changes workflow ownership and search expectations only.

It does not:

- widen the runtime default lane
- make review cleanup silent
- replace the provider-backed smoke path
- claim that open-ended review automation is solved
