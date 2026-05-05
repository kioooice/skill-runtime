import json
import subprocess
import sys

from scripts.evaluate_workflow_search_quality import evaluate
from tests.runtime_test_support import ROOT


class RuntimeWorkflowSearchQualityTestsMixin:
    def test_workflow_search_quality_report_contains_required_fields(self) -> None:
        payload = evaluate(self.runtime_root)

        self.assertEqual("ok", payload["status"])
        self.assertTrue(payload["fixture_skills"])
        self.assertTrue(payload["queries"])
        self.assertIn("summary", payload)
        for item in payload["queries"]:
            self.assertIn("query_id", item)
            self.assertIn("query", item)
            self.assertIn("query_type", item)
            self.assertIn("expectation_mode", item)
            self.assertIn("expected_top_skill", item)
            self.assertIn("expected_skills", item)
            self.assertIn("actual_top_skill", item)
            self.assertIn("actual_recommended_skill", item)
            self.assertIn("matched", item)
            self.assertIn("expectation_met", item)
            self.assertIn("failure_reason", item)
            self.assertIn("rank_diagnostics", item)
            self.assertIn("top_results", item)

    def test_workflow_search_quality_matches_at_least_one_positive_query(self) -> None:
        payload = evaluate(self.runtime_root)
        positive_queries = [
            item for item in payload["queries"] if item["query_type"].startswith("positive_")
        ]

        self.assertTrue(positive_queries)
        self.assertTrue(any(item["matched"] for item in positive_queries), payload)

    def test_workflow_search_quality_negative_utility_query_is_not_fake_workflow_pass(self) -> None:
        payload = evaluate(self.runtime_root)
        negative_query = next(
            item for item in payload["queries"] if item["query_id"] == "negative_utility_merge_markdown"
        )

        self.assertEqual("negative_utility_query", negative_query["query_type"])
        self.assertEqual("should_not_match", negative_query["expectation_mode"])
        self.assertFalse(negative_query["matched"])
        self.assertTrue(negative_query["expectation_met"])
        self.assertIsNone(negative_query["actual_recommended_skill"])

    def test_workflow_search_quality_script_runs(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "evaluate_workflow_search_quality.py"),
            ],
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

    def test_workflow_search_quality_script_compares_machine_readable_baseline(self) -> None:
        baseline_path = ROOT / "docs" / "workflow-search-quality-baseline.json"
        baseline_payload = json.loads(baseline_path.read_text(encoding="utf-8"))

        self.assertIn("queries", baseline_payload)
        self.assertTrue(baseline_payload["queries"])
        for query in baseline_payload["queries"]:
            self.assertIn("query_id", query)
            self.assertIn("query_type", query)
            self.assertIn("expectation_mode", query)
            self.assertIn("expected_top_skill", query)
            self.assertIn("expected_matched", query)
            self.assertIn("expected_expectation_met", query)
            self.assertIn("expected_recommended_skill", query)

        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "evaluate_workflow_search_quality.py"),
                "--baseline",
                str(baseline_path),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=str(ROOT),
            timeout=120,
            check=False,
        )

        self.assertEqual(0, result.returncode, msg=result.stderr or result.stdout)
        payload = json.loads(result.stdout)
        comparison = payload["baseline_comparison"]
        self.assertEqual(5, len(comparison["matched"]))
        self.assertEqual([], comparison["regressions"])
        self.assertEqual([], comparison["improvements"])
        self.assertEqual([], comparison["unexpected_failures"])
        self.assertEqual([], comparison["unexpected_passes"])
        self.assertEqual([], comparison["missing_queries"])
        self.assertEqual([], comparison["extra_queries"])

    def test_workflow_search_quality_fail_on_regression_passes_for_current_baseline(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "evaluate_workflow_search_quality.py"),
                "--baseline",
                str(ROOT / "docs" / "workflow-search-quality-baseline.json"),
                "--fail-on-regression",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=str(ROOT),
            timeout=120,
            check=False,
        )

        self.assertEqual(0, result.returncode, msg=result.stderr or result.stdout)
