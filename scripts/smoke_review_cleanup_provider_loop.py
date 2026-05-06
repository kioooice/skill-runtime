from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from skill_runtime.api.service import RuntimeService  # noqa: E402
from skill_runtime.retrieval.skill_index import SkillIndex  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run a local review-cleanup provider loop smoke test in a temporary runtime sandbox."
    )
    parser.add_argument(
        "--keep-sandbox",
        action="store_true",
        help="Keep the sandbox under .tmp_review_cleanup_provider_loop for inspection.",
    )
    parser.add_argument(
        "--skill-name",
        default="maintainer_review_cleanup_generated",
        help="Skill name to generate inside the sandbox.",
    )
    args = parser.parse_args()

    sandbox_root = ROOT / ".tmp_review_cleanup_provider_loop"
    if sandbox_root.exists():
        shutil.rmtree(sandbox_root)

    try:
        _run_smoke(sandbox_root, skill_name=args.skill_name)
    except Exception as exc:
        print(
            json.dumps(
                {
                    "status": "failed",
                    "stage": "distill_and_promote",
                    "reason": str(exc),
                    "sandbox_root": str(sandbox_root),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1

    if not args.keep_sandbox and sandbox_root.exists():
        shutil.rmtree(sandbox_root)
    return 0


def _run_smoke(sandbox_root: Path, *, skill_name: str) -> None:
    _prepare_sandbox(sandbox_root)
    _configure_demo_providers()

    service = RuntimeService(sandbox_root)
    payload = service.distill_and_promote(
        observed_task_path=sandbox_root / "demo" / "maintainer_review_cleanup" / "observed_task.json",
        skill_name=skill_name,
    )

    execute_payload = None
    if payload.get("promoted"):
        execute_payload = service.execute(
            skill_name,
            {
                "input_path": "demo/maintainer_review_cleanup/review_comments.json",
                "output_path": "demo/maintainer_review_cleanup/reused_cleanup_plan.md",
                "metadata_path": "demo/maintainer_review_cleanup/reused_cleanup_plan.json",
            },
        )

    result = {
        "status": "passed" if payload.get("promoted") else "failed",
        "sandbox_root": str(sandbox_root),
        "promoted": payload.get("promoted"),
        "skipped_reason": payload.get("skipped_reason"),
        "audit_status": payload.get("audit", {}).get("report", {}).get("status"),
        "semantic_provider": payload.get("audit", {}).get("report", {}).get("semantic_provider"),
        "staging_file": payload.get("distillation", {}).get("staging_file"),
        "metadata_file": payload.get("distillation", {}).get("metadata_file"),
        "fallback_artifact": payload.get("distillation", {}).get("fallback_artifact"),
        "active_skill_file": str((sandbox_root / "skill_store" / "active" / f"{skill_name}.py").resolve()),
        "recommended_host_operation": payload.get("recommended_host_operation"),
        "execute_status": execute_payload.get("result", {}).get("status") if execute_payload else None,
        "reuse_output_path": str((sandbox_root / "demo" / "maintainer_review_cleanup" / "reused_cleanup_plan.md").resolve()),
        "reuse_metadata_path": str(
            (sandbox_root / "demo" / "maintainer_review_cleanup" / "reused_cleanup_plan.json").resolve()
        ),
        "reuse_output_exists": (sandbox_root / "demo" / "maintainer_review_cleanup" / "reused_cleanup_plan.md").exists(),
        "reuse_metadata_exists": (sandbox_root / "demo" / "maintainer_review_cleanup" / "reused_cleanup_plan.json").exists(),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


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


def _configure_demo_providers() -> None:
    os.environ["SKILL_RUNTIME_FALLBACK_PROVIDER_CMD"] = json.dumps(
        [sys.executable, str(ROOT / "examples" / "providers" / "review_cleanup_fallback_provider.py")]
    )
    os.environ["SKILL_RUNTIME_SEMANTIC_PROVIDER_CMD"] = json.dumps(
        [sys.executable, str(ROOT / "examples" / "providers" / "pass_semantic_review_provider.py")]
    )
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
