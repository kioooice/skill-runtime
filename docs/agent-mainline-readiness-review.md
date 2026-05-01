# Agent Mainline Readiness Review

Date: 2026-04-29

## Verdict

The new agent-first path is real enough to be treated as a preferred experimental path.

It is not ready to replace the default top-level product path across the whole project yet.

## What Is Already True

- The project now has a hidden capability-layer direction, not only an explicit skill-library direction.
- The new path already exists in runnable code:
  - planning for quiet reuse
  - planning for post-task learning
  - lifecycle helpers
  - a minimal task runner
  - a host-facing facade
- Real callers can already reach it through:
  - CLI
  - service helpers
  - `skill_runtime.api.host`
- Fast tests already prove the new path is not just documentation.

## What Is Still Missing Before A Default Switch

- `run_task(...)` still uses a minimal execution strategy, not a broad host-ready strategy.
- `improve_existing_skill` is still a decision outcome, not a complete lifecycle path.
- Unknown-workflow generation is still not strong enough to become a silent default background promise.
- Search is usable, but still not mature enough to become a universal silent-routing layer.
- A real host path has not yet been used as the first controlled experimental integration target.

## Recommendation

Do not switch the full default top-level path yet.

Use the new path as a preferred experimental path first.

## Recommended Next Step

Choose one controlled, low-risk, reversible real host path and wire it to `skill_runtime.api.host`.

That first trial path should be small enough to roll back easily, but real enough to validate:

- reuse planning
- execution behavior
- learning planning
- rollback expectations

## First Trial Target

The first controlled trial target is an isolated MCP tool:

- `run_agent_task_experimental`

Why this target:

- it is a real host-facing path
- it reuses the new `skill_runtime.api.host` facade directly
- it does not replace the existing `search_skill` / `execute_skill` mainline
- it is additive and easy to roll back if behavior is weak

## Stop Rule

Do not widen the default path until one real host path has validated the new facade under normal use.

## Current Closure

The current recommended closure point is:

- stop at `capture + recommendation`

Reason:

- this now covers both demo-style workflows and real project-maintenance workflows
- it proves the agent-first layer is useful without taking on automatic promotion risk too early

See:

- `docs/agent-layer-stage-closure.md`
