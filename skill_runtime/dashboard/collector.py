from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from skill_runtime.api.models import SkillMetadata
from skill_runtime.api.service import RuntimeService
from skill_runtime.collections.store import load_capability_collections
from skill_runtime.observability.events import RUNTIME_LANE_EVENTS_FILE, read_runtime_lane_events
from skill_runtime.platforms.discovery import collect_platform_inventory
from skill_runtime.retrieval.skill_index import SkillIndex, SkillIndexError


def collect_dashboard_data(root: str | Path, *, event_limit: int = 50) -> dict[str, Any]:
    runtime_root = Path(root).resolve()
    diagnostics: list[str] = []
    skills = _collect_skills(runtime_root, diagnostics)
    events = list(reversed(read_runtime_lane_events(runtime_root, limit=event_limit)))
    governance = _collect_governance(runtime_root, diagnostics)
    platform_inventory = collect_platform_inventory(runtime_root)
    capability_collections = load_capability_collections(runtime_root, skills, diagnostics)
    overview = _build_overview(skills, events, governance)
    return {
        "root": str(runtime_root),
        "overview": overview,
        "skills": skills,
        "events": events,
        "governance": governance,
        "capability_collections": capability_collections,
        "platform_inventory": platform_inventory,
        "diagnostics": diagnostics,
    }


def collect_global_dashboard_data(
    root: str | Path,
    *,
    scan_roots: list[str | Path] | None = None,
    event_limit: int = 200,
) -> dict[str, Any]:
    runtime_root = Path(root).resolve()
    diagnostics: list[str] = []
    resolved_scan_roots = _resolve_scan_roots(runtime_root, scan_roots, diagnostics)
    project_roots = _discover_event_roots(runtime_root, resolved_scan_roots, diagnostics)
    projects: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []

    for project_root in project_roots:
        project_events = list(reversed(read_runtime_lane_events(project_root, limit=event_limit)))
        if not project_events:
            continue
        annotated_events = [_global_event_payload(event, project_root) for event in project_events]
        events.extend(annotated_events)
        counts = _event_counts(annotated_events)
        projects.append(
            {
                "project_name": project_root.name,
                "project_root": str(project_root),
                "event_count": len(annotated_events),
                "latest_event_time": annotated_events[0].get("timestamp"),
                "recent_event_counts": counts,
            }
        )

    events = sorted(events, key=lambda item: str(item.get("timestamp") or ""), reverse=True)[:event_limit]
    projects = sorted(projects, key=lambda item: str(item.get("latest_event_time") or ""), reverse=True)
    return {
        "root": str(runtime_root),
        "scan_roots": [str(path) for path in resolved_scan_roots],
        "overview": _build_global_overview(projects, events),
        "projects": projects,
        "events": events,
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
    status_rank = {"active": 0, "staging": 1, "archived": 2, "rejected": 3}
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
            existing = skills.get(skill_name)
            if existing is not None and status_rank.get(existing["status"], 99) <= status_rank.get(status, 99):
                continue
            indexed_metadata = indexed.get(skill_name)
            skills[skill_name] = _skill_payload(skill_name, status, payload, indexed_metadata, root)
    return sorted(skills.values(), key=lambda item: (item["status"], item["skill_name"]))


def _resolve_scan_roots(
    runtime_root: Path,
    scan_roots: list[str | Path] | None,
    diagnostics: list[str],
) -> list[Path]:
    raw_scan_roots = scan_roots if scan_roots else [runtime_root.parent]
    resolved: list[Path] = []
    seen: set[Path] = set()
    for raw_path in raw_scan_roots:
        try:
            path = Path(raw_path).resolve()
        except OSError as exc:
            diagnostics.append(f"Could not resolve scan root {raw_path}: {exc}")
            continue
        if path in seen:
            continue
        seen.add(path)
        resolved.append(path)
    return resolved


def _discover_event_roots(runtime_root: Path, scan_roots: list[Path], diagnostics: list[str]) -> list[Path]:
    discovered: list[Path] = []
    seen: set[Path] = set()

    def add_if_event_root(candidate: Path) -> None:
        try:
            project_root = candidate.resolve()
        except OSError as exc:
            diagnostics.append(f"Could not inspect project root {candidate}: {exc}")
            return
        if project_root in seen:
            return
        if (project_root / RUNTIME_LANE_EVENTS_FILE).exists():
            seen.add(project_root)
            discovered.append(project_root)

    add_if_event_root(runtime_root)
    for scan_root in scan_roots:
        if not scan_root.exists():
            diagnostics.append(f"Missing scan root: {scan_root}")
            continue
        add_if_event_root(scan_root)
        try:
            children = sorted(path for path in scan_root.iterdir() if path.is_dir())
        except OSError as exc:
            diagnostics.append(f"Could not scan {scan_root}: {exc}")
            continue
        for child in children:
            add_if_event_root(child)
    return discovered


def _global_event_payload(event: dict[str, Any], project_root: Path) -> dict[str, Any]:
    payload = dict(event)
    payload["project_name"] = project_root.name
    payload["project_root"] = str(project_root)
    return payload


def _event_counts(events: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"used": 0, "entered": 0, "skipped": 0}
    for event in events:
        status = event.get("runtime_lane_status")
        if status in counts:
            counts[status] += 1
    return counts


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
    tags = payload.get("tags") if isinstance(payload.get("tags"), list) else []
    provenance = payload.get("provenance") if isinstance(payload.get("provenance"), dict) else {}
    audit_status = payload.get("audit_status")
    import_source = payload.get("import_source")
    imported_at = payload.get("imported_at")
    content_hash = payload.get("content_hash")
    provenance_type = provenance.get("type")
    return {
        "skill_name": skill_name,
        "status": status,
        "summary": str(payload.get("summary") or ""),
        "file_path": file_path,
        "relative_file_path": _relative_path(file_path, root),
        "source_trajectory_ids": [str(item) for item in source_trajectory_ids],
        "audit_score": payload.get("audit_score"),
        "audit_status": audit_status if isinstance(audit_status, str) else None,
        "usage_count": usage_count if isinstance(usage_count, int) else 0,
        "last_used_at": last_used_at if isinstance(last_used_at, str) else None,
        "tags": tags,
        "import_source": import_source if isinstance(import_source, str) else None,
        "imported_at": imported_at if isinstance(imported_at, str) else None,
        "content_hash": content_hash if isinstance(content_hash, str) else None,
        "provenance": provenance,
        "is_imported": "imported" in tags or provenance_type == "local_skill_import",
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


def _build_global_overview(projects: list[dict[str, Any]], events: list[dict[str, Any]]) -> dict[str, Any]:
    counts = _event_counts(events)
    return {
        "project_count": len(projects),
        "event_count": len(events),
        "latest_event_time": events[0].get("timestamp") if events else None,
        "recent_event_counts": counts,
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
