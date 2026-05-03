class RuntimeSkillImportTestsMixin:
    def test_local_skill_import_copies_external_skill_into_staging_with_provenance(self) -> None:
        from skill_runtime.importers.local_skill_importer import import_local_skill_to_staging

        source_dir = self.runtime_root / "external-skills" / "summarize-notes"
        source_dir.mkdir(parents=True)
        (source_dir / "SKILL.md").write_text(
            "---\nname: summarize-notes\ndescription: Summarize local notes.\n---\n\n# Summarize Notes\n",
            encoding="utf-8",
        )
        before_source_files = sorted(path.relative_to(source_dir) for path in source_dir.rglob("*"))

        result = import_local_skill_to_staging(self.runtime_root, source_dir)
        after_source_files = sorted(path.relative_to(source_dir) for path in source_dir.rglob("*"))

        self.assertEqual(before_source_files, after_source_files)
        self.assertEqual("summarize-notes", result["skill_name"])
        self.assertEqual("staging", result["status"])
        self.assertEqual("requires_review", result["audit_status"])
        self.assertTrue(result["read_only_source"])
        self.assertTrue((self.runtime_root / "skill_store" / "staging" / "imported" / "summarize-notes" / "SKILL.md").exists())
        self.assertTrue((self.runtime_root / "skill_store" / "staging" / "summarize-notes.metadata.json").exists())
        self.assertFalse((self.runtime_root / "skill_store" / "active" / "summarize-notes.metadata.json").exists())

    def test_local_skill_import_rejects_directory_without_skill_md(self) -> None:
        from skill_runtime.importers.local_skill_importer import SkillImportError, import_local_skill_to_staging

        source_dir = self.runtime_root / "external-skills" / "missing-skill"
        source_dir.mkdir(parents=True)

        with self.assertRaises(SkillImportError) as context:
            import_local_skill_to_staging(self.runtime_root, source_dir)

        self.assertEqual("SKILL_MD_NOT_FOUND", context.exception.code)

    def test_import_skill_to_staging_cli_returns_staging_payload(self) -> None:
        source_dir = self.runtime_root / "external-skills" / "cli-skill"
        source_dir.mkdir(parents=True)
        (source_dir / "SKILL.md").write_text(
            "---\nname: cli-skill\ndescription: CLI imported skill.\n---\n\n# CLI Skill\n",
            encoding="utf-8",
        )

        payload = self._run_cli(
            "import-skill-to-staging",
            "--source",
            str(source_dir),
            expect_json=True,
            root=self.runtime_root,
        )

        self.assertEqual("ok", payload["status"])
        data = payload["data"]
        self.assertEqual("cli-skill", data["skill_name"])
        self.assertEqual("staging", data["status"])
        self.assertEqual("requires_review", data["audit_status"])
        self.assertTrue((self.runtime_root / "skill_store" / "staging" / "imported" / "cli-skill" / "SKILL.md").exists())
        self.assertFalse((self.runtime_root / "skill_store" / "active" / "cli-skill.metadata.json").exists())
