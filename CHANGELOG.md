# Changelog

All notable changes to this project should be documented in this file.

## v0.2.0-rc1 - 2026-05-06

### Release Candidate Gates

- Governed maintainer workflow proof bundle is now packaged as the accepted `capture-trajectory --render-recommendation text` path in [`docs/v0.2-maintainer-proof-bundle.md`](./docs/v0.2-maintainer-proof-bundle.md)
- Provider quality is release-gated by `python scripts/evaluate_provider_quality.py --baseline docs/provider-quality-baseline.json --fail-on-regression`
- Utility search quality is release-gated by `python scripts/evaluate_search_quality.py --baseline docs/search-quality-baseline.json --fail-on-regression`
- Workflow search quality is release-gated by `python scripts/evaluate_workflow_search_quality.py --baseline docs/workflow-search-quality-baseline.json --fail-on-regression`

### Presentation And Governance Boundaries

- CLI recommendation presentation is accepted only as the opt-in `capture-trajectory --render-recommendation text` operator path
- Governed follow-up remains explicit; no distill, promote, or apply step runs automatically in the proof path
- No evidence supports widening `default-in`

### Not Included In v0.2 RC

- no auto-promote of generated or distilled skills
- no auto-apply of evolution candidates
- no widening of `default-in`
- no ranking changes to force expected workflow gaps into search passes
- no workflow-query expansion to make `maintainer_review_cleanup` or governed learning follow-up look more complete than current evidence supports

### Verification

- `python scripts/check_mcp_architecture.py`
- `python scripts/check_runtime_contracts.py`
- `python -m unittest tests.test_runtime_fast -v`
- `python scripts/evaluate_provider_quality.py --baseline docs/provider-quality-baseline.json --fail-on-regression`
- `python scripts/evaluate_search_quality.py --baseline docs/search-quality-baseline.json --fail-on-regression`
- `python scripts/evaluate_workflow_search_quality.py --baseline docs/workflow-search-quality-baseline.json --fail-on-regression`
- `python scripts/run_v0_2_proof_bundle.py`

## v0.1.0-alpha - 2026-05-05

### Added

- Local-first `Skill Runtime` release shape spanning runtime service, CLI, and MCP surfaces
- Governed workflow lifecycle for `search -> execute -> capture/distill -> audit -> promote -> reuse`
- Maintainer-facing demo set, with review cleanup as the main public walkthrough
- Architecture and runtime contract verification scripts for release checks
- Early release documentation for public evaluation, including the main demo walkthrough and `v0.1.0-alpha` release plan

### Safety Boundaries

- Review cleanup remains conservative and stays `default-out`
- Maintainer-facing demo outputs are explicit plans and governed follow-up actions, not silent code mutation
- No evidence currently supports widening `default-in`
- Promotion remains governed through capture, distill, audit, and explicit follow-up steps

### Verification

- `python scripts/check_mcp_architecture.py`
- `python scripts/check_runtime_contracts.py`
- `python -m unittest tests.test_runtime_fast -v`
- `git diff --check`

### Known Limitations

- Semantic audit is provider-backed but mock-backed by default
- Fallback distillation is provider-backed but mock-backed by default
- Retrieval is still lightweight
- The runtime is strongest on local file and maintainer workflow patterns
- Public traction is still limited and should not be overstated

### Not Included

- Wider `default-in` entry policy
- Silent automation for open-ended review cleanup
- Dashboard-first product positioning
- Hosted-service guarantees or mature remote-provider claims
