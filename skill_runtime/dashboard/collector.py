from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from skill_runtime.api.models import SkillMetadata
from skill_runtime.api.service import RuntimeService
from skill_runtime.observability.events import read_runtime_lane_events
from skill_runtime.retrieval.skill_index import SkillIndex, SkillIndexError


def collect_dashboard_data(root: str | Path, *, event_limit: int = 50) -> dict[str, Any]:
    runtime_root = Path(root).resolve()
    diagnostics: list[str] = []
    skills = _collect_skills(runtime_root, diagnostics)
    events = list(reversed(read_runtime_lane_events(runtime_root, limit=event_limit)))
    governance = _collect_governance(runtime_root, diagnostics)
    overview = _build_overview(skills, events, governance)
    return {
        "root": str(runtime_root),
        "overview": overview,
        "skills": skills,
        "events": events,
        "governance": governance,
        "diagnostics": diagnostics,
    }


def _collect_skills(root: Path, diagnostics: list[str]) -> list[dict[str, Any]]:
    index_path = root / "skill_store" / "index.json"
    try:
        indexed = {skill.skill_name: skill for skill in SkillIndex(index_path).load_all()}
    except (json.JSONDecodeError, SkillIndexError, OSError) as exc:
        diagnostics.append(f"Could not read skill index: {exc}")
        indexed = {}

    skills: dict[str, dict[str, Any]] = {}
    for status, directory_name in (
        ("active", "active"),
        ("staging", "staging"),
        ("archived", "archive"),
        ("rejected", "rejected"),
    ):
        directory = root / "skill_store" / directory_name
        if not directory.exists():
            diagnostics.append(f"Missing skill directory: {directory.relative_to(root)}")
            continue
        for metadata_path in sorted(directory.glob("*.metadata.json")):
            payload = _read_json(metadata_path, diagnostics)
            if not isinstance(payload, dict):
                continue
            skill_name = str(payload.get("skill_name") or metadata_path.name.replace(".metadata.json", ""))
            indexed_metadata = indexed.get(skill_name)
            skills[skill_name] = _skill_payload(skill_name, status, payload, indexed_metadata, root)
    return sorted(skills.values(), key=lambda item: (item["status"], item["skill_name"]))


def _skill_payload(
    skill_name: str,
    status: str,
    payload: dict[str, Any],
    indexed_metadata: SkillMetadata | None,
    root: Path,
) -> dict[str, Any]:
    source_trajectory_ids = payload.get("source_trajectory_ids")
    if not isinstance(source_trajectory_ids, list):
        source_trajectory_ids = []
    usage_count = payload.get("usage_count", 0)
    last_used_at = payload.get("last_used_at")
    if indexed_metadata is not None:
        usage_count = indexed_metadata.usage_count
        last_used_at = indexed_metadata.last_used_at
    file_path = str(payload.get("file_path") or "")
    return {
        "skill_name": skill_name,
        "status": status,
        "summary": str(payload.get("summary") or ""),
        "file_path": file_path,
        "relative_file_path": _relative_path(file_path, root),
        "source_trajectory_ids": [str(item) for item in source_trajectory_ids],
        "audit_score": payload.get("audit_score"),
        "usage_count": usage_count if isinstance(usage_count, int) else 0,
        "last_used_at": last_used_at if isinstance(last_used_at, str) else None,
        "tags": payload.get("tags") if isinstance(payload.get("tags"), list) else [],
    }


def _collect_governance(root: Path, diagnostics: list[str]) -> dict[str, Any]:
    try:
        report = RuntimeService(root).governance_report()
    except Exception as exc:
        diagnostics.append(f"Could not build governance report: {exc}")
        return {"status_counts": {}, "duplicate_candidates": [], "recommended_actions": []}
    return {
        "status_counts": report.get("status_counts", {}),
        "duplicate_candidates": report.get("duplicate_candidates", []),
        "recommended_actions": report.get("recommended_actions", []),
    }


def _build_overview(
    skills: list[dict[str, Any]],
    events: list[dict[str, Any]],
    governance: dict[str, Any],
) -> dict[str, Any]:
    status_counts = {"active": 0, "staging": 0, "archived": 0, "rejected": 0}
    for skill in skills:
        status = skill["status"]
        if status in status_counts:
            status_counts[status] += 1
    event_counts = {"used": 0, "entered": 0, "skipped": 0}
    for event in events:
        status = event.get("runtime_lane_status")
        if status in event_counts:
            event_counts[status] += 1
    duplicate_candidates = governance.get("duplicate_candidates")
    governance_warning_count = len(duplicate_candidates) if isinstance(duplicate_candidates, list) else 0
    return {
        "active_count": status_counts["active"],
        "staging_count": status_counts["staging"],
        "archive_count": status_counts["archived"],
        "rejected_count": status_counts["rejected"],
        "latest_event_time": events[0].get("timestamp") if events else None,
        "recent_event_counts": event_counts,
        "governance_warning_count": governance_warning_count,
    }


def _read_json(path: Path, diagnostics: list[str]) -> object | None:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (json.JSONDecodeError, OSError) as exc:
        diagnostics.append(f"Could not read {path.name}: {exc}")
        return None


def _relative_path(raw_path: str, root: Path) -> str:
    if not raw_path:
        return ""
    try:
        return str(Path(raw_path).resolve().relative_to(root))
    except ValueError:
        return raw_path
