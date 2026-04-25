import hashlib
import json
from typing import Any

TOOL_PRESETS = {
    "execute_skill": {
        "display_label": "Run skill",
        "effect_summary": "Execute the selected skill with the provided arguments.",
        "argument_schema": {
            "skill_name": {"type": "string", "required": True, "prefilled": True},
            "args": {"type": "object", "required": True, "prefilled": False},
        },
        "risk_level": "low",
        "requires_confirmation": False,
    },
    "distill_and_promote_candidate": {
        "display_label": "Promote workflow",
        "effect_summary": "Capture a successful workflow into the governed skill library.",
        "argument_schema": {
            "trajectory_path": {"type": "string", "required": False, "prefilled": False},
            "observed_task_path": {"type": "string", "required": False, "prefilled": False},
            "skill_name": {"type": "string", "required": False, "prefilled": False},
            "register_trajectory": {"type": "boolean", "required": False, "prefilled": False},
        },
        "risk_level": "low",
        "requires_confirmation": False,
    },
    "archive_duplicate_candidates": {
        "display_label": "Archive duplicates",
        "effect_summary": "Archive lower-priority duplicate skills while leaving canonical skills active.",
        "argument_schema": {
            "skill_names": {"type": "array", "required": True, "prefilled": True},
            "dry_run": {"type": "boolean", "required": True, "prefilled": True},
        },
        "risk_level": "high",
        "requires_confirmation": True,
        "confirmation_message": "Archive the suggested duplicate skills while keeping the canonical skill active?",
        "preview_display_label": "Preview archive",
        "preview_effect_summary": "Preview which duplicate skills would be archived without changing the library.",
        "preview_risk_level": "low",
        "preview_requires_confirmation": False,
    },
    "governance_report": {
        "display_label": "Refresh governance report",
        "effect_summary": "Recompute governance recommendations and duplicate clusters.",
        "risk_level": "low",
        "requires_confirmation": False,
    },
    "capture_trajectory": {
        "display_label": "Capture trajectory",
        "effect_summary": "Capture an observed task record into a reusable trajectory file.",
        "argument_schema": {
            "file_path": {"type": "string", "required": True, "prefilled": False},
            "task_id": {"type": "string", "required": False, "prefilled": False},
            "session_id": {"type": "string", "required": False, "prefilled": False},
        },
        "risk_level": "low",
        "requires_confirmation": False,
    },
    "distill_trajectory": {
        "display_label": "Distill trajectory",
        "effect_summary": "Generate a staging skill and metadata draft from a saved trajectory.",
        "argument_schema": {
            "trajectory_path": {"type": "string", "required": True, "prefilled": True},
            "skill_name": {"type": "string", "required": False, "prefilled": False},
        },
        "risk_level": "low",
        "requires_confirmation": False,
    },
    "audit_skill": {
        "display_label": "Audit skill",
        "effect_summary": "Audit a staging skill for safety, generalization, and retrievability.",
        "argument_schema": {
            "file_path": {"type": "string", "required": True, "prefilled": True},
            "trajectory_path": {"type": "string", "required": False, "prefilled": True},
        },
        "risk_level": "low",
        "requires_confirmation": False,
    },
    "promote_skill": {
        "display_label": "Promote skill",
        "effect_summary": "Promote a passing staging skill into the active governed library.",
        "argument_schema": {
            "file_path": {"type": "string", "required": True, "prefilled": True},
        },
        "risk_level": "medium",
        "requires_confirmation": False,
    },
}

TYPE_ALIASES = {
    "str": "string",
    "string": "string",
    "int": "integer",
    "integer": "integer",
    "float": "number",
    "number": "number",
    "bool": "boolean",
    "boolean": "boolean",
    "dict": "object",
    "object": "object",
    "list": "array",
    "array": "array",
}


def source_ref_skill(skill_name: str) -> str:
    return f"skill:{skill_name}"


def source_ref_search_recommended_skill(skill_name: str) -> str:
    return f"search:recommended_skill:{skill_name}"


def source_ref_search_no_match() -> str:
    return "search:no_strong_match"


def source_ref_search_no_match_distill() -> str:
    return "search:no_strong_match:distill"


def source_ref_observed_task(observed_task_path: str) -> str:
    return f"observed_task:{observed_task_path}"


def source_ref_distill(skill_name: str) -> str:
    return f"distill:{skill_name}"


def source_ref_audit(skill_name: str) -> str:
    return f"audit:{skill_name}"


def source_ref_promote(skill_name: str) -> str:
    return f"promote:{skill_name}"


def source_ref_trajectory(task_id: str) -> str:
    return f"trajectory:{task_id}"


def source_ref_log_trajectory(task_id: str) -> str:
    return f"log_trajectory:{task_id}"


def source_ref_archive_duplicate_candidates(canonical_skill: str) -> str:
    return f"governance:archive_duplicate_candidates:{canonical_skill}"


def source_ref_archive_duplicate_candidates_preview(canonical_skill: str) -> str:
    return f"{source_ref_archive_duplicate_candidates(canonical_skill)}:preview"


def source_ref_archive_duplicate_candidates_follow_up() -> str:
    return "archive_duplicate_candidates:follow_up"


def source_ref_archive_duplicate_candidates_apply_follow_up() -> str:
    return "archive_duplicate_candidates:apply_follow_up"


def source_ref_governance_report_refresh() -> str:
    return "governance:report_refresh"


def tool_call(
    tool_name: str,
    arguments: dict[str, Any],
    display_label: str | None = None,
    effect_summary: str | None = None,
    argument_schema: dict[str, Any] | None = None,
    risk_level: str | None = None,
    requires_confirmation: bool | None = None,
    confirmation_message: str | None = None,
    operation_role: str = "default",
    source_ref: str | None = None,
) -> dict[str, Any]:
    preset = TOOL_PRESETS.get(tool_name, {})
    resolved_display_label = display_label or preset.get("display_label") or _default_label(tool_name)
    resolved_requires_confirmation = (
        requires_confirmation
        if requires_confirmation is not None
        else preset.get("requires_confirmation", False)
    )
    return {
        "type": "mcp_tool_call",
        "operation_id": _operation_id(tool_name, arguments, resolved_display_label),
        "tool_name": tool_name,
        "arguments": arguments,
        "source_ref": source_ref,
        "display_label": resolved_display_label,
        "effect_summary": effect_summary or preset.get("effect_summary") or f"Call {tool_name}.",
        "argument_schema": argument_schema or preset.get("argument_schema", {}),
        "risk_level": risk_level if risk_level is not None else preset.get("risk_level", "low"),
        "requires_confirmation": resolved_requires_confirmation,
        "confirmation_message": (
            confirmation_message
            if resolved_requires_confirmation
            else None
        ) or (
            preset.get("confirmation_message")
            if resolved_requires_confirmation
            else None
        ),
        "operation_role": operation_role,
    }


def execute_skill_argument_schema(input_schema: dict[str, Any] | None) -> dict[str, Any]:
    properties: dict[str, Any] = {}
    for name, schema in (input_schema or {}).items():
        properties[name] = {
            "type": _normalize_schema_type(schema),
            "required": True,
            "prefilled": False,
        }

    return {
        "skill_name": {"type": "string", "required": True, "prefilled": True},
        "args": {
            "type": "object",
            "required": True,
            "prefilled": False,
            "properties": properties,
        },
    }


def execute_skill_operation(
    skill_name: str,
    input_schema: dict[str, Any] | None,
    *,
    display_label: str | None = None,
    effect_summary: str | None = None,
    risk_level: str | None = None,
    requires_confirmation: bool | None = None,
    confirmation_message: str | None = None,
    operation_role: str = "default",
    source_ref: str | None = None,
) -> dict[str, Any]:
    return tool_call(
        "execute_skill",
        {"skill_name": skill_name, "args": {}},
        display_label=display_label,
        effect_summary=effect_summary,
        argument_schema=execute_skill_argument_schema(input_schema),
        risk_level=risk_level,
        requires_confirmation=requires_confirmation,
        confirmation_message=confirmation_message,
        operation_role=operation_role,
        source_ref=source_ref,
    )


def capture_trajectory_operation(
    *,
    file_path: str | None = None,
    task_id: str | None = None,
    session_id: str | None = None,
    display_label: str | None = None,
    effect_summary: str | None = None,
    risk_level: str | None = None,
    requires_confirmation: bool | None = None,
    confirmation_message: str | None = None,
    operation_role: str = "default",
    source_ref: str | None = None,
) -> dict[str, Any]:
    arguments = {}
    if file_path is not None:
        arguments["file_path"] = file_path
    if task_id is not None:
        arguments["task_id"] = task_id
    if session_id is not None:
        arguments["session_id"] = session_id
    return tool_call(
        "capture_trajectory",
        arguments,
        display_label=display_label,
        effect_summary=effect_summary,
        risk_level=risk_level,
        requires_confirmation=requires_confirmation,
        confirmation_message=confirmation_message,
        operation_role=operation_role,
        source_ref=source_ref,
    )


def distill_trajectory_operation(
    trajectory_path: str,
    *,
    skill_name: str | None = None,
    display_label: str | None = None,
    effect_summary: str | None = None,
    risk_level: str | None = None,
    requires_confirmation: bool | None = None,
    confirmation_message: str | None = None,
    operation_role: str = "default",
    source_ref: str | None = None,
) -> dict[str, Any]:
    arguments = {"trajectory_path": trajectory_path}
    if skill_name is not None:
        arguments["skill_name"] = skill_name
    return tool_call(
        "distill_trajectory",
        arguments,
        display_label=display_label,
        effect_summary=effect_summary,
        risk_level=risk_level,
        requires_confirmation=requires_confirmation,
        confirmation_message=confirmation_message,
        operation_role=operation_role,
        source_ref=source_ref,
    )


def audit_skill_operation(
    file_path: str,
    *,
    trajectory_path: str | None = None,
    display_label: str | None = None,
    effect_summary: str | None = None,
    risk_level: str | None = None,
    requires_confirmation: bool | None = None,
    confirmation_message: str | None = None,
    operation_role: str = "default",
    source_ref: str | None = None,
) -> dict[str, Any]:
    arguments = {"file_path": file_path}
    if trajectory_path is not None:
        arguments["trajectory_path"] = trajectory_path
    return tool_call(
        "audit_skill",
        arguments,
        display_label=display_label,
        effect_summary=effect_summary,
        risk_level=risk_level,
        requires_confirmation=requires_confirmation,
        confirmation_message=confirmation_message,
        operation_role=operation_role,
        source_ref=source_ref,
    )


def promote_skill_operation(
    file_path: str,
    *,
    display_label: str | None = None,
    effect_summary: str | None = None,
    risk_level: str | None = None,
    requires_confirmation: bool | None = None,
    confirmation_message: str | None = None,
    operation_role: str = "default",
    source_ref: str | None = None,
) -> dict[str, Any]:
    return tool_call(
        "promote_skill",
        {"file_path": file_path},
        display_label=display_label,
        effect_summary=effect_summary,
        risk_level=risk_level,
        requires_confirmation=requires_confirmation,
        confirmation_message=confirmation_message,
        operation_role=operation_role,
        source_ref=source_ref,
    )


def governance_report_operation(
    *,
    display_label: str | None = None,
    effect_summary: str | None = None,
    risk_level: str | None = None,
    requires_confirmation: bool | None = None,
    confirmation_message: str | None = None,
    operation_role: str = "default",
    source_ref: str | None = None,
) -> dict[str, Any]:
    return tool_call(
        "governance_report",
        {},
        display_label=display_label,
        effect_summary=effect_summary,
        risk_level=risk_level,
        requires_confirmation=requires_confirmation,
        confirmation_message=confirmation_message,
        operation_role=operation_role,
        source_ref=source_ref,
    )


def refresh_governance_report_operation(*, source_ref: str | None = None) -> dict[str, Any]:
    return governance_report_operation(
        display_label="Refresh governance report",
        effect_summary=(
            "Refresh the governance report to review the latest duplicate clusters and "
            "recommended maintenance actions."
        ),
        risk_level="low",
        requires_confirmation=False,
        source_ref=source_ref or source_ref_archive_duplicate_candidates_follow_up(),
    )


def archive_duplicate_candidates_operation(
    skill_names: list[str],
    *,
    dry_run: bool = False,
    include_preview: bool = False,
    display_label: str | None = None,
    effect_summary: str | None = None,
    argument_schema: dict[str, Any] | None = None,
    risk_level: str | None = None,
    requires_confirmation: bool | None = None,
    confirmation_message: str | None = None,
    preview_display_label: str | None = None,
    preview_effect_summary: str | None = None,
    preview_risk_level: str | None = None,
    preview_requires_confirmation: bool | None = None,
    preview_confirmation_message: str | None = None,
    operation_role: str = "default",
    source_ref: str | None = None,
    preview_source_ref: str | None = None,
) -> dict[str, Any]:
    arguments = {"skill_names": skill_names, "dry_run": dry_run}
    if include_preview:
        return tool_call_with_preview(
            "archive_duplicate_candidates",
            arguments,
            {"skill_names": skill_names, "dry_run": True},
            display_label=display_label,
            effect_summary=effect_summary,
            argument_schema=argument_schema,
            risk_level=risk_level,
            requires_confirmation=requires_confirmation,
            confirmation_message=confirmation_message,
            preview_display_label=preview_display_label,
            preview_effect_summary=preview_effect_summary,
            preview_risk_level=preview_risk_level,
            preview_requires_confirmation=preview_requires_confirmation,
            preview_confirmation_message=preview_confirmation_message,
            operation_role=operation_role,
            source_ref=source_ref,
            preview_source_ref=preview_source_ref,
        )
    return tool_call(
        "archive_duplicate_candidates",
        arguments,
        display_label=display_label,
        effect_summary=effect_summary,
        argument_schema=argument_schema,
        risk_level=risk_level,
        requires_confirmation=requires_confirmation,
        confirmation_message=confirmation_message,
        operation_role=operation_role,
        source_ref=source_ref,
    )


def distill_and_promote_operation(
    *,
    trajectory_path: str | None = None,
    observed_task_path: str | None = None,
    skill_name: str | None = None,
    register_trajectory: bool | None = None,
    display_label: str | None = None,
    effect_summary: str | None = None,
    argument_schema: dict[str, Any] | None = None,
    risk_level: str | None = None,
    requires_confirmation: bool | None = None,
    confirmation_message: str | None = None,
    operation_role: str = "default",
    source_ref: str | None = None,
) -> dict[str, Any]:
    arguments = {}
    if trajectory_path is not None:
        arguments["trajectory_path"] = trajectory_path
    if observed_task_path is not None:
        arguments["observed_task_path"] = observed_task_path
    if skill_name is not None:
        arguments["skill_name"] = skill_name
    if register_trajectory is not None:
        arguments["register_trajectory"] = register_trajectory
    return tool_call(
        "distill_and_promote_candidate",
        arguments,
        display_label=display_label,
        effect_summary=effect_summary,
        argument_schema=argument_schema,
        risk_level=risk_level,
        requires_confirmation=requires_confirmation,
        confirmation_message=confirmation_message,
        operation_role=operation_role,
        source_ref=source_ref,
    )


def tool_call_with_preview(
    tool_name: str,
    arguments: dict[str, Any],
    preview_arguments: dict[str, Any],
    display_label: str | None = None,
    effect_summary: str | None = None,
    argument_schema: dict[str, Any] | None = None,
    risk_level: str | None = None,
    requires_confirmation: bool | None = None,
    confirmation_message: str | None = None,
    preview_display_label: str | None = None,
    preview_effect_summary: str | None = None,
    preview_risk_level: str | None = None,
    preview_requires_confirmation: bool | None = None,
    preview_confirmation_message: str | None = None,
    operation_role: str = "default",
    source_ref: str | None = None,
    preview_source_ref: str | None = None,
) -> dict[str, Any]:
    preset = TOOL_PRESETS.get(tool_name, {})
    payload = tool_call(
        tool_name,
        arguments,
        display_label=display_label,
        effect_summary=effect_summary,
        argument_schema=argument_schema,
        risk_level=risk_level,
        requires_confirmation=requires_confirmation,
        confirmation_message=confirmation_message,
        operation_role=operation_role,
        source_ref=source_ref,
    )
    payload["preview"] = tool_call(
        tool_name,
        preview_arguments,
        display_label=preview_display_label or preset.get("preview_display_label") or f"Preview {payload['display_label'].lower()}",
        effect_summary=preview_effect_summary or preset.get("preview_effect_summary"),
        risk_level=preview_risk_level if preview_risk_level is not None else preset.get("preview_risk_level", "low"),
        requires_confirmation=(
            preview_requires_confirmation
            if preview_requires_confirmation is not None
            else preset.get("preview_requires_confirmation", False)
        ),
        confirmation_message=preview_confirmation_message,
        operation_role="preview",
        source_ref=preview_source_ref,
    )
    return payload


def collect_operations(candidates: list[dict[str, Any] | None]) -> list[dict[str, Any]]:
    operations: list[dict[str, Any]] = []
    seen: set[str] = set()

    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        identity = repr(
            (
                candidate.get("tool_name"),
                candidate.get("display_label"),
                candidate.get("arguments"),
            )
        )
        if identity in seen:
            continue
        seen.add(identity)
        operations.append(candidate)

    operations.sort(key=_operation_sort_key)
    return operations


def operation_list(
    primary_operation: dict[str, Any] | None = None,
    additional_operations: list[dict[str, Any] | None] | None = None,
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any] | None] = []
    if isinstance(primary_operation, dict):
        candidates.append(
            {
                **primary_operation,
                "operation_role": "primary",
            }
        )
    if additional_operations:
        candidates.extend(additional_operations)
    return collect_operations(candidates)


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


def action_host_operations(actions: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any] | None] = []
    for action in actions or []:
        if not isinstance(action, dict):
            continue
        host_operation = action.get("host_operation")
        if not isinstance(host_operation, dict):
            continue
        candidates.append(host_operation)
        preview = host_operation.get("preview")
        if isinstance(preview, dict):
            candidates.append(preview)
    return collect_operations(candidates)


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
    secondary_operation = distill_and_promote_operation(
        display_label="Promote new workflow",
        risk_level="low",
        requires_confirmation=False,
        source_ref=source_ref_search_no_match_distill(),
    )
    return capture_trajectory_recommendation(
        display_label="Capture new workflow",
        effect_summary=(
            "Capture the new workflow as an observed task record before distillation or promotion."
        ),
        risk_level="low",
        requires_confirmation=False,
        source_ref=source_ref_search_no_match(),
        reason=reason,
        additional_operations=[secondary_operation],
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


def governance_action(
    action: str,
    reason: str,
    *,
    skill_names: list[str] | None = None,
    canonical_skill: str | None = None,
    cluster_count: int = 0,
    host_operation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "action": action,
        "reason": reason,
        "skill_names": list(skill_names or []),
        "canonical_skill": canonical_skill,
        "cluster_count": cluster_count,
        "host_operation": host_operation,
    }


def archive_duplicate_candidates_action(
    skill_names: list[str],
    *,
    canonical_skill: str,
    cluster_count: int,
    rule_name: str | None = None,
) -> dict[str, Any]:
    return governance_action(
        "archive_duplicate_candidates",
        (
            f'Keep "{canonical_skill}" as canonical for '
            f'{rule_name or "unclassified"} and archive lower-priority duplicates.'
        ),
        skill_names=skill_names,
        canonical_skill=canonical_skill,
        cluster_count=cluster_count,
        host_operation=archive_duplicate_candidates_operation(
            skill_names,
            dry_run=False,
            include_preview=True,
            source_ref=source_ref_archive_duplicate_candidates(canonical_skill),
            preview_source_ref=source_ref_archive_duplicate_candidates_preview(canonical_skill),
        ),
    )


def review_archive_volume_action() -> dict[str, Any]:
    return governance_action(
        "review_archive_volume",
        "Archived skills now outnumber active skills; review whether the library is fragmenting.",
        host_operation=refresh_governance_report_operation(source_ref=source_ref_governance_report_refresh()),
    )


def _default_label(tool_name: str) -> str:
    return tool_name.replace("_", " ").strip().title()


def _operation_id(tool_name: str, arguments: dict[str, Any], display_label: str) -> str:
    payload = json.dumps(
        {
            "tool_name": tool_name,
            "arguments": arguments,
            "display_label": display_label,
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    digest = hashlib.sha1(payload.encode("utf-8")).hexdigest()[:12]
    return f"{tool_name}:{digest}"


def _operation_sort_key(operation: dict[str, Any]) -> tuple[int, str, str]:
    role = operation.get("operation_role", "default")
    rank = {
        "primary": 0,
        "preview": 1,
        "default": 2,
    }.get(role, 3)
    return (
        rank,
        str(operation.get("display_label", "")),
        str(operation.get("operation_id", "")),
    )


def _normalize_schema_type(schema: Any) -> str:
    if isinstance(schema, dict):
        raw_type = schema.get("type")
        if isinstance(raw_type, str):
            return TYPE_ALIASES.get(raw_type.lower(), raw_type.lower())

    if not isinstance(schema, str):
        return "string"

    lowered = schema.lower().strip()
    if lowered.startswith("list[") or lowered.startswith("array["):
        return "array"
    if lowered.startswith("dict["):
        return "object"
    return TYPE_ALIASES.get(lowered, lowered or "string")
