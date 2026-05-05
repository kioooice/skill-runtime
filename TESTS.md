# Minimal Test Checklist

## Runtime Test Tiers

- Fast local validation: `python -m unittest tests.test_runtime_fast -v`
- Runtime contract checks:
  - `python scripts/check_mcp_architecture.py`
  - `python scripts/check_runtime_contracts.py`
- Full slow runtime suite: `python -m unittest tests.test_runtime -v`
- Slow-test profiling: `python scripts/profile_runtime_tests.py --suite tests.test_runtime --top 20`

Use the fast suite for routine development feedback. Use the two contract scripts when touching runtime/MCP boundaries, recommendation payloads, docs that claim contract shape, or orchestration layering. Use the full suite before release-level changes or when broad runtime behavior may be affected.

## Current Suite Status

- Fast suite test count: `146`
- Full suite test count: `493`
- Last verified fast command: `python -m unittest tests.test_runtime_fast -v`
- Last verified contract commands:
  - `python scripts/check_mcp_architecture.py`
  - `python scripts/check_runtime_contracts.py`
- Last known full-suite description: the suite remains the broad regression gate and is materially slower than the fast suite; do not use it as the default loop for small changes.

## Recent Validation Commands

Most recent recommendation-dogfood validation pass:

```text
python scripts/check_mcp_architecture.py
python scripts/check_runtime_contracts.py
python -m unittest tests.test_runtime_fast -v
```

## Fast Suite Coverage Highlights

- Codex task classification boundaries:
  - `default-in`
  - `guarded-in`
  - `default-out`
- Silent reuse boundaries:
  - complete strong match -> `auto_execute`
  - missing required inputs -> `background_hint`
  - scope mismatch -> `background_hint`
  - expected-output mismatch -> `background_hint`
- Learning decision boundaries:
  - clean existing-skill reuse -> `skip`
  - weak existing-skill gap -> `observed_only`
  - concrete new workflow output -> `new_skill_candidate`
  - explicit existing-skill gap -> `improve_existing_skill_candidate`
- Recommendation contract propagation:
  - `background_hint -> execute_skill`
  - `new_skill_candidate -> distill_trajectory`
  - `improve_existing_skill_candidate -> review_evolution_candidate`
- Evolution lifecycle:
  - `candidate -> review -> apply -> rollback`
  - byte-preserving rollback for BOM-backed skill files
- Dashboard regression coverage for:
  - trigger log balancing
  - evolution lifecycle detail panel
  - governance snapshot wording
  - grouped workflow library views

## Contract Architecture Expectations

- `build_mcp_server` can be imported and construct a server without starting a stdio loop
- `skill_runtime/mcp/source_refs.py` does not import other `skill_runtime.mcp` modules
- `operation_builders.py` only depends on `source_refs.py`
- `recommendation_builders.py` only depends on `operation_builders.py` and `source_refs.py`
- `governance_actions.py` only depends on `operation_builders.py` and `source_refs.py`
- modules outside `skill_runtime/mcp/` import MCP helpers through `skill_runtime.mcp.host_operations` or `skill_runtime.mcp.server`
- `host_operations.py` remains the compatibility export surface
- `host_operations.py` stays a pure re-export facade with no implementation logic
- `host_operations.__all__` matches the combined public exports from the internal MCP modules
- `README.md`, `README.zh-CN.md`, and runtime contract docs stay aligned with the current contract entry points

## Execution / Lifecycle Expectations

- active skills with `run` execute successfully
- active skills without `run` fail cleanly
- non-dict results are wrapped as `raw_result`
- `copy_file` rollback deletes a newly created copied target
- `copy_file` overwrite rollback remains `manual_restore_required` and is not auto-applied
- `log-trajectory -> distill -> audit -> promote -> search -> execute` runs successfully

## DeepSeek / Provider Notes

- Fast suite provider dogfood uses the repository demo providers under `examples/providers/`, not ad-hoc generated scripts
- Fast suite DeepSeek provider checks use a local fake DeepSeek API server, not a real network call
- DeepSeek live smoke with the real API is not part of the automated suite
- Manual live DeepSeek loop smoke remains:
  - `python scripts/smoke_deepseek_provider_loop.py`
  - requires `DEEPSEEK_API_KEY`
  - uses a temporary sandbox
  - verifies generate -> audit -> promote -> execute
