from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from skill_runtime.api.service import RuntimeService  # noqa: E402


SEARCH_CASES = [
    {
        "query": "merge txt files into markdown",
        "expected_skill": "merge_text_files",
    },
    {
        "query": "combine text files into one markdown document",
        "expected_skill": "merge_text_files",
    },
    {
        "query": "archive log files from inbox",
        "expected_skill": "archive_log_files_dogfood",
    },
    {
        "query": "move all log files to archive folder",
        "expected_skill": "archive_log_files_dogfood",
    },
    {
        "query": "convert json records to csv",
        "expected_skill": "json_to_csv_dogfood",
    },
    {
        "query": "export json list as csv file",
        "expected_skill": "json_to_csv_dogfood",
    },
    {
        "query": "convert json directory to csv files",
        "expected_skill": "directory_json_to_csv_dogfood",
    },
    {
        "query": "batch export json records folder to csv",
        "expected_skill": "directory_json_to_csv_dogfood",
    },
    {
        "query": "replace text in one file",
        "expected_skill": "text_replace_dogfood",
    },
    {
        "query": "update draft word in a text file",
        "expected_skill": "text_replace_dogfood",
    },
    {
        "query": "clean text files in a directory",
        "expected_skill": "directory_text_cleanup_dogfood",
    },
    {
        "query": "normalize txt folder trailing whitespace",
        "expected_skill": "directory_text_cleanup_dogfood",
    },
]

NO_RECOMMENDATION_CASES = [
    {
        "query": "send an email newsletter campaign",
    },
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate active skill search quality against a small fixture set.")
    parser.add_argument("--root", default=str(ROOT), help="runtime root to evaluate")
    parser.add_argument("--top-k", type=int, default=5, help="number of search results to inspect")
    args = parser.parse_args()

    payload = evaluate(Path(args.root), top_k=args.top_k)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["passed"] else 1


def evaluate(root: Path, *, top_k: int = 5) -> dict[str, Any]:
    service = RuntimeService(root)
    checks: list[dict[str, Any]] = []

    for case in SEARCH_CASES:
        result = service.search(case["query"], top_k=top_k)
        recommended = result["recommended_skill_name"]
        checks.append(
            {
                "query": case["query"],
                "expected_skill": case["expected_skill"],
                "recommended_skill": recommended,
                "passed": recommended == case["expected_skill"],
                "top_results": [item["skill_name"] for item in result["results"]],
            }
        )

    for case in NO_RECOMMENDATION_CASES:
        result = service.search(case["query"], top_k=top_k)
        recommended = result["recommended_skill_name"]
        top_results = [item["skill_name"] for item in result["results"]]
        checks.append(
            {
                "query": case["query"],
                "expected_skill": None,
                "recommended_skill": recommended,
                "passed": recommended is None and not top_results,
                "top_results": top_results,
            }
        )

    passed_count = sum(1 for check in checks if check["passed"])
    return {
        "passed": passed_count == len(checks),
        "passed_count": passed_count,
        "total_count": len(checks),
        "checks": checks,
    }


if __name__ == "__main__":
    raise SystemExit(main())
