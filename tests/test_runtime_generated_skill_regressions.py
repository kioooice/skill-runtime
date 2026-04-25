import json
from pathlib import Path

from skill_runtime.api.models import Trajectory, TrajectoryStep
from skill_runtime.distill.skill_generator import SkillGenerator
from tests.runtime_test_support import ROOT


class RuntimeGeneratedSkillRegressionTestsMixin:
    def test_full_generated_skill_promotion_flow(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        generated_name = "merge_text_files_promoted_test"
        output_path = sandbox_root / "demo" / "output" / "promoted_generated.md"

        self._run_cli(
            "distill",
            "--trajectory",
            str(sandbox_root / "trajectories" / "demo_merge_text_files.json"),
            "--skill-name",
            generated_name,
            root=sandbox_root,
        )
        self._run_cli(
            "audit",
            "--file",
            str(sandbox_root / "skill_store" / "staging" / f"{generated_name}.py"),
            root=sandbox_root,
        )
        self._run_cli(
            "promote",
            "--file",
            str(sandbox_root / "skill_store" / "staging" / f"{generated_name}.py"),
            root=sandbox_root,
        )

        args_file = self._write_args_file(
            "promoted_execute_args.json",
            {"input_dir": "demo/input", "output_path": "demo/output/promoted_generated.md"},
            root=sandbox_root,
        )
        self._execute_skill_cli(generated_name, args_file=args_file, root=sandbox_root)
        self.assertTrue(output_path.exists())
        self.assertIn("hello from file b", output_path.read_text(encoding="utf-8"))

        promoted = sandbox_index.get(generated_name)
        self.assertIsNotNone(promoted)
        self.assertEqual("text_merge", promoted.rule_name)
        self.assertIsNotNone(promoted.rule_reason)

    def test_unmatched_trajectory_uses_llm_fallback_artifact(self) -> None:
        sandbox_root, _, _ = self._make_runtime_sandbox()
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

        generated = SkillGenerator(sandbox_root / "skill_store" / "staging").generate(
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
