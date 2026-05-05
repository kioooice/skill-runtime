from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import shutil
import sys
import tempfile
import threading
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from skill_runtime.api.service import RuntimeService, RuntimeServiceError  # noqa: E402
from skill_runtime.distill.fallback.service import FallbackService  # noqa: E402
from skill_runtime.execution.runtime_tools import RuntimeTools  # noqa: E402
from skill_runtime.memory.trajectory_store import TrajectoryStore  # noqa: E402
from skill_runtime.retrieval.skill_index import SkillIndex  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate provider-backed governed learning quality across local fixtures."
    )
    parser.add_argument(
        "--output",
        help="Optional path to write the full JSON report. The report is still printed to stdout.",
    )
    parser.add_argument(
        "--baseline",
        help="Optional machine-readable baseline JSON path to compare against the evaluation report.",
    )
    parser.add_argument(
        "--fail-on-regression",
        action="store_true",
        help="Return non-zero when baseline comparison finds a regression, unexpected failure, or missing fixture.",
    )
    args = parser.parse_args()

    fixtures = [
        _run_demo_local_success_fixture(),
        _run_mock_template_execute_failure_fixture(),
        _run_fake_deepseek_repair_success_fixture(),
        _run_fake_deepseek_semantic_block_fixture(),
        _run_fake_deepseek_generation_failure_fixture(),
        _run_review_cleanup_provider_quality_fixture(),
        _run_review_cleanup_demo_provider_success_fixture(),
        _run_runtime_service_distill_demo_provider_fixture(),
    ]
    passed = sum(1 for item in fixtures if item["execution_smoke_status"] == "passed")
    failed = sum(1 for item in fixtures if item["failure_reason"])
    payload = {
        "status": "ok",
        "fixtures": fixtures,
        "summary": {
            "fixture_count": len(fixtures),
            "execution_smoke_passed": passed,
            "fixtures_with_failures": failed,
        },
    }
    exit_code = 0
    if args.baseline:
        baseline_path = Path(args.baseline)
        baseline_payload = json.loads(baseline_path.read_text(encoding="utf-8-sig"))
        comparison = _compare_to_baseline(fixtures, baseline_payload)
        payload["baseline_comparison"] = comparison
        if args.fail_on_regression and _has_blocking_baseline_regression(comparison):
            exit_code = 1
    rendered = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")
    print(rendered)
    return exit_code


def _compare_to_baseline(fixtures: list[dict[str, Any]], baseline_payload: dict[str, Any]) -> dict[str, Any]:
    expected_fixtures = baseline_payload.get("fixtures")
    if not isinstance(expected_fixtures, list):
        raise ValueError("Baseline JSON must contain a fixtures list.")

    actual_by_name = {
        item["fixture_name"]: item
        for item in fixtures
        if isinstance(item.get("fixture_name"), str) and item.get("fixture_name")
    }
    expected_by_name = {
        item["fixture_name"]: item
        for item in expected_fixtures
        if isinstance(item, dict) and isinstance(item.get("fixture_name"), str) and item.get("fixture_name")
    }

    comparison: dict[str, Any] = {
        "matched": [],
        "regressions": [],
        "improvements": [],
        "unexpected_failures": [],
        "unexpected_passes": [],
        "missing_fixtures": [],
        "extra_fixtures": [],
    }

    for fixture_name, expected in expected_by_name.items():
        actual = actual_by_name.get(fixture_name)
        if actual is None:
            comparison["missing_fixtures"].append(fixture_name)
            continue

        actual_snapshot = _baseline_actual_snapshot(actual)
        mismatches = _baseline_mismatches(expected, actual_snapshot)
        if not mismatches:
            comparison["matched"].append(fixture_name)
            continue

        actual_failed = actual_snapshot["actual_failure"]
        expected_failed = bool(expected.get("expected_failure"))
        if actual_failed and not expected_failed:
            comparison["unexpected_failures"].append(_baseline_issue(fixture_name, mismatches, actual_snapshot))
        elif expected_failed and not actual_failed:
            comparison["unexpected_passes"].append(_baseline_issue(fixture_name, mismatches, actual_snapshot))
        elif _is_improvement(expected, actual_snapshot):
            comparison["improvements"].append(_baseline_issue(fixture_name, mismatches, actual_snapshot))
        else:
            comparison["regressions"].append(_baseline_issue(fixture_name, mismatches, actual_snapshot))

    for fixture_name in sorted(set(actual_by_name) - set(expected_by_name)):
        comparison["extra_fixtures"].append(fixture_name)

    for key in comparison:
        comparison[key] = sorted(comparison[key], key=_comparison_sort_key)
    return comparison


def _baseline_actual_snapshot(actual: dict[str, Any]) -> dict[str, Any]:
    return {
        "lifecycle_mode": actual.get("lifecycle_mode"),
        "loop_stage": actual.get("loop_stage"),
        "provider": _actual_provider(actual),
        "actual_failure": bool(actual.get("failure_reason")),
    }


def _actual_provider(actual: dict[str, Any]) -> str | None:
    provider = actual.get("generated_candidate_provider")
    if isinstance(provider, str) and provider:
        return provider
    provider_used = actual.get("provider_used")
    if isinstance(provider_used, dict):
        fallback = provider_used.get("fallback")
        if isinstance(fallback, str) and fallback:
            return fallback
    return None


def _baseline_mismatches(expected: dict[str, Any], actual_snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    checks = [
        ("lifecycle_mode", "lifecycle_mode"),
        ("expected_loop_stage", "loop_stage"),
        ("expected_provider", "provider"),
        ("expected_failure", "actual_failure"),
    ]
    mismatches = []
    for expected_key, actual_key in checks:
        expected_value = expected.get(expected_key)
        actual_value = actual_snapshot.get(actual_key)
        if expected_value != actual_value:
            mismatches.append(
                {
                    "field": expected_key,
                    "expected": expected_value,
                    "actual": actual_value,
                }
            )
    return mismatches


def _is_improvement(expected: dict[str, Any], actual_snapshot: dict[str, Any]) -> bool:
    if bool(expected.get("expected_failure")) and not actual_snapshot["actual_failure"]:
        return True
    expected_rank = _loop_stage_rank(expected.get("expected_loop_stage"))
    actual_rank = _loop_stage_rank(actual_snapshot.get("loop_stage"))
    return expected_rank is not None and actual_rank is not None and actual_rank > expected_rank


def _loop_stage_rank(stage: Any) -> int | None:
    order = {
        "generation_failed": 0,
        "audit_failed": 1,
        "execution_failed": 2,
        "execution_passed": 3,
    }
    return order.get(stage) if isinstance(stage, str) else None


def _baseline_issue(
    fixture_name: str,
    mismatches: list[dict[str, Any]],
    actual_snapshot: dict[str, Any],
) -> dict[str, Any]:
    return {
        "fixture_name": fixture_name,
        "mismatches": mismatches,
        "actual": actual_snapshot,
    }


def _comparison_sort_key(item: Any) -> str:
    if isinstance(item, dict):
        return str(item.get("fixture_name", ""))
    return str(item)


def _has_blocking_baseline_regression(comparison: dict[str, Any]) -> bool:
    return bool(
        comparison.get("regressions")
        or comparison.get("unexpected_failures")
        or comparison.get("missing_fixtures")
    )


def _run_demo_local_success_fixture() -> dict[str, Any]:
    return _evaluate_fixture(
        fixture_name="demo_local_success",
        lifecycle_mode="manual_provider_loop",
        configured_providers={
            "fallback": "local_copy_metadata_fallback_provider",
            "semantic": "local_pass_semantic_review_provider",
        },
        env_updates={
            "SKILL_RUNTIME_FALLBACK_PROVIDER_CMD": json.dumps(
                [sys.executable, str(ROOT / "examples" / "providers" / "copy_metadata_fallback_provider.py")]
            ),
            "SKILL_RUNTIME_SEMANTIC_PROVIDER_CMD": json.dumps(
                [sys.executable, str(ROOT / "examples" / "providers" / "pass_semantic_review_provider.py")]
            ),
        },
    )


def _run_mock_template_execute_failure_fixture() -> dict[str, Any]:
    return _evaluate_fixture(
        fixture_name="mock_template_execute_failure",
        lifecycle_mode="manual_provider_loop",
        configured_providers={
            "fallback": "mock_fallback_provider",
            "semantic": "mock_semantic_review_provider",
        },
        env_updates={
            "SKILL_RUNTIME_FALLBACK_PROVIDER_CMD": None,
            "SKILL_RUNTIME_SEMANTIC_PROVIDER_CMD": None,
        },
    )


def _run_fake_deepseek_repair_success_fixture() -> dict[str, Any]:
    invalid_candidate = _deepseek_invalid_signature_candidate()
    repaired_candidate = _deepseek_valid_copy_metadata_candidate()
    semantic_pass = {
        "provider_name": "deepseek_semantic_review_provider",
        "summary": "No blocking issue.",
        "issues": [],
    }
    with _fake_deepseek_server([invalid_candidate, repaired_candidate, semantic_pass]) as server:
        return _evaluate_fixture(
            fixture_name="fake_deepseek_repair_success",
            lifecycle_mode="manual_provider_loop",
            configured_providers={
                "fallback": "deepseek_fallback_provider",
                "semantic": "deepseek_semantic_review_provider",
            },
            env_updates={
                "DEEPSEEK_API_KEY": "test-deepseek-key",
                "DEEPSEEK_API_BASE": server.url,
                "DEEPSEEK_MODEL": "deepseek-v4-flash",
                "DEEPSEEK_REPAIR_ATTEMPTS": "1",
                "SKILL_RUNTIME_FALLBACK_PROVIDER_CMD": json.dumps(
                    [sys.executable, str(ROOT / "examples" / "providers" / "deepseek_fallback_provider.py")]
                ),
                "SKILL_RUNTIME_SEMANTIC_PROVIDER_CMD": json.dumps(
                    [sys.executable, str(ROOT / "examples" / "providers" / "deepseek_semantic_review_provider.py")]
                ),
            },
        )


def _run_fake_deepseek_semantic_block_fixture() -> dict[str, Any]:
    semantic_block = {
        "provider_name": "deepseek_semantic_review_provider",
        "summary": "Blocking semantic issue.",
        "issues": [
            {
                "rule_id": "provider-risk",
                "severity": "high",
                "message": "External semantic provider found an unacceptable workflow risk.",
            }
        ],
    }
    with _fake_deepseek_server([_deepseek_valid_copy_metadata_candidate(), semantic_block]) as server:
        return _evaluate_fixture(
            fixture_name="fake_deepseek_semantic_block",
            lifecycle_mode="manual_provider_loop",
            configured_providers={
                "fallback": "deepseek_fallback_provider",
                "semantic": "deepseek_semantic_review_provider",
            },
            env_updates={
                "DEEPSEEK_API_KEY": "test-deepseek-key",
                "DEEPSEEK_API_BASE": server.url,
                "DEEPSEEK_MODEL": "deepseek-v4-flash",
                "DEEPSEEK_REPAIR_ATTEMPTS": "1",
                "SKILL_RUNTIME_FALLBACK_PROVIDER_CMD": json.dumps(
                    [sys.executable, str(ROOT / "examples" / "providers" / "deepseek_fallback_provider.py")]
                ),
                "SKILL_RUNTIME_SEMANTIC_PROVIDER_CMD": json.dumps(
                    [sys.executable, str(ROOT / "examples" / "providers" / "deepseek_semantic_review_provider.py")]
                ),
            },
        )


def _run_fake_deepseek_generation_failure_fixture() -> dict[str, Any]:
    with _fake_deepseek_server(_deepseek_low_quality_candidate()) as server:
        return _evaluate_fixture(
            fixture_name="fake_deepseek_generation_failure",
            lifecycle_mode="manual_provider_loop",
            configured_providers={
                "fallback": "deepseek_fallback_provider",
                "semantic": "deepseek_semantic_review_provider",
            },
            env_updates={
                "DEEPSEEK_API_KEY": "test-deepseek-key",
                "DEEPSEEK_API_BASE": server.url,
                "DEEPSEEK_MODEL": "deepseek-v4-flash",
                "DEEPSEEK_REPAIR_ATTEMPTS": "0",
                "SKILL_RUNTIME_FALLBACK_PROVIDER_CMD": json.dumps(
                    [sys.executable, str(ROOT / "examples" / "providers" / "deepseek_fallback_provider.py")]
                ),
                "SKILL_RUNTIME_SEMANTIC_PROVIDER_CMD": json.dumps(
                    [sys.executable, str(ROOT / "examples" / "providers" / "deepseek_semantic_review_provider.py")]
                ),
            },
        )


def _run_review_cleanup_provider_quality_fixture() -> dict[str, Any]:
    observed_task = json.loads(
        (ROOT / "demo" / "maintainer_review_cleanup" / "observed_task.json").read_text(encoding="utf-8")
    )
    return _evaluate_fixture(
        fixture_name="review_cleanup_provider_quality",
        lifecycle_mode="manual_provider_loop",
        configured_providers={
            "fallback": "mock_fallback_provider",
            "semantic": "mock_semantic_review_provider",
        },
        env_updates={
            "SKILL_RUNTIME_FALLBACK_PROVIDER_CMD": None,
            "SKILL_RUNTIME_SEMANTIC_PROVIDER_CMD": None,
        },
        observed_task=observed_task,
        execution_args={
            "input_path": "demo/maintainer_review_cleanup/review_comments.json",
            "output_path": "demo/maintainer_review_cleanup/generated_cleanup_plan.md",
            "metadata_path": "demo/maintainer_review_cleanup/generated_cleanup_plan.json",
        },
        seed_callback=_seed_review_cleanup_fixture,
    )


def _run_review_cleanup_demo_provider_success_fixture() -> dict[str, Any]:
    observed_task = json.loads(
        (ROOT / "demo" / "maintainer_review_cleanup" / "observed_task.json").read_text(encoding="utf-8")
    )
    return _evaluate_fixture(
        fixture_name="review_cleanup_demo_provider_success",
        lifecycle_mode="manual_provider_loop",
        configured_providers={
            "fallback": "local_review_cleanup_fallback_provider",
            "semantic": "local_pass_semantic_review_provider",
        },
        env_updates={
            "SKILL_RUNTIME_FALLBACK_PROVIDER_CMD": json.dumps(
                [sys.executable, str(ROOT / "examples" / "providers" / "review_cleanup_fallback_provider.py")]
            ),
            "SKILL_RUNTIME_SEMANTIC_PROVIDER_CMD": json.dumps(
                [sys.executable, str(ROOT / "examples" / "providers" / "pass_semantic_review_provider.py")]
            ),
        },
        observed_task=observed_task,
        execution_args={
            "input_path": "demo/maintainer_review_cleanup/review_comments.json",
            "output_path": "demo/maintainer_review_cleanup/generated_cleanup_plan.md",
            "metadata_path": "demo/maintainer_review_cleanup/generated_cleanup_plan.json",
        },
        seed_callback=_seed_review_cleanup_fixture,
        manual_generation_config={
            "summary": "Read review comments and write a grouped maintainer cleanup plan.",
            "docstring": (
                "功能描述:\n"
                "    Read review comments and write a grouped maintainer cleanup plan.\n\n"
                "输入参数:\n"
                "    - input_path: str\n"
                "    - output_path: str\n"
                "    - metadata_path: str\n\n"
                "输出结果:\n"
                "    - status: str\n"
                "    - artifacts: list[str]\n"
                "    - steps_executed: int"
            ),
            "input_schema": {
                "input_path": "str",
                "output_path": "str",
                "metadata_path": "str",
            },
        },
    )


def _run_runtime_service_distill_demo_provider_fixture() -> dict[str, Any]:
    return _evaluate_fixture(
        fixture_name="runtime_service_distill_demo_provider",
        lifecycle_mode="runtime_service_distill",
        configured_providers={
            "fallback": "local_copy_metadata_fallback_provider",
            "semantic": "local_pass_semantic_review_provider",
        },
        env_updates={
            "SKILL_RUNTIME_FALLBACK_PROVIDER_CMD": json.dumps(
                [sys.executable, str(ROOT / "examples" / "providers" / "copy_metadata_fallback_provider.py")]
            ),
            "SKILL_RUNTIME_SEMANTIC_PROVIDER_CMD": json.dumps(
                [sys.executable, str(ROOT / "examples" / "providers" / "pass_semantic_review_provider.py")]
            ),
        },
        use_runtime_service_distill=True,
    )


def _evaluate_fixture(
    *,
    fixture_name: str,
    lifecycle_mode: str,
    configured_providers: dict[str, str | None],
    env_updates: dict[str, str | None],
    observed_task: dict[str, Any] | None = None,
    execution_args: dict[str, str] | None = None,
    seed_callback=None,
    use_runtime_service_distill: bool = False,
    manual_generation_config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result = {
        "fixture_name": fixture_name,
        "lifecycle_mode": lifecycle_mode,
        "provider_used": {
            "fallback": configured_providers.get("fallback"),
            "semantic": configured_providers.get("semantic"),
        },
        "generated_candidate_status": "failed",
        "audit_status": "skipped",
        "repair_attempted": False,
        "repair_status": "not_attempted",
        "execution_smoke_status": "skipped",
        "loop_stage": "generation_failed",
        "failure_reason": None,
        "recommended_next_action": None,
        "staging_file": None,
        "generated_candidate_provider": None,
        "inferred_or_used_input_schema": None,
        "declared_input_schema_keys": [],
        "execution_arg_keys": [],
        "candidate_kwargs_keys": [],
        "schema_execution_arg_mismatch": {
            "schema_not_in_execution_args": [],
            "execution_args_not_in_schema": [],
            "candidate_kwargs_not_in_schema": [],
        },
        "expected_artifacts": [],
        "produced_artifacts": [],
        "missing_artifacts": [],
    }

    with tempfile.TemporaryDirectory(prefix=f"skill-runtime-provider-quality-{fixture_name}-") as temp_dir:
        sandbox_root = Path(temp_dir)
        _prepare_sandbox(sandbox_root)
        if seed_callback is None:
            _seed_execution_fixture(sandbox_root)
        else:
            seed_callback(sandbox_root)
        service = RuntimeService(sandbox_root)
        selected_observed_task = observed_task or _observed_task()
        selected_execution_args = execution_args or _execution_args()
        result["expected_artifacts"] = _expected_artifacts(selected_execution_args)
        result["execution_arg_keys"] = sorted(selected_execution_args.keys())

        with _patched_env(env_updates):
            try:
                capture_result = service.capture_trajectory(
                    observed_task=selected_observed_task,
                    task_id=f"{fixture_name}_task",
                    session_id="provider_quality_eval",
                )
                if use_runtime_service_distill:
                    distill_result = service.distill(
                        capture_result["trajectory_path"],
                        skill_name=f"{fixture_name}_candidate",
                    )
                else:
                    distill_result = _generate_candidate(
                        service=service,
                        sandbox_root=sandbox_root,
                        trajectory_path=Path(capture_result["trajectory_path"]),
                        skill_name=f"{fixture_name}_candidate",
                        generation_config=manual_generation_config,
                    )
            except Exception as exc:  # noqa: BLE001
                result["failure_reason"] = str(exc)
                result["loop_stage"] = "generation_failed"
                return result

            result["generated_candidate_status"] = "passed"
            result["recommended_next_action"] = capture_result.get("recommended_next_action")
            result["staging_file"] = distill_result.get("staging_file")

            fallback_artifact = distill_result.get("fallback_artifact")
            result["generated_candidate_provider"] = _generated_candidate_provider(distill_result)
            result["inferred_or_used_input_schema"] = _inferred_or_used_input_schema(distill_result, fallback_artifact)
            result["declared_input_schema_keys"] = _schema_keys(result["inferred_or_used_input_schema"])
            result["candidate_kwargs_keys"] = _candidate_kwargs_keys(result["staging_file"])
            result["schema_execution_arg_mismatch"] = _schema_execution_arg_mismatch(
                declared_input_schema_keys=result["declared_input_schema_keys"],
                execution_arg_keys=result["execution_arg_keys"],
                candidate_kwargs_keys=result["candidate_kwargs_keys"],
            )
            if fallback_artifact:
                fallback_response = _read_fallback_artifact(Path(fallback_artifact))
                result["provider_used"]["fallback"] = (
                    fallback_response.get("provider_name") or result["provider_used"]["fallback"]
                )
                result["repair_attempted"] = _repair_attempted(fallback_response)
                if result["repair_attempted"]:
                    result["repair_status"] = "attempted"

            try:
                audit_result = service.audit(
                    distill_result["staging_file"],
                    trajectory_path=capture_result["trajectory_path"],
                )
            except Exception as exc:  # noqa: BLE001
                result["failure_reason"] = str(exc)
                result["loop_stage"] = "audit_failed"
                return result

            report = audit_result["report"]
            result["audit_status"] = report["status"]
            result["provider_used"]["semantic"] = report.get("semantic_provider") or result["provider_used"]["semantic"]
            result["recommended_next_action"] = (
                audit_result.get("recommended_next_action") or result["recommended_next_action"]
            )

            if report["status"] != "passed":
                result["failure_reason"] = _audit_failure_reason(report)
                result["loop_stage"] = "audit_failed"
                return result

            execution_result = _execute_staging_candidate(
                Path(distill_result["staging_file"]),
                sandbox_root,
                selected_execution_args,
            )
            result["execution_smoke_status"] = execution_result["status"]
            result["failure_reason"] = execution_result["failure_reason"]
            result["produced_artifacts"] = execution_result["produced_artifacts"]
            result["missing_artifacts"] = execution_result["missing_artifacts"]
            if execution_result["status"] == "passed":
                result["loop_stage"] = "execution_passed"
            else:
                result["loop_stage"] = "execution_failed"
            return result


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


def _seed_execution_fixture(sandbox_root: Path) -> None:
    input_path = sandbox_root / "demo" / "input" / "provider_quality_source.txt"
    input_path.parent.mkdir(parents=True, exist_ok=True)
    input_path.write_text("provider quality source", encoding="utf-8")


def _seed_review_cleanup_fixture(sandbox_root: Path) -> None:
    review_comments = sandbox_root / "demo" / "maintainer_review_cleanup" / "review_comments.json"
    review_comments.parent.mkdir(parents=True, exist_ok=True)
    if not review_comments.exists():
        review_comments.write_text("[]", encoding="utf-8")


def _generate_candidate(
    *,
    service: RuntimeService,
    sandbox_root: Path,
    trajectory_path: Path,
    skill_name: str,
    generation_config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    trajectory = TrajectoryStore(service.trajectories_dir).load_file(trajectory_path)
    generation_config = generation_config or {}
    summary = generation_config.get(
        "summary",
        "Copy one file and write a metadata sidecar for provider quality evaluation.",
    )
    docstring = generation_config.get(
        "docstring",
        (
            "功能描述:\n"
            "    Copy one file and write a metadata sidecar for provider quality evaluation.\n\n"
            "输入参数:\n"
            "    - input_path: str\n"
            "    - output_path: str\n"
            "    - metadata_path: str\n\n"
            "输出结果:\n"
            "    - status: str\n"
            "    - artifacts: list[str]\n"
            "    - steps_executed: int"
        ),
    )
    input_schema = generation_config.get(
        "input_schema",
        {
            "input_path": "str",
            "output_path": "str",
            "metadata_path": "str",
        },
    )
    code, provider_name, fallback_artifact = FallbackService(sandbox_root / "skill_store" / "staging").generate(
        skill_name,
        summary,
        docstring,
        trajectory,
        input_schema,
    )
    staging_file = sandbox_root / "skill_store" / "staging" / f"{skill_name}.py"
    staging_file.write_text(code, encoding="utf-8")
    return {
        "staging_file": str(staging_file.resolve()),
        "fallback_artifact": str(Path(fallback_artifact).resolve()) if fallback_artifact else None,
        "fallback_provider": provider_name,
        "input_schema": input_schema,
    }


def _observed_task() -> dict[str, Any]:
    return {
        "task": "Copy one file and write a metadata sidecar for provider quality evaluation.",
        "actions": [
            {
                "tool": "copy_file",
                "input": {
                    "source_path": "demo/input/provider_quality_source.txt",
                    "target_path": "demo/output/provider_quality_result.txt",
                },
                "result": "Copied the source file into the output directory.",
            },
            {
                "tool": "write_json",
                "input": {
                    "path": "demo/output/provider_quality_result.json",
                    "payload": {"source": "demo/input/provider_quality_source.txt"},
                },
                "result": "Wrote a JSON metadata sidecar.",
            },
        ],
        "outputs": [
            "demo/output/provider_quality_result.txt",
            "demo/output/provider_quality_result.json",
        ],
    }


def _execution_args() -> dict[str, str]:
    return {
        "input_path": "demo/input/provider_quality_source.txt",
        "output_path": "demo/output/provider_quality_result.txt",
        "metadata_path": "demo/output/provider_quality_result.json",
    }


def _execute_staging_candidate(skill_path: Path, workspace: Path, args: dict[str, str]) -> dict[str, Any]:
    expected_artifacts = _expected_artifacts(args)
    try:
        spec = importlib.util.spec_from_file_location("provider_quality_candidate", skill_path)
        if spec is None or spec.loader is None:
            return {
                "status": "failed",
                "failure_reason": f"Unable to load candidate module: {skill_path.name}",
                "produced_artifacts": [],
                "missing_artifacts": expected_artifacts,
            }
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        run = getattr(module, "run", None)
        if not callable(run):
            return {
                "status": "failed",
                "failure_reason": "Generated candidate is missing run(tools, **kwargs).",
                "produced_artifacts": [],
                "missing_artifacts": expected_artifacts,
            }
        tools = RuntimeTools(workspace)
        run_result = run(tools, **args)
        operation_log = tools.export_records()
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "failed",
            "failure_reason": str(exc),
            "produced_artifacts": [],
            "missing_artifacts": expected_artifacts,
        }

    produced_artifacts = _produced_artifacts(workspace, operation_log, expected_artifacts)
    missing_artifacts = [path for path in expected_artifacts if path not in produced_artifacts]
    if missing_artifacts:
        return {
            "status": "failed",
            "failure_reason": "Execution smoke did not create expected artifact(s): " + ", ".join(missing_artifacts),
            "produced_artifacts": produced_artifacts,
            "missing_artifacts": missing_artifacts,
        }
    if not isinstance(run_result, dict) or run_result.get("status") not in {"completed", "success"}:
        return {
            "status": "failed",
            "failure_reason": "Execution smoke returned a non-success result payload.",
            "produced_artifacts": produced_artifacts,
            "missing_artifacts": missing_artifacts,
        }
    return {
        "status": "passed",
        "failure_reason": None,
        "produced_artifacts": produced_artifacts,
        "missing_artifacts": missing_artifacts,
    }


def _expected_artifacts(args: dict[str, str]) -> list[str]:
    expected = []
    for key in ("output_path", "metadata_path"):
        value = args.get(key)
        if isinstance(value, str) and value:
            expected.append(value.replace("\\", "/"))
    return expected


def _produced_artifacts(
    workspace: Path,
    operation_log: list[dict[str, Any]],
    expected_artifacts: list[str],
) -> list[str]:
    produced: set[str] = set()
    for record in operation_log:
        artifacts = record.get("artifacts")
        if not isinstance(artifacts, list):
            continue
        for artifact in artifacts:
            if isinstance(artifact, str):
                produced.add(artifact.replace("\\", "/"))
    for artifact in expected_artifacts:
        if (workspace / artifact).exists():
            produced.add(artifact)
    return sorted(produced)


def _generated_candidate_provider(distill_result: dict[str, Any]) -> str | None:
    fallback_provider = distill_result.get("fallback_provider")
    if isinstance(fallback_provider, str) and fallback_provider:
        return fallback_provider
    fallback_artifact = distill_result.get("fallback_artifact")
    if isinstance(fallback_artifact, str) and fallback_artifact:
        fallback_response = _read_fallback_artifact(Path(fallback_artifact))
        artifact_provider = fallback_response.get("provider_name")
        if isinstance(artifact_provider, str) and artifact_provider:
            return artifact_provider
    metadata = _candidate_metadata(distill_result)
    rule_name = metadata.get("rule_name")
    if isinstance(rule_name, str) and rule_name:
        return f"deterministic_rule:{rule_name}"
    return None


def _schema_keys(input_schema: dict[str, Any] | None) -> list[str]:
    if not isinstance(input_schema, dict):
        return []
    return sorted(str(key) for key in input_schema.keys())


def _candidate_kwargs_keys(staging_file: str | None) -> list[str]:
    if not isinstance(staging_file, str) or not staging_file:
        return []
    try:
        source = Path(staging_file).read_text(encoding="utf-8")
    except OSError:
        return []
    matches = re.findall(r"kwargs\.get\(\s*['\"]([^'\"]+)['\"]\s*\)", source)
    return sorted(set(matches))


def _schema_execution_arg_mismatch(
    *,
    declared_input_schema_keys: list[str],
    execution_arg_keys: list[str],
    candidate_kwargs_keys: list[str],
) -> dict[str, list[str]]:
    schema_set = set(declared_input_schema_keys)
    execution_set = set(execution_arg_keys)
    candidate_set = set(candidate_kwargs_keys)
    return {
        "schema_not_in_execution_args": sorted(schema_set - execution_set),
        "execution_args_not_in_schema": sorted(execution_set - schema_set),
        "candidate_kwargs_not_in_schema": sorted(candidate_set - schema_set),
    }


def _inferred_or_used_input_schema(
    distill_result: dict[str, Any],
    fallback_artifact: str | None,
) -> dict[str, Any] | None:
    input_schema = distill_result.get("input_schema")
    if isinstance(input_schema, dict):
        return input_schema
    metadata = _candidate_metadata(distill_result)
    metadata_input_schema = metadata.get("input_schema")
    if isinstance(metadata_input_schema, dict):
        return metadata_input_schema
    if fallback_artifact:
        try:
            payload = json.loads(Path(fallback_artifact).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        request = payload.get("request")
        if isinstance(request, dict):
            request_input_schema = request.get("input_schema")
            if isinstance(request_input_schema, dict):
                return request_input_schema
    return None


def _candidate_metadata(distill_result: dict[str, Any]) -> dict[str, Any]:
    metadata_file = distill_result.get("metadata_file")
    if not isinstance(metadata_file, str) or not metadata_file:
        return {}
    try:
        payload = json.loads(Path(metadata_file).read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _read_fallback_artifact(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    response = payload.get("response")
    return response if isinstance(response, dict) else {}


def _repair_attempted(fallback_response: dict[str, Any]) -> bool:
    reason = fallback_response.get("reason")
    return isinstance(reason, str) and "Repaired after quality gate failure" in reason


def _audit_failure_reason(report: dict[str, Any]) -> str:
    findings = report.get("semantic_findings") or report.get("static_findings") or []
    if isinstance(findings, list) and findings:
        return "Audit did not pass: " + "; ".join(str(item) for item in findings)
    return "Audit did not pass."


@contextmanager
def _patched_env(updates: dict[str, str | None]):
    original = {key: os.environ.get(key) for key in updates}
    try:
        for key, value in updates.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        os.environ.setdefault("PYTHONIOENCODING", "utf-8")
        yield
    finally:
        for key, value in original.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


class _FakeDeepSeekServer:
    def __init__(self, response_content: dict[str, Any] | list[dict[str, Any]]) -> None:
        self.response_contents = response_content if isinstance(response_content, list) else [response_content]
        self._server: HTTPServer | None = None
        self._thread: threading.Thread | None = None
        self.url = ""
        self.request_count = 0

    def __enter__(self):
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self) -> None:  # noqa: N802
                content_length = int(self.headers.get("Content-Length", "0"))
                self.rfile.read(content_length)
                response_content = owner.response_contents[
                    min(owner.request_count, len(owner.response_contents) - 1)
                ]
                owner.request_count += 1
                response = {
                    "choices": [
                        {
                            "message": {
                                "content": json.dumps(response_content),
                            }
                        }
                    ]
                }
                encoded = json.dumps(response).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(encoded)))
                self.end_headers()
                self.wfile.write(encoded)

            def log_message(self, format: str, *args) -> None:  # noqa: A003
                return

        self._server = HTTPServer(("127.0.0.1", 0), Handler)
        host, port = self._server.server_address
        self.url = f"http://{host}:{port}"
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._server:
            self._server.shutdown()
            self._server.server_close()
        if self._thread:
            self._thread.join(timeout=5)


def _fake_deepseek_server(response_content: dict[str, Any] | list[dict[str, Any]]) -> _FakeDeepSeekServer:
    return _FakeDeepSeekServer(response_content)


def _deepseek_valid_copy_metadata_candidate() -> dict[str, str]:
    return {
        "code": (
            "def run(tools, **kwargs):\n"
            "    \"\"\"\n"
            "    功能描述:\n"
            "        Copy one file and write metadata.\n\n"
            "    输入参数:\n"
            "        - input_path: source file\n"
            "        - output_path: destination file\n"
            "        - metadata_path: metadata sidecar\n\n"
            "    输出结果:\n"
            "        - status and artifacts\n"
            "    \"\"\"\n"
            "    input_path = kwargs.get('input_path')\n"
            "    output_path = kwargs.get('output_path')\n"
            "    metadata_path = kwargs.get('metadata_path')\n"
            "    copied_path = tools.copy_file(input_path, output_path)\n"
            "    tools.write_json(metadata_path, {'copied_path': copied_path})\n"
            "    return {'status': 'completed', 'artifacts': [output_path, metadata_path]}\n"
        ),
        "provider_name": "deepseek_fallback_provider",
        "reason": "DeepSeek generated a candidate skill from the fallback prompt.",
    }


def _deepseek_invalid_signature_candidate() -> dict[str, str]:
    return {
        "code": (
            "def run(tools, **kwargs):\n"
            "    \"\"\"\n"
            "    功能描述:\n"
            "        Copy one file and write metadata.\n\n"
            "    输入参数:\n"
            "        - input_path: source file\n"
            "        - output_path: destination file\n"
            "        - metadata_path: metadata sidecar\n\n"
            "    输出结果:\n"
            "        - status and artifacts\n"
            "    \"\"\"\n"
            "    input_path = kwargs.get('input_path')\n"
            "    output_path = kwargs.get('output_path')\n"
            "    metadata_path = kwargs.get('metadata_path')\n"
            "    tools.copy_file(source_path=input_path, destination_path=output_path)\n"
            "    tools.write_json(path=metadata_path, data={'copied_path': output_path})\n"
            "    return {'status': 'completed'}\n"
        ),
        "provider_name": "deepseek_fallback_provider",
        "reason": "DeepSeek generated a candidate skill from the fallback prompt.",
    }


def _deepseek_low_quality_candidate() -> dict[str, str]:
    return {
        "code": "def run(tools, **kwargs):\n    return {'status': 'completed'}\n",
        "provider_name": "deepseek_fallback_provider",
        "reason": "DeepSeek generated a low-quality candidate skill from the fallback prompt.",
    }


if __name__ == "__main__":
    raise SystemExit(main())
