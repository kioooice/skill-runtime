# Host Call Alignment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Unify `recommended_actions`, search recommendations, and follow-up runtime responses around one host-call contract so an MCP host can move directly from "show recommendation" to "preview", "execute", and "continue workflow" without inventing arguments or re-mapping action names.

**Architecture:** Introduce one shared host-operation builder module and make every host-facing recommendation surface emit the same envelope: `type`, `tool_name`, `arguments`, and optional `preview` or `next_step` metadata. Keep business logic in existing service/retrieval/governance modules, but move host-call shape generation into a single utility so search, governance, and later execute/distill flows stay aligned. Verification stays test-first and focused on response shape, not implementation detail.

**Tech Stack:** Python 3, stdlib dataclasses/typing/json, existing `RuntimeService`, `SkillIndex`, `LibraryReport`, FastMCP server, `unittest`

---

## File Map

**Create:**
- `D:/02-Projects/vibe/skill_runtime/mcp/host_operations.py` - shared builder helpers for host-call payloads
- `D:/02-Projects/vibe/docs/superpowers/plans/2026-04-24-host-call-alignment.md` - this plan

**Modify:**
- `D:/02-Projects/vibe/skill_runtime/api/models.py` - optional typed dataclasses / aliases for host operation payloads if type centralization is useful
- `D:/02-Projects/vibe/skill_runtime/api/service.py` - top-level recommendation and post-execution next-step payloads
- `D:/02-Projects\vibe/skill_runtime/retrieval/skill_index.py` - per-result search host operation generation
- `D:/02-Projects/vibe/skill_runtime/governance/library_report.py` - recommended action and preview/apply host operations
- `D:/02-Projects/vibe/skill_runtime/mcp/server.py` - only if tool descriptions need tightening to reflect new host-call contract
- `D:/02-Projects/vibe/tests/test_runtime.py` - regression coverage for search/governance/execute follow-up shapes
- `D:/02-Projects/vibe/README.md` - public contract documentation
- `D:/02-Projects/vibe/README.zh-CN.md` - Chinese contract documentation
- `D:/02-Projects/vibe/docs/mcp-integration.md` - host-wiring guidance
- `D:/02-Projects/vibe/docs/codex-integration.md` - Codex-specific guidance

**Do not modify unless needed by tests:**
- `D:/02-Projects/vibe/scripts/skill_cli.py`
- `D:/02-Projects/vibe/scripts/skill_mcp_server.py`

## Target End State

By the end of this plan, the host should be able to rely on one contract:

1. `search_skill` returns:
   - `results[].host_operation`
   - `recommended_host_operation`
2. `governance_report` returns:
   - `recommended_actions[].host_operation`
   - optional `preview`
3. `execute_skill` returns:
   - `observed_task_record`
   - follow-up host-call hints for the next likely step, such as capture/distill
4. The builder for these payloads lives in one place.
5. Docs explain when the host should use:
   - direct action execution
   - preview/dry-run
   - next-step chaining after successful execution

## Non-Goals

- No App Server migration in this round
- No embedding retrieval work
- No semantic-audit provider swap
- No broad refactor of CLI payloads beyond what is needed to keep MCP and CLI shape consistent
- No automated host UI; only backend/runtime-facing contract work

## Design Decisions

### 1. Shared payload envelope

Use one stable shape everywhere:

```json
{
  "type": "mcp_tool_call",
  "tool_name": "execute_skill",
  "arguments": {
    "skill_name": "merge_text_files",
    "args": {}
  }
}
```

Optional extensions:

```json
{
  "preview": {
    "tool_name": "archive_duplicate_candidates",
    "arguments": {
      "skill_names": ["merge_text_files_generated"],
      "dry_run": true
    }
  },
  "next_step": {
    "tool_name": "distill_and_promote_candidate",
    "arguments": {
      "observed_task_path": "/abs/path.json"
    }
  }
}
```

### 2. Builder location

Put host-call builders in `skill_runtime/mcp/host_operations.py`, not in `api/service.py` or `governance/library_report.py`. Reason:

- this is an MCP-host-facing concern, not business logic
- both retrieval and governance need it
- future `execute` follow-up actions also need it
- it reduces drift across modules

### 3. Follow-up chaining after execution

Execution currently returns an observed record path. The missing piece is a direct next-step contract. Add:

```json
{
  "recommended_next_action": "distill_and_promote_candidate",
  "recommended_host_operation": {
    "type": "mcp_tool_call",
    "tool_name": "distill_and_promote_candidate",
    "arguments": {
      "observed_task_path": "/abs/path/to/record.json"
    }
  }
}
```

This is the most valuable next alignment step because it closes the loop from:

`search -> execute -> observe -> distill`

without host-side argument synthesis.

### 4. Keep response duplication intentional

Top-level recommendation and per-item recommendation should both exist even if redundant. Reason:

- hosts often render list rows and top recommendation separately
- keeping both prevents hosts from deriving top-level action from ranking themselves
- the payload size is small enough that duplication is acceptable

## Implementation Tasks

### Task 1: Add failing tests for shared host-call alignment target

**Files:**
- Modify: `D:/02-Projects/vibe/tests/test_runtime.py`

- [ ] **Step 1: Write the failing test for execute follow-up recommendation**

Add a test near the existing execute-path tests:

```python
    def test_service_execute_returns_follow_up_host_operation(self) -> None:
        result = self.service.execute(
            "merge_text_files",
            {"input_dir": "demo/input", "output_path": "demo/output/test_merged.md"},
        )
        self.assertEqual("distill_and_promote_candidate", result["recommended_next_action"])
        self.assertEqual("mcp_tool_call", result["recommended_host_operation"]["type"])
        self.assertEqual(
            "distill_and_promote_candidate",
            result["recommended_host_operation"]["tool_name"],
        )
        self.assertEqual(
            result["observed_task_record"],
            result["recommended_host_operation"]["arguments"]["observed_task_path"],
        )
```

- [ ] **Step 2: Write the failing test for MCP execute output**

```python
    def test_mcp_execute_tool_returns_follow_up_host_operation(self) -> None:
        server = build_mcp_server(ROOT)
        _, payload = asyncio.run(
            server.call_tool(
                "execute_skill",
                {
                    "skill_name": "merge_text_files",
                    "args": {
                        "input_dir": "demo/input",
                        "output_path": "demo/output/test_merged.md",
                    },
                },
            )
        )
        self.assertEqual("ok", payload["status"])
        self.assertEqual(
            "distill_and_promote_candidate",
            payload["data"]["recommended_host_operation"]["tool_name"],
        )
```

- [ ] **Step 3: Write the failing test for builder consistency across search and governance**

```python
    def test_search_and_governance_host_operations_share_same_type(self) -> None:
        search_payload = self.service.search("merge txt files into markdown", top_k=3)
        governance_payload = self.service.governance_report()
        archive_action = next(
            item for item in governance_payload["recommended_actions"]
            if item["action"] == "archive_duplicate_candidates"
        )
        self.assertEqual("mcp_tool_call", search_payload["recommended_host_operation"]["type"])
        self.assertEqual("mcp_tool_call", archive_action["host_operation"]["type"])
```

- [ ] **Step 4: Run tests to verify they fail**

Run:

```bash
python -m unittest tests.test_runtime.RuntimeTests.test_service_execute_returns_follow_up_host_operation tests.test_runtime.RuntimeTests.test_mcp_execute_tool_returns_follow_up_host_operation tests.test_runtime.RuntimeTests.test_search_and_governance_host_operations_share_same_type -v
```

Expected:
- FAIL with missing `recommended_next_action` or `recommended_host_operation` in execute responses
- possibly PASS on the consistency test if current types already match; that is acceptable

- [ ] **Step 5: Commit**

```bash
git add tests/test_runtime.py
git commit -m "test: add failing host-call alignment coverage"
```

### Task 2: Introduce shared host-operation builders

**Files:**
- Create: `D:/02-Projects/vibe/skill_runtime/mcp/host_operations.py`
- Modify: `D:/02-Projects/vibe/skill_runtime/api/models.py`

- [ ] **Step 1: Write the failing import test**

Add to `tests/test_runtime.py`:

```python
    def test_host_operations_builder_module_exports_tool_call_helpers(self) -> None:
        from skill_runtime.mcp.host_operations import tool_call, tool_call_with_preview

        payload = tool_call("execute_skill", {"skill_name": "merge_text_files", "args": {}})
        preview = tool_call_with_preview(
            "archive_duplicate_candidates",
            {"skill_names": ["merge_text_files_generated"], "dry_run": False},
            {"skill_names": ["merge_text_files_generated"], "dry_run": True},
        )
        self.assertEqual("mcp_tool_call", payload["type"])
        self.assertEqual("archive_duplicate_candidates", preview["tool_name"])
        self.assertTrue(preview["preview"]["arguments"]["dry_run"])
```

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
python -m unittest tests.test_runtime.RuntimeTests.test_host_operations_builder_module_exports_tool_call_helpers -v
```

Expected:
- FAIL with `ModuleNotFoundError` or missing helper name

- [ ] **Step 3: Write minimal builder implementation**

Create `skill_runtime/mcp/host_operations.py`:

```python
from typing import Any


def tool_call(tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "mcp_tool_call",
        "tool_name": tool_name,
        "arguments": arguments,
    }


def tool_call_with_preview(
    tool_name: str,
    arguments: dict[str, Any],
    preview_arguments: dict[str, Any],
) -> dict[str, Any]:
    payload = tool_call(tool_name, arguments)
    payload["preview"] = {
        "tool_name": tool_name,
        "arguments": preview_arguments,
    }
    return payload
```

Optionally add a typed alias in `api/models.py`:

```python
HostOperation = dict[str, Any]
```

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
python -m unittest tests.test_runtime.RuntimeTests.test_host_operations_builder_module_exports_tool_call_helpers -v
```

Expected:
- PASS

- [ ] **Step 5: Commit**

```bash
git add skill_runtime/mcp/host_operations.py skill_runtime/api/models.py tests/test_runtime.py
git commit -m "refactor: add shared host operation builders"
```

### Task 3: Migrate search and governance to the shared builder

**Files:**
- Modify: `D:/02-Projects/vibe/skill_runtime/retrieval/skill_index.py`
- Modify: `D:/02-Projects/vibe/skill_runtime/governance/library_report.py`
- Modify: `D:/02-Projects/vibe/tests/test_runtime.py`

- [ ] **Step 1: Write the failing regression for direct builder usage**

Add assertions that payloads still exist after refactor:

```python
    def test_search_result_host_operation_uses_execute_skill_contract(self) -> None:
        result = self.index.search("merge txt files into markdown", top_k=1)[0]
        self.assertEqual("execute_skill", result["host_operation"]["tool_name"])
        self.assertEqual(result["skill_name"], result["host_operation"]["arguments"]["skill_name"])

    def test_governance_action_preview_uses_archive_duplicate_candidates_contract(self) -> None:
        report = self.service.governance_report()
        action = next(
            item for item in report["recommended_actions"]
            if item["action"] == "archive_duplicate_candidates"
        )
        self.assertEqual("archive_duplicate_candidates", action["host_operation"]["tool_name"])
        self.assertTrue(action["host_operation"]["preview"]["arguments"]["dry_run"])
```

- [ ] **Step 2: Run tests to verify baseline behavior before refactor**

Run:

```bash
python -m unittest tests.test_runtime.RuntimeTests.test_search_result_host_operation_uses_execute_skill_contract tests.test_runtime.RuntimeTests.test_governance_action_preview_uses_archive_duplicate_candidates_contract -v
```

Expected:
- PASS if current behavior is intact

- [ ] **Step 3: Replace local helper logic with shared builder imports**

Update `skill_runtime/retrieval/skill_index.py`:

```python
from skill_runtime.mcp.host_operations import tool_call
```

and replace inline payload creation with:

```python
"host_operation": tool_call(
    "execute_skill",
    {"skill_name": skill.skill_name, "args": {}},
),
```

Update `skill_runtime/governance/library_report.py`:

```python
from skill_runtime.mcp.host_operations import tool_call, tool_call_with_preview
```

and replace custom helper method usage with:

```python
"host_operation": tool_call_with_preview(
    "archive_duplicate_candidates",
    {"skill_names": archive_candidates, "dry_run": False},
    {"skill_names": archive_candidates, "dry_run": True},
),
```

For non-preview governance actions:

```python
"host_operation": tool_call("governance_report", {}),
```

- [ ] **Step 4: Run tests to verify they still pass**

Run:

```bash
python -m unittest tests.test_runtime.RuntimeTests.test_search_result_host_operation_uses_execute_skill_contract tests.test_runtime.RuntimeTests.test_governance_action_preview_uses_archive_duplicate_candidates_contract tests.test_runtime.RuntimeTests.test_search_returns_active_skill tests.test_runtime.RuntimeTests.test_governance_report_surfaces_duplicate_candidates -v
```

Expected:
- PASS

- [ ] **Step 5: Commit**

```bash
git add skill_runtime/retrieval/skill_index.py skill_runtime/governance/library_report.py tests/test_runtime.py
git commit -m "refactor: route search and governance through shared host operation builders"
```

### Task 4: Add execute follow-up host call chaining

**Files:**
- Modify: `D:/02-Projects/vibe/skill_runtime/api/service.py`
- Modify: `D:/02-Projects/vibe/tests/test_runtime.py`

- [ ] **Step 1: Re-run the execute follow-up tests**

Run:

```bash
python -m unittest tests.test_runtime.RuntimeTests.test_service_execute_returns_follow_up_host_operation tests.test_runtime.RuntimeTests.test_mcp_execute_tool_returns_follow_up_host_operation -v
```

Expected:
- FAIL because execute response still lacks follow-up recommendation

- [ ] **Step 2: Write minimal implementation**

Update the execute response shape in `skill_runtime/api/service.py`:

```python
        return {
            "skill_name": skill_name,
            "result": result,
            "observed_task_record": str(observed_record.resolve()),
            "recommended_next_action": "distill_and_promote_candidate",
            "recommended_host_operation": tool_call(
                "distill_and_promote_candidate",
                {"observed_task_path": str(observed_record.resolve())},
            ),
        }
```

If using the shared builder:

```python
from skill_runtime.mcp.host_operations import tool_call
```

- [ ] **Step 3: Add a follow-up reason string**

Extend the same response:

```python
            "recommended_reason": (
                "Execution succeeded and emitted an observed task record that can be sent "
                "directly into distill_and_promote_candidate."
            ),
```

This is not required for host execution but helps hosts display the next step cleanly.

- [ ] **Step 4: Run tests to verify they pass**

Run:

```bash
python -m unittest tests.test_runtime.RuntimeTests.test_service_execute_returns_follow_up_host_operation tests.test_runtime.RuntimeTests.test_mcp_execute_tool_returns_follow_up_host_operation -v
```

Expected:
- PASS

- [ ] **Step 5: Commit**

```bash
git add skill_runtime/api/service.py tests/test_runtime.py
git commit -m "feat: add execute follow-up host operation recommendations"
```

### Task 5: Align top-level search recommendations with the shared builder

**Files:**
- Modify: `D:/02-Projects/vibe/skill_runtime/api/service.py`
- Modify: `D:/02-Projects/vibe/tests/test_runtime.py`

- [ ] **Step 1: Add a focused test for top-level search recommendation path**

```python
    def test_search_top_level_recommendation_uses_shared_tool_call_shape(self) -> None:
        payload = self.service.search("merge txt files into markdown", top_k=3)
        self.assertEqual("mcp_tool_call", payload["recommended_host_operation"]["type"])
        self.assertEqual("execute_skill", payload["recommended_host_operation"]["tool_name"])

        fallback = self.service.search("nonexistent workflow phrase for zero matches", top_k=3)
        self.assertEqual(
            "distill_and_promote_candidate",
            fallback["recommended_host_operation"]["tool_name"],
        )
```

- [ ] **Step 2: Run test to verify baseline**

Run:

```bash
python -m unittest tests.test_runtime.RuntimeTests.test_search_top_level_recommendation_uses_shared_tool_call_shape -v
```

Expected:
- PASS if Task 3 and Task 4 are complete

- [ ] **Step 3: Remove any remaining duplicate `_mcp_tool_call` helper from `api/service.py`**

Replace:

```python
    def _mcp_tool_call(...):
        ...
```

with shared imports and direct builder calls.

- [ ] **Step 4: Run search regression tests**

Run:

```bash
python -m unittest tests.test_runtime.RuntimeTests.test_search_returns_active_skill tests.test_runtime.RuntimeTests.test_service_search_matches_cli_shape tests.test_runtime.RuntimeTests.test_mcp_search_tool_returns_structured_payload tests.test_runtime.RuntimeTests.test_service_search_without_matches_recommends_distill_and_promote tests.test_runtime.RuntimeTests.test_search_top_level_recommendation_uses_shared_tool_call_shape -v
```

Expected:
- PASS

- [ ] **Step 5: Commit**

```bash
git add skill_runtime/api/service.py tests/test_runtime.py
git commit -m "refactor: unify top-level search recommendations with shared host operation builder"
```

### Task 6: Tighten docs around the closed host flow

**Files:**
- Modify: `D:/02-Projects/vibe/README.md`
- Modify: `D:/02-Projects/vibe/README.zh-CN.md`
- Modify: `D:/02-Projects/vibe/docs/mcp-integration.md`
- Modify: `D:/02-Projects/vibe/docs/codex-integration.md`

- [ ] **Step 1: Add failing doc checklist in notes or self-review**

Before editing, confirm the docs answer these questions:

```text
1. How does a host execute a matched search result?
2. How does a host follow the top recommended search action?
3. How does a host preview a governance action?
4. How does a host continue from execute -> distill using the returned observed record?
```

Expected:
- At least question 4 is not fully documented yet

- [ ] **Step 2: Update README examples**

Add a minimal execution follow-up example:

```json
{
  "skill_name": "merge_text_files",
  "observed_task_record": "/abs/path.json",
  "recommended_next_action": "distill_and_promote_candidate",
  "recommended_host_operation": {
    "type": "mcp_tool_call",
    "tool_name": "distill_and_promote_candidate",
    "arguments": {
      "observed_task_path": "/abs/path.json"
    }
  }
}
```

- [ ] **Step 3: Update integration docs**

In `docs/mcp-integration.md`, add a closed-loop section:

```text
search_skill -> execute_skill -> recommended_host_operation -> distill_and_promote_candidate
```

In `docs/codex-integration.md`, add host responsibilities:

```text
- treat recommended_host_operation as executable
- treat preview as optional preflight
- do not synthesize observed_task_path if runtime already returned it
```

- [ ] **Step 4: Review docs for consistency**

Check:

```bash
Select-String -Path README.md,README.zh-CN.md,docs\\mcp-integration.md,docs\\codex-integration.md -Pattern "recommended_host_operation|observed_task_record|preview|distill_and_promote_candidate"
```

Expected:
- all four docs mention the new flow

- [ ] **Step 5: Commit**

```bash
git add README.md README.zh-CN.md docs/mcp-integration.md docs/codex-integration.md
git commit -m "docs: describe closed host call chain for search, governance, and execute"
```

### Task 7: Full regression pass

**Files:**
- Modify: `D:/02-Projects/vibe/tests/test_runtime.py` only if a failing test exposes a real mismatch

- [ ] **Step 1: Run focused host-call contract suite**

Run:

```bash
python -m unittest tests.test_runtime.RuntimeTests.test_search_returns_active_skill tests.test_runtime.RuntimeTests.test_service_search_matches_cli_shape tests.test_runtime.RuntimeTests.test_mcp_search_tool_returns_structured_payload tests.test_runtime.RuntimeTests.test_service_search_without_matches_recommends_distill_and_promote tests.test_runtime.RuntimeTests.test_governance_report_surfaces_duplicate_candidates tests.test_runtime.RuntimeTests.test_mcp_governance_report_returns_host_ready_recommended_actions tests.test_runtime.RuntimeTests.test_service_execute_returns_follow_up_host_operation tests.test_runtime.RuntimeTests.test_mcp_execute_tool_returns_follow_up_host_operation tests.test_runtime.RuntimeTests.test_search_and_governance_host_operations_share_same_type -v
```

Expected:
- PASS

- [ ] **Step 2: Run broader runtime suite**

Run:

```bash
python -m unittest tests.test_runtime -v
```

Expected:
- PASS
- If unrelated legacy failures exist, record them explicitly before proceeding

- [ ] **Step 3: Inspect git diff for contract drift**

Run:

```bash
git diff -- skill_runtime/api/service.py skill_runtime/retrieval/skill_index.py skill_runtime/governance/library_report.py skill_runtime/mcp/host_operations.py tests/test_runtime.py README.md README.zh-CN.md docs/mcp-integration.md docs/codex-integration.md
```

Expected:
- no duplicate builder helpers left in service/retrieval/governance
- docs mention the same field names as tests

- [ ] **Step 4: Final commit**

```bash
git add skill_runtime/mcp/host_operations.py skill_runtime/api/service.py skill_runtime/retrieval/skill_index.py skill_runtime/governance/library_report.py tests/test_runtime.py README.md README.zh-CN.md docs/mcp-integration.md docs/codex-integration.md
git commit -m "feat: unify host-call contract across search governance and execute"
```

- [ ] **Step 5: Prepare rollout summary**

Use this summary template:

```text
Completed:
- shared host operation builder
- search per-result and top-level executable recommendations
- governance preview/apply executable recommendations
- execute follow-up distill recommendation
- docs and tests aligned

Verification:
- focused host-call contract suite passed
- full runtime suite passed

Residual risk:
- hosts still need their own UX choice on whether to auto-run previews
- archive-cold is still CLI-only
```

## Risks and Mitigations

### Risk 1: Builder abstraction drifts from actual tool signatures

Mitigation:
- tests must assert real MCP tool names
- arguments must match current server tool parameters exactly
- do not introduce alias names in host payloads

### Risk 2: Execute follow-up recommendation becomes misleading for failed runs

Mitigation:
- only emit `recommended_next_action` on successful execution
- if execution errors, keep current error payload and do not add follow-up recommendation

### Risk 3: Docs get ahead of implementation

Mitigation:
- update docs only after tests for the shape pass
- use exact field names copied from tested payloads

## Rollout Order

Recommended order:

1. tests for execute follow-up
2. shared builder module
3. migrate search/governance to builder
4. add execute follow-up recommendation
5. remove duplicate local builders
6. update docs
7. run full regression

This order keeps the highest-value host workflow improvement on the critical path while limiting refactor noise.

## Audit Notes For Review

When reviewing this plan, focus on these decisions:

1. Should `execute` always recommend `distill_and_promote_candidate`, or only when the executed skill is new / low-usage / experimental?
2. Should `recommended_host_operation` include only required arguments, or should it also include optional placeholders?
3. Do we want `preview` only on governance actions, or also on any future destructive skill execution?
4. Is `skill_runtime/mcp/host_operations.py` the right home, or should host payload builders live under `api/` instead?

## Spec Coverage Self-Review

- Search path covered: yes, Tasks 3 and 5
- Governance path covered: yes, Task 3
- Execute follow-up path covered: yes, Task 4
- Shared builder / de-duplication covered: yes, Tasks 2 and 5
- Docs and rollout guidance covered: yes, Tasks 6 and 7
- Placeholder scan: no `TODO` / `TBD` placeholders left
- Type consistency: all proposed payloads use `type`, `tool_name`, `arguments`, optional `preview`
