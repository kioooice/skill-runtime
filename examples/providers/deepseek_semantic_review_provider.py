import json
import os
import sys
import urllib.error
import urllib.request

DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-v4-flash"
DEFAULT_TIMEOUT_SECONDS = 60


def main() -> int:
    request = _read_json_stdin()
    api_key = _required_env("DEEPSEEK_API_KEY")
    response = _chat_completion(
        api_key=api_key,
        messages=[
            {
                "role": "system",
                "content": (
                    "You review generated Skill Runtime Python skills. "
                    "Return only JSON with provider_name, summary, and issues. "
                    "Each issue must contain rule_id, severity, and message. "
                    "Use severity high only for problems that should block promotion, such as dangerous shell use, "
                    "path traversal, destructive behavior, missing run(), syntax failure, or code that cannot perform "
                    "the trajectory. Use medium for docstring, retrievability, naming, or generalization concerns. "
                    "If built-in heuristic findings are medium-only and the source clearly calls the same runtime "
                    "tools as the trajectory, do not add high-severity issues."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Review this Skill Runtime candidate request:\n"
                    + json.dumps(request, ensure_ascii=False)
                    + "\n\nReturn JSON only. Example shape: "
                    + json.dumps(
                        {
                            "provider_name": "deepseek",
                            "summary": "Short review summary.",
                            "issues": [],
                        },
                        ensure_ascii=False,
                    )
                ),
            },
        ],
    )
    payload = _parse_json_content(response)
    _ensure_string(payload, "provider_name", "deepseek_semantic_review_provider")
    _ensure_string(payload, "summary", "DeepSeek completed semantic review.")
    payload.setdefault("issues", [])
    _validate_issues(payload["issues"])
    print(json.dumps(payload, ensure_ascii=False))
    return 0


def _chat_completion(api_key: str, messages: list[dict[str, str]]) -> dict:
    base_url = os.environ.get("DEEPSEEK_API_BASE", DEFAULT_BASE_URL).rstrip("/")
    model = os.environ.get("DEEPSEEK_MODEL", DEFAULT_MODEL)
    timeout = float(os.environ.get("DEEPSEEK_TIMEOUT_SECONDS", str(DEFAULT_TIMEOUT_SECONDS)))
    body = {
        "model": model,
        "messages": messages,
        "temperature": float(os.environ.get("DEEPSEEK_TEMPERATURE", "0.0")),
        "response_format": {"type": "json_object"},
    }
    request = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"DeepSeek semantic provider request failed: HTTP {exc.code}: {error_body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"DeepSeek semantic provider request failed: {exc.reason}") from exc


def _parse_json_content(response: dict) -> dict:
    try:
        content = response["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError("DeepSeek response missing choices[0].message.content") from exc
    if not isinstance(content, str) or not content.strip():
        raise ValueError("DeepSeek response content must be a non-empty string")
    try:
        payload = json.loads(_strip_json_fence(content))
    except json.JSONDecodeError as exc:
        raise ValueError("DeepSeek semantic response content was not valid JSON") from exc
    if not isinstance(payload, dict):
        raise ValueError("DeepSeek semantic response content must be a JSON object")
    return payload


def _strip_json_fence(content: str) -> str:
    stripped = content.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return stripped


def _read_json_stdin() -> dict:
    raw_input = sys.stdin.read().lstrip("\ufeff")
    if not raw_input.strip():
        raise ValueError("deepseek semantic provider expects a JSON request on stdin")
    payload = json.loads(raw_input)
    if not isinstance(payload, dict):
        raise ValueError("deepseek semantic provider request must be a JSON object")
    return payload


def _required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise ValueError(f"{name} is required")
    return value


def _require_string(payload: dict, key: str) -> None:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"DeepSeek semantic response missing string field: {key}")


def _ensure_string(payload: dict, key: str, default: str) -> None:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        payload[key] = default


def _validate_issues(issues: object) -> None:
    if not isinstance(issues, list):
        raise ValueError("DeepSeek semantic response field issues must be a list")
    for issue in issues:
        if not isinstance(issue, dict):
            raise ValueError("DeepSeek semantic response issue must be an object")
        _require_string(issue, "rule_id")
        _require_string(issue, "severity")
        _require_string(issue, "message")


if __name__ == "__main__":
    raise SystemExit(main())
