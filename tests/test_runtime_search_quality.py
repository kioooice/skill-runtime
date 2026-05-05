import json
import subprocess
import sys
import tempfile
from pathlib import Path

from scripts.evaluate_search_quality import evaluate
from tests.runtime_test_support import ROOT


class RuntimeSearchQualityTestsMixin:
    def test_active_skill_search_quality_report_contains_required_fields(self) -> None:
        payload = evaluate(self.runtime_root)

        self.assertEqual("ok", payload["status"])
        self.assertTrue(payload["fixture_skills"])
        self.assertTrue(payload["queries"])
        self.assertIn("summary", payload)
        for item in payload["queries"]:
            self.assertIn("query_id", item)
            self.assertIn("query", item)
            self.assertIn("expected_top_skill", item)
            self.assertIn("expected_skills", item)
            self.assertIn("actual_top_skill", item)
            self.assertIn("matched", item)
            self.assertIn("top_k", item)
            self.assertIn("failure_reason", item)
            self.assertIn("rank_diagnostics", item)
            self.assertIn("top_results", item)

    def test_active_skill_search_quality_matches_at_least_one_positive_query(self) -> None:
        payload = evaluate(self.runtime_root)
        positive_queries = [item for item in payload["queries"] if item["expected_top_skill"]]

        self.assertTrue(positive_queries)
        self.assertTrue(any(item["matched"] for item in positive_queries), payload)
        chinese_query = next(item for item in payload["queries"] if item["query_id"] == "chinese_merge_query")
        self.assertTrue(chinese_query["matched"], payload)
        self.assertEqual("merge_text_files", chinese_query["actual_recommended_skill"])

    def test_active_skill_search_quality_negative_query_is_not_fake_pass(self) -> None:
        payload = evaluate(self.runtime_root)
        negative_queries = [
            item
            for item in payload["queries"]
            if item["query_id"] in {"negative_email_newsletter", "negative_chinese_email_campaign"}
        ]

        self.assertEqual(2, len(negative_queries))
        for negative_query in negative_queries:
            self.assertIsNone(negative_query["expected_top_skill"])
            if negative_query["matched"]:
                self.assertIsNone(negative_query["actual_recommended_skill"])
            else:
                self.assertTrue(negative_query["failure_reason"])

    def test_search_quality_evaluation_script_compares_machine_readable_baseline(self) -> None:
        baseline_path = ROOT / "docs" / "search-quality-baseline.json"
        baseline_payload = json.loads(baseline_path.read_text(encoding="utf-8"))

        self.assertIn("queries", baseline_payload)
        self.assertTrue(baseline_payload["queries"])
        for query in baseline_payload["queries"]:
            self.assertIn("query_id", query)
            self.assertIn("expected_top_skill", query)
            self.assertIn("expected_matched", query)
            self.assertIn("expected_recommended_skill", query)
            self.assertIn("query_type", query)

        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "evaluate_search_quality.py"),
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
        self.assertEqual(7, len(comparison["matched"]))
        self.assertEqual([], comparison["regressions"])
        self.assertEqual([], comparison["improvements"])
        self.assertEqual([], comparison["unexpected_failures"])
        self.assertEqual([], comparison["unexpected_passes"])
        self.assertEqual([], comparison["missing_queries"])
        self.assertEqual([], comparison["extra_queries"])

    def test_search_quality_fail_on_regression_passes_for_current_baseline(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "evaluate_search_quality.py"),
                "--baseline",
                str(ROOT / "docs" / "search-quality-baseline.json"),
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

    def test_search_quality_evaluation_script_detects_bad_baseline(self) -> None:
        with tempfile.TemporaryDirectory(prefix="search-quality-baseline-") as temp_dir:
            baseline_path = Path(temp_dir) / "bad-baseline.json"
            baseline_path.write_text(
                json.dumps(
                    {
                        "queries": [
                            {
                                "query_id": "fuzzy_merge_english",
                                "expected_top_skill": None,
                                "expected_matched": True,
                                "expected_recommended_skill": None,
                                "query_type": "negative_no_strong_match",
                            }
                        ]
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "evaluate_search_quality.py"),
                    "--baseline",
                    str(baseline_path),
                    "--fail-on-regression",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                cwd=str(ROOT),
                timeout=120,
                check=False,
            )

        self.assertNotEqual(0, result.returncode)
        payload = json.loads(result.stdout)
        comparison = payload["baseline_comparison"]
        self.assertEqual([], comparison["matched"])
        self.assertTrue(comparison["unexpected_failures"])
        self.assertTrue(comparison["extra_queries"])
