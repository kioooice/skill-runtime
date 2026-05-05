# Evolution Lifecycle Acceptance

Date: 2026-05-05

## Goal

Define the operator-facing acceptance path for the governed skill evolution lifecycle.

This mainline is:

`candidate -> review -> apply -> rollback`

The question is not whether the individual tools exist. The question is:

`Can a maintainer inspect, apply, and if needed revert a global skill change through an explicit, auditable path?`

If the answer is yes, the evolution lifecycle is real.

If the answer is no, more dashboard polish does not help.

## Scope

This acceptance path covers:

1. when an existing-skill gap should become an evolution candidate
2. what `review_evolution_candidate` must produce
3. what `apply_evolution_candidate` must guard
4. what `rollback_evolution_candidate` must restore
5. what host-facing next actions must remain explicit at each step

This acceptance path does not cover:

- automatic skill mutation
- dashboard interaction changes
- widening Codex default-in boundaries
- distilling brand-new workflow skills

## Why This Is A Core Mainline

Skill Runtime now has a real path for improving existing global workflow skills.

That makes the real product question:

`Can a maintainer trust the system to improve a global skill without losing control of the audit trail or rollback path?`

This is the governance backbone for existing-skill improvement.

## Chosen Lifecycle

### Candidate

Input shape:

- a real task exposes a gap in an existing workflow skill
- the learning decision prefers `improve_existing_skill_candidate`
- the candidate records target skill name, task context, reason, evidence, and proposed changes

Expected output shape:

- a candidate JSON record under `.skill_runtime/evolution_candidates`

### Review

Input shape:

- candidate record
- target global skill path

Expected output shape:

- `rejected`, `needs_more_evidence`, or `ready_for_manual_diff`
- review record under `.skill_runtime/evolution_reviews`
- diff output when evidence is sufficient
- no mutation to global skill content

### Apply

Input shape:

- reviewed candidate with `ready_for_manual_diff`
- explicit confirmation

Expected output shape:

- target hash check before mutation
- backup file
- application record under `.skill_runtime/evolution_applications`
- candidate status becomes `applied`

### Rollback

Input shape:

- applied candidate
- explicit confirmation

Expected output shape:

- restore from recorded backup only
- refuse overwrite if target changed after apply
- rollback record under `.skill_runtime/evolution_rollbacks`
- candidate status becomes `rolled_back`

## Mainline Phases

### Phase 1 - Candidate capture

Use the evolution lifecycle only when a task exposed a gap in an existing workflow skill.

Do not use it for:

- brand-new workflow capture
- generic runtime observation
- dashboard-only clarification work

Acceptance check:

- existing-skill gaps become candidates
- unrelated work does not create fake lifecycle pressure

### Phase 2 - Review

`review_evolution_candidate` must keep the system in a manual governance state.

The review step must:

- reject missing targets
- reject weak evidence
- produce a review record and diff when evidence is sufficient
- leave the target global skill unchanged

Host-facing expectation:

- if review succeeds, the recommended next action is explicit `apply_evolution_candidate`
- this recommendation must still require confirmation

Acceptance check:

- review creates a governed proposal, not an edit
- host does not need to guess the next manual step

### Phase 3 - Apply

`apply_evolution_candidate` is the mutation boundary.

The apply step must:

- require explicit confirmation
- verify the target hash from review
- write a backup before mutation
- write an application record

Host-facing expectation:

- after apply, the recommended next action is explicit `rollback_evolution_candidate`
- a governance refresh remains visible as a secondary action

Acceptance check:

- the system keeps rollback ready as an explicit follow-up
- apply never looks final or irreversible

### Phase 4 - Rollback

`rollback_evolution_candidate` is the safety close.

The rollback step must:

- require explicit confirmation
- restore the exact original bytes from the recorded backup only
- refuse overwrite if the target changed after apply
- write a rollback record linked to both review and application

Host-facing expectation:

- after rollback, the recommended next action is `governance_report`

Acceptance check:

- the rollback artifact itself is auditable
- the restored target hash matches the pre-apply target hash
- the host sees a clean next step after rollback

## Happy Path

```text
Task exposes gap in existing skill
-> candidate is created
-> maintainer reviews candidate and diff
-> host recommends explicit apply
-> maintainer confirms apply
-> host keeps explicit rollback available
-> maintainer inspects result
-> if needed, maintainer confirms rollback
-> host recommends governance refresh
```

## Failure Boundaries

The lifecycle is not acceptable if any of these happen:

- review mutates the global skill
- apply bypasses confirmation
- rollback overwrites later manual edits
- rollback cannot be traced back to the reviewed proposal
- host receives raw lifecycle data without a clear next action

## Acceptance Criteria

The evolution lifecycle is considered proven when all of these are true:

1. A real existing-skill gap becomes a candidate instead of a duplicate new-skill path.
2. Review produces a governed diff without editing the global skill.
3. Apply requires confirmation, stale-target checks, and backup creation.
4. Rollback restores only from the recorded backup and refuses stale overwrite.
5. Review, apply, and rollback each return explicit host-facing next actions.

## Stop Conditions Before Further Expansion

Do not add more lifecycle surface area until this path is clearly usable.

Stop and reevaluate if work drifts into:

- more dashboard expansion
- automatic apply behavior
- mutation features without stronger operator clarity
- new lifecycle variants before the current path is documented and auditable

## Next Implementation Target

The next practical target should be one of these, in order:

1. create a runbook that exercises `candidate -> review -> apply -> rollback`
2. if needed, add one more acceptance-style test for host-facing lifecycle menus
3. only after that, decide whether any stronger operator guardrail or richer host surface is actually needed
