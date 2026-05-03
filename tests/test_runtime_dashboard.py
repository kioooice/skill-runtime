import json
from argparse import Namespace
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch


class RuntimeDashboardTestsMixin:
    def _write_dashboard_event(
        self,
        project_root,
        *,
        timestamp: str,
        task_description: str,
        runtime_lane_status: str,
        runtime_lane_reason: str,
        selected_skill_name: str | None = None,
        recommended_next_action: str | None = None,
        available_host_operation_labels: list[str] | None = None,
    ) -> None:
        event_dir = project_root / ".skill_runtime"
        event_dir.mkdir(parents=True, exist_ok=True)
        event_path = event_dir / "runtime_lane_events.jsonl"
        event_path.write_text(
            json.dumps(
                {
                    "timestamp": timestamp,
                    "working_directory": str(project_root),
                    "task_description": task_description,
                    "runtime_lane_status": runtime_lane_status,
                    "runtime_lane_reason": runtime_lane_reason,
                    "classification_bucket": "default-in",
                    "reuse_decision": "auto_execute" if runtime_lane_status == "used" else "skip",
                    "learning_decision": "skip",
                    "selected_skill_name": selected_skill_name,
                    "observed_task_record": None,
                    "recommended_next_action": recommended_next_action,
                    "available_host_operation_labels": available_host_operation_labels or [],
                },
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )

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

    def test_dashboard_collector_prefers_active_metadata_when_staging_duplicate_exists(self) -> None:
        from skill_runtime.dashboard.collector import collect_dashboard_data

        duplicate_name = "dashboard_duplicate"
        active_dir = self.runtime_root / "skill_store" / "active"
        staging_dir = self.runtime_root / "skill_store" / "staging"
        active_dir.mkdir(parents=True, exist_ok=True)
        staging_dir.mkdir(parents=True, exist_ok=True)
        base_payload = {
            "skill_name": duplicate_name,
            "file_path": str(active_dir / f"{duplicate_name}.py"),
            "summary": "Active copy",
            "source_trajectory_ids": [],
            "audit_score": 100,
            "usage_count": 0,
            "last_used_at": None,
            "tags": [],
        }
        (active_dir / f"{duplicate_name}.metadata.json").write_text(json.dumps(base_payload), encoding="utf-8")
        staging_payload = dict(base_payload)
        staging_payload["summary"] = "Staging duplicate"
        staging_payload["file_path"] = str(staging_dir / f"{duplicate_name}.py")
        (staging_dir / f"{duplicate_name}.metadata.json").write_text(json.dumps(staging_payload), encoding="utf-8")

        data = collect_dashboard_data(self.runtime_root)
        duplicate = next(skill for skill in data["skills"] if skill["skill_name"] == duplicate_name)

        self.assertEqual("active", duplicate["status"])
        self.assertEqual("Active copy", duplicate["summary"])

    def test_global_dashboard_collector_aggregates_project_events(self) -> None:
        from skill_runtime.dashboard.collector import collect_global_dashboard_data

        workspace_parent = self.runtime_root / "global-workspaces"
        project_alpha = workspace_parent / "alpha"
        project_beta = workspace_parent / "beta"
        self._write_dashboard_event(
            project_alpha,
            timestamp="2026-05-01T12:00:00+00:00",
            task_description="merge alpha notes",
            runtime_lane_status="used",
            runtime_lane_reason="auto-executed reusable skill",
            selected_skill_name="merge_text_files",
        )
        self._write_dashboard_event(
            project_beta,
            timestamp="2026-05-01T13:00:00+00:00",
            task_description="review beta roadmap",
            runtime_lane_status="skipped",
            runtime_lane_reason="kept on normal Codex path",
        )

        data = collect_global_dashboard_data(self.runtime_root, scan_roots=[workspace_parent])

        self.assertEqual(2, data["overview"]["project_count"])
        self.assertEqual(2, data["overview"]["event_count"])
        self.assertEqual({"used": 1, "entered": 0, "skipped": 1}, data["overview"]["recent_event_counts"])
        self.assertEqual(["beta", "alpha"], [project["project_name"] for project in data["projects"]])
        self.assertEqual("beta", data["events"][0]["project_name"])
        self.assertEqual(str(workspace_parent.resolve()), data["scan_roots"][0])

    def test_global_dashboard_renderer_includes_local_and_global_views(self) -> None:
        from skill_runtime.dashboard.collector import collect_dashboard_data, collect_global_dashboard_data
        from skill_runtime.dashboard.render import render_dashboard_html

        workspace_parent = self.runtime_root / "global-render-workspaces"
        project_alpha = workspace_parent / "alpha"
        project_beta = workspace_parent / "beta"
        self._write_dashboard_event(
            project_alpha,
            timestamp="2026-05-01T12:00:00+00:00",
            task_description="merge alpha notes",
            runtime_lane_status="used",
            runtime_lane_reason="auto-executed reusable skill",
            selected_skill_name="merge_text_files",
        )
        self._write_dashboard_event(
            project_beta,
            timestamp="2026-05-01T13:00:00+00:00",
            task_description="review beta roadmap",
            runtime_lane_status="skipped",
            runtime_lane_reason="kept on normal Codex path",
        )

        data = collect_dashboard_data(self.runtime_root)
        data["global"] = collect_global_dashboard_data(self.runtime_root, scan_roots=[workspace_parent])
        html = render_dashboard_html(data)

        self.assertIn("<!doctype html>", html.lower())
        self.assertIn('<html lang="zh-CN">', html)
        self.assertIn("全局运行时观察面板", html)
        self.assertIn("当前项目总览", html)
        self.assertIn("全局总览", html)
        self.assertIn("技能树视图", html)
        self.assertIn("触发日志视图", html)
        self.assertIn("治理快照", html)
        self.assertIn("全局项目概览", html)
        self.assertIn("全局触发日志", html)
        self.assertIn('data-view-target="global-projects"', html)
        self.assertIn('data-view-target="global-log"', html)
        self.assertIn("alpha", html)
        self.assertIn("beta", html)
        self.assertIn("merge alpha notes", html)
        self.assertIn("review beta roadmap", html)
        self.assertIn("普通 Codex 路径", html)

    def test_dashboard_renderer_includes_core_sections(self) -> None:
        from skill_runtime.dashboard.collector import collect_dashboard_data
        from skill_runtime.dashboard.render import render_dashboard_html

        data = collect_dashboard_data(self.runtime_root)
        html = render_dashboard_html(data)

        self.assertIn("<!doctype html>", html.lower())
        self.assertIn('<html lang="zh-CN">', html)
        self.assertIn("运行时可观察面板", html)
        self.assertIn("当前项目总览", html)
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
        self.assertIn("平台与项目", html)
        self.assertIn('data-view-target="platforms"', html)
        self.assertIn('data-view-page="platforms"', html)
        self.assertIn("目录 JSON 批量转 CSV", html)
        self.assertIn("将文件夹中的所有 JSON 记录批量导出为 CSV 文件。", html)
        self.assertIn('data-skill-name="directory_json_to_csv_dogfood"', html)
        self.assertIn("合并文本文件", html)
        self.assertIn("进入 runtime 观察", html)
        self.assertNotIn("Batch export all JSON records in a folder into CSV files.", html)

    def test_dashboard_renderer_shows_runtime_follow_up_actions(self) -> None:
        from skill_runtime.dashboard.collector import collect_dashboard_data
        from skill_runtime.dashboard.render import render_dashboard_html

        self._write_dashboard_event(
            self.runtime_root,
            timestamp="2026-05-03T06:40:00+00:00",
            task_description="capture a reusable workflow",
            runtime_lane_status="used",
            runtime_lane_reason="captured learning payload",
            recommended_next_action="distill_trajectory",
            available_host_operation_labels=[
                "Distill captured trajectory",
                "Promote captured workflow globally",
            ],
        )

        html = render_dashboard_html(collect_dashboard_data(self.runtime_root))

        self.assertIn("下一步：distill_trajectory", html)
        self.assertIn("Promote captured workflow globally", html)

    def test_dashboard_collector_includes_imported_staging_provenance(self) -> None:
        from skill_runtime.dashboard.collector import collect_dashboard_data
        from skill_runtime.importers.local_skill_importer import import_local_skill_to_staging

        source_dir = self.runtime_root / "external-skills" / "dashboard-import"
        source_dir.mkdir(parents=True)
        (source_dir / "SKILL.md").write_text(
            "---\nname: dashboard-import\ndescription: Imported dashboard skill.\n---\n\n# Dashboard Import\n",
            encoding="utf-8",
        )

        result = import_local_skill_to_staging(self.runtime_root, source_dir)
        data = collect_dashboard_data(self.runtime_root)
        imported = next(skill for skill in data["skills"] if skill["skill_name"] == "dashboard-import")

        self.assertEqual("staging", imported["status"])
        self.assertEqual("requires_review", imported["audit_status"])
        self.assertEqual(str(source_dir.resolve()), imported["import_source"])
        self.assertEqual(result["content_hash"], imported["content_hash"])
        self.assertEqual("local_skill_import", imported["provenance"]["type"])
        self.assertTrue(imported["is_imported"])

    def test_dashboard_renderer_shows_imported_candidate_provenance(self) -> None:
        from skill_runtime.dashboard.collector import collect_dashboard_data
        from skill_runtime.dashboard.render import render_dashboard_html
        from skill_runtime.importers.local_skill_importer import import_local_skill_to_staging

        source_dir = self.runtime_root / "external-skills" / "dashboard-import"
        source_dir.mkdir(parents=True)
        (source_dir / "SKILL.md").write_text(
            "---\nname: dashboard-import\ndescription: Imported dashboard skill.\n---\n\n# Dashboard Import\n",
            encoding="utf-8",
        )
        result = import_local_skill_to_staging(self.runtime_root, source_dir)

        html = render_dashboard_html(collect_dashboard_data(self.runtime_root))

        self.assertIn('data-skill-name="dashboard-import"', html)
        self.assertIn("外部导入", html)
        self.assertIn("需要审核", html)
        self.assertIn(str(source_dir.resolve()), html)
        self.assertIn(result["content_hash"][:12], html)

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

    def test_global_dashboard_cli_writes_static_html_file(self) -> None:
        workspace_parent = self.runtime_root / "global-cli-workspaces"
        project_alpha = workspace_parent / "alpha"
        self._write_dashboard_event(
            project_alpha,
            timestamp="2026-05-01T12:00:00+00:00",
            task_description="merge alpha notes",
            runtime_lane_status="used",
            runtime_lane_reason="auto-executed reusable skill",
            selected_skill_name="merge_text_files",
        )
        output_path = self.runtime_root / ".skill_runtime" / "global-dashboard.html"

        payload = self._run_cli(
            "dashboard",
            "--global",
            "--scan-root",
            str(workspace_parent),
            "--output",
            str(output_path),
            expect_json=True,
            root=self.runtime_root,
        )

        self.assertEqual("ok", payload["status"])
        self.assertTrue(payload["data"]["global"])
        self.assertEqual(1, payload["data"]["project_count"])
        self.assertEqual(1, payload["data"]["event_count"])
        self.assertEqual(str(output_path.resolve()), payload["data"]["output_path"])
        self.assertTrue(output_path.exists())
        html = output_path.read_text(encoding="utf-8")
        self.assertIn("全局运行时观察面板", html)
        self.assertIn("当前项目总览", html)
        self.assertIn("全局总览", html)
        self.assertIn("技能树视图", html)
        self.assertIn("触发日志视图", html)
        self.assertIn("治理快照", html)
        self.assertIn("全局项目概览", html)
        self.assertIn("全局触发日志", html)
        self.assertIn("merge alpha notes", html)

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
