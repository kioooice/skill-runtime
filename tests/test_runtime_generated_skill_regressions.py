import json
from pathlib import Path

from skill_runtime.api.models import Trajectory, TrajectoryStep
from skill_runtime.distill.skill_generator import SkillGenerator
from tests.runtime_test_support import ROOT


class RuntimeGeneratedSkillRegressionTestsMixin:
    def test_full_generated_skill_promotion_flow(self) -> None:
        generated_name = "merge_text_files_promoted_test"
        output_path = ROOT / "demo" / "output" / "promoted_generated.md"
        if output_path.exists():
            output_path.unlink()

        self._run_cli(
            "distill",
            "--trajectory",
            "trajectories/demo_merge_text_files.json",
            "--skill-name",
            generated_name,
        )
        self._run_cli("audit", "--file", f"skill_store/staging/{generated_name}.py")
        self._run_cli("promote", "--file", f"skill_store/staging/{generated_name}.py")

        args_file = self._write_args_file(
            "promoted_execute_args.json",
            {"input_dir": "demo/input", "output_path": "demo/output/promoted_generated.md"},
        )
        self._execute_skill_cli(generated_name, args_file=args_file)
        self.assertTrue(output_path.exists())
        self.assertIn("hello from file b", output_path.read_text(encoding="utf-8"))

        promoted = self.index.get(generated_name)
        self.assertIsNotNone(promoted)
        self.assertEqual("text_merge", promoted.rule_name)
        self.assertIsNotNone(promoted.rule_reason)

    def test_unmatched_trajectory_uses_llm_fallback_artifact(self) -> None:
        trajectory = Trajectory(
            task_id="fallback_demo",
            session_id="session_fallback_demo",
            task_description="Generate a report from mixed observations without a known deterministic file rule.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="observe_state",
                    tool_input={"report_name": "weekly_report"},
                    observation="Collected mixed observations.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="summarize_notes",
                    tool_input={"topic": "weekly_report"},
                    observation="Summarized notes into a draft.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/fallback_report.txt"],
            started_at="2026-04-18T12:00:00",
            ended_at="2026-04-18T12:01:00",
        )

        generated = SkillGenerator(ROOT / "skill_store" / "staging").generate(
            trajectory, skill_name="fallback_rule_test"
        )
        self.assertEqual("llm_fallback", generated["metadata"].rule_name)
        self.assertEqual(0, generated["metadata"].rule_priority)
        self.assertIsNotNone(generated["fallback_artifact"])
        artifact_path = Path(generated["fallback_artifact"])
        self.assertTrue(artifact_path.exists())
        artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
        self.assertEqual("mock_fallback_provider", artifact["response"]["provider_name"])
        self.assertIn("Skill name: fallback_rule_test", artifact["request"]["prompt"])
