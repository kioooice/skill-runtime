# Codex Integration

This document is the Codex-specific wiring guide for the local skill runtime.

It describes the current transition from:

- MCP-first skill tooling

to:

- Codex-first background capability routing

## Recommended Integration Shape

For Codex, this runtime should be treated as a local background capability layer, not as a second chat agent.

MCP is still an important host transport, but it is no longer the full product identity.

Earlier integration flow:

```text
Codex
-> MCP server: skill_runtime
-> runtime service
-> skill store / trajectories / audits
```

Current preferred flow:

```text
User task
-> Codex
-> task classification
-> runtime lane when appropriate
-> normal execution
-> capture + recommendation
```

That keeps:

- user interaction in Codex
- skill lifecycle inside the runtime
- future model-provider changes internal to the runtime

## Why This Matches Codex

OpenAI’s Docs MCP guide states that Codex can connect to MCP servers through shared configuration in `~/.codex/config.toml`.

OpenAI’s App Server article also states:

- MCP is a good fit when you already have an MCP-based workflow and want callable tools
- App Server is the first-class protocol for full Codex harness integration

For this project, MCP remains the correct transport because this runtime is still a capability layer under Codex, not a replacement for the Codex harness.

What changed is the product description:

- before: “Codex calls MCP tools”
- now: “Codex uses a background runtime lane, and MCP is one way that lane is exposed”

## Installed Codex Config

The local Codex config now includes a `skill_runtime` MCP server entry.

It no longer needs to hard-bind the runtime to one repository root.

The current setup uses a small launcher that prefers the active workspace as the runtime root and only falls back to `vibe` when no better root is available.

```toml
[mcp_servers.skill_runtime]
command = "powershell"
args = ["-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "C:/Users/Administrator/.codex/launch-skill-runtime.ps1"]
```

Config file:

`C:/Users/Administrator/.codex/config.toml`

## What Codex Can Call

The runtime currently exposes these MCP tools:

- `search_skill`
- `execute_skill`
- `distill_trajectory`
- `distill_and_promote_candidate`
- `audit_skill`
- `promote_skill`
- `log_trajectory`
- `capture_trajectory`
- `reindex_skills`
- `backfill_skill_provenance`
- `governance_report`
- `distill_coverage_report`
- `archive_duplicate_candidates`
- `archive_fixture_skills`
- `archive_cold_skills`

## Recommended Codex Workflow

For repetitive or workflow-like tasks, the preferred behavior is no longer “search skill first by ritual”.

The preferred behavior is:

1. classify whether the task should enter the runtime lane
2. if it should, try quiet reuse conservatively
3. if reuse is weak or unsuitable, let Codex complete the task normally
4. after success, keep `capture + recommendation` as the default learning depth
5. use explicit MCP tools only when manual control, debugging, or governance is the real goal
6. use `governance_report`, `distill_coverage_report`, `reindex_skills`, `backfill_skill_provenance`, `archive_duplicate_candidates`, `archive_fixture_skills`, and `archive_cold_skills` for library maintenance

## Runtime Lane Visibility

Codex-facing orchestration results expose runtime lane visibility directly:

- `runtime_lane_status`
- `runtime_lane_reason`

`runtime_lane_status` has three values:

- `used`: the lane actually auto-executed a reusable skill, or captured learning payload
- `entered`: the task entered the lane, but no skill execution or learning capture happened
- `skipped`: the task stayed on the normal Codex path

`runtime_lane_reason` explains the status in one sentence, including the classifier bucket
or reuse / learning decision when useful.

This is the operator-facing check for "did Skill Runtime actually participate?".
Normal Codex work should not require manual skill lookup just to answer that question.

For scriptable local inspection, use:

```bash
python -m skill_runtime.cli runtime-events --limit 20
python -m skill_runtime.cli runtime-events --global --scan-root D:\02-Projects --limit 20
```

This reads `.skill_runtime/runtime_lane_events.jsonl` and returns JSON with recent
events, `used / entered / skipped` counts, and learning follow-up fields such as
`recommended_next_action` and available host operation labels.

The explicit MCP-first loop still exists, but it is now a support path:

1. `search_skill`
2. `execute_skill`
3. `recommended_host_operation`
4. `distill_and_promote_candidate` or the explicit lifecycle path

`governance_report` recommendations are now host-call aligned. A Codex host can read
`recommended_actions[].host_operation` and directly call the named MCP tool with the
returned arguments, instead of translating a prose suggestion into a separate tool call.

For archive recommendations, the payload also includes a dry-run `preview` call so the
host can offer "preview" and "apply" from the same recommendation object.

The governance tools now also form one consistent maintenance loop:

1. `reindex_skills`
2. `governance_report`
3. `backfill_skill_provenance`
4. `archive_duplicate_candidates`
5. `archive_fixture_skills`
6. `archive_cold_skills`

Any maintenance tool that refreshes or mutates library state now points back to
`governance_report` as the approved follow-up, so Codex hosts can keep returning to the
same review surface after each maintenance action.

Search responses now expose the same pattern. Codex can read:

- `results[].host_operation` for per-result execution
- `recommended_host_operation` for the top-level recommended next step
- `available_host_operations` for a render-ready action list

When multiple skills match strongly, that list now includes the top recommended run action
followed by additional matched-skill actions.

Execute responses now continue that same contract. After a successful `execute_skill`,
Codex can use:

- `observed_task_record` as the runtime-produced artifact
- `observed_task` as the inline artifact payload
- `recommended_host_operation` to call `distill_and_promote_candidate`
- `available_host_operations` to present the approved next actions directly

That means the host should not synthesize `observed_task_path` itself when the runtime
has already returned it. If the host prefers not to pass file paths around, it can use
the secondary inline `observed_task` follow-up action from `available_host_operations`.

`distill_coverage_report` now follows the same idea for observability. Besides
`view_host_operations`, the combined `all` view will also recommend the execution-only view
when fallback and backlog work are both clear but execution-derived traffic is still present,
so Codex can continue drilling into the next useful review surface instead of stopping on an
empty recommendation.

## Host-Call Lifecycle Loop

The explicit lifecycle tools now do the same:

- `log_trajectory` recommends `distill_trajectory`
- `capture_trajectory` recommends `distill_trajectory`
- `distill_trajectory` recommends `audit_skill`
- `audit_skill` recommends `promote_skill` when the audit passes
- `promote_skill` recommends `execute_skill` for the newly active skill
- `distill_and_promote_candidate` recommends `execute_skill` after a successful promotion

That removes most of the remaining host-side sequencing logic for the manual lifecycle path.

For no-strong-match search fallbacks, Codex now gets `capture_trajectory` as the primary
recommended action and `distill_and_promote_candidate` as a secondary available action.
The shorter-path operation still exposes both `trajectory_path` and `observed_task_path`
in `argument_schema`, plus inline `observed_task`, along with optional `skill_name` and `register_trajectory`, so
Codex integrations can drive the right input collection flow explicitly.
The no-strong-match action list now also includes an inline `capture_trajectory(observed_task=...)`
variant, so hosts can choose between file-backed and in-memory capture without inventing
their own contract shape.
The accepted observed-task artifact shapes are documented centrally in
`docs/mcp-integration.md` under `Observed Task Input Shapes`.

For governance dry runs, `archive_duplicate_candidates(dry_run=true)` now returns the
apply call as the primary follow-up and leaves `governance_report` in
`available_host_operations` as a secondary option. After a real archive run, refresh
remains the primary follow-up.

Host-operation payloads now also include:

- `operation_id`
- `operation_role`
- `operation_group`
- `delivery_mode`
- `variant_role`
- `source_ref`
- `display_label`
- `effect_summary`
- `argument_schema`
- `risk_level`
- `requires_confirmation`
- `confirmation_message`

So Codex-side integrations can make consistent UX choices for low-risk execution,
medium-risk promotion flows, and high-risk archive actions.
Those values are driven by shared runtime presets unless a specific workflow supplies a
more specific override.
For paired host actions, `operation_group` and `delivery_mode` let Codex-side hosts present
file-backed and inline variants as one grouped choice instead of unrelated buttons.
`variant_role` then tells the host which grouped variant is the runtime-preferred default
and which one should be treated as the alternate path.
For `execute_skill`, `argument_schema.args.properties` is now expanded from the skill's
metadata input schema, which lets Codex-side hosts build parameter UIs from concrete fields
instead of treating `args` as an undifferentiated object.

For maintainers, the current contract is intentionally split into three layers:

- operation builders emit a single host-call payload
- recommendation builders emit `recommended_next_action`, `recommended_host_operation`, and
  `available_host_operations`
- governance action builders emit `recommended_actions[].host_operation`

New runtime flows should extend those shared builders instead of hand-authoring top-level
recommendation dictionaries in service or report code. `source_ref` should also come from
shared builder helpers so Codex-side logging and reconciliation remain stable across
refactors.
Internally, those builders are now separated into `source_refs.py`, `operation_builders.py`,
`recommendation_builders.py`, and `governance_actions.py`, while
`skill_runtime.mcp.host_operations` remains the stable import surface for the rest of the
runtime and any external callers.
The same contract guard is checked by `python scripts/check_mcp_architecture.py` and is
also run in `.github/workflows/runtime-contracts.yml`.
Payload shape invariants are checked separately by `python scripts/check_runtime_contracts.py`.
That guard now also covers the adjacent runtime layering around `service`, `governance`,
and `retrieval`, so orchestration and host-contract logic do not drift back into
cross-layer imports.
It now also covers the nearby `memory`, `distill`, `audit`, and `execution` layers, so
trajectory capture, generation, review, and execution helpers stay separated from the
orchestration layer instead of reacquiring cross-layer dependencies.

This keeps Codex responsible for:

- task understanding
- planning
- user communication

And keeps the runtime responsible for:

- skill storage
- audit
- retrieval
- provenance
- execution

## Runtime Relocation

If you move this runtime project, update the launcher path or fallback root in:

`C:/Users/Administrator/.codex/config.toml`

The current launcher is:

`C:/Users/Administrator/.codex/launch-skill-runtime.ps1`

If the active workspace should be preferred, keep the launcher pattern.

If you want to re-bind the runtime to a single fixed repository again, you can replace the launcher with a direct script call.

## Recommended Dogfooding Loop

For real repeated work, the shortest useful loop is now:

1. `search_skill`
2. `execute_skill`
3. keep the returned `observed_task_record`
4. if the task was new or improved, follow `recommended_host_operation` into `distill_and_promote_candidate`
5. if an explicit governed path is needed, use the host-call lifecycle loop above
6. when library state changes, run the governance maintenance loop starting from `governance_report`

That gives Codex a practical `reuse -> observe -> distill -> govern` loop without hand-writing trajectories.

## Current Limits

- This is still not full Codex App Server integration.
- You do not get richer Codex session semantics such as native diff-stream interactions through this runtime MCP layer.
- The current system is already more than “a set of MCP tools”, but it is still not a universal always-on lane for every Codex task.
- If you later want deeper integration with Codex itself, the next protocol to consider is Codex App Server rather than replacing this MCP layer.

## Sources

- OpenAI Docs MCP quickstart for Codex: https://developers.openai.com/learn/docs-mcp
- OpenAI App Server architecture and protocol guidance: https://openai.com/index/unlocking-the-codex-harness/
