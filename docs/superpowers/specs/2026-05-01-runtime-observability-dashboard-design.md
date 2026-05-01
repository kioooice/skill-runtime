# Runtime Observability Dashboard Design

Date: 2026-05-01

## Purpose

This design defines a first read-only dashboard for Skill Runtime.

The dashboard should answer one product question:

`Is the runtime lane actually working in this repository?`

It is not a full skill management backend. It is an observation surface for the current local runtime root.

## Scope

The first version is local and read-only.

It reads data from the current runtime root and generates a static HTML dashboard.

Recommended command:

```bash
skill-runtime dashboard
```

Optional flags can be added in implementation:

```bash
skill-runtime dashboard --output .skill_runtime/dashboard.html
skill-runtime dashboard --open
```

## Non-Goals

The first version must not include:

- editing skill files
- approving or promoting skills from the UI
- deleting or archiving skills from the UI
- cross-workspace aggregation
- long-running web service
- user accounts or remote access

These are intentionally excluded so the dashboard stays safe and useful as an observation layer.

## Primary User Questions

The dashboard should make these questions easy to answer:

- What active skills exist in this runtime root?
- Which trajectories produced or influenced each skill?
- Which skills are staging, active, archived, or rejected?
- Did recent Codex tasks enter the runtime lane?
- Did any recent task actually use a skill?
- Why did a task get skipped?
- Are there obvious governance concerns, such as duplicate or cold skills?

## Data Sources

The first version should read only local repository/runtime files:

- `skill_store/index.json`
- `skill_store/active/*.metadata.json`
- `skill_store/staging/*.metadata.json`
- `skill_store/archive/*.metadata.json`
- `skill_store/rejected/*.metadata.json`
- `trajectories/*.json`
- `audits/*.audit.json`
- `.skill_runtime/usage.json`
- `.skill_runtime/runtime_lane_events.jsonl`

The dashboard should tolerate missing files and show empty states instead of failing.

## Runtime Lane Event Log

The trigger log should be append-only JSONL.

Recommended path:

```text
.skill_runtime/runtime_lane_events.jsonl
```

Each Codex-facing orchestration result should append one event when it returns from a runtime-lane entry point.

Recommended event shape:

```json
{
  "timestamp": "2026-05-01T12:00:00Z",
  "working_directory": "D:/02-Projects/vibe",
  "task_description": "merge txt files into markdown",
  "runtime_lane_status": "used",
  "runtime_lane_reason": "task entered Codex runtime lane and auto-executed reusable skill merge_text_files",
  "classification_bucket": "default-in",
  "classification_reason": "local low-risk text transformation",
  "reuse_decision": "auto_execute",
  "learning_decision": "skip",
  "selected_skill_name": "merge_text_files",
  "observed_task_record": null
}
```

Allowed `runtime_lane_status` values:

- `used`
- `entered`
- `skipped`

The event logger must be best-effort. A logging failure must not break the user task.

## Dashboard Layout

The dashboard should have four main sections.

### 1. Overview

Shows the health of the local runtime root:

- active skill count
- staging skill count
- archived skill count
- rejected skill count
- latest runtime lane event time
- recent `used / entered / skipped` counts
- governance warning count

This section answers whether the runtime is alive and whether recent work touched it.

### 2. Skill Tree

Shows a relationship graph:

```text
trajectory
-> staging skill
-> audit
-> active skill
-> reuse events
```

For the first version, this can be rendered as grouped cards or a simple tree list.

The first version does not need a complex graph library. Clarity is more important than visual novelty.

### 3. Trigger Log

Shows recent runtime lane events:

- timestamp
- status badge: `used`, `entered`, or `skipped`
- task description
- selected skill name when available
- reason

The log should default to the latest 50 events.

The UI should make `skipped` normal, not alarming. A skipped task can mean the classifier correctly kept the task on the normal Codex path.

### 4. Governance Snapshot

Shows read-only maintenance signals:

- duplicate candidates from `governance_report`
- cold skills if available
- missing audit records
- metadata parse errors
- skills with no source trajectory

The first version should not provide action buttons. It can show the CLI/MCP command a user could run manually later.

## Architecture

Recommended implementation shape:

```text
skill_runtime/api/host.py
-> append runtime lane event

skill_runtime/dashboard/
-> collect local runtime data
-> build dashboard view model
-> render static HTML

skill_runtime/cli.py
-> dashboard command
```

Suggested modules:

- `skill_runtime/observability/events.py`
- `skill_runtime/dashboard/collector.py`
- `skill_runtime/dashboard/render.py`
- `skill_runtime/dashboard/templates.py`

The event logger and dashboard renderer should not import MCP server code.

## Data Flow

```text
Codex task
-> classify_codex_task
-> start/run/finalize_codex_task
-> AgentOrchestrationResult with runtime_lane_status
-> append runtime lane event
-> skill-runtime dashboard
-> read skill store + trajectories + audits + events
-> generate .skill_runtime/dashboard.html
```

## Error Handling

The dashboard should continue rendering when:

- event log does not exist
- a metadata file is malformed
- a trajectory file is missing
- a skill has no audit record
- governance report cannot be computed

Errors should appear in a small diagnostics section instead of crashing the command.

Runtime lane event logging should be best-effort and must not raise out of task execution.

## Testing Plan

Minimum tests:

- event logger appends valid JSONL
- logger failure does not break orchestration
- dashboard collector handles empty runtime root
- dashboard collector reads active skill metadata and usage
- dashboard collector reads runtime lane events
- dashboard renderer includes skill tree, trigger log, and governance sections
- CLI `dashboard` command writes an HTML file

Recommended first verification commands:

```bash
python -m unittest tests.test_runtime_fast -v
python scripts/check_mcp_architecture.py
python scripts/check_runtime_contracts.py
```

## Product Constraints

The dashboard should reinforce the current product direction:

- Skill Runtime is a background capability layer.
- Users should not need to manually browse skills before doing work.
- The UI exists to explain and diagnose the background layer.
- The UI should not become the primary way to operate normal tasks.

## Recommended First Milestone

Build only this closed loop:

1. Codex runtime lane appends event records.
2. `skill-runtime dashboard` reads local files.
3. The command writes a static HTML file.
4. The page shows overview, skill tree, trigger log, and governance snapshot.

Stop there before adding interactive controls.

## Open Decisions

No blocking decisions remain for the first design.

Future decisions, after the first read-only dashboard works:

- whether to add a local browser auto-open flag
- whether to add manual governance buttons
- whether to support cross-workspace aggregation
- whether to expose the dashboard through a long-running local web server
