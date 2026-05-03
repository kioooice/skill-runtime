from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from skill_runtime.collections.model import CapabilityCollectionDefinition


DEFAULT_COLLECTIONS = [
    CapabilityCollectionDefinition(
        collection_id="text-processing",
        label="文本处理",
        description="合并、清理、替换、Markdown 输出。",
    ),
    CapabilityCollectionDefinition(
        collection_id="structured-conversion",
        label="格式转换",
        description="JSON、CSV 和结构化导入导出。",
    ),
    CapabilityCollectionDefinition(
        collection_id="file-organization",
        label="文件整理",
        description="归档、移动、复制和批量重命名。",
    ),
    CapabilityCollectionDefinition(
        collection_id="project-maintenance",
        label="项目维护",
        description="项目状态、文档、配置和维护类工作流。",
    ),
    CapabilityCollectionDefinition(
        collection_id="runtime-governance",
        label="运行时治理",
        description="蒸馏、审核、候选维护、规则和 provider。",
    ),
]


def load_capability_collections(
    root: str | Path,
    skills: list[dict[str, Any]],
    diagnostics: list[str] | None = None,
) -> list[dict[str, Any]]:
    runtime_root = Path(root).resolve()
    definitions = _load_collection_definitions(runtime_root, diagnostics)
    skills_by_name = {str(skill.get("skill_name")): skill for skill in skills if skill.get("skill_name")}
    results: list[dict[str, Any]] = []

    for definition in definitions:
        skill_names = definition.skill_names or _default_skill_names(definition.collection_id, skills)
        collection_skills = [skills_by_name[name] for name in skill_names if name in skills_by_name]
        missing = [name for name in skill_names if name not in skills_by_name]
        results.append(
            {
                "collection_id": definition.collection_id,
                "label": definition.label,
                "description": definition.description,
                "skill_names": skill_names,
                "skills": collection_skills,
                "missing_skill_names": missing,
                "status_counts": _status_counts(collection_skills),
                "read_only": True,
            }
        )
    return results


def _load_collection_definitions(
    root: Path,
    diagnostics: list[str] | None,
) -> list[CapabilityCollectionDefinition]:
    path = root / "skill_store" / "collections.json"
    if not path.exists():
        return DEFAULT_COLLECTIONS
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        if diagnostics is not None:
            diagnostics.append(f"Could not read capability collections: {exc}")
        return DEFAULT_COLLECTIONS

    raw_collections = payload.get("collections") if isinstance(payload, dict) else None
    if not isinstance(raw_collections, list):
        if diagnostics is not None:
            diagnostics.append("Capability collections file must contain a collections list.")
        return DEFAULT_COLLECTIONS

    definitions: list[CapabilityCollectionDefinition] = []
    for item in raw_collections:
        definition = _definition_from_payload(item, diagnostics)
        if definition is not None:
            definitions.append(definition)
    return definitions or DEFAULT_COLLECTIONS


def _definition_from_payload(
    item: Any,
    diagnostics: list[str] | None,
) -> CapabilityCollectionDefinition | None:
    if not isinstance(item, dict):
        if diagnostics is not None:
            diagnostics.append("Skipped invalid capability collection entry.")
        return None
    collection_id = item.get("collection_id")
    label = item.get("label")
    description = item.get("description")
    skill_names = item.get("skill_names")
    if not isinstance(collection_id, str) or not collection_id.strip():
        if diagnostics is not None:
            diagnostics.append("Skipped capability collection without collection_id.")
        return None
    if not isinstance(label, str) or not label.strip():
        label = collection_id
    if not isinstance(description, str):
        description = ""
    if not isinstance(skill_names, list):
        skill_names = []
    return CapabilityCollectionDefinition(
        collection_id=collection_id.strip(),
        label=label.strip(),
        description=description.strip(),
        skill_names=[str(name) for name in skill_names if isinstance(name, str) and name.strip()],
    )


def _default_skill_names(collection_id: str, skills: list[dict[str, Any]]) -> list[str]:
    return [
        str(skill["skill_name"])
        for skill in skills
        if skill.get("skill_name") and _matches_collection(collection_id, skill)
    ]


def _matches_collection(collection_id: str, skill: dict[str, Any]) -> bool:
    raw_name = str(skill.get("skill_name") or "").lower()
    summary = str(skill.get("summary") or "").lower()
    tags = " ".join(str(tag).lower() for tag in skill.get("tags") or [])
    combined = f"{raw_name} {summary} {tags}"
    raw_hint = f" {raw_name} "
    markers = {
        "text-processing": ("markdown", "merge", "normalize", "replace", "text", "txt", "whitespace"),
        "structured-conversion": ("json", "csv", "convert", "export", "record"),
        "file-organization": ("archive", "copy", "directory", "log", "move", "prefix", "rename"),
        "project-maintenance": ("agent", "config", "docs", "handoff", "maintenance", "project", "state"),
        "runtime-governance": (
            "audit",
            "bridge",
            "demo",
            "distill",
            "fallback",
            "generated",
            "provider",
            "registry",
            "rule",
            "semantic",
            "service",
            "test",
        ),
    }
    collection_markers = markers.get(collection_id, ())
    if collection_id == "runtime-governance":
        return any(marker in raw_hint for marker in collection_markers)
    return any(marker in combined for marker in collection_markers)


def _status_counts(skills: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"active": 0, "staging": 0, "archived": 0, "rejected": 0}
    for skill in skills:
        status = skill.get("status")
        if status in counts:
            counts[status] += 1
    return counts
