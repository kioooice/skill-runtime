class RuntimeCollectionsTestsMixin:
    def test_capability_collection_store_reads_custom_overlay_without_changing_lifecycle(self) -> None:
        from skill_runtime.collections.store import load_capability_collections

        collections_path = self.runtime_root / "skill_store" / "collections.json"
        self._write_json_file(
            collections_path,
            {
                "collections": [
                    {
                        "collection_id": "project-maintenance",
                        "label": "项目维护",
                        "description": "项目状态、文档和维护类工作流。",
                        "skill_names": ["merge_text_files", "missing_skill"],
                    }
                ]
            },
        )
        skills = [
            {
                "skill_name": "merge_text_files",
                "status": "active",
                "summary": "Merge all .txt files in an input directory into one markdown output file.",
            }
        ]

        collections = load_capability_collections(self.runtime_root, skills)

        self.assertEqual(1, len(collections))
        self.assertEqual("project-maintenance", collections[0]["collection_id"])
        self.assertEqual("项目维护", collections[0]["label"])
        self.assertEqual(["merge_text_files"], [skill["skill_name"] for skill in collections[0]["skills"]])
        self.assertEqual(["missing_skill"], collections[0]["missing_skill_names"])
        self.assertEqual({"active": 1, "staging": 0, "archived": 0, "rejected": 0}, collections[0]["status_counts"])

    def test_dashboard_collector_includes_capability_collections(self) -> None:
        from skill_runtime.dashboard.collector import collect_dashboard_data

        collections_path = self.runtime_root / "skill_store" / "collections.json"
        self._write_json_file(
            collections_path,
            {
                "collections": [
                    {
                        "collection_id": "direction-strategy",
                        "label": "方向与策略",
                        "description": "开发方向、部署路线和仓库影响判断。",
                        "skill_names": ["pre_implementation_workflow_review"],
                    }
                ]
            },
        )

        data = collect_dashboard_data(self.runtime_root)

        self.assertIn("capability_collections", data)
        collection = data["capability_collections"][0]
        self.assertEqual("direction-strategy", collection["collection_id"])
        self.assertEqual("方向与策略", collection["label"])
        self.assertTrue(
            any(skill["skill_name"] == "pre_implementation_workflow_review" for skill in collection["skills"])
        )

    def test_default_capability_collections_show_only_workflow_groups(self) -> None:
        from skill_runtime.dashboard.collector import collect_dashboard_data

        data = collect_dashboard_data(self.runtime_root)
        collections = {collection["collection_id"]: collection for collection in data["capability_collections"]}

        self.assertEqual(
            {
                "direction-strategy",
                "autonomous-execution",
                "runtime-safety",
                "session-continuity",
            },
            set(collections),
        )
        self.assertNotIn("basic-skills", collections)
        self.assertNotIn("text-processing", collections)
        self.assertNotIn("structured-conversion", collections)
        self.assertNotIn("file-organization", collections)
        self.assertTrue(
            any(
                skill["skill_name"] == "pre_implementation_workflow_review"
                for skill in collections["direction-strategy"]["skills"]
            )
        )
        self.assertFalse(
            any(
                skill.get("skill_surface") == "basic"
                for collection in collections.values()
                for skill in collection["skills"]
            )
        )

    def test_default_capability_collections_group_workflows_by_function(self) -> None:
        from skill_runtime.dashboard.collector import collect_dashboard_data

        data = collect_dashboard_data(self.runtime_root)
        collections = {collection["collection_id"]: collection for collection in data["capability_collections"]}

        self.assertEqual(
            [
                "pre_implementation_workflow_review",
                "deployment_strategy_review",
                "repo_impact_analysis",
            ],
            [skill["skill_name"] for skill in collections["direction-strategy"]["skills"]],
        )
        self.assertEqual(
            ["auto_mode_stage_runner", "nontechnical_stage_report"],
            [skill["skill_name"] for skill in collections["autonomous-execution"]["skills"]],
        )
        self.assertEqual(
            ["runtime_gate_workflow", "runtime_verification_selector"],
            [skill["skill_name"] for skill in collections["runtime-safety"]["skills"]],
        )
        self.assertEqual(
            ["session_handoff_maintenance"],
            [skill["skill_name"] for skill in collections["session-continuity"]["skills"]],
        )

    def test_dashboard_renderer_uses_central_library_for_workflow_groups(self) -> None:
        from skill_runtime.dashboard.collector import collect_dashboard_data
        from skill_runtime.dashboard.render import render_dashboard_html

        html = render_dashboard_html(collect_dashboard_data(self.runtime_root))

        self.assertIn("可复用流程", html)
        self.assertIn("流程分组", html)
        self.assertIn('data-view-target="skill-tree"', html)
        self.assertIn('data-view-page="skill-tree"', html)
        self.assertNotIn("技能集合", html)
        self.assertNotIn('data-view-target="collections"', html)
        self.assertNotIn('data-view-page="collections"', html)
        self.assertNotIn("基础本地技能", html)
        self.assertIn("collection-section", html)
        self.assertNotIn('data-collection-id="text-processing"', html)
        self.assertNotIn("合并文本文件", html)
        self.assertIn('data-collection-id="direction-strategy"', html)
        self.assertIn("开发前方向审核", html)
        self.assertIn("按功能分组查看当前可复用的流程。", html)

    def test_dashboard_renderer_hides_collection_candidate_noise(self) -> None:
        from skill_runtime.dashboard.render import render_dashboard_html

        data = {
            "root": str(self.runtime_root),
            "overview": {},
            "skills": [],
            "events": [],
            "governance": {},
            "diagnostics": [],
            "platform_inventory": {},
            "capability_collections": [
                {
                    "collection_id": "runtime-safety",
                    "label": "运行时与验证",
                    "description": "工作流治理。",
                    "skills": [
                        {
                            "skill_name": "runtime_gate_workflow",
                            "status": "active",
                            "summary": "Thin runtime adapter that points to the global runtime gate workflow Codex skill.",
                            "source_trajectory_ids": [],
                        },
                        {
                            "skill_name": "bridge_config_test",
                            "status": "staging",
                            "summary": "Candidate bridge config test.",
                            "source_trajectory_ids": [],
                        },
                    ],
                    "status_counts": {"active": 1, "staging": 1, "archived": 0, "rejected": 0},
                    "missing_skill_names": [],
                    "read_only": True,
                },
                {
                    "collection_id": "text-processing",
                    "label": "文本处理",
                    "description": "基础文本处理。",
                    "skills": [
                        {
                            "skill_name": "merge_text_files",
                            "status": "active",
                            "summary": "Merge all .txt files in an input directory into one markdown output file.",
                            "source_trajectory_ids": [],
                        },
                        {
                            "skill_name": "batch_rename_candidate",
                            "status": "staging",
                            "summary": "Rename all txt files in a directory by prefixing them with a value.",
                            "source_trajectory_ids": [],
                        },
                    ],
                    "status_counts": {"active": 1, "staging": 1, "archived": 0, "rejected": 0},
                    "missing_skill_names": [],
                    "read_only": True,
                }
            ],
        }

        html = render_dashboard_html(data)
        workflow_card_start = html.index('data-collection-id="runtime-safety"')
        workflow_card_end = html.index("</article>", workflow_card_start)
        workflow_card_html = html[workflow_card_start:workflow_card_end]

        self.assertNotIn('data-collection-id="text-processing"', html)
        self.assertNotIn("基础文本处理", html)
        self.assertIn("<strong>1</strong>", workflow_card_html)
        self.assertIn("活跃 1", workflow_card_html)
        self.assertNotIn("候选 1", workflow_card_html)
        self.assertIn("运行时接入门禁", workflow_card_html)
        self.assertNotIn("桥接配置测试", workflow_card_html)
        self.assertNotIn("合并文本文件", html)
        self.assertNotIn("batch 重命名 candidate", html)
