import json
import os
import sys
from pathlib import Path

from tests.runtime_test_support import ROOT


class RuntimeCoreDogfoodAcceptanceTestsMixin:
    def test_mcp_host_style_loop_search_execute_promote_and_reuse(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()

        search_payload = self._call_mcp_tool(
            "search_skill",
            {"query": "merge txt files into markdown", "top_k": 5},
            root=sandbox_root,
        )
        search_data = search_payload["data"]

        self.assertEqual("merge_text_files", search_data["recommended_skill_name"])
        self.assertEqual("execute_skill", search_data["recommended_next_action"])
        self.assertTrue(search_data["results"])
        self.assertFalse(any(result["library_tier"] == "fixture" for result in search_data["results"]))

        execute_operation = search_data["recommended_host_operation"]
        self._assert_host_operation_basics(
            execute_operation,
            tool_name="execute_skill",
            source_ref="search:recommended_skill:merge_text_files",
            requires_confirmation=False,
        )
        execute_args = dict(execute_operation["arguments"])
        execute_args["args"] = {
            "input_dir": "demo/input",
            "output_path": "demo/output/core_acceptance_first.md",
        }
        execute_payload = self._call_mcp_tool(execute_operation["tool_name"], execute_args, root=sandbox_root)
        execute_data = execute_payload["data"]
        first_output = sandbox_root / "demo" / "output" / "core_acceptance_first.md"

        self.assertTrue(first_output.exists())
        self.assertEqual("distill_and_promote_candidate", execute_data["recommended_next_action"])
        self.assertTrue(Path(execute_data["observed_task_record"]).exists())
        self._assert_observed_skill_record(
            execute_data["observed_task"],
            skill_name="merge_text_files",
            status="completed",
            first_tool="list_files",
            last_tool="write_text",
        )

        promote_operation = execute_data["recommended_host_operation"]
        self._assert_observed_task_follow_up(
            promote_operation,
            observed_task_path=execute_data["observed_task_record"],
            display_label="Promote this execution",
            risk_level="medium",
        )
        promote_args = dict(promote_operation["arguments"])
        promote_args["skill_name"] = "core_acceptance_merge_text_files"
        promote_payload = self._call_mcp_tool(promote_operation["tool_name"], promote_args, root=sandbox_root)
        promote_data = promote_payload["data"]
        metadata = self._read_json_file(Path(promote_data["distillation"]["metadata_file"]))

        self.assertTrue(promote_data["promoted"])
        self.assertEqual("passed", promote_data["audit"]["report"]["status"])
        self.assertEqual("text_merge", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", promote_data["distillation"])

        promoted = sandbox_index.get("core_acceptance_merge_text_files")
        self.assertIsNotNone(promoted)
        self.assertEqual("active", promoted.status)

        reuse_operation = promote_data["recommended_host_operation"]
        self._assert_host_operation_basics(
            reuse_operation,
            tool_name="execute_skill",
            source_ref="promote:core_acceptance_merge_text_files",
            requires_confirmation=False,
        )
        reuse_args = dict(reuse_operation["arguments"])
        reuse_args["args"] = {
            "input_dir": "demo/input",
            "output_path": "demo/output/core_acceptance_reuse.md",
            "pattern": "*.txt",
        }
        reuse_payload = self._call_mcp_tool(reuse_operation["tool_name"], reuse_args, root=sandbox_root)
        reuse_data = reuse_payload["data"]
        reuse_output = sandbox_root / "demo" / "output" / "core_acceptance_reuse.md"

        self.assertTrue(reuse_output.exists())
        self.assertEqual("completed", reuse_data["result"]["status"])
        self.assertEqual("core_acceptance_merge_text_files", reuse_data["skill_name"])
        self.assertEqual("distill_and_promote_candidate", reuse_data["recommended_next_action"])

        final_search = self._call_mcp_tool(
            "search_skill",
            {"query": "merge txt files into markdown", "top_k": 10},
            root=sandbox_root,
        )["data"]
        library_tiers = {result["skill_name"]: result["library_tier"] for result in final_search["results"]}
        self.assertEqual("stable", library_tiers["merge_text_files"])
        self.assertEqual("stable", library_tiers["core_acceptance_merge_text_files"])
        self.assertNotIn("fixture", library_tiers.values())

        governance = self._call_mcp_tool("governance_report", {}, root=sandbox_root)["data"]
        self.assertEqual(0, governance["library_tier_counts"]["fixture"])
        self.assertGreaterEqual(governance["library_tier_counts"]["stable"], 2)

    def test_mcp_fallback_generated_candidate_is_not_auto_promoted(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()

        payload = self._call_mcp_tool(
            "distill_and_promote_candidate",
            {
                "observed_task": {
                    "task": "Create a weekly insight report from mixed observations.",
                    "actions": [
                        {
                            "tool": "observe_state",
                            "input": {"report_name": "weekly_report"},
                            "result": "Collected mixed observations.",
                        },
                        {
                            "tool": "summarize_notes",
                            "input": {"topic": "weekly_report"},
                            "result": "Summarized notes into a draft.",
                        },
                    ],
                    "outputs": ["demo/output/weekly_report.txt"],
                },
                "skill_name": "core_acceptance_unknown_workflow",
            },
            root=sandbox_root,
        )
        data = payload["data"]
        metadata = self._read_json_file(Path(data["distillation"]["metadata_file"]))

        self.assertFalse(data["promoted"])
        self.assertIsNone(data["promotion"])
        self.assertEqual("promotion skipped because audit did not pass", data["skipped_reason"])
        self.assertEqual("needs_fix", data["audit"]["report"]["status"])
        self.assertIn("fallback_artifact", data["distillation"])
        self.assertEqual("llm_fallback", metadata["rule_name"])
        self.assertEqual("mock_semantic_review_provider", data["audit"]["report"]["semantic_provider"])
        self.assertTrue(
            any(
                "template" in finding.lower() or "fallback" in finding.lower()
                for finding in data["audit"]["report"]["semantic_findings"]
            )
        )
        self.assertIsNone(data["recommended_host_operation"])
        self.assertEqual([], data["available_host_operations"])
        self.assertIsNone(sandbox_index.get("core_acceptance_unknown_workflow"))

    def test_mcp_external_provider_can_promote_and_reuse_unknown_workflow(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        fallback_provider = ROOT / "examples" / "providers" / "copy_metadata_fallback_provider.py"
        semantic_provider = ROOT / "examples" / "providers" / "pass_semantic_review_provider.py"

        original_fallback = os.environ.get("SKILL_RUNTIME_FALLBACK_PROVIDER_CMD")
        original_semantic = os.environ.get("SKILL_RUNTIME_SEMANTIC_PROVIDER_CMD")
        os.environ["SKILL_RUNTIME_FALLBACK_PROVIDER_CMD"] = json.dumps(
            [sys.executable, str(fallback_provider)]
        )
        os.environ["SKILL_RUNTIME_SEMANTIC_PROVIDER_CMD"] = json.dumps(
            [sys.executable, str(semantic_provider)]
        )
        self.addCleanup(self._restore_env, "SKILL_RUNTIME_FALLBACK_PROVIDER_CMD", original_fallback)
        self.addCleanup(self._restore_env, "SKILL_RUNTIME_SEMANTIC_PROVIDER_CMD", original_semantic)

        input_path = sandbox_root / "demo" / "input" / "provider_source.txt"
        input_path.write_text("external provider path", encoding="utf-8")
        payload = self._call_mcp_tool(
            "distill_and_promote_candidate",
            {
                "observed_task": {
                    "task": "Mirror one text file and write a metadata sidecar.",
                    "actions": [
                        {
                            "tool": "copy_file",
                            "input": {
                                "source_path": "demo/input/provider_source.txt",
                                "destination_path": "demo/output/provider_result.txt",
                            },
                            "result": "Mirrored source text.",
                        },
                        {
                            "tool": "write_json",
                            "input": {"metadata_path": "demo/output/provider_result.json"},
                            "result": "Wrote metadata sidecar.",
                        },
                    ],
                    "outputs": [
                        "demo/output/provider_result.txt",
                        "demo/output/provider_result.json",
                    ],
                },
                "skill_name": "core_acceptance_external_provider",
            },
            root=sandbox_root,
        )
        data = payload["data"]
        metadata = self._read_json_file(Path(data["distillation"]["metadata_file"]))
        fallback_artifact = self._read_json_file(Path(data["distillation"]["fallback_artifact"]))

        self.assertTrue(data["promoted"])
        self.assertEqual("passed", data["audit"]["report"]["status"])
        self.assertEqual("local_pass_semantic_review_provider", data["audit"]["report"]["semantic_provider"])
        self.assertEqual("llm_fallback", metadata["rule_name"])
        self.assertIn("local_copy_metadata_fallback_provider", metadata["rule_reason"])
        self.assertEqual("local_copy_metadata_fallback_provider", fallback_artifact["response"]["provider_name"])

        promoted = sandbox_index.get("core_acceptance_external_provider")
        self.assertIsNotNone(promoted)
        self.assertEqual("active", promoted.status)

        execute_payload = self._call_mcp_tool(
            "execute_skill",
            {
                "skill_name": "core_acceptance_external_provider",
                "args": {
                    "input_path": "demo/input/provider_source.txt",
                    "output_path": "demo/output/provider_reuse.txt",
                    "metadata_path": "demo/output/provider_reuse.json",
                },
            },
            root=sandbox_root,
        )
        self.assertEqual("completed", execute_payload["data"]["result"]["status"])
        self.assertEqual(
            "external provider path",
            (sandbox_root / "demo" / "output" / "provider_reuse.txt").read_text(encoding="utf-8"),
        )
        self.assertTrue((sandbox_root / "demo" / "output" / "provider_reuse.json").exists())

    def test_json_to_csv_dogfood_skill_executes_from_search(self) -> None:
        sandbox_root, _, _ = self._make_runtime_sandbox()

        search_payload = self._call_mcp_tool(
            "search_skill",
            {"query": "convert json records to csv", "top_k": 5},
            root=sandbox_root,
        )
        search_data = search_payload["data"]
        self.assertEqual("json_to_csv_dogfood", search_data["recommended_skill_name"])

        execute_args = dict(search_data["recommended_host_operation"]["arguments"])
        execute_args["args"] = {
            "input_path": "demo/input/records.json",
            "output_path": "demo/output/records_dogfood.csv",
            "delimiter": ",",
        }
        execute_payload = self._call_mcp_tool(
            search_data["recommended_host_operation"]["tool_name"],
            execute_args,
            root=sandbox_root,
        )
        output_path = sandbox_root / "demo" / "output" / "records_dogfood.csv"

        self.assertEqual("completed", execute_payload["data"]["result"]["status"])
        self.assertEqual("json_to_csv_dogfood", execute_payload["data"]["skill_name"])
        self.assertTrue(output_path.exists())
        self.assertEqual(
            "name,role\nAda,researcher\nGrace,engineer\n",
            output_path.read_text(encoding="utf-8"),
        )

    def test_directory_json_to_csv_dogfood_skill_executes_from_search(self) -> None:
        sandbox_root, _, _ = self._make_runtime_sandbox()

        search_payload = self._call_mcp_tool(
            "search_skill",
            {"query": "convert json directory to csv files", "top_k": 5},
            root=sandbox_root,
        )
        search_data = search_payload["data"]
        self.assertEqual("directory_json_to_csv_dogfood", search_data["recommended_skill_name"])

        execute_args = dict(search_data["recommended_host_operation"]["arguments"])
        execute_args["args"] = {
            "input_dir": "demo/input/json_records",
            "output_dir": "demo/output/json_records_csv_dogfood",
            "pattern": "**/*.json",
            "delimiter": ",",
        }
        execute_payload = self._call_mcp_tool(
            search_data["recommended_host_operation"]["tool_name"],
            execute_args,
            root=sandbox_root,
        )
        team_output = sandbox_root / "demo" / "output" / "json_records_csv_dogfood" / "team.csv"
        jobs_output = sandbox_root / "demo" / "output" / "json_records_csv_dogfood" / "ops" / "jobs.csv"

        self.assertEqual("completed", execute_payload["data"]["result"]["status"])
        self.assertEqual("directory_json_to_csv_dogfood", execute_payload["data"]["skill_name"])
        self.assertTrue(team_output.exists())
        self.assertTrue(jobs_output.exists())
        self.assertEqual(
            "name,team\nAda,research\nGrace,engineering\n",
            team_output.read_text(encoding="utf-8"),
        )
        self.assertEqual(
            "job_id,status\nnightly-cleanup,ok\nindex-refresh,queued\n",
            jobs_output.read_text(encoding="utf-8"),
        )

    def test_text_replace_dogfood_skill_executes_from_search(self) -> None:
        sandbox_root, _, _ = self._make_runtime_sandbox()

        search_payload = self._call_mcp_tool(
            "search_skill",
            {"query": "replace text in one file", "top_k": 5},
            root=sandbox_root,
        )
        search_data = search_payload["data"]
        self.assertEqual("text_replace_dogfood", search_data["recommended_skill_name"])

        execute_args = dict(search_data["recommended_host_operation"]["arguments"])
        execute_args["args"] = {
            "input_path": "demo/input/template_note.txt",
            "output_path": "demo/output/template_note_ready_dogfood.txt",
            "old_text": "draft",
            "new_text": "ready",
        }
        execute_payload = self._call_mcp_tool(
            search_data["recommended_host_operation"]["tool_name"],
            execute_args,
            root=sandbox_root,
        )
        output_path = sandbox_root / "demo" / "output" / "template_note_ready_dogfood.txt"

        self.assertEqual("completed", execute_payload["data"]["result"]["status"])
        self.assertEqual("text_replace_dogfood", execute_payload["data"]["skill_name"])
        self.assertTrue(output_path.exists())
        self.assertEqual(
            "Title: Weekly Update\nStatus: ready\nOwner: docs\n",
            output_path.read_text(encoding="utf-8"),
        )

    def test_directory_text_cleanup_dogfood_skill_executes_from_search(self) -> None:
        sandbox_root, _, _ = self._make_runtime_sandbox()

        search_payload = self._call_mcp_tool(
            "search_skill",
            {"query": "clean text files in a directory", "top_k": 5},
            root=sandbox_root,
        )
        search_data = search_payload["data"]
        self.assertEqual("directory_text_cleanup_dogfood", search_data["recommended_skill_name"])

        execute_args = dict(search_data["recommended_host_operation"]["arguments"])
        execute_args["args"] = {
            "input_dir": "demo/input/text_notes",
            "output_dir": "demo/output/text_notes_clean_dogfood",
            "pattern": "**/*.txt",
            "suffix": "_clean",
        }
        execute_payload = self._call_mcp_tool(
            search_data["recommended_host_operation"]["tool_name"],
            execute_args,
            root=sandbox_root,
        )
        day_output = sandbox_root / "demo" / "output" / "text_notes_clean_dogfood" / "day1_clean.txt"
        runbook_output = sandbox_root / "demo" / "output" / "text_notes_clean_dogfood" / "ops" / "runbook_clean.txt"

        self.assertEqual("completed", execute_payload["data"]["result"]["status"])
        self.assertEqual("directory_text_cleanup_dogfood", execute_payload["data"]["skill_name"])
        self.assertTrue(day_output.exists())
        self.assertTrue(runbook_output.exists())
        self.assertEqual("Daily note\nStatus: open\n", day_output.read_text(encoding="utf-8"))
        self.assertEqual("Runbook\nStep: verify\n", runbook_output.read_text(encoding="utf-8"))

    def test_pre_implementation_workflow_review_runtime_skill_points_to_global_authority(self) -> None:
        sandbox_root, _, _ = self._make_runtime_sandbox()

        search_payload = self._call_mcp_tool(
            "search_skill",
            {"query": "review workflow before implementation", "top_k": 5},
            root=sandbox_root,
        )
        search_data = search_payload["data"]
        self.assertEqual("pre_implementation_workflow_review", search_data["recommended_skill_name"])

        execute_args = dict(search_data["recommended_host_operation"]["arguments"])
        execute_args["args"] = {
            "task_description": "Build local basic active skills for merge txt, json to csv, and replace text.",
            "proposed_approach": "Spend several days implementing file skills before validating whether they help normal development.",
            "user_value_hypothesis": "Developers need less repeated setup work in real Codex development workflows.",
            "known_context": ["Codex can already handle simple local file operations with Python or shell commands."],
            "expected_outputs": ["skill_store/active/*.py"],
            "alternatives": ["Focus on default workflow integration and dashboard entered/used signals."],
            "output_path": "demo/output/pre_implementation_review.json",
        }
        execute_payload = self._call_mcp_tool(
            search_data["recommended_host_operation"]["tool_name"],
            execute_args,
            root=sandbox_root,
        )
        review_output = sandbox_root / "demo" / "output" / "pre_implementation_review.json"
        review_payload = self._read_json_file(review_output)

        self.assertEqual("completed", execute_payload["data"]["result"]["status"])
        self.assertEqual("pre_implementation_workflow_review", execute_payload["data"]["skill_name"])
        self.assertEqual("global_codex_skill_adapter", review_payload["adapter_role"])
        self.assertEqual("pre-implementation-workflow-review", review_payload["global_skill_name"])
        self.assertEqual("authoritative_global_skill", review_payload["source_role"])
        self.assertIn("C:\\Users\\Administrator\\.codex\\skills", review_payload["global_skill_path"])
        self.assertIn("Use the global Codex skill", review_payload["next_action"])

    def test_global_pre_implementation_workflow_review_defines_main_process_guardrails(self) -> None:
        skill_path = (
            Path("C:/Users/Administrator/.codex/skills")
            / "pre-implementation-workflow-review"
            / "SKILL.md"
        )
        self.assertTrue(skill_path.exists())
        content = skill_path.read_text(encoding="utf-8")

        for phrase in [
            "Do not start implementation until the workflow reaches a build-now verdict.",
            "`build_now`",
            "`manual_validation_first`",
            "`revise_direction`",
            "`do_not_build_now`",
            "smallest closed-loop validation",
            "Do not treat Skill Runtime, local skills, entered/used samples, dashboard events, or trigger validation as the product goal.",
        ]:
            self.assertIn(phrase, content)

    def test_global_auto_mode_stage_runner_supports_full_auto_finite_plan_mode(self) -> None:
        skill_path = (
            Path("C:/Users/Administrator/.codex/skills")
            / "auto-mode-stage-runner"
            / "SKILL.md"
        )
        self.assertTrue(skill_path.exists())
        content = skill_path.read_text(encoding="utf-8")

        for phrase in [
            "full-auto finite-plan mode",
            "列个长计划，然后自动推进",
            "中间不要汇报",
            "不要停下来",
            "直到计划全部完成",
            "send one consolidated final report after the plan is finished",
            "Skip intermediate stage reports in full-auto finite-plan mode.",
        ]:
            self.assertIn(phrase, content)

    def test_global_runtime_verification_selector_prefers_scoped_checks_before_fast_suite(self) -> None:
        skill_path = (
            Path("C:/Users/Administrator/.codex/skills")
            / "runtime-verification-selector"
            / "SKILL.md"
        )
        self.assertTrue(skill_path.exists())
        content = skill_path.read_text(encoding="utf-8")

        for phrase in [
            "Do not default to `python -m unittest tests.test_runtime_fast -v` for every change.",
            "For a single file or tightly scoped change, prefer:",
            "python -m py_compile <changed python files>",
            "python -m unittest <targeted test cases> -v",
            "Use `tests.test_runtime_fast` when the change touches shared behavior",
            "When you do not run `tests.test_runtime_fast`, say what narrower commands you ran and why they were enough",
        ]:
            self.assertIn(phrase, content)

    def test_workflow_error_correction_keeps_agents_lightweight(self) -> None:
        agents_content = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("workflow-error-correction", agents_content)
        self.assertIn("Do not default to `python -m unittest tests.test_runtime_fast -v` for every small change", agents_content)
        self.assertNotIn("Prefer the fast runtime suite for routine validation", agents_content)
        self.assertNotIn("Do not treat Skill Runtime, local skills", agents_content)
        self.assertNotIn("Do not continue adding or validating skills just because auto mode can keep going", agents_content)
        global_agents_content = Path("C:/Users/Administrator/.codex/AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("workflow-error-correction", global_agents_content)
        self.assertIn("Do not default to repository-wide test suites for every small change", global_agents_content)
        self.assertNotIn("Do not treat Skill Runtime, local skills", global_agents_content)
        self.assertNotIn(
            "Do not continue adding or validating skills just because auto mode can keep going",
            global_agents_content,
        )

        skill_path = (
            Path("C:/Users/Administrator/.codex/skills")
            / "workflow-error-correction"
            / "SKILL.md"
        )
        self.assertTrue(skill_path.exists())
        content = skill_path.read_text(encoding="utf-8")
        for phrase in [
            "The primary outcome is fewer repeated mistakes, not a better error log.",
            "Before taking an action in a known risk area, apply the matching guard without waiting for the user to complain.",
            "Known Mistake Guards",
            "Validation escalation: do not run repository-wide fast or full suites for every localized change",
            "If an existing guard applies, change the next action immediately.",
            "Record the mistake outside AGENTS.md",
            "Check existing correction records before creating a new one",
            "Do not require the user to repeat an already recorded mistake",
            "Create a new error record only when the repeat pattern is new",
            "classify the repeat pattern",
            "prevention rule",
            "Do not expand AGENTS.md with case-specific history",
        ]:
            self.assertIn(phrase, content)

    def test_agents_operational_workflow_skills_execute_from_search(self) -> None:
        sandbox_root, _, _ = self._make_runtime_sandbox()
        cases = [
            (
                "run auto mode stage report",
                "auto_mode_stage_runner",
                {
                    "trigger": "自动模式开始",
                    "task_goal": "Finish the current stage.",
                    "current_stage": "stage one",
                    "plan_items": ["inspect", "change", "verify"],
                    "output_path": "demo/output/auto_mode_stage.json",
                },
                "auto-mode-stage-runner",
            ),
            (
                "choose deployment strategy docker nextjs static node",
                "deployment_strategy_review",
                {
                    "project_files": ["package.json", "next.config.js"],
                    "user_label": "static",
                    "output_path": "demo/output/deployment_strategy.json",
                },
                "deployment-strategy-review",
            ),
            (
                "resume handoff update tasks decisions",
                "session_handoff_maintenance",
                {
                    "command": "继续",
                    "changed_state": ["stage completed"],
                    "output_path": "demo/output/session_handoff.json",
                },
                "session-handoff-maintenance",
            ),
            (
                "prepare runtime gate finalizer workflow",
                "runtime_gate_workflow",
                {
                    "task_description": "Update docs.",
                    "working_directory": ".",
                    "expected_outputs": ["HANDOFF.md"],
                    "output_path": "demo/output/runtime_gate.json",
                },
                "runtime-gate-workflow",
            ),
            (
                "choose fast full verification commands",
                "runtime_verification_selector",
                {
                    "change_scope": "single file syntax change",
                    "output_path": "demo/output/verification_selector.json",
                },
                "runtime-verification-selector",
            ),
            (
                "repo impact analysis symbols call chain gitnexus",
                "repo_impact_analysis",
                {
                    "target": "RuntimeService",
                    "gitnexus_available": True,
                    "indexed": True,
                    "output_path": "demo/output/repo_impact.json",
                },
                "repo-impact-analysis",
            ),
            (
                "write nontechnical stage progress report",
                "nontechnical_stage_report",
                {
                    "stage_name": "direction cleanup",
                    "completed": ["Moved rules into workflow skills."],
                    "changed_files": ["AGENTS.md"],
                    "risks": ["Needs dogfood."],
                    "output_path": "demo/output/nontechnical_stage_report.json",
                },
                "nontechnical-stage-report",
            ),
        ]

        for query, expected_skill, args, global_skill_name in cases:
            with self.subTest(skill=expected_skill):
                search_payload = self._call_mcp_tool(
                    "search_skill",
                    {"query": query, "top_k": 5},
                    root=sandbox_root,
                )
                search_data = search_payload["data"]
                self.assertEqual(expected_skill, search_data["recommended_skill_name"])

                execute_args = dict(search_data["recommended_host_operation"]["arguments"])
                execute_args["args"] = args
                execute_payload = self._call_mcp_tool(
                    search_data["recommended_host_operation"]["tool_name"],
                    execute_args,
                    root=sandbox_root,
                )
                output_path = sandbox_root / args["output_path"]
                payload = self._read_json_file(output_path)

                self.assertEqual("completed", execute_payload["data"]["result"]["status"])
                self.assertEqual(expected_skill, execute_payload["data"]["skill_name"])
                self.assertEqual("global_codex_skill_adapter", payload["adapter_role"])
                self.assertEqual(global_skill_name, payload["global_skill_name"])
                self.assertEqual("authoritative_global_skill", payload["source_role"])
                self.assertIn("C:\\Users\\Administrator\\.codex\\skills", payload["global_skill_path"])

    def _restore_env(self, name: str, value: str | None) -> None:
        if value is None:
            os.environ.pop(name, None)
            return
        os.environ[name] = value
