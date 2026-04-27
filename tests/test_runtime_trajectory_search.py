import json
from pathlib import Path

from skill_runtime.memory.trajectory_capture import TrajectoryCapture
from skill_runtime.memory.trajectory_store import TrajectoryStore, TrajectoryValidationError
from scripts.skill_mcp_server import resolve_runtime_root
from tests.runtime_test_support import ROOT


class RuntimeTrajectorySearchTestsMixin:
    def test_trajectory_loads(self) -> None:
        store = TrajectoryStore(ROOT / "trajectories")
        trajectory = store.load("demo_merge_text_files")
        self.assertEqual("demo_merge_text_files", trajectory.task_id)
        self.assertEqual("success", trajectory.final_status)

    def test_invalid_trajectory_rejected(self) -> None:
        store = TrajectoryStore(ROOT / "trajectories")
        invalid_path = ROOT / "trajectories" / "invalid.json"
        invalid_path.write_text(json.dumps({"task_id": "bad"}), encoding="utf-8")
        self.addCleanup(invalid_path.unlink)
        with self.assertRaises(TrajectoryValidationError):
            store.load_file(invalid_path)

    def test_capture_trajectory_from_observed_task_record(self) -> None:
        observed_path = self._write_demo_json(
            "observed_capture.json",
            self._build_move_logs_observed_task(
                variant="steps",
                input_dir="demo/inbox",
                output_dir="demo/archive",
                list_observation="Found 2 log files.",
                move_observation="Moved the matching files.",
                artifact="demo/archive/job1.log",
            ),
        )

        trajectory, saved_path = TrajectoryCapture(ROOT / "trajectories").capture(
            observed_path,
            task_id="capture_test_task",
            session_id="capture_test_session",
        )
        self.addCleanup(saved_path.unlink)

        self.assertEqual("capture_test_task", trajectory.task_id)
        self.assertEqual("capture_test_session", trajectory.session_id)
        self.assertEqual("success", trajectory.final_status)
        self.assertEqual("1", trajectory.steps[0].step_id)
        self.assertTrue(saved_path.exists())

    def test_capture_trajectory_accepts_compact_observed_record_aliases(self) -> None:
        observed_path = self._write_demo_json(
            "observed_capture_compact.json",
            {
                **self._build_move_logs_observed_task(
                    variant="compact",
                    input_dir="demo/inbox",
                    output_dir="demo/archive",
                    list_observation="Found 2 log files.",
                    move_observation="Moved the matching files.",
                    artifact="demo/archive/job1.log",
                ),
                "actions": [
                    {
                        "tool": "list_files",
                        "input": {"input_dir": "demo/inbox", "pattern": "*.log"},
                        "result": "Found 2 log files.",
                    },
                    {
                        "action": "move_file",
                        "args": {"input_dir": "demo/inbox", "output_dir": "demo/archive"},
                        "output": "Moved the matching files.",
                        "state": "success",
                    },
                ],
            },
        )

        trajectory, saved_path = TrajectoryCapture(ROOT / "trajectories").capture(
            observed_path,
            task_id="capture_compact_test_task",
            session_id="capture_compact_session",
        )
        self.addCleanup(saved_path.unlink)

        self.assertEqual("capture_compact_test_task", trajectory.task_id)
        self.assertEqual("capture_compact_session", trajectory.session_id)
        self.assertEqual("list_files", trajectory.steps[0].tool_name)
        self.assertEqual("move_file", trajectory.steps[1].tool_name)
        self.assertEqual("Moved the matching files.", trajectory.steps[1].observation)
        self.assertEqual(["demo/archive/job1.log"], trajectory.artifacts)

    def test_capture_trajectory_accepts_nested_tool_call_logs(self) -> None:
        observed_path = self._write_demo_json(
            "observed_capture_nested.json",
            {
                **self._build_move_logs_observed_task(
                    variant="nested",
                    input_dir="demo/inbox",
                    output_dir="demo/archive",
                    list_observation="Found 2 log files.",
                    move_observation="Moved the matching files.",
                    artifact="demo/archive/job1.log",
                ),
                "records": [
                    {
                        "tool": {
                            "name": "list_files",
                            "arguments": {"input_dir": "demo/inbox", "pattern": "*.log"},
                        },
                        "result": {"message": "Found 2 log files.", "status": "success"},
                    },
                    {
                        "call": {
                            "name": "move_file",
                            "arguments": {"input_dir": "demo/inbox", "output_dir": "demo/archive"},
                        },
                        "result": {
                            "output": "Moved the matching files.",
                            "success": True,
                            "outputs": ["demo/archive/job1.log"],
                        },
                    },
                ],
            },
        )

        trajectory, saved_path = TrajectoryCapture(ROOT / "trajectories").capture(
            observed_path,
            task_id="capture_nested_test_task",
            session_id="capture_nested_session",
        )
        self.addCleanup(saved_path.unlink)

        self.assertEqual("capture_nested_test_task", trajectory.task_id)
        self.assertEqual("list_files", trajectory.steps[0].tool_name)
        self.assertEqual({"input_dir": "demo/inbox", "pattern": "*.log"}, trajectory.steps[0].tool_input)
        self.assertEqual("move_file", trajectory.steps[1].tool_name)
        self.assertEqual("Moved the matching files.", trajectory.steps[1].observation)
        self.assertEqual(["demo/archive/job1.log"], trajectory.artifacts)

    def test_capture_trajectory_merges_execute_skill_args_into_step_inputs(self) -> None:
        observed_path = self._write_demo_json(
            "observed_capture_skill_args.json",
            {
                "task": "Replace one string with another across all txt files in a directory and write outputs to another directory.",
                "skill_name": "directory_text_replace_rule_test",
                "skill_args": {
                    "input_dir": "demo/replace_input",
                    "output_dir": "demo/replace_output",
                    "pattern": "*.txt",
                    "old_text": "hello",
                    "new_text": "hi",
                },
                "actions": [
                    {
                        "tool": "list_files",
                        "input": {"path": "demo/replace_input", "pattern": "*.txt"},
                        "result": "Found matching txt files.",
                    },
                    {
                        "tool": "read_text",
                        "input": {"path": "demo/replace_input/a.txt"},
                        "result": "Read one text file.",
                    },
                    {
                        "tool": "write_text",
                        "input": {"path": "demo/replace_output/a.txt"},
                        "result": "Wrote one replaced text file.",
                    },
                ],
                "result": {"status": "completed", "outputs": ["demo/replace_output/a.txt"]},
            },
        )

        trajectory, saved_path = TrajectoryCapture(ROOT / "trajectories").capture(
            observed_path,
            task_id="capture_skill_args_test_task",
            session_id="capture_skill_args_session",
        )
        self.addCleanup(saved_path.unlink)

        self.assertEqual("capture_skill_args_test_task", trajectory.task_id)
        self.assertEqual("demo/replace_input", trajectory.steps[0].tool_input["input_dir"])
        self.assertEqual("demo/replace_output", trajectory.steps[2].tool_input["output_dir"])
        self.assertEqual("hello", trajectory.steps[1].tool_input["old_text"])
        self.assertEqual("hi", trajectory.steps[1].tool_input["new_text"])

    def test_capture_trajectory_accepts_inline_observed_payload(self) -> None:
        observed_payload = self._build_move_logs_observed_task(
            variant="compact",
            input_dir="demo/inbox",
            output_dir="demo/archive",
            list_observation="Found 2 log files.",
            move_observation="Moved the matching files.",
            artifact="demo/archive/job1.log",
        )

        trajectory, saved_path = TrajectoryCapture(ROOT / "trajectories").capture_payload(
            observed_payload,
            task_id="capture_inline_test_task",
            session_id="capture_inline_session",
        )
        self.addCleanup(saved_path.unlink)

        self.assertEqual("capture_inline_test_task", trajectory.task_id)
        self.assertEqual("capture_inline_session", trajectory.session_id)
        self.assertEqual("list_files", trajectory.steps[0].tool_name)
        self.assertEqual("move_file", trajectory.steps[1].tool_name)
        self.assertEqual(["demo/archive/job1.log"], trajectory.artifacts)

    def test_service_capture_trajectory_returns_saved_file(self) -> None:
        observed_path = self._write_demo_json(
            "observed_service_capture.json",
            {
                "task_description": "Rename matching files with a prefix.",
                "steps": [
                    {
                        "tool_name": "list_files",
                        "tool_input": {"input_dir": "demo/input", "pattern": "*.txt"},
                        "observation": "Collected rename candidates.",
                    },
                    {
                        "tool_name": "rename_path",
                        "tool_input": {"input_dir": "demo/input", "prefix": "done_"},
                        "observation": "Renamed matching files.",
                    },
                ],
                "final_status": "success",
            },
        )

        result = self.service.capture_trajectory(
            observed_path,
            task_id="service_capture_test",
            session_id="service_capture_session",
        )
        saved_path = Path(result["trajectory_path"])
        self.addCleanup(saved_path.unlink)

        self.assertTrue(result["captured"])
        self.assertEqual("service_capture_test", result["task_id"])
        self.assertTrue(saved_path.exists())
        self.assertEqual("distill_trajectory", result["recommended_next_action"])
        self._assert_host_operation_basics(
            result["recommended_host_operation"],
            tool_name="distill_trajectory",
        )
        self.assertEqual(result["trajectory_path"], result["recommended_host_operation"]["arguments"]["trajectory_path"])
        self._assert_operation_role(result["available_host_operations"][0], "primary")

    def test_service_capture_trajectory_accepts_inline_observed_payload(self) -> None:
        result = self.service.capture_trajectory(
            observed_task=self._build_move_logs_observed_task(
                variant="steps",
                input_dir="demo/inbox",
                output_dir="demo/archive",
                list_observation="Found 2 log files.",
                move_observation="Moved the matching files.",
                artifact="demo/archive/job1.log",
            ),
            task_id="service_capture_inline_test",
            session_id="service_capture_inline_session",
        )
        saved_path = Path(result["trajectory_path"])
        self.addCleanup(saved_path.unlink)

        self.assertTrue(result["captured"])
        self.assertEqual("service_capture_inline_test", result["task_id"])
        self.assertTrue(saved_path.exists())
        self.assertEqual("distill_trajectory", result["recommended_next_action"])
        self._assert_host_operation_basics(
            result["recommended_host_operation"],
            tool_name="distill_trajectory",
        )

    def test_service_log_trajectory_returns_distill_follow_up(self) -> None:
        result = self.service.log_trajectory(ROOT / "trajectories" / "demo_merge_text_files.json")
        self.assertTrue(result["registered"])
        self.assertEqual("distill_trajectory", result["recommended_next_action"])
        self._assert_host_operation_basics(
            result["recommended_host_operation"],
            tool_name="distill_trajectory",
        )
        self.assertEqual(
            result["trajectory_path"],
            result["recommended_host_operation"]["arguments"]["trajectory_path"],
        )

    def test_search_returns_active_skill(self) -> None:
        results = self.index.search("merge txt files into markdown", top_k=20)
        self.assertTrue(results)
        names = {result["skill_name"] for result in results}
        self.assertIn("merge_text_files", names)
        first = results[0]
        self.assertEqual("merge_text_files", first["skill_name"])
        self.assertEqual("execute_skill", first["recommended_next_action"])
        self.assertIn("rule_name", first)
        self.assertIn("rule_reason", first)
        self.assertEqual("stable", first["library_tier"])
        self.assertIn("score_breakdown", first)
        self.assertGreater(first["score_breakdown"]["usage"], 0)
        self._assert_host_operation_basics(
            first["host_operation"],
            tool_name="execute_skill",
            source_ref="skill:merge_text_files",
            display_label="Run skill",
            risk_level="low",
            requires_confirmation=False,
        )
        self.assertEqual("merge_text_files", first["host_operation"]["arguments"]["skill_name"])
        self.assertEqual({}, first["host_operation"]["arguments"]["args"])
        args_properties = self._assert_execute_skill_schema(first["host_operation"])
        self.assertTrue(args_properties["input_dir"]["required"])
        self.assertFalse(args_properties["input_dir"]["prefilled"])

    def test_service_search_matches_cli_shape(self) -> None:
        payload = self.service.search("merge txt files into markdown", top_k=3)
        self.assertEqual("merge txt files into markdown", payload["query"])
        self.assertTrue(payload["results"])
        self.assertEqual("execute_skill", payload["recommended_next_action"])
        self.assertEqual("merge_text_files", payload["recommended_skill_name"])
        self.assertIn("why_matched", payload["results"][0])
        self.assertIn("score_breakdown", payload["results"][0])
        self._assert_host_operation_basics(
            payload["recommended_host_operation"],
            tool_name="execute_skill",
            source_ref="search:recommended_skill:merge_text_files",
            display_label="Run recommended skill",
            requires_confirmation=False,
        )
        self.assertEqual("merge_text_files", payload["recommended_host_operation"]["arguments"]["skill_name"])
        self._assert_execute_skill_schema(payload["recommended_host_operation"])
        self.assertTrue(payload["available_host_operations"])
        self.assertEqual("execute_skill", payload["available_host_operations"][0]["tool_name"])
        self._assert_operation_role(payload["available_host_operations"][0], "primary")
        self.assertGreaterEqual(len(payload["available_host_operations"]), 2)
        self._assert_operation_role(payload["available_host_operations"][1], "default")
        self.assertIn(
            payload["available_host_operations"][1]["operation_id"],
            {item["host_operation"]["operation_id"] for item in payload["results"][1:]},
        )

    def test_mcp_search_tool_returns_structured_payload(self) -> None:
        payload = self._call_mcp_tool(
            "search_skill",
            {"query": "merge txt files into markdown", "top_k": 3},
        )
        self.assertTrue(payload["data"]["results"])
        self.assertEqual("execute_skill", payload["data"]["recommended_next_action"])
        self.assertEqual("merge_text_files", payload["data"]["recommended_skill_name"])
        self.assertIn("rule_name", payload["data"]["results"][0])
        self.assertIn("score_breakdown", payload["data"]["results"][0])
        self._assert_host_operation_basics(
            payload["data"]["recommended_host_operation"],
            tool_name="execute_skill",
        )
        self.assertEqual("execute_skill", payload["data"]["results"][0]["host_operation"]["tool_name"])

    def test_search_deprioritizes_experimental_skill_names(self) -> None:
        results = self.index.search("merge txt files into markdown", top_k=10)
        experimental = next(result for result in results if result["skill_name"] == "merge_text_files_generated")
        stable = next(result for result in results if result["skill_name"] == "merge_text_files")
        self.assertEqual("experimental", experimental["library_tier"])
        self.assertEqual("stable", stable["library_tier"])
        self.assertGreater(stable["score"], experimental["score"])
        self.assertLess(experimental["score_breakdown"]["library_penalty"], 0)

    def test_mcp_capture_trajectory_tool_returns_structured_payload(self) -> None:
        observed_path = self._write_demo_json(
            "observed_mcp_capture.json",
            {
                "task_description": "Convert a CSV file into a JSON array file.",
                "steps": [
                    {
                        "tool_name": "read_text",
                        "tool_input": {"input_path": "demo/input/table.csv"},
                        "observation": "Read CSV input.",
                    },
                    {
                        "tool_name": "write_json",
                        "tool_input": {"output_path": "demo/output/table.json"},
                        "observation": "Wrote JSON output.",
                    },
                ],
            },
        )

        payload = self._call_mcp_tool(
            "capture_trajectory",
            {
                "file_path": str(observed_path),
                "task_id": "mcp_capture_test",
                "session_id": "mcp_capture_session",
            },
        )
        saved_path = Path(payload["data"]["trajectory_path"])
        self.addCleanup(saved_path.unlink)

        self.assertTrue(payload["data"]["captured"])
        self.assertEqual("mcp_capture_test", payload["data"]["task_id"])
        self.assertEqual("distill_trajectory", payload["data"]["recommended_next_action"])
        self._assert_host_operation_basics(
            payload["data"]["recommended_host_operation"],
            tool_name="distill_trajectory",
        )

    def test_mcp_capture_trajectory_tool_accepts_inline_observed_payload(self) -> None:
        payload = self._call_mcp_tool(
            "capture_trajectory",
            {
                "observed_task": self._build_move_logs_observed_task(
                    variant="nested",
                    input_dir="demo/inbox",
                    output_dir="demo/archive",
                    list_observation="Found 2 log files.",
                    move_observation="Moved the matching files.",
                    artifact="demo/archive/job1.log",
                ),
                "task_id": "mcp_capture_inline_test",
                "session_id": "mcp_capture_inline_session",
            },
        )
        saved_path = Path(payload["data"]["trajectory_path"])
        self.addCleanup(saved_path.unlink)

        self.assertTrue(payload["data"]["captured"])
        self.assertEqual("mcp_capture_inline_test", payload["data"]["task_id"])
        self.assertEqual("distill_trajectory", payload["data"]["recommended_next_action"])
        self._assert_host_operation_basics(
            payload["data"]["recommended_host_operation"],
            tool_name="distill_trajectory",
        )

    def test_cli_capture_trajectory_accepts_inline_observed_payload(self) -> None:
        payload = self._run_cli(
            "capture-trajectory",
            "--observed-task-json",
            json.dumps(
                self._build_move_logs_observed_task(
                    variant="compact",
                    input_dir="demo/inbox",
                    output_dir="demo/archive",
                    list_observation="Found 2 log files.",
                    move_observation="Moved the matching files.",
                    artifact="demo/archive/job1.log",
                )
            ),
            "--task-id",
            "cli_capture_inline_test",
            "--session-id",
            "cli_capture_inline_session",
            expect_json=True,
        )
        saved_path = Path(payload["data"]["trajectory_path"])
        self.addCleanup(saved_path.unlink)

        self.assertEqual("ok", payload["status"])
        self.assertTrue(payload["data"]["captured"])
        self.assertEqual("cli_capture_inline_test", payload["data"]["task_id"])
        self.assertEqual("distill_trajectory", payload["data"]["recommended_next_action"])

    def test_mcp_log_trajectory_returns_distill_follow_up(self) -> None:
        payload = self._call_mcp_tool(
            "log_trajectory",
            {"file_path": str(ROOT / "trajectories" / "demo_merge_text_files.json")},
        )
        self.assertTrue(payload["data"]["registered"])
        self.assertEqual("distill_trajectory", payload["data"]["recommended_next_action"])
        self._assert_host_operation_basics(
            payload["data"]["recommended_host_operation"],
            tool_name="distill_trajectory",
        )

    def test_service_search_without_matches_recommends_distill_and_promote(self) -> None:
        payload = self.service.search("nonexistent workflow phrase for zero matches", top_k=3)
        self.assertEqual("capture_trajectory", payload["recommended_next_action"])
        self.assertIsNone(payload["recommended_skill_name"])
        self.assertTrue(payload["results"])
        self.assertLess(payload["results"][0]["score"], self.service.RECOMMENDED_EXECUTION_SCORE)
        self._assert_host_operation_basics(
            payload["recommended_host_operation"],
            tool_name="capture_trajectory",
            source_ref="search:no_strong_match",
            display_label="Capture new workflow",
            requires_confirmation=False,
            operation_group="search_no_match_capture",
            delivery_mode="path",
        )
        self.assertEqual("preferred", payload["recommended_host_operation"]["variant_role"])
        self.assertEqual({}, payload["recommended_host_operation"]["arguments"])
        self._assert_argument_schema_entry(
            payload["recommended_host_operation"]["argument_schema"],
            "file_path",
            field_type="string",
            prefilled=False,
        )
        self._assert_argument_schema_entry(
            payload["recommended_host_operation"]["argument_schema"],
            "task_id",
            field_type="string",
        )
        self._assert_argument_schema_entry(
            payload["recommended_host_operation"]["argument_schema"],
            "session_id",
            field_type="string",
        )
        self.assertEqual(4, len(payload["available_host_operations"]))
        self._assert_operation_role(payload["available_host_operations"][0], "primary")
        self.assertEqual("capture_trajectory", payload["available_host_operations"][0]["tool_name"])
        inline_capture = next(
            item
            for item in payload["available_host_operations"]
            if item["tool_name"] == "capture_trajectory" and item["display_label"] == "Capture inline workflow"
        )
        self._assert_argument_schema_entry(
            inline_capture["argument_schema"],
            "observed_task",
            field_type="object",
            prefilled=False,
        )
        self.assertEqual("search_no_match_capture", inline_capture["operation_group"])
        self.assertEqual("inline", inline_capture["delivery_mode"])
        self.assertEqual("alternate", inline_capture["variant_role"])
        promote_new = next(
            item
            for item in payload["available_host_operations"]
            if item["tool_name"] == "distill_and_promote_candidate"
            and item["display_label"] == "Promote new workflow"
        )
        self._assert_argument_schema_entry(
            promote_new["argument_schema"],
            "trajectory_path",
            field_type="string",
            prefilled=False,
        )
        self._assert_argument_schema_entry(
            promote_new["argument_schema"],
            "observed_task_path",
            field_type="string",
            prefilled=False,
        )
        self._assert_argument_schema_entry(
            promote_new["argument_schema"],
            "skill_name",
            field_type="string",
        )
        self._assert_argument_schema_entry(
            promote_new["argument_schema"],
            "register_trajectory",
            field_type="boolean",
        )
        self.assertEqual("search_no_match_promote", promote_new["operation_group"])
        self.assertEqual("path", promote_new["delivery_mode"])
        self.assertEqual("preferred", promote_new["variant_role"])
        promote_inline = next(
            item
            for item in payload["available_host_operations"]
            if item["tool_name"] == "distill_and_promote_candidate"
            and item["display_label"] == "Promote inline workflow"
        )
        self._assert_argument_schema_entry(
            promote_inline["argument_schema"],
            "observed_task",
            field_type="object",
            prefilled=False,
        )
        self.assertEqual("search_no_match_promote", promote_inline["operation_group"])
        self.assertEqual("inline", promote_inline["delivery_mode"])
        self.assertEqual("alternate", promote_inline["variant_role"])

    def test_mcp_search_without_matches_returns_capture_primary(self) -> None:
        payload = self._call_mcp_tool(
            "search_skill",
            {"query": "nonexistent workflow phrase for zero matches", "top_k": 3},
        )
        self.assertEqual("capture_trajectory", payload["data"]["recommended_next_action"])
        self._assert_host_operation_basics(
            payload["data"]["recommended_host_operation"],
            tool_name="capture_trajectory",
        )

    def test_mcp_server_root_resolution(self) -> None:
        self.assertEqual(ROOT, resolve_runtime_root())
        self.assertEqual(ROOT, resolve_runtime_root(str(ROOT)))
