import json
import os
from dataclasses import asdict
from pathlib import Path

from skill_runtime.api.models import Trajectory
from skill_runtime.distill.fallback.command_provider import CommandFallbackProvider
from skill_runtime.distill.fallback.mock_provider import MockFallbackProvider
from skill_runtime.distill.fallback.prompt_builder import (
    build_fallback_prompt,
    build_provider_guidance,
)
from skill_runtime.distill.fallback.provider import FallbackRequest, FallbackResponse


class FallbackService:
    def __init__(self, staging_dir: str | Path, provider=None) -> None:
        self.staging_dir = Path(staging_dir)
        self.staging_dir.mkdir(parents=True, exist_ok=True)
        self.provider = provider or self._default_provider()

    def _default_provider(self):
        command = os.environ.get("SKILL_RUNTIME_FALLBACK_PROVIDER_CMD")
        if command:
            return CommandFallbackProvider(command)
        return MockFallbackProvider()

    def generate(
        self,
        skill_name: str,
        summary: str,
        docstring: str,
        trajectory: Trajectory,
        input_schema: dict[str, str],
    ) -> tuple[str, str, str]:
        provider_guidance = build_provider_guidance(summary, trajectory)
        prompt = build_fallback_prompt(
            skill_name,
            summary,
            docstring,
            trajectory,
            input_schema,
            provider_guidance,
        )
        request = FallbackRequest(
            skill_name=skill_name,
            summary=summary,
            docstring=docstring,
            trajectory=trajectory,
            input_schema=input_schema,
            provider_guidance=provider_guidance,
            prompt=prompt,
        )
        response = self.provider.generate(request)
        prompt_path = self._write_prompt_artifact(skill_name, request, response)
        return response.code, response.provider_name, str(prompt_path)

    def _write_prompt_artifact(
        self,
        skill_name: str,
        request: FallbackRequest,
        response: FallbackResponse,
    ) -> Path:
        artifact_path = self.staging_dir / f"{skill_name}.fallback.json"
        payload = {
            "request": {
                "skill_name": request.skill_name,
                "summary": request.summary,
                "docstring": request.docstring,
                "input_schema": request.input_schema,
                "provider_guidance": request.provider_guidance,
                "trajectory_task_id": request.trajectory.task_id,
                "prompt": request.prompt,
            },
            "response": asdict(response),
        }
        artifact_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return artifact_path
