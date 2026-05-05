import hashlib
import json
from pathlib import Path


class RuntimeOperatorSummaryTestsMixin:
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
        self.assertIn("Boundary:", result.stdout)
