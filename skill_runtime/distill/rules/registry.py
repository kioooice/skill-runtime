from typing import Any

from skill_runtime.api.models import Trajectory


def get_rule_name(rule: Any) -> str:
    return getattr(rule, "RULE_NAME", rule.__name__.split(".")[-1])


def get_rule_priority(rule: Any) -> int:
    return int(getattr(rule, "PRIORITY", 100))


def explain_match(rule: Any, trajectory: Trajectory, input_schema: dict[str, str]) -> str:
    if hasattr(rule, "explain_match"):
        return rule.explain_match(trajectory, input_schema)
    return f"Matched rule {get_rule_name(rule)}."
