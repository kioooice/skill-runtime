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
- `reindex_skills`
- `backfill_skill_provenance`

All tool responses use the same shape as the CLI:

```json
{
  "status": "ok",
  "data": {}
}
```

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
2. If no hit, host AI completes the task
3. Short path: `distill_and_promote_candidate`
4. Explicit path: `log_trajectory`, `distill_trajectory`, `audit_skill`, and `promote_skill`
5. Future runs use `execute_skill`

This keeps the host AI responsible for planning and user interaction, while the runtime handles:

- distillation
- audit
- provenance
- retrieval
- execution

## Current Limits

- The MCP server currently exposes tools only, not prompts or resources.
- `archive-cold` is not exposed yet because it is still a placeholder command.
- Fallback distillation still uses the mock provider unless a real provider is added later.
