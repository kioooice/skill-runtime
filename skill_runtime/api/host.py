from __future__ import annotations

from pathlib import Path

from skill_runtime.api.classification import CodexTaskClassifier
from skill_runtime.api.development_feedback import build_development_feedback
from skill_runtime.api.models import (
    AgentOrchestrationResult,
    AgentTaskRequest,
    CodexTaskClassification,
    LearningDecision,
    ReuseDecision,
)
from skill_runtime.api.orchestration import AgentOrchestrationService
from skill_runtime.observability.events import append_runtime_lane_event


def classify_codex_task(request: AgentTaskRequest) -> CodexTaskClassification:
    return CodexTaskClassifier().classify(request)


def start_agent_task(root: str | Path, request: AgentTaskRequest) -> AgentOrchestrationResult:
    return AgentOrchestrationService(root).start_task(request)


def finalize_agent_task(
    root: str | Path,
    plan: AgentOrchestrationResult,
    execution_payload: dict,
) -> AgentOrchestrationResult:
    return AgentOrchestrationService(root).finalize_task(plan, execution_payload)


def run_agent_task(root: str | Path, request: AgentTaskRequest) -> AgentOrchestrationResult:
    return AgentOrchestrationService(root).run_task(request)


def start_codex_task(root: str | Path, request: AgentTaskRequest) -> AgentOrchestrationResult:
    classification = classify_codex_task(request)
    if classification.bucket != "default-in":
        return _record_runtime_lane_event(root, _blocked_codex_result(root, request, classification))
    result = AgentOrchestrationService(root).start_task(request)
    return _record_runtime_lane_event(
        root,
        _with_classification(
            root,
            result,
            classification,
            runtime_lane_status="entered",
            runtime_lane_reason=_entered_runtime_lane_reason(result),
        ),
    )


def finalize_codex_task(
    root: str | Path,
    plan: AgentOrchestrationResult,
    execution_payload: dict,
) -> AgentOrchestrationResult:
    classification = plan.task_classification or classify_codex_task(plan.request)
    if classification.bucket != "default-in":
        return _record_runtime_lane_event(
            root,
            AgentOrchestrationResult(
                request=plan.request,
                reuse_decision=plan.reuse_decision,
                learning_decision=LearningDecision(
                    "skip",
                    f"task bucket {classification.bucket} stays outside Codex default runtime finalization",
                ),
                task_classification=classification,
                selected_skill_name=plan.selected_skill_name,
                selected_skill_args=dict(plan.selected_skill_args),
                development_feedback=list(plan.development_feedback),
                execution_payload=execution_payload,
                learning_capture_payload=None,
                runtime_lane_status="skipped",
                runtime_lane_reason=(
                    f"task bucket {classification.bucket} skipped Codex runtime lane finalization: "
                    f"{classification.reason}"
                ),
                recommended_next_action=None,
                recommended_reason=None,
                recommended_host_operation=None,
                available_host_operations=[],
            ),
        )
    result = AgentOrchestrationService(root).finalize_task(plan, execution_payload)
    return _record_runtime_lane_event(
        root,
        _with_classification(
            root,
            result,
            classification,
            runtime_lane_status="used" if result.learning_capture_payload else "entered",
            runtime_lane_reason=_finalize_runtime_lane_reason(result),
        ),
    )


def run_codex_task(root: str | Path, request: AgentTaskRequest) -> AgentOrchestrationResult:
    classification = classify_codex_task(request)
    if classification.bucket != "default-in":
        return _record_runtime_lane_event(root, _blocked_codex_result(root, request, classification))
    result = AgentOrchestrationService(root).run_task(request)
    return _record_runtime_lane_event(
        root,
        _with_classification(
            root,
            result,
            classification,
            runtime_lane_status="used" if result.execution_payload or result.learning_capture_payload else "entered",
            runtime_lane_reason=_run_runtime_lane_reason(result),
        ),
    )


def _blocked_codex_result(
    root: str | Path,
    request: AgentTaskRequest,
    classification: CodexTaskClassification,
) -> AgentOrchestrationResult:
    return AgentOrchestrationResult(
        request=request,
        reuse_decision=ReuseDecision("skip", classification.reason),
        learning_decision=None,
        task_classification=classification,
        selected_skill_name=None,
        selected_skill_args={},
        execution_payload=None,
        learning_capture_payload=None,
        runtime_lane_status="skipped",
        runtime_lane_reason=f"task bucket {classification.bucket} skipped Codex runtime lane: {classification.reason}",
        development_feedback=build_development_feedback(request, classification, root=root),
        recommended_next_action=None,
        recommended_reason=None,
        recommended_host_operation=None,
        available_host_operations=[],
    )


def _with_classification(
    root: str | Path,
    result: AgentOrchestrationResult,
    classification: CodexTaskClassification,
    *,
    runtime_lane_status: str | None = None,
    runtime_lane_reason: str | None = None,
) -> AgentOrchestrationResult:
    return AgentOrchestrationResult(
        request=result.request,
        reuse_decision=result.reuse_decision,
        learning_decision=result.learning_decision,
        task_classification=classification,
        runtime_lane_status=runtime_lane_status or result.runtime_lane_status,
        runtime_lane_reason=runtime_lane_reason or result.runtime_lane_reason,
        development_feedback=build_development_feedback(result.request, classification, root=root),
        selected_skill_name=result.selected_skill_name,
        selected_skill_args=dict(result.selected_skill_args),
        execution_payload=result.execution_payload,
        learning_capture_payload=result.learning_capture_payload,
        recommended_next_action=result.recommended_next_action,
        recommended_reason=result.recommended_reason,
        recommended_host_operation=result.recommended_host_operation,
        available_host_operations=list(result.available_host_operations),
    )


def _record_runtime_lane_event(root: str | Path, result: AgentOrchestrationResult) -> AgentOrchestrationResult:
    append_runtime_lane_event(root, result)
    return result


def _entered_runtime_lane_reason(result: AgentOrchestrationResult) -> str:
    return f"task entered Codex runtime lane; reuse decision: {result.reuse_decision.decision}"


def _run_runtime_lane_reason(result: AgentOrchestrationResult) -> str:
    if result.execution_payload:
        if result.selected_skill_name:
            return (
                "task entered Codex runtime lane and auto-executed reusable skill "
                f"{result.selected_skill_name}"
            )
        return "task entered Codex runtime lane and produced an execution payload"
    if result.learning_capture_payload:
        return "task entered Codex runtime lane and captured learning payload"
    return _entered_runtime_lane_reason(result)


def _finalize_runtime_lane_reason(result: AgentOrchestrationResult) -> str:
    if result.learning_capture_payload:
        return "task finalized through Codex runtime lane and captured learning payload"
    if result.learning_decision:
        return f"task finalized through Codex runtime lane; learning decision: {result.learning_decision.decision}"
    return _entered_runtime_lane_reason(result)
