import json
import subprocess
import sys
from pathlib import Path

from skill_runtime.api.models import AgentTaskRequest
from tests.runtime_test_support import CLI, ROOT


class RuntimeAgentOrchestrationTestsMixin:
    def test_codex_task_classifier_marks_local_file_workflow_as_default_in(self) -> None:
        from skill_runtime.api.host import classify_codex_task

        classification = classify_codex_task(
            AgentTaskRequest(
                task_description="merge txt files into markdown",
                known_inputs={
                    "input_dir": "demo/input",
                    "output_path": "demo/output/codex_classifier_merge.md",
                },
                expected_outputs=["demo/output/codex_classifier_merge.md"],
                risk_level="low",
                task_kind="workflow",
            )
        )

        self.assertEqual("default-in", classification.bucket)
        self.assertIn("local-targets", classification.matched_signals)
        self.assertIn("family:local-text-transformation", classification.matched_signals)

    def test_codex_task_classifier_marks_real_state_file_maintenance_as_default_in(self) -> None:
        from skill_runtime.api.host import classify_codex_task

        classification = classify_codex_task(
            AgentTaskRequest(
                task_description="Update HANDOFF, TASKS, and DECISIONS files after a completed runtime stage.",
                known_inputs={
                    "handoff_path": "HANDOFF.md",
                    "tasks_path": "TASKS.md",
                    "decisions_path": "DECISIONS.md",
                },
                expected_outputs=["HANDOFF.md", "TASKS.md", "DECISIONS.md"],
                risk_level="low",
                task_kind="workflow",
            )
        )

        self.assertEqual("default-in", classification.bucket)
        self.assertIn("state-files", classification.matched_signals)
        self.assertIn("family:project-state-maintenance", classification.matched_signals)

    def test_codex_task_classifier_keeps_structured_handoff_continuation_default_in(self) -> None:
        from skill_runtime.api.host import classify_codex_task

        classification = classify_codex_task(
            AgentTaskRequest(
                task_description="Refresh the continuation brief from HANDOFF, TASKS, and DECISIONS state files.",
                known_inputs={
                    "handoff_path": "HANDOFF.md",
                    "tasks_path": "TASKS.md",
                    "decisions_path": "DECISIONS.md",
                },
                expected_outputs=["continuation_brief.md"],
                risk_level="low",
                task_kind="workflow",
            )
        )

        self.assertEqual("default-in", classification.bucket)
        self.assertIn("state-files", classification.matched_signals)
        self.assertIn("family:project-state-maintenance", classification.matched_signals)

    def test_codex_task_classifier_keeps_natural_language_handoff_continuation_guarded_in(self) -> None:
        from skill_runtime.api.host import classify_codex_task

        classification = classify_codex_task(
            AgentTaskRequest(
                task_description="Continue from HANDOFF.md and produce a continuation brief for the next Codex session.",
                working_directory=str(self.runtime_root),
                risk_level="low",
                task_kind="workflow",
            )
        )

        self.assertEqual("guarded-in", classification.bucket)
        self.assertIn("workspace-scoped", classification.matched_signals)
        self.assertIn("state-files", classification.matched_signals)

    def test_codex_task_classifier_marks_structured_conversion_as_default_in(self) -> None:
        from skill_runtime.api.host import classify_codex_task

        classification = classify_codex_task(
            AgentTaskRequest(
                task_description="Convert JSON records into CSV for local export.",
                known_inputs={
                    "input_path": "demo/input/json_records/records.json",
                    "output_path": "demo/output/codex_classifier_records.csv",
                },
                expected_outputs=["demo/output/codex_classifier_records.csv"],
                risk_level="low",
                task_kind="workflow",
            )
        )

        self.assertEqual("default-in", classification.bucket)
        self.assertIn("family:structured-format-conversion", classification.matched_signals)

    def test_codex_task_classifier_marks_low_risk_workspace_organization_as_default_in(self) -> None:
        from skill_runtime.api.host import classify_codex_task

        classification = classify_codex_task(
            AgentTaskRequest(
                task_description="Archive local log files into an archive folder.",
                known_inputs={
                    "source_dir": "demo/input/text_notes",
                    "output_dir": "demo/output/log_archive",
                },
                expected_outputs=["demo/output/log_archive"],
                risk_level="low",
                task_kind="workflow",
            )
        )

        self.assertEqual("default-in", classification.bucket)
        self.assertIn("family:low-risk-workspace-organization", classification.matched_signals)

    def test_codex_task_classifier_marks_open_ended_review_as_default_out(self) -> None:
        from skill_runtime.api.host import classify_codex_task

        classification = classify_codex_task(
            AgentTaskRequest(
                task_description="Review this architecture and decide the roadmap.",
                risk_level="medium",
                task_kind="workflow",
            )
        )

        self.assertEqual("default-out", classification.bucket)

    def test_codex_task_classifier_keeps_external_login_task_default_out_even_with_output_path(self) -> None:
        from skill_runtime.api.host import classify_codex_task

        classification = classify_codex_task(
            AgentTaskRequest(
                task_description="Log into a third-party website and export the account report to demo/output/report.csv.",
                known_inputs={"output_path": "demo/output/report.csv"},
                expected_outputs=["demo/output/report.csv"],
                risk_level="medium",
                task_kind="workflow",
            )
        )

        self.assertEqual("default-out", classification.bucket)

    def test_codex_task_classifier_marks_local_but_broader_refactor_as_guarded_in(self) -> None:
        from skill_runtime.api.host import classify_codex_task

        classification = classify_codex_task(
            AgentTaskRequest(
                task_description="Refactor the local runtime modules to reduce duplication.",
                working_directory=str(self.runtime_root),
                known_inputs={"target_module": "skill_runtime/api"},
                risk_level="medium",
                task_kind="workflow",
            )
        )

        self.assertEqual("guarded-in", classification.bucket)

    def test_codex_task_classifier_marks_development_workflow_as_default_in_observation(self) -> None:
        from skill_runtime.api.host import classify_codex_task

        classification = classify_codex_task(
            AgentTaskRequest(
                task_description="Implement a dashboard runtime lane regression test and update related docs.",
                working_directory=str(self.runtime_root),
                known_inputs={"target_module": "skill_runtime/dashboard"},
                expected_outputs=["tests/test_runtime_dashboard.py", "docs/codex-default-lane-observation-log.md"],
                risk_level="medium",
                task_kind="workflow",
            )
        )

        self.assertEqual("default-in", classification.bucket)
        self.assertIn("family:development-workflow-observation", classification.matched_signals)
        self.assertIn("workspace-scoped", classification.matched_signals)

    def test_codex_task_classifier_uses_development_output_paths_as_observation_signal(self) -> None:
        from skill_runtime.api.host import classify_codex_task

        classification = classify_codex_task(
            AgentTaskRequest(
                task_description="Expose captured trajectory promotion follow-ups.",
                working_directory=str(self.runtime_root),
                expected_outputs=[
                    "skill_runtime/mcp/recommendation_builders.py",
                    "tests/test_runtime_host_operations.py",
                ],
                risk_level="medium",
                task_kind="workflow",
            )
        )

        self.assertEqual("default-in", classification.bucket)
        self.assertIn("family:development-workflow-observation", classification.matched_signals)

    def test_codex_host_api_run_task_enters_runtime_lane_for_development_workflow_without_auto_execution(self) -> None:
        from skill_runtime.api.host import run_codex_task

        request = AgentTaskRequest(
            task_description="Refactor the local runtime modules and add regression tests.",
            working_directory=str(self.runtime_root),
            known_inputs={"target_module": "skill_runtime/api"},
            expected_outputs=["skill_runtime/api/classification.py", "tests/test_runtime_agent_orchestration.py"],
            risk_level="medium",
            task_kind="workflow",
            allow_silent_reuse=False,
        )

        result = run_codex_task(self.runtime_root, request)

        self.assertEqual("default-in", result.task_classification.bucket)
        self.assertIn("family:development-workflow-observation", result.task_classification.matched_signals)
        self.assertEqual("skip", result.reuse_decision.decision)
        self.assertIsNone(result.execution_payload)
        self.assertEqual("entered", result.runtime_lane_status)
        self.assertIn("entered Codex runtime lane", result.runtime_lane_reason)

        event_path = self.runtime_root / ".skill_runtime" / "runtime_lane_events.jsonl"
        events = [
            json.loads(line)
            for line in event_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.assertEqual("entered", events[-1]["runtime_lane_status"])
        self.assertEqual("default-in", events[-1]["classification_bucket"])
        self.assertIn("family:development-workflow-observation", events[-1]["matched_signals"])

    def test_codex_finalize_captures_development_workflow_as_used_runtime_participation(self) -> None:
        from skill_runtime.api.host import finalize_codex_task, run_codex_task

        request = AgentTaskRequest(
            task_description="Update the dashboard runtime lane test and observation log after a development workflow.",
            working_directory=str(self.runtime_root),
            known_inputs={"target_module": "skill_runtime/dashboard"},
            expected_outputs=["tests/test_runtime_dashboard.py", "docs/codex-default-lane-observation-log.md"],
            risk_level="medium",
            task_kind="workflow",
            allow_silent_reuse=False,
        )
        plan = run_codex_task(self.runtime_root, request)

        finalized = finalize_codex_task(
            self.runtime_root,
            plan,
            {
                "result": {
                    "status": "completed",
                    "artifacts": ["tests/test_runtime_dashboard.py", "docs/codex-default-lane-observation-log.md"],
                },
                "operation_log": [
                    {"tool_name": "read_text", "status": "success", "path": "tests/test_runtime_dashboard.py"},
                    {"tool_name": "write_text", "status": "success", "path": "tests/test_runtime_dashboard.py"},
                    {"tool_name": "write_text", "status": "success", "path": "docs/codex-default-lane-observation-log.md"},
                ],
            },
        )

        self.assertEqual("default-in", finalized.task_classification.bucket)
        self.assertEqual("new_skill_candidate", finalized.learning_decision.decision)
        self.assertEqual("used", finalized.runtime_lane_status)
        self.assertTrue(finalized.learning_capture_payload["captured"])
        event_path = self.runtime_root / ".skill_runtime" / "runtime_lane_events.jsonl"
        events = [
            json.loads(line)
            for line in event_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.assertEqual("used", events[-1]["runtime_lane_status"])
        self.assertEqual("distill_trajectory", events[-1]["recommended_next_action"])
        self.assertIn(
            "Promote captured workflow globally",
            events[-1]["available_host_operation_labels"],
        )

    def test_codex_host_api_run_task_executes_default_in_flow(self) -> None:
        from skill_runtime.api.host import run_codex_task

        request = AgentTaskRequest(
            task_description="merge txt files into markdown",
            known_inputs={
                "input_dir": "demo/input",
                "output_path": "demo/output/codex_host_merge.md",
            },
            expected_outputs=["demo/output/codex_host_merge.md"],
            risk_level="low",
            task_kind="workflow",
        )

        result = run_codex_task(self.runtime_root, request)

        self.assertEqual("default-in", result.task_classification.bucket)
        self.assertEqual("auto_execute", result.reuse_decision.decision)
        self.assertEqual("merge_text_files", result.selected_skill_name)
        self.assertEqual("used", result.runtime_lane_status)
        self.assertIn("auto-executed", result.runtime_lane_reason)
        self.assertTrue((self.runtime_root / "demo" / "output" / "codex_host_merge.md").exists())

    def test_codex_host_api_run_task_appends_runtime_lane_event(self) -> None:
        from skill_runtime.api.host import run_codex_task

        request = AgentTaskRequest(
            task_description="merge txt files into markdown",
            known_inputs={
                "input_dir": "demo/input",
                "output_path": "demo/output/codex_host_event.md",
            },
            expected_outputs=["demo/output/codex_host_event.md"],
            risk_level="low",
            task_kind="workflow",
        )

        run_codex_task(self.runtime_root, request)

        event_path = self.runtime_root / ".skill_runtime" / "runtime_lane_events.jsonl"
        self.assertTrue(event_path.exists())
        events = [
            json.loads(line)
            for line in event_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.assertEqual(1, len(events))
        self.assertEqual("used", events[0]["runtime_lane_status"])
        self.assertEqual("default-in", events[0]["classification_bucket"])
        self.assertEqual("auto_execute", events[0]["reuse_decision"])
        self.assertEqual("merge_text_files", events[0]["selected_skill_name"])
        self.assertEqual(str(self.runtime_root), events[0]["working_directory"])

    def test_codex_host_api_run_task_keeps_default_out_work_on_normal_path(self) -> None:
        from skill_runtime.api.host import run_codex_task

        request = AgentTaskRequest(
            task_description="Review this architecture and decide the roadmap.",
            risk_level="medium",
            task_kind="workflow",
        )

        result = run_codex_task(self.runtime_root, request)

        self.assertEqual("default-out", result.task_classification.bucket)
        self.assertEqual("skip", result.reuse_decision.decision)
        self.assertIsNone(result.execution_payload)
        self.assertIsNone(result.learning_decision)
        self.assertEqual("skipped", result.runtime_lane_status)
        self.assertIn("default-out", result.runtime_lane_reason)

    def test_codex_host_api_run_task_logs_skipped_runtime_lane_event(self) -> None:
        from skill_runtime.api.host import run_codex_task

        request = AgentTaskRequest(
            task_description="Review this architecture and decide the roadmap.",
            risk_level="medium",
            task_kind="workflow",
        )

        run_codex_task(self.runtime_root, request)

        event_path = self.runtime_root / ".skill_runtime" / "runtime_lane_events.jsonl"
        events = [
            json.loads(line)
            for line in event_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.assertEqual(1, len(events))
        self.assertEqual("skipped", events[0]["runtime_lane_status"])
        self.assertEqual("default-out", events[0]["classification_bucket"])
        self.assertIsNone(events[0]["selected_skill_name"])

    def test_mcp_experimental_agent_run_keeps_rollback_operations_for_safe_reversal(self) -> None:
        payload = self._call_mcp_tool(
            "run_agent_task_experimental",
            {
                "task_description": "merge txt files into markdown",
                "known_inputs": {
                    "input_dir": "demo/input",
                    "output_path": "demo/output/mcp_agent_rollback.md",
                },
                "expected_outputs": ["demo/output/mcp_agent_rollback.md"],
                "risk_level": "low",
                "task_kind": "workflow",
            },
            root=self.runtime_root,
        )

        operations = payload["data"]["execution_payload"]["available_host_operations"]
        rollback = next(
            operation for operation in operations if operation["tool_name"] == "rollback_operations"
        )
        self.assertEqual("mcp_tool_call", rollback["type"])
        self.assertIn("operation_log", rollback["arguments"])
        self.assertTrue(rollback["arguments"]["operation_log"])

    def test_mcp_experimental_agent_run_uses_host_facade_for_real_host_trial(self) -> None:
        payload = self._call_mcp_tool(
            "run_agent_task_experimental",
            {
                "task_description": "merge txt files into markdown",
                "known_inputs": {
                    "input_dir": "demo/input",
                    "output_path": "demo/output/mcp_agent_run.md",
                },
                "expected_outputs": ["demo/output/mcp_agent_run.md"],
                "risk_level": "low",
                "task_kind": "workflow",
            },
            root=self.runtime_root,
        )

        data = payload["data"]
        self.assertEqual("auto_execute", data["reuse_decision"]["decision"])
        self.assertEqual("merge_text_files", data["selected_skill_name"])
        self.assertEqual("completed", data["execution_payload"]["result"]["status"])
        self.assertEqual("skip", data["learning_decision"]["decision"])
        self.assertTrue((self.runtime_root / "demo" / "output" / "mcp_agent_run.md").exists())

    def test_mcp_experimental_agent_run_cleanly_returns_plan_for_undercovered_workflow(self) -> None:
        payload = self._call_mcp_tool(
            "run_agent_task_experimental",
            {
                "task_description": "Create a summary JSON file from a text note and save it next to the original.",
                "known_inputs": {
                    "input_path": "demo/input/template_note.txt",
                    "output_path": "demo/output/mcp_agent_undercovered.json",
                },
                "expected_outputs": ["demo/output/mcp_agent_undercovered.json"],
                "risk_level": "low",
                "task_kind": "workflow",
            },
            root=self.runtime_root,
        )

        data = payload["data"]
        self.assertEqual("skip", data["reuse_decision"]["decision"])
        self.assertIsNone(data["selected_skill_name"])
        self.assertIsNone(data["execution_payload"])
        self.assertIsNone(data["learning_decision"])
        self.assertFalse((self.runtime_root / "demo" / "output" / "mcp_agent_undercovered.json").exists())

    def test_mcp_experimental_agent_run_respects_disabled_silent_reuse(self) -> None:
        payload = self._call_mcp_tool(
            "run_agent_task_experimental",
            {
                "task_description": "merge txt files into markdown",
                "known_inputs": {
                    "input_dir": "demo/input",
                    "output_path": "demo/output/mcp_agent_no_silent.md",
                },
                "expected_outputs": ["demo/output/mcp_agent_no_silent.md"],
                "risk_level": "low",
                "task_kind": "workflow",
                "allow_silent_reuse": False,
            },
            root=self.runtime_root,
        )

        data = payload["data"]
        self.assertEqual("skip", data["reuse_decision"]["decision"])
        self.assertIsNone(data["selected_skill_name"])
        self.assertIsNone(data["execution_payload"])
        self.assertIsNone(data["learning_decision"])
        self.assertFalse((self.runtime_root / "demo" / "output" / "mcp_agent_no_silent.md").exists())

    def test_mcp_experimental_agent_finalize_captures_undercovered_workflow_for_learning(self) -> None:
        plan_payload = self._call_mcp_tool(
            "run_agent_task_experimental",
            {
                "task_description": "Create a summary JSON file from a text note and save it next to the original.",
                "known_inputs": {
                    "input_path": "demo/input/template_note.txt",
                    "output_path": "demo/output/mcp_agent_finalize.json",
                },
                "expected_outputs": ["demo/output/mcp_agent_finalize.json"],
                "risk_level": "low",
                "task_kind": "workflow",
            },
            root=self.runtime_root,
        )

        finalized_payload = self._call_mcp_tool(
            "finalize_agent_task_experimental",
            {
                "plan": plan_payload["data"],
                "execution_payload": {
                    "result": {
                        "status": "completed",
                        "artifacts": ["demo/output/mcp_agent_finalize.json"],
                    },
                    "operation_log": [
                        {
                            "tool_name": "read_text",
                            "status": "success",
                            "path": "demo/input/template_note.txt",
                        },
                        {
                            "tool_name": "write_json",
                            "status": "success",
                            "path": "demo/output/mcp_agent_finalize.json",
                        },
                    ],
                },
            },
            root=self.runtime_root,
        )

        data = finalized_payload["data"]
        self.assertEqual("new_skill_candidate", data["learning_decision"]["decision"])
        self.assertIsNotNone(data["learning_capture_payload"])
        self.assertTrue(data["learning_capture_payload"]["captured"])
        trajectory_path = Path(data["learning_capture_payload"]["trajectory_path"])
        self.assertTrue(trajectory_path.exists())
        self.assertEqual(
            "distill_trajectory",
            data["learning_capture_payload"]["recommended_next_action"],
        )
        captured_promote_operations = [
            operation
            for operation in data["learning_capture_payload"]["available_host_operations"]
            if operation["tool_name"] == "distill_and_promote_candidate"
        ]
        self.assertEqual(2, len(captured_promote_operations))
        self.assertEqual(
            {None, "global_codex"},
            {operation["arguments"].get("promotion_target") for operation in captured_promote_operations},
        )
        self.assertEqual(
            {False},
            {operation["arguments"]["register_trajectory"] for operation in captured_promote_operations},
        )
        self.assertTrue(
            all(
                operation["arguments"]["trajectory_path"] == str(trajectory_path)
                for operation in captured_promote_operations
            )
        )

    def test_mcp_experimental_agent_finalize_captures_real_project_state_update_workflow(self) -> None:
        plan_payload = self._call_mcp_tool(
            "run_agent_task_experimental",
            {
                "task_description": "Update HANDOFF, TASKS, and DECISIONS files after a completed runtime stage.",
                "known_inputs": {
                    "handoff_path": "HANDOFF.md",
                    "tasks_path": "TASKS.md",
                    "decisions_path": "DECISIONS.md",
                },
                "expected_outputs": ["HANDOFF.md", "TASKS.md", "DECISIONS.md"],
                "risk_level": "low",
                "task_kind": "workflow",
            },
            root=self.runtime_root,
        )

        self.assertEqual("skip", plan_payload["data"]["reuse_decision"]["decision"])

        finalized_payload = self._call_mcp_tool(
            "finalize_agent_task_experimental",
            {
                "plan": plan_payload["data"],
                "execution_payload": {
                    "result": {
                        "status": "completed",
                        "artifacts": ["HANDOFF.md", "TASKS.md", "DECISIONS.md"],
                    },
                    "operation_log": [
                        {"tool_name": "read_text", "status": "success", "path": "HANDOFF.md"},
                        {"tool_name": "read_text", "status": "success", "path": "TASKS.md"},
                        {"tool_name": "read_text", "status": "success", "path": "DECISIONS.md"},
                        {"tool_name": "write_text", "status": "success", "path": "HANDOFF.md"},
                        {"tool_name": "write_text", "status": "success", "path": "TASKS.md"},
                        {"tool_name": "write_text", "status": "success", "path": "DECISIONS.md"},
                    ],
                },
            },
            root=self.runtime_root,
        )

        data = finalized_payload["data"]
        self.assertEqual("new_skill_candidate", data["learning_decision"]["decision"])
        capture_payload = data["learning_capture_payload"]
        self.assertTrue(capture_payload["captured"])
        trajectory_path = Path(capture_payload["trajectory_path"])
        trajectory = self._read_json_file(trajectory_path)
        self.assertEqual(
            "Update HANDOFF, TASKS, and DECISIONS files after a completed runtime stage.",
            trajectory["task_description"],
        )
        self.assertEqual(6, len(trajectory["steps"]))
        self.assertEqual("read_text", trajectory["steps"][0]["tool_name"])
        self.assertEqual("write_text", trajectory["steps"][-1]["tool_name"])
        self.assertEqual(
            ["HANDOFF.md", "TASKS.md", "DECISIONS.md"],
            trajectory["artifacts"],
        )

    def test_mcp_experimental_codex_run_classifies_and_executes_default_in_task(self) -> None:
        payload = self._call_mcp_tool(
            "run_codex_task_experimental",
            {
                "task_description": "merge txt files into markdown",
                "known_inputs": {
                    "input_dir": "demo/input",
                    "output_path": "demo/output/mcp_codex_run.md",
                },
                "expected_outputs": ["demo/output/mcp_codex_run.md"],
                "risk_level": "low",
                "task_kind": "workflow",
            },
            root=self.runtime_root,
        )

        data = payload["data"]
        self.assertEqual("default-in", data["task_classification"]["bucket"])
        self.assertEqual("auto_execute", data["reuse_decision"]["decision"])
        self.assertEqual("merge_text_files", data["selected_skill_name"])
        self.assertTrue((self.runtime_root / "demo" / "output" / "mcp_codex_run.md").exists())

    def test_mcp_experimental_codex_run_keeps_default_out_task_on_normal_path(self) -> None:
        payload = self._call_mcp_tool(
            "run_codex_task_experimental",
            {
                "task_description": "Review this architecture and decide the roadmap.",
                "risk_level": "medium",
                "task_kind": "workflow",
            },
            root=self.runtime_root,
        )

        data = payload["data"]
        self.assertEqual("default-out", data["task_classification"]["bucket"])
        self.assertEqual("skip", data["reuse_decision"]["decision"])
        self.assertIsNone(data["execution_payload"])
        self.assertIsNone(data["learning_decision"])

    def test_mcp_experimental_codex_finalize_captures_default_in_undercovered_workflow(self) -> None:
        plan_payload = self._call_mcp_tool(
            "run_codex_task_experimental",
            {
                "task_description": "Update HANDOFF, TASKS, and DECISIONS files after a completed runtime stage.",
                "known_inputs": {
                    "handoff_path": "HANDOFF.md",
                    "tasks_path": "TASKS.md",
                    "decisions_path": "DECISIONS.md",
                },
                "expected_outputs": ["HANDOFF.md", "TASKS.md", "DECISIONS.md"],
                "risk_level": "low",
                "task_kind": "workflow",
            },
            root=self.runtime_root,
        )

        self.assertEqual("default-in", plan_payload["data"]["task_classification"]["bucket"])

        finalized_payload = self._call_mcp_tool(
            "finalize_codex_task_experimental",
            {
                "plan": plan_payload["data"],
                "execution_payload": {
                    "result": {
                        "status": "completed",
                        "artifacts": ["HANDOFF.md", "TASKS.md", "DECISIONS.md"],
                    },
                    "operation_log": [
                        {"tool_name": "read_text", "status": "success", "path": "HANDOFF.md"},
                        {"tool_name": "read_text", "status": "success", "path": "TASKS.md"},
                        {"tool_name": "read_text", "status": "success", "path": "DECISIONS.md"},
                        {"tool_name": "write_text", "status": "success", "path": "HANDOFF.md"},
                        {"tool_name": "write_text", "status": "success", "path": "TASKS.md"},
                        {"tool_name": "write_text", "status": "success", "path": "DECISIONS.md"},
                    ],
                },
            },
            root=self.runtime_root,
        )

        data = finalized_payload["data"]
        self.assertEqual("default-in", data["task_classification"]["bucket"])
        self.assertEqual("new_skill_candidate", data["learning_decision"]["decision"])
        self.assertTrue(data["learning_capture_payload"]["captured"])

    def test_host_api_run_agent_task_executes_minimal_runtime_flow(self) -> None:
        from skill_runtime.api.host import run_agent_task

        request = AgentTaskRequest(
            task_description="merge txt files into markdown",
            known_inputs={
                "input_dir": "demo/input",
                "output_path": "demo/output/host_api_merge.md",
            },
            expected_outputs=["demo/output/host_api_merge.md"],
            risk_level="low",
            task_kind="workflow",
        )

        result = run_agent_task(self.runtime_root, request)

        self.assertEqual("auto_execute", result.reuse_decision.decision)
        self.assertEqual("merge_text_files", result.selected_skill_name)
        self.assertTrue((self.runtime_root / "demo" / "output" / "host_api_merge.md").exists())
        self.assertEqual("skip", result.learning_decision.decision)

    def test_start_task_returns_combined_reuse_plan_for_upper_layer(self) -> None:
        from skill_runtime.api.orchestration import AgentOrchestrationService

        planner = AgentOrchestrationService(self.runtime_root)
        request = AgentTaskRequest(
            task_description="merge txt files into markdown",
            known_inputs={
                "input_dir": "demo/input",
                "output_path": "demo/output/start_task_merge.md",
            },
            expected_outputs=["demo/output/start_task_merge.md"],
            risk_level="low",
            task_kind="workflow",
        )

        plan = planner.start_task(request)

        self.assertEqual("auto_execute", plan.reuse_decision.decision)
        self.assertEqual("merge_text_files", plan.selected_skill_name)
        self.assertEqual(request.known_inputs, plan.selected_skill_args)
        self.assertIsNone(plan.learning_decision)
        self.assertIsNone(plan.execution_payload)

    def test_run_task_executes_auto_reused_skill_and_finalizes_learning(self) -> None:
        from skill_runtime.api.orchestration import AgentOrchestrationService

        planner = AgentOrchestrationService(self.runtime_root)
        request = AgentTaskRequest(
            task_description="merge txt files into markdown",
            known_inputs={
                "input_dir": "demo/input",
                "output_path": "demo/output/run_task_merge.md",
            },
            expected_outputs=["demo/output/run_task_merge.md"],
            risk_level="low",
            task_kind="workflow",
        )

        result = planner.run_task(request)

        self.assertEqual("auto_execute", result.reuse_decision.decision)
        self.assertEqual("merge_text_files", result.selected_skill_name)
        self.assertIsNotNone(result.execution_payload)
        self.assertEqual("completed", result.execution_payload["result"]["status"])
        self.assertTrue((self.runtime_root / "demo" / "output" / "run_task_merge.md").exists())
        self.assertEqual("skip", result.learning_decision.decision)

    def test_run_task_returns_plan_only_when_no_auto_reuse_is_available(self) -> None:
        from skill_runtime.api.orchestration import AgentOrchestrationService

        planner = AgentOrchestrationService(self.runtime_root)
        request = AgentTaskRequest(
            task_description="Create a summary JSON file from a text note and save it next to the original.",
            known_inputs={
                "input_path": "demo/input/template_note.txt",
                "output_path": "demo/output/run_task_summary.json",
            },
            expected_outputs=["demo/output/run_task_summary.json"],
            risk_level="low",
            task_kind="workflow",
        )

        result = planner.run_task(request)

        self.assertEqual("skip", result.reuse_decision.decision)
        self.assertIsNone(result.execution_payload)
        self.assertIsNone(result.learning_decision)
        self.assertIsNone(result.selected_skill_name)

    def test_plan_reuse_auto_executes_for_strong_match_with_complete_inputs(self) -> None:
        from skill_runtime.api.orchestration import AgentOrchestrationService

        planner = AgentOrchestrationService(self.runtime_root)
        request = AgentTaskRequest(
            task_description="merge txt files into markdown",
            known_inputs={
                "input_dir": "demo/input",
                "output_path": "demo/output/orchestration_merge.md",
            },
            expected_outputs=["demo/output/orchestration_merge.md"],
            risk_level="low",
            task_kind="workflow",
        )

        decision = planner.plan_reuse(request)

        self.assertEqual("auto_execute", decision.decision)
        self.assertEqual("merge_text_files", decision.skill_name)
        self.assertGreaterEqual(decision.search_score, 0.85)
        self.assertEqual([], decision.missing_inputs)

    def test_plan_reuse_falls_back_to_background_hint_when_required_inputs_are_missing(self) -> None:
        from skill_runtime.api.orchestration import AgentOrchestrationService

        planner = AgentOrchestrationService(self.runtime_root)
        request = AgentTaskRequest(
            task_description="merge txt files into markdown",
            known_inputs={"input_dir": "demo/input"},
            risk_level="low",
            task_kind="workflow",
        )

        decision = planner.plan_reuse(request)

        self.assertEqual("background_hint", decision.decision)
        self.assertEqual("merge_text_files", decision.skill_name)
        self.assertIn("output_path", decision.missing_inputs)

    def test_plan_learning_skips_when_existing_skill_already_solved_the_task_cleanly(self) -> None:
        from skill_runtime.api.orchestration import AgentOrchestrationService

        planner = AgentOrchestrationService(self.runtime_root)
        request = AgentTaskRequest(
            task_description="merge txt files into markdown",
            known_inputs={
                "input_dir": "demo/input",
                "output_path": "demo/output/orchestration_learning_skip.md",
            },
            expected_outputs=["demo/output/orchestration_learning_skip.md"],
            risk_level="low",
            task_kind="workflow",
        )
        execution_payload = self.service.execute(
            "merge_text_files",
            {
                "input_dir": "demo/input",
                "output_path": "demo/output/orchestration_learning_skip.md",
            },
        )

        decision = planner.plan_learning(request, execution_payload)

        self.assertEqual("skip", decision.decision)
        self.assertFalse(decision.should_capture_trajectory)
        self.assertFalse(decision.should_distill_now)

    def test_plan_learning_marks_new_candidate_for_concrete_successful_undercovered_workflow(self) -> None:
        from skill_runtime.api.orchestration import AgentOrchestrationService

        planner = AgentOrchestrationService(self.runtime_root)
        request = AgentTaskRequest(
            task_description="Create a summary JSON file from a text note and save it next to the original.",
            known_inputs={
                "input_path": "demo/input/template_note.txt",
                "output_path": "demo/output/orchestration_summary.json",
            },
            expected_outputs=["demo/output/orchestration_summary.json"],
            risk_level="low",
            task_kind="workflow",
        )
        execution_payload = {
            "result": {"status": "completed", "artifacts": ["demo/output/orchestration_summary.json"]},
            "operation_log": [
                {
                    "tool_name": "read_text",
                    "status": "success",
                    "path": "demo/input/template_note.txt",
                },
                {
                    "tool_name": "write_json",
                    "status": "success",
                    "path": "demo/output/orchestration_summary.json",
                },
            ],
        }

        decision = planner.plan_learning(request, execution_payload)

        self.assertEqual("new_skill_candidate", decision.decision)
        self.assertTrue(decision.should_capture_trajectory)
        self.assertTrue(decision.should_distill_now)
        self.assertIsNone(decision.related_skill_name)

    def test_plan_learning_prefers_existing_skill_improvement_when_gap_is_explicit(self) -> None:
        from skill_runtime.api.orchestration import AgentOrchestrationService

        planner = AgentOrchestrationService(self.runtime_root)
        request = AgentTaskRequest(
            task_description="Improve the direction review workflow after a user correction.",
            expected_outputs=["C:/Users/Administrator/.codex/skills/pre-implementation-workflow-review/SKILL.md"],
            risk_level="medium",
            task_kind="workflow",
        )
        execution_payload = {
            "result": {"status": "completed", "artifacts": []},
            "operation_log": [
                {"tool_name": "read_text", "status": "success", "path": "AGENTS.md"},
                {"tool_name": "write_text", "status": "success", "path": "docs/decision-note.md"},
            ],
            "skill_gap": {
                "target_skill_name": "pre_implementation_workflow_review",
                "reason": "User correction showed the workflow should challenge low-value routes earlier.",
                "evidence": ["The old route allowed low-value skill work to continue too long."],
                "proposed_changes": ["Add a guard for repeated low-value validation loops."],
                "change_type": "guardrail",
            },
        }

        decision = planner.plan_learning(request, execution_payload)

        self.assertEqual("improve_existing_skill_candidate", decision.decision)
        self.assertEqual("pre_implementation_workflow_review", decision.related_skill_name)
        self.assertTrue(decision.should_capture_trajectory)
        self.assertFalse(decision.should_distill_now)

    def test_finalize_task_attaches_learning_decision_to_existing_plan(self) -> None:
        from skill_runtime.api.orchestration import AgentOrchestrationService

        planner = AgentOrchestrationService(self.runtime_root)
        request = AgentTaskRequest(
            task_description="Create a summary JSON file from a text note and save it next to the original.",
            known_inputs={
                "input_path": "demo/input/template_note.txt",
                "output_path": "demo/output/finalize_task_summary.json",
            },
            expected_outputs=["demo/output/finalize_task_summary.json"],
            risk_level="low",
            task_kind="workflow",
        )
        plan = planner.start_task(request)
        execution_payload = {
            "result": {"status": "completed", "artifacts": ["demo/output/finalize_task_summary.json"]},
            "operation_log": [
                {"tool_name": "read_text", "status": "success", "path": "demo/input/template_note.txt"},
                {"tool_name": "write_json", "status": "success", "path": "demo/output/finalize_task_summary.json"},
            ],
        }

        finalized = planner.finalize_task(plan, execution_payload)

        self.assertEqual("skip", finalized.reuse_decision.decision)
        self.assertEqual("new_skill_candidate", finalized.learning_decision.decision)
        self.assertEqual(execution_payload, finalized.execution_payload)
        self.assertIsNotNone(finalized.learning_capture_payload)
        self.assertTrue(finalized.learning_capture_payload["captured"])
        trajectory_path = Path(finalized.learning_capture_payload["trajectory_path"])
        self.assertTrue(trajectory_path.exists())

    def test_finalize_task_persists_existing_skill_improvement_candidate(self) -> None:
        from skill_runtime.api.orchestration import AgentOrchestrationService

        planner = AgentOrchestrationService(self.runtime_root)
        request = AgentTaskRequest(
            task_description="Improve the direction review workflow after a user correction.",
            expected_outputs=["C:/Users/Administrator/.codex/skills/pre-implementation-workflow-review/SKILL.md"],
            risk_level="medium",
            task_kind="workflow",
        )
        plan = planner.start_task(request)
        execution_payload = {
            "result": {"status": "completed", "artifacts": []},
            "operation_log": [
                {"tool_name": "read_text", "status": "success", "path": "AGENTS.md"},
                {"tool_name": "write_text", "status": "success", "path": "docs/decision-note.md"},
            ],
            "skill_gap": {
                "target_skill_name": "pre_implementation_workflow_review",
                "reason": "User correction showed the workflow should challenge low-value routes earlier.",
                "evidence": ["The old route allowed low-value skill work to continue too long."],
                "proposed_changes": ["Add a guard for repeated low-value validation loops."],
            },
        }

        finalized = planner.finalize_task(plan, execution_payload)

        self.assertEqual("improve_existing_skill_candidate", finalized.learning_decision.decision)
        self.assertIsNotNone(finalized.learning_capture_payload)
        candidate = finalized.learning_capture_payload["evolution_candidate"]
        candidate_path = Path(candidate["candidate_path"])
        self.assertTrue(candidate_path.exists())
        self.assertEqual("pre_implementation_workflow_review", candidate["target_skill_name"])
        self.assertEqual("review_evolution_candidate", finalized.learning_capture_payload["recommended_next_action"])

    def test_review_evolution_candidate_creates_manual_diff_without_editing_global_skill(self) -> None:
        from skill_runtime.evolution.candidates import EvolutionCandidateStore

        global_skills_dir = self.runtime_root / "global-skills"
        skill_dir = global_skills_dir / "pre-implementation-workflow-review"
        skill_dir.mkdir(parents=True)
        skill_path = skill_dir / "SKILL.md"
        original_text = (
            "---\n"
            "name: pre-implementation-workflow-review\n"
            "description: Review direction before implementation.\n"
            "---\n\n"
            "# Pre Implementation Workflow Review\n\n"
            "Review value before building.\n"
        )
        skill_path.write_text(original_text, encoding="utf-8")
        candidate = EvolutionCandidateStore(self.runtime_root).create_candidate(
            target_skill_name="pre_implementation_workflow_review",
            source_task_description="Improve direction review after a user correction.",
            reason="The workflow should catch repeated low-value validation loops earlier.",
            evidence=["The old route kept validating runtime samples instead of reviewing product value."],
            proposed_changes=["Add a guard that redirects repeated runtime validation to the value gate."],
            risk_level="medium",
            change_type="guardrail",
        )

        result = self.service.review_evolution_candidate(
            candidate["candidate_path"],
            global_skills_dir=global_skills_dir,
        )

        self.assertFalse(result["mutated_global_skill"])
        self.assertEqual(original_text, skill_path.read_text(encoding="utf-8"))
        self.assertEqual("reviewed", result["candidate"]["status"])
        self.assertEqual("ready_for_manual_diff", result["review"]["decision"])
        self.assertTrue(Path(result["review"]["review_path"]).exists())
        diff_path = Path(result["review"]["diff_path"])
        self.assertTrue(diff_path.exists())
        diff_text = diff_path.read_text(encoding="utf-8")
        self.assertIn("Evolution Candidate Proposal", diff_text)
        self.assertIn("low-value validation loops", diff_text)

    def test_review_evolution_candidate_requests_more_evidence_before_diff(self) -> None:
        from skill_runtime.evolution.candidates import EvolutionCandidateStore

        global_skills_dir = self.runtime_root / "global-skills"
        skill_dir = global_skills_dir / "pre-implementation-workflow-review"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\nname: pre-implementation-workflow-review\n---\n\n# Skill\n",
            encoding="utf-8",
        )
        candidate = EvolutionCandidateStore(self.runtime_root).create_candidate(
            target_skill_name="pre_implementation_workflow_review",
            source_task_description="Improve direction review.",
            reason="The candidate is too vague.",
            evidence=[],
            proposed_changes=[],
        )

        result = self.service.review_evolution_candidate(
            candidate["candidate_path"],
            global_skills_dir=global_skills_dir,
        )

        self.assertEqual("needs_more_evidence", result["candidate"]["status"])
        self.assertEqual("needs_more_evidence", result["review"]["decision"])
        self.assertNotIn("diff_path", result["review"])

    def test_review_evolution_candidate_cli_returns_review_payload(self) -> None:
        from skill_runtime.evolution.candidates import EvolutionCandidateStore

        global_skills_dir = self.runtime_root / "global-skills"
        skill_dir = global_skills_dir / "pre-implementation-workflow-review"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\nname: pre-implementation-workflow-review\n---\n\n# Skill\n",
            encoding="utf-8",
        )
        candidate = EvolutionCandidateStore(self.runtime_root).create_candidate(
            target_skill_name="pre_implementation_workflow_review",
            source_task_description="Improve direction review.",
            reason="Add a clearer build gate.",
            evidence=["A repeated route slipped past the current gate."],
            proposed_changes=["Require a verdict before implementation."],
        )

        payload = self._run_cli(
            "review-evolution-candidate",
            "--candidate",
            candidate["candidate_path"],
            "--global-skills-dir",
            str(global_skills_dir),
            expect_json=True,
            root=self.runtime_root,
        )

        self.assertEqual("ok", payload["status"])
        self.assertEqual("ready_for_manual_diff", payload["data"]["review"]["decision"])

    def test_apply_evolution_candidate_requires_explicit_confirmation(self) -> None:
        from skill_runtime.evolution.candidates import EvolutionCandidateStore

        global_skills_dir = self.runtime_root / "global-skills"
        skill_dir = global_skills_dir / "pre-implementation-workflow-review"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\nname: pre-implementation-workflow-review\n---\n\n# Skill\n",
            encoding="utf-8",
        )
        candidate = EvolutionCandidateStore(self.runtime_root).create_candidate(
            target_skill_name="pre_implementation_workflow_review",
            source_task_description="Improve direction review.",
            reason="Add a clearer build gate.",
            evidence=["A repeated route slipped past the current gate."],
            proposed_changes=["Require a verdict before implementation."],
        )
        self.service.review_evolution_candidate(candidate["candidate_path"], global_skills_dir=global_skills_dir)

        with self.assertRaises(Exception) as context:
            self.service.apply_evolution_candidate(
                candidate["candidate_path"],
                global_skills_dir=global_skills_dir,
            )

        self.assertIn("confirm_apply", str(context.exception))

    def test_apply_evolution_candidate_writes_backup_and_updates_status(self) -> None:
        from skill_runtime.evolution.candidates import EvolutionCandidateStore

        global_skills_dir = self.runtime_root / "global-skills"
        skill_dir = global_skills_dir / "pre-implementation-workflow-review"
        skill_dir.mkdir(parents=True)
        skill_path = skill_dir / "SKILL.md"
        original_text = "---\nname: pre-implementation-workflow-review\n---\n\n# Skill\n"
        skill_path.write_text(original_text, encoding="utf-8")
        candidate = EvolutionCandidateStore(self.runtime_root).create_candidate(
            target_skill_name="pre_implementation_workflow_review",
            source_task_description="Improve direction review.",
            reason="Add a clearer build gate.",
            evidence=["A repeated route slipped past the current gate."],
            proposed_changes=["Require a verdict before implementation."],
        )
        self.service.review_evolution_candidate(candidate["candidate_path"], global_skills_dir=global_skills_dir)

        result = self.service.apply_evolution_candidate(
            candidate["candidate_path"],
            confirm_apply=True,
            global_skills_dir=global_skills_dir,
        )

        self.assertTrue(result["mutated_global_skill"])
        self.assertEqual("applied", result["candidate"]["status"])
        self.assertTrue(Path(result["application"]["application_path"]).exists())
        backup_path = Path(result["application"]["backup_path"])
        self.assertTrue(backup_path.exists())
        self.assertEqual(original_text, backup_path.read_text(encoding="utf-8"))
        updated_text = skill_path.read_text(encoding="utf-8")
        self.assertIn("## Evolution Update", updated_text)
        self.assertIn("Require a verdict before implementation.", updated_text)
        self.assertIn("restore_backup_file", result["application"]["rollback_hint"]["strategy"])

    def test_apply_evolution_candidate_rejects_stale_target(self) -> None:
        from skill_runtime.evolution.candidates import EvolutionCandidateStore

        global_skills_dir = self.runtime_root / "global-skills"
        skill_dir = global_skills_dir / "pre-implementation-workflow-review"
        skill_dir.mkdir(parents=True)
        skill_path = skill_dir / "SKILL.md"
        skill_path.write_text("---\nname: pre-implementation-workflow-review\n---\n\n# Skill\n", encoding="utf-8")
        candidate = EvolutionCandidateStore(self.runtime_root).create_candidate(
            target_skill_name="pre_implementation_workflow_review",
            source_task_description="Improve direction review.",
            reason="Add a clearer build gate.",
            evidence=["A repeated route slipped past the current gate."],
            proposed_changes=["Require a verdict before implementation."],
        )
        self.service.review_evolution_candidate(candidate["candidate_path"], global_skills_dir=global_skills_dir)
        skill_path.write_text(
            "---\nname: pre-implementation-workflow-review\n---\n\n# Skill\n\nChanged after review.\n",
            encoding="utf-8",
        )

        with self.assertRaises(Exception) as context:
            self.service.apply_evolution_candidate(
                candidate["candidate_path"],
                confirm_apply=True,
                global_skills_dir=global_skills_dir,
            )

        self.assertIn("changed after review", str(context.exception))

    def test_apply_evolution_candidate_cli_requires_confirm_flag(self) -> None:
        from skill_runtime.evolution.candidates import EvolutionCandidateStore

        global_skills_dir = self.runtime_root / "global-skills"
        skill_dir = global_skills_dir / "pre-implementation-workflow-review"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\nname: pre-implementation-workflow-review\n---\n\n# Skill\n",
            encoding="utf-8",
        )
        candidate = EvolutionCandidateStore(self.runtime_root).create_candidate(
            target_skill_name="pre_implementation_workflow_review",
            source_task_description="Improve direction review.",
            reason="Add a clearer build gate.",
            evidence=["A repeated route slipped past the current gate."],
            proposed_changes=["Require a verdict before implementation."],
        )
        self.service.review_evolution_candidate(candidate["candidate_path"], global_skills_dir=global_skills_dir)

        result = subprocess.run(
            [
                sys.executable,
                str(CLI),
                "--root",
                str(self.runtime_root),
                "apply-evolution-candidate",
                "--candidate",
                candidate["candidate_path"],
                "--global-skills-dir",
                str(global_skills_dir),
            ],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        payload = json.loads(result.stdout)

        self.assertNotEqual(0, result.returncode)
        self.assertEqual("error", payload["status"])
        self.assertEqual("EVOLUTION_APPLY_CONFIRMATION_REQUIRED", payload["code"])

    def test_apply_evolution_candidate_cli_applies_with_confirm_flag(self) -> None:
        from skill_runtime.evolution.candidates import EvolutionCandidateStore

        global_skills_dir = self.runtime_root / "global-skills"
        skill_dir = global_skills_dir / "pre-implementation-workflow-review"
        skill_dir.mkdir(parents=True)
        skill_path = skill_dir / "SKILL.md"
        skill_path.write_text("---\nname: pre-implementation-workflow-review\n---\n\n# Skill\n", encoding="utf-8")
        candidate = EvolutionCandidateStore(self.runtime_root).create_candidate(
            target_skill_name="pre_implementation_workflow_review",
            source_task_description="Improve direction review.",
            reason="Add a clearer build gate.",
            evidence=["A repeated route slipped past the current gate."],
            proposed_changes=["Require a verdict before implementation."],
        )
        self.service.review_evolution_candidate(candidate["candidate_path"], global_skills_dir=global_skills_dir)

        payload = self._run_cli(
            "apply-evolution-candidate",
            "--candidate",
            candidate["candidate_path"],
            "--global-skills-dir",
            str(global_skills_dir),
            "--confirm-apply",
            expect_json=True,
            root=self.runtime_root,
        )

        self.assertEqual("ok", payload["status"])
        self.assertEqual("applied", payload["data"]["candidate"]["status"])
        self.assertIn("## Evolution Update", skill_path.read_text(encoding="utf-8"))

    def test_rollback_evolution_candidate_requires_explicit_confirmation(self) -> None:
        from skill_runtime.evolution.candidates import EvolutionCandidateStore

        global_skills_dir = self.runtime_root / "global-skills"
        skill_dir = global_skills_dir / "pre-implementation-workflow-review"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\nname: pre-implementation-workflow-review\n---\n\n# Skill\n",
            encoding="utf-8",
        )
        candidate = EvolutionCandidateStore(self.runtime_root).create_candidate(
            target_skill_name="pre_implementation_workflow_review",
            source_task_description="Improve direction review.",
            reason="Add a clearer build gate.",
            evidence=["A repeated route slipped past the current gate."],
            proposed_changes=["Require a verdict before implementation."],
        )
        self.service.review_evolution_candidate(candidate["candidate_path"], global_skills_dir=global_skills_dir)
        self.service.apply_evolution_candidate(
            candidate["candidate_path"],
            confirm_apply=True,
            global_skills_dir=global_skills_dir,
        )

        with self.assertRaises(Exception) as context:
            self.service.rollback_evolution_candidate(
                candidate["candidate_path"],
                global_skills_dir=global_skills_dir,
            )

        self.assertIn("confirm_rollback", str(context.exception))

    def test_rollback_evolution_candidate_restores_backup_and_updates_status(self) -> None:
        from skill_runtime.evolution.candidates import EvolutionCandidateStore

        global_skills_dir = self.runtime_root / "global-skills"
        skill_dir = global_skills_dir / "pre-implementation-workflow-review"
        skill_dir.mkdir(parents=True)
        skill_path = skill_dir / "SKILL.md"
        original_text = "---\nname: pre-implementation-workflow-review\n---\n\n# Skill\n"
        skill_path.write_text(original_text, encoding="utf-8")
        candidate = EvolutionCandidateStore(self.runtime_root).create_candidate(
            target_skill_name="pre_implementation_workflow_review",
            source_task_description="Improve direction review.",
            reason="Add a clearer build gate.",
            evidence=["A repeated route slipped past the current gate."],
            proposed_changes=["Require a verdict before implementation."],
        )
        self.service.review_evolution_candidate(candidate["candidate_path"], global_skills_dir=global_skills_dir)
        self.service.apply_evolution_candidate(
            candidate["candidate_path"],
            confirm_apply=True,
            global_skills_dir=global_skills_dir,
        )
        self.assertIn("## Evolution Update", skill_path.read_text(encoding="utf-8"))

        result = self.service.rollback_evolution_candidate(
            candidate["candidate_path"],
            confirm_rollback=True,
            global_skills_dir=global_skills_dir,
        )

        self.assertTrue(result["mutated_global_skill"])
        self.assertEqual("rolled_back", result["candidate"]["status"])
        self.assertTrue(Path(result["rollback"]["rollback_path"]).exists())
        self.assertEqual(original_text, skill_path.read_text(encoding="utf-8"))
        self.assertEqual("restore_backup_file", result["rollback"]["rollback_hint"]["strategy"])

    def test_rollback_evolution_candidate_rejects_target_changed_after_apply(self) -> None:
        from skill_runtime.evolution.candidates import EvolutionCandidateStore

        global_skills_dir = self.runtime_root / "global-skills"
        skill_dir = global_skills_dir / "pre-implementation-workflow-review"
        skill_dir.mkdir(parents=True)
        skill_path = skill_dir / "SKILL.md"
        skill_path.write_text("---\nname: pre-implementation-workflow-review\n---\n\n# Skill\n", encoding="utf-8")
        candidate = EvolutionCandidateStore(self.runtime_root).create_candidate(
            target_skill_name="pre_implementation_workflow_review",
            source_task_description="Improve direction review.",
            reason="Add a clearer build gate.",
            evidence=["A repeated route slipped past the current gate."],
            proposed_changes=["Require a verdict before implementation."],
        )
        self.service.review_evolution_candidate(candidate["candidate_path"], global_skills_dir=global_skills_dir)
        self.service.apply_evolution_candidate(
            candidate["candidate_path"],
            confirm_apply=True,
            global_skills_dir=global_skills_dir,
        )
        skill_path.write_text(skill_path.read_text(encoding="utf-8") + "\nManual edit after apply.\n", encoding="utf-8")

        with self.assertRaises(Exception) as context:
            self.service.rollback_evolution_candidate(
                candidate["candidate_path"],
                confirm_rollback=True,
                global_skills_dir=global_skills_dir,
            )

        self.assertIn("changed after evolution apply", str(context.exception))

    def test_rollback_evolution_candidate_cli_requires_confirm_flag(self) -> None:
        from skill_runtime.evolution.candidates import EvolutionCandidateStore

        global_skills_dir = self.runtime_root / "global-skills"
        skill_dir = global_skills_dir / "pre-implementation-workflow-review"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\nname: pre-implementation-workflow-review\n---\n\n# Skill\n",
            encoding="utf-8",
        )
        candidate = EvolutionCandidateStore(self.runtime_root).create_candidate(
            target_skill_name="pre_implementation_workflow_review",
            source_task_description="Improve direction review.",
            reason="Add a clearer build gate.",
            evidence=["A repeated route slipped past the current gate."],
            proposed_changes=["Require a verdict before implementation."],
        )
        self.service.review_evolution_candidate(candidate["candidate_path"], global_skills_dir=global_skills_dir)
        self.service.apply_evolution_candidate(
            candidate["candidate_path"],
            confirm_apply=True,
            global_skills_dir=global_skills_dir,
        )

        result = subprocess.run(
            [
                sys.executable,
                str(CLI),
                "--root",
                str(self.runtime_root),
                "rollback-evolution-candidate",
                "--candidate",
                candidate["candidate_path"],
                "--global-skills-dir",
                str(global_skills_dir),
            ],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        payload = json.loads(result.stdout)

        self.assertNotEqual(0, result.returncode)
        self.assertEqual("error", payload["status"])
        self.assertEqual("EVOLUTION_ROLLBACK_CONFIRMATION_REQUIRED", payload["code"])

    def test_rollback_evolution_candidate_cli_restores_with_confirm_flag(self) -> None:
        from skill_runtime.evolution.candidates import EvolutionCandidateStore

        global_skills_dir = self.runtime_root / "global-skills"
        skill_dir = global_skills_dir / "pre-implementation-workflow-review"
        skill_dir.mkdir(parents=True)
        skill_path = skill_dir / "SKILL.md"
        original_text = "---\nname: pre-implementation-workflow-review\n---\n\n# Skill\n"
        skill_path.write_text(original_text, encoding="utf-8")
        candidate = EvolutionCandidateStore(self.runtime_root).create_candidate(
            target_skill_name="pre_implementation_workflow_review",
            source_task_description="Improve direction review.",
            reason="Add a clearer build gate.",
            evidence=["A repeated route slipped past the current gate."],
            proposed_changes=["Require a verdict before implementation."],
        )
        self.service.review_evolution_candidate(candidate["candidate_path"], global_skills_dir=global_skills_dir)
        self.service.apply_evolution_candidate(
            candidate["candidate_path"],
            confirm_apply=True,
            global_skills_dir=global_skills_dir,
        )

        payload = self._run_cli(
            "rollback-evolution-candidate",
            "--candidate",
            candidate["candidate_path"],
            "--global-skills-dir",
            str(global_skills_dir),
            "--confirm-rollback",
            expect_json=True,
            root=self.runtime_root,
        )

        self.assertEqual("ok", payload["status"])
        self.assertEqual("rolled_back", payload["data"]["candidate"]["status"])
        self.assertEqual(original_text, skill_path.read_text(encoding="utf-8"))

    def test_agent_plan_cli_returns_reuse_decision_for_workflow_request(self) -> None:
        payload = self._run_cli(
            "agent-plan",
            "--task-description",
            "merge txt files into markdown",
            "--known-inputs-json",
            '{"input_dir":"demo/input","output_path":"demo/output/cli_agent_plan.md"}',
            "--expected-outputs-json",
            '["demo/output/cli_agent_plan.md"]',
            expect_json=True,
            root=self.runtime_root,
        )

        self.assertEqual("ok", payload["status"])
        data = payload["data"]
        self.assertEqual("default-in", data["task_classification"]["bucket"])
        self.assertEqual("auto_execute", data["reuse_decision"]["decision"])
        self.assertEqual("merge_text_files", data["reuse_decision"]["skill_name"])
        self.assertEqual("entered", data["runtime_lane_status"])
        self.assertIn("auto_execute", data["runtime_lane_reason"])
        self.assertIsNone(data["learning_decision"])
        self.assertEqual("merge_text_files", data["selected_skill_name"])
        self.assertEqual(
            {
                "input_dir": "demo/input",
                "output_path": "demo/output/cli_agent_plan.md",
            },
            data["selected_skill_args"],
        )
        self.assertIsNone(data["execution_payload"])

    def test_agent_plan_learning_cli_returns_new_skill_candidate_for_successful_workflow(self) -> None:
        plan_payload = self._run_cli(
            "agent-plan",
            "--task-description",
            "Create a summary JSON file from a text note and save it next to the original.",
            "--known-inputs-json",
            '{"input_path":"demo/input/template_note.txt","output_path":"demo/output/cli_agent_learning.json"}',
            "--expected-outputs-json",
            '["demo/output/cli_agent_learning.json"]',
            expect_json=True,
            root=self.runtime_root,
        )
        payload = self._run_cli(
            "agent-plan-learning",
            "--plan-json",
            json.dumps(plan_payload["data"], ensure_ascii=False),
            "--execution-json",
            '{"result":{"status":"completed","artifacts":["demo/output/cli_agent_learning.json"]},"operation_log":[{"tool_name":"read_text","status":"success","path":"demo/input/template_note.txt"},{"tool_name":"write_json","status":"success","path":"demo/output/cli_agent_learning.json"}]}',
            expect_json=True,
            root=self.runtime_root,
        )

        self.assertEqual("ok", payload["status"])
        data = payload["data"]
        self.assertEqual("default-in", data["task_classification"]["bucket"])
        self.assertEqual("new_skill_candidate", data["learning_decision"]["decision"])
        self.assertTrue(data["learning_decision"]["should_capture_trajectory"])
        self.assertTrue(data["learning_decision"]["should_distill_now"])
        self.assertEqual("skip", data["reuse_decision"]["decision"])
        self.assertEqual(
            {
                "input_path": "demo/input/template_note.txt",
                "output_path": "demo/output/cli_agent_learning.json",
            },
            data["request"]["known_inputs"],
        )

    def test_agent_plan_cli_now_keeps_default_out_work_on_normal_path(self) -> None:
        payload = self._run_cli(
            "agent-plan",
            "--task-description",
            "Review this architecture and decide the roadmap.",
            expect_json=True,
            root=self.runtime_root,
        )

        self.assertEqual("ok", payload["status"])
        data = payload["data"]
        self.assertEqual("default-out", data["task_classification"]["bucket"])
        self.assertEqual("skip", data["reuse_decision"]["decision"])
        self.assertIsNone(data["selected_skill_name"])
        self.assertIsNone(data["learning_decision"])
        self.assertEqual("skipped", data["runtime_lane_status"])
        self.assertIn("default-out", data["runtime_lane_reason"])

    def test_codex_classify_cli_marks_state_file_maintenance_as_default_in(self) -> None:
        payload = self._run_cli(
            "codex-classify",
            "--task-description",
            "Update HANDOFF, TASKS, and DECISIONS files after a completed runtime stage.",
            "--known-inputs-json",
            '{"handoff_path":"HANDOFF.md","tasks_path":"TASKS.md","decisions_path":"DECISIONS.md"}',
            "--expected-outputs-json",
            '["HANDOFF.md","TASKS.md","DECISIONS.md"]',
            expect_json=True,
            root=self.runtime_root,
        )

        self.assertEqual("ok", payload["status"])
        self.assertEqual("default-in", payload["data"]["bucket"])
        self.assertIn("state-files", payload["data"]["matched_signals"])

    def test_codex_run_cli_executes_default_in_task(self) -> None:
        payload = self._run_cli(
            "codex-run",
            "--task-description",
            "merge txt files into markdown",
            "--known-inputs-json",
            '{"input_dir":"demo/input","output_path":"demo/output/cli_codex_run.md"}',
            "--expected-outputs-json",
            '["demo/output/cli_codex_run.md"]',
            expect_json=True,
            root=self.runtime_root,
        )

        self.assertEqual("ok", payload["status"])
        data = payload["data"]
        self.assertEqual("default-in", data["task_classification"]["bucket"])
        self.assertEqual("auto_execute", data["reuse_decision"]["decision"])
        self.assertEqual("merge_text_files", data["selected_skill_name"])
        self.assertTrue((self.runtime_root / "demo" / "output" / "cli_codex_run.md").exists())

    def test_codex_run_cli_accepts_json_file_arguments(self) -> None:
        input_dir = self.runtime_root / "codex-file-args"
        input_dir.mkdir(parents=True)
        known_inputs_path = input_dir / "known-inputs.json"
        expected_outputs_path = input_dir / "expected-outputs.json"
        known_inputs_path.write_text(
            json.dumps(
                {
                    "input_dir": "demo/input",
                    "output_path": "demo/output/cli_codex_run_file_args.md",
                }
            ),
            encoding="utf-8",
        )
        expected_outputs_path.write_text(
            json.dumps(["demo/output/cli_codex_run_file_args.md"]),
            encoding="utf-8",
        )

        payload = self._run_cli(
            "codex-run",
            "--task-description",
            "merge txt files into markdown",
            "--known-inputs-json-file",
            str(known_inputs_path),
            "--expected-outputs-json-file",
            str(expected_outputs_path),
            expect_json=True,
            root=self.runtime_root,
        )

        self.assertEqual("ok", payload["status"])
        data = payload["data"]
        self.assertEqual("default-in", data["task_classification"]["bucket"])
        self.assertEqual("merge_text_files", data["selected_skill_name"])
        self.assertTrue((self.runtime_root / "demo" / "output" / "cli_codex_run_file_args.md").exists())

    def test_codex_finalize_cli_captures_default_in_undercovered_workflow(self) -> None:
        plan_payload = self._run_cli(
            "codex-run",
            "--task-description",
            "Update HANDOFF, TASKS, and DECISIONS files after a completed runtime stage.",
            "--known-inputs-json",
            '{"handoff_path":"HANDOFF.md","tasks_path":"TASKS.md","decisions_path":"DECISIONS.md"}',
            "--expected-outputs-json",
            '["HANDOFF.md","TASKS.md","DECISIONS.md"]',
            expect_json=True,
            root=self.runtime_root,
        )

        payload = self._run_cli(
            "codex-finalize",
            "--plan-json",
            json.dumps(plan_payload["data"], ensure_ascii=False),
            "--execution-json",
            '{"result":{"status":"completed","artifacts":["HANDOFF.md","TASKS.md","DECISIONS.md"]},"operation_log":[{"tool_name":"read_text","status":"success","path":"HANDOFF.md"},{"tool_name":"read_text","status":"success","path":"TASKS.md"},{"tool_name":"read_text","status":"success","path":"DECISIONS.md"},{"tool_name":"write_text","status":"success","path":"HANDOFF.md"},{"tool_name":"write_text","status":"success","path":"TASKS.md"},{"tool_name":"write_text","status":"success","path":"DECISIONS.md"}]}',
            expect_json=True,
            root=self.runtime_root,
        )

        self.assertEqual("ok", payload["status"])
        data = payload["data"]
        self.assertEqual("default-in", data["task_classification"]["bucket"])
        self.assertEqual("new_skill_candidate", data["learning_decision"]["decision"])
        self.assertTrue(data["learning_capture_payload"]["captured"])

    def test_codex_finalize_cli_accepts_plan_and_execution_json_files(self) -> None:
        plan_payload = self._run_cli(
            "codex-run",
            "--task-description",
            "Update HANDOFF, TASKS, and DECISIONS files after a completed runtime stage.",
            "--known-inputs-json",
            '{"handoff_path":"HANDOFF.md","tasks_path":"TASKS.md","decisions_path":"DECISIONS.md"}',
            "--expected-outputs-json",
            '["HANDOFF.md","TASKS.md","DECISIONS.md"]',
            expect_json=True,
            root=self.runtime_root,
        )
        input_dir = self.runtime_root / "codex-file-args"
        input_dir.mkdir(parents=True, exist_ok=True)
        plan_path = input_dir / "plan.json"
        execution_path = input_dir / "execution.json"
        plan_path.write_text(json.dumps(plan_payload["data"], ensure_ascii=False), encoding="utf-8")
        execution_path.write_text(
            json.dumps(
                {
                    "result": {"status": "completed", "artifacts": ["HANDOFF.md", "TASKS.md", "DECISIONS.md"]},
                    "operation_log": [
                        {"tool_name": "read_text", "status": "success", "path": "HANDOFF.md"},
                        {"tool_name": "write_text", "status": "success", "path": "HANDOFF.md"},
                    ],
                }
            ),
            encoding="utf-8",
        )

        payload = self._run_cli(
            "codex-finalize",
            "--plan-json-file",
            str(plan_path),
            "--execution-json-file",
            str(execution_path),
            expect_json=True,
            root=self.runtime_root,
        )

        self.assertEqual("ok", payload["status"])
        data = payload["data"]
        self.assertEqual("default-in", data["task_classification"]["bucket"])
        self.assertEqual("new_skill_candidate", data["learning_decision"]["decision"])
        self.assertTrue(data["learning_capture_payload"]["captured"])
