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
    schema_source: str | None = None
    tags: list[str] = field(default_factory=list)
    scope_policy: dict[str, Any] | None = None


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


@dataclass
class AgentTaskRequest:
    task_description: str
    working_directory: str | None = None
    known_inputs: dict[str, Any] = field(default_factory=dict)
    expected_outputs: list[str] = field(default_factory=list)
    risk_level: str = "medium"
    task_kind: str = "workflow"
    allow_silent_reuse: bool = True
    allow_learning: bool = True


@dataclass
class CodexTaskClassification:
    bucket: str
    reason: str
    matched_signals: list[str] = field(default_factory=list)


@dataclass
class ReuseDecision:
    decision: str
    reason: str
    skill_name: str | None = None
    search_query: str | None = None
    search_score: float | None = None
    missing_inputs: list[str] = field(default_factory=list)


@dataclass
class LearningDecision:
    decision: str
    reason: str
    related_skill_name: str | None = None
    should_capture_trajectory: bool = False
    should_distill_now: bool = False


@dataclass
class AgentOrchestrationResult:
    request: AgentTaskRequest
    reuse_decision: ReuseDecision
    learning_decision: LearningDecision | None = None
    task_classification: CodexTaskClassification | None = None
    runtime_lane_status: str | None = None
    runtime_lane_reason: str | None = None
    selected_skill_name: str | None = None
    selected_skill_args: dict[str, Any] = field(default_factory=dict)
    execution_payload: dict[str, Any] | None = None
    learning_capture_payload: dict[str, Any] | None = None
    recommended_next_action: str | None = None
    recommended_reason: str | None = None
    recommended_host_operation: dict[str, Any] | None = None
    available_host_operations: list[dict[str, Any]] = field(default_factory=list)
