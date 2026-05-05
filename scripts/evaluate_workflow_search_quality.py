from __future__ import annotations

import argparse
import json
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


FIXTURE_SKILLS = [
    "session_handoff_maintenance",
    "pre_implementation_workflow_review",
    "runtime_gate_workflow",
    "runtime_verification_selector",
    "repo_impact_analysis",
    "deployment_strategy_review",
    "auto_mode_stage_runner",
    "nontechnical_stage_report",
]

QUERY_CASES = [
    {
        "query_id": "handoff_continuation",
        "query": "continue from handoff and update tasks decisions",
        "expected_top_skill": "session_handoff_maintenance",
        "query_type": "positive_handoff_continuation",
        "expectation_mode": "should_match",
        "expectation_note": "Repository-state continuation should route to the session handoff workflow.",
    },
    {
        "query_id": "pre_implementation_review",
        "query": "review the plan before coding",
        "expected_top_skill": "pre_implementation_workflow_review",
        "query_type": "positive_pre_implementation_review",
        "expectation_mode": "should_match",
        "expectation_note": "Direction or route review before implementation should route to the pre-implementation workflow review skill.",
    },
    {
        "query_id": "maintainer_review_cleanup",
        "query": "turn review comments into a cleanup plan",
        "expected_top_skill": None,
        "query_type": "positive_review_cleanup_expected_gap",
        "expectation_mode": "expected_gap",
        "expectation_note": "Review cleanup is a real maintainer workflow, but there is no active workflow search skill that should own this intent yet.",
    },
    {
        "query_id": "governed_learning_follow_up",
        "query": "decide whether to distill or review a skill candidate",
        "expected_top_skill": None,
        "query_type": "positive_governed_learning_expected_gap",
        "expectation_mode": "expected_gap",
        "expectation_note": "Distill and evolution review are current host follow-up operations, not active workflow search skills.",
    },
    {
        "query_id": "negative_utility_merge_markdown",
        "query": "merge text files into markdown",
        "expected_top_skill": None,
        "query_type": "negative_utility_query",
        "expectation_mode": "should_not_match",
        "expectation_note": "A utility-file task should not be counted as a workflow-skill search success in the workflow-only fixture set.",
    },
]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate local workflow-oriented skill search quality against a workflow-only fixture set."
    )
    parser.add_argument(
        "--source-root",
        default=str(ROOT),
        help="Repository root used as the source of active workflow skill fixtures.",
    )
    parser.add_argument("--top-k", type=int, default=5, help="Number of search results to inspect.")
    parser.add_argument(
        "--baseline",
        help="Optional machine-readable baseline JSON path to compare against the evaluation report.",
    )
    parser.add_argument(
        "--fail-on-regression",
        action="store_true",
        help="Return non-zero when baseline comparison finds a regression, unexpected failure, or missing query.",
    )
    parser.add_argument(
        "--output",
        help="Optional path to write the JSON report. The report is still printed to stdout.",
    )
    args = parser.parse_args()

    payload = evaluate(Path(args.source_root), top_k=args.top_k)
    exit_code = 0
    if args.baseline:
        baseline_path = Path(args.baseline)
        baseline_payload = json.loads(baseline_path.read_text(encoding="utf-8-sig"))
        comparison = compare_to_baseline(payload["queries"], baseline_payload)
        payload["baseline_comparison"] = comparison
        if args.fail_on_regression and has_blocking_baseline_regression(comparison):
            exit_code = 1
    rendered = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")
    print(rendered)
    return exit_code


def evaluate(source_root: Path, *, top_k: int = 5) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="skill-runtime-workflow-search-quality-") as temp_dir:
        sandbox_root = Path(temp_dir)
        _prepare_search_sandbox(source_root, sandbox_root)
        service = RuntimeService(sandbox_root)
        queries = [_evaluate_query(service, case, top_k=top_k) for case in QUERY_CASES]

    positive_queries = [item for item in queries if item["query_type"].startswith("positive_")]
    negative_queries = [item for item in queries if item["query_type"].startswith("negative_")]
    expected_gap_queries = [item for item in queries if item["expectation_mode"] == "expected_gap"]
    return {
        "status": "ok",
        "fixture_skills": FIXTURE_SKILLS,
        "queries": queries,
        "summary": {
            "query_count": len(queries),
            "matched_count": sum(1 for item in queries if item["matched"]),
            "expectation_met_count": sum(1 for item in queries if item["expectation_met"]),
            "positive_query_count": len(positive_queries),
            "positive_matched_count": sum(1 for item in positive_queries if item["matched"]),
            "expected_gap_query_count": len(expected_gap_queries),
            "expected_gap_confirmed_count": sum(1 for item in expected_gap_queries if item["expectation_met"]),
            "negative_query_count": len(negative_queries),
            "negative_expectation_met_count": sum(1 for item in negative_queries if item["expectation_met"]),
        },
        "current_limitations": [
            "Search is lexical and local only; no embeddings or external retrieval are used.",
            "This workflow baseline imports workflow adapters only; utility skills remain separate fixtures for smoke coverage and the existing utility search baseline.",
            "Maintainer review cleanup and governed learning follow-up are not yet represented as active workflow search skills, so this evaluator can record honest expected gaps without changing ranking.",
        ],
    }


def compare_to_baseline(queries: list[dict[str, Any]], baseline_payload: dict[str, Any]) -> dict[str, Any]:
    expected_queries = baseline_payload.get("queries")
    if not isinstance(expected_queries, list):
        raise ValueError("Baseline JSON must contain a queries list.")

    actual_by_id = {
        item["query_id"]: item
        for item in queries
        if isinstance(item.get("query_id"), str) and item.get("query_id")
    }
    expected_by_id = {
        item["query_id"]: item
        for item in expected_queries
        if isinstance(item, dict) and isinstance(item.get("query_id"), str) and item.get("query_id")
    }

    comparison: dict[str, Any] = {
        "matched": [],
        "regressions": [],
        "improvements": [],
        "unexpected_failures": [],
        "unexpected_passes": [],
        "missing_queries": [],
        "extra_queries": [],
    }

    for query_id, expected in expected_by_id.items():
        actual = actual_by_id.get(query_id)
        if actual is None:
            comparison["missing_queries"].append(query_id)
            continue

        actual_snapshot = _baseline_actual_snapshot(actual)
        mismatches = _baseline_mismatches(expected, actual_snapshot)
        if not mismatches:
            comparison["matched"].append(query_id)
            continue

        expected_mode = expected.get("expectation_mode")
        expected_met = bool(expected.get("expected_expectation_met"))
        actual_met = bool(actual_snapshot["expectation_met"])
        expected_recommended_skill = expected.get("expected_recommended_skill")
        actual_recommended_skill = actual_snapshot["recommended_skill"]

        if expected_mode == "should_not_match" and actual_recommended_skill is not None:
            comparison["unexpected_failures"].append(_baseline_issue(query_id, mismatches, actual_snapshot))
        elif expected_mode == "expected_gap" and actual_recommended_skill is not None:
            comparison["unexpected_failures"].append(_baseline_issue(query_id, mismatches, actual_snapshot))
        elif expected_met and not actual_met:
            comparison["regressions"].append(_baseline_issue(query_id, mismatches, actual_snapshot))
        elif not expected_met and actual_met:
            comparison["improvements"].append(_baseline_issue(query_id, mismatches, actual_snapshot))
        elif expected_recommended_skill != actual_recommended_skill:
            comparison["regressions"].append(_baseline_issue(query_id, mismatches, actual_snapshot))
        else:
            comparison["regressions"].append(_baseline_issue(query_id, mismatches, actual_snapshot))

    for query_id in sorted(set(actual_by_id) - set(expected_by_id)):
        comparison["extra_queries"].append(query_id)

    for key in comparison:
        comparison[key] = sorted(comparison[key], key=_comparison_sort_key)
    return comparison


def has_blocking_baseline_regression(comparison: dict[str, Any]) -> bool:
    return bool(
        comparison.get("regressions")
        or comparison.get("unexpected_failures")
        or comparison.get("missing_queries")
    )


def _prepare_search_sandbox(source_root: Path, sandbox_root: Path) -> None:
    active_dir = sandbox_root / "skill_store" / "active"
    active_dir.mkdir(parents=True, exist_ok=True)
    (sandbox_root / ".skill_runtime").mkdir(parents=True, exist_ok=True)

    source_active_dir = source_root / "skill_store" / "active"
    for skill_name in FIXTURE_SKILLS:
        source_skill = source_active_dir / f"{skill_name}.py"
        source_metadata = source_active_dir / f"{skill_name}.metadata.json"
        if not source_skill.exists() or not source_metadata.exists():
            raise FileNotFoundError(f"Missing active workflow fixture source for {skill_name}")

        target_skill = active_dir / source_skill.name
        target_metadata = active_dir / source_metadata.name
        shutil.copy2(source_skill, target_skill)
        metadata_payload = json.loads(source_metadata.read_text(encoding="utf-8-sig"))
        metadata_payload["file_path"] = str(target_skill.resolve())
        target_metadata.write_text(
            json.dumps(metadata_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    SkillIndex(sandbox_root / "skill_store" / "index.json").rebuild_from_directory(active_dir)


def _evaluate_query(service: RuntimeService, case: dict[str, Any], *, top_k: int) -> dict[str, Any]:
    payload = service.search(case["query"], top_k=top_k)
    results = payload["results"]
    expected_top_skill = case["expected_top_skill"]
    actual_top_skill = results[0]["skill_name"] if results else None
    actual_recommended_skill = payload["recommended_skill_name"]
    expected_rank = _skill_rank(results, expected_top_skill) if expected_top_skill else None
    matched = bool(expected_top_skill and actual_recommended_skill == expected_top_skill)
    expectation_met = _expectation_met(case["expectation_mode"], matched, actual_recommended_skill)

    return {
        "query_id": case["query_id"],
        "query": case["query"],
        "query_type": case["query_type"],
        "expectation_mode": case["expectation_mode"],
        "expectation_note": case["expectation_note"],
        "expected_top_skill": expected_top_skill,
        "expected_skills": [expected_top_skill] if expected_top_skill else [],
        "actual_top_skill": actual_top_skill,
        "actual_recommended_skill": actual_recommended_skill,
        "matched": matched,
        "expectation_met": expectation_met,
        "top_k": top_k,
        "failure_reason": _failure_reason(
            expectation_mode=case["expectation_mode"],
            expectation_note=case["expectation_note"],
            expected_top_skill=expected_top_skill,
            actual_top_skill=actual_top_skill,
            actual_recommended_skill=actual_recommended_skill,
            expected_rank=expected_rank,
            results=results,
        ),
        "rank_diagnostics": {
            "expected_skill_rank": expected_rank,
            "top_result_score": results[0]["score"] if results else None,
            "recommended_threshold": RuntimeService.RECOMMENDED_EXECUTION_SCORE,
            "result_count": len(results),
        },
        "top_results": [
            {
                "skill_name": item["skill_name"],
                "score": item["score"],
                "library_tier": item.get("library_tier"),
                "why_matched": item.get("why_matched"),
                "score_breakdown": item.get("score_breakdown"),
            }
            for item in results
        ],
    }


def _expectation_met(expectation_mode: str, matched: bool, actual_recommended_skill: str | None) -> bool:
    if expectation_mode == "should_match":
        return matched
    if expectation_mode in {"should_not_match", "expected_gap"}:
        return actual_recommended_skill is None
    raise ValueError(f"Unsupported expectation mode: {expectation_mode}")


def _baseline_actual_snapshot(actual: dict[str, Any]) -> dict[str, Any]:
    return {
        "query_type": actual.get("query_type"),
        "expectation_mode": actual.get("expectation_mode"),
        "top_skill": actual.get("actual_top_skill"),
        "matched": bool(actual.get("matched")),
        "expectation_met": bool(actual.get("expectation_met")),
        "recommended_skill": actual.get("actual_recommended_skill"),
    }


def _baseline_mismatches(expected: dict[str, Any], actual_snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    mismatches = []
    expectation_mode = expected.get("expectation_mode")
    checks: list[tuple[str, str]] = [
        ("query_type", "query_type"),
        ("expectation_mode", "expectation_mode"),
        ("expected_matched", "matched"),
        ("expected_expectation_met", "expectation_met"),
        ("expected_recommended_skill", "recommended_skill"),
    ]
    if expectation_mode == "should_match":
        checks.insert(2, ("expected_top_skill", "top_skill"))

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


def _baseline_issue(
    query_id: str,
    mismatches: list[dict[str, Any]],
    actual_snapshot: dict[str, Any],
) -> dict[str, Any]:
    return {
        "query_id": query_id,
        "mismatches": mismatches,
        "actual": actual_snapshot,
    }


def _comparison_sort_key(item: Any) -> str:
    if isinstance(item, dict):
        return str(item.get("query_id", ""))
    return str(item)


def _skill_rank(results: list[dict[str, Any]], skill_name: str | None) -> int | None:
    if not skill_name:
        return None
    for index, item in enumerate(results, start=1):
        if item.get("skill_name") == skill_name:
            return index
    return None


def _failure_reason(
    *,
    expectation_mode: str,
    expectation_note: str,
    expected_top_skill: str | None,
    actual_top_skill: str | None,
    actual_recommended_skill: str | None,
    expected_rank: int | None,
    results: list[dict[str, Any]],
) -> str | None:
    if expectation_mode == "should_not_match":
        if actual_recommended_skill is None:
            return None
        return (
            "Utility query unexpectedly recommended a workflow skill: "
            f"{actual_recommended_skill}."
        )

    if expectation_mode == "expected_gap":
        if actual_recommended_skill is None:
            return None
        return (
            "Query currently behaves like an expected gap, but search recommended a workflow skill: "
            f"{actual_recommended_skill}."
        )

    if not expected_top_skill:
        return expectation_note
    if not results:
        return "No search results returned."
    if expected_rank is None:
        return f"Expected skill {expected_top_skill} was not found in top_k results."
    if actual_top_skill != expected_top_skill:
        return f"Expected top skill {expected_top_skill}, but top result was {actual_top_skill}."
    if actual_recommended_skill != expected_top_skill:
        return (
            f"Expected recommended skill {expected_top_skill}, but recommended skill was "
            f"{actual_recommended_skill!r}."
        )
    return None


if __name__ == "__main__":
    raise SystemExit(main())
