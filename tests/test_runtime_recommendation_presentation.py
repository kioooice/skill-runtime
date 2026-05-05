from copy import deepcopy
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
RECOMMENDATION_FIXTURE_DIR = ROOT / "docs" / "fixtures" / "recommendation-payloads"


class RuntimeRecommendationPresentationTestsMixin:
    def test_cli_capture_trajectory_default_output_stays_json_only(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/skill_cli.py",
                "--root",
                str(self.runtime_root),
                "capture-trajectory",
                "--file",
                "demo/maintainer_review_cleanup/observed_task.json",
                "--task-id",
                "cli_recommendation_default_output",
                "--session-id",
                "cli_recommendation_default_output",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

        self.assertEqual(0, result.returncode, msg=result.stderr or result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual("ok", payload["status"])
        self.assertEqual("distill_trajectory", payload["data"]["recommended_next_action"])
        self.assertEqual("", result.stderr)

    def test_cli_capture_trajectory_render_recommendation_text_keeps_json_audit_output(self) -> None:
        staging_dir = self.runtime_root / "skill_store" / "staging"
        staging_before = sorted(
            str(path.relative_to(self.runtime_root))
            for path in staging_dir.rglob("*")
            if path.is_file()
        )

        result = subprocess.run(
            [
                sys.executable,
                "scripts/skill_cli.py",
                "--root",
                str(self.runtime_root),
                "capture-trajectory",
                "--file",
                "demo/maintainer_review_cleanup/observed_task.json",
                "--task-id",
                "cli_recommendation_text_output",
                "--session-id",
                "cli_recommendation_text_output",
                "--render-recommendation",
                "text",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

        self.assertEqual(0, result.returncode, msg=result.stderr or result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual("ok", payload["status"])
        self.assertEqual("distill_trajectory", payload["data"]["recommended_next_action"])
        self.assertIn("Follow-up: Distill captured workflow", result.stderr)
        self.assertIn("does not promote", result.stderr)
        self.assertIn("not automatic promotion", result.stderr)

        staging_after = sorted(
            str(path.relative_to(self.runtime_root))
            for path in staging_dir.rglob("*")
            if path.is_file()
        )
        self.assertEqual(staging_before, staging_after)

    def test_cli_recommendation_rendering_helper_handles_non_recommendation_payload(self) -> None:
        from skill_runtime.cli import render_recommendation_text_for_payload

        text = render_recommendation_text_for_payload(
            {"captured": True, "trajectory_path": "trajectories/example.json"},
            recommendation_format="text",
        )

        self.assertIsNotNone(text)
        self.assertIn("Follow-up: No automatic follow-up", text)
        self.assertIn("No host operation should run automatically", text)

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

    def test_render_recommendation_presentation_text_from_payload_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            payload_path = Path(tmp_dir) / "payload.json"
            original = json.dumps(_sample_recommendation_payload(), indent=2)
            payload_path.write_text(original, encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/render_recommendation_presentation.py",
                    "--input",
                    str(payload_path),
                    "--format",
                    "text",
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertIn("Follow-up: Distill captured workflow", result.stdout)
            self.assertIn("does not promote", result.stdout)
            self.assertEqual(original, payload_path.read_text(encoding="utf-8"))

    def test_render_recommendation_presentation_json_from_payload_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            payload_path = Path(tmp_dir) / "payload.json"
            original = json.dumps(_sample_recommendation_payload(), indent=2)
            payload_path.write_text(original, encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/render_recommendation_presentation.py",
                    "--input",
                    str(payload_path),
                    "--format",
                    "json",
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )

            rendered = json.loads(result.stdout)
            self.assertIn("card", rendered)
            self.assertEqual("Distill captured workflow", rendered["card"]["title"])
            self.assertEqual(
                "distill_trajectory",
                rendered["card"]["recommended_action"],
            )
            self.assertEqual(original, payload_path.read_text(encoding="utf-8"))

    def test_render_recommendation_presentation_missing_file_returns_error(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/render_recommendation_presentation.py",
                "--input",
                "does-not-exist.json",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(0, result.returncode)
        self.assertIn("Input file not found", result.stderr)

    def test_render_recommendation_presentation_non_object_json_returns_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            payload_path = Path(tmp_dir) / "payload.json"
            original = "[1, 2, 3]"
            payload_path.write_text(original, encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/render_recommendation_presentation.py",
                    "--input",
                    str(payload_path),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(0, result.returncode)
            self.assertIn("Payload must be a JSON object", result.stderr)
            self.assertEqual(original, payload_path.read_text(encoding="utf-8"))

    def test_render_recommendation_presentation_invalid_json_returns_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            payload_path = Path(tmp_dir) / "payload.json"
            original = "{not valid json"
            payload_path.write_text(original, encoding="utf-8")

            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/render_recommendation_presentation.py",
                    "--input",
                    str(payload_path),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(0, result.returncode)
            self.assertIn("Invalid JSON", result.stderr)
            self.assertEqual(original, payload_path.read_text(encoding="utf-8"))

    def test_dogfood_recommendation_presentation_script_outputs_fixture_scenarios(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/dogfood_recommendation_presentation.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        payload = json.loads(result.stdout)
        scenario_ids = [item["scenario_id"] for item in payload["scenarios"]]

        self.assertEqual(
            [
                "background_hint_execute_skill_missing_inputs",
                "improve_existing_skill_candidate_review_evolution",
                "new_skill_candidate_distill_trajectory",
            ],
            scenario_ids,
        )
        self.assertEqual(3, payload["summary"]["scenario_count"])
        self.assertIn("not automatic execution", result.stdout)
        self.assertIn("does not promote", result.stdout)
        self.assertIn("does not apply", result.stdout)

    def test_dogfood_recommendation_presentation_script_does_not_modify_fixture_payloads(self) -> None:
        originals = {
            path.name: path.read_text(encoding="utf-8")
            for path in sorted(RECOMMENDATION_FIXTURE_DIR.glob("*.json"))
        }

        subprocess.run(
            [sys.executable, "scripts/dogfood_recommendation_presentation.py"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        after = {
            path.name: path.read_text(encoding="utf-8")
            for path in sorted(RECOMMENDATION_FIXTURE_DIR.glob("*.json"))
        }
        self.assertEqual(originals, after)


def _sample_recommendation_payload() -> dict[str, object]:
    return {
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
