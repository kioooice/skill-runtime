from __future__ import annotations

from pathlib import Path
from typing import Any

from skill_runtime.platforms.registry import PlatformRoot, known_platforms


def collect_platform_inventory(
    runtime_root: str | Path,
    *,
    platform_roots: list[PlatformRoot] | None = None,
    project_roots: list[str | Path] | None = None,
) -> dict[str, Any]:
    root = Path(runtime_root).resolve()
    diagnostics: list[str] = []
    platforms = list(platform_roots) if platform_roots is not None else known_platforms()
    projects = [_safe_resolve(path, diagnostics) for path in (project_roots or [])]
    resolved_projects = [path for path in projects if path is not None]
    items: list[dict[str, Any]] = []

    for platform in platforms:
        skills_dir = _safe_resolve(platform.skills_dir, diagnostics)
        if skills_dir is None:
            continue
        if not skills_dir.exists():
            diagnostics.append(f"Missing platform skills directory: {skills_dir}")
            continue
        if not skills_dir.is_dir():
            diagnostics.append(f"Platform skills path is not a directory: {skills_dir}")
            continue
        try:
            skill_files = sorted(skills_dir.glob("*/SKILL.md"))
        except OSError as exc:
            diagnostics.append(f"Could not scan platform skills directory {skills_dir}: {exc}")
            continue
        for skill_file in skill_files:
            skill_dir = skill_file.parent
            items.append(
                _inventory_item(
                    root,
                    platform,
                    skills_dir,
                    skill_dir,
                    skill_file,
                    resolved_projects,
                )
            )

    return {
        "items": sorted(items, key=lambda item: (item["platform_id"], item["skill_name"])),
        "diagnostics": diagnostics,
    }


def _inventory_item(
    runtime_root: Path,
    platform: PlatformRoot,
    source_root: Path,
    skill_dir: Path,
    skill_file: Path,
    project_roots: list[Path],
) -> dict[str, Any]:
    ownership = _ownership(runtime_root, source_root, skill_dir, project_roots)
    return {
        "platform_id": platform.platform_id,
        "display_name": platform.display_name,
        "skills_dir": str(source_root),
        "skill_name": skill_dir.name,
        "skill_path": str(skill_dir),
        "skill_file": str(skill_file),
        "ownership": ownership,
        "link_type": _link_type(skill_dir),
        "source_root": str(source_root),
        "is_read_only": True,
    }


def _ownership(runtime_root: Path, source_root: Path, skill_dir: Path, project_roots: list[Path]) -> str:
    if _is_relative_to(skill_dir, runtime_root / "skill_store"):
        return "managed_by_runtime"
    for project_root in project_roots:
        if _is_relative_to(skill_dir, project_root):
            return "project_local"
    return "external"


def _link_type(skill_dir: Path) -> str:
    if skill_dir.is_symlink():
        return "symlink_export"
    return "read_only"


def _safe_resolve(path: str | Path, diagnostics: list[str]) -> Path | None:
    try:
        return Path(path).expanduser().resolve()
    except OSError as exc:
        diagnostics.append(f"Could not resolve {path}: {exc}")
        return None


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True
