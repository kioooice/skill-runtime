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


FIXTURE_DIR = ROOT / "docs" / "fixtures" / "recommendation-payloads"


def main() -> int:
    scenarios = [_render_scenario(path) for path in sorted(FIXTURE_DIR.glob("*.json"))]
    summary = {
        "scenario_count": len(scenarios),
        "helper_sufficient": all(item["helper_sufficient"] for item in scenarios),
        "ambiguous_scenarios": [
            item["scenario_id"] for item in scenarios if item["ambiguities"]
        ],
        "next_action": "real host integration dogfood / operator validation",
    }
    print(
        json.dumps(
            {
                "fixture_dir": str(FIXTURE_DIR),
                "scenarios": scenarios,
                "summary": summary,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def _render_scenario(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    card = format_recommendation_card(payload)
    text = format_recommendation_text(payload)
    return {
        "scenario_id": path.stem,
        "payload_path": str(path.relative_to(ROOT)),
        "recommended_next_action": payload.get("recommended_next_action"),
        "card": card,
        "text": text,
        "operator_interpretation": _operator_interpretation(card),
        "ambiguities": _ambiguities(card),
        "helper_sufficient": True,
    }


def _operator_interpretation(card: dict[str, Any]) -> str:
    action = card.get("recommended_action")
    if action == "execute_skill":
        return "The operator can see a suggested reusable skill, but still needs to provide missing inputs before choosing to run it."
    if action == "distill_trajectory":
        return "The operator can see that the successful workflow should move into staging through distillation, not directly into promotion."
    if action == "review_evolution_candidate":
        return "The operator can see that the next step is manual review of an evolution candidate, not automatic apply."
    return "The operator can see that no automatic governed follow-up should run."


def _ambiguities(card: dict[str, Any]) -> list[str]:
    ambiguities: list[str] = []
    if card.get("recommended_action") == "execute_skill" and not card.get("missing_inputs"):
        ambiguities.append("execute_skill suggestion is missing the required missing_inputs context")
    return ambiguities


if __name__ == "__main__":
    raise SystemExit(main())
