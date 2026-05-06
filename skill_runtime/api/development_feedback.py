from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from pathlib import PurePath
from typing import Any

from skill_runtime.api.models import AgentTaskRequest, CodexTaskClassification


DEVELOPMENT_OUTPUT_SUFFIXES = {".md", ".json", ".py", ".toml", ".yml", ".yaml", ".txt"}
STATE_FILE_NAMES = {"HANDOFF.md", "TASKS.md", "DECISIONS.md"}
DEVELOPMENT_FEEDBACK_REVIEW_FILE = Path(".skill_runtime") / "development_feedback_reviews.json"
DEVELOPMENT_FEEDBACK_REVIEW_STATUSES = {"needs_review", "accepted", "applied", "dismissed"}


def build_development_feedback(
    request: AgentTaskRequest,
    classification: CodexTaskClassification | None,
    *,
    root: str | Path | None = None,
) -> list[dict[str, str]]:
    if not _is_development_feedback_candidate(request, classification):
        return []

    feedback: list[dict[str, str]] = []
    if _touches_cli_json_path(request):
        feedback.append(
            {
                "id": "powershell-safe-cli-json",
                "title": "Use PowerShell-safe CLI JSON inputs",
                "source": "runtime-gate-workflow",
                "why": "This touches CLI or Codex command paths; avoid PowerShell inline JSON and BOM-prone here-strings.",
                "behavior_change": (
                    "Prefer --known-inputs-json-file, --expected-outputs-json-file, --plan-json-file, "
                    "or direct host API calls for structured Codex CLI payloads."
                ),
            }
        )
    if _looks_like_localized_change(request):
        feedback.append(
            {
                "id": "scoped-verification",
                "title": "Use scoped verification",
                "source": "workflow-error-correction",
                "why": "This looks like a localized development change, so repository-wide suites are not the default first check.",
                "behavior_change": (
                    "Choose the smallest useful checks first, such as JSON validation, targeted tests, "
                    "py_compile for changed Python files, and git diff --check."
                ),
            }
        )

    feedback.append(
        {
            "id": "state-file-churn",
            "title": "Avoid state-file churn",
            "source": "workflow-error-correction",
            "why": "State files are durable handoff memory, not a required artifact for every small task.",
            "behavior_change": (
                "Update HANDOFF.md, TASKS.md, and DECISIONS.md only if the next-session entry point changes, "
                "a durable decision was made, a blocker appeared, or long-context risk changed."
            ),
        }
    )
    feedback.append(
        {
            "id": "publish-churn",
            "title": "Avoid automatic publish churn",
            "source": "workflow-error-correction",
            "why": "Small local slices should not create commit/push overhead unless the user asked or a meaningful stage finished.",
            "behavior_change": (
                "Do not commit and push by default after this task; publish only at a meaningful batching point "
                "or on explicit request."
            ),
        }
    )
    return _with_review_state(feedback[:3], root)


def load_development_feedback_reviews(root: str | Path) -> dict[str, dict[str, str]]:
    path = Path(root).resolve() / DEVELOPMENT_FEEDBACK_REVIEW_FILE
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (json.JSONDecodeError, OSError):
        return {}
    reviews = payload.get("reviews") if isinstance(payload, dict) else None
    if not isinstance(reviews, dict):
        return {}
    clean: dict[str, dict[str, str]] = {}
    for feedback_id, raw_record in reviews.items():
        if not isinstance(feedback_id, str) or not isinstance(raw_record, dict):
            continue
        clean_record = {
            key: value
            for key, value in raw_record.items()
            if isinstance(key, str) and isinstance(value, str)
        }
        if clean_record:
            clean[feedback_id] = clean_record
    return clean


def record_development_feedback_review(
    root: str | Path,
    *,
    feedback_id: str,
    status: str,
    note: str = "",
    reviewer: str = "local",
) -> dict[str, str]:
    normalized_id = feedback_id.strip()
    normalized_status = status.strip()
    if not normalized_id:
        raise ValueError("feedback_id is required")
    if normalized_status not in DEVELOPMENT_FEEDBACK_REVIEW_STATUSES:
        allowed = ", ".join(sorted(DEVELOPMENT_FEEDBACK_REVIEW_STATUSES))
        raise ValueError(f"status must be one of: {allowed}")

    runtime_root = Path(root).resolve()
    path = runtime_root / DEVELOPMENT_FEEDBACK_REVIEW_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    reviews = load_development_feedback_reviews(runtime_root)
    record = {
        "id": normalized_id,
        "status": normalized_status,
        "note": note.strip(),
        "reviewer": reviewer.strip() or "local",
        "reviewed_at": datetime.now(timezone.utc).isoformat(),
    }
    reviews[normalized_id] = record
    payload = {
        "version": 1,
        "updated_at": record["reviewed_at"],
        "reviews": reviews,
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return {**record, "review_record_path": str(path)}


def _is_development_feedback_candidate(
    request: AgentTaskRequest,
    classification: CodexTaskClassification | None,
) -> bool:
    signals = set(classification.matched_signals) if classification else set()
    if "family:development-workflow-observation" in signals:
        return True
    return _looks_like_development_outputs(request)


def _looks_like_localized_change(request: AgentTaskRequest) -> bool:
    outputs = _normalized_outputs(request)
    if not outputs:
        return False
    return len(outputs) <= 4 and all(_has_development_suffix(path) for path in outputs)


def _looks_like_development_outputs(request: AgentTaskRequest) -> bool:
    outputs = _normalized_outputs(request)
    if not outputs:
        return False
    if any(path.name in STATE_FILE_NAMES for path in outputs):
        return True
    return any(_has_development_suffix(path) for path in outputs)


def _touches_cli_json_path(request: AgentTaskRequest) -> bool:
    task = request.task_description.lower()
    if any(token in task for token in ("codex-run", "codex-finalize", "cli", "powershell", "inline json")):
        return True
    for path in _normalized_outputs(request):
        normalized = path.as_posix().lower()
        if normalized in {"skill_runtime/cli.py", "skill_runtime/mcp/server.py"}:
            return True
        if normalized.endswith("/cli.py") or normalized.endswith("/mcp/server.py"):
            return True
    return False


def _normalized_outputs(request: AgentTaskRequest) -> list[PurePath]:
    return [PurePath(item) for item in request.expected_outputs if isinstance(item, str) and item.strip()]


def _has_development_suffix(path: PurePath) -> bool:
    return path.suffix.lower() in DEVELOPMENT_OUTPUT_SUFFIXES


def _with_review_state(
    feedback: list[dict[str, str]],
    root: str | Path | None,
) -> list[dict[str, str]]:
    reviews = load_development_feedback_reviews(root) if root is not None else {}
    annotated: list[dict[str, str]] = []
    for item in feedback:
        feedback_id = item.get("id", "")
        review = reviews.get(feedback_id, {})
        annotated.append(
            {
                **item,
                "review_status": review.get("status", "needs_review"),
                "review_note": review.get("note", ""),
                "reviewed_at": review.get("reviewed_at", ""),
                "reviewer": review.get("reviewer", ""),
            }
        )
    return annotated
