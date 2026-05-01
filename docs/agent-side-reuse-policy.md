# Agent-Side Reuse Policy

Date: 2026-04-29

## Purpose

This document defines when the agent should try to reuse an existing skill automatically.

The goal is to make reuse feel invisible to the user, without turning every task into a forced skill lookup.

## Default Principle

The agent should not ask the user to search for a skill.

Instead:

- the agent receives a normal task
- the agent decides whether silent reuse is worth attempting
- if reuse is safe and likely helpful, it uses it
- if reuse is weak or risky, it just does the work normally

## When To Attempt Silent Reuse

Attempt silent reuse when most of the following are true:

- the task is local and tool-driven
- the task shape is concrete enough to describe in a short workflow phrase
- expected inputs are already known or can be read cheaply
- the likely outcome is repeatable
- the task is closer to execution than to brainstorming

Examples:

- merge files
- transform data files
- clean a directory of text files
- replace text using known inputs

## When Not To Attempt Silent Reuse

Do not attempt silent reuse by default when any of the following are true:

- the task is mainly strategy, product judgment, or open-ended design
- the task is clearly novel and not workflow-like
- the task involves destructive actions with unclear rollback
- the task depends on major context the runtime cannot cheaply reconstruct
- the task is a one-off conversational request with no reusable shape

Examples:

- choose a product direction
- investigate architecture tradeoffs
- write a custom one-time explanation
- delete or rewrite large unknown parts of a project

## Reuse Decision Bands

### Band A - Auto reuse

Allow silent reuse when all of the following are true:

- the top search match is strong enough
- the required arguments are already available
- the skill scope policy does not conflict with the current task
- the expected operation type is low or medium risk

Initial score target:

- top match score `>= 0.85`

### Band B - Reuse candidate, but do not auto-run

Do not auto-run yet when the match looks plausible but not strong enough.

Instead, the agent should continue solving normally while optionally keeping the match as a background hint.

Initial score target:

- top match score `>= 0.75` and `< 0.85`

This keeps the current `RuntimeService.RECOMMENDED_EXECUTION_SCORE = 0.75` useful for recommendation, but sets a stricter bar for silent automatic execution.

### Band C - No reuse

Do not reuse when:

- the top match score is below `0.75`
- the task shape is not clearly reusable
- required arguments are missing
- the risk level is not acceptable

## Required Gates Before Silent Execution

Even a strong match should not auto-run unless these gates pass:

1. Argument completeness
   - All required inputs for the skill are already known.

2. Scope compatibility
   - The skill's scope policy must fit the current working area.

3. Risk compatibility
   - The expected action must not be destructive without a safe rollback story.

4. Result clarity
   - The agent should be able to explain internally what output it expects from the reused step.

If any gate fails, the agent should fall back to normal task execution.

## First Code Integration Point

The first code integration point should be above the current explicit `search -> execute` split, not inside MCP.

Recommended location:

- add a thin orchestration boundary next to `RuntimeService` in `skill_runtime/api/`

Reason:

- `RuntimeService` already contains the reusable primitives
- MCP and CLI currently expose those primitives directly
- the product shift should happen above those primitives, not by growing more MCP tool semantics

Recommended first boundary:

- a new agent-facing policy/orchestration layer that:
  - receives a normal task-shaped request
  - decides whether silent reuse should be attempted
  - calls `RuntimeService.search(...)`
  - auto-executes only when the policy gates pass
  - otherwise returns “solve normally”

## Why MCP Is Not The First Integration Point

MCP still matters, but it is the wrong place to define the new default behavior.

If this policy lives first inside MCP:

- the product shape stays tool-first
- host integrations remain responsible for orchestration
- the runtime keeps looking like a skill toolbox

The intended change is the opposite:

- orchestration should own reuse decisions
- MCP should remain a support interface

## Validation Goal

This policy is successful when the user can give a normal task and the agent:

- silently reuses a strong match when appropriate
- avoids weak or risky automatic reuse
- still completes the task when no good skill exists

That is the first step toward a real automatic learning layer.
