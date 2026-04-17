# Codex Integration

This document is the Codex-specific wiring guide for the local skill runtime.

## Recommended Integration Shape

For Codex, this runtime should be treated as a local MCP-backed capability layer, not as a second chat agent.

Recommended flow:

```text
Codex
-> MCP server: skill_runtime
-> runtime service
-> skill store / trajectories / audits
```

That keeps:

- user interaction in Codex
- skill lifecycle inside the runtime
- future model-provider changes internal to the runtime

## Why This Matches Codex

OpenAI’s Docs MCP guide states that Codex can connect to MCP servers through shared configuration in `~/.codex/config.toml`.

OpenAI’s App Server article also states:

- MCP is a good fit when you already have an MCP-based workflow and want callable tools
- App Server is the first-class protocol for full Codex harness integration

For this project, MCP is the correct near-term integration because this runtime is a tool layer under Codex, not a replacement for the Codex harness.

## Installed Codex Config

The local Codex config now includes this MCP server entry:

```toml
[mcp_servers.skill_runtime]
command = "python"
args = ["D:/02-Projects/vibe/scripts/skill_mcp_server.py", "--root", "D:/02-Projects/vibe"]
```

Config file:

`C:/Users/Administrator/.codex/config.toml`

## What Codex Can Call

The runtime currently exposes these MCP tools:

- `search_skill`
- `execute_skill`
- `distill_trajectory`
- `distill_and_promote_candidate`
- `audit_skill`
- `promote_skill`
- `log_trajectory`
- `reindex_skills`
- `backfill_skill_provenance`

## Recommended Codex Workflow

For repetitive or workflow-like tasks:

1. Ask Codex to call `search_skill` first
2. If a good match exists, call `execute_skill`
3. If no good match exists, let Codex complete the task normally
4. Save or construct a trajectory JSON
5. Preferred short path: call `distill_and_promote_candidate`
6. Explicit path: call `log_trajectory`, `distill_trajectory`, `audit_skill`, and `promote_skill`

This keeps Codex responsible for:

- task understanding
- planning
- user communication

And keeps the runtime responsible for:

- skill storage
- audit
- retrieval
- provenance
- execution

## Runtime Relocation

If you move this runtime project, update the MCP args in:

`C:/Users/Administrator/.codex/config.toml`

Or keep the same script path and change only the `--root` value.

## Current Limits

- This is tool-level integration, not full Codex App Server integration.
- You do not get richer Codex session semantics such as native diff-stream interactions through this runtime MCP layer.
- If you later want deeper integration with Codex itself, the next protocol to consider is Codex App Server rather than replacing this MCP layer.

## Sources

- OpenAI Docs MCP quickstart for Codex: https://developers.openai.com/learn/docs-mcp
- OpenAI App Server architecture and protocol guidance: https://openai.com/index/unlocking-the-codex-harness/
