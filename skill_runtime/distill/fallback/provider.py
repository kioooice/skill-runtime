from dataclasses import dataclass
from typing import Protocol

from skill_runtime.api.models import Trajectory


@dataclass
class FallbackRequest:
    skill_name: str
    summary: str
    docstring: str
    trajectory: Trajectory
    input_schema: dict[str, str]
    prompt: str


@dataclass
class FallbackResponse:
    code: str
    provider_name: str
    reason: str


class FallbackProvider(Protocol):
    def generate(self, request: FallbackRequest) -> FallbackResponse:
        ...
