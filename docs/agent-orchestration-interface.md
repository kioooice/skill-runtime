# Agent Orchestration Interface

Date: 2026-04-29

## Purpose

This document defines the first agent-facing runtime boundary.

The goal is to give the agent one place to ask:

- should I silently reuse something now
- after success, should I learn from this task now

This boundary sits above `RuntimeService`.

## Why This Boundary Exists

Today the runtime primitives are real, but they are exposed mostly as separate actions:

- search
- execute
- capture trajectory
- distill
- audit
- promote

That keeps the product feeling like a toolbox.

The orchestration boundary should turn those primitives into one internal decision point for the agent.

## First Interface Scope

The first version should stay narrow.

It should not plan the whole task.

It should only decide:

1. whether silent reuse should be attempted before normal work
2. whether successful work should become observation only, a new candidate, or an improvement candidate afterward

## Recommended Input Shape

The boundary should accept a normal task-shaped request with just enough structure for policy decisions.

Core fields:

- `task_description`
- `working_directory`
- `known_inputs`
- `expected_outputs`
- `risk_level`
- `task_kind`
- `allow_silent_reuse`
- `allow_learning`

The first version should tolerate partial input. Missing information should make the policy more conservative, not fail hard.

## Recommended Output Shape

The boundary should return a single structured decision bundle containing:

- pre-task reuse decision
- optional chosen skill
- optional execution recommendation
- post-task learning decision
- plain-language reasons for both halves

This should be one agent-consumable object, not multiple unrelated payloads.

## Pre-Task Decision Output

Recommended fields:

- `reuse_decision`: `skip | background_hint | auto_execute`
- `reason`
- `skill_name`
- `search_query`
- `search_score`
- `missing_inputs`

Meaning:

- `skip`: do not try reuse
- `background_hint`: a plausible match exists, but do normal work
- `auto_execute`: silent reuse is allowed if arguments are already complete

## Post-Task Decision Output

Recommended fields:

- `learning_decision`: `skip | observed_only | new_skill_candidate | improve_existing_skill`
- `reason`
- `related_skill_name`
- `should_capture_trajectory`
- `should_distill_now`

Meaning:

- `skip`: nothing new worth learning now
- `observed_only`: save the task history, but do not distill yet
- `new_skill_candidate`: create a new candidate
- `improve_existing_skill`: use this result to improve an existing skill family

## First Version Control Flow

### Step 1 - Pre-task policy

The agent sends a task-shaped request to the orchestration boundary.

The boundary decides:

- no reuse
- hint only
- silent auto-reuse

### Step 2 - Task execution

The agent either:

- executes a reused skill
- or completes the task normally

### Step 3 - Post-task policy

After success, the boundary evaluates:

- should this be learned from now
- if yes, how

### Step 4 - Runtime primitive calls

Only after the policy decides should the boundary call lower-level runtime primitives such as:

- `search`
- `execute`
- `capture_trajectory`
- `distill_and_promote`

## First Implementation Cut

The first implementation should not auto-promote anything new.

Keep it conservative:

- allow silent auto-reuse only for strong low-risk matches
- allow observed-task capture first
- delay automatic candidate creation until the orchestration boundary is stable

This keeps the first cut useful without reintroducing skill pollution.

## Recommended Initial API Surface

The first implementation can start with one new class near `RuntimeService`, for example:

- `AgentOrchestrationService`

Recommended first methods:

- `plan_reuse(request) -> ReuseDecision`
- `plan_learning(request, execution_result) -> LearningDecision`
- optional later: `orchestrate(request) -> AgentOrchestrationResult`

This lets the project land the policy in small steps instead of building a large new manager all at once.

## Why This Is The Right First Cut

This boundary is small enough to implement safely, but large enough to change the product shape.

It moves the system from:

- explicit skill tools

toward:

- hidden runtime support under a normal task agent
