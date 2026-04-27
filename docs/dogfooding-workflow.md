# Dogfooding Workflow

This document captures the recommended real-usage loop for `skill-runtime` after the latest usability improvements.

## Goal

Use the runtime the way a host AI such as Codex would use it in day-to-day repeated local tasks, without hand-writing full trajectories.

## Default Loop

```text
search -> execute -> rollback dry-run/apply when needed -> observed task record -> distill/promote -> reuse -> govern
```

## Fast Path

Use this for repeated or obviously reusable local workflows.

1. Search first

```bash
python scripts/skill_cli.py search --query "<task>"
```

2. If there is a strong match, execute it

```bash
python scripts/skill_cli.py execute --skill <skill_name> --args-file <json file>
```

3. Keep the returned `observed_task_record`

Successful `execute` calls now emit a lightweight observed task record automatically. This removes the need to reconstruct the task manually afterward.

The same response now also exposes:

- `operation_log` for the full ordered tool trace
- `planned_changes` for dry-run-only mutation previews
- `available_host_operations` for direct follow-up actions such as rollback or promotion

4. If the execution changed files, inspect or apply rollback from the `execute` payload

The CLI can now consume the full `execute` response directly instead of making you extract `operation_log` and `operation_ids` by hand.

```bash
python scripts/skill_cli.py rollback-operations --execute-result-file <execute_result.json> --dry-run
python scripts/skill_cli.py rollback-operations --execute-result-file <execute_result.json>
```

5. If the task was new, improved, or worth reusing, send that record back into the library

```bash
python scripts/skill_cli.py distill-and-promote --observed-task <observed_task.json> --skill-name <optional_name>
```

## Explicit Path

Use this only when step-by-step inspection is needed.

```bash
python scripts/skill_cli.py capture-trajectory --file <observed_task.json>
python scripts/skill_cli.py log-trajectory --file <trajectory.json>
python scripts/skill_cli.py distill --trajectory <trajectory.json> --skill-name <optional_name>
python scripts/skill_cli.py audit --file <staging_skill.py> --trajectory <trajectory.json>
python scripts/skill_cli.py promote --file <staging_skill.py>
```

## Observed Task Record Shapes

The runtime now accepts three practical shapes:

### 1. Verbose trajectory-like shape

- `task_description`
- `steps[].tool_name`
- `steps[].tool_input`
- `steps[].observation`

### 2. Compact host-friendly shape

- `task`
- `actions[].tool` or `actions[].action`
- `actions[].input` or `actions[].args`
- `actions[].result` or `actions[].output`

### 3. Nested tool-call log shape

- `records[].tool.name`
- `records[].tool.arguments`
- `records[].result.message` or `records[].result.output`
- `records[].result.success` or `records[].result.status`

## Governance Pass

Run this periodically once the library grows:

```bash
python scripts/skill_cli.py governance-report
python scripts/skill_cli.py archive-cold --days 30
python scripts/skill_cli.py archive-duplicate-candidates --dry-run
python scripts/skill_cli.py archive-duplicate-candidates --skill-name <name>
python scripts/skill_cli.py backfill-provenance
```

What to look for:

- duplicate candidates
- too many experimental or test-generated skills
- active/archive counts drifting out of control
- canonical recommendations before archiving duplicate candidates

## Practical Recommendation

For most real usage, do not hand-author trajectories anymore.

Prefer:

1. `search`
2. `execute`
3. keep `observed_task_record`
4. `distill-and-promote --observed-task`

That is currently the most realistic dogfooding path for this project.
