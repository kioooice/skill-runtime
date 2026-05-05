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
        "query_type": "known_limitation_chinese",
    },
    {
        "query_id": "negative_email_newsletter",
        "query": "send an email newsletter campaign",
        "expected_top_skill": None,
        "query_type": "negative_no_strong_match",
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
        "--output",
        help="Optional path to write the JSON report. The report is still printed to stdout.",
    )
    args = parser.parse_args()

    payload = evaluate(Path(args.source_root), top_k=args.top_k)
    rendered = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")
    print(rendered)
    return 0


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
            "Tokenization only keeps ASCII-style alphanumeric tokens and underscores, so Chinese-only queries are expected to be weak or unmatched.",
            "A result can appear in top_k without being recommended for reuse if it stays below RuntimeService.RECOMMENDED_EXECUTION_SCORE.",
        ],
    }


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
