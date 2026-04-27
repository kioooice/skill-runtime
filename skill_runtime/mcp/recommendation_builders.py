from __future__ import annotations

from typing import Any

from skill_runtime.mcp.operation_builders import (
    archive_duplicate_candidates_operation,
    audit_skill_operation,
    capture_trajectory_operation,
    distill_and_promote_operation,
    distill_coverage_report_operation,
    distill_trajectory_operation,
    execute_skill_operation,
    governance_report_operation,
    operation_list,
    promote_skill_operation,
    rollback_operations_operation,
    refresh_governance_report_operation,
)
from skill_runtime.mcp.source_refs import (
    source_ref_archive_duplicate_candidates_apply_follow_up,
    source_ref_archive_duplicate_candidates_follow_up,
    source_ref_audit,
    source_ref_distill_coverage_report_refresh,
    source_ref_distill,
    source_ref_log_trajectory,
    source_ref_observed_task,
    source_ref_observed_task_rollback,
    source_ref_promote,
    source_ref_search_no_match,
    source_ref_search_no_match_inline_capture,
    source_ref_search_no_match_inline_distill,
    source_ref_search_no_match_distill,
    source_ref_search_recommended_skill,
    source_ref_skill,
    source_ref_trajectory,
)

__all__ = [
    "recommendation_fields",
    "no_recommendation",
    "recommendation_from_operation",
    "recommendation_from_payload",
    "with_recommendation",
    "execute_skill_recommendation",
    "capture_trajectory_recommendation",
    "distill_trajectory_recommendation",
    "audit_skill_recommendation",
    "promote_skill_recommendation",
    "governance_report_recommendation",
    "distill_coverage_report_recommendation",
    "archive_duplicate_candidates_recommendation",
    "distill_and_promote_recommendation",
    "search_no_match_recommendation",
    "search_result_execute_skill_operation",
    "search_recommended_skill_recommendation",
    "search_result_payload",
    "search_response_payload",
    "executed_skill_promotion_recommendation",
    "distilled_skill_audit_recommendation",
    "promoted_skill_execution_recommendation",
    "registered_trajectory_recommendation",
    "captured_trajectory_recommendation",
    "archive_duplicate_candidates_follow_up_recommendation",
    "rollback_operations_recommendation",
]


def recommendation_fields(
    next_action: str | None,
    host_operation: dict[str, Any] | None = None,
    *,
    reason: str | None = None,
    additional_operations: list[dict[str, Any] | None] | None = None,
) -> dict[str, Any]:
    if next_action is None or not isinstance(host_operation, dict):
        return {
            "recommended_next_action": None,
            "recommended_reason": reason,
            "recommended_host_operation": None,
            "available_host_operations": [],
        }
    return {
        "recommended_next_action": next_action,
        "recommended_reason": reason,
        "recommended_host_operation": host_operation,
        "available_host_operations": operation_list(host_operation, additional_operations),
    }


def no_recommendation(reason: str | None = None) -> dict[str, Any]:
    return recommendation_fields(None, None, reason=reason)


def recommendation_from_operation(
    next_action: str | None,
    operation: dict[str, Any] | None,
    *,
    reason: str | None = None,
    additional_operations: list[dict[str, Any] | None] | None = None,
) -> dict[str, Any]:
    return recommendation_fields(
        next_action,
        operation,
        reason=reason,
        additional_operations=additional_operations,
    )


def recommendation_from_payload(
    payload: dict[str, Any] | None,
    *,
    reason: str | None = None,
    additional_operations: list[dict[str, Any] | None] | None = None,
) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return no_recommendation(reason)

    resolved_reason = payload.get("recommended_reason") if reason is None else reason
    resolved_additional_operations = additional_operations
    if resolved_additional_operations is None:
        available_operations = payload.get("available_host_operations")
        if isinstance(available_operations, list):
            resolved_additional_operations = available_operations[1:]

    return recommendation_fields(
        payload.get("recommended_next_action"),
        payload.get("recommended_host_operation"),
        reason=resolved_reason,
        additional_operations=resolved_additional_operations,
    )


def with_recommendation(
    payload: dict[str, Any],
    recommendation: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        **payload,
        **(recommendation or {}),
    }


def execute_skill_recommendation(
    skill_name: str,
    input_schema: dict[str, Any] | None,
    *,
    reason: str | None = None,
    additional_operations: list[dict[str, Any] | None] | None = None,
    **operation_kwargs: Any,
) -> dict[str, Any]:
    return recommendation_from_operation(
        "execute_skill",
        execute_skill_operation(skill_name, input_schema, **operation_kwargs),
        reason=reason,
        additional_operations=additional_operations,
    )


def capture_trajectory_recommendation(
    *,
    reason: str | None = None,
    additional_operations: list[dict[str, Any] | None] | None = None,
    **operation_kwargs: Any,
) -> dict[str, Any]:
    return recommendation_from_operation(
        "capture_trajectory",
        capture_trajectory_operation(**operation_kwargs),
        reason=reason,
        additional_operations=additional_operations,
    )


def distill_trajectory_recommendation(
    trajectory_path: str,
    *,
    reason: str | None = None,
    additional_operations: list[dict[str, Any] | None] | None = None,
    **operation_kwargs: Any,
) -> dict[str, Any]:
    return recommendation_from_operation(
        "distill_trajectory",
        distill_trajectory_operation(trajectory_path, **operation_kwargs),
        reason=reason,
        additional_operations=additional_operations,
    )


def audit_skill_recommendation(
    file_path: str,
    *,
    reason: str | None = None,
    additional_operations: list[dict[str, Any] | None] | None = None,
    **operation_kwargs: Any,
) -> dict[str, Any]:
    return recommendation_from_operation(
        "audit_skill",
        audit_skill_operation(file_path, **operation_kwargs),
        reason=reason,
        additional_operations=additional_operations,
    )


def promote_skill_recommendation(
    file_path: str,
    *,
    reason: str | None = None,
    additional_operations: list[dict[str, Any] | None] | None = None,
    **operation_kwargs: Any,
) -> dict[str, Any]:
    return recommendation_from_operation(
        "promote_skill",
        promote_skill_operation(file_path, **operation_kwargs),
        reason=reason,
        additional_operations=additional_operations,
    )


def rollback_operations_recommendation(
    operation_log: list[dict[str, Any]],
    *,
    operation_ids: list[str] | None = None,
    reason: str | None = None,
    additional_operations: list[dict[str, Any] | None] | None = None,
    **operation_kwargs: Any,
) -> dict[str, Any]:
    return recommendation_from_operation(
        "rollback_operations",
        rollback_operations_operation(
            operation_log,
            operation_ids=operation_ids,
            **operation_kwargs,
        ),
        reason=reason,
        additional_operations=additional_operations,
    )


def governance_report_recommendation(
    *,
    reason: str | None = None,
    additional_operations: list[dict[str, Any] | None] | None = None,
    **operation_kwargs: Any,
) -> dict[str, Any]:
    return recommendation_from_operation(
        "governance_report",
        governance_report_operation(**operation_kwargs),
        reason=reason,
        additional_operations=additional_operations,
    )


def distill_coverage_report_recommendation(
    *,
    reason: str | None = None,
    additional_operations: list[dict[str, Any] | None] | None = None,
    **operation_kwargs: Any,
) -> dict[str, Any]:
    return recommendation_from_operation(
        "distill_coverage_report",
        distill_coverage_report_operation(**operation_kwargs),
        reason=reason,
        additional_operations=additional_operations,
    )


def archive_duplicate_candidates_recommendation(
    skill_names: list[str],
    *,
    reason: str | None = None,
    additional_operations: list[dict[str, Any] | None] | None = None,
    **operation_kwargs: Any,
) -> dict[str, Any]:
    return recommendation_from_operation(
        "archive_duplicate_candidates",
        archive_duplicate_candidates_operation(skill_names, **operation_kwargs),
        reason=reason,
        additional_operations=additional_operations,
    )


def distill_and_promote_recommendation(
    *,
    reason: str | None = None,
    additional_operations: list[dict[str, Any] | None] | None = None,
    **operation_kwargs: Any,
) -> dict[str, Any]:
    return recommendation_from_operation(
        "distill_and_promote_candidate",
        distill_and_promote_operation(**operation_kwargs),
        reason=reason,
        additional_operations=additional_operations,
    )


def search_no_match_recommendation(
    *,
    reason: str | None = None,
) -> dict[str, Any]:
    inline_capture_operation = capture_trajectory_operation(
        display_label="Capture inline workflow",
        effect_summary=(
            "Capture the new workflow from an inline observed task payload before distillation."
        ),
        argument_schema={
            "observed_task": {"type": "object", "required": True, "prefilled": False},
            "task_id": {"type": "string", "required": False, "prefilled": False},
            "session_id": {"type": "string", "required": False, "prefilled": False},
        },
        risk_level="low",
        requires_confirmation=False,
        source_ref=source_ref_search_no_match_inline_capture(),
        operation_group="search_no_match_capture",
        delivery_mode="inline",
        variant_role="alternate",
    )
    secondary_operation = distill_and_promote_operation(
        display_label="Promote new workflow",
        risk_level="low",
        requires_confirmation=False,
        source_ref=source_ref_search_no_match_distill(),
        operation_group="search_no_match_promote",
        delivery_mode="path",
        variant_role="preferred",
    )
    inline_distill_operation = distill_and_promote_operation(
        display_label="Promote inline workflow",
        effect_summary=(
            "Capture, distill, audit, and promote a new workflow directly from an inline observed task payload."
        ),
        argument_schema={
            "observed_task": {"type": "object", "required": True, "prefilled": False},
            "skill_name": {"type": "string", "required": False, "prefilled": False},
            "register_trajectory": {"type": "boolean", "required": False, "prefilled": False},
        },
        risk_level="low",
        requires_confirmation=False,
        source_ref=source_ref_search_no_match_inline_distill(),
        operation_group="search_no_match_promote",
        delivery_mode="inline",
        variant_role="alternate",
    )
    return capture_trajectory_recommendation(
        display_label="Capture new workflow",
        effect_summary=(
            "Capture the new workflow as an observed task record before distillation or promotion."
        ),
        risk_level="low",
        requires_confirmation=False,
        source_ref=source_ref_search_no_match(),
        operation_group="search_no_match_capture",
        delivery_mode="path",
        variant_role="preferred",
        reason=reason,
        additional_operations=[inline_capture_operation, secondary_operation, inline_distill_operation],
    )


def search_result_execute_skill_operation(
    skill_name: str,
    input_schema: dict[str, Any] | None,
    *,
    display_label: str | None = None,
    effect_summary: str | None = None,
) -> dict[str, Any]:
    return execute_skill_operation(
        skill_name,
        input_schema,
        display_label=display_label,
        effect_summary=effect_summary,
        source_ref=source_ref_skill(skill_name),
    )


def search_recommended_skill_recommendation(
    skill_name: str,
    input_schema: dict[str, Any] | None,
    *,
    additional_operations: list[dict[str, Any] | None] | None = None,
) -> dict[str, Any]:
    return execute_skill_recommendation(
        skill_name,
        input_schema,
        display_label="Run recommended skill",
        risk_level="low",
        requires_confirmation=False,
        source_ref=source_ref_search_recommended_skill(skill_name),
        additional_operations=additional_operations,
    )


def search_result_payload(
    skill_name: str,
    summary: str,
    score: float,
    why_matched: str,
    input_schema: dict[str, Any] | None,
    *,
    rule_name: str | None = None,
    rule_priority: int | None = None,
    rule_reason: str | None = None,
    library_tier: str | None = None,
    score_breakdown: dict[str, float] | None = None,
) -> dict[str, Any]:
    return {
        "skill_name": skill_name,
        "summary": summary,
        "score": round(score, 4),
        "why_matched": why_matched,
        "recommended_next_action": "execute_skill",
        "host_operation": search_result_execute_skill_operation(skill_name, input_schema),
        "rule_name": rule_name,
        "rule_priority": rule_priority,
        "rule_reason": rule_reason,
        "library_tier": library_tier,
        "score_breakdown": score_breakdown or {},
    }


def search_response_payload(
    query: str,
    results: list[dict[str, Any]],
    recommended_skill_name: str | None,
    recommendation: dict[str, Any] | None,
) -> dict[str, Any]:
    return with_recommendation(
        {
            "query": query,
            "results": results,
            "recommended_skill_name": recommended_skill_name,
        },
        recommendation,
    )


def executed_skill_promotion_recommendation(
    observed_task_path: str,
    *,
    observed_task: dict[str, Any] | None = None,
    operation_log: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    additional_operations: list[dict[str, Any]] = []
    if observed_task is not None:
        additional_operations.append(
            distill_and_promote_operation(
                observed_task=observed_task,
                display_label="Promote this execution inline",
                effect_summary=(
                    "Promote this successful execution by sending the inline observed task "
                    "payload into distill_and_promote_candidate."
                ),
                argument_schema={
                    "observed_task": {"type": "object", "required": True, "prefilled": True},
                },
                risk_level="medium",
                requires_confirmation=False,
                source_ref=source_ref_observed_task(observed_task_path),
                operation_group="execute_promote",
                delivery_mode="inline",
                variant_role="alternate",
            )
        )
    rollbackable_operations = [
        item
        for item in (operation_log or [])
        if isinstance(item, dict)
        and item.get("status") == "success"
        and isinstance(item.get("rollback_hint"), dict)
        and item["rollback_hint"].get("strategy") in {"delete_created_file", "rename_back"}
    ]
    if rollbackable_operations:
        additional_operations.append(
            rollback_operations_operation(
                rollbackable_operations,
                operation_ids=[item["operation_id"] for item in rollbackable_operations],
                dry_run=False,
                display_label="Rollback this execution",
                effect_summary=(
                    "Rollback the safe file changes produced by this execution using its operation log."
                ),
                argument_schema={
                    "operation_log": {"type": "array", "required": True, "prefilled": True},
                    "operation_ids": {"type": "array", "required": True, "prefilled": True},
                    "dry_run": {"type": "boolean", "required": False, "prefilled": True},
                },
                risk_level="medium",
                requires_confirmation=True,
                confirmation_message="Rollback the safe file changes from this execution?",
                source_ref=source_ref_observed_task_rollback(observed_task_path),
            )
        )
    return distill_and_promote_recommendation(
        observed_task_path=observed_task_path,
        display_label="Promote this execution",
        effect_summary=(
            "Promote this successful execution by sending its observed task record into "
            "distill_and_promote_candidate."
        ),
        argument_schema={
            "observed_task_path": {"type": "string", "required": True, "prefilled": True},
        },
        risk_level="medium",
        requires_confirmation=False,
        source_ref=source_ref_observed_task(observed_task_path),
        operation_group="execute_promote",
        delivery_mode="path",
        variant_role="preferred",
        reason=(
            "Execution succeeded and emitted an observed task record that can be sent "
            "directly into distill_and_promote_candidate."
        ),
        additional_operations=additional_operations,
    )


def distilled_skill_audit_recommendation(
    staging_file: str,
    trajectory_path: str,
    skill_name: str,
) -> dict[str, Any]:
    return audit_skill_recommendation(
        staging_file,
        trajectory_path=trajectory_path,
        display_label="Audit distilled skill",
        effect_summary="Audit the newly distilled staging skill before any promotion step.",
        risk_level="low",
        requires_confirmation=False,
        source_ref=source_ref_distill(skill_name),
        reason="Distillation produced a staging skill. Audit it next before considering promotion.",
    )


def promoted_skill_execution_recommendation(
    skill_name: str,
    input_schema: dict[str, Any] | None,
) -> dict[str, Any]:
    return execute_skill_recommendation(
        skill_name,
        input_schema,
        display_label="Run promoted skill",
        effect_summary="Execute the newly promoted active skill.",
        risk_level="low",
        requires_confirmation=False,
        source_ref=source_ref_promote(skill_name),
        reason="The skill is now active and can be executed directly from the active library.",
    )


def registered_trajectory_recommendation(trajectory_path: str, *, task_id: str) -> dict[str, Any]:
    return distill_trajectory_recommendation(
        trajectory_path,
        display_label="Distill registered trajectory",
        effect_summary="Distill the registered trajectory into a staging skill draft.",
        risk_level="low",
        requires_confirmation=False,
        source_ref=source_ref_log_trajectory(task_id),
        reason="The trajectory has been registered and is ready for distillation.",
    )


def captured_trajectory_recommendation(trajectory_path: str, *, task_id: str) -> dict[str, Any]:
    return distill_trajectory_recommendation(
        trajectory_path,
        display_label="Distill captured trajectory",
        effect_summary="Distill the captured trajectory into a staging skill draft.",
        risk_level="low",
        requires_confirmation=False,
        source_ref=source_ref_trajectory(task_id),
        reason="The observed task has been captured into a trajectory and is ready for distillation.",
    )


def archive_duplicate_candidates_follow_up_recommendation(
    skill_names: list[str],
    *,
    dry_run: bool,
) -> dict[str, Any]:
    refresh_operation = refresh_governance_report_operation()
    if dry_run:
        return archive_duplicate_candidates_recommendation(
            skill_names,
            dry_run=False,
            display_label="Apply archive",
            effect_summary="Apply the previewed duplicate archive action.",
            argument_schema={
                "skill_names": {"type": "array", "required": True, "prefilled": True},
                "dry_run": {"type": "boolean", "required": True, "prefilled": True},
            },
            risk_level="high",
            requires_confirmation=True,
            confirmation_message=(
                "Archive the previewed duplicate skills while keeping the canonical skill active?"
            ),
            source_ref=source_ref_archive_duplicate_candidates_apply_follow_up(),
            reason=(
                "The dry run identified archive candidates. Apply the archive action to update the library."
            ),
            additional_operations=[refresh_operation],
        )

    return governance_report_recommendation(
        display_label="Refresh governance report",
        effect_summary=(
            "Refresh the governance report to review the latest duplicate clusters and "
            "recommended maintenance actions."
        ),
        risk_level="low",
        requires_confirmation=False,
        source_ref=source_ref_archive_duplicate_candidates_follow_up(),
        reason=(
            "The archive operation changes governance state. Refresh governance_report to "
            "inspect the updated duplicate set and next maintenance actions."
        ),
    )
