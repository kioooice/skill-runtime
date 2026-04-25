# MCP Integration

This runtime can be exposed to host AI applications as a local MCP server over stdio.

## Start Command

From the runtime project root:

```bash
python scripts/skill_mcp_server.py
```

From any other working directory:

```bash
python D:/02-Projects/vibe/scripts/skill_mcp_server.py --root D:/02-Projects/vibe
```

You can also set the runtime root through an environment variable:

```bash
set SKILL_RUNTIME_ROOT=D:/02-Projects/vibe
python D:/02-Projects/vibe/scripts/skill_mcp_server.py
```

## Exposed MCP Tools

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
- `archive_cold_skills`

## Runtime Contract Layout

The host-call contract is now split across internal modules under `skill_runtime/mcp/`:

- `source_refs.py` for stable `source_ref` helpers
- `operation_builders.py` for single MCP host-call payload builders
- `recommendation_builders.py` for recommendation envelope builders
- `governance_actions.py` for governance action payload builders
- `host_operations.py` as the compatibility export surface

External callers should continue importing from `skill_runtime.mcp.host_operations`.
The internal split is for maintainability and should not change the public contract shape.
For maintenance checks, run `python scripts/check_mcp_architecture.py` to verify that
the internal module boundaries still match the documented import rules.
Run `python scripts/check_runtime_contracts.py` to validate the runtime-approved host
operation, recommendation, and governance-action payload shapes.
The repository also runs the same contract gate in
`.github/workflows/runtime-contracts.yml`, which covers both the architecture check and
the payload contract check before `python -m unittest tests.test_runtime -v`.

`distill_and_promote_candidate` can now start from either:

- `trajectory_path`
- or `observed_task_path`

If `observed_task_path` is used, the runtime captures it into a standard trajectory before distillation.

All tool responses use the same shape as the CLI:

```json
{
  "status": "ok",
  "data": {}
}
```

`governance_report` is now meant to be host-actionable, not just host-readable. Its
`recommended_actions[]` entries include a `host_operation` payload shaped like:

```json
{
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
```

That gives the host a direct bridge from:

1. showing a governance recommendation
2. optionally running the preview call
3. issuing the real MCP tool call without inventing arguments

`search_skill` now exposes the same host-call alignment in two places:

- each result item includes `host_operation`
- the top-level response includes `recommended_host_operation`
- the top-level response also includes `available_host_operations`

For strong matches, `available_host_operations` now includes:

- the primary recommended action first
- additional matched-skill execution actions after it

That lets a host wire both:

1. "run this matched skill"
2. "follow the top recommendation"

without any extra translation layer.

The host-call payload now also includes interaction metadata:

- `operation_id`
- `operation_role`
- `source_ref`
- `display_label`
- `effect_summary`
- `argument_schema`
- `risk_level`
- `requires_confirmation`
- `confirmation_message`

So a host can decide not only what to call, but also how to present and gate that call.
These values now come from shared runtime presets by default, while explicit values set by
the calling workflow take precedence when the context is more specific.
`operation_id` is a stable runtime-generated identifier based on the operation payload and
is intended for host-side reconciliation, rendering keys, and action callbacks.
`operation_role` indicates how the runtime expects the host to present the action, such as
`primary`, `default`, or `preview`.
`source_ref` links the operation back to the runtime object or context that produced it,
such as a matched skill, a governance recommendation, or an observed task record.
The runtime now treats `source_ref` as a stable contract field and emits it from shared
builders instead of ad-hoc string formatting at call sites.
`effect_summary` is short host-facing copy describing what the operation will do when run.
`argument_schema` describes the expected tool arguments and whether each one is already
prefilled by the runtime for the current action context.
For `execute_skill`, that schema now keeps the outer MCP tool shape stable while expanding
`args.properties` from the matched skill metadata, so hosts can render concrete fields such
as `input_dir` or `output_path` instead of a single opaque JSON object.
`confirmation_message` is present for actions that require confirmation and is `null` otherwise.

`execute_skill` now completes that chain. On success it returns:

- `observed_task_record`
- `recommended_next_action`
- `recommended_host_operation`
- `available_host_operations`

with a payload like:

```json
{
  "type": "mcp_tool_call",
  "tool_name": "distill_and_promote_candidate",
  "arguments": {
    "observed_task_path": "/abs/path.json"
  }
}
```

So the host can wire a closed loop:

1. `search_skill`
2. `execute_skill`
3. follow `recommended_host_operation`
4. call `distill_and_promote_candidate`

## Host-Call Lifecycle Loop

The explicit lifecycle path now uses the same host-call contract. Hosts can follow:

1. `log_trajectory` -> returned `recommended_host_operation` calls `distill_trajectory`
1. `capture_trajectory` -> returned `recommended_host_operation` calls `distill_trajectory`
2. `distill_trajectory` -> returned `recommended_host_operation` calls `audit_skill`
3. `audit_skill` on pass -> returned `recommended_host_operation` calls `promote_skill`
4. `promote_skill` -> returned `recommended_host_operation` calls `execute_skill`
5. `distill_and_promote_candidate` on success -> returned `recommended_host_operation` also calls `execute_skill`

so the host does not need to invent the next tool call between lifecycle steps.

For `search_skill` with no strong match, the primary recommendation is now
`capture_trajectory`, with `distill_and_promote_candidate` retained as a secondary action.
That lets the host guide the user through the most explicit capture-first path while still
exposing the shorter path when the host already has the needed artifact.

The fallback `distill_and_promote_candidate` operation advertises both supported entry paths in `argument_schema`:

- `trajectory_path`
- `observed_task_path`

plus optional `skill_name` and `register_trajectory`, so the host can guide the user
through the right input mode without guessing hidden parameters.

## Observed Task Input Shapes

Observed-task based flows share one normalized input contract across:

- `capture_trajectory`
- `distill_and_promote_candidate(observed_task_path=...)`
- execute follow-ups that emit `observed_task_record`

The runtime accepts three host-friendly shapes:

1. Verbose shape
   - `task_description`
   - `steps[].tool_name`
   - `steps[].tool_input`
   - `steps[].observation`
2. Compact shape
   - `task`
   - `actions[].tool` or `actions[].action`
   - `actions[].input` or `actions[].args`
   - `actions[].result` or `actions[].output`
3. Nested tool-log shape
   - `records[].tool.name`
   - `records[].tool.arguments`
   - `records[].result.message` or `records[].result.output`
   - `records[].result.success` or `records[].result.status`

Hosts should prefer keeping the emitted `observed_task_record` and passing it forward
through `recommended_host_operation` instead of reconstructing a new artifact by hand.

For governance preview flows, `archive_duplicate_candidates(dry_run=true)` now returns
an apply-ready `recommended_host_operation` for the same archive action, while keeping
`governance_report` available as a secondary action. After a real archive run, the primary
follow-up remains `governance_report`.

## Governance Maintenance Loop

The governance-oriented MCP tools are intended to be used as one closed maintenance loop:

1. `reindex_skills` refreshes the active library snapshot and now recommends `governance_report`
2. `governance_report` surfaces duplicate clusters and maintenance actions
3. `backfill_skill_provenance` repairs legacy metadata and then recommends `governance_report`
4. `archive_duplicate_candidates` supports preview/apply cleanup and returns `governance_report` after apply
5. `archive_cold_skills` archives stale active skills and returns `governance_report`

This means a host can keep one stable review surface for library maintenance instead of
inventing a different next step for each governance tool.

Current `source_ref` families include:

- `skill:{skill_name}` for search result run actions
- `search:recommended_skill:{skill_name}` for the top search recommendation
- `search:no_strong_match` and `search:no_strong_match:distill` for the capture-first fallback path
- `observed_task:{path}` for execution-emitted observed task follow-ups
- `log_trajectory:{task_id}` and `trajectory:{task_id}` for lifecycle follow-ups
- `distill:{skill_name}`, `audit:{skill_name}`, and `promote:{skill_name}` for governed promotion steps
- `governance:archive_duplicate_candidates:{canonical_skill}` and `...:preview` for governance archive actions
- `archive_duplicate_candidates:apply_follow_up`, `archive_duplicate_candidates:follow_up`, and
  `governance:report_refresh` for governance follow-up and refresh actions

Hosts should treat these as traceable provenance pointers rather than user-facing labels.
If the runtime changes the copy shown in `display_label` or `effect_summary`, `source_ref`
should remain the field used for telemetry, analytics, and reconciliation.

When a host wants to render buttons or menus directly, `available_host_operations` is the
preferred field because it exposes the runtime-approved action list without requiring the
host to merge top-level and nested recommendation fields itself.

On failure:

```json
{
  "status": "error",
  "message": "human readable error",
  "code": "MACHINE_READABLE_CODE",
  "details": {}
}
```

## Recommended Host Wiring

Use the runtime as a capability layer under the host AI, not as a second chat agent.

Recommended architecture:

```text
Host AI
-> MCP adapter
-> skill runtime
-> skill store / trajectories / audits
```

That keeps:

- user interaction in the host AI
- skill lifecycle and governance in the runtime
- model-provider choices internal to the runtime

## Generic stdio MCP Config Example

Example shape for hosts that accept a stdio MCP server definition:

```json
{
  "mcpServers": {
    "skill-runtime": {
      "command": "python",
      "args": [
        "D:/02-Projects/vibe/scripts/skill_mcp_server.py",
        "--root",
        "D:/02-Projects/vibe"
      ]
    }
  }
}
```

If the host supports environment variables in MCP config, this is cleaner:

```json
{
  "mcpServers": {
    "skill-runtime": {
      "command": "python",
      "args": [
        "D:/02-Projects/vibe/scripts/skill_mcp_server.py"
      ],
      "env": {
        "SKILL_RUNTIME_ROOT": "D:/02-Projects/vibe"
      }
    }
  }
}
```

## Codex-Oriented Usage

For Codex-style hosts, the intended flow is:

1. `search_skill`
2. If there is a strong match, `execute_skill`
3. Successful execution now returns an `observed_task_record` path
4. If the task was new or improved, follow `recommended_host_operation` into `distill_and_promote_candidate`
5. If no hit, host AI completes the task
6. Explicit path: use the host-call lifecycle loop above
7. Use the governance maintenance loop for library maintenance

This keeps the host AI responsible for planning and user interaction, while the runtime handles:

- distillation
- audit
- provenance
- retrieval
- execution
- governance reporting

## Current Limits

- The MCP server currently exposes tools only, not prompts or resources.
- Fallback distillation still uses the mock provider unless a real provider is added later.
