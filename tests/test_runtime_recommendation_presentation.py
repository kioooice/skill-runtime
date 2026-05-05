from copy import deepcopy
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


class RuntimeRecommendationPresentationTestsMixin:
    def test_recommendation_presentation_shows_observed_only_as_manual_observation(self) -> None:
        from skill_runtime.presentation.recommendation import format_recommendation_card

        payload = {
            "learning_decision": {
                "decision": "observed_only",
                "reason": "task succeeded, but the evidence was too weak for immediate distillation",
            },
            "recommended_next_action": None,
            "recommended_host_operation": None,
            "available_host_operations": [],
        }

        card = format_recommendation_card(payload)

        self.assertEqual("Keep as observation", card["title"])
        self.assertIsNone(card["recommended_action"])
        self.assertIn("not strong enough", card["boundary"])
        self.assertIn("Human review", card["boundary"])
        self.assertFalse(card["is_automatic"])

    def test_recommendation_presentation_shows_background_hint_execute_skill(self) -> None:
        from skill_runtime.presentation.recommendation import format_recommendation_card

        payload = {
            "reuse_decision": {
                "decision": "background_hint",
                "reason": "a plausible reusable match exists, but the agent should keep solving normally",
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
        }

        card = format_recommendation_card(payload)

        self.assertEqual("Reuse candidate found", card["title"])
        self.assertEqual("execute_skill", card["recommended_action"])
        self.assertEqual("execute_skill", card["tool_name"])
        self.assertEqual(["output_path"], card["missing_inputs"])
        self.assertIn("not automatic execution", card["boundary"])
        self.assertFalse(card["is_automatic"])

    def test_recommendation_presentation_shows_new_skill_candidate_distill_trajectory(self) -> None:
        from skill_runtime.presentation.recommendation import format_recommendation_card

        payload = {
            "learning_decision": {
                "decision": "new_skill_candidate",
                "reason": "task succeeded with a concrete under-covered workflow pattern",
            },
            "learning_capture_payload": {"trajectory_path": "trajectories/task.json"},
            "recommended_next_action": "distill_trajectory",
            "recommended_host_operation": {
                "tool_name": "distill_trajectory",
                "display_label": "Distill trajectory",
                "risk_level": "low",
                "requires_confirmation": False,
                "arguments": {"trajectory_path": "trajectories/task.json"},
            },
            "available_host_operations": [],
        }

        card = format_recommendation_card(payload)

        self.assertEqual("Distill captured workflow", card["title"])
        self.assertEqual("distill_trajectory", card["recommended_action"])
        self.assertEqual("distill_trajectory", card["tool_name"])
        self.assertIn("does not promote", card["boundary"])
        self.assertIn("not automatic", card["boundary"])

    def test_recommendation_presentation_shows_improvement_review_without_apply(self) -> None:
        from skill_runtime.presentation.recommendation import format_recommendation_card

        payload = {
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
        }

        card = format_recommendation_card(payload)

        self.assertEqual("Review existing-skill improvement", card["title"])
        self.assertEqual("review_evolution_candidate", card["recommended_action"])
        self.assertTrue(card["requires_confirmation"])
        self.assertIn("does not apply", card["boundary"])
        self.assertIn("Human confirmation", card["boundary"])

    def test_recommendation_presentation_does_not_mutate_original_payload(self) -> None:
        from skill_runtime.presentation.recommendation import format_recommendation_card

        payload = {
            "reuse_decision": {"decision": "background_hint", "missing_inputs": ["output_path"]},
            "recommended_next_action": "execute_skill",
            "recommended_host_operation": {"tool_name": "execute_skill", "requires_confirmation": False},
            "available_host_operations": [],
        }
        original = deepcopy(payload)

        format_recommendation_card(payload)

        self.assertEqual(original, payload)

    def test_recommendation_presentation_demo_script_outputs_all_fixture_cards(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/demo_recommendation_presentation.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        output = result.stdout
        payload = json.loads(output)
        titles = [item["card"]["title"] for item in payload["examples"]]

        self.assertEqual(
            [
                "Keep as observation",
                "Reuse candidate found",
                "Distill captured workflow",
                "Review existing-skill improvement",
            ],
            titles,
        )
        self.assertIn("not automatic", output)
        self.assertIn("does not promote", output)
        self.assertIn("does not apply", output)
        self.assertIn("Human confirmation", output)
