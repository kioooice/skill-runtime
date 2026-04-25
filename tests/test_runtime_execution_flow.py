from pathlib import Path

from tests.runtime_test_support import ROOT


class RuntimeExecutionFlowTestsMixin:
    def test_execute_active_skill(self) -> None:
        output_path = ROOT / "demo" / "output" / "test_merged.md"
        if output_path.exists():
            output_path.unlink()

        before = self.index.get("merge_text_files")
        self.assertIsNotNone(before)
        before_usage = before.usage_count

        args_file = self._write_args_file(
            "test_execute_args.json",
            {"input_dir": "demo/input", "output_path": "demo/output/test_merged.md"},
        )
        payload = self._execute_skill_cli("merge_text_files", args_file=args_file)
        self.assertTrue(output_path.exists())
        observed_path = Path(payload["data"]["observed_task_record"])
        self.addCleanup(observed_path.unlink)
        self.assertTrue(observed_path.exists())
        observed_payload = self._read_json_file(observed_path)
        self._assert_observed_skill_record(
            observed_payload,
            skill_name="merge_text_files",
            first_tool="list_files",
            last_tool="write_text",
        )

        after = self.index.get("merge_text_files")
        self.assertIsNotNone(after)
        self.assertEqual(before_usage + 1, after.usage_count)
        self.assertIsNotNone(after.last_used_at)

    def test_service_execute_returns_observed_task_record(self) -> None:
        result = self.service.execute(
            "merge_text_files",
            {"input_dir": "demo/input", "output_path": "demo/output/service_execute_observed.md"},
        )
        output_path = ROOT / "demo" / "output" / "service_execute_observed.md"
        self.addCleanup(lambda: output_path.unlink(missing_ok=True))
        observed_path = Path(result["observed_task_record"])
        self.addCleanup(observed_path.unlink)

        self.assertTrue(output_path.exists())
        self.assertTrue(observed_path.exists())
        observed_payload = self._read_json_file(observed_path)
        self._assert_observed_skill_record(
            observed_payload,
            skill_name="merge_text_files",
            status="completed",
            contains_tool="write_text",
        )

    def test_service_execute_returns_follow_up_host_operation(self) -> None:
        result = self.service.execute(
            "merge_text_files",
            {"input_dir": "demo/input", "output_path": "demo/output/service_execute_followup.md"},
        )
        output_path = ROOT / "demo" / "output" / "service_execute_followup.md"
        self.addCleanup(lambda: output_path.unlink(missing_ok=True))
        observed_path = Path(result["observed_task_record"])
        self.addCleanup(observed_path.unlink)

        self.assertEqual("distill_and_promote_candidate", result["recommended_next_action"])
        self._assert_observed_task_follow_up(
            result["recommended_host_operation"],
            observed_task_path=result["observed_task_record"],
            display_label="Promote this execution",
            risk_level="medium",
        )
        self.assertIn("observed task record", result["recommended_host_operation"]["effect_summary"])
        self.assertTrue(result["available_host_operations"])
        self.assertEqual("distill_and_promote_candidate", result["available_host_operations"][0]["tool_name"])
        self._assert_operation_role(result["available_host_operations"][0], "primary")

    def test_mcp_execute_tool_returns_follow_up_host_operation(self) -> None:
        output_path = ROOT / "demo" / "output" / "mcp_execute_followup.md"
        self.addCleanup(lambda: output_path.unlink(missing_ok=True))

        payload = self._call_mcp_tool(
            "execute_skill",
            {
                "skill_name": "merge_text_files",
                "args": {
                    "input_dir": "demo/input",
                    "output_path": "demo/output/mcp_execute_followup.md",
                },
            },
        )
        observed_path = Path(payload["data"]["observed_task_record"])
        self.addCleanup(observed_path.unlink)

        self._assert_observed_task_follow_up(
            payload["data"]["recommended_host_operation"],
            observed_task_path=payload["data"]["observed_task_record"],
        )
