# Post-Task Distillation Policy

Date: 2026-04-29

## Purpose

This document defines what the runtime should do after a task succeeds.

The goal is not to turn every finished task into a new skill.

The goal is to decide among four outcomes:

- reuse proved enough, learn nothing new
- keep only an observed task record
- create a new skill candidate
- improve an existing skill candidate

## Default Principle

Successful work should always be eligible for observation.

Successful work should not always become a promoted skill candidate.

The runtime must be selective, or the library will become noisy again.

## Decision Outcomes

### Outcome A - Reuse already proved enough

Choose this when:

- the task mostly reused an existing skill successfully
- no meaningful new step or broader pattern appeared
- the result does not reveal a clear improvement gap

Action:

- keep execution logs and usage updates
- do not create a new candidate skill
- do not create an “improve existing skill” candidate

### Outcome B - Keep only an observed task

Choose this when:

- the task succeeded
- the workflow might be useful later
- but confidence is still too low to distill now

Common reasons:

- the task was novel
- the task was only partly structured
- too much of the work depended on one-off judgment
- required inputs were unstable or messy

Action:

- save the observed task
- allow future coverage or clustering logic to revisit it
- do not distill immediately

### Outcome C - Create a new skill candidate

Choose this when most of the following are true:

- the task succeeded clearly
- the useful part of the workflow is repeatable
- the workflow can be described compactly
- the expected inputs and outputs are stable
- the result is not already well covered by an existing active skill

Action:

- capture trajectory if needed
- distill to a staging candidate
- audit before any promotion

### Outcome D - Improve an existing skill candidate

Choose this when:

- an existing skill was relevant or partially used
- the successful task reveals a broader or cleaner version of that workflow
- creating a separate new skill would likely duplicate the existing one

Action:

- keep the successful task as evidence
- create an improvement candidate tied to the existing skill
- review whether to refine scope, inputs, docs, or implementation

## Immediate Do-Not-Distill Rules

Do not distill immediately when any of the following are true:

- the task failed
- the task required heavy one-off judgment
- the task has unclear or unstable inputs
- the task contains high-risk destructive behavior without safe rollback
- the useful workflow cannot yet be described in a compact reusable way

In those cases, keep only logs or observed tasks.

## New Skill vs Improve Existing Skill

Use this split first:

### Prefer “new skill candidate” when:

- the workflow is clearly different from active skills
- the inputs or outputs define a new reusable family
- forcing it into an existing skill would make that skill confusing

### Prefer “improve existing skill candidate” when:

- the workflow is the same family as an existing skill
- the difference is mainly stronger generalization, safer behavior, or clearer arguments
- creating a new active skill would likely fragment search and reuse

## Required Gates Before Distill

Before automatic distillation starts, all of these should pass:

1. Success gate
   - The task or sub-workflow finished successfully.

2. Reusability gate
   - The useful part is repeatable and not mostly one-off reasoning.

3. Shape gate
   - The workflow can be described as a compact task pattern.

4. Safety gate
   - The behavior is within acceptable execution risk and rollback expectations.

5. Coverage gate
   - The runtime can explain why this is not already sufficiently covered by active skills.

If any gate fails, keep the observed task only.

## Suggested First Automatic Policy

The first automatic policy should be conservative:

- always record observed tasks for successful workflow-like execution
- do not auto-distill purely conversational tasks
- do not auto-distill when the task already cleanly reused a strong existing skill
- prefer “observed task only” over immediate distill when uncertain
- only auto-distill when the workflow is concrete, successful, repeatable, and under-covered

This reduces the chance of reintroducing library pollution.

## First Interface Requirement

The first agent-side orchestration boundary should eventually answer two questions after task completion:

1. should this execution be learned from now
2. if yes, should it become:
   - observed task only
   - new skill candidate
   - existing skill improvement candidate

Recommended output shape:

- `learning_decision`: `skip | observed_only | new_skill_candidate | improve_existing_skill`
- `reason`
- `related_skill_name` when the decision is to improve an existing skill
- `should_capture_trajectory`
- `should_distill_now`

## Validation Goal

This policy is successful when the system:

- learns from genuinely reusable work
- does not create noisy skills from one-off tasks
- starts preferring improvement over duplicate skill creation

That is the second half of the automatic learning loop.
