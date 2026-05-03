from __future__ import annotations

import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class SkillImportError(ValueError):
    def __init__(self, message: str, code: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


def import_local_skill_to_staging(runtime_root: str | Path, source: str | Path) -> dict[str, Any]:
    root = Path(runtime_root).resolve()
    source_dir = Path(source).expanduser().resolve()
    if not source_dir.exists() or not source_dir.is_dir():
        raise SkillImportError("source skill directory not found", "SOURCE_NOT_FOUND", {"source": str(source_dir)})

    skill_file = source_dir / "SKILL.md"
    if not skill_file.exists():
        raise SkillImportError("source directory must contain SKILL.md", "SKILL_MD_NOT_FOUND", {"source": str(source_dir)})

    skill_text = skill_file.read_text(encoding="utf-8-sig")
    frontmatter = _parse_frontmatter(skill_text)
    skill_name = _safe_skill_name(str(frontmatter.get("name") or source_dir.name))
    summary = str(frontmatter.get("description") or _first_markdown_heading(skill_text) or f"Imported skill {skill_name}.")
    content_hash = _directory_hash(source_dir)
    imported_dir = root / "skill_store" / "staging" / "imported" / skill_name
    metadata_path = root / "skill_store" / "staging" / f"{skill_name}.metadata.json"

    if imported_dir.exists():
        shutil.rmtree(imported_dir)
    imported_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source_dir, imported_dir, ignore=shutil.ignore_patterns("__pycache__"))

    metadata = {
        "skill_name": skill_name,
        "file_path": str((imported_dir / "SKILL.md").resolve()),
        "summary": summary,
        "docstring": summary,
        "input_schema": {},
        "output_schema": {},
        "source_trajectory_ids": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_used_at": None,
        "usage_count": 0,
        "status": "staging",
        "audit_score": None,
        "audit_status": "requires_review",
        "import_source": str(source_dir),
        "imported_at": datetime.now(timezone.utc).isoformat(),
        "content_hash": content_hash,
        "provenance": {
            "type": "local_skill_import",
            "source": str(source_dir),
            "content_hash": content_hash,
        },
        "tags": ["imported", "external", "requires_review"],
    }
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "skill_name": skill_name,
        "status": "staging",
        "audit_status": "requires_review",
        "source_path": str(source_dir),
        "staging_path": str(imported_dir.resolve()),
        "metadata_path": str(metadata_path.resolve()),
        "content_hash": content_hash,
        "read_only_source": True,
    }


def _parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    payload: dict[str, str] = {}
    for line in text[3:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        payload[key.strip()] = value.strip().strip("\"'")
    return payload


def _first_markdown_heading(text: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
    return None


def _safe_skill_name(raw: str) -> str:
    value = raw.strip().lower().replace(" ", "-")
    value = re.sub(r"[^a-z0-9_.-]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-._")
    if not value:
        raise SkillImportError("skill name is empty after normalization", "INVALID_SKILL_NAME")
    return value


def _directory_hash(source_dir: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in source_dir.rglob("*") if item.is_file()):
        relative = path.relative_to(source_dir).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()
