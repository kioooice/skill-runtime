import json
import os
import shlex
import subprocess
from dataclasses import asdict
from typing import Any

from skill_runtime.audit.semantic_checks import SemanticIssue
from skill_runtime.audit.semantic_provider import SemanticReviewRequest, SemanticReviewResponse

PROVIDER_TIMEOUT_SECONDS = 60


class CommandSemanticReviewProvider:
    provider_name = "command_semantic_review_provider"

    def __init__(self, command: str) -> None:
        if not command.strip():
            raise ValueError("semantic provider command must not be empty")
        self.command = command

    def review(self, request: SemanticReviewRequest) -> SemanticReviewResponse:
        payload = {
            "file_path": request.file_path,
            "source": request.source,
            "trajectory": asdict(request.trajectory) if request.trajectory else None,
            "heuristic_issues": [asdict(issue) for issue in request.heuristic_issues],
            "prompt": request.prompt,
        }
        response = self._run(payload)
        provider_name = self._required_str(response, "provider_name")
        summary = self._required_str(response, "summary")
        issues = self._issues(response.get("issues"))
        self.provider_name = provider_name
        return SemanticReviewResponse(
            provider_name=provider_name,
            summary=summary,
            issues=issues,
        )

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
            raise ValueError("semantic provider command timed out") from exc
        if result.returncode != 0:
            raise ValueError(
                "semantic provider command failed: "
                + (result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}")
            )
        try:
            response = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise ValueError("semantic provider command returned invalid JSON") from exc
        if not isinstance(response, dict):
            raise ValueError("semantic provider command must return a JSON object")
        return response

    def _issues(self, payload: Any) -> list[SemanticIssue]:
        if payload is None:
            return []
        if not isinstance(payload, list):
            raise ValueError("semantic provider response field issues must be a list")
        issues: list[SemanticIssue] = []
        for item in payload:
            if not isinstance(item, dict):
                raise ValueError("semantic provider issue must be an object")
            issues.append(
                SemanticIssue(
                    rule_id=self._required_str(item, "rule_id"),
                    severity=self._required_str(item, "severity"),
                    message=self._required_str(item, "message"),
                )
            )
        return issues

    def _required_str(self, payload: dict[str, Any], key: str) -> str:
        value = payload.get(key)
        if not isinstance(value, str) or not value:
            raise ValueError(f"semantic provider response missing string field: {key}")
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
