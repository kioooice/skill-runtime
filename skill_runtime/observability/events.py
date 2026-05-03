from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from skill_runtime.api.models import AgentOrchestrationResult

RUNTIME_LANE_EVENTS_FILE = Path(".skill_runtime") / "runtime_lane_events.jsonl"


def append_runtime_lane_event(root: str | Path, result: AgentOrchestrationResult) -> Path | None:
    try:
        event_path = Path(root).resolve() / RUNTIME_LANE_EVENTS_FILE
        event_path.parent.mkdir(parents=True, exist_ok=True)
        with event_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(_event_from_result(Path(root).resolve(), result), ensure_ascii=False) + "\n")
        return event_path
    except OSError:
        return None


def read_runtime_lane_events(root: str | Path, limit: int | None = None) -> list[dict[str, Any]]:
    event_path = Path(root).resolve() / RUNTIME_LANE_EVENTS_FILE
    if not event_path.exists():
        return []
    events: list[dict[str, Any]] = []
    for line in event_path.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            events.append(payload)
    if limit is None:
        return events
    return events[-limit:]


def _event_from_result(root: Path, result: AgentOrchestrationResult) -> dict[str, Any]:
    classification = result.task_classification
    learning_capture = result.learning_capture_payload if isinstance(result.learning_capture_payload, dict) else {}
    available_operations = _available_host_operations(learning_capture)
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "working_directory": str(root),
        "task_description": result.request.task_description,
        "runtime_lane_status": result.runtime_lane_status,
        "runtime_lane_reason": result.runtime_lane_reason,
        "classification_bucket": classification.bucket if classification else None,
        "classification_reason": classification.reason if classification else None,
        "matched_signals": list(classification.matched_signals) if classification else [],
        "reuse_decision": result.reuse_decision.decision,
        "learning_decision": result.learning_decision.decision if result.learning_decision else None,
        "selected_skill_name": result.selected_skill_name,
        "observed_task_record": _observed_task_record(result),
        "recommended_next_action": _string_or_none(learning_capture.get("recommended_next_action")),
        "available_host_operation_count": len(available_operations),
        "available_host_operation_labels": _operation_values(available_operations, "display_label"),
        "available_host_operation_tools": _operation_values(available_operations, "tool_name"),
    }


def _observed_task_record(result: AgentOrchestrationResult) -> str | None:
    if isinstance(result.execution_payload, dict):
        value = result.execution_payload.get("observed_task_record")
        if isinstance(value, str):
            return value
    if isinstance(result.learning_capture_payload, dict):
        value = result.learning_capture_payload.get("trajectory_path")
        if isinstance(value, str):
            return value
    return None


def _available_host_operations(payload: dict[str, Any]) -> list[dict[str, Any]]:
    operations = payload.get("available_host_operations")
    if not isinstance(operations, list):
        return []
    return [operation for operation in operations if isinstance(operation, dict)]


def _operation_values(operations: list[dict[str, Any]], key: str) -> list[str]:
    values: list[str] = []
    for operation in operations:
        value = operation.get(key)
        if isinstance(value, str) and value:
            values.append(value)
    return values


def _string_or_none(value: Any) -> str | None:
    return value if isinstance(value, str) and value else None
