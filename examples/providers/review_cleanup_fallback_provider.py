import json
import sys


def main() -> int:
    raw_input = sys.stdin.read().lstrip("\ufeff")
    if not raw_input.strip():
        raise ValueError("review cleanup fallback provider expects a JSON request on stdin")
    json.loads(raw_input)
    code = '''import json


def _comment_line(comment):
    comment_id = comment.get("id", "unknown")
    file_path = comment.get("file", "unknown")
    body = comment.get("comment", "").strip()
    return f"- {comment_id} [{file_path}]: {body}"


def run(tools, **kwargs):
    """
    功能描述:
        Read review comments and write a grouped maintainer cleanup plan without changing code.

    输入参数:
        - input_path: JSON file with pull request review comments.
        - output_path: Markdown cleanup plan path.
        - metadata_path: Optional JSON metadata output path.

    输出结果:
        - dict with completion status, produced artifacts, and grouped comment counts.
    """
    input_path = kwargs.get("input_path")
    output_path = kwargs.get("output_path")
    metadata_path = kwargs.get("metadata_path")
    missing = [name for name, value in {"input_path": input_path, "output_path": output_path}.items() if value is None]
    if missing:
        raise ValueError(f"Missing required inputs: {missing}")

    payload = tools.read_json(input_path)
    review_comments = payload.get("review_comments") or []
    pull_request = payload.get("pull_request") or {}
    maintainer_goal = payload.get("maintainer_goal") or "Convert review comments into a cleanup plan."

    required = [item for item in review_comments if item.get("severity") == "must_fix"]
    follow_up = [item for item in review_comments if item.get("severity") != "must_fix"]

    lines = [
        "# Review Cleanup Plan",
        "",
        f"Pull request: #{pull_request.get('number', 'unknown')} - {pull_request.get('title', 'Unknown PR')}",
        "",
        "## Maintainer Goal",
        "",
        maintainer_goal,
        "",
        "## Required Fixes",
        "",
    ]
    if required:
        lines.extend(_comment_line(item) for item in required)
    else:
        lines.append("- No required fixes.")
    lines.extend(["", "## Follow-Up Items", ""])
    if follow_up:
        lines.extend(_comment_line(item) for item in follow_up)
    else:
        lines.append("- No follow-up items.")
    lines.extend(["", "## Suggested Verification", "", "```powershell", "git diff --check", "```"])

    plan_text = "\\n".join(lines) + "\\n"
    tools.write_text(output_path, plan_text)

    artifacts = [output_path]
    if metadata_path:
        metadata = {
            "pull_request_number": pull_request.get("number"),
            "required_fix_count": len(required),
            "follow_up_count": len(follow_up),
        }
        tools.write_json(metadata_path, metadata)
        artifacts.append(metadata_path)

    return {
        "status": "completed",
        "artifacts": artifacts,
        "steps_executed": 3 if metadata_path else 2,
        "required_fix_count": len(required),
        "follow_up_count": len(follow_up),
        "generated_by": "local_review_cleanup_fallback_provider",
    }
'''
    print(
        json.dumps(
            {
                "code": code,
                "provider_name": "local_review_cleanup_fallback_provider",
                "reason": "Generated a local maintainer review cleanup planning skill.",
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
