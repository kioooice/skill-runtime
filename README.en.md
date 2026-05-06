# Skill Runtime

[中文说明](./README.zh-CN.md)

`Skill Runtime` is a local workflow governance layer for Codex-style coding agents. It helps open-source maintainers turn repeated review, triage, release, handoff, and maintenance automation workflows into auditable, reusable, improvable skills.

It is designed as a capability layer under tools like Codex, not as a second chat agent.

## Who It Is For

This project is for:

- open-source maintainers who want repeated maintenance work to outlive chat history
- agents that completed a workflow once and should not re-plan it from scratch next time
- teams that need audit, provenance, and promotion records before reusing automation
- Codex / MCP / CLI hosts that need a local-first governed skill lifecycle layer

One-line positioning:

```text
Skill Runtime helps Codex-style agents capture, audit, reuse, and improve repeatable maintainer workflows.
```

## What It Does

Most AI systems can complete tasks, but they often fail to build a governed layer of reusable workflows.

Typical failure modes are:

- repetitive tasks get solved from scratch every time
- successful workflows remain trapped in chat history
- agent-generated scripts or skills are stored without audit or lifecycle rules
- skill search and reuse become black boxes with weak explainability

Skill Runtime focuses on governing skills, then gradually hiding that lifecycle under normal Codex task execution.

The runtime supports a full local loop:

`search -> execute -> distill -> audit -> promote -> reuse`

It now also supports a lighter execution feedback loop:

`search -> execute -> observed task record -> capture/distill`

That means a host AI can:

- search for an existing reusable skill before rebuilding a workflow
- execute active skills through a stable `run(tools, **kwargs)` contract
- automatically emit an observed task record after successful execution
- distill successful trajectories into staging skills
- audit candidate skills with static and semantic checks
- promote only passed skills into the active library
- reuse previously learned skills on future tasks

## Core Properties

- `Host-first`: the host AI keeps planning, task understanding, and user interaction
- `Governed`: new skills pass through staging, audit, and promotion before becoming active
- `Explainable`: search results can expose match reasons, rule provenance, and recommended next action
- `Extensible`: the same runtime is exposed through CLI and MCP, but neither is the final product shape
- `Local-first`: storage is file-based and easy to inspect
- `Provenance-visible`: imported, distilled, exported, and legacy skills should keep explicit source history

## Maintainer Workflow Demos

- [Review cleanup](./docs/maintainer-review-cleanup-demo.md)
- [Release readiness](./docs/maintainer-release-readiness-demo.md)
- [Handoff continuation](./docs/maintainer-handoff-continuation-demo.md)

## Open Source Participation

- [Contributing Guide](./CONTRIBUTING.md)
- [Security Policy](./SECURITY.md)
- [Code Of Conduct](./CODE_OF_CONDUCT.md)
- [Open Source Release Readiness Checklist](./docs/open-source-release-readiness-checklist.md)
- [Codex Open Source Application Draft](./docs/codex-open-source-application-draft.md)

## Product Shape

The project has moved through two different descriptions.

### Earlier description

```text
Codex
-> MCP tool calls
-> runtime service
```

That shape is still technically true, but it is no longer the best product description.

### Current description

```text
User task
-> Codex
-> runtime gate
-> normal execution
-> runtime finalize
```

In this shape:

- Codex stays responsible for user interaction and task completion
- the runtime quietly decides when reuse is worth attempting
- successful work can be captured after execution
- MCP remains a useful host interface, not the main product identity

## Current Architecture

```text
Host AI
-> runtime gate / lifecycle adapter
-> Runtime service
-> skill store / trajectories / audits
-> CLI / MCP / scripts as interface surfaces
```

Main workspace layout:

```text
scripts/
  skill_cli.py
  skill_mcp_server.py

skill_runtime/
  api/
  mcp/
  memory/
  distill/
  audit/
  retrieval/
  execution/
  governance/

skill_store/
  staging/
  active/
  archive/
  rejected/
  index.json

trajectories/
audits/
demo/
tests/
docs/
```

Architecture maintenance guard:

- run `python scripts/check_mcp_architecture.py` to verify the documented layering and contract boundaries
- run `python scripts/check_runtime_contracts.py` to validate host-operation and recommendation payload invariants
- deeper MCP contract details live in [MCP Integration](./docs/mcp-integration.md)
- Codex-facing default-lane details live in [Codex Integration](./docs/codex-integration.md)
- privacy, external provider, and provenance boundaries live in [Privacy And Provenance](./docs/privacy-and-provenance.md)
- the current architecture pivot is summarized in [Agent-First Runtime Architecture](./docs/agent-first-runtime-architecture.md)
- the current runtime layering guard explicitly covers `service / governance / retrieval`
- it also covers `memory / distill / audit / execution`

## Feature Snapshot

### Runtime service

- shared service layer used by both CLI and MCP
- top-level recommendation fields on search:
  - `recommended_next_action`
  - `recommended_skill_name`
  - `recommended_host_operation`
- successful execute responses now also include:
  - `recommended_next_action`
  - `recommended_reason`
  - `recommended_host_operation`
- explicit lifecycle responses now also include host follow-ups:
  - `log_trajectory -> distill_trajectory`
  - `capture_trajectory -> distill_trajectory`
  - `distill_trajectory -> audit_skill`
  - `audit_skill -> promote_skill` on pass
  - `promote_skill -> execute_skill`

### Distillation

- rule-based executable generation for known local automation patterns
- fallback provider pipeline for unmatched successful trajectories
- optional external fallback provider command via `SKILL_RUNTIME_FALLBACK_PROVIDER_CMD`
- included local demo fallback provider in `examples/providers/copy_metadata_fallback_provider.py`
- DeepSeek fallback provider in `examples/providers/deepseek_fallback_provider.py`
- current rule registry includes:
  - text merge
  - text replace
  - single-file transform
  - batch rename
  - directory copy
  - directory move
  - directory-wide text replace
  - CSV to JSON
  - JSON to CSV

### Audit

- static checks for dangerous commands, shell usage, missing entrypoints, and hardcoded paths
- provider-backed semantic review with prompt artifacts and a mock provider by default
- optional external semantic review command via `SKILL_RUNTIME_SEMANTIC_PROVIDER_CMD`
- provider command details live in [Provider Integration](./docs/provider-integration.md)
- included local demo semantic provider in `examples/providers/pass_semantic_review_provider.py`
- DeepSeek semantic review provider in `examples/providers/deepseek_semantic_review_provider.py`
- semantic checks for:
  - trajectory alignment
  - parameter coverage
  - template-like skills
  - retrieval-oriented docstring structure

### Retrieval

- active-skill indexing through `skill_store/index.json`
- lightweight hybrid ranking
- provenance surfaced in search results:
  - `host_operation`
  - `rule_name`
  - `rule_priority`
  - `rule_reason`
  - `score_breakdown`
  - `library_tier`
  - `why_matched`

### Governance

- strict staging -> audit -> promote flow
- provenance persistence on promoted skills
- legacy provenance backfill command
- cold-skill archival through `archive-cold`
- lightweight governance reporting through `governance-report`
  - duplicate clusters now include `canonical_skill` and `archive_candidates`
  - host-friendly `recommended_actions`
  - each recommended action now includes a `host_operation` payload with the MCP `tool_name`
    and `arguments` needed for direct host execution
- duplicate candidate archival through `archive-duplicate-candidates`

## Local Installation

### Clone-to-Verify Path

From a fresh clone, run this sequence from the repository root:

```bash
python -m pip install --upgrade pip
python -m pip install -e .
python scripts/check_mcp_architecture.py
python scripts/check_runtime_contracts.py
python -m unittest tests.test_runtime_fast -v
python -c "from skill_runtime.mcp import build_mcp_server; build_mcp_server('.')"
python -m skill_runtime.cli search --query "merge txt files into markdown"
python -m skill_runtime.mcp_stdio --help
```

Expected result:

- the architecture and runtime contract checks pass
- the fast runtime suite passes
- the MCP smoke command exits without starting a long-running stdio loop
- the search command returns `merge_text_files` near the top of the results

The full runtime suite is intentionally broader and slower:

```bash
python -m unittest tests.test_runtime -v
```

Use it before release-level changes or when broad runtime generation behavior may be affected. On the current Windows development machine it takes about 9 minutes. To inspect slow tests:

```bash
python scripts/profile_runtime_tests.py --suite tests.test_runtime --top 20
```

If `skill-runtime` or `skill-runtime-mcp` is not on your shell `PATH` after install, use the portable module commands shown above.

Install the runtime in editable mode from the project root:

```bash
python -m pip install --upgrade pip
python -m pip install -e .
```

Minimum local verification:

```bash
python scripts/check_mcp_architecture.py
python scripts/check_runtime_contracts.py
python -m unittest tests.test_runtime_fast -v
python -c "from skill_runtime.mcp import build_mcp_server; build_mcp_server('.')"
```

Installed command entrypoints:

```bash
skill-runtime search --query "<task>"
skill-runtime-mcp --root .
```

Portable module entrypoints:

```bash
python -m skill_runtime.cli search --query "<task>"
python -m skill_runtime.mcp_stdio --root .
```

Local runtime usage statistics are stored in `.skill_runtime/usage.json`, which is ignored by Git so normal skill execution does not dirty versioned active-skill metadata.

## CLI Quick Start

```bash
skill-runtime search --query "<task>"
skill-runtime execute --skill <skill_name> --args-file <json file>
skill-runtime distill --trajectory <trajectory.json> --skill-name <optional_name>
skill-runtime distill-and-promote --trajectory <trajectory.json> --skill-name <optional_name>
skill-runtime distill-and-promote --observed-task <observed_task.json> --skill-name <optional_name>
skill-runtime audit --file <skill.py>
skill-runtime promote --file <staging_skill.py>
skill-runtime log-trajectory --file <trajectory.json>
skill-runtime capture-trajectory --file <observed_task.json>
skill-runtime reindex
skill-runtime archive-cold --days 30
skill-runtime governance-report
skill-runtime distill-coverage-report
skill-runtime archive-duplicate-candidates --dry-run
skill-runtime archive-duplicate-candidates --skill-name <name>
skill-runtime backfill-provenance
```

Legacy script path still works from the repo root:

```bash
python scripts/skill_cli.py search --query "<task>"
python scripts/skill_cli.py execute --skill <skill_name> --args-file <json file>
python scripts/skill_cli.py distill --trajectory <trajectory.json> --skill-name <optional_name>
python scripts/skill_cli.py distill-and-promote --trajectory <trajectory.json> --skill-name <optional_name>
python scripts/skill_cli.py distill-and-promote --observed-task <observed_task.json> --skill-name <optional_name>
python scripts/skill_cli.py audit --file <skill.py>
python scripts/skill_cli.py promote --file <staging_skill.py>
python scripts/skill_cli.py log-trajectory --file <trajectory.json>
python scripts/skill_cli.py capture-trajectory --file <observed_task.json>
python scripts/skill_cli.py reindex
python scripts/skill_cli.py archive-cold --days 30
python scripts/skill_cli.py governance-report
python scripts/skill_cli.py distill-coverage-report
python scripts/skill_cli.py archive-duplicate-candidates --dry-run
python scripts/skill_cli.py archive-duplicate-candidates --skill-name <name>
python scripts/skill_cli.py backfill-provenance
```

Successful `execute` calls now return an `observed_task_record` path. That file can be:

- captured into a standard trajectory with `capture-trajectory`
- sent directly into `distill-and-promote --observed-task`

## MCP Quick Start

Start the stdio MCP server from the project root:

```bash
skill-runtime-mcp --root .
```

Portable module entrypoint:

```bash
python -m skill_runtime.mcp_stdio --root .
```

Legacy script path still works from the repo root:

```bash
python scripts/skill_mcp_server.py
```

Or from any directory:

```bash
python D:/02-Projects/vibe/scripts/skill_mcp_server.py --root D:/02-Projects/vibe
```

Current MCP tools:

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

`distill_coverage_report` summarizes how many saved successful trajectories currently hit
deterministic rules versus `llm_fallback`, and clusters the remaining fallback hotspots by
tool sequence and inferred input schema.

`governance_report` now returns host-ready recommendations. Example:

```json
{
  "action": "archive_duplicate_candidates",
  "reason": "Keep \"merge_text_files\" as canonical and archive lower-priority duplicates.",
  "host_operation": {
    "type": "mcp_tool_call",
    "tool_name": "archive_duplicate_candidates",
    "display_label": "Archive duplicates",
    "risk_level": "high",
    "requires_confirmation": true,
    "arguments": {
      "skill_names": ["merge_text_files_generated"],
      "dry_run": false
    },
    "preview": {
      "tool_name": "archive_duplicate_candidates",
      "display_label": "Preview archive",
      "risk_level": "low",
      "requires_confirmation": false,
      "arguments": {
        "skill_names": ["merge_text_files_generated"],
        "dry_run": true
      }
    }
  }
}
```

That lets a host go directly from recommendation display to:

- preview via the `preview` call
- execution via the main `host_operation` call

Governance maintenance loop:

1. call `reindex_skills` after active-library changes
2. call `governance_report` to inspect duplicates and maintenance actions
3. call `backfill_skill_provenance` when legacy metadata needs rule provenance
4. call `archive_duplicate_candidates` to preview or apply duplicate cleanup
5. call `archive_fixture_skills` to preview or apply fixture-skill cleanup
6. call `archive_cold_skills` to move stale active skills into the archive

All maintenance tools that mutate or refresh library state now converge back to
`governance_report` as the approved follow-up, so a host can keep using one stable review
surface after each maintenance step.

`search_skill` now follows the same pattern:

- each result includes `host_operation`
- the top-level response includes `recommended_host_operation`
- the top-level response also includes `available_host_operations`

Example:

```json
{
  "recommended_next_action": "execute_skill",
  "recommended_skill_name": "merge_text_files",
  "recommended_host_operation": {
    "type": "mcp_tool_call",
    "tool_name": "execute_skill",
    "display_label": "Run recommended skill",
    "risk_level": "low",
    "requires_confirmation": false,
    "arguments": {
      "skill_name": "merge_text_files",
      "args": {}
    }
  }
}
```

For no-strong-match queries, `search_skill` now recommends `capture_trajectory` as the
primary next step and keeps `distill_and_promote_candidate` in
`available_host_operations` as a shorter secondary path when the host already has the
needed artifact.

Successful `execute_skill` responses now do as well:

```json
{
  "skill_name": "merge_text_files",
  "observed_task_record": "/abs/path.json",
  "recommended_next_action": "distill_and_promote_candidate",
  "recommended_reason": "Execution succeeded and emitted an observed task record that can be sent directly into distill_and_promote_candidate.",
  "recommended_host_operation": {
    "type": "mcp_tool_call",
    "tool_name": "distill_and_promote_candidate",
    "display_label": "Promote this execution",
    "risk_level": "medium",
    "requires_confirmation": false,
    "arguments": {
      "observed_task_path": "/abs/path.json"
    }
  }
}
```

That closes the host call chain:

- `search_skill`
- `execute_skill`
- `recommended_host_operation`
- `distill_and_promote_candidate`

Hosts can use the extra fields to drive interaction:

- `display_label` for button or menu text
- `risk_level` for visual emphasis
- `requires_confirmation` for confirmation gating

Host-call lifecycle loop:

- `log_trajectory` recommends `distill_trajectory`
- `capture_trajectory` recommends `distill_trajectory`
- `distill_trajectory` recommends `audit_skill`
- `audit_skill` recommends `promote_skill` when the audit passes
- `promote_skill` recommends `execute_skill`
- `distill_and_promote_candidate` recommends `execute_skill` after a successful promotion

The orchestration short path can now start from either:

- a full trajectory JSON
- a lightweight observed task record that is captured into a trajectory first

Observed task input shapes are documented centrally in
[MCP Integration](./docs/mcp-integration.md#observed-task-input-shapes), including the
verbose, compact, and nested tool-log forms accepted by `capture_trajectory` and
`distill_and_promote_candidate`.

## Codex Integration

This project is already structured to sit under Codex as a local background capability layer.

MCP is still one important transport for that layer, but it is no longer the whole story.

Recommended Codex usage:

1. let Codex decide whether the task belongs to the runtime lane
2. if it does, try quiet reuse conservatively
3. if reuse is weak or unsuitable, complete the task normally
4. after success, capture reusable experience when it is worth keeping
5. use explicit MCP lifecycle tools only when manual control, debugging, or governance is the real goal
6. use the governance maintenance loop after library changes

See:

- [MCP Integration](./docs/mcp-integration.md)
- [Codex Integration](./docs/codex-integration.md)
- [Codex Default Lane Stage Closure](./docs/codex-default-lane-stage-closure.md)
- [Codex Default Lane Observation Plan](./docs/codex-default-lane-observation-plan.md)
- [Agent-First Runtime Architecture](./docs/agent-first-runtime-architecture.md)

## Demo and Verification

Generate the local read-only dashboard:

```bash
python -m skill_runtime.cli dashboard --open
```

Inspect the current local operator summary and the current dashboard export status:

```bash
python -m skill_runtime.cli operator-summary
```

The returned summary now includes per-gate freshness so you can tell whether persisted provider, utility-search, or workflow-search status is still current before refreshing it.

Refresh the persisted local gate-status summaries before returning the operator summary:

```bash
python -m skill_runtime.cli operator-summary --refresh-operator-status
```

Refresh the stable dashboard export without rendering HTML:

```bash
python -m skill_runtime.cli operator-summary --refresh-dashboard-export
```

Refresh the local gate-status summaries and the stable dashboard export together:

```bash
python -m skill_runtime.cli operator-summary --refresh-operator-status --refresh-dashboard-export
```

Refresh the stable operator-summary export before rendering:

```bash
python -m skill_runtime.cli dashboard --refresh-operator-summary --open
```

The dashboard is static local HTML. It reads the current runtime root and shows the skill tree, capability collections, runtime lane trigger log, governance snapshot, and platform inventory as separate views. Capability collections are read-only organization overlays and do not change execution, audit, promotion, or archive semantics.

To inspect runtime lane records across sibling projects:

```bash
python -m skill_runtime.cli dashboard --global --scan-root D:\02-Projects --open
```

To inspect the same runtime lane records as read-only JSON without opening HTML:

```bash
python -m skill_runtime.cli runtime-events --limit 20
python -m skill_runtime.cli runtime-events --global --scan-root D:\02-Projects --limit 20
```

`runtime-events` returns recent events, `used / entered / skipped` counts, and finalizer follow-up fields such as `recommended_next_action` and available operation labels.

The narrow operator visibility path is documented in [docs/operator-visibility-runbook.md](./docs/operator-visibility-runbook.md).

Run the fast local validation suite:

```bash
python -m unittest tests.test_runtime_fast -v
```

Run the current active-skill search quality baseline:

```bash
python scripts/evaluate_search_quality.py
```

Run the included local provider demo path by setting trusted command providers:

```bash
export SKILL_RUNTIME_FALLBACK_PROVIDER_CMD='["python", "examples/providers/copy_metadata_fallback_provider.py"]'
export SKILL_RUNTIME_SEMANTIC_PROVIDER_CMD='["python", "examples/providers/pass_semantic_review_provider.py"]'
```

PowerShell:

```powershell
$env:SKILL_RUNTIME_FALLBACK_PROVIDER_CMD='["python", "examples/providers/copy_metadata_fallback_provider.py"]'
$env:SKILL_RUNTIME_SEMANTIC_PROVIDER_CMD='["python", "examples/providers/pass_semantic_review_provider.py"]'
```

These providers are narrow local examples, not a general LLM backend. They are useful for verifying that the real provider hook can generate, audit, promote, and reuse an executable skill without writing ad-hoc scripts.

Use DeepSeek as the real provider by setting local environment variables:

```bash
export DEEPSEEK_API_KEY="<your-deepseek-api-key>"
export DEEPSEEK_MODEL="deepseek-v4-flash"
export DEEPSEEK_REPAIR_ATTEMPTS="1"
export SKILL_RUNTIME_FALLBACK_PROVIDER_CMD='["python", "examples/providers/deepseek_fallback_provider.py"]'
export SKILL_RUNTIME_SEMANTIC_PROVIDER_CMD='["python", "examples/providers/deepseek_semantic_review_provider.py"]'
```

PowerShell:

```powershell
$env:DEEPSEEK_API_KEY="<your-deepseek-api-key>"
$env:DEEPSEEK_MODEL="deepseek-v4-flash"
$env:DEEPSEEK_REPAIR_ATTEMPTS="1"
$env:SKILL_RUNTIME_FALLBACK_PROVIDER_CMD='["python", "examples/providers/deepseek_fallback_provider.py"]'
$env:SKILL_RUNTIME_SEMANTIC_PROVIDER_CMD='["python", "examples/providers/deepseek_semantic_review_provider.py"]'
```

Do not commit API keys. The fallback provider runs a local quality gate and can ask DeepSeek for one repair pass before failing. DeepSeek provider details live in [Provider Integration](./docs/provider-integration.md#deepseek-providers).

Optional live DeepSeek loop smoke:

```bash
python scripts/smoke_deepseek_provider_loop.py
```

Run the demo flow:

```bash
python scripts/skill_cli.py log-trajectory --file trajectories/demo_merge_text_files.json
python scripts/skill_cli.py distill --trajectory trajectories/demo_merge_text_files.json --skill-name merge_text_files_generated
python scripts/skill_cli.py audit --file skill_store/staging/merge_text_files_generated.py
python scripts/skill_cli.py promote --file skill_store/staging/merge_text_files_generated.py
python scripts/skill_cli.py distill-and-promote --trajectory trajectories/demo_merge_text_files.json --skill-name merge_text_files_one_shot
python scripts/skill_cli.py distill-and-promote --observed-task output/observed_task.json --skill-name merge_text_files_from_observed
python scripts/skill_cli.py search --query "merge txt files into markdown"
python scripts/skill_cli.py execute --skill merge_text_files_generated --args-file demo/execute_args.json
```

## Documentation

- [Open Source Release Readiness Checklist](./docs/open-source-release-readiness-checklist.md)
- [Codex Open Source Application Draft](./docs/codex-open-source-application-draft.md)
- [Project Report](./docs/skill-runtime-project-report.md)
- [MCP Integration](./docs/mcp-integration.md)
- [Codex Integration](./docs/codex-integration.md)
- [Privacy And Provenance](./docs/privacy-and-provenance.md)
- [Multi-Host Adaptation Plan](./docs/multi-host-adaptation-plan.md)
- [Dogfooding Workflow](./docs/dogfooding-workflow.md)
- [Video Script Pack](./docs/skill-runtime-video-cover.md)

## Current Limits

- semantic audit is provider-backed but still uses a mock provider by default
- fallback distillation still uses a mock provider by default
- retrieval is still lightweight and not yet embedding-based
- the current runtime is strongest on local file workflows

## License

This project is licensed under the [MIT License](./LICENSE).

## Status

This project is already usable as a local MVP.

The next meaningful upgrades are likely:

1. real LLM semantic audit
2. lightweight hybrid retrieval
3. longer-term library governance
