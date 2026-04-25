import json
from dataclasses import asdict
from pathlib import Path

from skill_runtime.api.models import Trajectory
from skill_runtime.audit.mock_semantic_provider import MockSemanticReviewProvider
from skill_runtime.audit.semantic_checks import SemanticIssue
from skill_runtime.audit.semantic_prompt_builder import build_semantic_review_prompt
from skill_runtime.audit.semantic_provider import (
    SemanticReviewRequest,
    SemanticReviewResponse,
)


class SemanticReviewService:
    def __init__(self, audits_dir: str | Path, provider=None) -> None:
        self.audits_dir = Path(audits_dir)
        self.audits_dir.mkdir(parents=True, exist_ok=True)
        self.provider = provider or MockSemanticReviewProvider()

    def review(
        self,
        file_path: str | Path,
        source: str,
        heuristic_issues: list[SemanticIssue],
        trajectory: Trajectory | None = None,
    ) -> tuple[list[SemanticIssue], str, str | None]:
        prompt = build_semantic_review_prompt(file_path, source, trajectory, heuristic_issues)
        request = SemanticReviewRequest(
            file_path=str(file_path),
            source=source,
            trajectory=trajectory,
            heuristic_issues=heuristic_issues,
            prompt=prompt,
        )
        response = self.provider.review(request)
        artifact_path = self._write_artifact(file_path, request, response)
        return response.issues, response.summary, str(artifact_path.resolve())

    def _write_artifact(
        self,
        file_path: str | Path,
        request: SemanticReviewRequest,
        response: SemanticReviewResponse,
    ) -> Path:
        artifact_path = self.audits_dir / f"{Path(file_path).stem}.semantic-review.json"
        payload = {
            "request": {
                "file_path": request.file_path,
                "trajectory_task_id": request.trajectory.task_id if request.trajectory else None,
                "heuristic_issues": [asdict(issue) for issue in request.heuristic_issues],
                "prompt": request.prompt,
            },
            "response": {
                "provider_name": response.provider_name,
                "summary": response.summary,
                "issues": [asdict(issue) for issue in response.issues],
            },
        }
        artifact_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return artifact_path
