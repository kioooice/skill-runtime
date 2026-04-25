from tests.runtime_test_support import ROOT


class RuntimeLifecycleTestsMixin:
    def test_service_distill_and_promote_from_observed_single_file_transform_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_single_file_transform_service.json",
            {
                "task": "Normalize one text file into a cleaned output file.",
                "actions": [
                    {
                        "tool": "read_text",
                        "input": {"path": "demo/input/a.txt"},
                        "result": "Read text from demo/input/a.txt.",
                    },
                    {
                        "tool": "write_text",
                        "input": {"path": "demo/output/single_transform.txt"},
                        "result": "Wrote text to demo/output/single_transform.txt.",
                    },
                ],
                "outputs": ["demo/output/single_transform.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_single_file_transform_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("single_file_transform", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self.assertEqual("execute_skill", result["recommended_next_action"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_path", "output_path"),
        )

    def test_service_distill_and_promote_from_observed_csv_to_json_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_csv_to_json_service.json",
            {
                "task": "Convert one CSV file into a JSON output file.",
                "actions": [
                    {
                        "tool": "read_text",
                        "input": {"path": "demo/input/data.csv"},
                        "result": "Read text from demo/input/data.csv.",
                    },
                    {
                        "tool": "write_json",
                        "input": {"path": "demo/output/data.json"},
                        "result": "Wrote JSON to demo/output/data.json.",
                    },
                ],
                "outputs": ["demo/output/data.json"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_csv_to_json_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("csv_to_json", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self.assertEqual("execute_skill", result["recommended_next_action"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_path", "output_path"),
        )

    def test_service_distill_and_promote_from_observed_json_to_csv_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_json_to_csv_service.json",
            {
                "task": "Convert one JSON file into a CSV output file.",
                "actions": [
                    {
                        "tool": "read_json",
                        "input": {"path": "demo/input/data.json"},
                        "result": "Read JSON from demo/input/data.json.",
                    },
                    {
                        "tool": "write_text",
                        "input": {"path": "demo/output/data.csv"},
                        "result": "Wrote text to demo/output/data.csv.",
                    },
                ],
                "outputs": ["demo/output/data.csv"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_json_to_csv_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("json_to_csv", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self.assertEqual("execute_skill", result["recommended_next_action"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_path", "output_path"),
        )

    def test_service_distill_and_promote_from_observed_single_json_transform_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_single_json_transform.json",
            {
                "task": "Read one JSON file and write it to a new JSON output file.",
                "actions": [
                    {
                        "tool": "read_json",
                        "input": {"input_file": "demo/input/data.json"},
                        "result": "Read JSON from demo/input/data.json.",
                    },
                    {
                        "tool": "write_json",
                        "input": {"output_file": "demo/output/data_copy.json"},
                        "result": "Wrote JSON to demo/output/data_copy.json.",
                    },
                ],
                "outputs": ["demo/output/data_copy.json"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_single_json_transform_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("single_json_transform", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_path", "output_path"),
        )

    def test_service_distill_and_promote_from_observed_input_output_file_aliases_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_input_output_file_aliases.json",
            {
                "task": "Normalize one text file into a cleaned output file.",
                "actions": [
                    {
                        "tool": "read_text",
                        "input": {"input_file": "demo/input/a.txt"},
                        "result": "Read text from demo/input/a.txt.",
                    },
                    {
                        "tool": "write_text",
                        "input": {"output_file": "demo/output/alias_single_transform.txt"},
                        "result": "Wrote text to demo/output/alias_single_transform.txt.",
                    },
                ],
                "outputs": ["demo/output/alias_single_transform.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_input_output_file_alias_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("single_file_transform", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_path", "output_path"),
        )

    def test_service_distill_and_promote_from_observed_single_file_copy_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_single_file_copy.json",
            {
                "task": "Copy one text file into a new output file.",
                "actions": [
                    {
                        "tool": "copy_file",
                        "input": {"source_file": "demo/input/a.txt", "destination_file": "demo/output/copied_a.txt"},
                        "result": "Copied the source file.",
                    },
                ],
                "outputs": ["demo/output/copied_a.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_single_file_copy_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("single_file_copy", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_path", "output_path"),
        )

    def test_service_distill_and_promote_from_observed_single_file_move_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_single_file_move.json",
            {
                "task": "Move one text file into a new output file.",
                "actions": [
                    {
                        "tool": "move_file",
                        "input": {"source_path": "demo/input/a.txt", "target_path": "demo/output/moved_a.txt"},
                        "result": "Moved the source file.",
                    },
                ],
                "outputs": ["demo/output/moved_a.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_single_file_move_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("single_file_move", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_path", "output_path"),
        )

    def test_service_distill_and_promote_from_observed_single_file_rename_source_target_aliases_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_single_file_rename_source_target.json",
            {
                "task": "Rename one text file to a new output path.",
                "actions": [
                    {
                        "tool": "rename_path",
                        "input": {"source": "demo/input/a.txt", "target": "demo/output/renamed_a.txt"},
                        "result": "Renamed the source file.",
                    },
                ],
                "outputs": ["demo/output/renamed_a.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_single_file_rename_source_target_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("single_file_move", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_path", "output_path"),
        )

    def test_service_distill_and_promote_from_observed_source_target_dir_aliases_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_source_target_dir_aliases.json",
            {
                "task": "Move all log files from inbox to archive.",
                "actions": [
                    {
                        "tool": "list_files",
                        "input": {"source_dir": "demo/inbox", "pattern": "*.log"},
                        "result": "Found 2 log files.",
                    },
                    {
                        "tool": "move_file",
                        "input": {"source_dir": "demo/inbox", "target_dir": "demo/archive"},
                        "result": "Moved the matching files.",
                    },
                ],
                "outputs": ["demo/archive/job1.log"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_source_target_dir_alias_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_move", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern"),
        )

    def test_service_distill_and_promote_from_execute_observed_task_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        execute_result = sandbox_service.execute(
            "merge_text_files",
            {"input_dir": "demo/input", "output_path": "demo/output/execute_roundtrip_merge.md"},
        )
        observed_path = execute_result["observed_task_record"]

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="execute_observed_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertIsNotNone(result["capture"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("execute_observed_roundtrip_test", result["promotion"]["skill_name"])
        self.assertEqual("text_merge", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self.assertEqual("execute_skill", result["recommended_next_action"])
        self._assert_host_operation_basics(
            result["recommended_host_operation"],
            tool_name="execute_skill",
        )
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_path", "pattern"),
        )

    def test_service_distill_and_promote_from_execute_directory_move_observed_task_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        inbox = sandbox_root / "demo" / "inbox"
        archive = sandbox_root / "demo" / "archive"
        inbox.mkdir(parents=True, exist_ok=True)
        archive.mkdir(parents=True, exist_ok=True)
        (inbox / "job1.log").write_text("alpha\n", encoding="utf-8")
        (inbox / "job2.log").write_text("beta\n", encoding="utf-8")

        execute_result = sandbox_service.execute(
            "archive_log_files_dogfood",
            {"input_dir": "demo/inbox", "output_dir": "demo/archive", "pattern": "*.log"},
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=execute_result["observed_task_record"],
            skill_name="execute_directory_move_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_move", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern"),
        )

    def test_service_distill_and_promote_from_execute_directory_copy_observed_task_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        source_dir = sandbox_root / "demo" / "copy_input"
        target_dir = sandbox_root / "demo" / "copy_output"
        source_dir.mkdir(parents=True, exist_ok=True)
        target_dir.mkdir(parents=True, exist_ok=True)
        (source_dir / "a.txt").write_text("alpha\n", encoding="utf-8")
        (source_dir / "b.txt").write_text("beta\n", encoding="utf-8")

        execute_result = sandbox_service.execute(
            "directory_copy_rule_test",
            {"input_dir": "demo/copy_input", "output_dir": "demo/copy_output", "pattern": "*.txt"},
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=execute_result["observed_task_record"],
            skill_name="execute_directory_copy_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_copy", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern"),
        )

    def test_service_distill_and_promote_from_execute_batch_rename_observed_task_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        input_dir = sandbox_root / "demo" / "rename_input"
        input_dir.mkdir(parents=True, exist_ok=True)
        (input_dir / "a.txt").write_text("alpha\n", encoding="utf-8")
        (input_dir / "b.txt").write_text("beta\n", encoding="utf-8")

        execute_result = sandbox_service.execute(
            "batch_rename_rule_test",
            {"input_dir": "demo/rename_input", "prefix": "done_", "pattern": "*.txt"},
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=execute_result["observed_task_record"],
            skill_name="execute_batch_rename_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("batch_rename", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "prefix", "pattern"),
        )

    def test_service_distill_and_promote_flow(self) -> None:
        sandbox_root, sandbox_service, sandbox_index = self._make_runtime_sandbox()
        result = sandbox_service.distill_and_promote(
            trajectory_path=sandbox_root / "trajectories" / "demo_merge_text_files.json",
            skill_name="service_distill_and_promote_test",
        )
        self.assertTrue(result["promoted"])
        self.assertIsNotNone(result["trajectory"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("service_distill_and_promote_test", result["promotion"]["skill_name"])

        promoted = sandbox_index.get("service_distill_and_promote_test")
        self.assertIsNotNone(promoted)
        self.assertEqual("active", promoted.status)
        self.assertEqual("execute_skill", result["recommended_next_action"])
        self._assert_host_operation_basics(
            result["recommended_host_operation"],
            tool_name="execute_skill",
        )
        self.assertEqual(
            "service_distill_and_promote_test",
            result["recommended_host_operation"]["arguments"]["skill_name"],
        )
        self._assert_execute_skill_schema(result["recommended_host_operation"])

    def test_service_distill_returns_audit_follow_up_host_operation(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        result = sandbox_service.distill(
            sandbox_root / "trajectories" / "demo_merge_text_files.json",
            skill_name="service_distill_followup_test",
        )
        self.assertEqual("audit_skill", result["recommended_next_action"])
        self._assert_host_operation_basics(
            result["recommended_host_operation"],
            tool_name="audit_skill",
        )
        self.assertEqual(result["staging_file"], result["recommended_host_operation"]["arguments"]["file_path"])
        self.assertEqual(
            result["trajectory_path"],
            result["recommended_host_operation"]["arguments"]["trajectory_path"],
        )
        self._assert_operation_role(result["available_host_operations"][0], "primary")

    def test_service_distill_and_promote_from_observed_task(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_distill_promote_service.json",
            self._build_move_logs_observed_task(variant="steps"),
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_distill_promote_service_test",
        )
        self.assertTrue(result["promoted"])
        self.assertIsNotNone(result["capture"])
        self.assertIsNone(result["trajectory"])
        self.assertEqual("observed_distill_promote_service_test", result["promotion"]["skill_name"])
        self.assertEqual("execute_skill", result["recommended_next_action"])
        self._assert_host_operation_basics(
            result["recommended_host_operation"],
            tool_name="execute_skill",
        )
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern"),
        )

    def test_mcp_distill_and_promote_tool_returns_promoted_skill(self) -> None:
        sandbox_root, _, _ = self._make_runtime_sandbox()
        payload = self._call_mcp_tool(
            "distill_and_promote_candidate",
            {
                "trajectory_path": str(sandbox_root / "trajectories" / "demo_merge_text_files.json"),
                "skill_name": "mcp_distill_and_promote_test",
                "register_trajectory": True,
            },
            root=sandbox_root,
        )
        self.assertTrue(payload["data"]["promoted"])
        self.assertEqual("mcp_distill_and_promote_test", payload["data"]["promotion"]["skill_name"])
        self.assertEqual("execute_skill", payload["data"]["recommended_next_action"])
        self._assert_host_operation_basics(
            payload["data"]["recommended_host_operation"],
            tool_name="execute_skill",
        )
        self._assert_execute_skill_schema(
            payload["data"]["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_path", "pattern"),
        )

    def test_mcp_distill_and_promote_tool_accepts_observed_task(self) -> None:
        sandbox_root, _, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_distill_promote_mcp.json",
            self._build_move_logs_observed_task(variant="steps", artifact=None),
        )

        payload = self._call_mcp_tool(
            "distill_and_promote_candidate",
            {
                "observed_task_path": str(observed_path),
                "skill_name": "mcp_observed_distill_promote_test",
            },
            root=sandbox_root,
        )
        self.assertTrue(payload["data"]["promoted"])
        self.assertIsNotNone(payload["data"]["capture"])
        self.assertEqual("execute_skill", payload["data"]["recommended_next_action"])
        self._assert_host_operation_basics(
            payload["data"]["recommended_host_operation"],
            tool_name="execute_skill",
        )
        self._assert_execute_skill_schema(
            payload["data"]["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern"),
        )

    def test_cli_distill_and_promote_accepts_observed_task(self) -> None:
        sandbox_root, _, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_distill_promote_cli.json",
            self._build_move_logs_observed_task(variant="steps", artifact=None),
        )

        payload = self._run_cli(
            "distill-and-promote",
            "--observed-task",
            str(observed_path),
            "--skill-name",
            "cli_observed_distill_promote_test",
            root=sandbox_root,
            expect_json=True,
        )
        self.assertEqual("ok", payload["status"])
        self.assertTrue(payload["data"]["promoted"])
        self.assertIsNotNone(payload["data"]["capture"])

    def test_cli_distill_and_promote_accepts_compact_observed_task(self) -> None:
        sandbox_root, _, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_distill_promote_compact_cli.json",
            self._build_move_logs_observed_task(variant="compact"),
        )

        payload = self._run_cli(
            "distill-and-promote",
            "--observed-task",
            str(observed_path),
            "--skill-name",
            "cli_compact_observed_distill_promote_test",
            root=sandbox_root,
            expect_json=True,
        )
        self.assertEqual("ok", payload["status"])
        self.assertTrue(payload["data"]["promoted"])
        self.assertIsNotNone(payload["data"]["capture"])

    def test_cli_distill_and_promote_accepts_nested_tool_call_logs(self) -> None:
        sandbox_root, _, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_distill_promote_nested_cli.json",
            self._build_move_logs_observed_task(variant="nested"),
        )

        payload = self._run_cli(
            "distill-and-promote",
            "--observed-task",
            str(observed_path),
            "--skill-name",
            "cli_nested_observed_distill_promote_test",
            root=sandbox_root,
            expect_json=True,
        )
        self.assertEqual("ok", payload["status"])
        self.assertTrue(payload["data"]["promoted"])
        self.assertIsNotNone(payload["data"]["capture"])
