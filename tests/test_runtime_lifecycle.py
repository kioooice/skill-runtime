from tests.runtime_test_support import ROOT


class RuntimeLifecycleTestsMixin:
    def test_service_distill_and_promote_flow(self) -> None:
        result = self.service.distill_and_promote(
            trajectory_path=ROOT / "trajectories" / "demo_merge_text_files.json",
            skill_name="service_distill_and_promote_test",
        )
        self.assertTrue(result["promoted"])
        self.assertIsNotNone(result["trajectory"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("service_distill_and_promote_test", result["promotion"]["skill_name"])

        promoted = self.index.get("service_distill_and_promote_test")
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
        result = self.service.distill(
            ROOT / "trajectories" / "demo_merge_text_files.json",
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
        observed_path = self._write_demo_json(
            "observed_distill_promote_service.json",
            self._build_move_logs_observed_task(variant="steps"),
        )

        result = self.service.distill_and_promote(
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
        payload = self._call_mcp_tool(
            "distill_and_promote_candidate",
            {
                "trajectory_path": str(ROOT / "trajectories" / "demo_merge_text_files.json"),
                "skill_name": "mcp_distill_and_promote_test",
                "register_trajectory": True,
            },
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
        observed_path = self._write_demo_json(
            "observed_distill_promote_mcp.json",
            self._build_move_logs_observed_task(variant="steps", artifact=None),
        )

        payload = self._call_mcp_tool(
            "distill_and_promote_candidate",
            {
                "observed_task_path": str(observed_path),
                "skill_name": "mcp_observed_distill_promote_test",
            },
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
        observed_path = self._write_demo_json(
            "observed_distill_promote_cli.json",
            self._build_move_logs_observed_task(variant="steps", artifact=None),
        )

        payload = self._run_cli(
            "distill-and-promote",
            "--observed-task",
            str(observed_path),
            "--skill-name",
            "cli_observed_distill_promote_test",
            expect_json=True,
        )
        self.assertEqual("ok", payload["status"])
        self.assertTrue(payload["data"]["promoted"])
        self.assertIsNotNone(payload["data"]["capture"])

    def test_cli_distill_and_promote_accepts_compact_observed_task(self) -> None:
        observed_path = self._write_demo_json(
            "observed_distill_promote_compact_cli.json",
            self._build_move_logs_observed_task(variant="compact"),
        )

        payload = self._run_cli(
            "distill-and-promote",
            "--observed-task",
            str(observed_path),
            "--skill-name",
            "cli_compact_observed_distill_promote_test",
            expect_json=True,
        )
        self.assertEqual("ok", payload["status"])
        self.assertTrue(payload["data"]["promoted"])
        self.assertIsNotNone(payload["data"]["capture"])

    def test_cli_distill_and_promote_accepts_nested_tool_call_logs(self) -> None:
        observed_path = self._write_demo_json(
            "observed_distill_promote_nested_cli.json",
            self._build_move_logs_observed_task(variant="nested"),
        )

        payload = self._run_cli(
            "distill-and-promote",
            "--observed-task",
            str(observed_path),
            "--skill-name",
            "cli_nested_observed_distill_promote_test",
            expect_json=True,
        )
        self.assertEqual("ok", payload["status"])
        self.assertTrue(payload["data"]["promoted"])
        self.assertIsNotNone(payload["data"]["capture"])
