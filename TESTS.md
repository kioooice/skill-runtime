# Minimal Test Checklist

## CLI

- `search` returns an empty list when the index is empty
- `distill` rejects invalid trajectory files
- `audit` rejects missing skill files
- `promote` rejects skills without a passing audit
- `execute` rejects missing skills
- `execute` accepts `--args-file` for shell-safe invocation

## Trajectory

- valid trajectories can be saved and loaded
- invalid trajectories are rejected

## Audit

- detects `shell=True`
- detects `os.system`
- detects hardcoded absolute paths
- detects missing docstrings

## Promotion

- blocks missing audit reports
- blocks `needs_fix`
- accepts `passed`

## Retrieval

- `reindex` rebuilds `skill_store/index.json`
- `search` returns `score` and `why_matched`

## MCP Contract Architecture

- `skill_runtime/mcp/source_refs.py` does not import other `skill_runtime.mcp` modules
- `operation_builders.py` only depends on `source_refs.py`
- `recommendation_builders.py` only depends on `operation_builders.py` and `source_refs.py`
- `governance_actions.py` only depends on `operation_builders.py` and `source_refs.py`
- internal MCP split modules explicitly declare literal `__all__` export lists
- `host_operations.py` remains the compatibility export surface
- `host_operations.py` stays a pure re-export facade with no implementation logic
- `host_operations.__all__` matches the combined public exports from the internal MCP modules
- `docs/mcp-integration.md` stays aligned with the current MCP module layout and maintenance command
- `docs/codex-integration.md` stays aligned with the Codex-facing MCP contract surface
- `README.md` and `README.zh-CN.md` stay aligned with the runtime contract guard entry points
- `.github/workflows/runtime-contracts.yml` stays aligned with the runtime contract checks and doc coverage
- modules outside `skill_runtime/mcp/` do not import internal MCP submodules directly; they use `skill_runtime.mcp.host_operations` or `skill_runtime.mcp.server`
- `python scripts/check_mcp_architecture.py` passes as a standalone architecture check
- `python scripts/check_runtime_contracts.py` passes as a standalone payload contract check
- `.github/workflows/runtime-contracts.yml` runs both the architecture check and `tests.test_runtime`

## Runtime Layer Architecture

- `skill_runtime/api/service.py` remains the orchestration layer and only depends on the current runtime service collaborators
- `skill_runtime/governance/library_report.py` depends only on models, retrieval, and MCP host-operation builders
- `promotion_guard.py` depends only on API models
- `provenance_backfill.py` depends only on API models and retrieval
- `skill_runtime/retrieval/skill_index.py` depends only on API models and MCP host-operation builders
- `skill_runtime/memory/trajectory_capture.py` and `trajectory_store.py` depend only on API models
- `skill_runtime/distill/skill_generator.py` depends only on models plus distill rule/fallback layers
- `skill_runtime/audit/skill_auditor.py` depends only on models plus audit semantic/static review layers
- `skill_runtime/execution/skill_executor.py` depends only on the loader and retrieval index
- `skill_loader.py` and `runtime_tools.py` stay free of internal `skill_runtime` imports
- `distill/fallback` stays split between provider contracts, prompt building, mock provider behavior, and fallback orchestration
- `distill/rules` modules stay on the rule-local layer: rule files depend only on models plus `rules.common`
- `audit` sublayers stay split between semantic/static checks, provider contracts, provider mocks, prompt building, and orchestration

## Execution

- active skills with `run` execute successfully
- active skills without `run` fail cleanly
- non-dict results are wrapped as `raw_result`

## End-to-End

- `log-trajectory -> distill -> audit -> promote -> search -> execute` runs successfully
