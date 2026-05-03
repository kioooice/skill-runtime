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
                        "collection_id": "text-processing",
                        "label": "文本处理",
                        "description": "合并、清理、替换和 Markdown 输出。",
                        "skill_names": ["merge_text_files"],
                    }
                ]
            },
        )

        data = collect_dashboard_data(self.runtime_root)

        self.assertIn("capability_collections", data)
        collection = data["capability_collections"][0]
        self.assertEqual("text-processing", collection["collection_id"])
        self.assertEqual("文本处理", collection["label"])
        self.assertTrue(any(skill["skill_name"] == "merge_text_files" for skill in collection["skills"]))

    def test_dashboard_renderer_includes_capability_collections_view(self) -> None:
        from skill_runtime.dashboard.collector import collect_dashboard_data
        from skill_runtime.dashboard.render import render_dashboard_html

        collections_path = self.runtime_root / "skill_store" / "collections.json"
        self._write_json_file(
            collections_path,
            {
                "collections": [
                    {
                        "collection_id": "text-processing",
                        "label": "文本处理",
                        "description": "合并、清理、替换和 Markdown 输出。",
                        "skill_names": ["merge_text_files"],
                    }
                ]
            },
        )

        html = render_dashboard_html(collect_dashboard_data(self.runtime_root))

        self.assertIn("能力集合", html)
        self.assertIn('data-view-target="collections"', html)
        self.assertIn('data-view-page="collections"', html)
        self.assertIn('data-collection-id="text-processing"', html)
        self.assertIn("合并文本文件", html)
        self.assertIn("不改变执行、审核、提升或归档语义", html)
