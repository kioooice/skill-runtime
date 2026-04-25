from pathlib import Path

from skill_runtime.api.models import Trajectory, TrajectoryStep
from skill_runtime.audit.skill_auditor import SkillAuditor
from skill_runtime.distill.skill_generator import SkillGenerator
from skill_runtime.memory.trajectory_store import TrajectoryStore
from tests.runtime_test_support import ROOT


class RuntimeAuditLifecycleTestsMixin:
    def test_audit_detects_shell_true(self) -> None:
        skill_path = ROOT / "skill_store" / "staging" / "unsafe_skill.py"
        skill_path.parent.mkdir(parents=True, exist_ok=True)
        skill_path.write_text(
            'import subprocess\n'
            'def run(tools, **kwargs):\n'
            '    """bad"""\n'
            '    subprocess.run("echo hi", shell=True)\n',
            encoding="utf-8",
        )
        self.addCleanup(skill_path.unlink)

        report = SkillAuditor().audit(skill_path)
        self.assertEqual("needs_fix", report.status)
        self.assertLess(report.security_score, 100)

    def test_semantic_audit_flags_template_skill_against_trajectory(self) -> None:
        skill_path = ROOT / "skill_store" / "staging" / "semantic_template_skill.py"
        skill_path.parent.mkdir(parents=True, exist_ok=True)
        skill_path.write_text(
            'def run(tools, **kwargs):\n'
            '    """\n'
            '    功能描述:\n'
            '        Placeholder skill.\n\n'
            '    输入参数:\n'
            '        - input_dir: str\n'
            '        - output_path: str\n\n'
            '    输出结果:\n'
            '        - status: str\n'
            '    """\n'
            '    inputs = {"input_dir": kwargs.get("input_dir"), "output_path": kwargs.get("output_path")}\n'
            '    missing = [key for key, value in inputs.items() if value is None]\n'
            '    if missing:\n'
            '        raise ValueError(missing)\n'
            '    return {"status": "completed", "inputs": inputs, "steps_executed": 3}\n',
            encoding="utf-8",
        )
        self.addCleanup(skill_path.unlink)

        trajectory = TrajectoryStore(ROOT / "trajectories").load("demo_merge_text_files")
        report = SkillAuditor().audit(skill_path, trajectory=trajectory)
        self.assertEqual("needs_fix", report.status)
        self.assertLess(report.semantic_score, 100)
        self.assertTrue(
            any("template" in finding.lower() or "trajectory" in finding.lower() for finding in report.semantic_findings)
        )
        self.assertEqual("mock_semantic_review_provider", report.semantic_provider)
        self.assertIsNotNone(report.semantic_artifact)
        self.assertTrue(Path(report.semantic_artifact).exists())

    def test_service_audit_with_trajectory_returns_semantic_fields(self) -> None:
        result = self.service.audit(
            ROOT / "skill_store" / "active" / "merge_text_files.py",
            trajectory_path=ROOT / "trajectories" / "demo_merge_text_files.json",
        )
        report = result["report"]
        self.assertEqual("passed", report["status"])
        self.assertIn("static_score", report)
        self.assertIn("semantic_score", report)
        self.assertIn("semantic_findings", report)
        self.assertEqual([], report["semantic_findings"])
        self.assertEqual("mock_semantic_review_provider", report["semantic_provider"])
        self.assertTrue(Path(report["semantic_artifact"]).exists())

    def test_service_audit_returns_promote_follow_up_on_pass(self) -> None:
        distill_result = self.service.distill(
            ROOT / "trajectories" / "demo_merge_text_files.json",
            skill_name="service_audit_followup_test",
        )
        result = self.service.audit(
            distill_result["staging_file"],
            trajectory_path=distill_result["trajectory_path"],
        )
        self.assertEqual("promote_skill", result["recommended_next_action"])
        self._assert_host_operation_basics(
            result["recommended_host_operation"],
            tool_name="promote_skill",
        )
        self.assertEqual(
            distill_result["staging_file"],
            result["recommended_host_operation"]["arguments"]["file_path"],
        )
        self._assert_operation_role(result["available_host_operations"][0], "primary")

    def test_service_promote_returns_execute_follow_up(self) -> None:
        distill_result = self.service.distill(
            ROOT / "trajectories" / "demo_merge_text_files.json",
            skill_name="service_promote_followup_test",
        )
        audit_result = self.service.audit(
            distill_result["staging_file"],
            trajectory_path=distill_result["trajectory_path"],
        )
        self.assertEqual("promote_skill", audit_result["recommended_next_action"])

        result = self.service.promote(distill_result["staging_file"])
        self.assertEqual("execute_skill", result["recommended_next_action"])
        self._assert_host_operation_basics(
            result["recommended_host_operation"],
            tool_name="execute_skill",
        )
        self.assertEqual(
            "service_promote_followup_test",
            result["recommended_host_operation"]["arguments"]["skill_name"],
        )
        self._assert_execute_skill_schema(result["recommended_host_operation"])
        self._assert_operation_role(result["available_host_operations"][0], "primary")

    def test_mcp_promote_returns_execute_follow_up(self) -> None:
        distill_result = self.service.distill(
            ROOT / "trajectories" / "demo_merge_text_files.json",
            skill_name="mcp_promote_followup_test",
        )
        self.service.audit(
            distill_result["staging_file"],
            trajectory_path=distill_result["trajectory_path"],
        )

        payload = self._call_mcp_tool(
            "promote_skill",
            {"file_path": distill_result["staging_file"]},
        )
        self.assertEqual("execute_skill", payload["data"]["recommended_next_action"])
        self._assert_host_operation_basics(
            payload["data"]["recommended_host_operation"],
            tool_name="execute_skill",
        )
        self._assert_execute_skill_schema(payload["data"]["recommended_host_operation"])

    def test_provider_backed_semantic_review_flags_fallback_generated_skill(self) -> None:
        trajectory = Trajectory(
            task_id="fallback_semantic_audit_demo",
            session_id="session_fallback_semantic_audit",
            task_description="Generate a report from mixed observations without a deterministic rule.",
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
            artifacts=["demo/output/fallback_semantic.txt"],
            started_at="2026-04-24T14:00:00",
            ended_at="2026-04-24T14:01:00",
        )

        generated = SkillGenerator(ROOT / "skill_store" / "staging").generate(
            trajectory, skill_name="semantic_provider_fallback_test"
        )
        report = SkillAuditor().audit(generated["skill_file"], trajectory=trajectory)
        self.assertEqual("mock_semantic_review_provider", report.semantic_provider)
        self.assertIsNotNone(report.semantic_artifact)
        self.assertTrue(Path(report.semantic_artifact).exists())
        self.assertTrue(
            any("fallback" in finding.lower() or "template" in finding.lower() for finding in report.semantic_findings)
        )
