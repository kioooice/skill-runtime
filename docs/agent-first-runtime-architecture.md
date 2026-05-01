# Agent-First Runtime Architecture

Date: 2026-04-29

## Goal

The target product shape is not a user-facing skill marketplace.

The target is an agent that completes real work first, while the runtime learns in the background:

`do task -> observe steps -> decide reuse value -> distill or improve skill -> reuse later automatically`

The user should not need to think about searching for skills in normal use.

## Product Shape

### What the user should experience

- The user gives a normal task.
- The agent tries to complete it directly.
- If a useful reusable step already exists, the agent uses it quietly.
- If no reusable step exists, the agent completes the task normally.
- After success, the system decides whether part of the work should become a reusable skill.
- On later similar tasks, the system prefers reuse automatically.

### What the user should not need to do

- Manually browse a skill list before asking for work
- Think in terms of skill names
- Decide by hand whether a finished task should become a reusable skill
- Re-run the same “teach the system” ceremony each time

## Architecture Layers

### 1. Task Agent Layer

Responsible for understanding the user request and finishing the task.

This is the only layer the user should feel directly.

### 2. Execution Orchestration Layer

Responsible for planning steps, calling tools, collecting outputs, and deciding when to continue or retry.

This layer can ask the runtime for reuse help, but it should not force explicit “search skill first” behavior for every task.

### 3. Skill Evolution Layer

Responsible for background learning:

- detect repeated or reusable steps
- match against existing skills
- decide whether to reuse, create, or improve a skill
- distill successful trajectories
- audit generated candidates
- promote, reject, archive, or revise skills
- adjust future reuse priority

This is the real core of the product direction.

### 4. Interface Layer

Includes MCP, CLI, scripts, and governance tools.

This layer is still useful, but it is not the main product shape. It should serve:

- debugging
- external host integration
- smoke checks
- governance
- manual intervention

## Current State vs Target

### Current default shape

The current system is closer to:

`search skill -> execute skill -> maybe distill/promote`

This proves the runtime parts exist, but it still feels like a tool-driven skill library.

### Target default shape

The target system should behave more like:

`execute task -> quietly reuse if possible -> quietly learn if valuable -> reuse better next time`

This is agent-first, with the runtime acting as a hidden capability layer.

## Why the Previous Path Should Stop Here

Six generic dogfood skills are enough to prove the loop is not fake.

Adding more generic samples now has weak return:

- it does not change the product shape
- it does not prove automatic learning in real work
- it risks drifting into a manual skill catalog mentality

From this point, new samples should come from real task execution or from targeted regression coverage, not from chasing a larger generic count.

## New Mainline

The next mainline is not “add more generic skills”.

The next mainline is:

1. make reuse an agent-side default attempt
2. make post-task distillation an automatic decision path
3. make skill improvement compete with new skill creation
4. make MCP a support interface, not the primary product behavior

## Migration Path

### Stage 1 - Preserve the current runtime as the capability core

Keep existing search, execute, observed task, distill, audit, and promote primitives.

Do not throw away the current MCP and CLI surfaces.

### Stage 2 - Add an agent-side reuse policy

Introduce a thin policy layer that answers:

- should the agent attempt reuse here
- should it search silently or solve directly
- how strong must the match be before reuse

The important shift is that reuse becomes an internal decision, not a user-visible ritual.

### Stage 3 - Add post-task automatic distillation decisions

After a successful task, evaluate:

- was this reusable
- is it a brand-new skill
- is it an improvement to an existing skill
- should it stay only as an observed task

This is where the product begins to feel self-improving.

See:

- `docs/post-task-distillation-policy.md`
- `docs/agent-orchestration-interface.md`

### Stage 4 - Add skill-improvement logic

Do not treat every successful new trajectory as a new skill candidate.

The system should also consider:

- refine an existing skill
- widen an existing skill description
- increase confidence in reuse
- leave the existing skill unchanged

### Stage 5 - Use real tasks as the primary proof

Validation should shift from generic sample count to real-task outcomes:

- did the agent reuse something helpful without user prompting
- did it avoid bad reuse
- did it learn a useful new step after the task
- did later similar work become easier or more reliable

## Stop Rules

Stop adding generic dogfood samples by default when all of the following are true:

- the main loop has already passed on several real samples
- search, execute, distill, audit, and reuse are each proven more than once
- the next generic sample would not change architecture confidence

After that point, only continue generic samples when they expose a specific missing class of behavior.

Otherwise switch to:

- real-task dogfood
- automatic distillation policy
- reuse policy
- skill-improvement policy

## Immediate Next Step

Implement the architecture pivot in small safe steps:

1. define the agent-side reuse policy boundary
2. define the post-task automatic distillation decision boundary
3. choose the first place in code where explicit skill-first behavior should be hidden behind agent-side orchestration

This should happen before adding more generic active skills.
