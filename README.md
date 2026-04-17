# Skill Runtime

[中文说明](./README.zh-CN.md)

`Skill Runtime` is a local, host-AI-compatible runtime for turning successful task executions into governed reusable skills.

It is designed as a capability layer under tools like Codex, not as a second chat agent.

## What It Does

The runtime supports a full local loop:

`search -> execute -> distill -> audit -> promote -> reuse`

That means a host AI can:

- search for an existing reusable skill before rebuilding a workflow
- execute active skills through a stable `run(tools, **kwargs)` contract
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
- semantic heuristic checks for:
  - trajectory alignment
  - parameter coverage
  - template-like skills
  - retrieval-oriented docstring structure

### Retrieval

- active-skill indexing through `skill_store/index.json`
- keyword-based ranking
- provenance surfaced in search results:
  - `rule_name`
  - `rule_priority`
  - `rule_reason`
  - `why_matched`

### Governance

- strict staging -> audit -> promote flow
- provenance persistence on promoted skills
- legacy provenance backfill command

## CLI Quick Start

```bash
python scripts/skill_cli.py search --query "<task>"
python scripts/skill_cli.py execute --skill <skill_name> --args-file <json file>
python scripts/skill_cli.py distill --trajectory <trajectory.json> --skill-name <optional_name>
python scripts/skill_cli.py distill-and-promote --trajectory <trajectory.json> --skill-name <optional_name>
python scripts/skill_cli.py audit --file <skill.py>
python scripts/skill_cli.py promote --file <staging_skill.py>
python scripts/skill_cli.py log-trajectory --file <trajectory.json>
python scripts/skill_cli.py reindex
python scripts/skill_cli.py backfill-provenance
```

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
- `reindex_skills`
- `backfill_skill_provenance`

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
python scripts/skill_cli.py search --query "merge txt files into markdown"
python scripts/skill_cli.py execute --skill merge_text_files_generated --args-file demo/execute_args.json
```

## Documentation

- [Project Report](./docs/skill-runtime-project-report.md)
- [MCP Integration](./docs/mcp-integration.md)
- [Codex Integration](./docs/codex-integration.md)
- [Video Script Pack](./docs/skill-runtime-video-cover.md)

## Current Limits

- semantic audit is still heuristic, not a full LLM semantic auditor
- fallback distillation still uses a mock provider by default
- retrieval is still lightweight and not yet hybrid-ranked
- `archive-cold` is still a placeholder
- the current runtime is strongest on local file workflows

## Status

This project is already usable as a local MVP.

The next meaningful upgrades are likely:

1. real LLM semantic audit
2. lightweight hybrid retrieval
3. longer-term library governance
