from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


DEFAULT_OUTPUT_DIR = ROOT / "docs" / "fixtures" / "v0.2-proof-bundle"
DEFAULT_RUNTIME_ROOT = ROOT / ".tmp_v0_2_proof_bundle"
OBSERVED_TASK_PATH = ROOT / "demo" / "maintainer_review_cleanup" / "observed_task.json"
TASK_ID = "v0_2_proof_bundle"
SESSION_ID = "v0_2_proof_bundle"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run the accepted v0.2 maintainer-facing proof bundle path and save stdout/stderr "
            "artifacts without executing the recommended host operation."
        )
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory where stdout/stderr/summary artifacts will be written.",
    )
    parser.add_argument(
        "--runtime-root",
        type=Path,
        default=DEFAULT_RUNTIME_ROOT,
        help="Temporary runtime root used for the proof-bundle command.",
    )
    args = parser.parse_args(argv)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    if args.runtime_root.exists():
        shutil.rmtree(args.runtime_root)

    command = [
        sys.executable,
        "-m",
        "skill_runtime.cli",
        "--root",
        str(args.runtime_root),
        "capture-trajectory",
        "--file",
        str(OBSERVED_TASK_PATH),
        "--task-id",
        TASK_ID,
        "--session-id",
        SESSION_ID,
        "--render-recommendation",
        "text",
    ]

    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            print(result.stderr or result.stdout, file=sys.stderr)
            return result.returncode or 1

        stdout_artifact = args.output_dir / "stdout.capture-trajectory.json"
        stderr_artifact = args.output_dir / "stderr.capture-trajectory.txt"
        summary_artifact = args.output_dir / "summary.capture-trajectory.json"

        stdout_artifact.write_text(result.stdout, encoding="utf-8")
        stderr_artifact.write_text(result.stderr, encoding="utf-8")

        payload = json.loads(result.stdout)
        data = payload.get("data", {}) if isinstance(payload, dict) else {}
        recommended_host_operation = (
            data.get("recommended_host_operation", {})
            if isinstance(data, dict)
            else {}
        )

        staging_dir = args.runtime_root / "skill_store" / "staging"
        active_dir = args.runtime_root / "skill_store" / "active"
        global_dir = args.runtime_root / "global-skills"

        summary = {
            "proof_bundle": "v0.2_maintainer_facing",
            "maintainer_scenario": "maintainer_review_cleanup",
            "command": command,
            "stdout_artifact": _display_path(stdout_artifact),
            "stderr_artifact": _display_path(stderr_artifact),
            "summary_artifact": _display_path(summary_artifact),
            "recommended_next_action": data.get("recommended_next_action"),
            "recommended_reason": data.get("recommended_reason"),
            "recommended_host_operation_tool_name": recommended_host_operation.get("tool_name"),
            "requires_confirmation": recommended_host_operation.get("requires_confirmation"),
            "missing_inputs": _extract_missing_inputs(data),
            "stdout_json_parseable": True,
            "render_recommendation_text_used": True,
            "executed_recommended_host_operation": False,
            "staging_files_created": _contains_files(staging_dir),
            "active_files_created": _contains_files(active_dir),
            "global_skill_files_created": _contains_files(global_dir),
            "no_distill_executed": not _contains_files(staging_dir),
            "no_promote_executed": not _contains_files(active_dir)
            and not _contains_files(global_dir),
            "no_apply_executed": True,
            "governed_boundary_visible": "does not promote" in result.stderr
            or "not automatic promotion" in result.stderr,
        }
        summary_artifact.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0
    finally:
        if args.runtime_root.exists():
            shutil.rmtree(args.runtime_root)


def _contains_files(path: Path) -> bool:
    return path.exists() and any(item.is_file() for item in path.rglob("*"))


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _extract_missing_inputs(data: dict[str, Any]) -> list[str]:
    reuse_decision = data.get("reuse_decision")
    if isinstance(reuse_decision, dict):
        missing_inputs = reuse_decision.get("missing_inputs")
        if isinstance(missing_inputs, list):
            return [str(item) for item in missing_inputs]
    return []


if __name__ == "__main__":
    raise SystemExit(main())
