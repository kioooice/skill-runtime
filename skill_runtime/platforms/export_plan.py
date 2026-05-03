from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from skill_runtime.platforms.registry import PlatformRoot, known_platforms


def plan_platform_export(
    runtime_root: str | Path,
    skill_name: str,
    platform_id: str,
    *,
    platform_roots: list[PlatformRoot] | None = None,
    target_dir: str | Path | None = None,
    force_copy: bool = False,
) -> dict[str, Any]:
    root = Path(runtime_root).resolve()
    skill_metadata = _load_active_skill_metadata(root, skill_name)
    platform = _resolve_platform(platform_id, platform_roots, target_dir)
    warnings: list[str] = []

    if platform is None:
        return _blocked_plan(root, skill_name, platform_id, "platform_not_found", ["Platform is not registered."])

    source_path = _source_path(root, skill_metadata)
    target_root = Path(platform.skills_dir).expanduser().resolve()
    target_path = target_root / skill_name
    link_type = _planned_link_type(force_copy=force_copy)
    conflict = _target_conflict(target_path)

    if skill_metadata is None:
        warnings.append("Only active skills can be exported to platform directories.")
        return _plan_payload(
            root,
            skill_name,
            platform,
            source_path,
            target_root,
            target_path,
            link_type,
            "skill_not_active",
            warnings,
            eligible=False,
        )

    if not target_root.exists():
        warnings.append("Target platform skills directory does not exist; this preview will not create it.")

    if conflict in {"existing_directory", "existing_file"}:
        warnings.append("Target path already exists as a real filesystem object and will not be overwritten.")
        eligible = False
    else:
        eligible = True

    if link_type == "copied_export":
        warnings.append("Copy fallback is planned; no files are copied by this preview command.")
    else:
        warnings.append("Symlink export is planned; no link is created by this preview command.")

    return _plan_payload(
        root,
        skill_name,
        platform,
        source_path,
        target_root,
        target_path,
        link_type,
        conflict,
        warnings,
        eligible=eligible,
    )


def _load_active_skill_metadata(root: Path, skill_name: str) -> dict[str, Any] | None:
    metadata_path = root / "skill_store" / "active" / f"{skill_name}.metadata.json"
    if not metadata_path.exists():
        return None
    try:
        payload = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
    except (json.JSONDecodeError, OSError):
        return None
    return payload if isinstance(payload, dict) else None


def _resolve_platform(
    platform_id: str,
    platform_roots: list[PlatformRoot] | None,
    target_dir: str | Path | None,
) -> PlatformRoot | None:
    if target_dir is not None:
        return PlatformRoot(platform_id=platform_id, display_name=platform_id, skills_dir=Path(target_dir))
    platforms = platform_roots if platform_roots is not None else known_platforms()
    for platform in platforms:
        if platform.platform_id == platform_id:
            return platform
    return None


def _source_path(root: Path, metadata: dict[str, Any] | None) -> str | None:
    if metadata is None:
        return None
    raw_file_path = metadata.get("file_path")
    if isinstance(raw_file_path, str) and raw_file_path.strip():
        return str(Path(raw_file_path).resolve())
    raw_skill_name = metadata.get("skill_name")
    if isinstance(raw_skill_name, str) and raw_skill_name.strip():
        return str((root / "skill_store" / "active" / f"{raw_skill_name}.py").resolve())
    return None


def _planned_link_type(*, force_copy: bool) -> str:
    if force_copy or os.name == "nt":
        return "copied_export"
    return "symlink_export"


def _target_conflict(target_path: Path) -> str:
    if target_path.is_symlink():
        return "existing_symlink"
    if target_path.is_dir():
        return "existing_directory"
    if target_path.exists():
        return "existing_file"
    return "none"


def _blocked_plan(root: Path, skill_name: str, platform_id: str, conflict: str, warnings: list[str]) -> dict[str, Any]:
    return {
        "runtime_root": str(root),
        "skill_name": skill_name,
        "platform_id": platform_id,
        "display_name": platform_id,
        "source_path": None,
        "target_root": None,
        "target_path": None,
        "link_type": "copied_export" if os.name == "nt" else "symlink_export",
        "conflict": conflict,
        "requires_confirmation": True,
        "eligible": False,
        "read_only": True,
        "warnings": warnings,
    }


def _plan_payload(
    root: Path,
    skill_name: str,
    platform: PlatformRoot,
    source_path: str | None,
    target_root: Path,
    target_path: Path,
    link_type: str,
    conflict: str,
    warnings: list[str],
    *,
    eligible: bool,
) -> dict[str, Any]:
    return {
        "runtime_root": str(root),
        "skill_name": skill_name,
        "platform_id": platform.platform_id,
        "display_name": platform.display_name,
        "source_path": source_path,
        "target_root": str(target_root),
        "target_path": str(target_path),
        "link_type": link_type,
        "conflict": conflict,
        "requires_confirmation": True,
        "eligible": eligible,
        "read_only": True,
        "warnings": warnings,
    }
