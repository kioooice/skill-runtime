import json
import sys


def main() -> int:
    raw_input = sys.stdin.read().lstrip("\ufeff")
    if not raw_input.strip():
        raise ValueError("pass semantic review provider expects a JSON request on stdin")
    request = json.loads(raw_input)
    heuristic_issues = request.get("heuristic_issues") or []
    blocking = [
        issue
        for issue in heuristic_issues
        if isinstance(issue, dict) and issue.get("severity") == "high"
    ]
    if blocking:
        print(
            json.dumps(
                {
                    "provider_name": "local_pass_semantic_review_provider",
                    "summary": "Local demo semantic provider preserved blocking heuristic issues.",
                    "issues": [],
                }
            )
        )
        return 0

    print(
        json.dumps(
            {
                "provider_name": "local_pass_semantic_review_provider",
                "summary": "Local demo semantic provider found no additional issues.",
                "issues": [],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
