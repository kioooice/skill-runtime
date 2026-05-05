# Maintainer Review Cleanup Mainline Acceptance

Date: 2026-05-05

## Goal

Define the second maintainer-facing mainline for Skill Runtime using the existing review cleanup demo.

This mainline is:

`review comments -> maintainer cleanup plan -> governed learning artifact`

The question is:

`Can the system help a maintainer turn review comments into an explicit cleanup plan without pretending that open-ended review work is already a silent runtime lane?`

If the answer is yes, this is a real maintainer mainline.

## Scope

This acceptance path covers:

1. what the maintainer-facing cleanup output should look like
2. how the Codex-facing runtime gate should currently classify this task family
3. how the workflow leaves a governed learning artifact
4. what should remain explicit instead of silently automated

This acceptance path does not cover:

- GitHub connector automation
- automatic code fixing from review comments
- silent promotion of a review-cleanup skill
- widening the phase-one default-in lane

## Chosen Task Family

### Review cleanup

Input shape:

- structured review comments
- maintainer intent to group them into required fixes and follow-up work

Expected output shape:

- a maintainer-facing cleanup plan
- grouped required changes
- clear follow-up items
- no unreviewed code mutation

This output must reduce maintainer review overhead, not just echo the raw comments back.

## Why This Is A Real Mainline

Maintainers repeatedly spend time turning scattered review comments into:

- what must be fixed now
- what can wait
- what should block merge

That is real workflow value even when the underlying implementation work still requires human judgment.

## Mainline Phases

### Phase 1 - Cleanup output quality

The expected output must be maintainer-facing.

Acceptance check:

- the cleanup plan is grouped and actionable
- the plan separates required work from follow-up work
- the result is review-oriented, not runtime-internal

### Phase 2 - Runtime gate boundary

At the current product boundary, open-ended review cleanup should remain conservative.

Expected current classification:

- `bucket: default-out`
- `runtime_lane_status: skipped`

Reason:

- the task is dominated by open-ended reasoning
- the current phase-one runtime lane should not silently take over review judgment

This is not a failure.

It is a deliberate boundary.

### Phase 3 - Governed learning artifact

Even when the runtime gate stays conservative, the workflow should still be capturable.

Acceptance check:

- the observed task can be captured into a trajectory
- the output recommends explicit distillation
- no active skill is silently promoted

### Phase 4 - Explicit follow-up

This task family should still keep the learning path explicit.

Acceptance check:

- success leaves a trajectory artifact
- the next action is `distill_trajectory`
- promotion remains a deliberate later step

## What This Mainline Proves

If this path passes, it proves:

1. Skill Runtime can support a real maintainer review workflow without pretending that all review work is low-risk automation.
2. The project can handle valuable maintainer workflows even when the runtime lane should stay conservative.
3. Governed learning is still useful outside silent reuse.

## What It Does Not Prove

This path does not prove:

- that review cleanup should move into `default-in`
- that open-ended review reasoning should be silently auto-executed
- that the system should automatically turn cleanup plans into code changes

## Acceptance Standard

This mainline is considered real when all of these are true:

1. The cleanup plan is actually useful to a maintainer.
2. The current conservative runtime classification is explicit and explainable.
3. The workflow can still be captured into a governed trajectory.
4. No automatic promotion or hidden mutation happens.
