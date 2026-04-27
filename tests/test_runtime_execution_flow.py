from pathlib import Path

from skill_runtime.api.service import RuntimeServiceError
from tests.runtime_test_support import ROOT


class RuntimeExecutionFlowTestsMixin:
    def test_service_execute_blocks_shell_without_scope_permission(self) -> None:
        sandbox_root, sandbox_service, sandbox_index = self._make_runtime_sandbox()
        self._write_active_skill_fixture(
            "scope_block_shell_skill",
            {
                "summary": "Attempt to run a shell command.",
                "docstring": "scope test",
                "input_schema": {},
                "output_schema": {"status": "str"},
                "source_trajectory_ids": [],
                "created_at": "2026-04-27T00:00:00+00:00",
                "last_used_at": None,
                "usage_count": 0,
                "status": "active",
                "audit_score": 100,
                "tags": ["scope", "shell"],
            },
            source=(
                "def run(tools, **kwargs):\n"
                "    return tools.run_shell(['python', '-c', \"print('blocked')\"])\n"
            ),
            root=sandbox_root,
        )
        sandbox_index.rebuild_from_directory(sandbox_root / "skill_store" / "active")

        with self.assertRaises(RuntimeServiceError) as context:
            sandbox_service.execute("scope_block_shell_skill", {})

        self.assertEqual("SKILL_EXECUTION_FAILED", context.exception.code)
        self.assertIn("shell access is not allowed", context.exception.details["reason"])

    def test_service_execute_honors_allowed_roots_and_extensions(self) -> None:
        sandbox_root, sandbox_service, sandbox_index = self._make_runtime_sandbox()
        self._write_active_skill_fixture(
            "scope_write_skill",
            {
                "summary": "Write scoped output.",
                "docstring": "scope test",
                "input_schema": {"output_path": "str"},
                "output_schema": {"status": "str"},
                "source_trajectory_ids": [],
                "created_at": "2026-04-27T00:00:00+00:00",
                "last_used_at": None,
                "usage_count": 0,
                "status": "active",
                "audit_score": 100,
                "tags": ["scope", "write"],
                "scope_policy": {
                    "allowed_roots": ["demo/output"],
                    "allowed_extensions": [".txt"],
                },
            },
            source=(
                "def run(tools, output_path, **kwargs):\n"
                "    tools.write_text(output_path, 'scoped')\n"
                "    return {'status': 'completed'}\n"
            ),
            root=sandbox_root,
        )
        sandbox_index.rebuild_from_directory(sandbox_root / "skill_store" / "active")

        allowed_result = sandbox_service.execute(
            "scope_write_skill",
            {"output_path": "demo/output/scoped.txt"},
        )
        self.assertEqual("completed", allowed_result["result"]["status"])
        self.assertTrue((sandbox_root / "demo" / "output" / "scoped.txt").exists())

        with self.assertRaises(RuntimeServiceError) as root_error:
            sandbox_service.execute(
                "scope_write_skill",
                {"output_path": "demo/input/scoped.txt"},
            )
        self.assertEqual("SKILL_EXECUTION_FAILED", root_error.exception.code)
        self.assertIn("path is outside allowed roots", root_error.exception.details["reason"])

        with self.assertRaises(RuntimeServiceError) as extension_error:
            sandbox_service.execute(
                "scope_write_skill",
                {"output_path": "demo/output/scoped.json"},
            )
        self.assertEqual("SKILL_EXECUTION_FAILED", extension_error.exception.code)
        self.assertIn("path extension is not allowed", extension_error.exception.details["reason"])

    def test_service_execute_blocks_mutation_when_dry_run_is_required(self) -> None:
        sandbox_root, sandbox_service, sandbox_index = self._make_runtime_sandbox()
        self._write_active_skill_fixture(
            "scope_requires_dry_run_skill",
            {
                "summary": "Write output behind dry-run policy.",
                "docstring": "scope test",
                "input_schema": {"output_path": "str"},
                "output_schema": {"status": "str"},
                "source_trajectory_ids": [],
                "created_at": "2026-04-27T00:00:00+00:00",
                "last_used_at": None,
                "usage_count": 0,
                "status": "active",
                "audit_score": 100,
                "tags": ["scope", "dry-run"],
                "scope_policy": {
                    "allowed_roots": ["demo/output"],
                    "allowed_extensions": [".txt"],
                    "requires_dry_run": True,
                },
            },
            source=(
                "def run(tools, output_path, **kwargs):\n"
                "    tools.write_text(output_path, 'dry-run-required')\n"
                "    return {'status': 'completed'}\n"
            ),
            root=sandbox_root,
        )
        sandbox_index.rebuild_from_directory(sandbox_root / "skill_store" / "active")

        with self.assertRaises(RuntimeServiceError) as context:
            sandbox_service.execute(
                "scope_requires_dry_run_skill",
                {"output_path": "demo/output/requires_dry_run.txt"},
            )

        self.assertEqual("SKILL_EXECUTION_FAILED", context.exception.code)
        self.assertIn("dry-run execution is required", context.exception.details["reason"])

    def test_service_execute_dry_run_returns_planned_changes_without_writing(self) -> None:
        sandbox_root, sandbox_service, sandbox_index = self._make_runtime_sandbox()
        self._write_active_skill_fixture(
            "scope_dry_run_plan_skill",
            {
                "summary": "Plan a scoped write.",
                "docstring": "scope test",
                "input_schema": {"output_path": "str"},
                "output_schema": {"status": "str"},
                "source_trajectory_ids": [],
                "created_at": "2026-04-27T00:00:00+00:00",
                "last_used_at": None,
                "usage_count": 0,
                "status": "active",
                "audit_score": 100,
                "tags": ["scope", "dry-run"],
                "scope_policy": {
                    "allowed_roots": ["demo/output"],
                    "allowed_extensions": [".txt"],
                    "requires_dry_run": True,
                },
            },
            source=(
                "def run(tools, output_path, **kwargs):\n"
                "    tools.write_text(output_path, 'planned-write')\n"
                "    return {'status': 'completed', 'mode': 'dry-run'}\n"
            ),
            root=sandbox_root,
        )
        sandbox_index.rebuild_from_directory(sandbox_root / "skill_store" / "active")

        result = sandbox_service.execute(
            "scope_dry_run_plan_skill",
            {"output_path": "demo/output/planned_only.txt"},
            dry_run=True,
        )

        self.assertTrue(result["dry_run"])
        self.assertEqual("completed", result["result"]["status"])
        self.assertEqual("dry-run", result["result"]["mode"])
        self.assertFalse((sandbox_root / "demo" / "output" / "planned_only.txt").exists())
        self.assertEqual(result["operation_log"], result["observed_task"]["operation_log"])
        self.assertEqual(1, len(result["planned_changes"]))
        self.assertEqual("write_text", result["planned_changes"][0]["tool_name"])
        self.assertEqual("planned", result["planned_changes"][0]["status"])
        self.assertEqual("op_0001", result["planned_changes"][0]["operation_id"])
        self.assertTrue(result["planned_changes"][0]["mutation"])
        self.assertEqual(
            {
                "strategy": "delete_created_file",
                "target_path": "demo/output/planned_only.txt",
            },
            result["planned_changes"][0]["rollback_hint"],
        )
        self.assertIn("Would write text", result["planned_changes"][0]["observation"])

    def test_scope_policy_round_trips_through_skill_index(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        self._write_active_skill_fixture(
            "scope_round_trip_skill",
            {
                "summary": "Round-trip scope metadata.",
                "docstring": "scope test",
                "input_schema": {},
                "output_schema": {"status": "str"},
                "source_trajectory_ids": [],
                "created_at": "2026-04-27T00:00:00+00:00",
                "last_used_at": None,
                "usage_count": 0,
                "status": "active",
                "audit_score": 100,
                "tags": ["scope"],
                "scope_policy": {
                    "allow_shell": False,
                    "allow_delete": False,
                    "allowed_roots": ["demo/output"],
                    "allowed_extensions": [".txt"],
                    "requires_dry_run": True,
                },
            },
            root=sandbox_root,
        )
        sandbox_index.rebuild_from_directory(sandbox_root / "skill_store" / "active")

        metadata = sandbox_index.get("scope_round_trip_skill")

        self.assertIsNotNone(metadata)
        self.assertEqual(
            {
                "allow_shell": False,
                "allow_delete": False,
                "allowed_roots": ["demo/output"],
                "allowed_extensions": [".txt"],
                "requires_dry_run": True,
            },
            metadata.scope_policy,
        )

    def test_execute_active_skill(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        output_path = sandbox_root / "demo" / "output" / "test_merged.md"

        before = sandbox_index.get("merge_text_files")
        self.assertIsNotNone(before)
        before_usage = before.usage_count

        args_file = self._write_args_file(
            "test_execute_args.json",
            {"input_dir": "demo/input", "output_path": "demo/output/test_merged.md"},
            root=sandbox_root,
        )
        payload = self._execute_skill_cli("merge_text_files", args_file=args_file, root=sandbox_root)
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

        after = sandbox_index.get("merge_text_files")
        self.assertIsNotNone(after)
        self.assertEqual(before_usage + 1, after.usage_count)
        self.assertIsNotNone(after.last_used_at)

    def test_execute_cli_accepts_utf8_bom_args_file(self) -> None:
        sandbox_root, _, _ = self._make_runtime_sandbox()
        output_path = sandbox_root / "demo" / "output" / "bom_execute.md"
        args_file = sandbox_root / "demo" / "bom_execute_args.json"
        args_file.write_text(
            '{"input_dir":"demo/input","output_path":"demo/output/bom_execute.md"}',
            encoding="utf-8-sig",
        )
        self.addCleanup(lambda: args_file.unlink(missing_ok=True))
        self.addCleanup(lambda: output_path.unlink(missing_ok=True))

        payload = self._execute_skill_cli("merge_text_files", args_file=args_file, root=sandbox_root)

        self.assertEqual("ok", payload["status"])
        self.assertTrue(output_path.exists())

    def test_execute_cli_dry_run_returns_planned_changes(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        self._write_active_skill_fixture(
            "scope_cli_dry_run_skill",
            {
                "summary": "Plan output through CLI dry-run.",
                "docstring": "scope test",
                "input_schema": {"output_path": "str"},
                "output_schema": {"status": "str"},
                "source_trajectory_ids": [],
                "created_at": "2026-04-27T00:00:00+00:00",
                "last_used_at": None,
                "usage_count": 0,
                "status": "active",
                "audit_score": 100,
                "tags": ["scope", "dry-run", "cli"],
                "scope_policy": {
                    "allowed_roots": ["demo/output"],
                    "allowed_extensions": [".txt"],
                    "requires_dry_run": True,
                },
            },
            source=(
                "def run(tools, output_path, **kwargs):\n"
                "    tools.write_text(output_path, 'cli-planned-write')\n"
                "    return {'status': 'completed'}\n"
            ),
            root=sandbox_root,
        )
        sandbox_index.rebuild_from_directory(sandbox_root / "skill_store" / "active")
        output_path = sandbox_root / "demo" / "output" / "cli_planned_only.txt"
        args_file = self._write_args_file(
            "cli_dry_run_args.json",
            {"output_path": "demo/output/cli_planned_only.txt"},
            root=sandbox_root,
        )

        payload = self._run_cli(
            "execute",
            "--skill",
            "scope_cli_dry_run_skill",
            "--args-file",
            str(args_file),
            "--dry-run",
            root=sandbox_root,
            expect_json=True,
        )

        self.assertEqual("ok", payload["status"])
        self.assertTrue(payload["data"]["dry_run"])
        self.assertFalse(output_path.exists())
        self.assertEqual(payload["data"]["operation_log"], payload["data"]["planned_changes"])
        self.assertEqual("planned", payload["data"]["planned_changes"][0]["status"])

    def test_service_execute_returns_observed_task_record(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        result = sandbox_service.execute(
            "merge_text_files",
            {"input_dir": "demo/input", "output_path": "demo/output/service_execute_observed.md"},
        )
        output_path = sandbox_root / "demo" / "output" / "service_execute_observed.md"
        self.addCleanup(lambda: output_path.unlink(missing_ok=True))
        observed_path = Path(result["observed_task_record"])
        self.addCleanup(observed_path.unlink)

        self.assertTrue(output_path.exists())
        self.assertTrue(observed_path.exists())
        observed_payload = self._read_json_file(observed_path)
        self.assertEqual(observed_payload, result["observed_task"])
        self.assertEqual(result["operation_log"], result["observed_task"]["operation_log"])
        self._assert_observed_skill_record(
            observed_payload,
            skill_name="merge_text_files",
            status="completed",
            contains_tool="write_text",
        )
        self.assertEqual("op_0001", result["operation_log"][0]["operation_id"])
        self.assertFalse(result["operation_log"][0]["mutation"])
        write_record = next(
            record for record in result["operation_log"] if record["tool_name"] == "write_text"
        )
        self.assertEqual("success", write_record["status"])
        self.assertTrue(write_record["mutation"])
        self.assertEqual(
            {
                "strategy": "delete_created_file",
                "target_path": "demo/output/service_execute_observed.md",
            },
            write_record["rollback_hint"],
        )

    def test_service_execute_returns_follow_up_host_operation(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        result = sandbox_service.execute(
            "merge_text_files",
            {"input_dir": "demo/input", "output_path": "demo/output/service_execute_followup.md"},
        )
        output_path = sandbox_root / "demo" / "output" / "service_execute_followup.md"
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
        self.assertEqual("execute_promote", result["recommended_host_operation"]["operation_group"])
        self.assertEqual("path", result["recommended_host_operation"]["delivery_mode"])
        self.assertEqual("preferred", result["recommended_host_operation"]["variant_role"])
        self.assertIn("observed task record", result["recommended_host_operation"]["effect_summary"])
        self.assertTrue(result["available_host_operations"])
        self.assertEqual("distill_and_promote_candidate", result["available_host_operations"][0]["tool_name"])
        self._assert_operation_role(result["available_host_operations"][0], "primary")
        self.assertGreaterEqual(len(result["available_host_operations"]), 2)
        inline_follow_up = result["available_host_operations"][1]
        self.assertEqual("distill_and_promote_candidate", inline_follow_up["tool_name"])
        self.assertEqual(result["observed_task"], inline_follow_up["arguments"]["observed_task"])
        self.assertEqual("Promote this execution inline", inline_follow_up["display_label"])
        self.assertEqual("execute_promote", inline_follow_up["operation_group"])
        self.assertEqual("inline", inline_follow_up["delivery_mode"])
        self.assertEqual("alternate", inline_follow_up["variant_role"])
        self._assert_operation_role(inline_follow_up, "default")

    def test_mcp_execute_tool_returns_follow_up_host_operation(self) -> None:
        sandbox_root, _, _ = self._make_runtime_sandbox()
        output_path = sandbox_root / "demo" / "output" / "mcp_execute_followup.md"
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
            root=sandbox_root,
        )
        observed_path = Path(payload["data"]["observed_task_record"])
        self.addCleanup(observed_path.unlink)

        self.assertEqual(self._read_json_file(observed_path), payload["data"]["observed_task"])
        self._assert_observed_task_follow_up(
            payload["data"]["recommended_host_operation"],
            observed_task_path=payload["data"]["observed_task_record"],
        )
