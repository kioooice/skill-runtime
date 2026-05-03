class RuntimePlatformInventoryTestsMixin:
    def test_platform_registry_includes_known_skill_roots(self) -> None:
        from skill_runtime.platforms.registry import known_platforms

        platforms = {platform.platform_id: platform for platform in known_platforms()}

        self.assertIn("codex", platforms)
        self.assertIn("claude-code", platforms)
        self.assertIn("cursor", platforms)
        self.assertIn("gemini-cli", platforms)
        self.assertEqual("Codex", platforms["codex"].display_name)
        self.assertTrue(str(platforms["codex"].skills_dir).endswith(".codex\\skills") or str(platforms["codex"].skills_dir).endswith(".codex/skills"))

    def test_platform_inventory_discovers_skills_without_writing(self) -> None:
        from skill_runtime.platforms.discovery import collect_platform_inventory
        from skill_runtime.platforms.registry import PlatformRoot

        platform_root = self.runtime_root / "platforms" / "codex" / "skills"
        skill_dir = platform_root / "merge-text"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("---\nname: merge-text\n---\n\nMerge text files.\n", encoding="utf-8")

        before_paths = sorted(path.relative_to(platform_root) for path in platform_root.rglob("*"))
        inventory = collect_platform_inventory(
            self.runtime_root,
            platform_roots=[
                PlatformRoot(
                    platform_id="codex",
                    display_name="Codex",
                    skills_dir=platform_root,
                )
            ],
        )
        after_paths = sorted(path.relative_to(platform_root) for path in platform_root.rglob("*"))

        self.assertEqual(before_paths, after_paths)
        self.assertEqual(1, len(inventory["items"]))
        item = inventory["items"][0]
        self.assertEqual("codex", item["platform_id"])
        self.assertEqual("Codex", item["display_name"])
        self.assertEqual("merge-text", item["skill_name"])
        self.assertEqual("external", item["ownership"])
        self.assertEqual("read_only", item["link_type"])
        self.assertTrue(item["is_read_only"])
        self.assertEqual(str(platform_root.resolve()), item["source_root"])

    def test_platform_inventory_keeps_shared_agents_root_separate_from_project_local(self) -> None:
        from skill_runtime.platforms.discovery import collect_platform_inventory
        from skill_runtime.platforms.registry import PlatformRoot

        workspace = self.runtime_root / "workspace"
        project_root = workspace / "project-a"
        shared_root = workspace / ".agents" / "skills"
        shared_skill = shared_root / "shared-skill"
        shared_skill.mkdir(parents=True)
        project_root.mkdir(parents=True)
        (shared_skill / "SKILL.md").write_text("# Shared Skill\n", encoding="utf-8")

        inventory = collect_platform_inventory(
            self.runtime_root,
            platform_roots=[
                PlatformRoot(
                    platform_id="agents-shared",
                    display_name="Shared Agents",
                    skills_dir=shared_root,
                )
            ],
            project_roots=[project_root],
        )

        self.assertEqual(1, len(inventory["items"]))
        item = inventory["items"][0]
        self.assertEqual("agents-shared", item["platform_id"])
        self.assertEqual("external", item["ownership"])
        self.assertEqual(str(shared_root.resolve()), item["source_root"])
        self.assertNotEqual(str(project_root.resolve()), item["source_root"])
