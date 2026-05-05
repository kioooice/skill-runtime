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
from scripts.operator_status_utils import (  # noqa: E402
    build_operator_status_payload,
    summarize_baseline_comparison,
    write_operator_status,
)


FIXTURE_SKILLS = [
    "merge_text_files",
    "json_to_csv_dogfood",
    "session_handoff_maintenance",
    "pre_implementation_workflow_review",
    "directory_text_cleanup_dogfood",
]

QUERY_CASES = [
    {
        "query_id": "exact_merge_english",
        "query": "merge txt files into markdown",
        "expected_top_skill": "merge_text_files",
        "query_type": "positive_exact_english",
    },
    {
        "query_id": "fuzzy_merge_english",
        "query": "combine text files into one markdown document",
        "expected_top_skill": "merge_text_files",
        "query_type": "positive_fuzzy_english",
    },
    {
        "query_id": "structured_json_to_csv",
        "query": "convert json records to csv",
        "expected_top_skill": "json_to_csv_dogfood",
        "query_type": "positive_structured_conversion",
    },
    {
        "query_id": "maintainer_handoff_workflow",
        "query": "resume handoff update tasks decisions",
        "expected_top_skill": "session_handoff_maintenance",
        "query_type": "positive_maintainer_workflow",
    },
    {
        "query_id": "chinese_merge_query",
        "query": "把多个文本文件合并成一个文档",
        "expected_top_skill": "merge_text_files",
        "query_type": "positive_alias_driven_chinese",
    },
    {
        "query_id": "negative_email_newsletter",
        "query": "send an email newsletter campaign",
        "expected_top_skill": None,
        "query_type": "negative_no_strong_match",
    },
    {
        "query_id": "negative_chinese_email_campaign",
        "query": "发送邮件营销活动",
        "expected_top_skill": None,
        "query_type": "negative_no_strong_match_chinese",
    },
]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evaluate local skill search quality against a fixed small fixture set."
    )
    parser.add_argument(
        "--source-root",
        default=str(ROOT),
        help="Repository root used as the source of active skill fixtures.",
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
    parser.add_argument(
        "--write-operator-status",
        action="store_true",
        help="Optionally write a local operator-status summary under .skill_runtime/operator_status without changing stdout output.",
    )
    parser.add_argument(
        "--operator-status-root",
        help="Optional root directory for persisted operator-status output. Defaults to --source-root.",
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
    if args.write_operator_status:
        status_root = Path(args.operator_status_root).resolve() if args.operator_status_root else Path(args.source_root).resolve()
        write_operator_status(
            status_root,
            "search_quality.json",
            build_operator_status_payload(
                report_status=str(payload.get("status") or "ok"),
                summary=payload.get("summary") if isinstance(payload.get("summary"), dict) else None,
                baseline_comparison=summarize_baseline_comparison(payload.get("baseline_comparison")),
            ),
        )
    print(rendered)
    return exit_code


def evaluate(source_root: Path, *, top_k: int = 5) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="skill-runtime-search-quality-") as temp_dir:
        sandbox_root = Path(temp_dir)
        _prepare_search_sandbox(source_root, sandbox_root)
        service = RuntimeService(sandbox_root)
        queries = [_evaluate_query(service, case, top_k=top_k) for case in QUERY_CASES]

    matched_count = sum(1 for item in queries if item["matched"])
    positive_queries = [item for item in queries if item["expected_top_skill"]]
    negative_queries = [item for item in queries if item["expected_top_skill"] is None]
    return {
        "status": "ok",
        "fixture_skills": FIXTURE_SKILLS,
        "queries": queries,
        "summary": {
            "query_count": len(queries),
            "matched_count": matched_count,
            "unmatched_count": len(queries) - matched_count,
            "positive_query_count": len(positive_queries),
            "positive_matched_count": sum(1 for item in positive_queries if item["matched"]),
            "negative_query_count": len(negative_queries),
            "negative_matched_count": sum(1 for item in negative_queries if item["matched"]),
        },
        "current_limitations": [
            "Search is lexical and local only; no embeddings or external retrieval are used.",
            "Chinese intent support is still alias-driven only; there is no general Chinese tokenization or semantic retrieval.",
            "A result can appear in top_k without being recommended for reuse if it stays below RuntimeService.RECOMMENDED_EXECUTION_SCORE.",
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

        expected_query_type = expected.get("query_type")
        expected_matched = bool(expected.get("expected_matched"))
        actual_matched = bool(actual_snapshot["matched"])
        expected_recommended_skill = expected.get("expected_recommended_skill")
        actual_recommended_skill = actual_snapshot["recommended_skill"]

        if _is_negative_query_type(expected_query_type) and expected_matched and actual_recommended_skill is not None:
            comparison["unexpected_failures"].append(_baseline_issue(query_id, mismatches, actual_snapshot))
        elif expected_matched and not actual_matched:
            comparison["regressions"].append(_baseline_issue(query_id, mismatches, actual_snapshot))
        elif not expected_matched and actual_matched:
            if _is_negative_query_type(expected_query_type):
                comparison["unexpected_passes"].append(_baseline_issue(query_id, mismatches, actual_snapshot))
            else:
                comparison["improvements"].append(_baseline_issue(query_id, mismatches, actual_snapshot))
        elif expected_recommended_skill is None and actual_recommended_skill is not None:
            comparison["unexpected_failures"].append(_baseline_issue(query_id, mismatches, actual_snapshot))
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
            raise FileNotFoundError(f"Missing active skill fixture source for {skill_name}")

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

    if expected_top_skill is None:
        matched = actual_recommended_skill is None
    else:
        matched = actual_recommended_skill == expected_top_skill

    return {
        "query_id": case["query_id"],
        "query": case["query"],
        "query_type": case["query_type"],
        "expected_top_skill": expected_top_skill,
        "expected_skills": [expected_top_skill] if expected_top_skill else [],
        "actual_top_skill": actual_top_skill,
        "actual_recommended_skill": actual_recommended_skill,
        "matched": matched,
        "top_k": top_k,
        "failure_reason": _failure_reason(
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


def _baseline_actual_snapshot(actual: dict[str, Any]) -> dict[str, Any]:
    return {
        "query_type": actual.get("query_type"),
        "top_skill": actual.get("actual_top_skill"),
        "matched": bool(actual.get("matched")),
        "recommended_skill": actual.get("actual_recommended_skill"),
    }


def _baseline_mismatches(expected: dict[str, Any], actual_snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    checks = [
        ("query_type", "query_type"),
        ("expected_top_skill", "top_skill"),
        ("expected_matched", "matched"),
        ("expected_recommended_skill", "recommended_skill"),
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


def _is_negative_query_type(query_type: Any) -> bool:
    return isinstance(query_type, str) and query_type.startswith("negative_")


def _skill_rank(results: list[dict[str, Any]], skill_name: str | None) -> int | None:
    if not skill_name:
        return None
    for index, item in enumerate(results, start=1):
        if item.get("skill_name") == skill_name:
            return index
    return None


def _failure_reason(
    *,
    expected_top_skill: str | None,
    actual_top_skill: str | None,
    actual_recommended_skill: str | None,
    expected_rank: int | None,
    results: list[dict[str, Any]],
) -> str | None:
    if expected_top_skill is None:
        if actual_recommended_skill is None:
            return None
        return (
            "Negative query produced an unexpected recommended skill: "
            f"{actual_recommended_skill}."
        )

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
