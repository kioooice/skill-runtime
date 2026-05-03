from __future__ import annotations

import os
from pathlib import Path
from typing import Any


DEFAULT_CODEX_HOME = Path(r"C:\Users\Administrator\.codex")


def run_global_skill_adapter(
    tools: Any,
    *,
    runtime_skill_name: str,
    global_skill_name: str,
    output_path: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    if not output_path:
        raise ValueError("Missing required input: output_path")

    codex_home = Path(os.environ.get("CODEX_HOME") or DEFAULT_CODEX_HOME)
    global_skill_path = codex_home / "skills" / global_skill_name
    next_action = f"Use the global Codex skill ${global_skill_name}; this runtime skill is only a thin adapter."
    report = {
        "status": "completed",
        "skill_name": runtime_skill_name,
        "adapter_role": "global_codex_skill_adapter",
        "global_skill_name": global_skill_name,
        "global_skill_path": str(global_skill_path),
        "source_role": "authoritative_global_skill",
        "received_args": {key: value for key, value in kwargs.items() if key != "output_path"},
        "next_action": next_action,
    }
    tools.write_json(output_path, report, ensure_ascii=False, indent=2)
    return {
        "status": "completed",
        "skill_name": runtime_skill_name,
        "summary": next_action,
        "artifacts": [output_path],
        "steps_executed": 1,
        "next_action": next_action,
        "report": report,
    }
