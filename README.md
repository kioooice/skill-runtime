# Skill Runtime

[中文说明](./README.zh-CN.md)

`Skill Runtime` is a local, host-AI-compatible runtime for turning successful task executions into governed reusable skills.

It is designed as a capability layer under tools like Codex, not as a second chat agent.

## What It Does

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

## Why This Project Exists

Most AI systems can complete tasks, but they often fail to build a governed layer of reusable workflows.

Typical failure modes are:

- repetitive tasks get solved from scratch every time
- successful workflows remain trapped in chat history
- generated skills are stored without audit or lifecycle rules
- the “skill system” becomes a black box with weak explainability

This project focuses on a different goal:

- not just accumulating skills
- but governing skills

## Core Properties

- `Host-first`: the host AI keeps planning, task understanding, and user interaction
- `Governed`: new skills pass through staging, audit, and promotion before becoming active
- `Explainable`: search results can expose match reasons, rule provenance, and recommended next action
- `Extensible`: the same runtime is exposed through CLI and MCP
- `Local-first`: storage is file-based and easy to inspect

## Current Architecture

```text
Host AI
-> CLI / MCP adapter
-> Runtime service
-> skill store / trajectories / audits
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

## CLI Quick Start

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
- `archive_duplicate_candidates`

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

The explicit lifecycle path now exposes the same contract:

- `log_trajectory` recommends `distill_trajectory`
- `capture_trajectory` recommends `distill_trajectory`
- `distill_trajectory` recommends `audit_skill`
- `audit_skill` recommends `promote_skill` when the audit passes
- `promote_skill` recommends `execute_skill`
- `distill_and_promote_candidate` recommends `execute_skill` after a successful promotion

The orchestration short path can now start from either:

- a full trajectory JSON
- a lightweight observed task record that is captured into a trajectory first

Observed task records can now use either the verbose shape:

- `task_description`
- `steps[].tool_name`
- `steps[].tool_input`
- `steps[].observation`

or a compact host-friendly shape:

- `task`
- `actions[].tool` or `actions[].action`
- `actions[].input` or `actions[].args`
- `actions[].result` or `actions[].output`

It also accepts nested tool-call log shapes such as:

- `records[].tool.name`
- `records[].tool.arguments`
- `records[].result.message` or `records[].result.output`
- `records[].result.success` or `records[].result.status`

## Codex Integration

This project is already structured to sit under Codex as a local MCP-backed capability layer.

Recommended Codex usage:

1. `search_skill`
2. if a strong match exists, `execute_skill`
3. if no strong match exists, complete the task normally
4. use `distill_and_promote_candidate` for the short path back into the library

See:

- [MCP Integration](./docs/mcp-integration.md)
- [Codex Integration](./docs/codex-integration.md)

## Demo and Verification

Run the focused test suite:

```bash
python -m unittest tests.test_runtime -v
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

- [Project Report](./docs/skill-runtime-project-report.md)
- [MCP Integration](./docs/mcp-integration.md)
- [Codex Integration](./docs/codex-integration.md)
- [Dogfooding Workflow](./docs/dogfooding-workflow.md)
- [Video Script Pack](./docs/skill-runtime-video-cover.md)

## Current Limits

- semantic audit is provider-backed but still uses a mock provider by default
- fallback distillation still uses a mock provider by default
- retrieval is still lightweight and not yet embedding-based
- the current runtime is strongest on local file workflows

## Status

This project is already usable as a local MVP.

The next meaningful upgrades are likely:

1. real LLM semantic audit
2. lightweight hybrid retrieval
3. longer-term library governance
