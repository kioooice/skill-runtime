from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def current_command() -> str:
    return subprocess.list2cmdline([sys.executable, *sys.argv])


def summarize_baseline_comparison(comparison: dict[str, Any] | None) -> dict[str, int] | None:
    if not isinstance(comparison, dict):
        return None
    summary: dict[str, int] = {}
    for key, value in comparison.items():
        if isinstance(value, list):
            summary[key] = len(value)
    return summary


def build_operator_status_payload(
    *,
    report_status: str,
    summary: dict[str, Any] | None,
    baseline_comparison: dict[str, int] | None,
    command: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "status": report_status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "command": command or current_command(),
        "summary": summary or {},
    }
    if baseline_comparison is not None:
        payload["baseline_comparison"] = baseline_comparison
    return payload


def write_operator_status(root: str | Path, file_name: str, payload: dict[str, Any]) -> Path:
    status_dir = Path(root).resolve() / ".skill_runtime" / "operator_status"
    status_dir.mkdir(parents=True, exist_ok=True)
    output_path = status_dir / file_name
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path
