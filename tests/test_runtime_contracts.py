import subprocess
import sys

from tests.runtime_test_support import ROOT


class RuntimeContractTestsMixin:
    def test_check_runtime_contracts_script_passes(self) -> None:
        script = ROOT / "scripts" / "check_runtime_contracts.py"
        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(
            0,
            result.returncode,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        self.assertIn("Runtime contract check passed.", result.stdout)

    def test_check_runtime_contracts_detects_invalid_operation_shape(self) -> None:
        from scripts.check_runtime_contracts import validate_host_operation

        operation = {
            "type": "mcp_tool_call",
            "tool_name": "execute_skill",
            "arguments": {},
            "display_label": "Run skill",
            "effect_summary": "Execute a skill.",
            "argument_schema": {},
            "risk_level": "low",
            "requires_confirmation": False,
            "confirmation_message": None,
            "operation_role": "default",
            "source_ref": None,
        }
        violations = validate_host_operation(
            operation,
            label="bad-operation",
        )

        self.assertTrue(any("operation_id" in violation for violation in violations))

    def test_check_runtime_contracts_detects_invalid_mcp_wrapper_shape(self) -> None:
        from scripts.check_runtime_contracts import validate_mcp_tool_result

        violations = validate_mcp_tool_result(
            {
                "status": "ok",
            },
            label="bad-wrapper",
        )

        self.assertTrue(any("data" in violation for violation in violations))

    def test_check_runtime_contracts_detects_service_mcp_data_mismatch(self) -> None:
        from scripts.check_runtime_contracts import validate_wrapped_service_payload

        service_payload = {
            "query": "merge text files",
            "recommended_next_action": "execute_skill",
            "recommended_reason": None,
            "recommended_host_operation": {
                "type": "mcp_tool_call",
                "operation_id": "execute_skill:123",
                "tool_name": "execute_skill",
                "arguments": {"skill_name": "merge_text_files", "args": {}},
                "source_ref": "search:recommended_skill:merge_text_files",
                "display_label": "Run recommended skill",
                "effect_summary": "Execute the selected skill.",
                "argument_schema": {},
                "risk_level": "low",
                "requires_confirmation": False,
                "confirmation_message": None,
                "operation_role": "primary",
            },
            "available_host_operations": [],
        }
        self._assert_host_operation_basics(
            service_payload["recommended_host_operation"],
            tool_name="execute_skill",
            source_ref="search:recommended_skill:merge_text_files",
            display_label="Run recommended skill",
            risk_level="low",
            requires_confirmation=False,
        )
        self._assert_operation_role(service_payload["recommended_host_operation"], "primary")
        wrapped_payload = {
            "status": "ok",
            "data": {
                **service_payload,
                "recommended_next_action": "capture_trajectory",
            },
        }

        violations = validate_wrapped_service_payload(
            wrapped_payload,
            service_payload,
            label="search_skill",
        )

        self.assertTrue(any("data does not match service payload" in violation for violation in violations))

    def test_check_runtime_contracts_detects_invalid_error_wrapper_shape(self) -> None:
        from scripts.check_runtime_contracts import validate_mcp_tool_result

        violations = validate_mcp_tool_result(
            {
                "status": "error",
                "message": "bad request",
            },
            label="bad-error-wrapper",
        )

        self.assertTrue(any("code" in violation for violation in violations))
        self.assertTrue(any("details" in violation for violation in violations))

    def test_check_runtime_contracts_script_mentions_governance_and_lifecycle_equivalence(self) -> None:
        script_source = (ROOT / "scripts" / "check_runtime_contracts.py").read_text(encoding="utf-8")
        self.assertIn("governance_report", script_source)
        self.assertIn("backfill_skill_provenance", script_source)
        self.assertIn("reindex_skills", script_source)
        self.assertIn("log_trajectory", script_source)
        self.assertIn("execute_skill", script_source)
        self.assertIn("distill_trajectory", script_source)
        self.assertIn("audit_skill", script_source)
        self.assertIn("promote_skill", script_source)
        self.assertIn("archive_duplicate_candidates", script_source)
        self.assertIn("archive_fixture_skills", script_source)
        self.assertIn("archive_cold_skills", script_source)
        self.assertIn("distill_coverage_report", script_source)

    def test_ci_workflow_runs_mcp_architecture_check_and_runtime_suite(self) -> None:
        workflow_path = ROOT / ".github" / "workflows" / "runtime-contracts.yml"
        self.assertTrue(workflow_path.exists(), msg=f"Missing workflow: {workflow_path}")

        workflow = workflow_path.read_text(encoding="utf-8")
        self.assertIn("README.md", workflow)
        self.assertIn("README.zh-CN.md", workflow)
        self.assertIn("docs/mcp-integration.md", workflow)
        self.assertIn("docs/codex-integration.md", workflow)
        self.assertIn("python scripts/check_mcp_architecture.py", workflow)
        self.assertIn("python scripts/check_runtime_contracts.py", workflow)
        self.assertIn("python -m unittest tests.test_runtime -v", workflow)
