from dataclasses import dataclass
from typing import Protocol

from skill_runtime.api.models import Trajectory
from skill_runtime.audit.semantic_checks import SemanticIssue


@dataclass
class SemanticReviewRequest:
    file_path: str
    source: str
    trajectory: Trajectory | None
    heuristic_issues: list[SemanticIssue]
    prompt: str


@dataclass
class SemanticReviewResponse:
    provider_name: str
    summary: str
    issues: list[SemanticIssue]


class SemanticReviewProvider(Protocol):
    def review(self, request: SemanticReviewRequest) -> SemanticReviewResponse:
        ...
