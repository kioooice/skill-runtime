from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from skill_runtime.api.service import RuntimeService  # noqa: E402
from skill_runtime.retrieval.skill_index import SkillIndex  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run a live DeepSeek provider loop smoke test in a temporary runtime sandbox."
    )
    parser.add_argument(
        "--keep-sandbox",
        action="store_true",
        help="keep the temporary sandbox and print its path for debugging",
    )
    parser.add_argument(
        "--skill-name",
        default="deepseek_full_loop_provider_smoke",
        help="skill name to use inside the sandbox",
    )
    args = parser.parse_args()

    if not os.environ.get("DEEPSEEK_API_KEY"):
        print("DEEPSEEK_API_KEY is required for the live DeepSeek smoke test.", file=sys.stderr)
        return 2

    if args.keep_sandbox:
        sandbox_root = Path(tempfile.mkdtemp(prefix="skill-runtime-deepseek-smoke-"))
        return _run_smoke(sandbox_root, skill_name=args.skill_name, keep_sandbox=True)

    with tempfile.TemporaryDirectory(prefix="skill-runtime-deepseek-smoke-") as temp_dir:
        return _run_smoke(Path(temp_dir), skill_name=args.skill_name, keep_sandbox=False)


def _run_smoke(sandbox_root: Path, *, skill_name: str, keep_sandbox: bool) -> int:
    _prepare_sandbox(sandbox_root)
    _configure_deepseek_providers()

    source = sandbox_root / "demo" / "input" / "deepseek_provider_source.txt"
    source.write_text("deepseek full loop source", encoding="utf-8")

    service = RuntimeService(sandbox_root)
    try:
        payload = service.distill_and_promote(
            observed_task=_observed_task(),
            skill_name=skill_name,
        )
    except Exception as exc:
        print(
            json.dumps(
                {
                    "status": "failed",
                    "stage": "distill_and_promote",
                    "reason": str(exc),
                    "sandbox_root": str(sandbox_root) if keep_sandbox else None,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1

    summary: dict[str, Any] = {
        "status": "failed",
        "promoted": payload["promoted"],
        "audit_status": payload["audit"]["report"]["status"],
        "semantic_provider": payload["audit"]["report"].get("semantic_provider"),
        "fallback_artifact_exists": bool(payload["distillation"].get("fallback_artifact")),
        "skipped_reason": payload.get("skipped_reason"),
        "sandbox_root": str(sandbox_root) if keep_sandbox else None,
    }

    if not payload["promoted"]:
        summary["semantic_findings"] = payload["audit"]["report"].get("semantic_findings", [])
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 1

    try:
        execute_payload = service.execute(
            skill_name,
            {
                "input_path": "demo/input/deepseek_provider_source.txt",
                "output_path": "demo/output/deepseek_provider_reuse.txt",
                "metadata_path": "demo/output/deepseek_provider_reuse.json",
            },
        )
    except Exception as exc:
        summary["stage"] = "execute_skill"
        summary["reason"] = str(exc)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 1

    output_path = sandbox_root / "demo" / "output" / "deepseek_provider_reuse.txt"
    metadata_path = sandbox_root / "demo" / "output" / "deepseek_provider_reuse.json"
    reuse_text_ok = output_path.exists() and output_path.read_text(encoding="utf-8") == "deepseek full loop source"
    reuse_metadata_exists = metadata_path.exists()
    execute_status = execute_payload["result"].get("status")
    passed = bool(
        execute_status in {"completed", "success"}
        and reuse_text_ok
        and reuse_metadata_exists
    )

    summary.update(
        {
            "status": "passed" if passed else "failed",
            "execute_status": execute_status,
            "reuse_text_ok": reuse_text_ok,
            "reuse_metadata_exists": reuse_metadata_exists,
        }
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if passed else 1


def _prepare_sandbox(sandbox_root: Path) -> None:
    sandbox_root.mkdir(parents=True, exist_ok=True)
    shutil.copytree(ROOT / "demo", sandbox_root / "demo")
    shutil.copytree(
        ROOT / "skill_store",
        sandbox_root / "skill_store",
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    shutil.copytree(ROOT / "trajectories", sandbox_root / "trajectories")
    (sandbox_root / "audits").mkdir(parents=True, exist_ok=True)
    (sandbox_root / "observed_tasks").mkdir(parents=True, exist_ok=True)

    for metadata_path in (sandbox_root / "skill_store").rglob("*.metadata.json"):
        payload = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
        payload["file_path"] = str(
            metadata_path.with_name(metadata_path.name.replace(".metadata.json", ".py")).resolve()
        )
        metadata_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    SkillIndex(sandbox_root / "skill_store" / "index.json").rebuild_from_directory(
        sandbox_root / "skill_store" / "active"
    )


def _configure_deepseek_providers() -> None:
    os.environ["SKILL_RUNTIME_FALLBACK_PROVIDER_CMD"] = json.dumps(
        [sys.executable, str(ROOT / "examples" / "providers" / "deepseek_fallback_provider.py")]
    )
    os.environ["SKILL_RUNTIME_SEMANTIC_PROVIDER_CMD"] = json.dumps(
        [sys.executable, str(ROOT / "examples" / "providers" / "deepseek_semantic_review_provider.py")]
    )
    os.environ.setdefault("DEEPSEEK_MODEL", "deepseek-v4-flash")
    os.environ.setdefault("DEEPSEEK_REPAIR_ATTEMPTS", "1")
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")


def _observed_task() -> dict[str, Any]:
    return {
        "task": "Mirror one text file and write a metadata sidecar with DeepSeek provider.",
        "actions": [
            {
                "tool": "copy_file",
                "input": {
                    "source_path": "demo/input/deepseek_provider_source.txt",
                    "destination_path": "demo/output/deepseek_provider_result.txt",
                },
                "result": "Mirrored source text.",
            },
            {
                "tool": "write_json",
                "input": {"metadata_path": "demo/output/deepseek_provider_result.json"},
                "result": "Wrote metadata sidecar.",
            },
        ],
        "outputs": [
            "demo/output/deepseek_provider_result.txt",
            "demo/output/deepseek_provider_result.json",
        ],
    }


if __name__ == "__main__":
    raise SystemExit(main())
