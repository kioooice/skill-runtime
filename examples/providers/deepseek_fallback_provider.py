import ast
import json
import os
import sys
import urllib.error
import urllib.request

DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-v4-flash"
DEFAULT_TIMEOUT_SECONDS = 60
DOCSTRING_SECTIONS = ("功能描述", "输入参数", "输出结果")
RUNTIME_TOOLS = {
    "copy_file",
    "list_files",
    "move_file",
    "read_json",
    "read_text",
    "rename_path",
    "resolve_path",
    "run_shell",
    "write_json",
    "write_text",
}
TOOL_SIGNATURES = {
    "copy_file": {"required": ("source_path", "target_path"), "allowed": {"source_path", "target_path"}},
    "move_file": {"required": ("source_path", "target_path"), "allowed": {"source_path", "target_path"}},
    "rename_path": {"required": ("source_path", "target_path"), "allowed": {"source_path", "target_path"}},
    "write_json": {"required": ("path", "data"), "allowed": {"path", "data"}},
    "write_text": {"required": ("path", "content"), "allowed": {"path", "content"}},
    "read_json": {"required": ("path",), "allowed": {"path"}},
    "read_text": {"required": ("path",), "allowed": {"path"}},
    "list_files": {"required": ("path",), "allowed": {"path", "pattern"}},
    "resolve_path": {"required": ("path",), "allowed": {"path"}},
}


def main() -> int:
    request = _read_json_stdin()
    api_key = _required_env("DEEPSEEK_API_KEY")
    response = _chat_completion(
        api_key=api_key,
        messages=[
            {
                "role": "system",
                "content": (
                    "You generate governed Python skills for Skill Runtime. "
                    "Return only JSON with string fields: code, provider_name, reason. "
                    "The code must define run(tools, **kwargs), use runtime tools instead of shell commands, "
                    "stay parameterized, and return a structured dict. "
                    "The run() function must have a docstring containing exactly these Chinese section headers: "
                    "功能描述, 输入参数, 输出结果. "
                    "Read inputs through kwargs.get(...). Prefer canonical parameter names such as input_path, "
                    "output_path, metadata_path, input_dir, output_dir, pattern, old_text, and new_text. "
                    "The generated code must read every key from the provided input_schema literally via kwargs. "
                    "If the trajectory uses copy_file, call tools.copy_file. "
                    "If the trajectory uses write_json, call tools.write_json. "
                    "Do not hardcode demo paths or artifact names in the generated skill."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Generate a candidate Skill Runtime skill from this provider request:\n"
                    + json.dumps(request, ensure_ascii=False)
                    + "\n\nReturn JSON only. Example shape: "
                    + json.dumps(
                        {
                            "code": "def run(tools, **kwargs):\\n    ...",
                            "provider_name": "deepseek",
                            "reason": "Short generation rationale.",
                        },
                        ensure_ascii=False,
                    )
                ),
            },
        ],
    )
    payload = _parse_json_content(response)
    _require_string(payload, "code")
    payload["code"] = _normalize_code_string(payload["code"])
    _ensure_string(payload, "provider_name", "deepseek_fallback_provider")
    _ensure_string(payload, "reason", "DeepSeek generated a candidate skill from the fallback prompt.")
    _validate_candidate_skill(payload["code"], request)
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
        raise RuntimeError(f"DeepSeek fallback provider request failed: HTTP {exc.code}: {error_body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"DeepSeek fallback provider request failed: {exc.reason}") from exc


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
        raise ValueError("DeepSeek fallback response content was not valid JSON") from exc
    if not isinstance(payload, dict):
        raise ValueError("DeepSeek fallback response content must be a JSON object")
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


def _normalize_code_string(code: str) -> str:
    if "\n" in code or "\\n" not in code:
        return code
    return (
        code
        .replace("\\r\\n", "\n")
        .replace("\\n", "\n")
        .replace("\\t", "    ")
        .replace('\\"', '"')
    )


def _read_json_stdin() -> dict:
    raw_input = sys.stdin.read().lstrip("\ufeff")
    if not raw_input.strip():
        raise ValueError("deepseek fallback provider expects a JSON request on stdin")
    payload = json.loads(raw_input)
    if not isinstance(payload, dict):
        raise ValueError("deepseek fallback provider request must be a JSON object")
    return payload


def _required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise ValueError(f"{name} is required")
    return value


def _require_string(payload: dict, key: str) -> None:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"DeepSeek fallback response missing string field: {key}")


def _ensure_string(payload: dict, key: str, default: str) -> None:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        payload[key] = default


def _validate_candidate_skill(code: str, request: dict) -> None:
    issues: list[str] = []
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        raise ValueError(f"DeepSeek fallback candidate has invalid Python syntax: {exc.msg}") from exc

    run_node = _find_run_function(tree)
    if run_node is None:
        issues.append("missing run(tools, **kwargs) entrypoint")
    else:
        docstring = ast.get_docstring(run_node) or ""
        missing_sections = [section for section in DOCSTRING_SECTIONS if section not in docstring]
        if missing_sections:
            issues.append("run() docstring missing sections: " + ", ".join(missing_sections))

    expected_tools = _expected_runtime_tools(request)
    called_tools = _called_runtime_tools(tree)
    missing_tools = sorted(expected_tools - called_tools)
    if missing_tools:
        issues.append("missing runtime tool calls from trajectory: " + ", ".join(missing_tools))

    call_signature_issues = _runtime_tool_signature_issues(tree)
    issues.extend(call_signature_issues)

    expected_inputs = _expected_input_names(request)
    exposed_inputs = _exposed_kwargs(tree)
    missing_inputs = sorted(input_name for input_name in expected_inputs if input_name not in exposed_inputs)
    if missing_inputs:
        issues.append("missing kwargs for inferred inputs: " + ", ".join(missing_inputs))

    if issues:
        raise ValueError("DeepSeek fallback candidate failed quality gate: " + "; ".join(issues))


def _find_run_function(tree: ast.AST) -> ast.FunctionDef | None:
    body = tree.body if isinstance(tree, ast.Module) else []
    for node in body:
        if isinstance(node, ast.FunctionDef) and node.name == "run":
            return node
    return None


def _called_runtime_tools(tree: ast.AST) -> set[str]:
    calls: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if (
            isinstance(func, ast.Attribute)
            and isinstance(func.value, ast.Name)
            and func.value.id == "tools"
            and func.attr in RUNTIME_TOOLS
        ):
            calls.add(func.attr)
    return calls


def _runtime_tool_signature_issues(tree: ast.AST) -> list[str]:
    issues: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        tool_name = _runtime_tool_name(node)
        if tool_name is None or tool_name not in TOOL_SIGNATURES:
            continue
        signature = TOOL_SIGNATURES[tool_name]
        required = signature["required"]
        allowed = signature["allowed"]
        keyword_names = {keyword.arg for keyword in node.keywords if keyword.arg is not None}
        unexpected = sorted(keyword_names - allowed)
        if unexpected:
            issues.append(f"tools.{tool_name} uses unsupported keyword argument(s): {', '.join(unexpected)}")
        positional_count = len(node.args)
        missing_required = [
            name
            for index, name in enumerate(required)
            if positional_count <= index and name not in keyword_names
        ]
        if missing_required:
            issues.append(f"tools.{tool_name} missing required argument(s): {', '.join(missing_required)}")
    return issues


def _runtime_tool_name(node: ast.Call) -> str | None:
    func = node.func
    if (
        isinstance(func, ast.Attribute)
        and isinstance(func.value, ast.Name)
        and func.value.id == "tools"
        and func.attr in RUNTIME_TOOLS
    ):
        return func.attr
    return None


def _expected_runtime_tools(request: dict) -> set[str]:
    trajectory = request.get("trajectory")
    if not isinstance(trajectory, dict):
        return set()
    steps = trajectory.get("steps")
    if not isinstance(steps, list):
        return set()
    expected: set[str] = set()
    for step in steps:
        if not isinstance(step, dict):
            continue
        tool_name = step.get("tool_name")
        if isinstance(tool_name, str) and tool_name in RUNTIME_TOOLS:
            expected.add(tool_name)
    return expected


def _expected_input_names(request: dict) -> set[str]:
    input_schema = request.get("input_schema")
    if not isinstance(input_schema, dict):
        return set()
    return {
        key
        for key, value in input_schema.items()
        if isinstance(key, str)
        and key
        and key not in {"task_input"}
        and isinstance(value, str)
    }


def _exposed_kwargs(tree: ast.AST) -> set[str]:
    keys: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and _is_kwargs_get(node.func) and node.args:
            key = _literal_string(node.args[0])
            if key:
                keys.add(key)
        if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name) and node.value.id == "kwargs":
            key = _literal_string(node.slice)
            if key:
                keys.add(key)
    return keys


def _is_kwargs_get(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Attribute)
        and node.attr == "get"
        and isinstance(node.value, ast.Name)
        and node.value.id == "kwargs"
    )


def _literal_string(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
