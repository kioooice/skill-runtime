import json


class RuntimeDashboardTestsMixin:
    def test_dashboard_collector_handles_empty_runtime_root(self) -> None:
        from skill_runtime.dashboard.collector import collect_dashboard_data

        empty_root = self.runtime_root / "empty-dashboard-root"
        empty_root.mkdir()

        data = collect_dashboard_data(empty_root)

        self.assertEqual(0, data["overview"]["active_count"])
        self.assertEqual(0, data["overview"]["staging_count"])
        self.assertEqual(0, data["overview"]["archive_count"])
        self.assertEqual(0, data["overview"]["rejected_count"])
        self.assertEqual([], data["skills"])
        self.assertEqual([], data["events"])
        self.assertTrue(data["diagnostics"])

    def test_dashboard_collector_reads_skills_and_runtime_lane_events(self) -> None:
        from skill_runtime.dashboard.collector import collect_dashboard_data

        event_dir = self.runtime_root / ".skill_runtime"
        event_dir.mkdir(parents=True, exist_ok=True)
        event_path = event_dir / "runtime_lane_events.jsonl"
        event_path.write_text(
            json.dumps(
                {
                    "timestamp": "2026-05-01T12:00:00+00:00",
                    "working_directory": str(self.runtime_root),
                    "task_description": "merge txt files into markdown",
                    "runtime_lane_status": "used",
                    "runtime_lane_reason": "auto-executed reusable skill",
                    "classification_bucket": "default-in",
                    "reuse_decision": "auto_execute",
                    "learning_decision": "skip",
                    "selected_skill_name": "merge_text_files",
                    "observed_task_record": None,
                },
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )

        data = collect_dashboard_data(self.runtime_root)

        self.assertGreaterEqual(data["overview"]["active_count"], 1)
        self.assertEqual({"used": 1, "entered": 0, "skipped": 0}, data["overview"]["recent_event_counts"])
        self.assertTrue(any(skill["skill_name"] == "merge_text_files" for skill in data["skills"]))
        self.assertEqual("used", data["events"][0]["runtime_lane_status"])

    def test_dashboard_renderer_includes_core_sections(self) -> None:
        from skill_runtime.dashboard.collector import collect_dashboard_data
        from skill_runtime.dashboard.render import render_dashboard_html

        data = collect_dashboard_data(self.runtime_root)
        html = render_dashboard_html(data)

        self.assertIn("<!doctype html>", html.lower())
        self.assertIn("Runtime Observability Dashboard", html)
        self.assertIn("Overview", html)
        self.assertIn("Skill Tree", html)
        self.assertIn("Trigger Log", html)
        self.assertIn("Governance Snapshot", html)
        self.assertIn("merge_text_files", html)

    def test_dashboard_cli_writes_static_html_file(self) -> None:
        output_path = self.runtime_root / ".skill_runtime" / "dashboard.html"

        payload = self._run_cli(
            "dashboard",
            "--output",
            str(output_path),
            expect_json=True,
            root=self.runtime_root,
        )

        self.assertEqual("ok", payload["status"])
        self.assertEqual(str(output_path.resolve()), payload["data"]["output_path"])
        self.assertTrue(output_path.exists())
        html = output_path.read_text(encoding="utf-8")
        self.assertIn("Runtime Observability Dashboard", html)
        self.assertIn("Trigger Log", html)
