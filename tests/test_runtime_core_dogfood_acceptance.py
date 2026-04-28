import json
import os
import sys
import textwrap
from pathlib import Path


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
        fallback_provider = sandbox_root / "demo" / "external_fallback_provider.py"
        semantic_provider = sandbox_root / "demo" / "external_semantic_provider.py"
        fallback_provider.write_text(
            textwrap.dedent(
                '''
                import json
                import sys


                request = json.loads(sys.stdin.read())
                docstring = request["docstring"].replace("\\\\", "\\\\\\\\").replace('"""', '\\"\\"\\"')
                code = f"""def run(tools, **kwargs):
                    \\"\\"\\"
                {docstring}
                    \\"\\"\\"
                    input_path = kwargs.get("input_path")
                    output_path = kwargs.get("output_path")
                    metadata_path = kwargs.get("metadata_path")
                    missing = [
                        name
                        for name, value in {{
                            "input_path": input_path,
                            "output_path": output_path,
                            "metadata_path": metadata_path,
                        }}.items()
                        if value is None
                    ]
                    if missing:
                        raise ValueError(f"Missing required inputs: {{missing}}")

                    copied_path = tools.copy_file(input_path, output_path)
                    tools.write_json(metadata_path, {{"source": input_path, "copied_path": copied_path}})
                    return {{
                        "status": "completed",
                        "artifacts": [output_path, metadata_path],
                        "steps_executed": 3,
                        "generated_by": "command_fallback_acceptance",
                    }}
                """
                print(json.dumps({
                    "code": code,
                    "provider_name": "command_fallback_acceptance",
                    "reason": "External command provider generated executable runtime-tool code.",
                }))
                '''
            ).strip(),
            encoding="utf-8",
        )
        semantic_provider.write_text(
            textwrap.dedent(
                '''
                import json
                import sys


                json.loads(sys.stdin.read())
                print(json.dumps({
                    "provider_name": "command_semantic_acceptance",
                    "summary": "External semantic provider accepted the generated skill.",
                    "issues": [],
                }))
                '''
            ).strip(),
            encoding="utf-8",
        )
        self.addCleanup(lambda: fallback_provider.unlink(missing_ok=True))
        self.addCleanup(lambda: semantic_provider.unlink(missing_ok=True))

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
        self.assertEqual("command_semantic_acceptance", data["audit"]["report"]["semantic_provider"])
        self.assertEqual("llm_fallback", metadata["rule_name"])
        self.assertIn("command_fallback_acceptance", metadata["rule_reason"])
        self.assertEqual("command_fallback_acceptance", fallback_artifact["response"]["provider_name"])

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

    def _restore_env(self, name: str, value: str | None) -> None:
        if value is None:
            os.environ.pop(name, None)
            return
        os.environ[name] = value
