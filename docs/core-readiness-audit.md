# Core Readiness Audit

Date: 2026-04-28

## Verdict

Skill Runtime has a usable local MVP, but the core product is not yet complete.

The core loop exists:

`search -> execute -> observed task -> distill -> audit -> promote -> reuse`

The current risk is not that the project cannot run. The risk is that several core quality steps are still only good enough for controlled local workflows, not yet strong enough to call the core finished.

## Current Core Map

| Area | Status | Plain-language meaning | Main gap |
| --- | --- | --- | --- |
| Search and retrieval | MVP usable | The system can find active skills and explain why they matched. | Ranking is still lightweight keyword scoring, not a proven quality search layer. |
| Skill execution | Strong MVP | Active skills can run through one stable `run(tools, **kwargs)` contract and produce operation logs. | Needs more real dogfood cases beyond the current small active library. |
| Observed task capture | Usable | Successful executions can leave a reusable record for later learning. | Needs an acceptance pack that proves records from real tasks keep working end to end. |
| Distillation | Partial core | Known local file workflows can become executable skills through deterministic rules. | Unknown workflows still fall back to a mock provider; this is not real autonomous skill creation yet. |
| Audit | Partial core | Static checks and heuristic semantic checks catch common unsafe or weak skills. | Provider-backed semantic review uses a mock provider by default, so quality judgment is not yet strong enough. |
| Promotion and governance | Solid MVP | Skills move through staging, audit, promotion, archive, and governance reports. | Governance is credible, but depends on audit quality and a small active library. |
| MCP integration | Runnable MVP | MCP server can be built, tools are exposed, and smoke coverage exists. | Smoke proves construction, not a full host round trip on real work. |
| Active skill library | Clean but small | Search is no longer polluted by fixtures and demos, and now includes merge, archive, single-file JSON-to-CSV, directory JSON-to-CSV, single-file text replace, and directory text cleanup dogfood samples. | Six real active skills still do not prove broad usefulness. |

## What Is Already Built

- The runtime has a real service layer shared by CLI and MCP.
- Search returns recommended next actions for the host.
- Execution records operation logs and observed task records.
- Distillation has many deterministic file-workflow rules.
- Audit combines static checks, heuristic semantic checks, and provider-shaped review.
- Promotion is guarded by audit results.
- Governance can report duplicates, fixture skills, cold skills, and follow-up operations.
- Tests cover architecture, contracts, lifecycle, execution, generated skills, governance, MCP smoke, and isolation.

## What Is Not Finished

- Real semantic audit is not wired as the default quality gate.
- Real fallback distillation is not wired as the default generator for unknown workflows.
- Search quality is not evaluated against a task set.
- The active skill library is clean but still too small to prove repeat reuse value.
- MCP is smoke-tested, but not yet proven through a realistic host-style task loop.

## Recommended Mainline

Do not continue by adding unrelated new features.

The project has already passed the “prove the loop is real” stage.

The next stage is not to keep growing a generic skill catalog.

The next stage is to shift the default product shape from explicit skill use to implicit background learning:

- complete the user task first
- quietly reuse existing skills when the match is strong enough
- automatically decide whether successful work should become a new skill or improve an old one
- keep MCP as a support interface, not the main user experience

See:

- `docs/agent-first-runtime-architecture.md`
- `docs/agent-mainline-readiness-review.md`

The current question is no longer only “can this direction exist”.

That part is now sufficiently proven.

The current question is:

- should the default top-level product path switch to the new agent-first route yet

Current answer:

- not yet

## Next Options

1. Agent-side reuse policy
   - Benefit: starts hiding skill search behind the agent, which is closer to the target product shape.
   - Cost: needs careful boundaries so reuse does not trigger too aggressively.

2. Post-task automatic distillation policy
   - Benefit: moves the system toward self-improving behavior after real work.
   - Cost: needs clear rules for when to create, improve, or skip a skill.

3. Real-task dogfood on the new policy path
   - Benefit: validates the intended product shape using real work instead of more generic samples.
   - Cost: may expose several gaps at once and require tighter stage control.

## Recommended Choice

Start with option 1: agent-side reuse policy.

Reason: the main missing piece is no longer proof that skills can exist. The main missing piece is that the agent still behaves like a user of a skill library instead of a system with a hidden learning layer.
