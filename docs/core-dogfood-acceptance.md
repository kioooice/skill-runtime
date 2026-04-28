# Core Dogfood Acceptance

Date: 2026-04-28

## Purpose

This acceptance pack proves the current Skill Runtime core loop from the host user's point of view.

It is not a new product feature. It is a verification layer for the existing core.

## Covered Loop

The first acceptance path covers:

1. Search for an existing useful skill through MCP.
2. Execute the recommended skill through MCP.
3. Confirm the execution writes a real output file.
4. Confirm the execution emits an observed task record.
5. Promote the observed execution into a new active skill through MCP.
6. Confirm the candidate passes audit through the existing deterministic rule path.
7. Reuse the newly promoted skill through MCP.
8. Confirm active search is not polluted by fixture-tier skills.
9. Confirm governance still reports no active fixture skills.

The second acceptance path covers:

1. Submit an unknown workflow through MCP.
2. Confirm no deterministic rule matches and fallback distillation is used.
3. Confirm the candidate is marked as `llm_fallback`.
4. Confirm the default mock semantic review flags the candidate as template or fallback risk.
5. Confirm the audit does not pass.
6. Confirm the candidate is not promoted into the active library.
7. Confirm no follow-up execution operation is recommended for the blocked candidate.

## Current Acceptance Test

- `tests/test_runtime_core_dogfood_acceptance.py`
- Test name: `test_mcp_host_style_loop_search_execute_promote_and_reuse`
- Test name: `test_mcp_fallback_generated_candidate_is_not_auto_promoted`

## What This Proves

- The core loop can run as one connected host-style workflow.
- MCP tool payloads are usable beyond a basic smoke construction test.
- A real active skill can produce a reusable observed task.
- A promoted skill can be executed again.
- The active library can stay free of fixture-tier pollution during this path.
- Unknown workflows that fall back to the default mock provider are not automatically promoted.

## What This Does Not Yet Prove

- Real semantic audit quality, because the default provider is still mock-backed.
- Real unknown-workflow skill generation, because fallback distillation is still mock-backed and currently blocked from promotion.
- Search quality across many real skills, because the active library is still small.
- Long-term governance quality under a larger active library.

## Next Recommended Acceptance Work

The fallback safety path is now covered. The next core investment should be a deliberate provider decision:

- connect a real semantic audit / fallback provider path, or
- keep fallback candidates blocked unless an explicit trusted provider is configured.
