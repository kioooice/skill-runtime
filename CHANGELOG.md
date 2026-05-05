# Changelog

All notable changes to this project should be documented in this file.

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
