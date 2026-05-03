class RuntimePlatformExportTestsMixin:
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
