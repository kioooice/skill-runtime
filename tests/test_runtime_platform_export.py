class RuntimePlatformExportTestsMixin:
    def test_service_promotes_staging_workflow_skill_to_global_codex_skill_without_active_copy(self) -> None:
        staging_dir = self.runtime_root / "skill_store" / "staging"
        staging_dir.mkdir(parents=True, exist_ok=True)
        skill_name = "review_direction_before_building"
        skill_path = staging_dir / f"{skill_name}.py"
        metadata_path = staging_dir / f"{skill_name}.metadata.json"
        global_skills_dir = self.runtime_root / "global-codex-skills"

        skill_path.write_text(
            "def run(tools, output_path, **kwargs):\n"
            "    \"\"\"Review whether a proposed workflow is worth building before implementation.\"\"\"\n"
            "    tools.write_json(output_path, {'status': 'reviewed'})\n"
            "    return {'status': 'completed'}\n",
            encoding="utf-8",
        )
        self._write_json_file(
            metadata_path,
            {
                "skill_name": skill_name,
                "file_path": str(skill_path.resolve()),
                "summary": "Review a development direction before implementation.",
                "docstring": "Review whether a proposed workflow is worth building before implementation.",
                "input_schema": {"output_path": "str"},
                "output_schema": {"status": "str"},
                "source_trajectory_ids": ["trajectory-review-direction"],
                "created_at": "2026-05-03T00:00:00+00:00",
                "last_used_at": None,
                "usage_count": 0,
                "status": "staging",
                "audit_score": None,
                "tags": ["workflow", "review"],
            },
        )

        audit_result = self.service.audit(skill_path)
        self.assertEqual("passed", audit_result["report"]["status"])
        self.assertEqual("promote_global_codex_skill", audit_result["recommended_next_action"])
        self.assertEqual(
            str(skill_path),
            audit_result["recommended_host_operation"]["arguments"]["file_path"],
        )

        result = self.service.promote_to_global_codex_skill(
            skill_path,
            global_skills_dir=global_skills_dir,
        )

        self.assertEqual("review-direction-before-building", result["global_skill_name"])
        self.assertEqual("authoritative_global_skill", result["source_role"])
        self.assertFalse((self.runtime_root / "skill_store" / "active" / f"{skill_name}.py").exists())
        self.assertIsNone(self.index.get(skill_name))

        skill_file = global_skills_dir / "review-direction-before-building" / "SKILL.md"
        self.assertTrue(skill_file.exists())
        content = skill_file.read_text(encoding="utf-8")
        self.assertIn("name: review-direction-before-building", content)
        self.assertIn("Review a development direction before implementation.", content)
        self.assertIn("source runtime skill", content)
        self.assertTrue((global_skills_dir / "review-direction-before-building" / "agents" / "openai.yaml").exists())

    def test_cli_promotes_staging_workflow_skill_to_global_codex_skill(self) -> None:
        staging_dir = self.runtime_root / "skill_store" / "staging"
        staging_dir.mkdir(parents=True, exist_ok=True)
        skill_name = "manual_validation_before_mvp"
        skill_path = staging_dir / f"{skill_name}.py"
        metadata_path = staging_dir / f"{skill_name}.metadata.json"
        global_skills_dir = self.runtime_root / "global-codex-skills-cli"

        skill_path.write_text(
            "def run(tools, output_path, **kwargs):\n"
            "    \"\"\"Check whether a manual validation loop exists before MVP work starts.\"\"\"\n"
            "    tools.write_json(output_path, {'status': 'checked'})\n"
            "    return {'status': 'completed'}\n",
            encoding="utf-8",
        )
        self._write_json_file(
            metadata_path,
            {
                "skill_name": skill_name,
                "file_path": str(skill_path.resolve()),
                "summary": "Check manual validation before MVP work.",
                "docstring": "Check whether a manual validation loop exists before MVP work starts.",
                "input_schema": {"output_path": "str"},
                "output_schema": {"status": "str"},
                "source_trajectory_ids": ["trajectory-manual-validation"],
                "created_at": "2026-05-03T00:00:00+00:00",
                "last_used_at": None,
                "usage_count": 0,
                "status": "staging",
                "audit_score": None,
                "tags": ["workflow", "validation"],
            },
        )
        self.service.audit(skill_path)

        payload = self._run_cli(
            "promote-global-codex-skill",
            "--file",
            str(skill_path),
            "--global-skills-dir",
            str(global_skills_dir),
            expect_json=True,
            root=self.runtime_root,
        )

        self.assertEqual("ok", payload["status"])
        data = payload["data"]
        self.assertEqual("manual-validation-before-mvp", data["global_skill_name"])
        self.assertEqual("authoritative_global_skill", data["source_role"])
        self.assertTrue((global_skills_dir / "manual-validation-before-mvp" / "SKILL.md").exists())

    def test_service_distill_and_promote_can_target_global_codex_skill(self) -> None:
        global_skills_dir = self.runtime_root / "global-distill-promote"
        result = self.service.distill_and_promote(
            trajectory_path=self.runtime_root / "trajectories" / "demo_merge_text_files.json",
            skill_name="review_global_promotion_target",
            promotion_target="global_codex",
            global_skills_dir=global_skills_dir,
        )

        self.assertTrue(result["promoted"])
        self.assertEqual("global_codex", result["promotion_target"])
        self.assertEqual("review-global-promotion-target", result["promotion"]["global_skill_name"])
        self.assertEqual("authoritative_global_skill", result["promotion"]["source_role"])
        self.assertFalse((self.runtime_root / "skill_store" / "active" / "review_global_promotion_target.py").exists())
        self.assertIsNone(self.index.get("review_global_promotion_target"))
        self.assertTrue((global_skills_dir / "review-global-promotion-target" / "SKILL.md").exists())

    def test_cli_distill_and_promote_can_target_global_codex_skill(self) -> None:
        global_skills_dir = self.runtime_root / "global-distill-promote-cli"
        payload = self._run_cli(
            "distill-and-promote",
            "--trajectory",
            str(self.runtime_root / "trajectories" / "demo_merge_text_files.json"),
            "--skill-name",
            "cli_review_global_promotion_target",
            "--promotion-target",
            "global-codex",
            "--global-skills-dir",
            str(global_skills_dir),
            root=self.runtime_root,
            expect_json=True,
        )

        self.assertEqual("ok", payload["status"])
        data = payload["data"]
        self.assertTrue(data["promoted"])
        self.assertEqual("global_codex", data["promotion_target"])
        self.assertEqual("cli-review-global-promotion-target", data["promotion"]["global_skill_name"])
        self.assertTrue((global_skills_dir / "cli-review-global-promotion-target" / "SKILL.md").exists())

    def test_mcp_distill_and_promote_can_target_global_codex_skill(self) -> None:
        global_skills_dir = self.runtime_root / "global-distill-promote-mcp"
        payload = self._call_mcp_tool(
            "distill_and_promote_candidate",
            {
                "trajectory_path": str(self.runtime_root / "trajectories" / "demo_merge_text_files.json"),
                "skill_name": "mcp_review_global_promotion_target",
                "register_trajectory": True,
                "promotion_target": "global_codex",
                "global_skills_dir": str(global_skills_dir),
            },
            root=self.runtime_root,
        )

        data = payload["data"]
        self.assertTrue(data["promoted"])
        self.assertEqual("global_codex", data["promotion_target"])
        self.assertEqual("mcp-review-global-promotion-target", data["promotion"]["global_skill_name"])
        self.assertTrue((global_skills_dir / "mcp-review-global-promotion-target" / "SKILL.md").exists())

    def test_observed_task_distill_and_promote_can_target_global_codex_skill(self) -> None:
        observed_path = self._write_json_file(
            self.runtime_root / "demo" / "observed_global_distill_promote.json",
            self._build_move_logs_observed_task(variant="steps", artifact=None),
        )
        global_skills_dir = self.runtime_root / "global-observed-distill-promote"

        result = self.service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_review_global_promotion_target",
            promotion_target="global_codex",
            global_skills_dir=global_skills_dir,
        )

        self.assertTrue(result["promoted"])
        self.assertIsNotNone(result["capture"])
        self.assertIsNone(result["trajectory"])
        self.assertEqual("global_codex", result["promotion_target"])
        self.assertEqual("observed-review-global-promotion-target", result["promotion"]["global_skill_name"])
        self.assertFalse(
            (self.runtime_root / "skill_store" / "active" / "observed_review_global_promotion_target.py").exists()
        )
        self.assertIsNone(self.index.get("observed_review_global_promotion_target"))
        self.assertTrue((global_skills_dir / "observed-review-global-promotion-target" / "SKILL.md").exists())

    def test_distill_and_promote_rejects_unknown_promotion_target(self) -> None:
        from skill_runtime.api.service import RuntimeServiceError

        with self.assertRaises(RuntimeServiceError) as blocked:
            self.service.distill_and_promote(
                trajectory_path=self.runtime_root / "trajectories" / "demo_merge_text_files.json",
                skill_name="invalid_promotion_target_test",
                promotion_target="global",
            )

        self.assertEqual("INVALID_PROMOTION_TARGET", blocked.exception.code)

    def test_platform_export_plan_previews_active_skill_without_writing_target(self) -> None:
        from skill_runtime.platforms.export_plan import plan_platform_export
        from skill_runtime.platforms.registry import PlatformRoot

        target_dir = self.runtime_root / "platform-export" / "codex-skills"
        target_dir.mkdir(parents=True)
        before_paths = sorted(path.relative_to(target_dir) for path in target_dir.rglob("*"))

        plan = plan_platform_export(
            self.runtime_root,
            "merge_text_files",
            "codex",
            platform_roots=[
                PlatformRoot(
                    platform_id="codex",
                    display_name="Codex",
                    skills_dir=target_dir,
                )
            ],
        )

        after_paths = sorted(path.relative_to(target_dir) for path in target_dir.rglob("*"))
        self.assertEqual(before_paths, after_paths)
        self.assertTrue(plan["eligible"])
        self.assertEqual("merge_text_files", plan["skill_name"])
        self.assertEqual("codex", plan["platform_id"])
        self.assertEqual(str((target_dir / "merge_text_files").resolve()), plan["target_path"])
        self.assertEqual("none", plan["conflict"])
        self.assertTrue(plan["requires_confirmation"])
        self.assertTrue(plan["read_only"])
        self.assertIn(plan["link_type"], {"symlink_export", "copied_export"})

    def test_platform_export_plan_blocks_non_active_skill(self) -> None:
        from skill_runtime.platforms.export_plan import plan_platform_export
        from skill_runtime.platforms.registry import PlatformRoot

        target_dir = self.runtime_root / "platform-export" / "codex-skills"
        target_dir.mkdir(parents=True)

        plan = plan_platform_export(
            self.runtime_root,
            "bridge_config_test",
            "codex",
            platform_roots=[
                PlatformRoot(
                    platform_id="codex",
                    display_name="Codex",
                    skills_dir=target_dir,
                )
            ],
        )

        self.assertFalse(plan["eligible"])
        self.assertEqual("skill_not_active", plan["conflict"])
        self.assertIn("Only active skills", plan["warnings"][0])

    def test_platform_export_plan_refuses_existing_real_directory_conflict(self) -> None:
        from skill_runtime.platforms.export_plan import plan_platform_export
        from skill_runtime.platforms.registry import PlatformRoot

        target_dir = self.runtime_root / "platform-export" / "codex-skills"
        existing_target = target_dir / "merge_text_files"
        existing_target.mkdir(parents=True)
        (existing_target / "SKILL.md").write_text("# Existing\n", encoding="utf-8")

        plan = plan_platform_export(
            self.runtime_root,
            "merge_text_files",
            "codex",
            platform_roots=[
                PlatformRoot(
                    platform_id="codex",
                    display_name="Codex",
                    skills_dir=target_dir,
                )
            ],
        )

        self.assertFalse(plan["eligible"])
        self.assertEqual("existing_directory", plan["conflict"])
        self.assertTrue(plan["requires_confirmation"])

    def test_platform_export_plan_cli_returns_preview_payload(self) -> None:
        target_dir = self.runtime_root / "platform-export-cli" / "codex-skills"
        target_dir.mkdir(parents=True)

        payload = self._run_cli(
            "platform-export-plan",
            "--skill",
            "merge_text_files",
            "--platform",
            "codex",
            "--target-dir",
            str(target_dir),
            expect_json=True,
            root=self.runtime_root,
        )

        self.assertEqual("ok", payload["status"])
        data = payload["data"]
        self.assertTrue(data["eligible"])
        self.assertEqual("merge_text_files", data["skill_name"])
        self.assertEqual("codex", data["platform_id"])
        self.assertEqual(str((target_dir / "merge_text_files").resolve()), data["target_path"])
