import json
import os
import shlex
import subprocess
from dataclasses import asdict
from typing import Any

from skill_runtime.distill.fallback.provider import FallbackRequest, FallbackResponse

PROVIDER_TIMEOUT_SECONDS = 60


class CommandFallbackProvider:
    def __init__(self, command: str) -> None:
        if not command.strip():
            raise ValueError("fallback provider command must not be empty")
        self.command = command

    def generate(self, request: FallbackRequest) -> FallbackResponse:
        payload = {
            "skill_name": request.skill_name,
            "summary": request.summary,
            "docstring": request.docstring,
            "input_schema": request.input_schema,
            "trajectory": asdict(request.trajectory),
            "prompt": request.prompt,
        }
        response = self._run(payload)
        code = self._required_str(response, "code")
        provider_name = self._required_str(response, "provider_name")
        reason = self._required_str(response, "reason")
        return FallbackResponse(code=code, provider_name=provider_name, reason=reason)

    def _run(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            result = subprocess.run(
                _command_args(self.command),
                input=json.dumps(payload, ensure_ascii=False),
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
                timeout=PROVIDER_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired as exc:
            raise ValueError("fallback provider command timed out") from exc
        if result.returncode != 0:
            raise ValueError(
                "fallback provider command failed: "
                + (result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}")
            )
        try:
            response = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise ValueError("fallback provider command returned invalid JSON") from exc
        if not isinstance(response, dict):
            raise ValueError("fallback provider command must return a JSON object")
        return response

    def _required_str(self, payload: dict[str, Any], key: str) -> str:
        value = payload.get(key)
        if not isinstance(value, str) or not value:
            raise ValueError(f"fallback provider response missing string field: {key}")
        return value


def _command_args(command: str) -> list[str]:
    try:
        parsed = json.loads(command)
    except json.JSONDecodeError:
        return shlex.split(command, posix=os.name != "nt")
    if not isinstance(parsed, list) or not all(isinstance(item, str) for item in parsed):
        raise ValueError("provider command JSON must be a list of strings")
    if not parsed:
        raise ValueError("provider command JSON must not be empty")
    return parsed
