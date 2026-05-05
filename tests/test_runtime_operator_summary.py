import hashlib
import json
from pathlib import Path


class RuntimeOperatorSummaryTestsMixin:
    def _operator_status_dir(self) -> Path:
        return self.runtime_root / ".skill_runtime" / "operator_status"

    def _snapshot_paths(self, *paths: Path) -> dict[str, str]:
        snapshot: dict[str, str] = {}
        for base in paths:
            if not base.exists():
                snapshot[str(base)] = "<missing>"
                continue
            if base.is_file():
                snapshot[str(base)] = hashlib.sha256(base.read_bytes()).hexdigest()
                continue
            for child in sorted(path for path in base.rglob("*") if path.is_file()):
                relative = child.relative_to(self.runtime_root)
                snapshot[str(relative)] = hashlib.sha256(child.read_bytes()).hexdigest()
        return snapshot

    def test_operator_summary_cli_returns_parseable_json(self) -> None:
        payload = self._run_cli(
            "operator-summary",
            expect_json=True,
            root=self.runtime_root,
        )

        self.assertEqual("ok", payload["status"])
        self.assertEqual(str(self.runtime_root.resolve()), payload["data"]["root"])
        self.assertIn("generated_at", payload["data"])
        self.assertIn("active_skills", payload["data"])
        self.assertIn("trajectories", payload["data"])
        self.assertIn("safe_next_steps", payload["data"])
        self.assertIn("intentionally_not_automatic", payload["data"])
        self.assertIn("dashboard_export", payload["data"])

    def test_operator_summary_marks_gate_status_unavailable_without_persisted_operator_status(self) -> None:
        payload = self._run_cli(
            "operator-summary",
            expect_json=True,
            root=self.runtime_root,
        )

        quality_gates = payload["data"]["quality_gates"]
        self.assertEqual("unavailable", quality_gates["provider_quality"]["status"])
        self.assertEqual("unavailable", quality_gates["utility_search_quality"]["status"])
        self.assertEqual("unavailable", quality_gates["workflow_search_quality"]["status"])
        self.assertIn("provider_quality", payload["data"]["missing_or_unavailable"])
        self.assertIn("utility_search_quality", payload["data"]["missing_or_unavailable"])
        self.assertIn("workflow_search_quality", payload["data"]["missing_or_unavailable"])

    def test_operator_summary_reads_persisted_operator_status_when_available(self) -> None:
        operator_status_dir = self._operator_status_dir()
        operator_status_dir.mkdir(parents=True, exist_ok=True)
        self._write_json_file(
            operator_status_dir / "provider_quality.json",
            {
                "status": "ok",
                "generated_at": "2026-05-06T10:00:00+00:00",
                "command": "python scripts/evaluate_provider_quality.py --baseline docs/provider-quality-baseline.json --fail-on-regression --write-operator-status",
                "summary": {
                    "fixture_count": 8,
                    "execution_smoke_passed": 4,
                    "fixtures_with_failures": 4,
                },
                "baseline_comparison": {
                    "matched": 8,
                    "regressions": 0,
                    "improvements": 0,
                    "unexpected_failures": 0,
                    "unexpected_passes": 0,
                    "missing_fixtures": 0,
                    "extra_fixtures": 0,
                },
            },
        )
        self._write_json_file(
            operator_status_dir / "search_quality.json",
            {
                "status": "ok",
                "generated_at": "2026-05-06T10:01:00+00:00",
                "command": "python scripts/evaluate_search_quality.py --baseline docs/search-quality-baseline.json --fail-on-regression --write-operator-status",
                "summary": {
                    "query_count": 7,
                    "matched_count": 7,
                    "positive_matched_count": 5,
                    "negative_matched_count": 2,
                },
                "baseline_comparison": {
                    "matched": 7,
                    "regressions": 0,
                    "improvements": 0,
                    "unexpected_failures": 0,
                    "unexpected_passes": 0,
                    "missing_queries": 0,
                    "extra_queries": 0,
                },
            },
        )
        self._write_json_file(
            operator_status_dir / "workflow_search_quality.json",
            {
                "status": "ok",
                "generated_at": "2026-05-06T10:02:00+00:00",
                "command": "python scripts/evaluate_workflow_search_quality.py --baseline docs/workflow-search-quality-baseline.json --fail-on-regression --write-operator-status",
                "summary": {
                    "query_count": 5,
                    "matched_count": 2,
                    "expectation_met_count": 5,
                    "expected_gap_confirmed_count": 2,
                },
                "baseline_comparison": {
                    "matched": 5,
                    "regressions": 0,
                    "improvements": 0,
                    "unexpected_failures": 0,
                    "unexpected_passes": 0,
                    "missing_queries": 0,
                    "extra_queries": 0,
                },
            },
        )

        payload = self._run_cli(
            "operator-summary",
            expect_json=True,
            root=self.runtime_root,
        )

        quality_gates = payload["data"]["quality_gates"]
        self.assertEqual("available", quality_gates["provider_quality"]["status"])
        self.assertEqual("ok", quality_gates["provider_quality"]["report_status"])
        self.assertEqual(8, quality_gates["provider_quality"]["summary"]["fixture_count"])
        self.assertEqual(8, quality_gates["provider_quality"]["baseline_comparison"]["matched"])
        self.assertEqual("available", quality_gates["utility_search_quality"]["status"])
        self.assertEqual(7, quality_gates["utility_search_quality"]["summary"]["matched_count"])
        self.assertEqual("available", quality_gates["workflow_search_quality"]["status"])
        self.assertEqual(5, quality_gates["workflow_search_quality"]["summary"]["expectation_met_count"])
        self.assertEqual([], payload["data"]["missing_or_unavailable"])

    def test_operator_summary_text_reflects_available_operator_status(self) -> None:
        operator_status_dir = self._operator_status_dir()
        operator_status_dir.mkdir(parents=True, exist_ok=True)
        self._write_json_file(
            operator_status_dir / "provider_quality.json",
            {
                "status": "ok",
                "generated_at": "2026-05-06T10:00:00+00:00",
                "command": "python scripts/evaluate_provider_quality.py --write-operator-status",
                "summary": {
                    "fixture_count": 8,
                    "execution_smoke_passed": 4,
                },
                "baseline_comparison": {
                    "matched": 8,
                    "regressions": 0,
                },
            },
        )

        result = self._run_cli(
            "operator-summary",
            "--format",
            "text",
            root=self.runtime_root,
            expect_json=False,
        )

        self.assertIn("provider_quality: available", result.stdout)
        self.assertIn("fixture_count=8", result.stdout)
        self.assertIn("matched=8", result.stdout)

    def test_operator_summary_reports_dashboard_export_status_without_refresh(self) -> None:
        export_path = self.runtime_root / ".skill_runtime" / "dashboard" / "operator-summary.json"
        export_path.parent.mkdir(parents=True, exist_ok=True)
        self._write_json_file(
            export_path,
            {
                "generated_at": "2026-05-06T12:00:00+00:00",
                "freshness_policy": {"basis": "generated_at", "stale_after_seconds": 86400},
                "active_skills": {"count": 14},
                "staging_candidates": {"count": 20},
                "trajectories": {"count": 20},
                "recommended_host_operations": {"count": 0},
                "quality_gates": {
                    "provider_quality": {
                        "label": "provider_quality",
                        "status": "available",
                        "generated_at": "2026-05-06T10:00:00+00:00",
                        "freshness_policy": {"basis": "generated_at", "stale_after_seconds": 259200},
                    },
                    "utility_search_quality": {
                        "label": "utility_search_quality",
                        "status": "available",
                        "generated_at": "2026-05-06T10:01:00+00:00",
                        "freshness_policy": {"basis": "generated_at", "stale_after_seconds": 259200},
                    },
                    "workflow_search_quality": {
                        "label": "workflow_search_quality",
                        "status": "available",
                        "generated_at": "2026-05-06T10:02:00+00:00",
                        "freshness_policy": {"basis": "generated_at", "stale_after_seconds": 259200},
                    },
                },
                "safe_next_steps": [],
                "intentionally_not_automatic": [],
                "missing_or_unavailable": [],
                "non_automatic_explanation": "read-only summary",
            },
        )

        payload = self._run_cli(
            "operator-summary",
            expect_json=True,
            root=self.runtime_root,
        )

        dashboard_export = payload["data"]["dashboard_export"]
        self.assertFalse(dashboard_export["refreshed"])
        self.assertTrue(dashboard_export["available"])
        self.assertEqual("fresh", dashboard_export["freshness_status"])
        self.assertEqual(str(export_path.resolve()), dashboard_export["output_path"])
        self.assertEqual("2026-05-06T12:00:00+00:00", dashboard_export["generated_at"])

    def test_operator_summary_reports_missing_dashboard_export_honestly(self) -> None:
        payload = self._run_cli(
            "operator-summary",
            expect_json=True,
            root=self.runtime_root,
        )

        dashboard_export = payload["data"]["dashboard_export"]
        self.assertFalse(dashboard_export["refreshed"])
        self.assertFalse(dashboard_export["available"])
        self.assertIsNone(dashboard_export["freshness_status"])
        self.assertIsNone(dashboard_export["output_path"])
        self.assertIsNone(dashboard_export["generated_at"])

    def test_operator_summary_can_refresh_dashboard_export_without_rendering_html(self) -> None:
        export_path = self.runtime_root / ".skill_runtime" / "dashboard" / "operator-summary.json"

        payload = self._run_cli(
            "operator-summary",
            "--refresh-dashboard-export",
            expect_json=True,
            root=self.runtime_root,
        )

        dashboard_export = payload["data"]["dashboard_export"]
        self.assertTrue(dashboard_export["refreshed"])
        self.assertTrue(dashboard_export["available"])
        self.assertEqual("fresh", dashboard_export["freshness_status"])
        self.assertEqual(str(export_path.resolve()), dashboard_export["output_path"])
        self.assertTrue(export_path.exists())

    def test_operator_summary_text_reports_dashboard_export_status(self) -> None:
        export_path = self.runtime_root / ".skill_runtime" / "dashboard" / "operator-summary.json"
        export_path.parent.mkdir(parents=True, exist_ok=True)
        self._write_json_file(
            export_path,
            {
                "generated_at": "2026-05-06T12:00:00+00:00",
                "freshness_policy": {"basis": "generated_at", "stale_after_seconds": 86400},
                "active_skills": {"count": 14},
                "staging_candidates": {"count": 20},
                "trajectories": {"count": 20},
                "recommended_host_operations": {"count": 0},
                "quality_gates": {
                    "provider_quality": {
                        "label": "provider_quality",
                        "status": "available",
                        "generated_at": "2026-05-06T10:00:00+00:00",
                        "freshness_policy": {"basis": "generated_at", "stale_after_seconds": 259200},
                    },
                    "utility_search_quality": {
                        "label": "utility_search_quality",
                        "status": "available",
                        "generated_at": "2026-05-06T10:01:00+00:00",
                        "freshness_policy": {"basis": "generated_at", "stale_after_seconds": 259200},
                    },
                    "workflow_search_quality": {
                        "label": "workflow_search_quality",
                        "status": "available",
                        "generated_at": "2026-05-06T10:02:00+00:00",
                        "freshness_policy": {"basis": "generated_at", "stale_after_seconds": 259200},
                    },
                },
                "safe_next_steps": [],
                "intentionally_not_automatic": [],
                "missing_or_unavailable": [],
                "non_automatic_explanation": "read-only summary",
            },
        )

        result = self._run_cli(
            "operator-summary",
            "--format",
            "text",
            root=self.runtime_root,
            expect_json=False,
        )

        self.assertIn("Dashboard export:", result.stdout)
        self.assertIn("available (fresh)", result.stdout)
        self.assertIn(str(export_path.resolve()), result.stdout)

    def test_operator_summary_cli_lists_active_skills(self) -> None:
        payload = self._run_cli(
            "operator-summary",
            expect_json=True,
            root=self.runtime_root,
        )

        active_skills = payload["data"]["active_skills"]
        self.assertGreater(active_skills["count"], 0)
        self.assertTrue(any(item["skill_name"] == "merge_text_files" for item in active_skills["items"]))

    def test_operator_summary_cli_lists_captured_trajectories(self) -> None:
        payload = self._run_cli(
            "operator-summary",
            expect_json=True,
            root=self.runtime_root,
        )

        trajectories = payload["data"]["trajectories"]
        self.assertGreater(trajectories["count"], 0)
        self.assertTrue(any(item["task_id"] == "demo_merge_text_files" for item in trajectories["items"]))

    def test_operator_summary_cli_exposes_recommended_follow_up_without_executing_it(self) -> None:
        self._write_dashboard_event(
            self.runtime_root,
            timestamp="2026-05-06T09:00:00+00:00",
            task_description="capture a reusable workflow",
            runtime_lane_status="used",
            runtime_lane_reason="captured learning payload",
            recommended_next_action="distill_trajectory",
            available_host_operation_labels=[
                "Distill captured trajectory",
                "Promote captured workflow globally",
            ],
        )
        before = self._snapshot_paths(
            self.runtime_root / "skill_store",
            self.runtime_root / "trajectories",
            self.runtime_root / "audits",
            self.runtime_root / "observed_tasks",
            self.runtime_root / ".skill_runtime",
        )

        payload = self._run_cli(
            "operator-summary",
            expect_json=True,
            root=self.runtime_root,
        )

        after = self._snapshot_paths(
            self.runtime_root / "skill_store",
            self.runtime_root / "trajectories",
            self.runtime_root / "audits",
            self.runtime_root / "observed_tasks",
            self.runtime_root / ".skill_runtime",
        )
        self.assertEqual(before, after)

        recommended = payload["data"]["recommended_host_operations"]
        self.assertGreaterEqual(recommended["count"], 1)
        self.assertEqual("distill_trajectory", recommended["items"][0]["recommended_next_action"])
        self.assertIn("Distill captured trajectory", recommended["items"][0]["available_host_operation_labels"])
        self.assertIn("promote_skill", payload["data"]["intentionally_not_automatic"])
        self.assertIn("apply_evolution_candidate", payload["data"]["intentionally_not_automatic"])

    def test_operator_summary_cli_text_output_runs(self) -> None:
        result = self._run_cli(
            "operator-summary",
            "--format",
            "text",
            root=self.runtime_root,
            expect_json=False,
        )

        self.assertIn("Operator Summary", result.stdout)
        self.assertIn("Active skills", result.stdout)
        self.assertIn("Trajectories", result.stdout)
        self.assertIn("Recent runtime events", result.stdout)
        self.assertIn("Recent audits", result.stdout)
        self.assertIn("Quality gates", result.stdout)
        self.assertIn("unavailable", result.stdout)
        self.assertIn("Boundary:", result.stdout)
