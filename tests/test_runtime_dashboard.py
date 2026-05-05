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

        workflow_active_count = sum(
            1 for skill in data["skills"] if skill["status"] == "active" and skill["skill_surface"] == "workflow"
        )
        self.assertEqual(workflow_active_count, data["overview"]["active_count"])
        self.assertEqual({"used": 1, "entered": 0, "skipped": 0}, data["overview"]["recent_event_counts"])
        self.assertTrue(any(skill["skill_name"] == "merge_text_files" for skill in data["skills"]))
        self.assertEqual("used", data["events"][0]["runtime_lane_status"])
        merge_skill = next(skill for skill in data["skills"] if skill["skill_name"] == "merge_text_files")
        workflow_skill = next(
            skill for skill in data["skills"] if skill["skill_name"] == "pre_implementation_workflow_review"
        )
        self.assertEqual("basic", merge_skill["skill_surface"])
        self.assertEqual("workflow", workflow_skill["skill_surface"])

    def test_dashboard_collector_reads_exported_operator_summary_when_available(self) -> None:
        from skill_runtime.dashboard.collector import collect_dashboard_data

        export_dir = self.runtime_root / ".skill_runtime" / "dashboard"
        export_dir.mkdir(parents=True, exist_ok=True)
        (export_dir / "operator-summary.json").write_text(
            json.dumps(
                {
                    "generated_at": "2026-05-06T12:00:00+00:00",
                    "freshness_policy": {"basis": "generated_at", "stale_after_seconds": 86400},
                    "active_skills": {"count": 14},
                    "staging_candidates": {"count": 20},
                    "trajectories": {"count": 20},
                    "recommended_host_operations": {"count": 1},
                    "quality_gates": {
                        "provider_quality": {
                            "label": "provider_quality",
                            "status": "available",
                            "generated_at": "2026-05-06T11:30:00+00:00",
                            "freshness_policy": {"basis": "generated_at", "stale_after_seconds": 259200},
                        },
                        "utility_search_quality": {
                            "label": "utility_search_quality",
                            "status": "available",
                            "generated_at": "2026-05-06T11:35:00+00:00",
                            "freshness_policy": {"basis": "generated_at", "stale_after_seconds": 259200},
                        },
                        "workflow_search_quality": {
                            "label": "workflow_search_quality",
                            "status": "unavailable",
                            "freshness_policy": {"basis": "generated_at", "stale_after_seconds": 259200},
                        },
                    },
                    "safe_next_steps": [{"action": "distill_trajectory", "automatic": False, "reason": "explicit"}],
                    "intentionally_not_automatic": ["promote_skill", "apply_evolution_candidate"],
                    "missing_or_unavailable": ["workflow_search_quality"],
                    "non_automatic_explanation": "read-only export",
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        data = collect_dashboard_data(self.runtime_root)

        self.assertIn("operator_summary", data)
        self.assertEqual("2026-05-06T12:00:00+00:00", data["operator_summary"]["generated_at"])
        self.assertEqual(14, data["operator_summary"]["active_skills"]["count"])
        self.assertEqual("available", data["operator_summary"]["quality_gates"]["provider_quality"]["status"])
        self.assertEqual("fresh", data["operator_summary"]["freshness"]["status"])
        self.assertEqual("fresh", data["operator_summary"]["quality_gates"]["provider_quality"]["freshness"]["status"])
        self.assertIn("workflow_search_quality", data["operator_summary"]["missing_or_unavailable"])

    def test_dashboard_collector_marks_exported_operator_summary_stale_when_generated_at_is_old(self) -> None:
        from skill_runtime.dashboard.collector import collect_dashboard_data

        export_dir = self.runtime_root / ".skill_runtime" / "dashboard"
        export_dir.mkdir(parents=True, exist_ok=True)
        (export_dir / "operator-summary.json").write_text(
            json.dumps(
                {
                    "generated_at": "2026-05-01T12:00:00+00:00",
                    "freshness_policy": {"basis": "generated_at", "stale_after_seconds": 3600},
                    "active_skills": {"count": 14},
                    "staging_candidates": {"count": 20},
                    "trajectories": {"count": 20},
                    "recommended_host_operations": {"count": 1},
                    "quality_gates": {
                        "provider_quality": {
                            "label": "provider_quality",
                            "status": "available",
                            "generated_at": "2026-05-01T12:00:00+00:00",
                            "freshness_policy": {"basis": "generated_at", "stale_after_seconds": 3600},
                        },
                        "utility_search_quality": {
                            "label": "utility_search_quality",
                            "status": "available",
                            "generated_at": "2026-05-06T11:45:00+00:00",
                            "freshness_policy": {"basis": "generated_at", "stale_after_seconds": 86400},
                        },
                        "workflow_search_quality": {
                            "label": "workflow_search_quality",
                            "status": "unavailable",
                            "freshness_policy": {"basis": "generated_at", "stale_after_seconds": 86400},
                        },
                    },
                    "safe_next_steps": [],
                    "intentionally_not_automatic": ["promote_skill", "apply_evolution_candidate"],
                    "missing_or_unavailable": ["workflow_search_quality"],
                    "non_automatic_explanation": "read-only export",
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        data = collect_dashboard_data(self.runtime_root)

        self.assertEqual("stale", data["operator_summary"]["freshness"]["status"])
        self.assertEqual("stale", data["operator_summary"]["quality_gates"]["provider_quality"]["freshness"]["status"])
        self.assertEqual("fresh", data["operator_summary"]["quality_gates"]["utility_search_quality"]["freshness"]["status"])
        self.assertEqual(
            "unknown",
            data["operator_summary"]["quality_gates"]["workflow_search_quality"]["freshness"]["status"],
        )

    def test_dashboard_collector_leaves_operator_summary_empty_without_export(self) -> None:
        from skill_runtime.dashboard.collector import collect_dashboard_data

        data = collect_dashboard_data(self.runtime_root)

        self.assertIn("operator_summary", data)
        self.assertIsNone(data["operator_summary"])

    def test_dashboard_trigger_log_keeps_used_and_entered_when_recent_events_are_skipped(self) -> None:
        from skill_runtime.dashboard.collector import collect_dashboard_data
        from skill_runtime.dashboard.render import render_dashboard_html

        event_dir = self.runtime_root / ".skill_runtime"
        event_dir.mkdir(parents=True, exist_ok=True)
        event_path = event_dir / "runtime_lane_events.jsonl"
        rows = [
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
            {
                "timestamp": "2026-05-01T12:01:00+00:00",
                "working_directory": str(self.runtime_root),
                "task_description": "capture shared payload workflow",
                "runtime_lane_status": "entered",
                "runtime_lane_reason": "default lane observation",
                "classification_bucket": "default-in",
                "reuse_decision": "skip",
                "learning_decision": None,
                "selected_skill_name": None,
                "observed_task_record": None,
            },
        ]
        for index in range(5):
            rows.append(
                {
                    "timestamp": f"2026-05-01T12:1{index}:00+00:00",
                    "working_directory": str(self.runtime_root),
                    "task_description": f"skipped task {index}",
                    "runtime_lane_status": "skipped",
                    "runtime_lane_reason": "kept on normal Codex path",
                    "classification_bucket": "default-out",
                    "reuse_decision": "skip",
                    "learning_decision": None,
                    "selected_skill_name": None,
                    "observed_task_record": None,
                }
            )
        event_path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + "\n", encoding="utf-8")

        data = collect_dashboard_data(self.runtime_root, event_limit=3)
        html = render_dashboard_html(data)

        self.assertEqual({"used": 1, "entered": 1, "skipped": 5}, data["overview"]["recent_event_counts"])
        self.assertIn('data-event-status="used"', html)
        self.assertIn('data-event-status="entered"', html)
        self.assertIn('data-event-status="skipped"', html)
        self.assertIn("已使用 <span>1</span>", html)
        self.assertIn("进入观察 <span>1</span>", html)
        self.assertIn("已跳过 <span>5</span>", html)
        self.assertNotIn("暂无已使用记录。", html)
        self.assertNotIn("暂无进入观察记录。", html)

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

    def test_global_dashboard_collector_reads_project_operator_summary_metadata(self) -> None:
        from skill_runtime.dashboard.collector import collect_global_dashboard_data

        workspace_parent = self.runtime_root / "global-operator-summary-workspaces"
        project_alpha = workspace_parent / "alpha"
        self._write_dashboard_event(
            project_alpha,
            timestamp="2026-05-01T12:00:00+00:00",
            task_description="merge alpha notes",
            runtime_lane_status="used",
            runtime_lane_reason="auto-executed reusable skill",
            selected_skill_name="merge_text_files",
        )
        export_dir = project_alpha / ".skill_runtime" / "dashboard"
        export_dir.mkdir(parents=True, exist_ok=True)
        (export_dir / "operator-summary.json").write_text(
            json.dumps(
                {
                    "generated_at": "2026-05-06T12:05:00+00:00",
                    "freshness_policy": {"basis": "generated_at", "stale_after_seconds": 86400},
                    "active_skills": {"count": 8},
                    "staging_candidates": {"count": 3},
                    "trajectories": {"count": 11},
                    "recommended_host_operations": {"count": 0},
                    "quality_gates": {
                        "provider_quality": {
                            "label": "provider_quality",
                            "status": "available",
                            "generated_at": "2026-05-06T12:04:00+00:00",
                            "freshness_policy": {"basis": "generated_at", "stale_after_seconds": 259200},
                        },
                        "utility_search_quality": {
                            "label": "utility_search_quality",
                            "status": "available",
                            "generated_at": "2026-05-01T12:04:00+00:00",
                            "freshness_policy": {"basis": "generated_at", "stale_after_seconds": 3600},
                        },
                        "workflow_search_quality": {
                            "label": "workflow_search_quality",
                            "status": "available",
                            "generated_at": "2026-05-06T12:03:00+00:00",
                            "freshness_policy": {"basis": "generated_at", "stale_after_seconds": 259200},
                        },
                    },
                    "safe_next_steps": [],
                    "intentionally_not_automatic": ["promote_skill"],
                    "missing_or_unavailable": [],
                    "non_automatic_explanation": "read-only export",
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        data = collect_global_dashboard_data(self.runtime_root, scan_roots=[workspace_parent])

        alpha = next(project for project in data["projects"] if project["project_name"] == "alpha")
        self.assertTrue(alpha["operator_summary_available"])
        self.assertEqual("2026-05-06T12:05:00+00:00", alpha["operator_summary_generated_at"])
        self.assertEqual("fresh", alpha["operator_summary_freshness_status"])
        self.assertEqual("available", alpha["operator_quality_gate_statuses"]["provider_quality"])
        self.assertEqual("fresh", alpha["operator_quality_gate_freshness_statuses"]["provider_quality"])
        self.assertEqual("stale", alpha["operator_quality_gate_freshness_statuses"]["utility_search_quality"])

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
        project_gamma = workspace_parent / "gamma"
        self._write_dashboard_event(
            project_gamma,
            timestamp="2026-05-01T14:00:00+00:00",
            task_description="capture shared payload workflow",
            runtime_lane_status="entered",
            runtime_lane_reason="default lane observation",
        )

        data = collect_dashboard_data(self.runtime_root)
        data["global"] = collect_global_dashboard_data(self.runtime_root, scan_roots=[workspace_parent])
        html = render_dashboard_html(data)

        self.assertIn("<!doctype html>", html.lower())
        self.assertIn('<html lang="zh-CN">', html)
        self.assertIn("全局运行时总览", html)
        self.assertIn("当前项目", html)
        self.assertIn("跨工作区", html)
        self.assertIn('data-view-target="overview"', html)
        self.assertIn('data-view-page="overview"', html)
        self.assertIn("中央技能库", html)
        self.assertIn("触发日志", html)
        self.assertIn("治理快照", html)
        self.assertIn("全局项目", html)
        self.assertIn('data-view-target="global-projects"', html)
        self.assertNotIn("全局日志", html)
        self.assertNotIn('data-view-target="global-log"', html)
        self.assertNotIn('data-view-page="global-log"', html)
        self.assertNotIn("跨工作区调用记录已合并", html)
        self.assertIn("alpha", html)
        self.assertIn("beta", html)
        self.assertIn("gamma", html)
        self.assertIn("任务：合并 alpha 笔记", html)
        self.assertIn("任务：评审 beta 路线", html)
        self.assertIn("任务：记录共享工作流", html)
        self.assertIn("处理方式：普通 Codex 处理", html)
        self.assertIn("处理方式：合并文本文件", html)
        self.assertIn("处理方式：运行时观察", html)
        self.assertIn("结果：运行时已参与处理，并复用了匹配技能。", html)
        self.assertIn("结果：任务已进入运行时观察，但没有自动接管。", html)
        self.assertIn("结果：Codex 直接处理，运行时没有接管。", html)
        self.assertNotIn("kept on normal Codex path", html)
        self.assertNotIn("auto-executed reusable skill", html)
        self.assertIn('data-active-event-filter="used"', html)
        self.assertIn('data-event-filter="used"', html)
        self.assertIn('data-event-filter="entered"', html)
        self.assertIn('data-event-filter="skipped"', html)
        self.assertIn('data-event-status="used"', html)
        self.assertIn('data-event-status="entered"', html)
        self.assertIn('data-event-status="skipped"', html)
        self.assertIn("进入观察", html)
        self.assertIn("setEventFilter", html)

    def test_dashboard_renderer_includes_core_sections(self) -> None:
        from skill_runtime.dashboard.collector import collect_dashboard_data
        from skill_runtime.dashboard.render import render_dashboard_html

        data = collect_dashboard_data(self.runtime_root)
        html = render_dashboard_html(data)

        self.assertIn("<!doctype html>", html.lower())
        self.assertIn('<html lang="zh-CN">', html)
        self.assertIn("运行时总览", html)
        self.assertIn("当前项目", html)
        self.assertNotIn("候选 - 候选技能", html)
        self.assertIn('data-view-header="overview"', html)
        self.assertIn('data-view-header="skill-tree"', html)
        self.assertIn('data-view-header="skill-evolution"', html)
        self.assertNotIn('data-view-header="collections"', html)
        self.assertEqual(0, html.count('class="search-row"'))
        self.assertNotIn("搜索当前视图", html)
        self.assertIn('data-view-target="overview"', html)
        self.assertIn('data-view-page="overview"', html)
        self.assertIn("overview-section", html)
        self.assertIn("skills-runtime", html)
        self.assertIn("desktop-shell", html)
        self.assertIn("topbar", html)
        self.assertNotIn("traffic-lights", html)
        self.assertNotIn("topbar-title", html)
        self.assertIn("global-search", html)
        self.assertIn("sidebar", html)
        self.assertIn("sidebar-settings", html)
        self.assertIn("中央技能库", html)
        self.assertIn("按功能分组查看工作流技能", html)
        self.assertNotIn('data-view-target="collections"', html)
        self.assertNotIn('data-view-page="collections"', html)
        self.assertNotIn("技能集合", html)
        self.assertIn("collection-grid", html)
        self.assertIn("collection-card", html)
        self.assertIn("方向与策略", html)
        self.assertIn("自动推进", html)
        self.assertIn("运行时与验证", html)
        self.assertIn("会话接续", html)
        self.assertIn("platform-row", html)
        self.assertIn("JetBrains Mono", html)
        self.assertIn("#eff1f5", html)
        self.assertIn("#7e3ee6", html)
        self.assertNotIn("默认技能树只展示工作流技能", html)
        self.assertNotIn("基础本地技能", html)
        self.assertNotIn("tree-fan", html)
        self.assertNotIn("radial-tree", html)
        self.assertNotIn("radial-center", html)
        self.assertNotIn("radial-quadrants", html)
        self.assertNotIn("branch-map", html)
        self.assertNotIn("branch-canopy", html)
        self.assertNotIn("data-skill-group-modal", html)
        self.assertNotIn("data-skill-group-target", html)
        self.assertNotIn("setActiveSkillGroup", html)
        self.assertNotIn("scrollIntoView", html)
        self.assertNotIn('data-skill-group="structured-conversion"', html)
        self.assertNotIn('data-skill-group="text-processing"', html)
        self.assertNotIn('<details class="skill-group', html)
        self.assertNotIn('class="skill-leaf"', html)
        self.assertNotIn('class="skill-node"', html)
        self.assertNotIn("运行时根节点", html)
        self.assertIn("可用技能", html)
        self.assertIn("触发日志", html)
        self.assertIn('data-active-view="skill-tree"', html)
        self.assertIn('data-view-target="trigger-log"', html)
        self.assertIn('data-view-page="trigger-log"', html)
        self.assertIn('data-view-target="skill-evolution"', html)
        self.assertIn('data-view-page="skill-evolution"', html)
        self.assertIn("技能进化", html)
        self.assertIn('data-view-target="governance"', html)
        self.assertIn('data-view-page="governance"', html)
        self.assertIn("setDashboardView", html)
        self.assertIn("data-view-header", html)
        self.assertNotIn('href="#trigger-log-view"', html)
        self.assertIn("治理快照", html)
        self.assertIn("平台与项目", html)
        self.assertIn('data-view-target="platforms"', html)
        self.assertIn('data-view-page="platforms"', html)
        self.assertNotIn("基础本地技能", html)
        self.assertNotIn("目录 JSON 批量转 CSV", html)
        self.assertNotIn('data-skill-name="directory_json_to_csv_dogfood"', html)
        self.assertNotIn("合并文本文件", html)
        self.assertIn("进入观察", html)
        self.assertNotIn("Batch export all JSON records in a folder into CSV files.", html)

    def test_dashboard_collector_and_renderer_show_skill_evolution_candidates(self) -> None:
        from skill_runtime.dashboard.collector import collect_dashboard_data
        from skill_runtime.dashboard.render import render_dashboard_html
        from skill_runtime.evolution.candidates import EvolutionCandidateStore

        EvolutionCandidateStore(self.runtime_root).create_candidate(
            target_skill_name="pre_implementation_workflow_review",
            source_task_description="Improve the direction review workflow after a user correction.",
            reason="User correction showed the workflow should challenge low-value routes earlier.",
            evidence=["The old route allowed low-value skill work to continue too long."],
            proposed_changes=["Add a guard for repeated low-value validation loops."],
            risk_level="medium",
            change_type="guardrail",
        )

        data = collect_dashboard_data(self.runtime_root)
        html = render_dashboard_html(data)

        self.assertEqual(1, data["overview"]["evolution_candidate_count"])
        self.assertEqual(1, len(data["evolution_candidates"]))
        self.assertIn("技能进化", html)
        self.assertIn("待审核", html)
        self.assertIn("开发前方向审核", html)
        self.assertIn("low-value", html)
        self.assertIn("中风险", html)

    def test_dashboard_skill_evolution_empty_state_explains_mechanism(self) -> None:
        from skill_runtime.dashboard.collector import collect_dashboard_data
        from skill_runtime.dashboard.render import render_dashboard_html

        data = collect_dashboard_data(self.runtime_root)
        html = render_dashboard_html(data)

        self.assertEqual([], data["evolution_candidates"])
        self.assertIn("data-evolution-empty-state", html)
        self.assertIn("真实任务", html)
        self.assertIn("暴露缺口", html)
        self.assertIn("候选提案", html)
        self.assertIn("人工审核", html)
        self.assertIn("确认应用", html)
        self.assertIn("可回滚", html)
        self.assertIn("例如：开发前方向审核", html)
        self.assertIn("候选不会自动改写全局技能", html)

    def test_dashboard_evolution_cards_open_lifecycle_detail_drawer(self) -> None:
        from skill_runtime.dashboard.collector import collect_dashboard_data
        from skill_runtime.dashboard.render import render_dashboard_html
        from skill_runtime.evolution.candidates import EvolutionCandidateStore

        store = EvolutionCandidateStore(self.runtime_root)
        candidate = store.create_candidate(
            target_skill_name="pre_implementation_workflow_review",
            source_task_description="Improve the direction review workflow after a user correction.",
            reason="User correction showed the workflow should challenge low-value routes earlier.",
            evidence=["The old route allowed low-value skill work to continue too long."],
            proposed_changes=["Add a guard for repeated low-value validation loops."],
            risk_level="medium",
            change_type="guardrail",
        )
        store.update_candidate(
            candidate["candidate_path"],
            {
                "status": "applied",
                "review_path": str(self.runtime_root / ".skill_runtime" / "evolution_reviews" / "demo.review.json"),
                "review_decision": "ready_for_manual_diff",
                "application_path": str(
                    self.runtime_root / ".skill_runtime" / "evolution_applications" / "demo.apply.json"
                ),
                "applied_at": "2026-05-05T10:00:00+00:00",
            },
        )

        data = collect_dashboard_data(self.runtime_root)
        html = render_dashboard_html(data)

        self.assertIn("data-evolution-detail-drawer", html)
        self.assertIn("data-evolution-detail-open", html)
        self.assertIn('data-evolution-target="开发前方向审核"', html)
        self.assertIn('data-evolution-status="已应用"', html)
        self.assertIn('data-evolution-risk="中风险"', html)
        self.assertIn('data-evolution-review-path=', html)
        self.assertIn('data-evolution-application-path=', html)
        self.assertIn("生命周期", html)
        self.assertIn("候选提案", html)
        self.assertIn("审核结果", html)
        self.assertIn("应用记录", html)
        self.assertIn("setActiveEvolutionDetail", html)
        self.assertIn("clearActiveEvolutionDetail", html)

    def test_dashboard_skill_cards_open_read_only_detail_drawer(self) -> None:
        from skill_runtime.dashboard.collector import collect_dashboard_data
        from skill_runtime.dashboard.render import render_dashboard_html

        data = collect_dashboard_data(self.runtime_root)
        html = render_dashboard_html(data)

        self.assertIn('data-skill-detail-drawer', html)
        self.assertIn('data-skill-detail-open', html)
        self.assertIn('data-detail-name="开发前方向审核"', html)
        self.assertIn('data-detail-raw-name="pre_implementation_workflow_review"', html)
        self.assertIn('data-detail-status="active"', html)
        self.assertIn('data-detail-usage-count=', html)
        self.assertIn('data-detail-source-count=', html)
        self.assertIn("Review a proposed development direction before implementation", html)
        self.assertNotIn("global_skill_path", html)
        self.assertNotIn("只读详情", html)
        self.assertNotIn("只读链接", html)
        self.assertNotIn("只读视图", html)
        self.assertNotIn("read_only", html)
        self.assertIn("setActiveSkillDetail", html)
        self.assertIn("clearActiveSkillDetail", html)

    def test_dashboard_platform_inventory_uses_compact_skill_style_cards(self) -> None:
        from skill_runtime.dashboard.render import render_dashboard_html

        data = {
            "root": str(self.runtime_root),
            "overview": {},
            "skills": [],
            "events": [],
            "governance": {},
            "diagnostics": [],
            "capability_collections": [],
            "platform_inventory": {
                "items": [
                    {
                        "skill_name": "code",
                        "skill_path": r"C:\Users\Administrator\.codex\skills\code-1.0.4",
                        "description": (
                            "Coding workflow with planning, implementation, verification, and testing "
                            "for clean software development."
                        ),
                        "source_role": "authoritative_global_skill",
                        "display_name": "Codex",
                        "ownership": "external",
                        "link_type": "read_only",
                        "source_root": r"C:\Users\Administrator\.codex\skills",
                    }
                ],
                "diagnostics": [],
            },
        }

        html = render_dashboard_html(data)

        self.assertIn("platform-card-grid", html)
        self.assertIn("platform-skill-card", html)
        self.assertIn("platform-card-head", html)
        self.assertIn("platform-summary", html)
        self.assertIn("platform-path-chip", html)
        self.assertIn("全局权威", html)
        self.assertIn("外部", html)
        self.assertIn("只读来源", html)
        self.assertNotIn("角色：authoritative_global_skill", html)
        self.assertNotIn(r"来源：C:\Users\Administrator\.codex\skills", html)

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

        self.assertIn("处理方式：运行时参与（记录经验）", html)
        self.assertIn("下一步：整理这次任务轨迹", html)
        self.assertIn("提升这条捕获到的工作流到全局", html)

    def test_dashboard_governance_snapshot_explains_empty_state_and_missing_rejected_directory(self) -> None:
        from skill_runtime.dashboard.render import render_dashboard_html

        data = {
            "root": str(self.runtime_root),
            "overview": {},
            "skills": [],
            "events": [],
            "governance": {"duplicate_candidates": []},
            "diagnostics": ["Missing skill directory: skill_store\\rejected"],
            "platform_inventory": {},
            "capability_collections": [],
        }

        html = render_dashboard_html(data)

        self.assertIn("当前没有发现需要合并处理的重复候选。", html)
        self.assertIn("这表示目前没有两条过于相似、可能其实是同一项技能的候选。", html)
        self.assertIn("当前还没有“已拒绝候选”目录。", html)
        self.assertIn("这不是错误，只表示你还没有把候选明确标记为拒绝。", html)
        self.assertIn("暂时不需要处理。只有你开始使用“拒绝候选”流程时，这个目录才会出现。", html)
        self.assertNotIn("Missing skill directory: skill_store\\rejected", html)

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

    def test_dashboard_renderer_shows_imported_workflow_provenance(self) -> None:
        from skill_runtime.dashboard.render import render_dashboard_html

        source_dir = self.runtime_root / "external-skills" / "dashboard-import"
        source_dir.mkdir(parents=True)
        content_hash = "1234567890abcdef"
        imported_skill = {
            "skill_name": "dashboard-import",
            "status": "active",
            "summary": "Imported dashboard skill.",
            "source_trajectory_ids": [],
            "usage_count": 0,
            "tags": ["imported"],
            "is_imported": True,
            "audit_status": "requires_review",
            "import_source": str(source_dir.resolve()),
            "imported_at": "2026-05-03T12:00:00+00:00",
            "content_hash": content_hash,
            "provenance": {"type": "local_skill_import"},
            "skill_surface": "workflow",
        }
        data = {
            "root": str(self.runtime_root),
            "overview": {},
            "skills": [imported_skill],
            "events": [],
            "governance": {},
            "diagnostics": [],
            "platform_inventory": {},
            "capability_collections": [
                {
                    "collection_id": "imported-workflows",
                    "label": "外部导入",
                    "description": "外部导入的工作流技能。",
                    "skills": [imported_skill],
                    "status_counts": {"active": 1, "staging": 0, "archived": 0, "rejected": 0},
                    "missing_skill_names": [],
                    "read_only": True,
                }
            ],
        }

        html = render_dashboard_html(data)

        self.assertIn('data-skill-name="dashboard-import"', html)
        self.assertIn("需要审核", html)
        self.assertIn(str(source_dir.resolve()), html)
        self.assertIn(content_hash[:12], html)

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
        self.assertIn("运行时总览", html)
        self.assertIn("触发日志", html)
        self.assertIn("方向与策略", html)
        self.assertIn("开发前方向审核", html)
        self.assertNotIn("合并文本文件", html)

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
        self.assertIn("全局运行时总览", html)
        self.assertIn("当前项目", html)
        self.assertIn("跨工作区", html)
        self.assertIn('data-view-target="overview"', html)
        self.assertIn("中央技能库", html)
        self.assertIn("触发日志", html)
        self.assertIn("治理快照", html)
        self.assertIn("全局项目", html)
        self.assertNotIn("全局日志", html)
        self.assertNotIn('data-view-target="global-log"', html)
        self.assertNotIn("跨工作区调用记录已合并", html)
        self.assertIn("任务：合并 alpha 笔记", html)
        self.assertNotIn("auto-executed reusable skill", html)

    def test_runtime_events_cli_returns_recent_follow_up_actions(self) -> None:
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

        payload = self._run_cli(
            "runtime-events",
            "--limit",
            "5",
            expect_json=True,
            root=self.runtime_root,
        )

        self.assertEqual("ok", payload["status"])
        self.assertFalse(payload["data"]["global"])
        self.assertEqual(1, payload["data"]["event_count"])
        self.assertEqual({"used": 1, "entered": 0, "skipped": 0}, payload["data"]["recent_event_counts"])
        event = payload["data"]["events"][0]
        self.assertEqual("distill_trajectory", event["recommended_next_action"])
        self.assertIn("Promote captured workflow globally", event["available_host_operation_labels"])

    def test_runtime_events_cli_can_return_global_events(self) -> None:
        workspace_parent = self.runtime_root / "global-events-cli-workspaces"
        project_alpha = workspace_parent / "alpha"
        self._write_dashboard_event(
            project_alpha,
            timestamp="2026-05-03T06:41:00+00:00",
            task_description="capture alpha workflow",
            runtime_lane_status="used",
            runtime_lane_reason="captured learning payload",
            recommended_next_action="distill_trajectory",
            available_host_operation_labels=["Promote captured workflow globally"],
        )

        payload = self._run_cli(
            "runtime-events",
            "--global",
            "--scan-root",
            str(workspace_parent),
            "--limit",
            "10",
            expect_json=True,
            root=self.runtime_root,
        )

        self.assertEqual("ok", payload["status"])
        self.assertTrue(payload["data"]["global"])
        self.assertEqual(1, payload["data"]["event_count"])
        self.assertEqual("alpha", payload["data"]["events"][0]["project_name"])
        self.assertIn("Promote captured workflow globally", payload["data"]["events"][0]["available_host_operation_labels"])

    def test_runtime_events_payload_builder_matches_cli_shape(self) -> None:
        from skill_runtime.observability.events import build_runtime_events_payload

        self._write_dashboard_event(
            self.runtime_root,
            timestamp="2026-05-03T06:44:00+00:00",
            task_description="capture shared payload workflow",
            runtime_lane_status="entered",
            runtime_lane_reason="default lane observation",
        )

        payload = build_runtime_events_payload(self.runtime_root, limit=5)

        self.assertFalse(payload["global"])
        self.assertEqual(str(self.runtime_root.resolve()), payload["root"])
        self.assertEqual(1, payload["event_count"])
        self.assertEqual({"used": 0, "entered": 1, "skipped": 0}, payload["recent_event_counts"])
        self.assertEqual("capture shared payload workflow", payload["events"][0]["task_description"])

    def test_global_runtime_events_payload_builder_matches_cli_shape(self) -> None:
        from skill_runtime.observability.events import build_global_runtime_events_payload

        workspace_parent = self.runtime_root / "global-events-builder-workspaces"
        project_alpha = workspace_parent / "alpha"
        self._write_dashboard_event(
            project_alpha,
            timestamp="2026-05-03T06:45:00+00:00",
            task_description="capture shared global payload workflow",
            runtime_lane_status="skipped",
            runtime_lane_reason="outside default lane",
        )

        payload = build_global_runtime_events_payload(
            self.runtime_root,
            scan_roots=[str(workspace_parent)],
            limit=5,
        )

        self.assertTrue(payload["global"])
        self.assertEqual(str(self.runtime_root.resolve()), payload["root"])
        self.assertEqual(1, payload["event_count"])
        self.assertEqual({"used": 0, "entered": 0, "skipped": 1}, payload["recent_event_counts"])
        self.assertEqual("alpha", payload["events"][0]["project_name"])

    def test_mcp_runtime_events_reads_recent_follow_up_actions(self) -> None:
        self._write_dashboard_event(
            self.runtime_root,
            timestamp="2026-05-03T06:42:00+00:00",
            task_description="capture a reusable workflow through mcp",
            runtime_lane_status="used",
            runtime_lane_reason="captured learning payload",
            recommended_next_action="distill_trajectory",
            available_host_operation_labels=["Promote captured workflow globally"],
        )

        payload = self._call_mcp_tool(
            "runtime_events",
            {"limit": 10},
            root=self.runtime_root,
        )

        self.assertFalse(payload["data"]["global"])
        self.assertEqual(1, payload["data"]["event_count"])
        event = payload["data"]["events"][0]
        self.assertEqual("distill_trajectory", event["recommended_next_action"])
        self.assertIn("Promote captured workflow globally", event["available_host_operation_labels"])

    def test_mcp_runtime_events_can_return_global_events(self) -> None:
        workspace_parent = self.runtime_root / "global-events-mcp-workspaces"
        project_alpha = workspace_parent / "alpha"
        self._write_dashboard_event(
            project_alpha,
            timestamp="2026-05-03T06:43:00+00:00",
            task_description="capture alpha workflow through mcp",
            runtime_lane_status="used",
            runtime_lane_reason="captured learning payload",
            recommended_next_action="distill_trajectory",
            available_host_operation_labels=["Promote captured workflow globally"],
        )

        payload = self._call_mcp_tool(
            "runtime_events",
            {
                "global_events": True,
                "scan_roots": [str(workspace_parent)],
                "limit": 10,
            },
            root=self.runtime_root,
        )

        self.assertTrue(payload["data"]["global"])
        self.assertEqual(1, payload["data"]["event_count"])
        self.assertEqual("alpha", payload["data"]["events"][0]["project_name"])

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
