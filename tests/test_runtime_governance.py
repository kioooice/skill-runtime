from skill_runtime.governance.provenance_backfill import ProvenanceBackfill
from tests.runtime_test_support import ROOT


class RuntimeGovernanceTestsMixin:
    def test_backfill_provenance_updates_legacy_skill_metadata(self) -> None:
        active_dir = ROOT / "skill_store" / "active"
        skill_source = (
            'def run(tools, **kwargs):\n'
            '    """legacy"""\n'
            '    inputs = {"input_dir": kwargs.get("input_dir"), "output_path": kwargs.get("output_path")}\n'
            '    return {"status": "completed"}\n'
        )
        _, _ = self._write_active_skill_fixture(
            "legacy_merge_skill",
            {
                "summary": "Merge all txt files in a directory into one markdown file.",
                "docstring": "legacy",
                "input_schema": {"input_dir": "str", "output_path": "str"},
                "output_schema": {"status": "str"},
                "source_trajectory_ids": [],
                "created_at": "2026-04-18T00:00:00",
                "last_used_at": None,
                "usage_count": 0,
                "status": "active",
                "audit_score": 100,
                "tags": ["merge", "txt", "input_dir", "output_path"],
            },
            source=skill_source,
        )
        self.index.rebuild_from_directory(active_dir)

        updated = ProvenanceBackfill(active_dir, self.index).run()
        self.assertTrue(any(item["skill_name"] == "legacy_merge_skill" for item in updated))

        refreshed = self.index.get("legacy_merge_skill")
        self.assertIsNotNone(refreshed)
        self.assertEqual("text_merge", refreshed.rule_name)
        self.assertIsNotNone(refreshed.rule_reason)

    def test_service_backfill_provenance_returns_governance_follow_up(self) -> None:
        active_dir = ROOT / "skill_store" / "active"
        self._write_active_skill_fixture(
            "legacy_backfill_follow_up_skill",
            {
                "summary": "Legacy backfill follow-up skill.",
                "docstring": "legacy",
                "input_schema": {"input_dir": "str", "output_path": "str"},
                "output_schema": {"status": "str"},
                "source_trajectory_ids": [],
                "created_at": "2026-04-18T00:00:00",
                "last_used_at": None,
                "usage_count": 0,
                "status": "active",
                "audit_score": 100,
                "tags": ["merge", "txt", "input_dir", "output_path"],
            },
            source=(
                'def run(tools, **kwargs):\n'
                '    """legacy"""\n'
                '    inputs = {"input_dir": kwargs.get("input_dir"), "output_path": kwargs.get("output_path")}\n'
                '    return {"status": "completed"}\n'
            ),
        )
        self.index.rebuild_from_directory(active_dir)

        payload = self.service.backfill_provenance()

        self.assertGreaterEqual(payload["updated_count"], 1)
        self.assertTrue(
            any(item["skill_name"] == "legacy_backfill_follow_up_skill" for item in payload["updated"])
        )
        self.assertEqual("governance_report", payload["recommended_next_action"])
        self._assert_host_operation_basics(
            payload["recommended_host_operation"],
            tool_name="governance_report",
            display_label="Refresh governance report",
            risk_level="low",
            requires_confirmation=False,
        )
        self._assert_operation_role(payload["available_host_operations"][0], "primary")

    def test_mcp_backfill_skill_provenance_returns_governance_follow_up(self) -> None:
        active_dir = ROOT / "skill_store" / "active"
        self._write_active_skill_fixture(
            "legacy_backfill_mcp_skill",
            {
                "summary": "Legacy backfill MCP skill.",
                "docstring": "legacy",
                "input_schema": {"input_dir": "str", "output_path": "str"},
                "output_schema": {"status": "str"},
                "source_trajectory_ids": [],
                "created_at": "2026-04-18T00:00:00",
                "last_used_at": None,
                "usage_count": 0,
                "status": "active",
                "audit_score": 100,
                "tags": ["merge", "txt", "input_dir", "output_path"],
            },
            source=(
                'def run(tools, **kwargs):\n'
                '    """legacy"""\n'
                '    inputs = {"input_dir": kwargs.get("input_dir"), "output_path": kwargs.get("output_path")}\n'
                '    return {"status": "completed"}\n'
            ),
        )
        self.index.rebuild_from_directory(active_dir)

        payload = self._call_mcp_tool("backfill_skill_provenance", {})

        self.assertIn("updated", payload["data"])
        self.assertIn("updated_count", payload["data"])
        self.assertEqual(len(payload["data"]["updated"]), payload["data"]["updated_count"])
        self.assertEqual("governance_report", payload["data"]["recommended_next_action"])
        self._assert_host_operation_basics(
            payload["data"]["recommended_host_operation"],
            tool_name="governance_report",
            display_label="Refresh governance report",
            risk_level="low",
            requires_confirmation=False,
        )
        self._assert_operation_role(payload["data"]["available_host_operations"][0], "primary")

    def test_service_reindex_returns_governance_follow_up(self) -> None:
        payload = self.service.reindex()

        self.assertIn("index_path", payload)
        self.assertIn("skill_count", payload)
        self.assertEqual("governance_report", payload["recommended_next_action"])
        self._assert_host_operation_basics(
            payload["recommended_host_operation"],
            tool_name="governance_report",
            display_label="Refresh governance report",
            risk_level="low",
            requires_confirmation=False,
        )
        self._assert_operation_role(payload["available_host_operations"][0], "primary")

    def test_mcp_reindex_skills_returns_governance_follow_up(self) -> None:
        payload = self._call_mcp_tool("reindex_skills", {})

        self.assertIn("index_path", payload["data"])
        self.assertIn("skill_count", payload["data"])
        self.assertEqual("governance_report", payload["data"]["recommended_next_action"])
        self._assert_host_operation_basics(
            payload["data"]["recommended_host_operation"],
            tool_name="governance_report",
            display_label="Refresh governance report",
            risk_level="low",
            requires_confirmation=False,
        )
        self._assert_operation_role(payload["data"]["available_host_operations"][0], "primary")

    def test_archive_cold_moves_old_active_skill_out_of_search(self) -> None:
        active_dir = ROOT / "skill_store" / "active"
        archive_dir = ROOT / "skill_store" / "archive"
        archive_dir.mkdir(parents=True, exist_ok=True)
        skill_name = "archive_candidate_skill"
        skill_path = active_dir / f"{skill_name}.py"
        metadata_path = active_dir / f"{skill_name}.metadata.json"
        archived_skill_path = archive_dir / "archive_candidate_skill.py"
        archived_metadata_path = archive_dir / "archive_candidate_skill.metadata.json"

        self._write_active_skill_fixture(
            skill_name,
            {
                "summary": "Archive candidate skill for governance testing.",
                "docstring": "archive candidate",
                "input_schema": {},
                "output_schema": {"status": "str"},
                "source_trajectory_ids": [],
                "created_at": "2025-01-01T00:00:00+00:00",
                "last_used_at": None,
                "usage_count": 0,
                "status": "active",
                "audit_score": 100,
                "tags": ["archive", "candidate"],
            },
        )
        self.addCleanup(lambda: archived_skill_path.unlink(missing_ok=True))
        self.addCleanup(lambda: archived_metadata_path.unlink(missing_ok=True))

        self.index.rebuild_from_directory(active_dir)
        result = self.service.archive_cold(days=30)

        self.assertIn("archive_candidate_skill", result["archived"])
        self.assertFalse(skill_path.exists())
        self.assertFalse(metadata_path.exists())
        self.assertTrue(archived_skill_path.exists())
        self.assertTrue(archived_metadata_path.exists())

        refreshed = self.index.get("archive_candidate_skill")
        self.assertIsNotNone(refreshed)
        self.assertEqual("archived", refreshed.status)
        self.assertEqual("governance_report", result["recommended_next_action"])
        self._assert_host_operation_basics(
            result["recommended_host_operation"],
            tool_name="governance_report",
            display_label="Refresh governance report",
            risk_level="low",
            requires_confirmation=False,
        )
        self._assert_operation_role(result["available_host_operations"][0], "primary")

        results = self.index.search("archive candidate skill", top_k=20)
        self.assertNotIn("archive_candidate_skill", {item["skill_name"] for item in results})

    def test_mcp_archive_cold_skills_returns_governance_follow_up(self) -> None:
        active_dir = ROOT / "skill_store" / "active"
        archive_dir = ROOT / "skill_store" / "archive"
        archive_dir.mkdir(parents=True, exist_ok=True)
        skill_name = "archive_mcp_candidate_skill"
        archived_skill_path = archive_dir / f"{skill_name}.py"
        archived_metadata_path = archive_dir / f"{skill_name}.metadata.json"

        self._write_active_skill_fixture(
            skill_name,
            {
                "summary": "Archive cold MCP candidate skill.",
                "docstring": "archive cold mcp candidate",
                "input_schema": {},
                "output_schema": {"status": "str"},
                "source_trajectory_ids": [],
                "created_at": "2025-01-01T00:00:00+00:00",
                "last_used_at": None,
                "usage_count": 0,
                "status": "active",
                "audit_score": 100,
                "tags": ["archive", "cold", "candidate"],
            },
        )
        self.addCleanup(lambda: archived_skill_path.unlink(missing_ok=True))
        self.addCleanup(lambda: archived_metadata_path.unlink(missing_ok=True))

        self.index.rebuild_from_directory(active_dir)
        payload = self._call_mcp_tool("archive_cold_skills", {"days": 30})

        self.assertIn(skill_name, payload["data"]["archived"])
        self.assertEqual("governance_report", payload["data"]["recommended_next_action"])
        self._assert_host_operation_basics(
            payload["data"]["recommended_host_operation"],
            tool_name="governance_report",
        )
        self._assert_operation_role(payload["data"]["available_host_operations"][0], "primary")

    def test_governance_report_surfaces_duplicate_candidates(self) -> None:
        report = self.service.governance_report()
        self.assertIn("status_counts", report)
        self.assertIn("duplicate_candidates", report)
        self.assertIn("recommended_actions", report)
        self.assertGreaterEqual(report["active_count"], 1)
        duplicate_cluster = next(
            item for item in report["duplicate_candidates"] if "merge_text_files_generated" in item["skill_names"]
        )
        self.assertGreaterEqual(duplicate_cluster["count"], 2)
        self.assertEqual("merge_text_files", duplicate_cluster["canonical_skill"])
        self.assertIn("merge_text_files_generated", duplicate_cluster["archive_candidates"])
        archive_action = self._find_action(
            report["recommended_actions"],
            "archive_duplicate_candidates",
            canonical_skill="merge_text_files",
        )
        self.assertIn("merge_text_files_generated", archive_action["skill_names"])
        self._assert_host_operation_basics(
            archive_action["host_operation"],
            tool_name="archive_duplicate_candidates",
            source_ref="governance:archive_duplicate_candidates:merge_text_files",
            display_label="Archive duplicates",
            risk_level="high",
            requires_confirmation=True,
        )
        self.assertIn(
            "merge_text_files_generated",
            archive_action["host_operation"]["arguments"]["skill_names"],
        )
        self.assertFalse(archive_action["host_operation"]["arguments"]["dry_run"])
        self._assert_argument_schema_entry(
            archive_action["host_operation"]["argument_schema"],
            "skill_names",
            field_type="array",
            prefilled=True,
        )
        self._assert_argument_schema_entry(
            archive_action["host_operation"]["argument_schema"],
            "dry_run",
            field_type="boolean",
        )
        self._assert_host_operation_basics(
            archive_action["host_operation"]["preview"],
            tool_name="archive_duplicate_candidates",
            source_ref="governance:archive_duplicate_candidates:merge_text_files:preview",
            display_label="Preview archive",
            risk_level="low",
            requires_confirmation=False,
        )
        self.assertTrue(archive_action["host_operation"]["preview"]["arguments"]["dry_run"])
        self._assert_operation_role(archive_action["host_operation"]["preview"], "preview")

    def test_mcp_governance_report_returns_host_ready_recommended_actions(self) -> None:
        payload = self._call_mcp_tool("governance_report", {})
        self.assertIn("recommended_actions", payload["data"])
        self.assertIn("available_host_operations", payload["data"])
        self.assertGreaterEqual(len(payload["data"]["available_host_operations"]), 2)
        archive_action = self._find_action(payload["data"]["recommended_actions"], "archive_duplicate_candidates")
        self._assert_host_operation_basics(
            archive_action["host_operation"],
            tool_name="archive_duplicate_candidates",
        )
        self.assertIn("arguments", archive_action["host_operation"])
        self.assertTrue(
            any(item["tool_name"] == "archive_duplicate_candidates" for item in payload["data"]["available_host_operations"])
        )
        self.assertTrue(
            any(item["operation_role"] == "preview" for item in payload["data"]["available_host_operations"])
        )
        self._assert_operation_role(payload["data"]["available_host_operations"][0], "preview")
        preview_count = 0
        for item in payload["data"]["available_host_operations"]:
            if item["operation_role"] == "preview":
                preview_count += 1
                continue
            break
        self.assertGreaterEqual(preview_count, 1)
        self._assert_operation_role(payload["data"]["available_host_operations"][preview_count], "default")

    def test_archive_duplicate_candidates_keeps_canonical_skill_active(self) -> None:
        active_dir = ROOT / "skill_store" / "active"
        archive_dir = ROOT / "skill_store" / "archive"
        archive_dir.mkdir(parents=True, exist_ok=True)

        canonical_skill = active_dir / "dup_keep_skill.py"
        canonical_metadata = active_dir / "dup_keep_skill.metadata.json"
        duplicate_skill = active_dir / "dup_test_skill.py"
        duplicate_metadata = active_dir / "dup_test_skill.metadata.json"
        archived_duplicate_skill = archive_dir / "dup_test_skill.py"
        archived_duplicate_metadata = archive_dir / "dup_test_skill.metadata.json"

        canonical_payload = {
            "summary": "Merge duplicate txt files into one markdown file.",
            "docstring": "canonical",
            "input_schema": {"input_dir": "str", "output_path": "str"},
            "output_schema": {"status": "str"},
            "source_trajectory_ids": [],
            "created_at": "2026-01-01T00:00:00+00:00",
            "last_used_at": "2026-04-24T00:00:00+00:00",
            "usage_count": 5,
            "status": "active",
            "audit_score": 100,
            "rule_name": "text_merge",
            "rule_priority": 70,
            "rule_reason": "duplicate canonical",
            "tags": ["merge", "markdown", "txt"],
        }
        duplicate_payload = {
            "summary": "Merge duplicate txt files into one markdown file.",
            "docstring": "duplicate",
            "input_schema": {"input_dir": "str", "output_path": "str"},
            "output_schema": {"status": "str"},
            "source_trajectory_ids": [],
            "created_at": "2026-01-01T00:00:00+00:00",
            "last_used_at": None,
            "usage_count": 0,
            "status": "active",
            "audit_score": 90,
            "rule_name": "text_merge",
            "rule_priority": 70,
            "rule_reason": "duplicate candidate",
            "tags": ["merge", "markdown", "txt"],
        }
        self._write_active_skill_fixture("dup_keep_skill", canonical_payload)
        self._write_active_skill_fixture("dup_test_skill", duplicate_payload)
        self.addCleanup(lambda: archived_duplicate_skill.unlink(missing_ok=True))
        self.addCleanup(lambda: archived_duplicate_metadata.unlink(missing_ok=True))

        self.index.rebuild_from_directory(active_dir)
        result = self.service.archive_duplicate_candidates(skill_names=["dup_test_skill"])

        self.assertIn("dup_test_skill", result["archived"])
        self.assertTrue(canonical_skill.exists())
        self.assertTrue(canonical_metadata.exists())
        self.assertFalse(duplicate_skill.exists())
        self.assertFalse(duplicate_metadata.exists())
        self.assertTrue(archived_duplicate_skill.exists())
        self.assertTrue(archived_duplicate_metadata.exists())

        kept = self.index.get("dup_keep_skill")
        archived = self.index.get("dup_test_skill")
        self.assertIsNotNone(kept)
        self.assertEqual("active", kept.status)
        self.assertIsNotNone(archived)
        self.assertEqual("archived", archived.status)
        self.assertEqual("governance_report", result["recommended_next_action"])
        self._assert_host_operation_basics(
            result["recommended_host_operation"],
            tool_name="governance_report",
        )
        self._assert_operation_role(result["available_host_operations"][0], "primary")

    def test_archive_duplicate_candidates_dry_run_does_not_modify_files(self) -> None:
        active_dir = ROOT / "skill_store" / "active"
        archive_dir = ROOT / "skill_store" / "archive"
        archive_dir.mkdir(parents=True, exist_ok=True)

        canonical_skill = active_dir / "dup_preview_keep.py"
        canonical_metadata = active_dir / "dup_preview_keep.metadata.json"
        duplicate_skill = active_dir / "dup_preview_test.py"
        duplicate_metadata = active_dir / "dup_preview_test.metadata.json"

        canonical_payload = {
            "summary": "Preview duplicate txt files into one markdown file.",
            "docstring": "canonical",
            "input_schema": {"input_dir": "str", "output_path": "str"},
            "output_schema": {"status": "str"},
            "source_trajectory_ids": [],
            "created_at": "2026-01-01T00:00:00+00:00",
            "last_used_at": "2026-04-24T00:00:00+00:00",
            "usage_count": 3,
            "status": "active",
            "audit_score": 100,
            "rule_name": "text_merge",
            "rule_priority": 70,
            "rule_reason": "duplicate canonical",
            "tags": ["preview", "merge", "markdown", "txt"],
        }
        duplicate_payload = {
            "summary": "Preview duplicate txt files into one markdown file.",
            "docstring": "duplicate",
            "input_schema": {"input_dir": "str", "output_path": "str"},
            "output_schema": {"status": "str"},
            "source_trajectory_ids": [],
            "created_at": "2026-01-01T00:00:00+00:00",
            "last_used_at": None,
            "usage_count": 0,
            "status": "active",
            "audit_score": 90,
            "rule_name": "text_merge",
            "rule_priority": 70,
            "rule_reason": "duplicate candidate",
            "tags": ["preview", "merge", "markdown", "txt"],
        }
        self._write_active_skill_fixture("dup_preview_keep", canonical_payload)
        self._write_active_skill_fixture("dup_preview_test", duplicate_payload)

        self.index.rebuild_from_directory(active_dir)
        result = self.service.archive_duplicate_candidates(skill_names=["dup_preview_test"], dry_run=True)

        self.assertTrue(result["dry_run"])
        self.assertIn("dup_preview_test", result["planned"])
        self.assertEqual([], result["archived"])
        self.assertTrue(duplicate_skill.exists())
        self.assertTrue(duplicate_metadata.exists())
        self.assertEqual("archive_duplicate_candidates", result["recommended_next_action"])
        self._assert_host_operation_basics(
            result["recommended_host_operation"],
            tool_name="archive_duplicate_candidates",
        )
        self.assertFalse(result["recommended_host_operation"]["arguments"]["dry_run"])
        self.assertIn("dup_preview_test", result["recommended_host_operation"]["arguments"]["skill_names"])
        self.assertTrue(
            any(item["tool_name"] == "governance_report" for item in result["available_host_operations"])
        )

    def test_mcp_archive_duplicate_candidates_returns_follow_up_host_operation(self) -> None:
        active_dir = ROOT / "skill_store" / "active"
        archive_dir = ROOT / "skill_store" / "archive"
        archive_dir.mkdir(parents=True, exist_ok=True)

        canonical_skill = active_dir / "dup_mcp_keep.py"
        canonical_metadata = active_dir / "dup_mcp_keep.metadata.json"
        duplicate_skill = active_dir / "dup_mcp_test.py"
        duplicate_metadata = active_dir / "dup_mcp_test.metadata.json"

        canonical_payload = {
            "summary": "MCP duplicate txt files into one markdown file.",
            "docstring": "canonical",
            "input_schema": {"input_dir": "str", "output_path": "str"},
            "output_schema": {"status": "str"},
            "source_trajectory_ids": [],
            "created_at": "2026-01-01T00:00:00+00:00",
            "last_used_at": "2026-04-24T00:00:00+00:00",
            "usage_count": 4,
            "status": "active",
            "audit_score": 100,
            "rule_name": "text_merge",
            "rule_priority": 70,
            "rule_reason": "duplicate canonical",
            "tags": ["mcp", "merge", "markdown", "txt"],
        }
        duplicate_payload = {
            "summary": "MCP duplicate txt files into one markdown file.",
            "docstring": "duplicate",
            "input_schema": {"input_dir": "str", "output_path": "str"},
            "output_schema": {"status": "str"},
            "source_trajectory_ids": [],
            "created_at": "2026-01-01T00:00:00+00:00",
            "last_used_at": None,
            "usage_count": 0,
            "status": "active",
            "audit_score": 90,
            "rule_name": "text_merge",
            "rule_priority": 70,
            "rule_reason": "duplicate candidate",
            "tags": ["mcp", "merge", "markdown", "txt"],
        }
        self._write_active_skill_fixture("dup_mcp_keep", canonical_payload)
        self._write_active_skill_fixture("dup_mcp_test", duplicate_payload)
        self.addCleanup(lambda: (archive_dir / "dup_mcp_test.py").unlink(missing_ok=True))
        self.addCleanup(lambda: (archive_dir / "dup_mcp_test.metadata.json").unlink(missing_ok=True))

        self.index.rebuild_from_directory(active_dir)
        payload = self._call_mcp_tool(
            "archive_duplicate_candidates",
            {"skill_names": ["dup_mcp_test"], "dry_run": True},
        )

        self.assertEqual("archive_duplicate_candidates", payload["data"]["recommended_next_action"])
        self._assert_host_operation_basics(
            payload["data"]["recommended_host_operation"],
            tool_name="archive_duplicate_candidates",
        )
        self._assert_operation_role(payload["data"]["available_host_operations"][0], "primary")
