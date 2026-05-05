from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from skill_runtime.api.models import SkillMetadata
from skill_runtime.api.service import RuntimeService
from skill_runtime.collections.store import load_capability_collections
from skill_runtime.evolution.candidates import EvolutionCandidateStore
from skill_runtime.observability.events import RUNTIME_LANE_EVENTS_FILE, read_runtime_lane_events
from skill_runtime.platforms.discovery import collect_platform_inventory
from skill_runtime.retrieval.skill_index import SkillIndex, SkillIndexError


def collect_dashboard_data(root: str | Path, *, event_limit: int = 50) -> dict[str, Any]:
    runtime_root = Path(root).resolve()
    diagnostics: list[str] = []
    skills = _collect_skills(runtime_root, diagnostics)
    operator_summary = _load_exported_operator_summary(runtime_root, diagnostics)
    all_events = list(reversed(read_runtime_lane_events(runtime_root)))
    events = _balanced_recent_events(all_events, per_status_limit=event_limit)
    governance = _collect_governance(runtime_root, diagnostics)
    platform_inventory = collect_platform_inventory(runtime_root)
    capability_collections = load_capability_collections(runtime_root, skills, diagnostics)
    evolution_candidates = EvolutionCandidateStore(runtime_root).list_candidates(limit=50)
    overview = _build_overview(skills, all_events, governance, evolution_candidates)
    return {
        "root": str(runtime_root),
        "overview": overview,
        "skills": skills,
        "events": events,
        "governance": governance,
        "evolution_candidates": evolution_candidates,
        "operator_summary": operator_summary,
        "capability_collections": capability_collections,
        "platform_inventory": platform_inventory,
        "diagnostics": diagnostics,
    }


def collect_dashboard_operator_summary_data(root: str | Path) -> dict[str, Any]:
    runtime_root = Path(root).resolve()
    summary = RuntimeService(runtime_root).operator_summary()
    quality_gates = summary.get("quality_gates") if isinstance(summary.get("quality_gates"), dict) else {}
    return {
        "generated_at": summary.get("generated_at") if isinstance(summary.get("generated_at"), str) else None,
        "active_skills": {"count": _summary_count(summary.get("active_skills"))},
        "staging_candidates": {"count": _summary_count(summary.get("staging_candidates"))},
        "trajectories": {"count": _summary_count(summary.get("trajectories"))},
        "recommended_host_operations": {"count": _summary_count(summary.get("recommended_host_operations"))},
        "quality_gates": {
            "provider_quality": _operator_gate_export(
                quality_gates.get("provider_quality"),
                fallback_label="provider_quality",
            ),
            "utility_search_quality": _operator_gate_export(
                quality_gates.get("utility_search_quality"),
                fallback_label="utility_search_quality",
            ),
            "workflow_search_quality": _operator_gate_export(
                quality_gates.get("workflow_search_quality"),
                fallback_label="workflow_search_quality",
            ),
        },
        "safe_next_steps": _summary_list(summary.get("safe_next_steps")),
        "intentionally_not_automatic": _string_list(summary.get("intentionally_not_automatic")),
        "missing_or_unavailable": _string_list(summary.get("missing_or_unavailable")),
        "non_automatic_explanation": summary.get("non_automatic_explanation")
        if isinstance(summary.get("non_automatic_explanation"), str)
        else None,
    }


def export_dashboard_operator_summary_data(
    root: str | Path,
    *,
    output_path: str | Path | None = None,
) -> tuple[dict[str, Any], Path]:
    runtime_root = Path(root).resolve()
    resolved_output = Path(output_path) if output_path is not None else runtime_root / ".skill_runtime" / "dashboard" / "operator-summary.json"
    if not resolved_output.is_absolute():
        resolved_output = runtime_root / resolved_output
    resolved_output = resolved_output.resolve()
    resolved_output.parent.mkdir(parents=True, exist_ok=True)
    payload = collect_dashboard_operator_summary_data(runtime_root)
    resolved_output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload, resolved_output


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
        project_events = list(reversed(read_runtime_lane_events(project_root)))
        if not project_events:
            continue
        operator_summary = _load_exported_operator_summary(project_root, diagnostics=None)
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
                "operator_summary_available": operator_summary is not None,
                "operator_summary_generated_at": (
                    operator_summary.get("generated_at")
                    if isinstance(operator_summary, dict) and isinstance(operator_summary.get("generated_at"), str)
                    else None
                ),
                "operator_quality_gate_statuses": _operator_quality_gate_statuses(operator_summary),
            }
        )

    events = _balanced_recent_events(
        sorted(events, key=lambda item: str(item.get("timestamp") or ""), reverse=True),
        per_status_limit=event_limit,
    )
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


def _balanced_recent_events(events: list[dict[str, Any]], *, per_status_limit: int) -> list[dict[str, Any]]:
    limit = max(1, int(per_status_limit))
    seen_counts = {"used": 0, "entered": 0, "skipped": 0}
    selected: list[dict[str, Any]] = []
    for event in events:
        status = event.get("runtime_lane_status")
        if status not in seen_counts:
            status = "skipped"
        if seen_counts[status] >= limit:
            continue
        seen_counts[status] += 1
        selected.append(event)
    return sorted(selected, key=lambda item: str(item.get("timestamp") or ""), reverse=True)


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
    authoritative_description = _authoritative_global_skill_description(payload)
    return {
        "skill_name": skill_name,
        "status": status,
        "summary": str(payload.get("summary") or ""),
        "docstring": str(payload.get("docstring") or ""),
        "authoritative_description": authoritative_description,
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
        "skill_surface": _skill_surface(payload),
    }


def _skill_surface(payload: dict[str, Any]) -> str:
    tags = [str(tag).lower() for tag in payload.get("tags") or []]
    summary = str(payload.get("summary") or "").lower()
    docstring = str(payload.get("docstring") or "").lower()
    provenance = payload.get("provenance") if isinstance(payload.get("provenance"), dict) else {}
    if "imported" in tags or provenance.get("type") == "local_skill_import":
        return "workflow"
    if "workflow" in tags or "global codex skill" in summary or "global codex skill" in docstring:
        return "workflow"
    return "basic"


def _authoritative_global_skill_description(payload: dict[str, Any]) -> str:
    global_skill_name = _adapter_global_skill_name(payload)
    if not global_skill_name:
        return ""
    skill_file = Path.home() / ".codex" / "skills" / global_skill_name / "SKILL.md"
    try:
        content = skill_file.read_text(encoding="utf-8-sig")
    except OSError:
        return ""
    return _skill_md_description(content)


def _adapter_global_skill_name(payload: dict[str, Any]) -> str:
    file_path = payload.get("file_path")
    if isinstance(file_path, str) and file_path.strip():
        try:
            content = Path(file_path).read_text(encoding="utf-8-sig")
        except OSError:
            content = ""
        match = re.search(r'global_skill_name\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            return match.group(1).strip()

    docstring = str(payload.get("docstring") or "")
    match = re.search(r"global Codex skill ([A-Za-z0-9_-]+)", docstring)
    return match.group(1).strip() if match else ""


def _skill_md_description(content: str) -> str:
    if content.startswith("---"):
        end = content.find("\n---", 3)
        if end != -1:
            frontmatter = content[3:end]
            for line in frontmatter.splitlines():
                if line.startswith("description:"):
                    return line.split(":", 1)[1].strip().strip('"')
    body = content.split("---", 2)[-1] if content.startswith("---") else content
    paragraphs = [paragraph.strip() for paragraph in body.split("\n\n") if paragraph.strip()]
    for paragraph in paragraphs:
        if not paragraph.startswith("#"):
            return " ".join(paragraph.split())
    return ""


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


def _load_exported_operator_summary(root: Path, diagnostics: list[str] | None) -> dict[str, Any] | None:
    path = root / ".skill_runtime" / "dashboard" / "operator-summary.json"
    if not path.exists():
        return None
    bucket = diagnostics if diagnostics is not None else []
    payload = _read_json(path, bucket)
    return payload if isinstance(payload, dict) else None


def _summary_count(payload: Any) -> int:
    if not isinstance(payload, dict):
        return 0
    value = payload.get("count")
    return value if isinstance(value, int) else 0


def _summary_list(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, list):
        return []
    return [item for item in payload if isinstance(item, dict)]


def _string_list(payload: Any) -> list[str]:
    if not isinstance(payload, list):
        return []
    return [str(item) for item in payload if str(item).strip()]


def _operator_gate_export(payload: Any, *, fallback_label: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {
            "label": fallback_label,
            "status": "unavailable",
            "report_status": None,
            "generated_at": None,
            "summary": None,
            "baseline_comparison": None,
            "reason": "Operator summary gate payload is unavailable.",
        }
    return {
        "label": payload.get("label") if isinstance(payload.get("label"), str) else fallback_label,
        "status": payload.get("status") if isinstance(payload.get("status"), str) else "unavailable",
        "report_status": payload.get("report_status") if isinstance(payload.get("report_status"), str) else None,
        "generated_at": payload.get("generated_at") if isinstance(payload.get("generated_at"), str) else None,
        "summary": payload.get("summary") if isinstance(payload.get("summary"), dict) else None,
        "baseline_comparison": payload.get("baseline_comparison")
        if isinstance(payload.get("baseline_comparison"), dict)
        else None,
        "reason": payload.get("reason") if isinstance(payload.get("reason"), str) else None,
    }


def _operator_quality_gate_statuses(payload: dict[str, Any] | None) -> dict[str, str]:
    if not isinstance(payload, dict):
        return {}
    quality_gates = payload.get("quality_gates")
    if not isinstance(quality_gates, dict):
        return {}
    statuses: dict[str, str] = {}
    for key in ("provider_quality", "utility_search_quality", "workflow_search_quality"):
        gate = quality_gates.get(key)
        if isinstance(gate, dict) and isinstance(gate.get("status"), str):
            statuses[key] = gate["status"]
    return statuses


def _build_overview(
    skills: list[dict[str, Any]],
    events: list[dict[str, Any]],
    governance: dict[str, Any],
    evolution_candidates: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    status_counts = {"active": 0, "staging": 0, "archived": 0, "rejected": 0}
    workflow_active_count = 0
    for skill in skills:
        status = skill["status"]
        if status in status_counts:
            status_counts[status] += 1
        if status == "active" and skill.get("skill_surface") == "workflow":
            workflow_active_count += 1
    event_counts = {"used": 0, "entered": 0, "skipped": 0}
    for event in events:
        status = event.get("runtime_lane_status")
        if status in event_counts:
            event_counts[status] += 1
    duplicate_candidates = governance.get("duplicate_candidates")
    governance_warning_count = len(duplicate_candidates) if isinstance(duplicate_candidates, list) else 0
    proposed_evolution_count = sum(
        1 for candidate in evolution_candidates or [] if candidate.get("status") == "proposed"
    )
    return {
        "active_count": workflow_active_count,
        "staging_count": status_counts["staging"],
        "archive_count": status_counts["archived"],
        "rejected_count": status_counts["rejected"],
        "latest_event_time": events[0].get("timestamp") if events else None,
        "recent_event_counts": event_counts,
        "governance_warning_count": governance_warning_count,
        "evolution_candidate_count": proposed_evolution_count,
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
