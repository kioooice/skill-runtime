import json
import subprocess
import sys

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
        self.assertEqual("passed", fixtures["demo_local_success"]["generated_candidate_status"])
        self.assertEqual("passed", fixtures["demo_local_success"]["audit_status"])
        self.assertEqual("passed", fixtures["demo_local_success"]["execution_smoke_status"])

        self.assertIn("mock_template_execute_failure", fixtures)
        self.assertEqual("passed", fixtures["mock_template_execute_failure"]["generated_candidate_status"])
        self.assertEqual("needs_fix", fixtures["mock_template_execute_failure"]["audit_status"])
        self.assertEqual("skipped", fixtures["mock_template_execute_failure"]["execution_smoke_status"])
        self.assertTrue(fixtures["mock_template_execute_failure"]["failure_reason"])

        self.assertIn("fake_deepseek_repair_success", fixtures)
        self.assertEqual("passed", fixtures["fake_deepseek_repair_success"]["generated_candidate_status"])
        self.assertTrue(fixtures["fake_deepseek_repair_success"]["repair_attempted"])

        self.assertIn("fake_deepseek_semantic_block", fixtures)
        self.assertEqual("needs_fix", fixtures["fake_deepseek_semantic_block"]["audit_status"])
        self.assertEqual("skipped", fixtures["fake_deepseek_semantic_block"]["execution_smoke_status"])

        self.assertIn("fake_deepseek_generation_failure", fixtures)
        self.assertEqual("failed", fixtures["fake_deepseek_generation_failure"]["generated_candidate_status"])
        self.assertEqual("skipped", fixtures["fake_deepseek_generation_failure"]["audit_status"])
        self.assertEqual("skipped", fixtures["fake_deepseek_generation_failure"]["execution_smoke_status"])
