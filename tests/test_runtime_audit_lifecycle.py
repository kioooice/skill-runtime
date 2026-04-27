from pathlib import Path

from skill_runtime.api.service import RuntimeServiceError
from skill_runtime.api.models import Trajectory, TrajectoryStep
from skill_runtime.audit.skill_auditor import SkillAuditor
from skill_runtime.distill.skill_generator import SkillGenerator
from skill_runtime.memory.trajectory_store import TrajectoryStore
from tests.runtime_test_support import ROOT


class RuntimeAuditLifecycleTestsMixin:
    def test_audit_detects_shell_true(self) -> None:
        sandbox_root, _, _ = self._make_runtime_sandbox()
        skill_path = sandbox_root / "skill_store" / "staging" / "unsafe_skill.py"
        skill_path.parent.mkdir(parents=True, exist_ok=True)
        skill_path.write_text(
            'import subprocess\n'
            'def run(tools, **kwargs):\n'
            '    """bad"""\n'
            '    subprocess.run("echo hi", shell=True)\n',
            encoding="utf-8",
        )
        self.addCleanup(skill_path.unlink)

        report = SkillAuditor(sandbox_root / "audits").audit(skill_path)
        self.assertEqual("needs_fix", report.status)
        self.assertLess(report.security_score, 100)

    def test_semantic_audit_flags_template_skill_against_trajectory(self) -> None:
        sandbox_root, _, _ = self._make_runtime_sandbox()
        skill_path = sandbox_root / "skill_store" / "staging" / "semantic_template_skill.py"
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

        trajectory = TrajectoryStore(sandbox_root / "trajectories").load("demo_merge_text_files")
        report = SkillAuditor(sandbox_root / "audits").audit(skill_path, trajectory=trajectory)
        self.assertEqual("needs_fix", report.status)
        self.assertLess(report.semantic_score, 100)
        self.assertTrue(
            any("template" in finding.lower() or "trajectory" in finding.lower() for finding in report.semantic_findings)
        )
        self.assertEqual("mock_semantic_review_provider", report.semantic_provider)
        self.assertIsNotNone(report.semantic_artifact)
        self.assertTrue(Path(report.semantic_artifact).exists())

    def test_service_audit_with_trajectory_returns_semantic_fields(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        result = sandbox_service.audit(
            sandbox_root / "skill_store" / "active" / "merge_text_files.py",
            trajectory_path=sandbox_root / "trajectories" / "demo_merge_text_files.json",
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
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        distill_result = sandbox_service.distill(
            sandbox_root / "trajectories" / "demo_merge_text_files.json",
            skill_name="service_audit_followup_test",
        )
        result = sandbox_service.audit(
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

    def test_semantic_audit_accepts_single_file_rename_source_target_aliases(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        trajectory = Trajectory(
            task_id="single_rename_alias_demo",
            session_id="session_single_rename_alias",
            task_description="Rename one text file to a new output path.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="rename_path",
                    tool_input={"source": "demo/input/a.txt", "target": "demo/output/renamed_a.txt"},
                    observation="Renamed the source file.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/renamed_a.txt"],
            started_at="2026-04-25T10:00:00",
            ended_at="2026-04-25T10:01:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="single_file_rename_alias_audit_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        report = SkillAuditor(sandbox_root / "audits").audit(generated["skill_file"], trajectory=trajectory)
        self.assertEqual("passed", report.status)
        self.assertEqual([], report.semantic_findings)

    def test_semantic_audit_accepts_directory_move_source_target_path_aliases(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        trajectory = Trajectory(
            task_id="directory_move_path_alias_demo",
            session_id="session_directory_move_path_alias",
            task_description="Move matching log files from one directory into another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/input", "pattern": "*.log"},
                    observation="Listed matching log files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="rename_path",
                    tool_input={
                        "source_path": "demo/input/a.log",
                        "target_path": "demo/output/a.log",
                    },
                    observation="Moved the matching file into the output directory.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/a.log"],
            started_at="2026-04-26T12:00:00",
            ended_at="2026-04-26T12:01:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="directory_move_path_alias_audit_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        report = SkillAuditor(sandbox_root / "audits").audit(generated["skill_file"], trajectory=trajectory)
        self.assertEqual("passed", report.status)
        self.assertEqual([], report.semantic_findings)

    def test_semantic_audit_accepts_directory_copy_source_destination_path_aliases(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        trajectory = Trajectory(
            task_id="directory_copy_path_alias_demo",
            session_id="session_directory_copy_path_alias",
            task_description="Copy matching text files from one directory into another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/input", "pattern": "*.txt"},
                    observation="Listed matching text files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="copy_file",
                    tool_input={
                        "source_path": "demo/input/a.txt",
                        "destination_path": "demo/output/a.txt",
                    },
                    observation="Copied the matching file into the output directory.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/a.txt"],
            started_at="2026-04-26T12:02:00",
            ended_at="2026-04-26T12:03:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="directory_copy_path_alias_audit_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        report = SkillAuditor(sandbox_root / "audits").audit(generated["skill_file"], trajectory=trajectory)
        self.assertEqual("passed", report.status)
        self.assertEqual([], report.semantic_findings)

    def test_service_promote_returns_execute_follow_up(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        distill_result = sandbox_service.distill(
            sandbox_root / "trajectories" / "demo_merge_text_files.json",
            skill_name="service_promote_followup_test",
        )
        audit_result = sandbox_service.audit(
            distill_result["staging_file"],
            trajectory_path=distill_result["trajectory_path"],
        )
        self.assertEqual("promote_skill", audit_result["recommended_next_action"])

        result = sandbox_service.promote(distill_result["staging_file"])
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

    def test_service_promote_preserves_scope_policy_into_active_metadata_and_execution(self) -> None:
        sandbox_root, sandbox_service, sandbox_index = self._make_runtime_sandbox()
        staging_dir = sandbox_root / "skill_store" / "staging"
        staging_dir.mkdir(parents=True, exist_ok=True)
        skill_name = "scope_policy_promote_roundtrip_test"
        skill_path = staging_dir / f"{skill_name}.py"
        metadata_path = staging_dir / f"{skill_name}.metadata.json"
        active_path = sandbox_root / "skill_store" / "active" / f"{skill_name}.py"
        active_metadata_path = sandbox_root / "skill_store" / "active" / f"{skill_name}.metadata.json"
        promoted_output = sandbox_root / "demo" / "output" / "scope_policy_promote_roundtrip.txt"
        scope_policy = {
            "allow_shell": False,
            "allow_delete": False,
            "allowed_roots": ["demo/output"],
            "allowed_extensions": [".txt"],
            "requires_dry_run": True,
        }

        skill_path.write_text(
            "def run(tools, output_path, **kwargs):\n"
            "    tools.write_text(output_path, 'promoted-scope-policy')\n"
            "    return {'status': 'completed'}\n",
            encoding="utf-8",
        )
        self.addCleanup(lambda: skill_path.unlink(missing_ok=True))
        self._write_json_file(
            metadata_path,
            {
                "skill_name": skill_name,
                "file_path": str(skill_path.resolve()),
                "summary": "Write output under promoted scope policy.",
                "docstring": "scope policy promote roundtrip",
                "input_schema": {"output_path": "str"},
                "output_schema": {"status": "str"},
                "source_trajectory_ids": [],
                "created_at": "2026-04-27T00:00:00+00:00",
                "last_used_at": None,
                "usage_count": 0,
                "status": "staging",
                "audit_score": None,
                "tags": ["scope", "promote"],
                "scope_policy": scope_policy,
            },
        )
        self.addCleanup(lambda: active_path.unlink(missing_ok=True))
        self.addCleanup(lambda: active_metadata_path.unlink(missing_ok=True))
        self.addCleanup(lambda: promoted_output.unlink(missing_ok=True))

        audit_result = sandbox_service.audit(skill_path)
        self.assertEqual("passed", audit_result["report"]["status"])

        promote_result = sandbox_service.promote(skill_path)
        self.assertEqual("execute_skill", promote_result["recommended_next_action"])

        active_metadata = self._read_json_file(Path(promote_result["metadata_file"]))
        self.assertEqual(scope_policy, active_metadata["scope_policy"])

        promoted = sandbox_index.get(skill_name)
        self.assertIsNotNone(promoted)
        self.assertEqual(scope_policy, promoted.scope_policy)

        with self.assertRaises(RuntimeServiceError) as blocked:
            sandbox_service.execute(
                skill_name,
                {"output_path": "demo/output/scope_policy_promote_roundtrip.txt"},
            )
        self.assertEqual("SKILL_EXECUTION_FAILED", blocked.exception.code)
        self.assertIn("dry-run execution is required", blocked.exception.details["reason"])

        dry_run_result = sandbox_service.execute(
            skill_name,
            {"output_path": "demo/output/scope_policy_promote_roundtrip.txt"},
            dry_run=True,
        )
        self.assertTrue(dry_run_result["dry_run"])
        self.assertEqual("planned", dry_run_result["planned_changes"][0]["status"])
        self.assertFalse(promoted_output.exists())

    def test_mcp_promote_returns_execute_follow_up(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        distill_result = sandbox_service.distill(
            sandbox_root / "trajectories" / "demo_merge_text_files.json",
            skill_name="mcp_promote_followup_test",
        )
        sandbox_service.audit(
            distill_result["staging_file"],
            trajectory_path=distill_result["trajectory_path"],
        )

        payload = self._call_mcp_tool(
            "promote_skill",
            {"file_path": distill_result["staging_file"]},
            root=sandbox_root,
        )
        self.assertEqual("execute_skill", payload["data"]["recommended_next_action"])
        self._assert_host_operation_basics(
            payload["data"]["recommended_host_operation"],
            tool_name="execute_skill",
        )
        self._assert_execute_skill_schema(payload["data"]["recommended_host_operation"])

    def test_provider_backed_semantic_review_flags_fallback_generated_skill(self) -> None:
        sandbox_root, _, _ = self._make_runtime_sandbox()
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

        generated = SkillGenerator(sandbox_root / "skill_store" / "staging").generate(
            trajectory, skill_name="semantic_provider_fallback_test"
        )
        report = SkillAuditor(sandbox_root / "audits").audit(generated["skill_file"], trajectory=trajectory)
        self.assertEqual("mock_semantic_review_provider", report.semantic_provider)
        self.assertIsNotNone(report.semantic_artifact)
        self.assertTrue(Path(report.semantic_artifact).exists())
        self.assertTrue(
            any("fallback" in finding.lower() or "template" in finding.lower() for finding in report.semantic_findings)
        )
