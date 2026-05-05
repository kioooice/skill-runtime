from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from skill_runtime.presentation.recommendation import (  # noqa: E402
    format_recommendation_card,
    format_recommendation_text,
)


def main() -> int:
    examples = [
        _render_example(
            "observed_only",
            {
                "learning_decision": {
                    "decision": "observed_only",
                    "reason": (
                        "task succeeded, but the evidence was too weak for immediate distillation"
                    ),
                },
                "recommended_next_action": None,
                "recommended_host_operation": None,
                "available_host_operations": [],
            },
        ),
        _render_example(
            "background_hint_execute_skill",
            {
                "reuse_decision": {
                    "decision": "background_hint",
                    "reason": (
                        "a plausible reusable match exists, but the agent should keep solving normally"
                    ),
                    "skill_name": "merge_text_files",
                    "missing_inputs": ["output_path"],
                },
                "recommended_next_action": "execute_skill",
                "recommended_host_operation": {
                    "tool_name": "execute_skill",
                    "display_label": "Run skill",
                    "risk_level": "low",
                    "requires_confirmation": False,
                    "arguments": {"skill_name": "merge_text_files", "args": {}},
                },
                "available_host_operations": [],
            },
        ),
        _render_example(
            "new_skill_candidate_distill_trajectory",
            {
                "learning_decision": {
                    "decision": "new_skill_candidate",
                    "reason": "task succeeded with a concrete under-covered workflow pattern",
                },
                "learning_capture_payload": {"trajectory_path": "trajectories/example_task.json"},
                "recommended_next_action": "distill_trajectory",
                "recommended_host_operation": {
                    "tool_name": "distill_trajectory",
                    "display_label": "Distill trajectory",
                    "risk_level": "low",
                    "requires_confirmation": False,
                    "arguments": {"trajectory_path": "trajectories/example_task.json"},
                },
                "available_host_operations": [],
            },
        ),
        _render_example(
            "improve_existing_skill_candidate_review_evolution",
            {
                "learning_decision": {
                    "decision": "improve_existing_skill_candidate",
                    "reason": "task exposed a concrete existing-skill gap",
                },
                "learning_capture_payload": {"evolution_candidate_path": "evolution/candidate.json"},
                "recommended_next_action": "review_evolution_candidate",
                "recommended_host_operation": {
                    "tool_name": "review_evolution_candidate",
                    "display_label": "Review evolution candidate",
                    "risk_level": "low",
                    "requires_confirmation": True,
                    "confirmation_message": "Review before editing any global skill.",
                    "arguments": {"candidate": "evolution/candidate.json"},
                },
                "available_host_operations": [],
            },
        ),
    ]
    print(json.dumps({"examples": examples}, ensure_ascii=False, indent=2))
    return 0


def _render_example(example_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "example_id": example_id,
        "card": format_recommendation_card(payload),
        "text": format_recommendation_text(payload),
    }


if __name__ == "__main__":
    raise SystemExit(main())
