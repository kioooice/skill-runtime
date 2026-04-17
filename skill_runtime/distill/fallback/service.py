import json
from dataclasses import asdict
from pathlib import Path

from skill_runtime.api.models import Trajectory
from skill_runtime.distill.fallback.mock_provider import MockFallbackProvider
from skill_runtime.distill.fallback.prompt_builder import build_fallback_prompt
from skill_runtime.distill.fallback.provider import FallbackRequest, FallbackResponse


class FallbackService:
    def __init__(self, staging_dir: str | Path, provider=None) -> None:
        self.staging_dir = Path(staging_dir)
        self.staging_dir.mkdir(parents=True, exist_ok=True)
        self.provider = provider or MockFallbackProvider()

    def generate(
        self,
        skill_name: str,
        summary: str,
        docstring: str,
        trajectory: Trajectory,
        input_schema: dict[str, str],
    ) -> tuple[str, str, str]:
        prompt = build_fallback_prompt(skill_name, summary, docstring, trajectory, input_schema)
        request = FallbackRequest(
            skill_name=skill_name,
            summary=summary,
            docstring=docstring,
            trajectory=trajectory,
            input_schema=input_schema,
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
                "trajectory_task_id": request.trajectory.task_id,
                "prompt": request.prompt,
            },
            "response": asdict(response),
        }
        artifact_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return artifact_path
