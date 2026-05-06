import json
import subprocess
import sys
from pathlib import Path

from tests.runtime_test_support import ROOT


class RuntimeDashboardOperatorSummaryExportTestsMixin:
    def _run_operator_summary_export(
        self,
        *,
        root: Path | None = None,
        output: Path | None = None,
    ) -> tuple[dict, Path]:
        runtime_root = self._default_root(root)
        script = ROOT / "scripts" / "export_operator_summary_for_dashboard.py"
        command = [sys.executable, str(script), "--root", str(runtime_root)]
        if output is not None:
            command.extend(["--output", str(output)])

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        self.assertEqual(0, result.returncode, msg=result.stderr or result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual("ok", payload["status"])
        output_path = Path(payload["data"]["output_path"])
        self.assertTrue(output_path.exists())
        return payload, output_path

    def test_dashboard_operator_summary_export_writes_parseable_json_with_stable_fields(self) -> None:
        payload, output_path = self._run_operator_summary_export(root=self.runtime_root)
        exported = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual(
            str((self.runtime_root / ".skill_runtime" / "dashboard" / "operator-summary.json").resolve()),
            payload["data"]["output_path"],
        )
        self.assertEqual(
            {
                "generated_at",
                "freshness_policy",
                "active_skills",
                "staging_candidates",
                "trajectories",
                "recommended_host_operations",
                "quality_gates",
                "safe_next_steps",
                "intentionally_not_automatic",
                "missing_or_unavailable",
                "non_automatic_explanation",
            },
            set(exported.keys()),
        )
        self.assertEqual({"count"}, set(exported["active_skills"].keys()))
        self.assertEqual({"count"}, set(exported["staging_candidates"].keys()))
        self.assertEqual({"count"}, set(exported["trajectories"].keys()))
        self.assertEqual({"count"}, set(exported["recommended_host_operations"].keys()))
        self.assertEqual("generated_at", exported["freshness_policy"]["basis"])
        self.assertIsInstance(exported["freshness_policy"]["stale_after_seconds"], int)
        self.assertIn("provider_quality", exported["quality_gates"])
        self.assertIn("utility_search_quality", exported["quality_gates"])
        self.assertIn("workflow_search_quality", exported["quality_gates"])
        self.assertEqual(
            "generated_at",
            exported["quality_gates"]["provider_quality"]["freshness_policy"]["basis"],
        )
        self.assertIsInstance(
            exported["quality_gates"]["provider_quality"]["freshness_policy"]["stale_after_seconds"],
            int,
        )

    def test_dashboard_operator_summary_export_keeps_gate_status_unavailable_without_persisted_reports(self) -> None:
        operator_status_dir = self.runtime_root / ".skill_runtime" / "operator_status"

        _, output_path = self._run_operator_summary_export(root=self.runtime_root)
        exported = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertFalse(operator_status_dir.exists())
        self.assertEqual("unavailable", exported["quality_gates"]["provider_quality"]["status"])
        self.assertEqual("unavailable", exported["quality_gates"]["utility_search_quality"]["status"])
        self.assertEqual("unavailable", exported["quality_gates"]["workflow_search_quality"]["status"])
        self.assertIn("provider_quality", exported["missing_or_unavailable"])
        self.assertIn("utility_search_quality", exported["missing_or_unavailable"])
        self.assertIn("workflow_search_quality", exported["missing_or_unavailable"])

    def test_dashboard_operator_summary_export_reads_fake_persisted_gate_status(self) -> None:
        operator_status_dir = self.runtime_root / ".skill_runtime" / "operator_status"
        operator_status_dir.mkdir(parents=True, exist_ok=True)
        self._write_json_file(
            operator_status_dir / "provider_quality.json",
            {
                "status": "ok",
                "generated_at": "2026-05-06T10:00:00+00:00",
                "command": "python scripts/evaluate_provider_quality.py --write-operator-status",
                "summary": {"fixture_count": 8, "execution_smoke_passed": 4},
                "baseline_comparison": {"matched": 8, "regressions": 0},
            },
        )
        self._write_json_file(
            operator_status_dir / "search_quality.json",
            {
                "status": "ok",
                "generated_at": "2026-05-06T10:01:00+00:00",
                "command": "python scripts/evaluate_search_quality.py --write-operator-status",
                "summary": {"query_count": 7, "matched_count": 7},
                "baseline_comparison": {"matched": 7, "regressions": 0},
            },
        )
        self._write_json_file(
            operator_status_dir / "workflow_search_quality.json",
            {
                "status": "ok",
                "generated_at": "2026-05-06T10:02:00+00:00",
                "command": "python scripts/evaluate_workflow_search_quality.py --write-operator-status",
                "summary": {"query_count": 6, "expectation_met_count": 6},
                "baseline_comparison": {"matched": 6, "regressions": 0},
            },
        )

        _, output_path = self._run_operator_summary_export(root=self.runtime_root)
        exported = json.loads(output_path.read_text(encoding="utf-8"))

        self.assertEqual("available", exported["quality_gates"]["provider_quality"]["status"])
        self.assertEqual("ok", exported["quality_gates"]["provider_quality"]["report_status"])
        self.assertEqual(8, exported["quality_gates"]["provider_quality"]["summary"]["fixture_count"])
        self.assertEqual("available", exported["quality_gates"]["utility_search_quality"]["status"])
        self.assertEqual("available", exported["quality_gates"]["workflow_search_quality"]["status"])
        self.assertEqual([], exported["missing_or_unavailable"])

    def test_dashboard_operator_summary_export_is_read_only_for_skill_store_and_dashboard_html(self) -> None:
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
        )

        _, output_path = self._run_operator_summary_export(root=self.runtime_root)
        exported = json.loads(output_path.read_text(encoding="utf-8"))

        after = self._snapshot_paths(
            self.runtime_root / "skill_store",
            self.runtime_root / "trajectories",
            self.runtime_root / "audits",
            self.runtime_root / "observed_tasks",
        )
        self.assertEqual(before, after)
        self.assertGreaterEqual(exported["recommended_host_operations"]["count"], 1)
        self.assertIn("promote_skill", exported["intentionally_not_automatic"])
        self.assertIn("apply_evolution_candidate", exported["intentionally_not_automatic"])
        self.assertFalse((self.runtime_root / ".skill_runtime" / "dashboard.html").exists())
        self.assertFalse((self.runtime_root / ".skill_runtime" / "global-dashboard.html").exists())
