import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from tests.runtime_test_support import ROOT


class RuntimeDeepSeekProviderExampleTestsMixin:
    def test_deepseek_fallback_provider_uses_chat_completion_contract(self) -> None:
        response_content = {
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
                "    return {'status': 'completed'}\n"
            ),
            "provider_name": "deepseek_fallback_provider",
        }
        with _fake_deepseek_server(response_content) as server:
            result = _run_provider_script(
                ROOT / "examples" / "providers" / "deepseek_fallback_provider.py",
                {
                    "skill_name": "deepseek_contract_test",
                    "summary": "Generate a simple skill.",
                    "docstring": "A simple skill.",
                    "input_schema": {
                        "input_path": "str",
                        "output_path": "str",
                        "metadata_path": "str",
                    },
                    "trajectory": {
                        "steps": [
                            {"tool_name": "copy_file", "tool_input": {}},
                            {"tool_name": "write_json", "tool_input": {}},
                        ]
                    },
                    "prompt": "Generate a simple skill.",
                },
                server.url,
            )

        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual("deepseek_fallback_provider", payload["provider_name"])
        self.assertEqual("DeepSeek generated a candidate skill from the fallback prompt.", payload["reason"])
        self.assertIn("def run", payload["code"])
        self.assertEqual("/chat/completions", server.received_path)
        self.assertEqual("Bearer test-deepseek-key", server.received_headers["Authorization"])
        self.assertEqual("deepseek-v4-flash", server.received_body["model"])
        self.assertEqual({"type": "json_object"}, server.received_body["response_format"])
        system_prompt = server.received_body["messages"][0]["content"]
        self.assertIn("功能描述", system_prompt)
        self.assertIn("tools.copy_file", system_prompt)

    def test_deepseek_fallback_provider_blocks_low_quality_candidate(self) -> None:
        response_content = {
            "code": "def run(tools, **kwargs):\n    return {'status': 'completed'}\n",
            "provider_name": "deepseek_fallback_provider",
        }
        with _fake_deepseek_server(response_content) as server:
            result = _run_provider_script(
                ROOT / "examples" / "providers" / "deepseek_fallback_provider.py",
                {
                    "skill_name": "deepseek_quality_gate_test",
                    "summary": "Copy a file and write metadata.",
                    "docstring": "Copy a file and write metadata.",
                    "input_schema": {
                        "input_path": "str",
                        "output_path": "str",
                        "metadata_path": "str",
                    },
                    "trajectory": {
                        "steps": [
                            {"tool_name": "copy_file", "tool_input": {}},
                            {"tool_name": "write_json", "tool_input": {}},
                        ]
                    },
                    "prompt": "Generate a copy metadata skill.",
                },
                server.url,
            )

        self.assertNotEqual(0, result.returncode)
        self.assertIn("failed quality gate", result.stderr)
        self.assertIn("missing runtime tool calls", result.stderr)

    def test_deepseek_fallback_provider_requires_schema_kwargs(self) -> None:
        response_content = {
            "code": (
                "def run(tools, **kwargs):\n"
                "    \"\"\"\n"
                "    功能描述:\n"
                "        Copy one file and write metadata.\n\n"
                "    输入参数:\n"
                "        - source_path: source file\n"
                "        - destination_path: destination file\n"
                "        - metadata_path: metadata sidecar\n\n"
                "    输出结果:\n"
                "        - status and artifacts\n"
                "    \"\"\"\n"
                "    source_path = kwargs.get('source_path')\n"
                "    destination_path = kwargs.get('destination_path')\n"
                "    metadata_path = kwargs.get('metadata_path')\n"
                "    copied_path = tools.copy_file(source_path, destination_path)\n"
                "    tools.write_json(metadata_path, {'copied_path': copied_path})\n"
                "    return {'status': 'completed'}\n"
            ),
            "provider_name": "deepseek_fallback_provider",
        }
        with _fake_deepseek_server(response_content) as server:
            result = _run_provider_script(
                ROOT / "examples" / "providers" / "deepseek_fallback_provider.py",
                {
                    "skill_name": "deepseek_schema_gate_test",
                    "summary": "Copy a file and write metadata.",
                    "docstring": "Copy a file and write metadata.",
                    "input_schema": {
                        "input_path": "str",
                        "output_path": "str",
                        "metadata_path": "str",
                    },
                    "trajectory": {
                        "steps": [
                            {"tool_name": "copy_file", "tool_input": {}},
                            {"tool_name": "write_json", "tool_input": {}},
                        ]
                    },
                    "prompt": "Generate a copy metadata skill.",
                },
                server.url,
            )

        self.assertNotEqual(0, result.returncode)
        self.assertIn("missing kwargs for inferred inputs", result.stderr)
        self.assertIn("input_path", result.stderr)
        self.assertIn("output_path", result.stderr)

    def test_deepseek_fallback_provider_blocks_invalid_runtime_tool_signature(self) -> None:
        response_content = {
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
                "    tools.write_json(metadata_path=metadata_path)\n"
                "    return {'status': 'completed'}\n"
            ),
            "provider_name": "deepseek_fallback_provider",
        }
        with _fake_deepseek_server(response_content) as server:
            result = _run_provider_script(
                ROOT / "examples" / "providers" / "deepseek_fallback_provider.py",
                {
                    "skill_name": "deepseek_signature_gate_test",
                    "summary": "Copy a file and write metadata.",
                    "docstring": "Copy a file and write metadata.",
                    "input_schema": {
                        "input_path": "str",
                        "output_path": "str",
                        "metadata_path": "str",
                    },
                    "trajectory": {
                        "steps": [
                            {"tool_name": "copy_file", "tool_input": {}},
                            {"tool_name": "write_json", "tool_input": {}},
                        ]
                    },
                    "prompt": "Generate a copy metadata skill.",
                },
                server.url,
            )

        self.assertNotEqual(0, result.returncode)
        self.assertIn("unsupported keyword argument", result.stderr)
        self.assertIn("destination_path", result.stderr)
        self.assertIn("missing required argument", result.stderr)
        self.assertIn("data", result.stderr)

    def test_deepseek_fallback_provider_repairs_candidate_once(self) -> None:
        invalid_response = {
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
                "    tools.write_json(metadata_path=metadata_path)\n"
                "    return {'status': 'completed'}\n"
            ),
            "provider_name": "deepseek_fallback_provider",
        }
        repaired_response = {
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
                "    return {'status': 'completed'}\n"
            ),
            "provider_name": "deepseek_fallback_provider",
            "reason": "Fixed signatures.",
        }
        with _fake_deepseek_server([invalid_response, repaired_response]) as server:
            result = _run_provider_script(
                ROOT / "examples" / "providers" / "deepseek_fallback_provider.py",
                {
                    "skill_name": "deepseek_repair_gate_test",
                    "summary": "Copy a file and write metadata.",
                    "docstring": "Copy a file and write metadata.",
                    "input_schema": {
                        "input_path": "str",
                        "output_path": "str",
                        "metadata_path": "str",
                    },
                    "trajectory": {
                        "steps": [
                            {"tool_name": "copy_file", "tool_input": {}},
                            {"tool_name": "write_json", "tool_input": {}},
                        ]
                    },
                    "prompt": "Generate a copy metadata skill.",
                },
                server.url,
            )

        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertIn("tools.copy_file(input_path, output_path)", payload["code"])
        self.assertIn("Repaired after quality gate failure", payload["reason"])
        self.assertEqual(2, server.request_count)
        repair_prompt = server.received_bodies[1]["messages"][1]["content"]
        self.assertIn("Quality gate failure", repair_prompt)
        self.assertIn("destination_path", repair_prompt)
        self.assertIn("target_path", repair_prompt)

    def test_deepseek_fallback_provider_can_disable_repair(self) -> None:
        response_content = {
            "code": (
                "def run(tools, **kwargs):\n"
                "    \"\"\"\n"
                "    功能描述:\n"
                "        Copy one file.\n\n"
                "    输入参数:\n"
                "        - input_path: source file\n"
                "        - output_path: destination file\n\n"
                "    输出结果:\n"
                "        - status and artifacts\n"
                "    \"\"\"\n"
                "    input_path = kwargs.get('input_path')\n"
                "    output_path = kwargs.get('output_path')\n"
                "    tools.copy_file(source_path=input_path, destination_path=output_path)\n"
                "    return {'status': 'completed'}\n"
            ),
            "provider_name": "deepseek_fallback_provider",
        }
        with _fake_deepseek_server(response_content) as server:
            result = _run_provider_script(
                ROOT / "examples" / "providers" / "deepseek_fallback_provider.py",
                {
                    "skill_name": "deepseek_repair_disabled_test",
                    "summary": "Copy a file.",
                    "docstring": "Copy a file.",
                    "input_schema": {
                        "input_path": "str",
                        "output_path": "str",
                    },
                    "trajectory": {
                        "steps": [
                            {"tool_name": "copy_file", "tool_input": {}},
                        ]
                    },
                    "prompt": "Generate a copy skill.",
                },
                server.url,
                extra_env={"DEEPSEEK_REPAIR_ATTEMPTS": "0"},
            )

        self.assertNotEqual(0, result.returncode)
        self.assertIn("failed quality gate", result.stderr)
        self.assertEqual(1, server.request_count)

    def test_deepseek_fallback_provider_normalizes_escaped_code_string(self) -> None:
        code = (
            'def run(tools, **kwargs):\\n'
            '    \\"\\"\\"\\n'
            '    功能描述:\\n'
            '        Copy one file and write metadata.\\n\\n'
            '    输入参数:\\n'
            '        - input_path: source file\\n'
            '        - output_path: destination file\\n'
            '        - metadata_path: metadata sidecar\\n\\n'
            '    输出结果:\\n'
            '        - status and artifacts\\n'
            '    \\"\\"\\"\\n'
            "    input_path = kwargs.get('input_path')\\n"
            "    output_path = kwargs.get('output_path')\\n"
            "    metadata_path = kwargs.get('metadata_path')\\n"
            "    copied_path = tools.copy_file(input_path, output_path)\\n"
            "    tools.write_json(metadata_path, {'copied_path': copied_path})\\n"
            "    return {'status': 'completed'}\\n"
        )
        response_content = {
            "code": code,
            "provider_name": "deepseek_fallback_provider",
        }
        with _fake_deepseek_server(response_content) as server:
            result = _run_provider_script(
                ROOT / "examples" / "providers" / "deepseek_fallback_provider.py",
                {
                    "skill_name": "deepseek_escaped_code_gate_test",
                    "summary": "Copy a file and write metadata.",
                    "docstring": "Copy a file and write metadata.",
                    "input_schema": {
                        "input_path": "str",
                        "output_path": "str",
                        "metadata_path": "str",
                    },
                    "trajectory": {
                        "steps": [
                            {"tool_name": "copy_file", "tool_input": {}},
                            {"tool_name": "write_json", "tool_input": {}},
                        ]
                    },
                    "prompt": "Generate a copy metadata skill.",
                },
                server.url,
            )

        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertIn("\n", payload["code"])
        self.assertNotIn("\\n", payload["code"])

    def test_deepseek_semantic_provider_uses_chat_completion_contract(self) -> None:
        response_content = {
            "provider_name": "deepseek_semantic_review_provider",
            "summary": "No blocking issue.",
            "issues": [],
        }
        with _fake_deepseek_server(response_content) as server:
            result = _run_provider_script(
                ROOT / "examples" / "providers" / "deepseek_semantic_review_provider.py",
                {
                    "file_path": "skill_store/staging/example.py",
                    "source": "def run(tools, **kwargs):\n    return {'status': 'completed'}",
                    "trajectory": None,
                    "heuristic_issues": [],
                    "prompt": "Review candidate.",
                },
                server.url,
            )

        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual("deepseek_semantic_review_provider", payload["provider_name"])
        self.assertEqual([], payload["issues"])
        self.assertEqual("/chat/completions", server.received_path)
        self.assertEqual("Bearer test-deepseek-key", server.received_headers["Authorization"])
        self.assertEqual("deepseek-v4-flash", server.received_body["model"])
        self.assertEqual({"type": "json_object"}, server.received_body["response_format"])
        system_prompt = server.received_body["messages"][0]["content"]
        self.assertIn("Use medium for docstring", system_prompt)
        self.assertIn("do not add high-severity issues", system_prompt)


class _FakeDeepSeekServer:
    def __init__(self, response_content: dict | list[dict]) -> None:
        self.response_contents = response_content if isinstance(response_content, list) else [response_content]
        self.received_path: str | None = None
        self.received_headers: dict[str, str] = {}
        self.received_body: dict = {}
        self.received_bodies: list[dict] = []
        self.request_count = 0
        self._server: HTTPServer | None = None
        self._thread: threading.Thread | None = None
        self.url = ""

    def __enter__(self):
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self) -> None:
                content_length = int(self.headers.get("Content-Length", "0"))
                body = self.rfile.read(content_length).decode("utf-8")
                owner.received_path = self.path
                owner.received_headers = dict(self.headers.items())
                owner.received_body = json.loads(body)
                owner.received_bodies.append(owner.received_body)
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

            def log_message(self, format: str, *args) -> None:
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


def _fake_deepseek_server(response_content: dict | list[dict]) -> _FakeDeepSeekServer:
    return _FakeDeepSeekServer(response_content)


def _run_provider_script(
    script_path: Path,
    request: dict,
    base_url: str,
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.update(
        {
            "DEEPSEEK_API_KEY": "test-deepseek-key",
            "DEEPSEEK_API_BASE": base_url,
            "DEEPSEEK_MODEL": "deepseek-v4-flash",
            "PYTHONIOENCODING": "utf-8",
        }
    )
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        [sys.executable, str(script_path)],
        input=json.dumps(request, ensure_ascii=False),
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        check=False,
        timeout=30,
    )
