# Codex-Compatible Self-Evolving Skill Runtime

This workspace now contains a local MVP for a Codex-compatible self-evolving skill runtime.

The runtime supports:

- storing task trajectories
- distilling successful trajectories into staging skills
- auditing generated skills with static safety checks plus a semantic review layer
- promoting only audited skills into the active store
- indexing active skills for retrieval
- executing active skills through a stable `run(tools, **kwargs)` interface
- exposing the runtime through both CLI and MCP tool adapters

## Layout

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
```

## CLI Commands

```bash
python scripts/skill_cli.py search --query "<task>"
python scripts/skill_cli.py execute --skill <skill_name> --args-file <json file>
python scripts/skill_cli.py distill --trajectory <trajectory.json> --skill-name <optional_name>
python scripts/skill_cli.py distill-and-promote --trajectory <trajectory.json> --skill-name <optional_name>
python scripts/skill_cli.py audit --file <skill.py>
python scripts/skill_cli.py promote --file <staging_skill.py>
python scripts/skill_cli.py log-trajectory --file <trajectory.json>
python scripts/skill_cli.py reindex
python scripts/skill_cli.py archive-cold --days 30
python scripts/skill_cli.py backfill-provenance
```

## MCP Adapter

The runtime now also exposes a local MCP server over stdio:

```bash
python scripts/skill_mcp_server.py
```

You can also launch it from anywhere by passing the runtime root explicitly:

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

The MCP adapter reuses the same runtime service layer as the CLI, so both interfaces share:

- the same result schema
- the same skill store and audit rules
- the same promotion guard and provenance behavior

Search responses now also include:

- `recommended_next_action`
- `recommended_skill_name`

So host AIs can more easily choose between:

- `execute_skill` when a strong reusable match exists
- `distill_and_promote_candidate` when no relevant reusable skill was found

See `docs/mcp-integration.md` for host wiring guidance and copyable stdio config examples.
See `docs/codex-integration.md` for the Codex-specific setup used in this machine.

## Audit Model

The audit pipeline now combines two layers:

1. static checks for dangerous commands, shell invocation, missing entrypoints, and hardcoded paths
2. semantic checks for trajectory alignment, parameter coverage, template-like skills, and retrieval-oriented docstring structure

Audit reports now include:

- `static_score`
- `semantic_score`
- `static_findings`
- `semantic_findings`
- `semantic_summary`

## Codex Meta-Skill Bridge

The following global Codex skills are installed under `C:/Users/Administrator/.codex/skills/`:

- `skill-search`
- `skill-execute`
- `skill-distill`
- `skill-audit`
- `skill-promote`

They now read the runtime location from:

`C:/Users/Administrator/.codex/skill-runtime.json`

Current config:

```json
{
  "runtime_root": "D:/02-Projects/vibe"
}
```

To repoint the Codex bridge to another runtime project, only update `runtime_root` in that file. The wrapper scripts do not need to change.

## Current Distillation Behavior

The generator currently supports two levels:

1. rule-based executable generation for known local automation patterns
2. fallback provider generation for unmatched successful trajectories

The current executable rule registry includes:

- text merge
- text replace
- single-file transform
- batch rename
- directory copy
- directory move
- directory-wide text replace
- CSV to JSON
- JSON to CSV

Generated metadata also persists:

- `rule_name`
- `rule_priority`
- `rule_reason`

Those provenance fields are preserved through promotion and surfaced by retrieval.

When no deterministic rule matches, the runtime now:

1. builds a fallback prompt artifact
2. sends it through a provider abstraction
3. writes the generated candidate code to staging

The current provider is a local mock provider that keeps the fallback path testable without external model dependencies.

For legacy active skills created before provenance support, run:

```bash
python scripts/skill_cli.py backfill-provenance
```

That command scans existing active skills and fills in rule provenance where it can be inferred safely from source or metadata.

## Verification

Run the focused test suite:

```bash
python -m unittest tests.test_runtime -v
```

Run the manual demo flow:

```bash
python scripts/skill_cli.py log-trajectory --file trajectories/demo_merge_text_files.json
python scripts/skill_cli.py distill --trajectory trajectories/demo_merge_text_files.json --skill-name merge_text_files_generated
python scripts/skill_cli.py audit --file skill_store/staging/merge_text_files_generated.py
python scripts/skill_cli.py promote --file skill_store/staging/merge_text_files_generated.py
python scripts/skill_cli.py distill-and-promote --trajectory trajectories/demo_merge_text_files.json --skill-name merge_text_files_one_shot
python scripts/skill_cli.py search --query "merge txt files into markdown"
python scripts/skill_cli.py execute --skill merge_text_files_generated --args-file demo/execute_args.json
```

## Current Limits

- semantic audit is heuristic and trajectory-aware, but it is not yet backed by a real LLM semantic reviewer
- unmatched trajectories still fall back to a generic template skill
- `archive-cold` is still a placeholder
- there is no browser or GUI tool integration yet
- global meta-skills are installed, and the runtime now exposes a combined orchestration path through CLI and MCP
