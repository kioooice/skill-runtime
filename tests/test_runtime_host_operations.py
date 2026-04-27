class RuntimeHostOperationTestsMixin:
    HOST_SKILL_NAME = "merge_text_files"
    HOST_SKILL_IO_SCHEMA = {"input_dir": "str", "output_path": "str"}
    HOST_TRAJECTORY_PATH = "D:/tmp/demo.json"
    HOST_SKILL_FILE = "D:/tmp/demo.py"
    HOST_OBSERVED_TASK_PATH = "D:/tmp/observed.json"
    HOST_OBSERVED_TASK_PAYLOAD = {
        "task": "Merge txt files into markdown.",
        "actions": [{"tool": "list_files", "input": {"input_dir": "demo/input"}, "result": "Found files."}],
        "outputs": ["demo/output/merged.md"],
    }
    HOST_DUPLICATE_SKILL = "merge_text_files_generated"

    def _build_host_operation_payload_samples(self) -> dict:
        from skill_runtime.mcp.host_operations import (
            __all__ as host_operations_exports,
            action_host_operations,
            audit_skill_operation,
            archive_duplicate_candidates_action,
            archive_duplicate_candidates_operation,
            archive_fixture_skills_operation,
            collect_operations,
            distill_coverage_report_operation,
            distill_trajectory_operation,
            execute_skill_operation,
            governance_report_operation,
            governance_report_payload,
            operation_list,
            refresh_governance_report_operation,
            review_archive_volume_action,
            review_fixture_noise_action,
            search_response_payload,
            search_result_execute_skill_operation,
            search_result_payload,
            tool_call,
            tool_call_with_preview,
        )

        execute_payload = tool_call(
            "execute_skill",
            {"skill_name": self.HOST_SKILL_NAME, "args": {}},
            argument_schema={
                "skill_name": {"type": "string", "required": True, "prefilled": True},
                "args": {
                    "type": "object",
                    "required": True,
                    "prefilled": False,
                    "properties": {
                        "input_dir": {"type": "string", "required": True, "prefilled": False},
                        "output_path": {"type": "string", "required": True, "prefilled": False},
                    },
                },
            },
        )
        archive_payload = tool_call_with_preview(
            "archive_duplicate_candidates",
            {"skill_names": [self.HOST_DUPLICATE_SKILL], "dry_run": False},
            {"skill_names": [self.HOST_DUPLICATE_SKILL], "dry_run": True},
        )
        archive_helper_payload = archive_duplicate_candidates_operation(
            [self.HOST_DUPLICATE_SKILL],
            dry_run=False,
            include_preview=True,
        )
        archive_fixture_payload = archive_fixture_skills_operation(
            ["cli_merge_fixture_test", "demo_merge_fixture_test"],
            dry_run=False,
            include_preview=True,
        )
        distill_payload = distill_trajectory_operation(self.HOST_TRAJECTORY_PATH)
        audit_payload = audit_skill_operation(self.HOST_SKILL_FILE, trajectory_path=self.HOST_TRAJECTORY_PATH)
        governance_payload = governance_report_operation()
        distill_coverage_payload = distill_coverage_report_operation()
        ordered_payloads = operation_list(execute_payload, [archive_payload["preview"], archive_payload])
        archive_action = archive_duplicate_candidates_action(
            [self.HOST_DUPLICATE_SKILL],
            canonical_skill=self.HOST_SKILL_NAME,
            cluster_count=2,
            rule_name="text_merge",
        )
        action_operations = action_host_operations(
            [
                {"host_operation": archive_payload},
                {"host_operation": governance_payload},
            ]
        )
        review_action = review_archive_volume_action()
        fixture_review_action = review_fixture_noise_action(
            skill_names=["cli_merge_fixture_test", "demo_merge_fixture_test"],
            fixture_count=2,
            hidden_fixture_only_duplicate_clusters=1,
        )
        refresh_governance_operation = refresh_governance_report_operation()
        search_result_operation = search_result_execute_skill_operation(
            self.HOST_SKILL_NAME,
            self.HOST_SKILL_IO_SCHEMA,
        )
        search_result = search_result_payload(
            self.HOST_SKILL_NAME,
            "Merge txt files into markdown.",
            0.92,
            "Matched on keywords: merge, txt.",
            self.HOST_SKILL_IO_SCHEMA,
        )
        governance_report = governance_report_payload(
            {"active": 2},
            [{"canonical_skill": self.HOST_SKILL_NAME}],
            [archive_action, review_action],
            staging_count=1,
            archive_count=3,
            active_count=2,
            library_tier_counts={"stable": 1, "experimental": 1, "fixture": 0},
            library_tier_summary={
                "production_ready_count": 1,
                "experimental_count": 1,
                "fixture_count": 0,
                "fixture_only_duplicate_clusters_hidden": 0,
            },
        )
        execute_helper_payload = execute_skill_operation(
            self.HOST_SKILL_NAME,
            self.HOST_SKILL_IO_SCHEMA,
        )

        return {
            "host_operations_exports": host_operations_exports,
            "execute_payload": execute_payload,
            "archive_payload": archive_payload,
            "archive_helper_payload": archive_helper_payload,
            "archive_fixture_payload": archive_fixture_payload,
            "distill_payload": distill_payload,
            "audit_payload": audit_payload,
            "governance_payload": governance_payload,
            "distill_coverage_payload": distill_coverage_payload,
            "ordered_payloads": ordered_payloads,
            "archive_action": archive_action,
            "action_operations": action_operations,
            "review_action": review_action,
            "fixture_review_action": fixture_review_action,
            "refresh_governance_operation": refresh_governance_operation,
            "search_result_operation": search_result_operation,
            "search_result": search_result,
            "governance_report": governance_report,
            "execute_helper_payload": execute_helper_payload,
            "search_response_payload": search_response_payload,
            "collected": collect_operations(
                [execute_payload, archive_payload, archive_payload["preview"], execute_payload]
            ),
        }

    def _build_host_operation_recommendation_samples(self, payloads: dict) -> dict:
        from skill_runtime.mcp.host_operations import (
            audit_skill_recommendation,
            archive_duplicate_candidates_follow_up_recommendation,
            archive_duplicate_candidates_recommendation,
            captured_trajectory_recommendation,
            distill_coverage_report_recommendation,
            distill_trajectory_recommendation,
            distilled_skill_audit_recommendation,
            execute_skill_recommendation,
            executed_skill_promotion_recommendation,
            governance_report_recommendation,
            no_recommendation,
            promote_skill_operation,
            promoted_skill_execution_recommendation,
            recommendation_fields,
            recommendation_from_payload,
            registered_trajectory_recommendation,
            rollback_operations_recommendation,
            search_no_match_recommendation,
            search_recommended_skill_recommendation,
        )

        recommendation_payload = recommendation_fields(
            "execute_skill",
            payloads["execute_payload"],
            reason="ready",
            additional_operations=[payloads["archive_payload"]],
        )
        recommendation_with_duplicate_payload = recommendation_fields(
            "execute_skill",
            payloads["execute_payload"],
            additional_operations=[
                payloads["execute_payload"],
                payloads["archive_payload"]["preview"],
                payloads["archive_payload"],
            ],
        )
        search_execute_recommendation = search_recommended_skill_recommendation(
            self.HOST_SKILL_NAME,
            self.HOST_SKILL_IO_SCHEMA,
            additional_operations=[payloads["search_result_operation"]],
        )
        search_response = payloads["search_response_payload"](
            "merge txt files into markdown",
            [payloads["search_result"]],
            self.HOST_SKILL_NAME,
            search_execute_recommendation,
        )
        return {
            "promote_payload": promote_skill_operation(self.HOST_SKILL_FILE),
            "recommendation_payload": recommendation_payload,
            "recommendation_with_duplicate_payload": recommendation_with_duplicate_payload,
            "derived_recommendation": recommendation_from_payload(recommendation_payload),
            "derived_duplicate_recommendation": recommendation_from_payload(
                recommendation_with_duplicate_payload
            ),
            "no_recommendation_payload": no_recommendation("blocked"),
            "execute_recommendation": execute_skill_recommendation(
                self.HOST_SKILL_NAME,
                self.HOST_SKILL_IO_SCHEMA,
                reason="execute next",
            ),
            "distill_recommendation": distill_trajectory_recommendation(
                self.HOST_TRAJECTORY_PATH,
                reason="distill next",
            ),
            "registered_trajectory_follow_up": registered_trajectory_recommendation(
                self.HOST_TRAJECTORY_PATH,
                task_id="demo_task",
            ),
            "captured_trajectory_follow_up": captured_trajectory_recommendation(
                self.HOST_TRAJECTORY_PATH,
                task_id="demo_task",
            ),
            "audit_recommendation": audit_skill_recommendation(
                self.HOST_SKILL_FILE,
                trajectory_path=self.HOST_TRAJECTORY_PATH,
                reason="audit next",
            ),
            "distilled_skill_follow_up": distilled_skill_audit_recommendation(
                self.HOST_SKILL_FILE,
                self.HOST_TRAJECTORY_PATH,
                "demo_skill",
            ),
            "archive_recommendation": archive_duplicate_candidates_recommendation(
                [self.HOST_DUPLICATE_SKILL],
                dry_run=False,
                include_preview=True,
                reason="archive next",
            ),
            "executed_skill_follow_up": executed_skill_promotion_recommendation(
                self.HOST_OBSERVED_TASK_PATH,
                observed_task=self.HOST_OBSERVED_TASK_PAYLOAD,
                operation_log=[
                    {
                        "operation_id": "op_0002",
                        "tool_name": "write_text",
                        "tool_input": {"path": "demo/output/merged.md"},
                        "observation": "Wrote text to demo/output/merged.md.",
                        "status": "success",
                        "mutation": True,
                        "rollback_hint": {
                            "strategy": "delete_created_file",
                            "target_path": "demo/output/merged.md",
                        },
                    }
                ],
            ),
            "rollback_recommendation": rollback_operations_recommendation(
                [
                    {
                        "operation_id": "op_0002",
                        "tool_name": "write_text",
                        "tool_input": {"path": "demo/output/merged.md"},
                        "observation": "Wrote text to demo/output/merged.md.",
                        "status": "success",
                        "mutation": True,
                        "rollback_hint": {
                            "strategy": "delete_created_file",
                            "target_path": "demo/output/merged.md",
                        },
                    }
                ],
                operation_ids=["op_0002"],
                reason="rollback next",
            ),
            "promoted_skill_follow_up": promoted_skill_execution_recommendation(
                self.HOST_SKILL_NAME,
                self.HOST_SKILL_IO_SCHEMA,
            ),
            "search_recommendation": search_no_match_recommendation(),
            "archive_dry_run_follow_up": archive_duplicate_candidates_follow_up_recommendation(
                [self.HOST_DUPLICATE_SKILL],
                dry_run=True,
            ),
            "archive_apply_follow_up": archive_duplicate_candidates_follow_up_recommendation(
                [self.HOST_DUPLICATE_SKILL],
                dry_run=False,
            ),
            "governance_recommendation": governance_report_recommendation(reason="refresh next"),
            "distill_coverage_recommendation": distill_coverage_report_recommendation(reason="coverage next"),
            "search_execute_recommendation": search_execute_recommendation,
            "search_response": search_response,
        }

    def _build_host_operation_source_ref_samples(self) -> dict:
        from skill_runtime.mcp.host_operations import (
            source_ref_archive_duplicate_candidates,
            source_ref_archive_duplicate_candidates_apply_follow_up,
            source_ref_archive_duplicate_candidates_follow_up,
            source_ref_archive_duplicate_candidates_preview,
            source_ref_archive_fixture_skills,
            source_ref_archive_fixture_skills_apply_follow_up,
            source_ref_archive_fixture_skills_follow_up,
            source_ref_archive_fixture_skills_preview,
            source_ref_audit,
            source_ref_distill_coverage_report_refresh,
            source_ref_distill_coverage_report_view,
            source_ref_distill,
            source_ref_governance_report_refresh,
            source_ref_observed_task,
            source_ref_observed_task_rollback,
            source_ref_promote,
            source_ref_search_no_match,
            source_ref_search_no_match_inline_capture,
            source_ref_search_no_match_inline_distill,
            source_ref_search_no_match_distill,
            source_ref_search_recommended_skill,
            source_ref_skill,
            source_ref_trajectory,
        )

        return {
            "search_recommended_source_ref": source_ref_search_recommended_skill(self.HOST_SKILL_NAME),
            "search_skill_source_ref": source_ref_skill(self.HOST_SKILL_NAME),
            "search_no_match_source_ref": source_ref_search_no_match(),
            "search_no_match_inline_capture_source_ref": source_ref_search_no_match_inline_capture(),
            "search_no_match_distill_source_ref": source_ref_search_no_match_distill(),
            "search_no_match_inline_distill_source_ref": source_ref_search_no_match_inline_distill(),
            "observed_task_source_ref": source_ref_observed_task(self.HOST_OBSERVED_TASK_PATH),
            "observed_task_rollback_source_ref": source_ref_observed_task_rollback(self.HOST_OBSERVED_TASK_PATH),
            "distill_source_ref": source_ref_distill(self.HOST_SKILL_NAME),
            "audit_source_ref": source_ref_audit(self.HOST_SKILL_NAME),
            "promote_source_ref": source_ref_promote(self.HOST_SKILL_NAME),
            "trajectory_source_ref": source_ref_trajectory(self.HOST_SKILL_NAME),
            "governance_source_ref": source_ref_archive_duplicate_candidates(self.HOST_SKILL_NAME),
            "governance_preview_source_ref": source_ref_archive_duplicate_candidates_preview(self.HOST_SKILL_NAME),
            "governance_follow_up_source_ref": source_ref_archive_duplicate_candidates_follow_up(),
            "governance_apply_follow_up_source_ref": source_ref_archive_duplicate_candidates_apply_follow_up(),
            "governance_archive_fixture_source_ref": source_ref_archive_fixture_skills(),
            "governance_archive_fixture_preview_source_ref": source_ref_archive_fixture_skills_preview(),
            "governance_archive_fixture_follow_up_source_ref": source_ref_archive_fixture_skills_follow_up(),
            "governance_archive_fixture_apply_follow_up_source_ref": source_ref_archive_fixture_skills_apply_follow_up(),
            "governance_report_refresh_source_ref": source_ref_governance_report_refresh(),
            "distill_coverage_report_refresh_source_ref": source_ref_distill_coverage_report_refresh(),
            "distill_coverage_report_execution_view_source_ref": source_ref_distill_coverage_report_view("execution"),
        }

    def _build_host_operation_samples(self) -> dict:
        payloads = self._build_host_operation_payload_samples()
        recommendations = self._build_host_operation_recommendation_samples(payloads)
        source_refs = self._build_host_operation_source_ref_samples()
        return {**payloads, **recommendations, **source_refs}

    def test_host_operation_export_surface_and_tool_payload_defaults(self) -> None:
        samples = self._build_host_operation_samples()
        execute_payload = samples["execute_payload"]
        distill_payload = samples["distill_payload"]
        audit_payload = samples["audit_payload"]
        promote_payload = samples["promote_payload"]
        governance_payload = samples["governance_payload"]
        distill_coverage_payload = samples["distill_coverage_payload"]
        archive_helper_payload = samples["archive_helper_payload"]

        self.assertIn("tool_call", samples["host_operations_exports"])
        self.assertIn("execute_skill_operation", samples["host_operations_exports"])
        self.assertIn("search_recommended_skill_recommendation", samples["host_operations_exports"])
        self.assertIn("governance_report_payload", samples["host_operations_exports"])

        self._assert_host_operation_basics(
            execute_payload,
            tool_name="execute_skill",
            display_label="Run skill",
            risk_level="low",
            requires_confirmation=False,
        )
        self.assertIsNone(execute_payload["source_ref"])
        self._assert_argument_schema_entry(
            execute_payload["argument_schema"],
            "skill_name",
            field_type="string",
            required=True,
            prefilled=True,
        )
        args_properties = self._assert_execute_skill_schema(execute_payload)
        self.assertTrue(args_properties["input_dir"]["required"])
        self.assertFalse(args_properties["input_dir"]["prefilled"])
        self.assertTrue(args_properties["output_path"]["required"])
        self.assertFalse(args_properties["output_path"]["prefilled"])
        self._assert_operation_role(execute_payload, "default")
        self.assertEqual("Distill trajectory", distill_payload["display_label"])
        self.assertEqual(self.HOST_TRAJECTORY_PATH, distill_payload["arguments"]["trajectory_path"])
        self.assertEqual("Audit skill", audit_payload["display_label"])
        self.assertEqual(self.HOST_SKILL_FILE, audit_payload["arguments"]["file_path"])
        self.assertEqual("Promote skill", promote_payload["display_label"])
        self.assertEqual(self.HOST_SKILL_FILE, promote_payload["arguments"]["file_path"])
        self.assertEqual("Refresh governance report", governance_payload["display_label"])
        self.assertEqual("Refresh distill coverage report", distill_coverage_payload["display_label"])
        self.assertEqual("archive_duplicate_candidates", archive_helper_payload["tool_name"])
        self.assertTrue(archive_helper_payload["preview"]["arguments"]["dry_run"])

    def test_host_operation_recommendation_helpers_keep_roles_and_deduplicate(self) -> None:
        samples = self._build_host_operation_samples()
        recommendation_payload = samples["recommendation_payload"]
        recommendation_with_duplicate_payload = samples["recommendation_with_duplicate_payload"]
        derived_recommendation = samples["derived_recommendation"]
        derived_duplicate_recommendation = samples["derived_duplicate_recommendation"]
        ordered_payloads = samples["ordered_payloads"]
        no_recommendation_payload = samples["no_recommendation_payload"]
        execute_recommendation = samples["execute_recommendation"]
        distill_recommendation = samples["distill_recommendation"]
        registered_trajectory_follow_up = samples["registered_trajectory_follow_up"]
        captured_trajectory_follow_up = samples["captured_trajectory_follow_up"]
        audit_recommendation = samples["audit_recommendation"]
        distilled_skill_follow_up = samples["distilled_skill_follow_up"]
        archive_recommendation = samples["archive_recommendation"]
        executed_skill_follow_up = samples["executed_skill_follow_up"]
        rollback_recommendation = samples["rollback_recommendation"]
        promoted_skill_follow_up = samples["promoted_skill_follow_up"]
        search_recommendation = samples["search_recommendation"]
        archive_dry_run_follow_up = samples["archive_dry_run_follow_up"]
        archive_apply_follow_up = samples["archive_apply_follow_up"]
        distill_coverage_recommendation = samples["distill_coverage_recommendation"]
        collected = samples["collected"]

        self._assert_operation_role(ordered_payloads[0], "primary")
        self.assertEqual("execute_skill", recommendation_payload["recommended_next_action"])
        self.assertEqual("ready", recommendation_payload["recommended_reason"])
        self.assertEqual(2, len(recommendation_payload["available_host_operations"]))
        self.assertEqual(
            recommendation_payload["available_host_operations"],
            derived_recommendation["available_host_operations"],
        )
        self.assertEqual(
            recommendation_with_duplicate_payload["available_host_operations"],
            derived_duplicate_recommendation["available_host_operations"],
        )
        self.assertEqual(3, len(recommendation_with_duplicate_payload["available_host_operations"]))
        self.assertEqual(
            ["primary", "preview", "default"],
            [item["operation_role"] for item in recommendation_with_duplicate_payload["available_host_operations"]],
        )
        self.assertIsNone(no_recommendation_payload["recommended_host_operation"])
        self.assertEqual([], no_recommendation_payload["available_host_operations"])
        self.assertEqual("execute_skill", execute_recommendation["recommended_next_action"])
        self.assertEqual("distill_trajectory", distill_recommendation["recommended_next_action"])
        self.assertEqual("distill_trajectory", registered_trajectory_follow_up["recommended_next_action"])
        self.assertEqual("distill_trajectory", captured_trajectory_follow_up["recommended_next_action"])
        self.assertEqual("audit_skill", audit_recommendation["recommended_next_action"])
        self.assertEqual("audit_skill", distilled_skill_follow_up["recommended_next_action"])
        self.assertEqual("archive_duplicate_candidates", archive_recommendation["recommended_next_action"])
        self.assertEqual("distill_and_promote_candidate", executed_skill_follow_up["recommended_next_action"])
        self.assertEqual(3, len(executed_skill_follow_up["available_host_operations"]))
        self.assertEqual(
            self.HOST_OBSERVED_TASK_PAYLOAD,
            executed_skill_follow_up["available_host_operations"][1]["arguments"]["observed_task"],
        )
        self.assertEqual("execute_promote", executed_skill_follow_up["recommended_host_operation"]["operation_group"])
        self.assertEqual("path", executed_skill_follow_up["recommended_host_operation"]["delivery_mode"])
        self.assertEqual("preferred", executed_skill_follow_up["recommended_host_operation"]["variant_role"])
        self.assertEqual("execute_promote", executed_skill_follow_up["available_host_operations"][1]["operation_group"])
        self.assertEqual("inline", executed_skill_follow_up["available_host_operations"][1]["delivery_mode"])
        self.assertEqual("alternate", executed_skill_follow_up["available_host_operations"][1]["variant_role"])
        self.assertEqual("rollback_operations", executed_skill_follow_up["available_host_operations"][2]["tool_name"])
        self.assertTrue(executed_skill_follow_up["available_host_operations"][2]["requires_confirmation"])
        self.assertEqual("rollback_operations", rollback_recommendation["recommended_next_action"])
        self.assertEqual("execute_skill", promoted_skill_follow_up["recommended_next_action"])
        self.assertEqual("capture_trajectory", search_recommendation["recommended_next_action"])
        self.assertEqual(4, len(search_recommendation["available_host_operations"]))
        self.assertEqual("capture_trajectory", search_recommendation["available_host_operations"][1]["tool_name"])
        self.assertEqual(
            "distill_and_promote_candidate",
            search_recommendation["available_host_operations"][2]["tool_name"],
        )
        self.assertEqual(
            ["search_no_match_capture", "search_no_match_capture", "search_no_match_promote", "search_no_match_promote"],
            [item["operation_group"] for item in search_recommendation["available_host_operations"]],
        )
        self.assertEqual(
            {
                item["display_label"]: (item["delivery_mode"], item["variant_role"])
                for item in search_recommendation["available_host_operations"]
            },
            {
                "Capture new workflow": ("path", "preferred"),
                "Capture inline workflow": ("inline", "alternate"),
                "Promote new workflow": ("path", "preferred"),
                "Promote inline workflow": ("inline", "alternate"),
            },
        )
        self.assertEqual(
            "distill_and_promote_candidate",
            search_recommendation["available_host_operations"][3]["tool_name"],
        )
        self.assertEqual("archive_duplicate_candidates", archive_dry_run_follow_up["recommended_next_action"])
        self.assertEqual("governance_report", archive_apply_follow_up["recommended_next_action"])
        self.assertEqual("distill_coverage_report", distill_coverage_recommendation["recommended_next_action"])
        self.assertEqual(3, len(collected))
        self._assert_operation_role(collected[0], "preview")
        self._assert_operation_role(collected[1], "default")

    def test_host_operation_source_refs_and_search_payloads_match_contracts(self) -> None:
        samples = self._build_host_operation_samples()
        search_result_operation = samples["search_result_operation"]
        search_result = samples["search_result"]
        search_response = samples["search_response"]
        search_execute_recommendation = samples["search_execute_recommendation"]

        self.assertEqual(f"search:recommended_skill:{self.HOST_SKILL_NAME}", samples["search_recommended_source_ref"])
        self.assertEqual(f"skill:{self.HOST_SKILL_NAME}", samples["search_skill_source_ref"])
        self.assertEqual("search:no_strong_match", samples["search_no_match_source_ref"])
        self.assertEqual(
            "search:no_strong_match:inline_capture",
            samples["search_no_match_inline_capture_source_ref"],
        )
        self.assertEqual("search:no_strong_match:distill", samples["search_no_match_distill_source_ref"])
        self.assertEqual(
            "search:no_strong_match:inline_distill",
            samples["search_no_match_inline_distill_source_ref"],
        )
        self.assertEqual(f"observed_task:{self.HOST_OBSERVED_TASK_PATH}", samples["observed_task_source_ref"])
        self.assertEqual(
            f"observed_task:{self.HOST_OBSERVED_TASK_PATH}:rollback",
            samples["observed_task_rollback_source_ref"],
        )
        self.assertEqual(f"distill:{self.HOST_SKILL_NAME}", samples["distill_source_ref"])
        self.assertEqual(f"audit:{self.HOST_SKILL_NAME}", samples["audit_source_ref"])
        self.assertEqual(f"promote:{self.HOST_SKILL_NAME}", samples["promote_source_ref"])
        self.assertEqual(f"trajectory:{self.HOST_SKILL_NAME}", samples["trajectory_source_ref"])
        self.assertEqual(f"skill:{self.HOST_SKILL_NAME}", search_result_operation["source_ref"])
        self.assertEqual("execute_skill", search_result["recommended_next_action"])
        self.assertEqual(f"skill:{self.HOST_SKILL_NAME}", search_result["host_operation"]["source_ref"])
        self.assertEqual("merge txt files into markdown", search_response["query"])
        self.assertEqual(self.HOST_SKILL_NAME, search_response["recommended_skill_name"])
        self.assertEqual("execute_skill", search_response["recommended_next_action"])
        self.assertIn("available_host_operations", search_response)
        self.assertEqual(
            f"search:recommended_skill:{self.HOST_SKILL_NAME}",
            search_execute_recommendation["recommended_host_operation"]["source_ref"],
        )
        self._assert_operation_role(search_execute_recommendation["available_host_operations"][1], "default")

    def test_governance_host_operations_include_preview_and_follow_up_paths(self) -> None:
        samples = self._build_host_operation_samples()
        archive_action = samples["archive_action"]
        review_action = samples["review_action"]
        fixture_review_action = samples["fixture_review_action"]
        archive_payload = samples["archive_payload"]
        archive_fixture_payload = samples["archive_fixture_payload"]
        governance_report = samples["governance_report"]
        governance_recommendation = samples["governance_recommendation"]
        action_operations = samples["action_operations"]
        refresh_governance_operation = samples["refresh_governance_operation"]
        execute_helper_payload = samples["execute_helper_payload"]

        self.assertEqual("archive_duplicate_candidates", archive_action["action"])
        self.assertEqual(self.HOST_SKILL_NAME, archive_action["canonical_skill"])
        self.assertEqual(2, archive_action["cluster_count"])
        self.assertEqual("archive_duplicate_candidates", archive_action["host_operation"]["tool_name"])
        self.assertEqual("review_archive_volume", review_action["action"])
        self.assertEqual("governance_report", review_action["host_operation"]["tool_name"])
        self.assertEqual("review_fixture_noise", fixture_review_action["action"])
        self.assertEqual("archive_fixture_skills", fixture_review_action["host_operation"]["tool_name"])
        self.assertIn("fixture skills are active", fixture_review_action["reason"])
        self.assertEqual(
            ["cli_merge_fixture_test", "demo_merge_fixture_test"],
            fixture_review_action["host_operation"]["arguments"]["skill_names"],
        )
        self.assertTrue(fixture_review_action["host_operation"]["preview"]["arguments"]["dry_run"])
        self.assertEqual("Refresh governance report", refresh_governance_operation["display_label"])
        self.assertEqual(
            f"governance:archive_duplicate_candidates:{self.HOST_SKILL_NAME}",
            samples["governance_source_ref"],
        )
        self.assertEqual(
            f"governance:archive_duplicate_candidates:{self.HOST_SKILL_NAME}:preview",
            samples["governance_preview_source_ref"],
        )
        self.assertEqual("archive_duplicate_candidates:follow_up", samples["governance_follow_up_source_ref"])
        self.assertEqual(
            "archive_duplicate_candidates:apply_follow_up",
            samples["governance_apply_follow_up_source_ref"],
        )
        self.assertEqual("governance:archive_fixture_skills", samples["governance_archive_fixture_source_ref"])
        self.assertEqual(
            "governance:archive_fixture_skills:preview",
            samples["governance_archive_fixture_preview_source_ref"],
        )
        self.assertEqual(
            "archive_fixture_skills:follow_up",
            samples["governance_archive_fixture_follow_up_source_ref"],
        )
        self.assertEqual(
            "archive_fixture_skills:apply_follow_up",
            samples["governance_archive_fixture_apply_follow_up_source_ref"],
        )
        self.assertEqual("governance:report_refresh", samples["governance_report_refresh_source_ref"])
        self.assertEqual("distill_coverage:report_refresh", samples["distill_coverage_report_refresh_source_ref"])
        self.assertEqual(
            "distill_coverage:view:execution",
            samples["distill_coverage_report_execution_view_source_ref"],
        )
        self.assertEqual({"active": 2}, governance_report["status_counts"])
        self.assertEqual({"stable": 1, "experimental": 1, "fixture": 0}, governance_report["library_tier_counts"])
        self.assertEqual(1, governance_report["library_tier_summary"]["production_ready_count"])
        self.assertEqual(0, governance_report["library_tier_summary"]["fixture_only_duplicate_clusters_hidden"])
        self.assertEqual(2, len(governance_report["recommended_actions"]))
        self.assertGreaterEqual(len(governance_report["available_host_operations"]), 2)
        self.assertEqual("governance_report", governance_recommendation["recommended_next_action"])
        self.assertTrue(any(item["operation_role"] == "preview" for item in action_operations))
        self.assertTrue(any(item["tool_name"] == "governance_report" for item in action_operations))
        self._assert_execute_skill_schema(execute_helper_payload)
        self._assert_host_operation_basics(
            archive_payload,
            tool_name="archive_duplicate_candidates",
            display_label="Archive duplicates",
            risk_level="high",
            requires_confirmation=True,
        )
        self.assertIsNone(archive_payload["source_ref"])
        self._assert_argument_schema_entry(
            archive_payload["argument_schema"],
            "skill_names",
            field_type="array",
        )
        self._assert_host_operation_basics(
            archive_payload["preview"],
            tool_name="archive_duplicate_candidates",
            display_label="Preview archive",
            requires_confirmation=False,
        )
        self.assertIsNone(archive_payload["preview"]["source_ref"])
        self._assert_operation_role(archive_payload["preview"], "preview")
        self._assert_host_operation_basics(
            archive_fixture_payload,
            tool_name="archive_fixture_skills",
            display_label="Archive fixture skills",
            risk_level="high",
            requires_confirmation=True,
        )
        self._assert_host_operation_basics(
            archive_fixture_payload["preview"],
            tool_name="archive_fixture_skills",
            display_label="Preview fixture archive",
            requires_confirmation=False,
        )
