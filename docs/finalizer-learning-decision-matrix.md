# Finalizer Learning Decision Matrix

Date: 2026-05-05

## Goal

Define the finalizer-side decision matrix for:

- `skip`
- `observed_only`
- `new_skill_candidate`
- `improve_existing_skill_candidate`

This document explains the governed learning boundary after a task finishes.

The question is:

`Why did this successful task become observation, a new-skill candidate, or an existing-skill evolution candidate instead of one of the other paths?`

If that question cannot be answered clearly, the runtime is still too implicit.

## Scope

This matrix covers:

1. reuse-aware learning decisions after task completion
2. the boundary between clean reuse and existing-skill evolution
3. the boundary between observation and brand-new workflow distillation
4. the minimum evidence required before the system proposes new governed work

This matrix does not cover:

- dashboard rendering
- lifecycle mutation steps such as review/apply/rollback
- task classification before execution
- external provider policy

## Decision Inputs

The finalizer now evaluates these signals:

1. did the task finish successfully
2. was an existing skill silently reused
3. does the payload contain an existing-skill gap signal
4. if so, is that gap signal concrete enough
5. is there a structured execution log
6. does the task have stable expected outputs
7. do the real written outputs match those expected outputs
8. is the task risk too high for immediate distillation

## Decision Matrix

| Situation | Finalizer decision | Why |
| --- | --- | --- |
| Task did not complete successfully | `skip` | no learning path should crystallize from a failed task |
| Learning disabled or task is not workflow-like | `skip` | outside the governed workflow-learning lane |
| Existing skill was reused cleanly, with no real gap evidence | `skip` | reuse already solved the task; no new learning artifact is needed |
| Existing-skill gap signal exists, but is vague | `observed_only` | the task is worth recording, but not worth proposing a governed skill change |
| Existing-skill gap signal includes explicit `evidence` and `proposed_changes` | `improve_existing_skill_candidate` | the task exposed a real gap in an existing workflow skill |
| No structured execution log | `observed_only` | not enough trace detail to distill safely |
| Risk is high or destructive | `observed_only` | capture the trajectory, but do not auto-distill now |
| Expected outputs are missing or unstable | `observed_only` | the workflow pattern is not concrete enough yet |
| Expected outputs exist, but the task only read files or never produced matching output artifacts | `observed_only` | declared intent is not enough; the task did not produce stable output proof |
| Structured execution succeeded, outputs are concrete, and the workflow is under-covered | `new_skill_candidate` | this is the positive case for distilling a brand-new reusable workflow |

## Existing-Skill Improvement Rule

Do not create `improve_existing_skill_candidate` only because:

- the task mentions a known skill
- the task touched files related to a known skill
- the payload contains a shallow `skill_gap` object

The finalizer now requires:

- target existing skill can be identified
- `reason` is present or can be normalized
- `evidence` is explicit
- `proposed_changes` is explicit

If `evidence` or `proposed_changes` is missing, the gap stays at:

`observed_only`

This keeps the evolution lane from turning into a generic “maybe improve this skill later” queue.

## New-Skill Distillation Rule

Do not create `new_skill_candidate` only because:

- the task succeeded
- the task is local
- the request declared `expected_outputs`

The finalizer now requires:

- a structured execution log
- at least one successful write-like operation
- `expected_outputs` that are actually covered by real written paths or produced artifacts

This keeps read-only inspection work and output-mismatch tasks from being treated as stable reusable workflows.

## Positive Cases

### Clean reuse

If a reusable skill already solved the task and no concrete gap signal was exposed:

`skip`

### Existing-skill evolution

If the task exposed a real existing-skill gap with concrete evidence and concrete proposed changes:

`improve_existing_skill_candidate`

### Under-covered new workflow

If the task produced a concrete, written output with matching expected outputs and no existing-skill gap was involved:

`new_skill_candidate`

## Negative Cases

The finalizer should stay conservative in these cases:

### Weak existing-skill gap

Example:

- `skill_gap.reason = "maybe improve this later"`
- no explicit evidence
- no explicit proposed changes

Expected:

`observed_only`

### Read-only success

Example:

- the task inspected files successfully
- `expected_outputs` were declared
- nothing was actually written

Expected:

`observed_only`

### Output mismatch

Example:

- the request expected `demo/output/report_a.json`
- the task actually wrote `demo/output/report_b.json`

Expected:

`observed_only`

## Why This Matrix Matters

Without this matrix:

- weak existing-skill hints become noisy evolution candidates
- weak local tasks become noisy new-skill candidates
- operators cannot explain why the runtime chose one learning path over another

With this matrix:

- reuse remains conservative
- evolution remains evidence-driven
- new-skill distillation remains output-driven
- observation remains the safe fallback instead of a product failure

## Acceptance Standard

This matrix is considered real when all of these are true:

1. clean reuse does not create fake learning work
2. weak existing-skill gaps stay `observed_only`
3. explicit existing-skill gaps become `improve_existing_skill_candidate`
4. read-only and output-mismatch workflows stay `observed_only`
5. concrete under-covered workflows still become `new_skill_candidate`
6. the finalizer reason is explainable without reading implementation code
