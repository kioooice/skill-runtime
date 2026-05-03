from dataclasses import asdict
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from skill_runtime.api.host import (
    finalize_agent_task,
    finalize_codex_task,
    run_agent_task,
    run_codex_task,
)
from skill_runtime.api.models import (
    AgentOrchestrationResult,
    AgentTaskRequest,
    CodexTaskClassification,
    LearningDecision,
    ReuseDecision,
)
from skill_runtime.api.service import RuntimeService, RuntimeServiceError
from skill_runtime.observability.events import build_global_runtime_events_payload, build_runtime_events_payload


def _wrap_tool(service: RuntimeService, handler_name: str, **kwargs: Any) -> dict[str, Any]:
    try:
        data = getattr(service, handler_name)(**kwargs)
    except RuntimeServiceError as exc:
        return {
            "status": "error",
            "message": exc.message,
            "code": exc.code,
            "details": exc.details,
        }
    return {"status": "ok", "data": data}


def _wrap_agent_host_tool(handler, **kwargs: Any) -> dict[str, Any]:
    try:
        data = handler(**kwargs)
    except RuntimeServiceError as exc:
        return {
            "status": "error",
            "message": exc.message,
            "code": exc.code,
            "details": exc.details,
        }
    return {"status": "ok", "data": asdict(data)}


def _agent_result_from_payload(raw_plan: dict[str, Any]) -> AgentOrchestrationResult:
    raw_request = raw_plan.get("request")
    raw_reuse = raw_plan.get("reuse_decision")
    raw_learning = raw_plan.get("learning_decision")
    if not isinstance(raw_request, dict) or not isinstance(raw_reuse, dict):
        raise RuntimeServiceError(
            "plan payload must contain request and reuse_decision objects",
            "INVALID_AGENT_PLAN",
        )
    if not isinstance(raw_plan.get("selected_skill_args", {}), dict):
        raise RuntimeServiceError(
            "selected_skill_args must be an object",
            "INVALID_AGENT_PLAN",
        )

    return AgentOrchestrationResult(
        request=AgentTaskRequest(**raw_request),
        reuse_decision=ReuseDecision(**raw_reuse),
        learning_decision=LearningDecision(**raw_learning) if isinstance(raw_learning, dict) else None,
        task_classification=CodexTaskClassification(**raw_plan["task_classification"])
        if isinstance(raw_plan.get("task_classification"), dict)
        else None,
        runtime_lane_status=raw_plan.get("runtime_lane_status")
        if isinstance(raw_plan.get("runtime_lane_status"), str)
        else None,
        runtime_lane_reason=raw_plan.get("runtime_lane_reason")
        if isinstance(raw_plan.get("runtime_lane_reason"), str)
        else None,
        selected_skill_name=raw_plan.get("selected_skill_name")
        if isinstance(raw_plan.get("selected_skill_name"), str)
        else None,
        selected_skill_args=dict(raw_plan.get("selected_skill_args", {})),
        execution_payload=raw_plan.get("execution_payload")
        if isinstance(raw_plan.get("execution_payload"), dict)
        else None,
        learning_capture_payload=raw_plan.get("learning_capture_payload")
        if isinstance(raw_plan.get("learning_capture_payload"), dict)
        else None,
    )


def build_mcp_server(root: str | Path) -> FastMCP:
    service = RuntimeService(root)
    server = FastMCP(
        name="skill-runtime",
        instructions=(
            "Codex-compatible self-evolving skill runtime. "
            "Use these tools to search, distill, audit, promote, execute, and govern local skills."
        ),
    )

    @server.tool(
        name="search_skill",
        description="Search the local active skill index for reusable skills relevant to a task.",
        structured_output=True,
    )
    def search_skill(query: str, top_k: int = 5) -> dict[str, Any]:
        return _wrap_tool(service, "search", query=query, top_k=top_k)

    @server.tool(
        name="execute_skill",
        description="Execute an active skill by name with structured keyword arguments.",
        structured_output=True,
    )
    def execute_skill(skill_name: str, args: dict[str, Any], dry_run: bool = False) -> dict[str, Any]:
        return _wrap_tool(service, "execute", skill_name=skill_name, args=args, dry_run=dry_run)

    @server.tool(
        name="rollback_operations",
        description="Rollback safe file changes described by an execution operation log.",
        structured_output=True,
    )
    def rollback_operations(
        operation_log: list[dict[str, Any]],
        operation_ids: list[str] | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        return _wrap_tool(
            service,
            "rollback_operations",
            operation_log=operation_log,
            operation_ids=operation_ids,
            dry_run=dry_run,
        )

    @server.tool(
        name="distill_trajectory",
        description="Distill a successful trajectory JSON file into a staging skill and metadata draft.",
        structured_output=True,
    )
    def distill_trajectory(trajectory_path: str, skill_name: str | None = None) -> dict[str, Any]:
        return _wrap_tool(service, "distill", trajectory_path=trajectory_path, skill_name=skill_name)

    @server.tool(
        name="distill_and_promote_candidate",
        description=(
            "Run the full reusable-skill pipeline for a trajectory: "
            "register it, distill it, audit it, and promote it if the audit passes."
        ),
        structured_output=True,
    )
    def distill_and_promote_candidate(
        trajectory_path: str | None = None,
        observed_task_path: str | None = None,
        observed_task: dict[str, Any] | None = None,
        skill_name: str | None = None,
        register_trajectory: bool = True,
        promotion_target: str = "active",
        global_skills_dir: str | None = None,
        global_skill_name: str | None = None,
        overwrite_global_skill: bool = False,
    ) -> dict[str, Any]:
        return _wrap_tool(
            service,
            "distill_and_promote",
            trajectory_path=trajectory_path,
            observed_task_path=observed_task_path,
            observed_task=observed_task,
            skill_name=skill_name,
            register_trajectory=register_trajectory,
            promotion_target=promotion_target,
            global_skills_dir=global_skills_dir,
            global_skill_name=global_skill_name,
            overwrite_global_skill=overwrite_global_skill,
        )

    @server.tool(
        name="audit_skill",
        description="Audit a staging skill for safety, generalization, atomicity, and retrievability.",
        structured_output=True,
    )
    def audit_skill(file_path: str, trajectory_path: str | None = None) -> dict[str, Any]:
        return _wrap_tool(service, "audit", file_path=file_path, trajectory_path=trajectory_path)

    @server.tool(
        name="promote_skill",
        description="Promote a staging skill into the active library after a passing audit report exists.",
        structured_output=True,
    )
    def promote_skill(file_path: str) -> dict[str, Any]:
        return _wrap_tool(service, "promote", file_path=file_path)

    @server.tool(
        name="promote_global_codex_skill",
        description=(
            "Promote a passing staging workflow skill into the global Codex skill library "
            "without creating a project active-skill copy."
        ),
        structured_output=True,
    )
    def promote_global_codex_skill(
        file_path: str,
        global_skills_dir: str | None = None,
        global_skill_name: str | None = None,
        overwrite: bool = False,
    ) -> dict[str, Any]:
        return _wrap_tool(
            service,
            "promote_to_global_codex_skill",
            file_path=file_path,
            global_skills_dir=global_skills_dir,
            global_skill_name=global_skill_name,
            overwrite=overwrite,
        )

    @server.tool(
        name="log_trajectory",
        description="Validate and register a trajectory JSON file into the local trajectory store.",
        structured_output=True,
    )
    def log_trajectory(file_path: str) -> dict[str, Any]:
        return _wrap_tool(service, "log_trajectory", file_path=file_path)

    @server.tool(
        name="capture_trajectory",
        description=(
            "Convert a lightweight observed task record into a full trajectory JSON file "
            "that can be used for distillation."
        ),
        structured_output=True,
    )
    def capture_trajectory(
        file_path: str | None = None,
        observed_task: dict[str, Any] | None = None,
        task_id: str | None = None,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        return _wrap_tool(
            service,
            "capture_trajectory",
            file_path=file_path,
            observed_task=observed_task,
            task_id=task_id,
            session_id=session_id,
        )

    @server.tool(
        name="reindex_skills",
        description="Rebuild the active skill index from metadata files in the active skill store.",
        structured_output=True,
    )
    def reindex_skills() -> dict[str, Any]:
        return _wrap_tool(service, "reindex")

    @server.tool(
        name="backfill_skill_provenance",
        description="Backfill missing rule provenance for legacy active skills and update the index.",
        structured_output=True,
    )
    def backfill_skill_provenance() -> dict[str, Any]:
        return _wrap_tool(service, "backfill_provenance")

    @server.tool(
        name="governance_report",
        description="Summarize library status counts and lightweight duplicate candidates for governance work.",
        structured_output=True,
    )
    def governance_report() -> dict[str, Any]:
        return _wrap_tool(service, "governance_report")

    @server.tool(
        name="distill_coverage_report",
        description="Summarize deterministic rule coverage and remaining fallback hotspots across saved trajectories.",
        structured_output=True,
    )
    def distill_coverage_report(
        observed_task_scope: str = "all",
        max_family_items: int | None = None,
        min_family_count: int = 1,
    ) -> dict[str, Any]:
        return _wrap_tool(
            service,
            "distill_coverage_report",
            observed_task_scope=observed_task_scope,
            max_family_items=max_family_items,
            min_family_count=min_family_count,
        )

    @server.tool(
        name="review_evolution_candidate",
        description=(
            "Review a skill evolution candidate and produce a manual diff proposal, "
            "a rejection, or a request for more evidence without editing global skills."
        ),
        structured_output=True,
    )
    def review_evolution_candidate(
        candidate: str,
        global_skills_dir: str | None = None,
    ) -> dict[str, Any]:
        return _wrap_tool(
            service,
            "review_evolution_candidate",
            candidate=candidate,
            global_skills_dir=global_skills_dir,
        )

    @server.tool(
        name="apply_evolution_candidate",
        description=(
            "Apply a reviewed skill evolution candidate only when confirm_apply=true, "
            "with stale target checks, backup creation, and candidate status tracking."
        ),
        structured_output=True,
    )
    def apply_evolution_candidate(
        candidate: str,
        confirm_apply: bool = False,
        global_skills_dir: str | None = None,
    ) -> dict[str, Any]:
        return _wrap_tool(
            service,
            "apply_evolution_candidate",
            candidate=candidate,
            confirm_apply=confirm_apply,
            global_skills_dir=global_skills_dir,
        )

    @server.tool(
        name="rollback_evolution_candidate",
        description=(
            "Rollback an applied skill evolution candidate only when confirm_rollback=true, "
            "restoring the recorded backup after checking the target was not changed after apply."
        ),
        structured_output=True,
    )
    def rollback_evolution_candidate(
        candidate: str,
        confirm_rollback: bool = False,
        global_skills_dir: str | None = None,
    ) -> dict[str, Any]:
        return _wrap_tool(
            service,
            "rollback_evolution_candidate",
            candidate=candidate,
            confirm_rollback=confirm_rollback,
            global_skills_dir=global_skills_dir,
        )

    @server.tool(
        name="archive_duplicate_candidates",
        description="Archive duplicate-candidate skills suggested by the governance report while keeping canonical skills active.",
        structured_output=True,
    )
    def archive_duplicate_candidates(
        skill_names: list[str] | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        return _wrap_tool(
            service,
            "archive_duplicate_candidates",
            skill_names=skill_names,
            dry_run=dry_run,
        )

    @server.tool(
        name="archive_fixture_skills",
        description="Archive active fixture skills and return a governance follow-up recommendation.",
        structured_output=True,
    )
    def archive_fixture_skills(
        skill_names: list[str] | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        return _wrap_tool(
            service,
            "archive_fixture_skills",
            skill_names=skill_names,
            dry_run=dry_run,
        )

    @server.tool(
        name="archive_cold_skills",
        description="Archive cold active skills older than the given day threshold and return a governance refresh follow-up.",
        structured_output=True,
    )
    def archive_cold_skills(days: int = 30) -> dict[str, Any]:
        return _wrap_tool(service, "archive_cold", days=days)

    @server.tool(
        name="runtime_events",
        description=(
            "Read recent runtime lane events, including lane status and learning follow-up actions. "
            "Set global_events=true with scan_roots to aggregate sibling project event logs."
        ),
        structured_output=True,
    )
    def runtime_events(
        limit: int = 20,
        global_events: bool = False,
        scan_roots: list[str] | None = None,
    ) -> dict[str, Any]:
        resolved_root = Path(root).resolve()
        if global_events:
            return {
                "status": "ok",
                "data": build_global_runtime_events_payload(
                    resolved_root,
                    scan_roots=scan_roots,
                    limit=int(limit),
                ),
            }
        return {
            "status": "ok",
            "data": build_runtime_events_payload(resolved_root, limit=int(limit)),
        }

    @server.tool(
        name="run_agent_task_experimental",
        description=(
            "Experimental host-facing task entry. "
            "Runs the agent-first orchestration facade without replacing the existing MCP mainline."
        ),
        structured_output=True,
    )
    def run_agent_task_experimental(
        task_description: str,
        working_directory: str | None = None,
        known_inputs: dict[str, Any] | None = None,
        expected_outputs: list[str] | None = None,
        risk_level: str = "medium",
        task_kind: str = "workflow",
        allow_silent_reuse: bool = True,
        allow_learning: bool = True,
    ) -> dict[str, Any]:
        request = AgentTaskRequest(
            task_description=task_description,
            working_directory=working_directory,
            known_inputs=known_inputs or {},
            expected_outputs=expected_outputs or [],
            risk_level=risk_level,
            task_kind=task_kind,
            allow_silent_reuse=allow_silent_reuse,
            allow_learning=allow_learning,
        )
        return _wrap_agent_host_tool(run_agent_task, root=root, request=request)

    @server.tool(
        name="finalize_agent_task_experimental",
        description=(
            "Experimental host-facing task finalizer. "
            "Feeds an actual execution result back into the agent-first learning path."
        ),
        structured_output=True,
    )
    def finalize_agent_task_experimental(
        plan: dict[str, Any],
        execution_payload: dict[str, Any],
    ) -> dict[str, Any]:
        return _wrap_agent_host_tool(
            finalize_agent_task,
            root=root,
            plan=_agent_result_from_payload(plan),
            execution_payload=execution_payload,
        )

    @server.tool(
        name="run_codex_task_experimental",
        description=(
            "Experimental Codex-facing task entry. "
            "Classifies the task first, then only enters the runtime lane for default-in workflow tasks."
        ),
        structured_output=True,
    )
    def run_codex_task_experimental(
        task_description: str,
        working_directory: str | None = None,
        known_inputs: dict[str, Any] | None = None,
        expected_outputs: list[str] | None = None,
        risk_level: str = "medium",
        task_kind: str = "workflow",
        allow_silent_reuse: bool = True,
        allow_learning: bool = True,
    ) -> dict[str, Any]:
        request = AgentTaskRequest(
            task_description=task_description,
            working_directory=working_directory,
            known_inputs=known_inputs or {},
            expected_outputs=expected_outputs or [],
            risk_level=risk_level,
            task_kind=task_kind,
            allow_silent_reuse=allow_silent_reuse,
            allow_learning=allow_learning,
        )
        return _wrap_agent_host_tool(run_codex_task, root=root, request=request)

    @server.tool(
        name="finalize_codex_task_experimental",
        description=(
            "Experimental Codex-facing task finalizer. "
            "Only default-in tasks continue into runtime-side post-task learning."
        ),
        structured_output=True,
    )
    def finalize_codex_task_experimental(
        plan: dict[str, Any],
        execution_payload: dict[str, Any],
    ) -> dict[str, Any]:
        return _wrap_agent_host_tool(
            finalize_codex_task,
            root=root,
            plan=_agent_result_from_payload(plan),
            execution_payload=execution_payload,
        )

    return server
