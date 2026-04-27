from __future__ import annotations

import hashlib
import json
from typing import Any

from skill_runtime.mcp.source_refs import source_ref_archive_duplicate_candidates_follow_up

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
            "observed_task": {"type": "object", "required": False, "prefilled": False},
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
    "archive_fixture_skills": {
        "display_label": "Archive fixture skills",
        "effect_summary": "Archive low-priority fixture skills from the active library.",
        "argument_schema": {
            "skill_names": {"type": "array", "required": True, "prefilled": True},
            "dry_run": {"type": "boolean", "required": True, "prefilled": True},
        },
        "risk_level": "high",
        "requires_confirmation": True,
        "confirmation_message": "Archive the suggested fixture skills from the active library?",
        "preview_display_label": "Preview fixture archive",
        "preview_effect_summary": "Preview which fixture skills would be archived without changing the library.",
        "preview_risk_level": "low",
        "preview_requires_confirmation": False,
    },
    "governance_report": {
        "display_label": "Refresh governance report",
        "effect_summary": "Recompute governance recommendations and duplicate clusters.",
        "risk_level": "low",
        "requires_confirmation": False,
    },
    "distill_coverage_report": {
        "display_label": "Refresh distill coverage report",
        "effect_summary": "Recompute deterministic coverage and fallback hotspot clusters across trajectories.",
        "argument_schema": {
            "observed_task_scope": {"type": "string", "required": False, "prefilled": True},
            "max_family_items": {"type": "integer", "required": False, "prefilled": True},
            "min_family_count": {"type": "integer", "required": False, "prefilled": True},
        },
        "risk_level": "low",
        "requires_confirmation": False,
    },
    "capture_trajectory": {
        "display_label": "Capture trajectory",
        "effect_summary": "Capture an observed task record into a reusable trajectory file.",
        "argument_schema": {
            "file_path": {"type": "string", "required": False, "prefilled": False},
            "observed_task": {"type": "object", "required": False, "prefilled": False},
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
    "rollback_operations": {
        "display_label": "Rollback operations",
        "effect_summary": "Rollback a safe subset of execution-side file changes from an operation log.",
        "argument_schema": {
            "operation_log": {"type": "array", "required": True, "prefilled": True},
            "operation_ids": {"type": "array", "required": False, "prefilled": True},
            "dry_run": {"type": "boolean", "required": False, "prefilled": True},
        },
        "risk_level": "medium",
        "requires_confirmation": True,
        "confirmation_message": "Rollback the selected execution changes?",
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

__all__ = [
    "tool_call",
    "tool_call_with_preview",
    "collect_operations",
    "operation_list",
    "execute_skill_argument_schema",
    "execute_skill_operation",
    "capture_trajectory_operation",
    "distill_trajectory_operation",
    "audit_skill_operation",
    "promote_skill_operation",
    "governance_report_operation",
    "distill_coverage_report_operation",
    "refresh_governance_report_operation",
    "archive_duplicate_candidates_operation",
    "archive_fixture_skills_operation",
    "distill_and_promote_operation",
    "rollback_operations_operation",
]


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
    operation_group: str | None = None,
    delivery_mode: str | None = None,
    variant_role: str | None = None,
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
        "operation_group": operation_group,
        "delivery_mode": delivery_mode,
        "variant_role": variant_role,
    }


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
    operation_group: str | None = None,
    delivery_mode: str | None = None,
    preview_operation_group: str | None = None,
    preview_delivery_mode: str | None = None,
    variant_role: str | None = None,
    preview_variant_role: str | None = None,
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
        operation_group=operation_group,
        delivery_mode=delivery_mode,
        variant_role=variant_role,
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
        operation_group=preview_operation_group or operation_group,
        delivery_mode=preview_delivery_mode,
        variant_role=preview_variant_role,
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
    operation_group: str | None = None,
    delivery_mode: str | None = None,
    variant_role: str | None = None,
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
        operation_group=operation_group,
        delivery_mode=delivery_mode,
        variant_role=variant_role,
    )


def capture_trajectory_operation(
    *,
    file_path: str | None = None,
    observed_task: dict[str, Any] | None = None,
    task_id: str | None = None,
    session_id: str | None = None,
    display_label: str | None = None,
    effect_summary: str | None = None,
    argument_schema: dict[str, Any] | None = None,
    risk_level: str | None = None,
    requires_confirmation: bool | None = None,
    confirmation_message: str | None = None,
    operation_role: str = "default",
    source_ref: str | None = None,
    operation_group: str | None = None,
    delivery_mode: str | None = None,
    variant_role: str | None = None,
) -> dict[str, Any]:
    arguments = {}
    if file_path is not None:
        arguments["file_path"] = file_path
    if observed_task is not None:
        arguments["observed_task"] = observed_task
    if task_id is not None:
        arguments["task_id"] = task_id
    if session_id is not None:
        arguments["session_id"] = session_id
    return tool_call(
        "capture_trajectory",
        arguments,
        display_label=display_label,
        effect_summary=effect_summary,
        argument_schema=argument_schema,
        risk_level=risk_level,
        requires_confirmation=requires_confirmation,
        confirmation_message=confirmation_message,
        operation_role=operation_role,
        source_ref=source_ref,
        operation_group=operation_group,
        delivery_mode=delivery_mode,
        variant_role=variant_role,
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
    operation_group: str | None = None,
    delivery_mode: str | None = None,
    variant_role: str | None = None,
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
        operation_group=operation_group,
        delivery_mode=delivery_mode,
        variant_role=variant_role,
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


def rollback_operations_operation(
    operation_log: list[dict[str, Any]],
    *,
    operation_ids: list[str] | None = None,
    dry_run: bool | None = None,
    display_label: str | None = None,
    effect_summary: str | None = None,
    argument_schema: dict[str, Any] | None = None,
    risk_level: str | None = None,
    requires_confirmation: bool | None = None,
    confirmation_message: str | None = None,
    operation_role: str = "default",
    source_ref: str | None = None,
    operation_group: str | None = None,
    delivery_mode: str | None = None,
    variant_role: str | None = None,
) -> dict[str, Any]:
    arguments: dict[str, Any] = {"operation_log": operation_log}
    if operation_ids is not None:
        arguments["operation_ids"] = operation_ids
    if dry_run is not None:
        arguments["dry_run"] = dry_run
    return tool_call(
        "rollback_operations",
        arguments,
        display_label=display_label,
        effect_summary=effect_summary,
        argument_schema=argument_schema,
        risk_level=risk_level,
        requires_confirmation=requires_confirmation,
        confirmation_message=confirmation_message,
        operation_role=operation_role,
        source_ref=source_ref,
        operation_group=operation_group,
        delivery_mode=delivery_mode,
        variant_role=variant_role,
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


def distill_coverage_report_operation(
    observed_task_scope: str | None = None,
    max_family_items: int | None = None,
    min_family_count: int | None = None,
    *,
    display_label: str | None = None,
    effect_summary: str | None = None,
    risk_level: str | None = None,
    requires_confirmation: bool | None = None,
    confirmation_message: str | None = None,
    operation_role: str = "default",
    source_ref: str | None = None,
) -> dict[str, Any]:
    arguments: dict[str, Any] = {}
    if observed_task_scope is not None:
        arguments["observed_task_scope"] = observed_task_scope
    if max_family_items is not None:
        arguments["max_family_items"] = max_family_items
    if min_family_count is not None:
        arguments["min_family_count"] = min_family_count
    return tool_call(
        "distill_coverage_report",
        arguments,
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


def archive_fixture_skills_operation(
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
            "archive_fixture_skills",
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
        "archive_fixture_skills",
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
    observed_task: dict[str, Any] | None = None,
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
    operation_group: str | None = None,
    delivery_mode: str | None = None,
    variant_role: str | None = None,
) -> dict[str, Any]:
    arguments = {}
    if trajectory_path is not None:
        arguments["trajectory_path"] = trajectory_path
    if observed_task_path is not None:
        arguments["observed_task_path"] = observed_task_path
    if observed_task is not None:
        arguments["observed_task"] = observed_task
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
        operation_group=operation_group,
        delivery_mode=delivery_mode,
        variant_role=variant_role,
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
