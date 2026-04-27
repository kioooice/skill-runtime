from dataclasses import asdict
from pathlib import Path

from skill_runtime.api.models import Trajectory, TrajectoryStep


class RuntimeDistillCoverageTestsMixin:
    def _write_coverage_trajectory(self, root, file_name: str, trajectory: Trajectory) -> None:
        trajectory_path = root / "trajectories" / file_name
        self._write_json_file(trajectory_path, asdict(trajectory))

    def _build_merge_trajectory(self) -> Trajectory:
        return Trajectory(
            task_id="coverage_merge_demo",
            session_id="coverage_session_merge",
            task_description="Merge all txt files in a directory into one markdown file.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"input_dir": "demo/input", "pattern": "*.txt"},
                    observation="Found matching txt files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_text",
                    tool_input={"input_dir": "demo/input"},
                    observation="Read matching file contents.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_text",
                    tool_input={"output_path": "demo/output/coverage_merge.md"},
                    observation="Wrote merged markdown output.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/coverage_merge.md"],
            started_at="2026-04-27T10:00:00",
            ended_at="2026-04-27T10:01:00",
        )

    def _build_fallback_trajectory(self) -> Trajectory:
        return Trajectory(
            task_id="coverage_fallback_demo",
            session_id="coverage_session_fallback",
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
            started_at="2026-04-27T10:02:00",
            ended_at="2026-04-27T10:03:00",
        )

    def _build_second_merge_trajectory(self) -> Trajectory:
        return Trajectory(
            task_id="coverage_merge_demo_two",
            session_id="coverage_session_merge_two",
            task_description="Merge matching txt files into one markdown file.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"input_dir": "demo/input", "pattern": "*.txt"},
                    observation="Found matching txt files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_text",
                    tool_input={"input_dir": "demo/input"},
                    observation="Read matching file contents.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_text",
                    tool_input={"output_path": "demo/output/coverage_merge_two.md"},
                    observation="Wrote merged markdown output.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/coverage_merge_two.md"],
            started_at="2026-04-27T10:04:00",
            ended_at="2026-04-27T10:05:00",
        )

    def _build_second_fallback_trajectory(self) -> Trajectory:
        return Trajectory(
            task_id="coverage_fallback_demo_two",
            session_id="coverage_session_fallback_two",
            task_description="Draft another mixed report without a deterministic file rule.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="observe_state",
                    tool_input={"report_name": "weekly_report"},
                    observation="Collected mixed observations again.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="summarize_notes",
                    tool_input={"topic": "weekly_report"},
                    observation="Summarized notes into another draft.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/fallback_report_two.txt"],
            started_at="2026-04-27T10:06:00",
            ended_at="2026-04-27T10:07:00",
        )

    def _build_distill_coverage_root(self):
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        for trajectory_file in (sandbox_root / "trajectories").glob("*.json"):
            trajectory_file.unlink()

        self._write_coverage_trajectory(
            sandbox_root,
            "coverage_merge_demo.json",
            self._build_merge_trajectory(),
        )
        self._write_coverage_trajectory(
            sandbox_root,
            "coverage_fallback_demo.json",
            self._build_fallback_trajectory(),
        )
        self._write_coverage_trajectory(
            sandbox_root,
            "coverage_merge_demo_two.json",
            self._build_second_merge_trajectory(),
        )
        self._write_coverage_trajectory(
            sandbox_root,
            "coverage_fallback_demo_two.json",
            self._build_second_fallback_trajectory(),
        )
        invalid_path = sandbox_root / "trajectories" / "invalid_trajectory.json"
        invalid_path.write_text("{invalid json", encoding="utf-8")
        self.addCleanup(lambda: invalid_path.unlink(missing_ok=True))
        return sandbox_root, sandbox_service

    def _build_observed_task_candidate_root(self):
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        for trajectory_file in (sandbox_root / "trajectories").glob("*.json"):
            trajectory_file.unlink()
        for observed_task_file in (sandbox_root / "observed_tasks").glob("*.json"):
            observed_task_file.unlink()

        self._write_coverage_trajectory(
            sandbox_root,
            "coverage_merge_demo.json",
            self._build_merge_trajectory(),
        )
        self._write_coverage_trajectory(
            sandbox_root,
            "coverage_merge_demo_two.json",
            self._build_second_merge_trajectory(),
        )
        self._write_json_file(
            sandbox_root / "observed_tasks" / "candidate_move_logs.json",
            self._build_move_logs_observed_task(
                task_text="Move log files into archive candidate one.",
            ),
        )
        self._write_json_file(
            sandbox_root / "observed_tasks" / "candidate_move_logs_two.json",
            self._build_move_logs_observed_task(
                task_text="Move log files into archive candidate two.",
                input_dir="demo/second_input",
                output_dir="demo/second_output",
                artifact="demo/second_output/job2.log",
            ),
        )
        invalid_path = sandbox_root / "observed_tasks" / "invalid_observed_task.json"
        invalid_path.write_text("{invalid json", encoding="utf-8")
        self.addCleanup(lambda: invalid_path.unlink(missing_ok=True))
        return sandbox_root, sandbox_service

    def _build_execution_observed_task_root(self):
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        for trajectory_file in (sandbox_root / "trajectories").glob("*.json"):
            trajectory_file.unlink()
        for observed_task_file in (sandbox_root / "observed_tasks").glob("*.json"):
            observed_task_file.unlink()

        self._write_coverage_trajectory(
            sandbox_root,
            "coverage_merge_demo.json",
            self._build_merge_trajectory(),
        )
        self._write_json_file(
            sandbox_root / "observed_tasks" / "execute_directory_move.json",
            {
                "task": "Move all log files from inbox to archive.",
                "skill_name": "directory_move",
                "skill_summary": "Move matching log files from one directory into another directory.",
                "skill_args": {
                    "input_dir": "demo/move_input",
                    "output_dir": "demo/move_output",
                    "pattern": "*.log",
                },
                "actions": [
                    {
                        "tool_name": "list_files",
                        "tool_input": {"input_dir": "demo/move_input", "pattern": "*.log"},
                        "observation": "Found matching log files.",
                        "status": "success",
                    },
                    {
                        "tool_name": "move_file",
                        "tool_input": {"input_dir": "demo/move_input", "output_dir": "demo/move_output"},
                        "observation": "Moved matching log files.",
                        "status": "success",
                    },
                ],
                "result": {"status": "completed", "outputs": ["demo/move_output/job1.log"]},
            },
        )
        return sandbox_root, sandbox_service

    def _build_multi_execution_observed_task_root(self):
        sandbox_root, sandbox_service = self._build_execution_observed_task_root()
        self._write_json_file(
            sandbox_root / "observed_tasks" / "execute_directory_copy.json",
            {
                "task": "Copy all txt files from inbox to archive.",
                "skill_name": "directory_copy",
                "skill_summary": "Copy matching txt files from one directory into another directory.",
                "skill_args": {
                    "input_dir": "demo/copy_input",
                    "output_dir": "demo/copy_output",
                    "pattern": "*.txt",
                },
                "actions": [
                    {
                        "tool_name": "list_files",
                        "tool_input": {"input_dir": "demo/copy_input", "pattern": "*.txt"},
                        "observation": "Found matching txt files.",
                        "status": "success",
                    },
                    {
                        "tool_name": "copy_file",
                        "tool_input": {"input_dir": "demo/copy_input", "output_dir": "demo/copy_output"},
                        "observation": "Copied matching txt files.",
                        "status": "success",
                    },
                ],
                "result": {"status": "completed", "outputs": ["demo/copy_output/job1.txt"]},
            },
        )
        self._write_json_file(
            sandbox_root / "observed_tasks" / "execute_directory_copy_two.json",
            {
                "task": "Copy all txt files from second inbox to second archive.",
                "skill_name": "directory_copy",
                "skill_summary": "Copy matching txt files from one directory into another directory.",
                "skill_args": {
                    "input_dir": "demo/copy_input_two",
                    "output_dir": "demo/copy_output_two",
                    "pattern": "*.txt",
                },
                "actions": [
                    {
                        "tool_name": "list_files",
                        "tool_input": {"input_dir": "demo/copy_input_two", "pattern": "*.txt"},
                        "observation": "Found matching txt files.",
                        "status": "success",
                    },
                    {
                        "tool_name": "copy_file",
                        "tool_input": {"input_dir": "demo/copy_input_two", "output_dir": "demo/copy_output_two"},
                        "observation": "Copied matching txt files.",
                        "status": "success",
                    },
                ],
                "result": {"status": "completed", "outputs": ["demo/copy_output_two/job2.txt"]},
            },
        )
        self._write_json_file(
            sandbox_root / "observed_tasks" / "execute_directory_move_two.json",
            {
                "task": "Move all log files from second inbox to second archive.",
                "skill_name": "directory_move",
                "skill_summary": "Move matching log files from one directory into another directory.",
                "skill_args": {
                    "input_dir": "demo/move_input_two",
                    "output_dir": "demo/move_output_two",
                    "pattern": "*.log",
                },
                "actions": [
                    {
                        "tool_name": "list_files",
                        "tool_input": {"input_dir": "demo/move_input_two", "pattern": "*.log"},
                        "observation": "Found matching log files.",
                        "status": "success",
                    },
                    {
                        "tool_name": "move_file",
                        "tool_input": {"input_dir": "demo/move_input_two", "output_dir": "demo/move_output_two"},
                        "observation": "Moved matching log files.",
                        "status": "success",
                    },
                ],
                "result": {"status": "completed", "outputs": ["demo/move_output_two/job2.log"]},
            },
        )
        self._write_json_file(
            sandbox_root / "observed_tasks" / "execute_text_replace.json",
            {
                "task": "Replace one string with another in a text file and write a new output file.",
                "skill_name": "text_replace",
                "skill_summary": "Replace one string with another in a text file and write a new output file.",
                "skill_args": {
                    "input_path": "demo/input.txt",
                    "output_path": "demo/output.txt",
                    "old_text": "old",
                    "new_text": "new",
                },
                "actions": [
                    {
                        "tool_name": "read_text",
                        "tool_input": {"input_path": "demo/input.txt"},
                        "observation": "Read source text.",
                        "status": "success",
                    },
                    {
                        "tool_name": "write_text",
                        "tool_input": {"output_path": "demo/output.txt"},
                        "observation": "Wrote replaced text.",
                        "status": "success",
                    },
                ],
                "result": {"status": "completed", "outputs": ["demo/output.txt"]},
            },
        )
        return sandbox_root, sandbox_service

    def test_service_distill_coverage_report_summarizes_rules_and_fallback_hotspots(self) -> None:
        sandbox_root, sandbox_service = self._build_distill_coverage_root()

        payload = sandbox_service.distill_coverage_report()

        self.assertEqual(4, payload["trajectory_count"])
        self.assertEqual(2, payload["matched_count"])
        self.assertEqual(2, payload["fallback_count"])
        self.assertEqual(1, payload["invalid_count"])
        self.assertEqual(0.5, payload["coverage_ratio"])
        self.assertEqual(2, payload["trajectory_family_count"])
        self.assertEqual(1, payload["matched_family_count"])
        self.assertEqual(1, payload["fallback_family_count"])
        self.assertEqual(0.5, payload["family_coverage_ratio"])
        self.assertEqual(
            [
                {"rule_name": "llm_fallback", "count": 2},
                {"rule_name": "text_merge", "count": 2},
            ],
            payload["rule_counts"],
        )
        self.assertEqual(1, len(payload["matched_families"]))
        matched_family = payload["matched_families"][0]
        self.assertEqual("text_merge", matched_family["rule_name"])
        self.assertEqual(2, matched_family["count"])
        self.assertEqual(["list_files", "read_text", "write_text"], matched_family["tool_sequence"])
        self.assertEqual(["input_dir", "output_path", "pattern"], matched_family["input_keys"])
        self.assertEqual(
            ["coverage_merge_demo", "coverage_merge_demo_two"],
            matched_family["example_task_ids"],
        )
        self.assertEqual(1, len(payload["fallback_hotspots"]))
        hotspot = payload["fallback_hotspots"][0]
        self.assertEqual(2, hotspot["count"])
        self.assertEqual(["observe_state", "summarize_notes"], hotspot["tool_sequence"])
        self.assertEqual(["report_name", "topic"], hotspot["input_keys"])
        self.assertEqual(
            ["coverage_fallback_demo", "coverage_fallback_demo_two"],
            hotspot["example_task_ids"],
        )
        self.assertEqual(
            [
                "Generate a report from mixed observations without a known deterministic file rule.",
                "Draft another mixed report without a deterministic file rule.",
            ],
            hotspot["example_task_descriptions"],
        )
        self.assertEqual(
            [
                str((sandbox_root / "trajectories" / "coverage_fallback_demo.json").resolve()),
                str((sandbox_root / "trajectories" / "coverage_fallback_demo_two.json").resolve()),
            ],
            hotspot["example_trajectory_paths"],
        )
        self.assertEqual("distill_trajectory", payload["recommended_next_action"])
        self._assert_host_operation_basics(
            payload["recommended_host_operation"],
            tool_name="distill_trajectory",
        )
        self.assertEqual(
            str((sandbox_root / "trajectories" / "coverage_fallback_demo.json").resolve()),
            payload["recommended_host_operation"]["arguments"]["trajectory_path"],
        )
        self._assert_operation_role(payload["available_host_operations"][0], "primary")
        self.assertEqual("distill_trajectory", payload["available_host_operations"][1]["tool_name"])
        self.assertEqual("distill_coverage_report", payload["available_host_operations"][-1]["tool_name"])
        self.assertEqual(
            [str((sandbox_root / "trajectories" / "invalid_trajectory.json").resolve())],
            payload["invalid_trajectory_paths"],
        )
        self.assertEqual(1.0, payload["concentration_summary"]["matched_families"]["top_share"])
        self.assertEqual("text_merge", payload["concentration_summary"]["matched_families"]["top_rule_name"])
        self.assertEqual(1.0, payload["concentration_summary"]["fallback_hotspots"]["top_share"])
        self.assertEqual(
            ["observe_state", "summarize_notes"],
            payload["concentration_summary"]["fallback_hotspots"]["top_tool_sequence"],
        )

    def test_service_distill_coverage_report_without_hotspots_returns_no_follow_up(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        for trajectory_file in (sandbox_root / "trajectories").glob("*.json"):
            trajectory_file.unlink()

        self._write_coverage_trajectory(
            sandbox_root,
            "coverage_merge_demo.json",
            self._build_merge_trajectory(),
        )
        self._write_coverage_trajectory(
            sandbox_root,
            "coverage_merge_demo_two.json",
            self._build_second_merge_trajectory(),
        )

        payload = sandbox_service.distill_coverage_report()

        self.assertEqual(2, payload["trajectory_count"])
        self.assertEqual(2, payload["matched_count"])
        self.assertEqual(0, payload["fallback_count"])
        self.assertEqual(1.0, payload["coverage_ratio"])
        self.assertEqual(1, payload["trajectory_family_count"])
        self.assertEqual(1, payload["matched_family_count"])
        self.assertEqual(0, payload["fallback_family_count"])
        self.assertEqual(1.0, payload["family_coverage_ratio"])
        self.assertEqual(None, payload["recommended_next_action"])
        self.assertEqual(None, payload["recommended_host_operation"])
        self.assertEqual([], payload["available_host_operations"])

    def test_service_distill_coverage_report_recommends_observed_task_candidates_when_no_fallbacks(self) -> None:
        sandbox_root, sandbox_service = self._build_observed_task_candidate_root()

        payload = sandbox_service.distill_coverage_report()

        self.assertEqual(2, payload["trajectory_count"])
        self.assertEqual(2, payload["matched_count"])
        self.assertEqual(0, payload["fallback_count"])
        self.assertEqual(2, payload["observed_task_candidate_count"])
        self.assertEqual(1, payload["observed_task_candidate_family_count"])
        self.assertEqual(1, payload["invalid_observed_task_count"])
        self.assertEqual(
            [str((sandbox_root / "observed_tasks" / "invalid_observed_task.json").resolve())],
            payload["invalid_observed_task_paths"],
        )
        self.assertEqual(1, len(payload["observed_task_candidates"]))
        candidate = payload["observed_task_candidates"][0]
        self.assertEqual(2, candidate["count"])
        self.assertEqual(["list_files", "move_file"], candidate["tool_sequence"])
        self.assertEqual(["input_dir", "output_dir", "pattern"], candidate["input_keys"])
        self.assertEqual(
            ["candidate_move_logs.json", "candidate_move_logs_two.json"],
            [Path(path).name for path in candidate["example_observed_task_paths"]],
        )
        self.assertEqual("distill_and_promote_candidate", payload["recommended_next_action"])
        self._assert_observed_task_follow_up(
            payload["recommended_host_operation"],
            observed_task_path=str((sandbox_root / "observed_tasks" / "candidate_move_logs.json").resolve()),
            display_label="Promote top observed-task candidate",
            risk_level="low",
        )
        self.assertEqual(
            "distill_and_promote_candidate",
            payload["available_host_operations"][1]["tool_name"],
        )
        self.assertEqual(
            "distill_coverage_report",
            payload["available_host_operations"][-1]["tool_name"],
        )

    def test_service_distill_coverage_report_separates_execution_observed_tasks_from_backlog(self) -> None:
        sandbox_root, sandbox_service = self._build_execution_observed_task_root()

        payload = sandbox_service.distill_coverage_report()

        self.assertEqual(1, payload["trajectory_count"])
        self.assertEqual(1, payload["matched_count"])
        self.assertEqual(0, payload["fallback_count"])
        self.assertEqual(0, payload["observed_task_candidate_count"])
        self.assertEqual(0, payload["observed_task_candidate_family_count"])
        self.assertEqual(1, payload["execution_observed_task_count"])
        self.assertEqual(1, payload["execution_observed_task_family_count"])
        self.assertEqual(1, len(payload["execution_observed_task_families"]))
        execution_family = payload["execution_observed_task_families"][0]
        self.assertEqual(1, execution_family["count"])
        self.assertEqual(["list_files", "move_file"], execution_family["tool_sequence"])
        self.assertEqual(["input_dir", "output_dir", "pattern"], execution_family["input_keys"])
        self.assertEqual(
            ["execute_directory_move.json"],
            [Path(path).name for path in execution_family["example_observed_task_paths"]],
        )
        self.assertEqual(1.0, payload["concentration_summary"]["execution_observed_task_families"]["top_share"])
        self.assertEqual(
            ["list_files", "move_file"],
            payload["concentration_summary"]["execution_observed_task_families"]["top_tool_sequence"],
        )
        self.assertEqual("distill_coverage_report", payload["recommended_next_action"])
        self.assertEqual("Focus execution view", payload["recommended_host_operation"]["display_label"])
        self.assertEqual(
            {"observed_task_scope": "execution", "min_family_count": 1},
            payload["recommended_host_operation"]["arguments"],
        )
        self.assertEqual("primary", payload["available_host_operations"][0]["operation_role"])

    def test_service_distill_coverage_report_backlog_scope_hides_execution_observed_tasks(self) -> None:
        _, sandbox_service = self._build_execution_observed_task_root()

        payload = sandbox_service.distill_coverage_report(observed_task_scope="backlog")

        self.assertEqual("backlog", payload["observed_task_scope"])
        self.assertEqual(0, payload["observed_task_candidate_count"])
        self.assertEqual(0, payload["execution_observed_task_count"])
        self.assertEqual([], payload["observed_task_candidates"])
        self.assertEqual([], payload["execution_observed_task_families"])
        self.assertEqual(None, payload["recommended_next_action"])

    def test_service_distill_coverage_report_recommends_execution_view_when_only_execution_signal_remains(self) -> None:
        _, sandbox_service = self._build_multi_execution_observed_task_root()

        payload = sandbox_service.distill_coverage_report(max_family_items=2, min_family_count=2)

        self.assertEqual("distill_coverage_report", payload["recommended_next_action"])
        self.assertEqual("Focus execution view", payload["recommended_host_operation"]["display_label"])
        self.assertEqual(
            {"observed_task_scope": "execution", "max_family_items": 2, "min_family_count": 2},
            payload["recommended_host_operation"]["arguments"],
        )
        self.assertEqual(
            "No fallback hotspots or backlog candidates remain. Inspect the execution-only view next to review dogfood and test-heavy execution traffic.",
            payload["recommended_reason"],
        )
        self.assertTrue(
            any(
                item["display_label"] == "Show lower-frequency families"
                for item in payload["available_host_operations"]
            )
        )

    def test_service_distill_coverage_report_execution_scope_hides_backlog_candidates(self) -> None:
        sandbox_root, sandbox_service = self._build_observed_task_candidate_root()

        payload = sandbox_service.distill_coverage_report(observed_task_scope="execution")

        self.assertEqual("execution", payload["observed_task_scope"])
        self.assertEqual(0, payload["observed_task_candidate_count"])
        self.assertEqual(0, payload["observed_task_candidate_family_count"])
        self.assertEqual([], payload["observed_task_candidates"])
        self.assertEqual(0, payload["execution_observed_task_count"])
        self.assertEqual([], payload["execution_observed_task_families"])
        self.assertEqual(None, payload["recommended_next_action"])
        self.assertEqual(None, payload["recommended_host_operation"])
        self.assertEqual([], payload["available_host_operations"])

    def test_mcp_distill_coverage_report_execution_scope_matches_service_payload(self) -> None:
        sandbox_root, sandbox_service = self._build_execution_observed_task_root()

        service_payload = sandbox_service.distill_coverage_report(observed_task_scope="execution")
        payload = self._call_mcp_tool(
            "distill_coverage_report",
            {"observed_task_scope": "execution"},
            root=sandbox_root,
        )

        self.assertEqual(service_payload, payload["data"])

    def test_cli_distill_coverage_report_backlog_scope_returns_wrapped_payload(self) -> None:
        sandbox_root, sandbox_service = self._build_observed_task_candidate_root()

        service_payload = sandbox_service.distill_coverage_report(observed_task_scope="backlog")
        payload = self._run_cli(
            "distill-coverage-report",
            "--observed-task-scope",
            "backlog",
            root=sandbox_root,
            expect_json=True,
        )

        self.assertEqual("ok", payload["status"])
        self.assertEqual(service_payload, payload["data"])

    def test_service_distill_coverage_report_limits_family_lists(self) -> None:
        sandbox_root, sandbox_service = self._build_distill_coverage_root()

        payload = sandbox_service.distill_coverage_report(max_family_items=1)

        self.assertEqual(1, payload["max_family_items"])
        self.assertEqual(1, len(payload["rule_counts"]))
        self.assertEqual(1, len(payload["matched_families"]))
        self.assertEqual(1, len(payload["fallback_hotspots"]))
        self.assertEqual("distill_trajectory", payload["recommended_next_action"])
        self.assertEqual(
            str((sandbox_root / "trajectories" / "coverage_fallback_demo.json").resolve()),
            payload["recommended_host_operation"]["arguments"]["trajectory_path"],
        )
        self.assertEqual("distill_coverage_report", payload["available_host_operations"][-1]["tool_name"])
        self.assertEqual(
            1,
            payload["available_host_operations"][-1]["arguments"]["max_family_items"],
        )
        self.assertEqual(
            {
                "raw_family_count": 2,
                "filtered_family_count": 2,
                "visible_family_count": 1,
                "hidden_family_count": 1,
                "raw_item_count": 4,
                "filtered_item_count": 4,
                "visible_item_count": 2,
                "hidden_item_count": 2,
            },
            payload["visibility_summary"]["rule_counts"],
        )
        self.assertEqual("distill_coverage_report", payload["view_host_operations"][0]["tool_name"])
        self.assertEqual(
            {"observed_task_scope": "all", "min_family_count": 1},
            payload["view_host_operations"][0]["arguments"],
        )

    def test_mcp_distill_coverage_report_max_family_items_matches_service_payload(self) -> None:
        sandbox_root, sandbox_service = self._build_distill_coverage_root()

        service_payload = sandbox_service.distill_coverage_report(max_family_items=1)
        payload = self._call_mcp_tool(
            "distill_coverage_report",
            {"max_family_items": 1},
            root=sandbox_root,
        )

        self.assertEqual(service_payload, payload["data"])

    def test_cli_distill_coverage_report_max_family_items_returns_wrapped_payload(self) -> None:
        sandbox_root, sandbox_service = self._build_distill_coverage_root()

        service_payload = sandbox_service.distill_coverage_report(max_family_items=1)
        payload = self._run_cli(
            "distill-coverage-report",
            "--max-family-items",
            "1",
            root=sandbox_root,
            expect_json=True,
        )

        self.assertEqual("ok", payload["status"])
        self.assertEqual(service_payload, payload["data"])

    def test_service_distill_coverage_report_min_family_count_filters_execution_families(self) -> None:
        _, sandbox_service = self._build_execution_observed_task_root()

        payload = sandbox_service.distill_coverage_report(
            observed_task_scope="execution",
            min_family_count=2,
        )

        self.assertEqual("execution", payload["observed_task_scope"])
        self.assertEqual(2, payload["min_family_count"])
        self.assertEqual(0, payload["execution_observed_task_count"])
        self.assertEqual(0, payload["execution_observed_task_family_count"])
        self.assertEqual([], payload["execution_observed_task_families"])
        self.assertEqual(0.0, payload["concentration_summary"]["execution_observed_task_families"]["top_share"])
        self.assertEqual(None, payload["recommended_next_action"])

    def test_service_distill_coverage_report_min_family_count_filters_fallback_hotspots(self) -> None:
        sandbox_root, sandbox_service = self._build_distill_coverage_root()

        payload = sandbox_service.distill_coverage_report(min_family_count=3)

        self.assertEqual(3, payload["min_family_count"])
        self.assertEqual([], payload["fallback_hotspots"])
        self.assertEqual(0, payload["fallback_family_count"])
        self.assertEqual(None, payload["recommended_next_action"])
        self.assertEqual(None, payload["recommended_host_operation"])
        self.assertEqual([], payload["available_host_operations"])
        self.assertEqual(
            {
                "raw_family_count": 1,
                "filtered_family_count": 0,
                "visible_family_count": 0,
                "hidden_family_count": 0,
                "raw_item_count": 2,
                "filtered_item_count": 0,
                "visible_item_count": 0,
                "hidden_item_count": 0,
            },
            payload["visibility_summary"]["fallback_hotspots"],
        )
        self.assertEqual("Show lower-frequency families", payload["view_host_operations"][0]["display_label"])
        self.assertEqual(
            {"observed_task_scope": "all", "min_family_count": 1},
            payload["view_host_operations"][0]["arguments"],
        )

    def test_service_distill_coverage_report_execution_scope_exposes_navigation_views(self) -> None:
        _, sandbox_service = self._build_multi_execution_observed_task_root()

        payload = sandbox_service.distill_coverage_report(
            observed_task_scope="execution",
            max_family_items=1,
            min_family_count=2,
        )

        self.assertEqual(
            ["Show all coverage", "Show hidden families", "Show lower-frequency families"],
            [item["display_label"] for item in payload["view_host_operations"]],
        )
        self.assertEqual(
            {"observed_task_scope": "all", "max_family_items": 1, "min_family_count": 2},
            payload["view_host_operations"][0]["arguments"],
        )
        self.assertEqual(
            {"observed_task_scope": "execution", "min_family_count": 2},
            payload["view_host_operations"][1]["arguments"],
        )
        self.assertEqual(
            {"observed_task_scope": "execution", "max_family_items": 1, "min_family_count": 1},
            payload["view_host_operations"][2]["arguments"],
        )

    def test_mcp_distill_coverage_report_min_family_count_matches_service_payload(self) -> None:
        sandbox_root, sandbox_service = self._build_execution_observed_task_root()

        service_payload = sandbox_service.distill_coverage_report(
            observed_task_scope="execution",
            min_family_count=2,
        )
        payload = self._call_mcp_tool(
            "distill_coverage_report",
            {"observed_task_scope": "execution", "min_family_count": 2},
            root=sandbox_root,
        )

        self.assertEqual(service_payload, payload["data"])

    def test_cli_distill_coverage_report_min_family_count_returns_wrapped_payload(self) -> None:
        sandbox_root, sandbox_service = self._build_execution_observed_task_root()

        service_payload = sandbox_service.distill_coverage_report(
            observed_task_scope="execution",
            min_family_count=2,
        )
        payload = self._run_cli(
            "distill-coverage-report",
            "--observed-task-scope",
            "execution",
            "--min-family-count",
            "2",
            root=sandbox_root,
            expect_json=True,
        )

        self.assertEqual("ok", payload["status"])
        self.assertEqual(service_payload, payload["data"])

    def test_mcp_distill_coverage_report_matches_service_payload(self) -> None:
        sandbox_root, sandbox_service = self._build_distill_coverage_root()

        service_payload = sandbox_service.distill_coverage_report()
        payload = self._call_mcp_tool("distill_coverage_report", {}, root=sandbox_root)

        self.assertEqual(service_payload, payload["data"])

    def test_cli_distill_coverage_report_returns_wrapped_payload(self) -> None:
        sandbox_root, sandbox_service = self._build_distill_coverage_root()

        service_payload = sandbox_service.distill_coverage_report()
        payload = self._run_cli(
            "distill-coverage-report",
            root=sandbox_root,
            expect_json=True,
        )

        self.assertEqual("ok", payload["status"])
        self.assertEqual(service_payload, payload["data"])
