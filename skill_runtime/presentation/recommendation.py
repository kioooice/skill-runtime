from __future__ import annotations

from typing import Any


def format_recommendation_card(payload: dict[str, Any]) -> dict[str, Any]:
    """Format an existing recommendation payload for operator display.

    This is intentionally presentation-only: it does not mutate the input,
    execute operations, or alter recommendation decisions.
    """
    reuse_decision = _mapping(payload.get("reuse_decision"))
    learning_decision = _mapping(payload.get("learning_decision"))
    host_operation = _mapping(payload.get("recommended_host_operation"))

    action = _string_or_none(payload.get("recommended_next_action"))
    tool_name = _string_or_none(host_operation.get("tool_name"))
    decision = _string_or_none(learning_decision.get("decision")) or _string_or_none(
        reuse_decision.get("decision")
    )

    title, status, boundary = _display_for_decision(
        decision=decision,
        action=action,
        tool_name=tool_name,
    )

    reason = (
        _string_or_none(payload.get("recommended_reason"))
        or _string_or_none(learning_decision.get("reason"))
        or _string_or_none(reuse_decision.get("reason"))
        or _string_or_none(host_operation.get("effect_summary"))
    )
    requires_confirmation = bool(host_operation.get("requires_confirmation", False))

    return {
        "title": title,
        "status": status,
        "recommended_action": action,
        "tool_name": tool_name,
        "reason": reason,
        "boundary": boundary,
        "requires_confirmation": requires_confirmation,
        "confirmation_message": _string_or_none(host_operation.get("confirmation_message")),
        "missing_inputs": _string_list(reuse_decision.get("missing_inputs")),
        "risk_level": _string_or_none(host_operation.get("risk_level")),
        "display_label": _string_or_none(host_operation.get("display_label")),
        "is_automatic": False,
    }


def format_recommendation_text(payload: dict[str, Any]) -> str:
    card = format_recommendation_card(payload)
    lines = [
        f"Follow-up: {card['title']}",
        f"Status: {card['status']}",
    ]
    if card["reason"]:
        lines.append(f"Why: {card['reason']}")
    if card["recommended_action"]:
        lines.append(f"Recommended action: {card['recommended_action']}")
    if card["tool_name"]:
        lines.append(f"Tool: {card['tool_name']}")
    if card["missing_inputs"]:
        lines.append(f"Missing inputs: {', '.join(card['missing_inputs'])}")
    lines.append(f"Boundary: {card['boundary']}")
    if card["requires_confirmation"]:
        message = card["confirmation_message"] or "Human confirmation is required before continuing."
        lines.append(f"Confirmation: {message}")
    return "\n".join(lines)


def _display_for_decision(
    *,
    decision: str | None,
    action: str | None,
    tool_name: str | None,
) -> tuple[str, str, str]:
    if decision == "background_hint" or action == "execute_skill" or tool_name == "execute_skill":
        return (
            "Reuse candidate found",
            "A reusable skill may help, but the host should not run it automatically.",
            "This is not automatic execution. The operator must provide missing inputs or confirm the call.",
        )

    if decision == "new_skill_candidate" or action == "distill_trajectory":
        return (
            "Distill captured workflow",
            "A successful workflow may be reusable.",
            "This creates a staging candidate; it does not promote an active skill and is not automatic promotion.",
        )

    if decision == "improve_existing_skill_candidate" or action == "review_evolution_candidate":
        return (
            "Review existing-skill improvement",
            "A concrete existing-skill gap should be reviewed manually.",
            "This only reviews the proposed change; it does not apply it automatically. Human confirmation is required before any later apply operation.",
        )

    if decision == "observed_only":
        return (
            "Keep as observation",
            "The task can be recorded, but should not become a skill automatically.",
            "The evidence is not strong enough for automatic distillation or evolution. Human review is required before turning this observation into a reusable workflow.",
        )

    return (
        "No automatic follow-up",
        "No concrete governed follow-up is recommended.",
        "No host operation should run automatically. Human review is required before continuing.",
    )


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _string_or_none(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value
    return None


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item.strip()]
