from dataclasses import dataclass, field
from typing import Any


@dataclass
class TrajectoryStep:
    step_id: str
    tool_name: str
    tool_input: dict[str, Any]
    observation: str
    status: str
    thought_summary: str | None = None


@dataclass
class Trajectory:
    task_id: str
    session_id: str
    task_description: str
    steps: list[TrajectoryStep]
    final_status: str
    artifacts: list[str]
    started_at: str
    ended_at: str


@dataclass
class SkillMetadata:
    skill_name: str
    file_path: str
    summary: str
    docstring: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any]
    source_trajectory_ids: list[str]
    created_at: str
    last_used_at: str | None
    usage_count: int
    status: str
    audit_score: int | None
    rule_name: str | None = None
    rule_priority: int | None = None
    rule_reason: str | None = None
    tags: list[str] = field(default_factory=list)


@dataclass
class AuditReport:
    status: str
    security_score: int
    suggestions: list[str]
    optimized_docstring: str
    refactored_code: str
    static_score: int | None = None
    semantic_score: int | None = None
    static_findings: list[str] = field(default_factory=list)
    semantic_findings: list[str] = field(default_factory=list)
    semantic_summary: str | None = None
    semantic_provider: str | None = None
    semantic_artifact: str | None = None
