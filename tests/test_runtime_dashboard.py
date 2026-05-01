import json
from argparse import Namespace
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch


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
        self.assertIn('<html lang="zh-CN">', html)
        self.assertIn("运行时可观察面板", html)
        self.assertIn("总览", html)
        self.assertIn("技能树视图", html)
        self.assertIn("tree-fan", html)
        self.assertIn("radial-tree", html)
        self.assertIn("radial-center", html)
        self.assertIn("radial-quadrants", html)
        self.assertNotIn("radial-spokes", html)
        self.assertIn("branch-map", html)
        self.assertIn("branch-canopy", html)
        self.assertIn("quadrant-nw", html)
        self.assertIn("quadrant-ne", html)
        self.assertIn("quadrant-sw", html)
        self.assertIn("quadrant-se", html)
        self.assertIn("skill-group", html)
        self.assertIn("group-skill-list", html)
        self.assertIn("group-detail-modal", html)
        self.assertIn("group-detail-surface", html)
        self.assertIn("data-skill-group-modal", html)
        self.assertIn("data-skill-group-target", html)
        self.assertIn("data-skill-group-panel", html)
        self.assertIn("data-skill-group-close", html)
        self.assertIn("setActiveSkillGroup", html)
        self.assertIn("has-skill-group-open", html)
        self.assertIn('event.key === "Escape"', html)
        self.assertNotIn("scrollIntoView", html)
        self.assertIn('data-skill-group="structured-conversion"', html)
        self.assertIn('data-skill-group="text-processing"', html)
        self.assertIn("格式转换", html)
        self.assertIn("文本处理", html)
        self.assertNotIn('<details class="skill-group', html)
        self.assertNotIn('class="skill-leaf"', html)
        self.assertNotIn('class="skill-node"', html)
        self.assertIn("运行时根节点", html)
        self.assertIn("活跃 - 可用技能", html)
        self.assertIn("触发日志视图", html)
        self.assertIn('data-active-view="skill-tree"', html)
        self.assertIn('data-view-target="trigger-log"', html)
        self.assertIn('data-view-page="trigger-log"', html)
        self.assertIn('data-view-target="governance"', html)
        self.assertIn('data-view-page="governance"', html)
        self.assertIn("setDashboardView", html)
        self.assertNotIn('href="#trigger-log-view"', html)
        self.assertIn("治理快照", html)
        self.assertIn("目录 JSON 批量转 CSV", html)
        self.assertIn("将文件夹中的所有 JSON 记录批量导出为 CSV 文件。", html)
        self.assertIn('data-skill-name="directory_json_to_csv_dogfood"', html)
        self.assertIn("合并文本文件", html)
        self.assertNotIn("Batch export all JSON records in a folder into CSV files.", html)

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
        self.assertIn("运行时可观察面板", html)
        self.assertIn("触发日志视图", html)
        self.assertIn("合并文本文件", html)

    def test_dashboard_command_can_open_generated_html(self) -> None:
        from skill_runtime.cli import cmd_dashboard

        output_path = self.runtime_root / ".skill_runtime" / "dashboard.html"
        args = Namespace(root=str(self.runtime_root), output=str(output_path), open=True)
        stdout = StringIO()

        with patch("skill_runtime.cli.webbrowser.open", return_value=True) as open_mock:
            with redirect_stdout(stdout):
                exit_code = cmd_dashboard(args)

        dashboard_url = output_path.resolve().as_uri()
        payload = json.loads(stdout.getvalue())

        self.assertEqual(0, exit_code)
        self.assertEqual("ok", payload["status"])
        self.assertEqual(str(output_path.resolve()), payload["data"]["output_path"])
        self.assertEqual(dashboard_url, payload["data"]["dashboard_url"])
        self.assertTrue(payload["data"]["opened"])
        open_mock.assert_called_once_with(dashboard_url)
