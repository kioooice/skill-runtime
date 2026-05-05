import json
import subprocess
import sys
import tempfile
from pathlib import Path

from tests.runtime_test_support import ROOT


class RuntimeProviderQualityEvalTestsMixin:
    def test_provider_quality_evaluation_script_reports_fixture_outcomes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "evaluate_provider_quality.py")],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=str(ROOT),
            timeout=120,
            check=False,
        )

        self.assertEqual(0, result.returncode, msg=result.stderr or result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual("ok", payload["status"])
        fixtures = {item["fixture_name"]: item for item in payload["fixtures"]}

        self.assertIn("demo_local_success", fixtures)
        self.assertIn("loop_stage", fixtures["demo_local_success"])
        self.assertEqual("passed", fixtures["demo_local_success"]["generated_candidate_status"])
        self.assertEqual("passed", fixtures["demo_local_success"]["audit_status"])
        self.assertEqual("passed", fixtures["demo_local_success"]["execution_smoke_status"])
        self.assertEqual("execution_passed", fixtures["demo_local_success"]["loop_stage"])

        self.assertIn("mock_template_execute_failure", fixtures)
        self.assertIn("loop_stage", fixtures["mock_template_execute_failure"])
        self.assertEqual("passed", fixtures["mock_template_execute_failure"]["generated_candidate_status"])
        self.assertEqual("needs_fix", fixtures["mock_template_execute_failure"]["audit_status"])
        self.assertEqual("skipped", fixtures["mock_template_execute_failure"]["execution_smoke_status"])
        self.assertEqual("audit_failed", fixtures["mock_template_execute_failure"]["loop_stage"])
        self.assertTrue(fixtures["mock_template_execute_failure"]["failure_reason"])

        self.assertIn("fake_deepseek_repair_success", fixtures)
        self.assertEqual("passed", fixtures["fake_deepseek_repair_success"]["generated_candidate_status"])
        self.assertTrue(fixtures["fake_deepseek_repair_success"]["repair_attempted"])
        self.assertEqual("attempted", fixtures["fake_deepseek_repair_success"]["repair_status"])
        self.assertEqual("execution_passed", fixtures["fake_deepseek_repair_success"]["loop_stage"])

        self.assertIn("fake_deepseek_semantic_block", fixtures)
        self.assertEqual("needs_fix", fixtures["fake_deepseek_semantic_block"]["audit_status"])
        self.assertEqual("skipped", fixtures["fake_deepseek_semantic_block"]["execution_smoke_status"])
        self.assertEqual("audit_failed", fixtures["fake_deepseek_semantic_block"]["loop_stage"])
        self.assertTrue(fixtures["fake_deepseek_semantic_block"]["failure_reason"])

        self.assertIn("fake_deepseek_generation_failure", fixtures)
        self.assertEqual("failed", fixtures["fake_deepseek_generation_failure"]["generated_candidate_status"])
        self.assertEqual("skipped", fixtures["fake_deepseek_generation_failure"]["audit_status"])
        self.assertEqual("skipped", fixtures["fake_deepseek_generation_failure"]["execution_smoke_status"])
        self.assertEqual("generation_failed", fixtures["fake_deepseek_generation_failure"]["loop_stage"])
        self.assertTrue(fixtures["fake_deepseek_generation_failure"]["failure_reason"])

        self.assertIn("review_cleanup_provider_quality", fixtures)
        self.assertIn("loop_stage", fixtures["review_cleanup_provider_quality"])
        self.assertTrue(
            isinstance(fixtures["review_cleanup_provider_quality"]["repair_attempted"], bool)
        )
        self.assertTrue(fixtures["review_cleanup_provider_quality"]["failure_reason"])

    def test_provider_quality_evaluation_script_writes_output_file(self) -> None:
        with tempfile.TemporaryDirectory(prefix="provider-quality-eval-") as temp_dir:
            output_path = Path(temp_dir) / "provider-quality-report.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "evaluate_provider_quality.py"),
                    "--output",
                    str(output_path),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                cwd=str(ROOT),
                timeout=120,
                check=False,
            )

            self.assertEqual(0, result.returncode, msg=result.stderr or result.stdout)
            stdout_payload = json.loads(result.stdout)
            self.assertTrue(output_path.exists())
            file_payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(stdout_payload, file_payload)
