from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PlatformRoot:
    platform_id: str
    display_name: str
    skills_dir: Path


def known_platforms(home: str | Path | None = None) -> list[PlatformRoot]:
    home_path = Path(home).expanduser().resolve() if home is not None else Path.home().resolve()
    return [
        PlatformRoot("codex", "Codex", home_path / ".codex" / "skills"),
        PlatformRoot("claude-code", "Claude Code", home_path / ".claude" / "skills"),
        PlatformRoot("cursor", "Cursor", home_path / ".cursor" / "skills"),
        PlatformRoot("gemini-cli", "Gemini CLI", home_path / ".gemini" / "skills"),
        PlatformRoot("agents-shared", "Shared Agents", home_path / ".agents" / "skills"),
    ]
