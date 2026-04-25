import asyncio
import json
import subprocess
import sys
import unittest
from dataclasses import asdict
from pathlib import Path

from skill_runtime.api.models import Trajectory, TrajectoryStep
from skill_runtime.api.service import RuntimeService
from skill_runtime.audit.skill_auditor import SkillAuditor
from skill_runtime.distill.skill_generator import SkillGenerator
from skill_runtime.governance.provenance_backfill import ProvenanceBackfill
from skill_runtime.memory.trajectory_capture import TrajectoryCapture
from skill_runtime.memory.trajectory_store import TrajectoryStore, TrajectoryValidationError
from skill_runtime.mcp.server import build_mcp_server
from skill_runtime.retrieval.skill_index import SkillIndex
from scripts.skill_mcp_server import resolve_runtime_root


ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / "scripts" / "skill_cli.py"


class RuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.index = SkillIndex(ROOT / "skill_store" / "index.json")
        self.index.rebuild_from_directory(ROOT / "skill_store" / "active")
        self.service = RuntimeService(ROOT)

    def _activate_generated_skill(self, generated: dict) -> None:
        module_path = generated["skill_file"]
        metadata = generated["metadata"]

        active_dir = ROOT / "skill_store" / "active"
        active_dir.mkdir(parents=True, exist_ok=True)
        active_skill = active_dir / module_path.name
        active_skill.write_text(module_path.read_text(encoding="utf-8"), encoding="utf-8")

        active_metadata = active_dir / f"{metadata.skill_name}.metadata.json"
        metadata.file_path = str(active_skill.resolve())
        metadata.status = "active"
        active_metadata.write_text(
            json.dumps(asdict(metadata), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        self.index.upsert(metadata)

    def test_trajectory_loads(self) -> None:
        store = TrajectoryStore(ROOT / "trajectories")
        trajectory = store.load("demo_merge_text_files")
        self.assertEqual("demo_merge_text_files", trajectory.task_id)
        self.assertEqual("success", trajectory.final_status)

    def test_invalid_trajectory_rejected(self) -> None:
        store = TrajectoryStore(ROOT / "trajectories")
        invalid_path = ROOT / "trajectories" / "invalid.json"
        invalid_path.write_text(json.dumps({"task_id": "bad"}), encoding="utf-8")
        self.addCleanup(invalid_path.unlink)
        with self.assertRaises(TrajectoryValidationError):
            store.load_file(invalid_path)

    def test_capture_trajectory_from_observed_task_record(self) -> None:
        observed_path = ROOT / "demo" / "observed_capture.json"
        observed_path.write_text(
            json.dumps(
                {
                    "task_description": "Move all log files from inbox to archive.",
                    "steps": [
                        {
                            "tool_name": "list_files",
                            "tool_input": {"input_dir": "demo/inbox", "pattern": "*.log"},
                            "observation": "Found 2 log files.",
                        },
                        {
                            "tool_name": "move_file",
                            "tool_input": {"input_dir": "demo/inbox", "output_dir": "demo/archive"},
                            "observation": "Moved the matching files.",
                        },
                    ],
                    "artifacts": ["demo/archive/job1.log"],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        self.addCleanup(observed_path.unlink)

        trajectory, saved_path = TrajectoryCapture(ROOT / "trajectories").capture(
            observed_path,
            task_id="capture_test_task",
            session_id="capture_test_session",
        )
        self.addCleanup(saved_path.unlink)

        self.assertEqual("capture_test_task", trajectory.task_id)
        self.assertEqual("capture_test_session", trajectory.session_id)
        self.assertEqual("success", trajectory.final_status)
        self.assertEqual("1", trajectory.steps[0].step_id)
        self.assertTrue(saved_path.exists())

    def test_capture_trajectory_accepts_compact_observed_record_aliases(self) -> None:
        observed_path = ROOT / "demo" / "observed_capture_compact.json"
        observed_path.write_text(
            json.dumps(
                {
                    "task": "Move all log files from inbox to archive.",
                    "actions": [
                        {
                            "tool": "list_files",
                            "input": {"input_dir": "demo/inbox", "pattern": "*.log"},
                            "result": "Found 2 log files.",
                        },
                        {
                            "action": "move_file",
                            "args": {"input_dir": "demo/inbox", "output_dir": "demo/archive"},
                            "output": "Moved the matching files.",
                            "state": "success",
                        },
                    ],
                    "outputs": ["demo/archive/job1.log"],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        self.addCleanup(observed_path.unlink)

        trajectory, saved_path = TrajectoryCapture(ROOT / "trajectories").capture(
            observed_path,
            task_id="capture_compact_test_task",
            session_id="capture_compact_session",
        )
        self.addCleanup(saved_path.unlink)

        self.assertEqual("capture_compact_test_task", trajectory.task_id)
        self.assertEqual("capture_compact_session", trajectory.session_id)
        self.assertEqual("list_files", trajectory.steps[0].tool_name)
        self.assertEqual("move_file", trajectory.steps[1].tool_name)
        self.assertEqual("Moved the matching files.", trajectory.steps[1].observation)
        self.assertEqual(["demo/archive/job1.log"], trajectory.artifacts)

    def test_capture_trajectory_accepts_nested_tool_call_logs(self) -> None:
        observed_path = ROOT / "demo" / "observed_capture_nested.json"
        observed_path.write_text(
            json.dumps(
                {
                    "goal": "Move all log files from inbox to archive.",
                    "records": [
                        {
                            "tool": {
                                "name": "list_files",
                                "arguments": {"input_dir": "demo/inbox", "pattern": "*.log"},
                            },
                            "result": {
                                "message": "Found 2 log files.",
                                "status": "success",
                            },
                        },
                        {
                            "call": {
                                "name": "move_file",
                                "arguments": {"input_dir": "demo/inbox", "output_dir": "demo/archive"},
                            },
                            "result": {
                                "output": "Moved the matching files.",
                                "success": True,
                                "outputs": ["demo/archive/job1.log"],
                            },
                        },
                    ],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        self.addCleanup(observed_path.unlink)

        trajectory, saved_path = TrajectoryCapture(ROOT / "trajectories").capture(
            observed_path,
            task_id="capture_nested_test_task",
            session_id="capture_nested_session",
        )
        self.addCleanup(saved_path.unlink)

        self.assertEqual("capture_nested_test_task", trajectory.task_id)
        self.assertEqual("list_files", trajectory.steps[0].tool_name)
        self.assertEqual({"input_dir": "demo/inbox", "pattern": "*.log"}, trajectory.steps[0].tool_input)
        self.assertEqual("move_file", trajectory.steps[1].tool_name)
        self.assertEqual("Moved the matching files.", trajectory.steps[1].observation)
        self.assertEqual(["demo/archive/job1.log"], trajectory.artifacts)

    def test_service_capture_trajectory_returns_saved_file(self) -> None:
        observed_path = ROOT / "demo" / "observed_service_capture.json"
        observed_path.write_text(
            json.dumps(
                {
                    "task_description": "Rename matching files with a prefix.",
                    "steps": [
                        {
                            "tool_name": "list_files",
                            "tool_input": {"input_dir": "demo/input", "pattern": "*.txt"},
                            "observation": "Collected rename candidates.",
                        },
                        {
                            "tool_name": "rename_path",
                            "tool_input": {"input_dir": "demo/input", "prefix": "done_"},
                            "observation": "Renamed matching files.",
                        },
                    ],
                    "final_status": "success",
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        self.addCleanup(observed_path.unlink)

        result = self.service.capture_trajectory(
            observed_path,
            task_id="service_capture_test",
            session_id="service_capture_session",
        )
        saved_path = Path(result["trajectory_path"])
        self.addCleanup(saved_path.unlink)

        self.assertTrue(result["captured"])
        self.assertEqual("service_capture_test", result["task_id"])
        self.assertTrue(saved_path.exists())
        self.assertEqual("distill_trajectory", result["recommended_next_action"])
        self.assertEqual("distill_trajectory", result["recommended_host_operation"]["tool_name"])
        self.assertEqual(result["trajectory_path"], result["recommended_host_operation"]["arguments"]["trajectory_path"])
        self.assertEqual("primary", result["available_host_operations"][0]["operation_role"])

    def test_service_log_trajectory_returns_distill_follow_up(self) -> None:
        result = self.service.log_trajectory(ROOT / "trajectories" / "demo_merge_text_files.json")
        self.assertTrue(result["registered"])
        self.assertEqual("distill_trajectory", result["recommended_next_action"])
        self.assertEqual("distill_trajectory", result["recommended_host_operation"]["tool_name"])
        self.assertEqual(
            result["trajectory_path"],
            result["recommended_host_operation"]["arguments"]["trajectory_path"],
        )

    def test_search_returns_active_skill(self) -> None:
        results = self.index.search("merge txt files into markdown", top_k=20)
        self.assertTrue(results)
        names = {result["skill_name"] for result in results}
        self.assertIn("merge_text_files", names)
        first = results[0]
        self.assertEqual("merge_text_files", first["skill_name"])
        self.assertEqual("execute_skill", first["recommended_next_action"])
        self.assertIn("rule_name", first)
        self.assertIn("rule_reason", first)
        self.assertEqual("stable", first["library_tier"])
        self.assertIn("score_breakdown", first)
        self.assertGreater(first["score_breakdown"]["usage"], 0)
        self.assertEqual("mcp_tool_call", first["host_operation"]["type"])
        self.assertEqual("execute_skill", first["host_operation"]["tool_name"])
        self.assertEqual("merge_text_files", first["host_operation"]["arguments"]["skill_name"])
        self.assertEqual({}, first["host_operation"]["arguments"]["args"])
        self.assertTrue(first["host_operation"]["operation_id"])
        self.assertEqual("skill:merge_text_files", first["host_operation"]["source_ref"])
        self.assertEqual("Run skill", first["host_operation"]["display_label"])
        self.assertTrue(first["host_operation"]["effect_summary"])
        self.assertEqual("low", first["host_operation"]["risk_level"])
        self.assertFalse(first["host_operation"]["requires_confirmation"])
        self.assertIsNone(first["host_operation"]["confirmation_message"])
        self.assertEqual("string", first["host_operation"]["argument_schema"]["skill_name"]["type"])
        self.assertEqual("object", first["host_operation"]["argument_schema"]["args"]["type"])
        self.assertIn("properties", first["host_operation"]["argument_schema"]["args"])
        self.assertEqual(
            "string",
            first["host_operation"]["argument_schema"]["args"]["properties"]["input_dir"]["type"],
        )
        self.assertTrue(
            first["host_operation"]["argument_schema"]["args"]["properties"]["input_dir"]["required"]
        )
        self.assertFalse(
            first["host_operation"]["argument_schema"]["args"]["properties"]["input_dir"]["prefilled"]
        )
        self.assertEqual(
            "string",
            first["host_operation"]["argument_schema"]["args"]["properties"]["output_path"]["type"],
        )

    def test_service_search_matches_cli_shape(self) -> None:
        payload = self.service.search("merge txt files into markdown", top_k=3)
        self.assertEqual("merge txt files into markdown", payload["query"])
        self.assertTrue(payload["results"])
        self.assertEqual("execute_skill", payload["recommended_next_action"])
        self.assertEqual("merge_text_files", payload["recommended_skill_name"])
        self.assertIn("why_matched", payload["results"][0])
        self.assertIn("score_breakdown", payload["results"][0])
        self.assertEqual("mcp_tool_call", payload["recommended_host_operation"]["type"])
        self.assertEqual("execute_skill", payload["recommended_host_operation"]["tool_name"])
        self.assertEqual("merge_text_files", payload["recommended_host_operation"]["arguments"]["skill_name"])
        self.assertTrue(payload["recommended_host_operation"]["operation_id"])
        self.assertEqual("search:recommended_skill:merge_text_files", payload["recommended_host_operation"]["source_ref"])
        self.assertEqual("Run recommended skill", payload["recommended_host_operation"]["display_label"])
        self.assertTrue(payload["recommended_host_operation"]["effect_summary"])
        self.assertIsNone(payload["recommended_host_operation"]["confirmation_message"])
        self.assertEqual("string", payload["recommended_host_operation"]["argument_schema"]["skill_name"]["type"])
        self.assertEqual("object", payload["recommended_host_operation"]["argument_schema"]["args"]["type"])
        self.assertIn("properties", payload["recommended_host_operation"]["argument_schema"]["args"])
        self.assertEqual(
            "string",
            payload["recommended_host_operation"]["argument_schema"]["args"]["properties"]["input_dir"]["type"],
        )
        self.assertEqual(
            "string",
            payload["recommended_host_operation"]["argument_schema"]["args"]["properties"]["output_path"]["type"],
        )
        self.assertTrue(payload["available_host_operations"])
        self.assertEqual("execute_skill", payload["available_host_operations"][0]["tool_name"])
        self.assertEqual("primary", payload["available_host_operations"][0]["operation_role"])
        self.assertGreaterEqual(len(payload["available_host_operations"]), 2)
        self.assertEqual("default", payload["available_host_operations"][1]["operation_role"])
        self.assertIn(
            payload["available_host_operations"][1]["operation_id"],
            {item["host_operation"]["operation_id"] for item in payload["results"][1:]},
        )

    def test_mcp_search_tool_returns_structured_payload(self) -> None:
        server = build_mcp_server(ROOT)
        _, payload = asyncio.run(
            server.call_tool("search_skill", {"query": "merge txt files into markdown", "top_k": 3})
        )
        self.assertEqual("ok", payload["status"])
        self.assertTrue(payload["data"]["results"])
        self.assertEqual("execute_skill", payload["data"]["recommended_next_action"])
        self.assertEqual("merge_text_files", payload["data"]["recommended_skill_name"])
        self.assertIn("rule_name", payload["data"]["results"][0])
        self.assertIn("score_breakdown", payload["data"]["results"][0])
        self.assertEqual("mcp_tool_call", payload["data"]["recommended_host_operation"]["type"])
        self.assertEqual("execute_skill", payload["data"]["results"][0]["host_operation"]["tool_name"])

    def test_search_deprioritizes_experimental_skill_names(self) -> None:
        results = self.index.search("merge txt files into markdown", top_k=10)
        experimental = next(result for result in results if result["skill_name"] == "merge_text_files_generated")
        stable = next(result for result in results if result["skill_name"] == "merge_text_files")
        self.assertEqual("experimental", experimental["library_tier"])
        self.assertEqual("stable", stable["library_tier"])
        self.assertGreater(stable["score"], experimental["score"])
        self.assertLess(experimental["score_breakdown"]["library_penalty"], 0)

    def test_mcp_capture_trajectory_tool_returns_structured_payload(self) -> None:
        observed_path = ROOT / "demo" / "observed_mcp_capture.json"
        observed_path.write_text(
            json.dumps(
                {
                    "task_description": "Convert a CSV file into a JSON array file.",
                    "steps": [
                        {
                            "tool_name": "read_text",
                            "tool_input": {"input_path": "demo/input/table.csv"},
                            "observation": "Read CSV input.",
                        },
                        {
                            "tool_name": "write_json",
                            "tool_input": {"output_path": "demo/output/table.json"},
                            "observation": "Wrote JSON output.",
                        },
                    ],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        self.addCleanup(observed_path.unlink)

        server = build_mcp_server(ROOT)
        _, payload = asyncio.run(
            server.call_tool(
                "capture_trajectory",
                {
                    "file_path": str(observed_path),
                    "task_id": "mcp_capture_test",
                    "session_id": "mcp_capture_session",
                },
            )
        )
        saved_path = Path(payload["data"]["trajectory_path"])
        self.addCleanup(saved_path.unlink)

        self.assertEqual("ok", payload["status"])
        self.assertTrue(payload["data"]["captured"])
        self.assertEqual("mcp_capture_test", payload["data"]["task_id"])
        self.assertEqual("distill_trajectory", payload["data"]["recommended_next_action"])
        self.assertEqual("distill_trajectory", payload["data"]["recommended_host_operation"]["tool_name"])

    def test_mcp_log_trajectory_returns_distill_follow_up(self) -> None:
        server = build_mcp_server(ROOT)
        _, payload = asyncio.run(
            server.call_tool(
                "log_trajectory",
                {"file_path": str(ROOT / "trajectories" / "demo_merge_text_files.json")},
            )
        )
        self.assertEqual("ok", payload["status"])
        self.assertTrue(payload["data"]["registered"])
        self.assertEqual("distill_trajectory", payload["data"]["recommended_next_action"])
        self.assertEqual("distill_trajectory", payload["data"]["recommended_host_operation"]["tool_name"])

    def test_service_search_without_matches_recommends_distill_and_promote(self) -> None:
        payload = self.service.search("nonexistent workflow phrase for zero matches", top_k=3)
        self.assertEqual("capture_trajectory", payload["recommended_next_action"])
        self.assertIsNone(payload["recommended_skill_name"])
        self.assertTrue(payload["results"])
        self.assertLess(payload["results"][0]["score"], self.service.RECOMMENDED_EXECUTION_SCORE)
        self.assertEqual("mcp_tool_call", payload["recommended_host_operation"]["type"])
        self.assertEqual("capture_trajectory", payload["recommended_host_operation"]["tool_name"])
        self.assertEqual({}, payload["recommended_host_operation"]["arguments"])
        self.assertTrue(payload["recommended_host_operation"]["operation_id"])
        self.assertEqual("search:no_strong_match", payload["recommended_host_operation"]["source_ref"])
        self.assertEqual("Capture new workflow", payload["recommended_host_operation"]["display_label"])
        self.assertTrue(payload["recommended_host_operation"]["effect_summary"])
        self.assertFalse(payload["recommended_host_operation"]["requires_confirmation"])
        self.assertIsNone(payload["recommended_host_operation"]["confirmation_message"])
        self.assertEqual("string", payload["recommended_host_operation"]["argument_schema"]["file_path"]["type"])
        self.assertFalse(payload["recommended_host_operation"]["argument_schema"]["file_path"]["prefilled"])
        self.assertEqual("string", payload["recommended_host_operation"]["argument_schema"]["task_id"]["type"])
        self.assertEqual("string", payload["recommended_host_operation"]["argument_schema"]["session_id"]["type"])
        self.assertEqual(2, len(payload["available_host_operations"]))
        self.assertEqual("primary", payload["available_host_operations"][0]["operation_role"])
        self.assertEqual("capture_trajectory", payload["available_host_operations"][0]["tool_name"])
        self.assertEqual("distill_and_promote_candidate", payload["available_host_operations"][1]["tool_name"])
        self.assertEqual("string", payload["available_host_operations"][1]["argument_schema"]["trajectory_path"]["type"])
        self.assertFalse(payload["available_host_operations"][1]["argument_schema"]["trajectory_path"]["prefilled"])
        self.assertEqual("string", payload["available_host_operations"][1]["argument_schema"]["observed_task_path"]["type"])
        self.assertFalse(payload["available_host_operations"][1]["argument_schema"]["observed_task_path"]["prefilled"])
        self.assertEqual("string", payload["available_host_operations"][1]["argument_schema"]["skill_name"]["type"])
        self.assertEqual("boolean", payload["available_host_operations"][1]["argument_schema"]["register_trajectory"]["type"])

    def test_mcp_search_without_matches_returns_capture_primary(self) -> None:
        server = build_mcp_server(ROOT)
        _, payload = asyncio.run(
            server.call_tool(
                "search_skill",
                {"query": "nonexistent workflow phrase for zero matches", "top_k": 3},
            )
        )
        self.assertEqual("ok", payload["status"])
        self.assertEqual("capture_trajectory", payload["data"]["recommended_next_action"])
        self.assertEqual("capture_trajectory", payload["data"]["recommended_host_operation"]["tool_name"])

    def test_mcp_server_root_resolution(self) -> None:
        self.assertEqual(ROOT, resolve_runtime_root())
        self.assertEqual(ROOT, resolve_runtime_root(str(ROOT)))

    def test_service_distill_and_promote_flow(self) -> None:
        result = self.service.distill_and_promote(
            trajectory_path=ROOT / "trajectories" / "demo_merge_text_files.json",
            skill_name="service_distill_and_promote_test",
        )
        self.assertTrue(result["promoted"])
        self.assertIsNotNone(result["trajectory"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("service_distill_and_promote_test", result["promotion"]["skill_name"])

        promoted = self.index.get("service_distill_and_promote_test")
        self.assertIsNotNone(promoted)
        self.assertEqual("active", promoted.status)
        self.assertEqual("execute_skill", result["recommended_next_action"])
        self.assertEqual("execute_skill", result["recommended_host_operation"]["tool_name"])
        self.assertEqual(
            "service_distill_and_promote_test",
            result["recommended_host_operation"]["arguments"]["skill_name"],
        )

    def test_service_distill_returns_audit_follow_up_host_operation(self) -> None:
        result = self.service.distill(
            ROOT / "trajectories" / "demo_merge_text_files.json",
            skill_name="service_distill_followup_test",
        )
        self.assertEqual("audit_skill", result["recommended_next_action"])
        self.assertEqual("audit_skill", result["recommended_host_operation"]["tool_name"])
        self.assertEqual(result["staging_file"], result["recommended_host_operation"]["arguments"]["file_path"])
        self.assertEqual(
            result["trajectory_path"],
            result["recommended_host_operation"]["arguments"]["trajectory_path"],
        )
        self.assertEqual("primary", result["available_host_operations"][0]["operation_role"])

    def test_service_distill_and_promote_from_observed_task(self) -> None:
        observed_path = ROOT / "demo" / "observed_distill_promote_service.json"
        observed_path.write_text(
            json.dumps(
                {
                    "task_description": "Move all log files from inbox to archive.",
                    "steps": [
                        {
                            "tool_name": "list_files",
                            "tool_input": {"input_dir": "demo/move_input", "pattern": "*.log"},
                            "observation": "Found matching log files.",
                        },
                        {
                            "tool_name": "move_file",
                            "tool_input": {"input_dir": "demo/move_input", "output_dir": "demo/move_output"},
                            "observation": "Moved matching log files.",
                        },
                    ],
                    "artifacts": ["demo/move_output/job1.log"],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        self.addCleanup(observed_path.unlink)

        result = self.service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_distill_promote_service_test",
        )
        self.assertTrue(result["promoted"])
        self.assertIsNotNone(result["capture"])
        self.assertIsNone(result["trajectory"])
        self.assertEqual(
            "observed_distill_promote_service_test",
            result["promotion"]["skill_name"],
        )
        self.assertEqual("execute_skill", result["recommended_next_action"])
        self.assertEqual("execute_skill", result["recommended_host_operation"]["tool_name"])

    def test_mcp_distill_and_promote_tool_returns_promoted_skill(self) -> None:
        server = build_mcp_server(ROOT)
        _, payload = asyncio.run(
            server.call_tool(
                "distill_and_promote_candidate",
                {
                    "trajectory_path": str(ROOT / "trajectories" / "demo_merge_text_files.json"),
                    "skill_name": "mcp_distill_and_promote_test",
                    "register_trajectory": True,
                },
            )
        )
        self.assertEqual("ok", payload["status"])
        self.assertTrue(payload["data"]["promoted"])
        self.assertEqual(
            "mcp_distill_and_promote_test",
            payload["data"]["promotion"]["skill_name"],
        )
        self.assertEqual("execute_skill", payload["data"]["recommended_next_action"])
        self.assertEqual("execute_skill", payload["data"]["recommended_host_operation"]["tool_name"])

    def test_mcp_distill_and_promote_tool_accepts_observed_task(self) -> None:
        observed_path = ROOT / "demo" / "observed_distill_promote_mcp.json"
        observed_path.write_text(
            json.dumps(
                {
                    "task_description": "Move all log files from inbox to archive.",
                    "steps": [
                        {
                            "tool_name": "list_files",
                            "tool_input": {"input_dir": "demo/move_input", "pattern": "*.log"},
                            "observation": "Found matching log files.",
                        },
                        {
                            "tool_name": "move_file",
                            "tool_input": {"input_dir": "demo/move_input", "output_dir": "demo/move_output"},
                            "observation": "Moved matching log files.",
                        },
                    ],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        self.addCleanup(observed_path.unlink)

        server = build_mcp_server(ROOT)
        _, payload = asyncio.run(
            server.call_tool(
                "distill_and_promote_candidate",
                {
                    "observed_task_path": str(observed_path),
                    "skill_name": "mcp_observed_distill_promote_test",
                },
            )
        )
        self.assertEqual("ok", payload["status"])
        self.assertTrue(payload["data"]["promoted"])
        self.assertIsNotNone(payload["data"]["capture"])
        self.assertEqual("execute_skill", payload["data"]["recommended_next_action"])
        self.assertEqual("execute_skill", payload["data"]["recommended_host_operation"]["tool_name"])

    def test_execute_active_skill(self) -> None:
        output_path = ROOT / "demo" / "output" / "test_merged.md"
        if output_path.exists():
            output_path.unlink()

        before = self.index.get("merge_text_files")
        self.assertIsNotNone(before)
        before_usage = before.usage_count

        args_file = ROOT / "demo" / "test_execute_args.json"
        args_file.write_text(
            json.dumps({"input_dir": "demo/input", "output_path": "demo/output/test_merged.md"}),
            encoding="utf-8",
        )
        self.addCleanup(args_file.unlink)

        command = [
            sys.executable,
            str(CLI),
            "execute",
            "--skill",
            "merge_text_files",
            "--args-file",
            str(args_file),
        ]
        result = subprocess.run(command, capture_output=True, text=True, cwd=str(ROOT))
        self.assertEqual(0, result.returncode, msg=result.stderr or result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual("ok", payload["status"])
        self.assertTrue(output_path.exists())
        observed_path = Path(payload["data"]["observed_task_record"])
        self.addCleanup(observed_path.unlink)
        self.assertTrue(observed_path.exists())
        observed_payload = json.loads(observed_path.read_text(encoding="utf-8"))
        self.assertEqual("merge_text_files", observed_payload["skill_name"])
        self.assertTrue(observed_payload["actions"])
        self.assertEqual("list_files", observed_payload["actions"][0]["tool_name"])
        self.assertEqual("write_text", observed_payload["actions"][-1]["tool_name"])

        after = self.index.get("merge_text_files")
        self.assertIsNotNone(after)
        self.assertEqual(before_usage + 1, after.usage_count)
        self.assertIsNotNone(after.last_used_at)

    def test_service_execute_returns_observed_task_record(self) -> None:
        result = self.service.execute(
            "merge_text_files",
            {"input_dir": "demo/input", "output_path": "demo/output/service_execute_observed.md"},
        )
        output_path = ROOT / "demo" / "output" / "service_execute_observed.md"
        self.addCleanup(lambda: output_path.unlink(missing_ok=True))
        observed_path = Path(result["observed_task_record"])
        self.addCleanup(observed_path.unlink)

        self.assertTrue(output_path.exists())
        self.assertTrue(observed_path.exists())
        observed_payload = json.loads(observed_path.read_text(encoding="utf-8"))
        self.assertEqual("merge_text_files", observed_payload["skill_name"])
        self.assertEqual("completed", observed_payload["result"]["status"])
        self.assertTrue(any(step["tool_name"] == "write_text" for step in observed_payload["actions"]))

    def test_service_execute_returns_follow_up_host_operation(self) -> None:
        result = self.service.execute(
            "merge_text_files",
            {"input_dir": "demo/input", "output_path": "demo/output/service_execute_followup.md"},
        )
        output_path = ROOT / "demo" / "output" / "service_execute_followup.md"
        self.addCleanup(lambda: output_path.unlink(missing_ok=True))
        observed_path = Path(result["observed_task_record"])
        self.addCleanup(observed_path.unlink)

        self.assertEqual("distill_and_promote_candidate", result["recommended_next_action"])
        self.assertEqual("mcp_tool_call", result["recommended_host_operation"]["type"])
        self.assertEqual("distill_and_promote_candidate", result["recommended_host_operation"]["tool_name"])
        self.assertEqual(
            result["observed_task_record"],
            result["recommended_host_operation"]["arguments"]["observed_task_path"],
        )
        self.assertTrue(result["recommended_host_operation"]["operation_id"])
        self.assertEqual(
            f"observed_task:{result['observed_task_record']}",
            result["recommended_host_operation"]["source_ref"],
        )
        self.assertEqual("Promote this execution", result["recommended_host_operation"]["display_label"])
        self.assertIn("observed task record", result["recommended_host_operation"]["effect_summary"])
        self.assertEqual("medium", result["recommended_host_operation"]["risk_level"])
        self.assertFalse(result["recommended_host_operation"]["requires_confirmation"])
        self.assertIsNone(result["recommended_host_operation"]["confirmation_message"])
        self.assertEqual("string", result["recommended_host_operation"]["argument_schema"]["observed_task_path"]["type"])
        self.assertTrue(result["recommended_host_operation"]["argument_schema"]["observed_task_path"]["prefilled"])
        self.assertTrue(result["available_host_operations"])
        self.assertEqual(
            "distill_and_promote_candidate",
            result["available_host_operations"][0]["tool_name"],
        )
        self.assertEqual("primary", result["available_host_operations"][0]["operation_role"])

    def test_mcp_execute_tool_returns_follow_up_host_operation(self) -> None:
        output_path = ROOT / "demo" / "output" / "mcp_execute_followup.md"
        self.addCleanup(lambda: output_path.unlink(missing_ok=True))

        server = build_mcp_server(ROOT)
        _, payload = asyncio.run(
            server.call_tool(
                "execute_skill",
                {
                    "skill_name": "merge_text_files",
                    "args": {
                        "input_dir": "demo/input",
                        "output_path": "demo/output/mcp_execute_followup.md",
                    },
                },
            )
        )
        observed_path = Path(payload["data"]["observed_task_record"])
        self.addCleanup(observed_path.unlink)

        self.assertEqual("ok", payload["status"])
        self.assertEqual(
            "distill_and_promote_candidate",
            payload["data"]["recommended_host_operation"]["tool_name"],
        )
        self.assertEqual(
            payload["data"]["observed_task_record"],
            payload["data"]["recommended_host_operation"]["arguments"]["observed_task_path"],
        )

    def test_host_operation_builder_applies_known_tool_presets(self) -> None:
        from skill_runtime.mcp.host_operations import (
            action_host_operations,
            audit_skill_operation,
            audit_skill_recommendation,
            archive_duplicate_candidates_action,
            archive_duplicate_candidates_operation,
            archive_duplicate_candidates_follow_up_recommendation,
            archive_duplicate_candidates_recommendation,
            collect_operations,
            distill_trajectory_operation,
            distill_trajectory_recommendation,
            execute_skill_operation,
            execute_skill_recommendation,
            governance_report_operation,
            governance_report_recommendation,
            no_recommendation,
            operation_list,
            promote_skill_operation,
            refresh_governance_report_operation,
            review_archive_volume_action,
            recommendation_from_payload,
            recommendation_fields,
            source_ref_archive_duplicate_candidates,
            source_ref_archive_duplicate_candidates_preview,
            source_ref_audit,
            source_ref_archive_duplicate_candidates_follow_up,
            source_ref_archive_duplicate_candidates_apply_follow_up,
            source_ref_distill,
            source_ref_governance_report_refresh,
            source_ref_observed_task,
            source_ref_promote,
            source_ref_search_no_match,
            source_ref_search_no_match_distill,
            source_ref_search_recommended_skill,
            source_ref_skill,
            source_ref_trajectory,
            search_recommended_skill_recommendation,
            search_result_execute_skill_operation,
            search_result_payload,
            search_no_match_recommendation,
            tool_call,
            tool_call_with_preview,
        )

        execute_payload = tool_call(
            "execute_skill",
            {"skill_name": "merge_text_files", "args": {}},
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
            {"skill_names": ["merge_text_files_generated"], "dry_run": False},
            {"skill_names": ["merge_text_files_generated"], "dry_run": True},
        )
        archive_helper_payload = archive_duplicate_candidates_operation(
            ["merge_text_files_generated"],
            dry_run=False,
            include_preview=True,
        )
        distill_payload = distill_trajectory_operation("D:/tmp/demo.json")
        audit_payload = audit_skill_operation("D:/tmp/demo.py", trajectory_path="D:/tmp/demo.json")
        promote_payload = promote_skill_operation("D:/tmp/demo.py")
        governance_payload = governance_report_operation()
        ordered_payloads = operation_list(
            execute_payload,
            [archive_payload["preview"], archive_payload],
        )
        recommendation_payload = recommendation_fields(
            "execute_skill",
            execute_payload,
            reason="ready",
            additional_operations=[archive_payload],
        )
        recommendation_with_duplicate_payload = recommendation_fields(
            "execute_skill",
            execute_payload,
            additional_operations=[execute_payload, archive_payload["preview"], archive_payload],
        )
        derived_recommendation = recommendation_from_payload(recommendation_payload)
        derived_duplicate_recommendation = recommendation_from_payload(
            recommendation_with_duplicate_payload
        )
        no_recommendation_payload = no_recommendation("blocked")
        execute_recommendation = execute_skill_recommendation(
            "merge_text_files",
            {"input_dir": "str", "output_path": "str"},
            reason="execute next",
        )
        distill_recommendation = distill_trajectory_recommendation(
            "D:/tmp/demo.json",
            reason="distill next",
        )
        audit_recommendation = audit_skill_recommendation(
            "D:/tmp/demo.py",
            trajectory_path="D:/tmp/demo.json",
            reason="audit next",
        )
        archive_recommendation = archive_duplicate_candidates_recommendation(
            ["merge_text_files_generated"],
            dry_run=False,
            include_preview=True,
            reason="archive next",
        )
        search_recommendation = search_no_match_recommendation()
        archive_dry_run_follow_up = archive_duplicate_candidates_follow_up_recommendation(
            ["merge_text_files_generated"],
            dry_run=True,
        )
        archive_apply_follow_up = archive_duplicate_candidates_follow_up_recommendation(
            ["merge_text_files_generated"],
            dry_run=False,
        )
        archive_action = archive_duplicate_candidates_action(
            ["merge_text_files_generated"],
            canonical_skill="merge_text_files",
            cluster_count=2,
            rule_name="text_merge",
        )
        governance_recommendation = governance_report_recommendation(reason="refresh next")
        action_operations = action_host_operations(
            [
                {"host_operation": archive_payload},
                {"host_operation": governance_payload},
            ]
        )
        review_action = review_archive_volume_action()
        refresh_governance_operation = refresh_governance_report_operation()
        search_recommended_source_ref = source_ref_search_recommended_skill("merge_text_files")
        search_skill_source_ref = source_ref_skill("merge_text_files")
        search_no_match_source_ref = source_ref_search_no_match()
        search_no_match_distill_source_ref = source_ref_search_no_match_distill()
        observed_task_source_ref = source_ref_observed_task("D:/tmp/observed.json")
        distill_source_ref = source_ref_distill("merge_text_files")
        audit_source_ref = source_ref_audit("merge_text_files")
        promote_source_ref = source_ref_promote("merge_text_files")
        trajectory_source_ref = source_ref_trajectory("merge_text_files")
        governance_source_ref = source_ref_archive_duplicate_candidates("merge_text_files")
        governance_preview_source_ref = source_ref_archive_duplicate_candidates_preview("merge_text_files")
        governance_follow_up_source_ref = source_ref_archive_duplicate_candidates_follow_up()
        governance_apply_follow_up_source_ref = source_ref_archive_duplicate_candidates_apply_follow_up()
        governance_report_refresh_source_ref = source_ref_governance_report_refresh()
        search_result_operation = search_result_execute_skill_operation(
            "merge_text_files",
            {"input_dir": "str", "output_path": "str"},
        )
        search_execute_recommendation = search_recommended_skill_recommendation(
            "merge_text_files",
            {"input_dir": "str", "output_path": "str"},
            additional_operations=[search_result_operation],
        )
        search_result = search_result_payload(
            "merge_text_files",
            "Merge txt files into markdown.",
            0.92,
            "Matched on keywords: merge, txt.",
            {"input_dir": "str", "output_path": "str"},
        )
        execute_helper_payload = execute_skill_operation(
            "merge_text_files",
            {"input_dir": "str", "output_path": "str"},
        )

        self.assertTrue(execute_payload["operation_id"])
        self.assertIsNone(execute_payload["source_ref"])
        self.assertEqual("Run skill", execute_payload["display_label"])
        self.assertTrue(execute_payload["effect_summary"])
        self.assertEqual("low", execute_payload["risk_level"])
        self.assertFalse(execute_payload["requires_confirmation"])
        self.assertIsNone(execute_payload["confirmation_message"])
        self.assertEqual("string", execute_payload["argument_schema"]["skill_name"]["type"])
        self.assertEqual("object", execute_payload["argument_schema"]["args"]["type"])
        self.assertEqual(
            "string",
            execute_payload["argument_schema"]["args"]["properties"]["input_dir"]["type"],
        )
        self.assertTrue(execute_payload["argument_schema"]["args"]["properties"]["input_dir"]["required"])
        self.assertEqual("default", execute_payload["operation_role"])
        self.assertEqual("Distill trajectory", distill_payload["display_label"])
        self.assertEqual("D:/tmp/demo.json", distill_payload["arguments"]["trajectory_path"])
        self.assertEqual("Audit skill", audit_payload["display_label"])
        self.assertEqual("D:/tmp/demo.py", audit_payload["arguments"]["file_path"])
        self.assertEqual("Promote skill", promote_payload["display_label"])
        self.assertEqual("D:/tmp/demo.py", promote_payload["arguments"]["file_path"])
        self.assertEqual("Refresh governance report", governance_payload["display_label"])
        self.assertEqual("archive_duplicate_candidates", archive_helper_payload["tool_name"])
        self.assertTrue(archive_helper_payload["preview"]["arguments"]["dry_run"])
        self.assertEqual("primary", ordered_payloads[0]["operation_role"])
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
        self.assertEqual("audit_skill", audit_recommendation["recommended_next_action"])
        self.assertEqual(
            "archive_duplicate_candidates",
            archive_recommendation["recommended_next_action"],
        )
        self.assertEqual("capture_trajectory", search_recommendation["recommended_next_action"])
        self.assertEqual(
            "distill_and_promote_candidate",
            search_recommendation["available_host_operations"][1]["tool_name"],
        )
        self.assertEqual(
            "archive_duplicate_candidates",
            archive_dry_run_follow_up["recommended_next_action"],
        )
        self.assertEqual(
            "governance_report",
            archive_apply_follow_up["recommended_next_action"],
        )
        self.assertEqual("archive_duplicate_candidates", archive_action["action"])
        self.assertEqual("merge_text_files", archive_action["canonical_skill"])
        self.assertEqual(2, archive_action["cluster_count"])
        self.assertEqual(
            "archive_duplicate_candidates",
            archive_action["host_operation"]["tool_name"],
        )
        self.assertEqual("review_archive_volume", review_action["action"])
        self.assertEqual("governance_report", review_action["host_operation"]["tool_name"])
        self.assertEqual("Refresh governance report", refresh_governance_operation["display_label"])
        self.assertEqual("search:recommended_skill:merge_text_files", search_recommended_source_ref)
        self.assertEqual("skill:merge_text_files", search_skill_source_ref)
        self.assertEqual("search:no_strong_match", search_no_match_source_ref)
        self.assertEqual("search:no_strong_match:distill", search_no_match_distill_source_ref)
        self.assertEqual("observed_task:D:/tmp/observed.json", observed_task_source_ref)
        self.assertEqual("distill:merge_text_files", distill_source_ref)
        self.assertEqual("audit:merge_text_files", audit_source_ref)
        self.assertEqual("promote:merge_text_files", promote_source_ref)
        self.assertEqual("trajectory:merge_text_files", trajectory_source_ref)
        self.assertEqual("governance:archive_duplicate_candidates:merge_text_files", governance_source_ref)
        self.assertEqual(
            "governance:archive_duplicate_candidates:merge_text_files:preview",
            governance_preview_source_ref,
        )
        self.assertEqual("archive_duplicate_candidates:follow_up", governance_follow_up_source_ref)
        self.assertEqual(
            "archive_duplicate_candidates:apply_follow_up",
            governance_apply_follow_up_source_ref,
        )
        self.assertEqual("governance:report_refresh", governance_report_refresh_source_ref)
        self.assertEqual("skill:merge_text_files", search_result_operation["source_ref"])
        self.assertEqual("execute_skill", search_result["recommended_next_action"])
        self.assertEqual("skill:merge_text_files", search_result["host_operation"]["source_ref"])
        self.assertEqual("search:recommended_skill:merge_text_files", search_execute_recommendation["recommended_host_operation"]["source_ref"])
        self.assertEqual("default", search_execute_recommendation["available_host_operations"][1]["operation_role"])
        self.assertEqual("governance_report", governance_recommendation["recommended_next_action"])
        self.assertTrue(
            any(item["operation_role"] == "preview" for item in action_operations)
        )
        self.assertTrue(
            any(item["tool_name"] == "governance_report" for item in action_operations)
        )
        self.assertEqual(
            "string",
            execute_helper_payload["argument_schema"]["args"]["properties"]["input_dir"]["type"],
        )
        self.assertTrue(archive_payload["operation_id"])
        self.assertIsNone(archive_payload["source_ref"])
        self.assertEqual("Archive duplicates", archive_payload["display_label"])
        self.assertTrue(archive_payload["effect_summary"])
        self.assertEqual("high", archive_payload["risk_level"])
        self.assertTrue(archive_payload["requires_confirmation"])
        self.assertTrue(archive_payload["confirmation_message"])
        self.assertEqual("array", archive_payload["argument_schema"]["skill_names"]["type"])
        self.assertTrue(archive_payload["preview"]["operation_id"])
        self.assertIsNone(archive_payload["preview"]["source_ref"])
        self.assertEqual("Preview archive", archive_payload["preview"]["display_label"])
        self.assertTrue(archive_payload["preview"]["effect_summary"])
        self.assertEqual("preview", archive_payload["preview"]["operation_role"])
        self.assertIsNone(archive_payload["preview"]["confirmation_message"])

        collected = collect_operations([execute_payload, archive_payload, archive_payload["preview"], execute_payload])
        self.assertEqual(3, len(collected))
        self.assertEqual("preview", collected[0]["operation_role"])
        self.assertEqual("default", collected[1]["operation_role"])

    def test_cli_distill_and_promote_accepts_observed_task(self) -> None:
        observed_path = ROOT / "demo" / "observed_distill_promote_cli.json"
        observed_path.write_text(
            json.dumps(
                {
                    "task_description": "Move all log files from inbox to archive.",
                    "steps": [
                        {
                            "tool_name": "list_files",
                            "tool_input": {"input_dir": "demo/move_input", "pattern": "*.log"},
                            "observation": "Found matching log files.",
                        },
                        {
                            "tool_name": "move_file",
                            "tool_input": {"input_dir": "demo/move_input", "output_dir": "demo/move_output"},
                            "observation": "Moved matching log files.",
                        },
                    ],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        self.addCleanup(observed_path.unlink)

        result = subprocess.run(
            [
                sys.executable,
                str(CLI),
                "distill-and-promote",
                "--observed-task",
                str(observed_path),
                "--skill-name",
                "cli_observed_distill_promote_test",
            ],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        self.assertEqual(0, result.returncode, msg=result.stderr or result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual("ok", payload["status"])
        self.assertTrue(payload["data"]["promoted"])
        self.assertIsNotNone(payload["data"]["capture"])

    def test_cli_distill_and_promote_accepts_compact_observed_task(self) -> None:
        observed_path = ROOT / "demo" / "observed_distill_promote_compact_cli.json"
        observed_path.write_text(
            json.dumps(
                {
                    "task": "Move all log files from inbox to archive.",
                    "actions": [
                        {
                            "tool": "list_files",
                            "input": {"input_dir": "demo/move_input", "pattern": "*.log"},
                            "result": "Found matching log files.",
                        },
                        {
                            "tool": "move_file",
                            "input": {"input_dir": "demo/move_input", "output_dir": "demo/move_output"},
                            "result": "Moved matching log files.",
                        },
                    ],
                    "outputs": ["demo/move_output/job1.log"],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        self.addCleanup(observed_path.unlink)

        result = subprocess.run(
            [
                sys.executable,
                str(CLI),
                "distill-and-promote",
                "--observed-task",
                str(observed_path),
                "--skill-name",
                "cli_compact_observed_distill_promote_test",
            ],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        self.assertEqual(0, result.returncode, msg=result.stderr or result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual("ok", payload["status"])
        self.assertTrue(payload["data"]["promoted"])
        self.assertIsNotNone(payload["data"]["capture"])

    def test_cli_distill_and_promote_accepts_nested_tool_call_logs(self) -> None:
        observed_path = ROOT / "demo" / "observed_distill_promote_nested_cli.json"
        observed_path.write_text(
            json.dumps(
                {
                    "goal": "Move all log files from inbox to archive.",
                    "records": [
                        {
                            "tool": {
                                "name": "list_files",
                                "arguments": {"input_dir": "demo/move_input", "pattern": "*.log"},
                            },
                            "result": {"message": "Found matching log files.", "status": "success"},
                        },
                        {
                            "tool": {
                                "name": "move_file",
                                "arguments": {"input_dir": "demo/move_input", "output_dir": "demo/move_output"},
                            },
                            "result": {
                                "output": "Moved matching log files.",
                                "success": True,
                                "outputs": ["demo/move_output/job1.log"],
                            },
                        },
                    ],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        self.addCleanup(observed_path.unlink)

        result = subprocess.run(
            [
                sys.executable,
                str(CLI),
                "distill-and-promote",
                "--observed-task",
                str(observed_path),
                "--skill-name",
                "cli_nested_observed_distill_promote_test",
            ],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        self.assertEqual(0, result.returncode, msg=result.stderr or result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual("ok", payload["status"])
        self.assertTrue(payload["data"]["promoted"])
        self.assertIsNotNone(payload["data"]["capture"])

    def test_audit_detects_shell_true(self) -> None:
        skill_path = ROOT / "skill_store" / "staging" / "unsafe_skill.py"
        skill_path.parent.mkdir(parents=True, exist_ok=True)
        skill_path.write_text(
            'import subprocess\n'
            'def run(tools, **kwargs):\n'
            '    """bad"""\n'
            '    subprocess.run("echo hi", shell=True)\n',
            encoding="utf-8",
        )
        self.addCleanup(skill_path.unlink)

        report = SkillAuditor().audit(skill_path)
        self.assertEqual("needs_fix", report.status)
        self.assertLess(report.security_score, 100)

    def test_semantic_audit_flags_template_skill_against_trajectory(self) -> None:
        skill_path = ROOT / "skill_store" / "staging" / "semantic_template_skill.py"
        skill_path.parent.mkdir(parents=True, exist_ok=True)
        skill_path.write_text(
            'def run(tools, **kwargs):\n'
            '    """\n'
            '    功能描述:\n'
            '        Placeholder skill.\n\n'
            '    输入参数:\n'
            '        - input_dir: str\n'
            '        - output_path: str\n\n'
            '    输出结果:\n'
            '        - status: str\n'
            '    """\n'
            '    inputs = {"input_dir": kwargs.get("input_dir"), "output_path": kwargs.get("output_path")}\n'
            '    missing = [key for key, value in inputs.items() if value is None]\n'
            '    if missing:\n'
            '        raise ValueError(missing)\n'
            '    return {"status": "completed", "inputs": inputs, "steps_executed": 3}\n',
            encoding="utf-8",
        )
        self.addCleanup(skill_path.unlink)

        trajectory = TrajectoryStore(ROOT / "trajectories").load("demo_merge_text_files")
        report = SkillAuditor().audit(skill_path, trajectory=trajectory)
        self.assertEqual("needs_fix", report.status)
        self.assertLess(report.semantic_score, 100)
        self.assertTrue(any("template" in finding.lower() or "trajectory" in finding.lower() for finding in report.semantic_findings))
        self.assertEqual("mock_semantic_review_provider", report.semantic_provider)
        self.assertIsNotNone(report.semantic_artifact)
        self.assertTrue(Path(report.semantic_artifact).exists())

    def test_service_audit_with_trajectory_returns_semantic_fields(self) -> None:
        result = self.service.audit(
            ROOT / "skill_store" / "active" / "merge_text_files.py",
            trajectory_path=ROOT / "trajectories" / "demo_merge_text_files.json",
        )
        report = result["report"]
        self.assertEqual("passed", report["status"])
        self.assertIn("static_score", report)
        self.assertIn("semantic_score", report)
        self.assertIn("semantic_findings", report)
        self.assertEqual([], report["semantic_findings"])
        self.assertEqual("mock_semantic_review_provider", report["semantic_provider"])
        self.assertTrue(Path(report["semantic_artifact"]).exists())

    def test_service_audit_returns_promote_follow_up_on_pass(self) -> None:
        distill_result = self.service.distill(
            ROOT / "trajectories" / "demo_merge_text_files.json",
            skill_name="service_audit_followup_test",
        )
        result = self.service.audit(
            distill_result["staging_file"],
            trajectory_path=distill_result["trajectory_path"],
        )
        self.assertEqual("promote_skill", result["recommended_next_action"])
        self.assertEqual("promote_skill", result["recommended_host_operation"]["tool_name"])
        self.assertEqual(
            distill_result["staging_file"],
            result["recommended_host_operation"]["arguments"]["file_path"],
        )
        self.assertEqual("primary", result["available_host_operations"][0]["operation_role"])

    def test_service_promote_returns_execute_follow_up(self) -> None:
        distill_result = self.service.distill(
            ROOT / "trajectories" / "demo_merge_text_files.json",
            skill_name="service_promote_followup_test",
        )
        audit_result = self.service.audit(
            distill_result["staging_file"],
            trajectory_path=distill_result["trajectory_path"],
        )
        self.assertEqual("promote_skill", audit_result["recommended_next_action"])

        result = self.service.promote(distill_result["staging_file"])
        self.assertEqual("execute_skill", result["recommended_next_action"])
        self.assertEqual("execute_skill", result["recommended_host_operation"]["tool_name"])
        self.assertEqual(
            "service_promote_followup_test",
            result["recommended_host_operation"]["arguments"]["skill_name"],
        )
        self.assertEqual("primary", result["available_host_operations"][0]["operation_role"])

    def test_mcp_promote_returns_execute_follow_up(self) -> None:
        distill_result = self.service.distill(
            ROOT / "trajectories" / "demo_merge_text_files.json",
            skill_name="mcp_promote_followup_test",
        )
        self.service.audit(
            distill_result["staging_file"],
            trajectory_path=distill_result["trajectory_path"],
        )

        server = build_mcp_server(ROOT)
        _, payload = asyncio.run(
            server.call_tool(
                "promote_skill",
                {"file_path": distill_result["staging_file"]},
            )
        )
        self.assertEqual("ok", payload["status"])
        self.assertEqual("execute_skill", payload["data"]["recommended_next_action"])
        self.assertEqual("execute_skill", payload["data"]["recommended_host_operation"]["tool_name"])

    def test_provider_backed_semantic_review_flags_fallback_generated_skill(self) -> None:
        trajectory = Trajectory(
            task_id="fallback_semantic_audit_demo",
            session_id="session_fallback_semantic_audit",
            task_description="Generate a report from mixed observations without a deterministic rule.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="observe_state",
                    tool_input={"report_name": "weekly_report"},
                    observation="Collected mixed observations.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="summarize_notes",
                    tool_input={"topic": "weekly_report"},
                    observation="Summarized notes into a draft.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/fallback_semantic.txt"],
            started_at="2026-04-24T14:00:00",
            ended_at="2026-04-24T14:01:00",
        )

        generated = SkillGenerator(ROOT / "skill_store" / "staging").generate(
            trajectory, skill_name="semantic_provider_fallback_test"
        )
        report = SkillAuditor().audit(generated["skill_file"], trajectory=trajectory)
        self.assertEqual("mock_semantic_review_provider", report.semantic_provider)
        self.assertIsNotNone(report.semantic_artifact)
        self.assertTrue(Path(report.semantic_artifact).exists())
        self.assertTrue(
            any("fallback" in finding.lower() or "template" in finding.lower() for finding in report.semantic_findings)
        )

    def test_distilled_merge_skill_writes_output(self) -> None:
        output_path = ROOT / "demo" / "output" / "generated.md"
        if output_path.exists():
            output_path.unlink()

        generator = SkillGenerator(ROOT / "skill_store" / "staging")
        trajectory = TrajectoryStore(ROOT / "trajectories").load("demo_merge_text_files")
        generated = generator.generate(trajectory, skill_name="merge_text_files_rule_test")
        self.assertEqual("text_merge", generated["metadata"].rule_name)
        self.assertIsNotNone(generated["metadata"].rule_reason)
        self._activate_generated_skill(generated)

        command = [
            sys.executable,
            str(CLI),
            "execute",
            "--skill",
            "merge_text_files_rule_test",
            "--args-file",
            str(ROOT / "demo" / "execute_args.json"),
        ]
        result = subprocess.run(command, capture_output=True, text=True, cwd=str(ROOT))
        self.assertEqual(0, result.returncode, msg=result.stderr or result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual("ok", payload["status"])
        self.assertTrue(output_path.exists())
        self.assertIn("hello from file a", output_path.read_text(encoding="utf-8"))

        search_results = self.index.search("merge txt files into markdown", top_k=50)
        generated_match = next(
            result for result in search_results if result["skill_name"] == "merge_text_files_rule_test"
        )
        self.assertEqual("text_merge", generated_match["rule_name"])
        self.assertIn("merging txt files", generated_match["rule_reason"])

    def test_distilled_single_file_transform_writes_output(self) -> None:
        output_path = ROOT / "demo" / "output" / "single_transform.txt"
        if output_path.exists():
            output_path.unlink()

        trajectory = Trajectory(
            task_id="single_transform_demo",
            session_id="session_single_transform",
            task_description="Read one text file and write it to a new output file.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="read_text",
                    tool_input={"input_path": "demo/input/a.txt"},
                    observation="Read the source file.",
                    status="success",
                    thought_summary="Load input text.",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="write_text",
                    tool_input={"output_path": "demo/output/single_transform.txt"},
                    observation="Wrote the transformed text.",
                    status="success",
                    thought_summary="Persist output text.",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/single_transform.txt"],
            started_at="2026-04-18T11:00:00",
            ended_at="2026-04-18T11:01:00",
        )

        generator = SkillGenerator(ROOT / "skill_store" / "staging")
        generated = generator.generate(trajectory, skill_name="single_file_transform_rule_test")
        self._activate_generated_skill(generated)

        args_file = ROOT / "demo" / "single_transform_args.json"
        args_file.write_text(
            json.dumps({"input_path": "demo/input/a.txt", "output_path": "demo/output/single_transform.txt"}),
            encoding="utf-8",
        )
        self.addCleanup(args_file.unlink)

        result = subprocess.run(
            [
                sys.executable,
                str(CLI),
                "execute",
                "--skill",
                "single_file_transform_rule_test",
                "--args-file",
                str(args_file),
            ],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        self.assertEqual(0, result.returncode, msg=result.stderr or result.stdout)
        self.assertTrue(output_path.exists())
        self.assertEqual("hello from file a\n", output_path.read_text(encoding="utf-8"))

    def test_distilled_text_replace_writes_output(self) -> None:
        output_path = ROOT / "demo" / "output" / "replace_output.txt"
        if output_path.exists():
            output_path.unlink()

        trajectory = Trajectory(
            task_id="text_replace_demo",
            session_id="session_text_replace",
            task_description="Replace one string with another in a text file and write a new output file.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="read_text",
                    tool_input={"input_path": "demo/input/a.txt", "old_text": "file", "new_text": "document"},
                    observation="Read source text for replacement.",
                    status="success",
                    thought_summary="Load source content.",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="write_text",
                    tool_input={"output_path": "demo/output/replace_output.txt"},
                    observation="Wrote replaced text output.",
                    status="success",
                    thought_summary="Persist replaced content.",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/replace_output.txt"],
            started_at="2026-04-18T11:05:00",
            ended_at="2026-04-18T11:06:00",
        )

        generator = SkillGenerator(ROOT / "skill_store" / "staging")
        generated = generator.generate(trajectory, skill_name="text_replace_rule_test")
        self.assertEqual("text_replace", generated["metadata"].rule_name)
        self.assertGreater(generated["metadata"].rule_priority, 0)
        self._activate_generated_skill(generated)

        args_file = ROOT / "demo" / "text_replace_args.json"
        args_file.write_text(
            json.dumps(
                {
                    "input_path": "demo/input/a.txt",
                    "output_path": "demo/output/replace_output.txt",
                    "old_text": "file",
                    "new_text": "document",
                }
            ),
            encoding="utf-8",
        )
        self.addCleanup(args_file.unlink)

        result = subprocess.run(
            [
                sys.executable,
                str(CLI),
                "execute",
                "--skill",
                "text_replace_rule_test",
                "--args-file",
                str(args_file),
            ],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        self.assertEqual(0, result.returncode, msg=result.stderr or result.stdout)
        self.assertTrue(output_path.exists())
        self.assertIn("document a", output_path.read_text(encoding="utf-8"))

    def test_distilled_batch_rename_renames_files(self) -> None:
        rename_dir = ROOT / "demo" / "rename_input"
        rename_dir.mkdir(parents=True, exist_ok=True)
        source_a = rename_dir / "one.txt"
        source_b = rename_dir / "two.txt"
        source_a.write_text("one", encoding="utf-8")
        source_b.write_text("two", encoding="utf-8")
        self.addCleanup(lambda: source_a.unlink(missing_ok=True))
        self.addCleanup(lambda: source_b.unlink(missing_ok=True))
        self.addCleanup(lambda: (rename_dir / "renamed_one.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (rename_dir / "renamed_two.txt").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="batch_rename_demo",
            session_id="session_batch_rename",
            task_description="Rename all txt files in a directory by prefixing them with a value.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"input_dir": "demo/rename_input", "pattern": "*.txt", "prefix": "renamed_"},
                    observation="Found files to rename.",
                    status="success",
                    thought_summary="Collect rename candidates.",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="rename_path",
                    tool_input={"input_dir": "demo/rename_input", "prefix": "renamed_"},
                    observation="Renamed matching files.",
                    status="success",
                    thought_summary="Apply prefix rename.",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-18T11:10:00",
            ended_at="2026-04-18T11:11:00",
        )

        generator = SkillGenerator(ROOT / "skill_store" / "staging")
        generated = generator.generate(trajectory, skill_name="batch_rename_rule_test")
        self._activate_generated_skill(generated)

        args_file = ROOT / "demo" / "batch_rename_args.json"
        args_file.write_text(
            json.dumps(
                {
                    "input_dir": "demo/rename_input",
                    "pattern": "*.txt",
                    "prefix": "renamed_",
                }
            ),
            encoding="utf-8",
        )
        self.addCleanup(args_file.unlink)

        result = subprocess.run(
            [
                sys.executable,
                str(CLI),
                "execute",
                "--skill",
                "batch_rename_rule_test",
                "--args-file",
                str(args_file),
            ],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        self.assertEqual(0, result.returncode, msg=result.stderr or result.stdout)
        self.assertTrue((rename_dir / "renamed_one.txt").exists())
        self.assertTrue((rename_dir / "renamed_two.txt").exists())

    def test_distilled_directory_copy_copies_matching_files(self) -> None:
        source_dir = ROOT / "demo" / "copy_input"
        output_dir = ROOT / "demo" / "copy_output"
        source_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (source_dir / "keep_a.txt").write_text("alpha", encoding="utf-8")
        (source_dir / "keep_b.txt").write_text("beta", encoding="utf-8")
        (source_dir / "skip.md").write_text("skip", encoding="utf-8")
        self.addCleanup(lambda: (source_dir / "keep_a.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (source_dir / "keep_b.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (source_dir / "skip.md").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "keep_a.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "keep_b.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "skip.md").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="directory_copy_demo",
            session_id="session_directory_copy",
            task_description="Copy matching txt files from one directory into another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"input_dir": "demo/copy_input", "output_dir": "demo/copy_output", "pattern": "*.txt"},
                    observation="Found txt files to copy.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="copy_file",
                    tool_input={"input_dir": "demo/copy_input", "output_dir": "demo/copy_output"},
                    observation="Copied matching files into output directory.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-18T11:15:00",
            ended_at="2026-04-18T11:16:00",
        )

        generated = SkillGenerator(ROOT / "skill_store" / "staging").generate(
            trajectory, skill_name="directory_copy_rule_test"
        )
        self._activate_generated_skill(generated)

        args_file = ROOT / "demo" / "directory_copy_args.json"
        args_file.write_text(
            json.dumps(
                {
                    "input_dir": "demo/copy_input",
                    "output_dir": "demo/copy_output",
                    "pattern": "*.txt",
                }
            ),
            encoding="utf-8",
        )
        self.addCleanup(args_file.unlink)

        result = subprocess.run(
            [
                sys.executable,
                str(CLI),
                "execute",
                "--skill",
                "directory_copy_rule_test",
                "--args-file",
                str(args_file),
            ],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        self.assertEqual(0, result.returncode, msg=result.stderr or result.stdout)
        self.assertTrue((output_dir / "keep_a.txt").exists())
        self.assertTrue((output_dir / "keep_b.txt").exists())
        self.assertFalse((output_dir / "skip.md").exists())

    def test_distilled_directory_text_replace_writes_outputs(self) -> None:
        source_dir = ROOT / "demo" / "replace_dir_input"
        output_dir = ROOT / "demo" / "replace_dir_output"
        source_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (source_dir / "a.txt").write_text("hello file a", encoding="utf-8")
        (source_dir / "b.txt").write_text("hello file b", encoding="utf-8")
        (source_dir / "skip.md").write_text("skip file", encoding="utf-8")
        self.addCleanup(lambda: (source_dir / "a.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (source_dir / "b.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (source_dir / "skip.md").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "a.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "b.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "skip.md").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="directory_text_replace_demo",
            session_id="session_directory_text_replace",
            task_description="Replace one string with another across all txt files in a directory and write outputs to another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={
                        "input_dir": "demo/replace_dir_input",
                        "output_dir": "demo/replace_dir_output",
                        "pattern": "*.txt",
                        "old_text": "file",
                        "new_text": "document",
                    },
                    observation="Found txt files to rewrite.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_text",
                    tool_input={"input_dir": "demo/replace_dir_input"},
                    observation="Read each source file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_text",
                    tool_input={"output_dir": "demo/replace_dir_output"},
                    observation="Wrote replaced outputs.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-18T11:20:00",
            ended_at="2026-04-18T11:21:00",
        )

        generated = SkillGenerator(ROOT / "skill_store" / "staging").generate(
            trajectory, skill_name="directory_text_replace_rule_test"
        )
        self.assertEqual("directory_text_replace", generated["metadata"].rule_name)
        self.assertIn("multiple files", generated["metadata"].rule_reason)
        self._activate_generated_skill(generated)

        args_file = ROOT / "demo" / "directory_text_replace_args.json"
        args_file.write_text(
            json.dumps(
                {
                    "input_dir": "demo/replace_dir_input",
                    "output_dir": "demo/replace_dir_output",
                    "pattern": "*.txt",
                    "old_text": "file",
                    "new_text": "document",
                }
            ),
            encoding="utf-8",
        )
        self.addCleanup(args_file.unlink)

        result = subprocess.run(
            [
                sys.executable,
                str(CLI),
                "execute",
                "--skill",
                "directory_text_replace_rule_test",
                "--args-file",
                str(args_file),
            ],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        self.assertEqual(0, result.returncode, msg=result.stderr or result.stdout)
        self.assertEqual("hello document a", (output_dir / "a.txt").read_text(encoding="utf-8"))
        self.assertEqual("hello document b", (output_dir / "b.txt").read_text(encoding="utf-8"))
        self.assertFalse((output_dir / "skip.md").exists())

    def test_distilled_csv_to_json_writes_output(self) -> None:
        input_path = ROOT / "demo" / "input" / "table.csv"
        output_path = ROOT / "demo" / "output" / "table.json"
        input_path.write_text("name,age\nalice,30\nbob,31\n", encoding="utf-8")
        self.addCleanup(lambda: input_path.unlink(missing_ok=True))
        self.addCleanup(lambda: output_path.unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="csv_to_json_demo",
            session_id="session_csv_to_json",
            task_description="Convert a CSV file into a JSON array file.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="read_text",
                    tool_input={"input_path": "demo/input/table.csv"},
                    observation="Read CSV input.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="write_json",
                    tool_input={"output_path": "demo/output/table.json"},
                    observation="Wrote JSON output.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/table.json"],
            started_at="2026-04-18T11:25:00",
            ended_at="2026-04-18T11:26:00",
        )

        generated = SkillGenerator(ROOT / "skill_store" / "staging").generate(
            trajectory, skill_name="csv_to_json_rule_test"
        )
        self.assertEqual("csv_to_json", generated["metadata"].rule_name)
        self._activate_generated_skill(generated)

        args_file = ROOT / "demo" / "csv_to_json_args.json"
        args_file.write_text(
            json.dumps({"input_path": "demo/input/table.csv", "output_path": "demo/output/table.json"}),
            encoding="utf-8",
        )
        self.addCleanup(args_file.unlink)

        result = subprocess.run(
            [
                sys.executable,
                str(CLI),
                "execute",
                "--skill",
                "csv_to_json_rule_test",
                "--args-file",
                str(args_file),
            ],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        self.assertEqual(0, result.returncode, msg=result.stderr or result.stdout)
        payload = json.loads(output_path.read_text(encoding="utf-8"))
        self.assertEqual("alice", payload[0]["name"])
        self.assertEqual("31", payload[1]["age"])

    def test_distilled_json_to_csv_writes_output(self) -> None:
        input_path = ROOT / "demo" / "input" / "table.json"
        output_path = ROOT / "demo" / "output" / "table.csv"
        input_path.write_text(
            json.dumps([{"name": "alice", "age": "30"}, {"name": "bob", "age": "31"}], ensure_ascii=False),
            encoding="utf-8",
        )
        self.addCleanup(lambda: input_path.unlink(missing_ok=True))
        self.addCleanup(lambda: output_path.unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="json_to_csv_demo",
            session_id="session_json_to_csv",
            task_description="Convert a JSON array file into CSV format.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="read_json",
                    tool_input={"input_path": "demo/input/table.json"},
                    observation="Read JSON input.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="write_text",
                    tool_input={"output_path": "demo/output/table.csv"},
                    observation="Wrote CSV output.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/table.csv"],
            started_at="2026-04-18T11:27:00",
            ended_at="2026-04-18T11:28:00",
        )

        generated = SkillGenerator(ROOT / "skill_store" / "staging").generate(
            trajectory, skill_name="json_to_csv_rule_test"
        )
        self.assertEqual("json_to_csv", generated["metadata"].rule_name)
        self._activate_generated_skill(generated)

        args_file = ROOT / "demo" / "json_to_csv_args.json"
        args_file.write_text(
            json.dumps({"input_path": "demo/input/table.json", "output_path": "demo/output/table.csv"}),
            encoding="utf-8",
        )
        self.addCleanup(args_file.unlink)

        result = subprocess.run(
            [
                sys.executable,
                str(CLI),
                "execute",
                "--skill",
                "json_to_csv_rule_test",
                "--args-file",
                str(args_file),
            ],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        self.assertEqual(0, result.returncode, msg=result.stderr or result.stdout)
        csv_text = output_path.read_text(encoding="utf-8")
        self.assertIn("name,age", csv_text)
        self.assertIn("alice,30", csv_text)

    def test_distilled_directory_move_moves_matching_files(self) -> None:
        source_dir = ROOT / "demo" / "move_input"
        output_dir = ROOT / "demo" / "move_output"
        source_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (source_dir / "move_a.txt").write_text("alpha", encoding="utf-8")
        (source_dir / "move_b.txt").write_text("beta", encoding="utf-8")
        (source_dir / "stay.md").write_text("stay", encoding="utf-8")
        self.addCleanup(lambda: (source_dir / "move_a.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (source_dir / "move_b.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (source_dir / "stay.md").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "move_a.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "move_b.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "stay.md").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="directory_move_demo",
            session_id="session_directory_move",
            task_description="Move matching txt files from one directory into another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"input_dir": "demo/move_input", "output_dir": "demo/move_output", "pattern": "*.txt"},
                    observation="Found txt files to move.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="move_file",
                    tool_input={"input_dir": "demo/move_input", "output_dir": "demo/move_output"},
                    observation="Moved matching files into output directory.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-18T11:30:00",
            ended_at="2026-04-18T11:31:00",
        )

        generated = SkillGenerator(ROOT / "skill_store" / "staging").generate(
            trajectory, skill_name="directory_move_rule_test"
        )
        self.assertEqual("directory_move", generated["metadata"].rule_name)
        self._activate_generated_skill(generated)

        args_file = ROOT / "demo" / "directory_move_args.json"
        args_file.write_text(
            json.dumps(
                {
                    "input_dir": "demo/move_input",
                    "output_dir": "demo/move_output",
                    "pattern": "*.txt",
                }
            ),
            encoding="utf-8",
        )
        self.addCleanup(args_file.unlink)

        result = subprocess.run(
            [
                sys.executable,
                str(CLI),
                "execute",
                "--skill",
                "directory_move_rule_test",
                "--args-file",
                str(args_file),
            ],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        self.assertEqual(0, result.returncode, msg=result.stderr or result.stdout)
        self.assertTrue((output_dir / "move_a.txt").exists())
        self.assertTrue((output_dir / "move_b.txt").exists())
        self.assertFalse((source_dir / "move_a.txt").exists())
        self.assertFalse((source_dir / "move_b.txt").exists())
        self.assertTrue((source_dir / "stay.md").exists())

    def test_full_generated_skill_promotion_flow(self) -> None:
        generated_name = "merge_text_files_promoted_test"
        output_path = ROOT / "demo" / "output" / "promoted_generated.md"
        if output_path.exists():
            output_path.unlink()

        subprocess.run(
            [
                sys.executable,
                str(CLI),
                "distill",
                "--trajectory",
                "trajectories/demo_merge_text_files.json",
                "--skill-name",
                generated_name,
            ],
            check=True,
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        subprocess.run(
            [
                sys.executable,
                str(CLI),
                "audit",
                "--file",
                f"skill_store/staging/{generated_name}.py",
            ],
            check=True,
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        subprocess.run(
            [
                sys.executable,
                str(CLI),
                "promote",
                "--file",
                f"skill_store/staging/{generated_name}.py",
            ],
            check=True,
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )

        args_file = ROOT / "demo" / "promoted_execute_args.json"
        args_file.write_text(
            json.dumps({"input_dir": "demo/input", "output_path": "demo/output/promoted_generated.md"}),
            encoding="utf-8",
        )
        self.addCleanup(args_file.unlink)

        result = subprocess.run(
            [
                sys.executable,
                str(CLI),
                "execute",
                "--skill",
                generated_name,
                "--args-file",
                str(args_file),
            ],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        self.assertEqual(0, result.returncode, msg=result.stderr or result.stdout)
        self.assertTrue(output_path.exists())
        self.assertIn("hello from file b", output_path.read_text(encoding="utf-8"))

        promoted = self.index.get(generated_name)
        self.assertIsNotNone(promoted)
        self.assertEqual("text_merge", promoted.rule_name)
        self.assertIsNotNone(promoted.rule_reason)

    def test_backfill_provenance_updates_legacy_skill_metadata(self) -> None:
        active_dir = ROOT / "skill_store" / "active"
        skill_path = active_dir / "legacy_merge_skill.py"
        metadata_path = active_dir / "legacy_merge_skill.metadata.json"

        skill_path.write_text(
            'def run(tools, **kwargs):\n'
            '    """legacy"""\n'
            '    inputs = {"input_dir": kwargs.get("input_dir"), "output_path": kwargs.get("output_path")}\n'
            '    return {"status": "completed"}\n',
            encoding="utf-8",
        )
        self.addCleanup(skill_path.unlink)
        self.addCleanup(metadata_path.unlink)

        legacy = {
            "skill_name": "legacy_merge_skill",
            "file_path": str(skill_path.resolve()),
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
        }
        metadata_path.write_text(json.dumps(legacy, ensure_ascii=False, indent=2), encoding="utf-8")
        self.index.rebuild_from_directory(active_dir)

        updated = ProvenanceBackfill(active_dir, self.index).run()
        self.assertTrue(any(item["skill_name"] == "legacy_merge_skill" for item in updated))

        refreshed = self.index.get("legacy_merge_skill")
        self.assertIsNotNone(refreshed)
        self.assertEqual("text_merge", refreshed.rule_name)
        self.assertIsNotNone(refreshed.rule_reason)

    def test_archive_cold_moves_old_active_skill_out_of_search(self) -> None:
        active_dir = ROOT / "skill_store" / "active"
        archive_dir = ROOT / "skill_store" / "archive"
        archive_dir.mkdir(parents=True, exist_ok=True)
        skill_path = active_dir / "archive_candidate_skill.py"
        metadata_path = active_dir / "archive_candidate_skill.metadata.json"
        archived_skill_path = archive_dir / "archive_candidate_skill.py"
        archived_metadata_path = archive_dir / "archive_candidate_skill.metadata.json"

        skill_path.write_text(
            'def run(tools, **kwargs):\n'
            '    return {"status": "completed"}\n',
            encoding="utf-8",
        )
        metadata = {
            "skill_name": "archive_candidate_skill",
            "file_path": str(skill_path.resolve()),
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
        }
        metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
        self.addCleanup(lambda: skill_path.unlink(missing_ok=True))
        self.addCleanup(lambda: metadata_path.unlink(missing_ok=True))
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

        results = self.index.search("archive candidate skill", top_k=20)
        self.assertNotIn("archive_candidate_skill", {item["skill_name"] for item in results})

    def test_governance_report_surfaces_duplicate_candidates(self) -> None:
        report = self.service.governance_report()
        self.assertIn("status_counts", report)
        self.assertIn("duplicate_candidates", report)
        self.assertIn("recommended_actions", report)
        self.assertGreaterEqual(report["active_count"], 1)
        duplicate_cluster = next(
            item
            for item in report["duplicate_candidates"]
            if "merge_text_files_generated" in item["skill_names"]
        )
        self.assertGreaterEqual(duplicate_cluster["count"], 2)
        self.assertEqual("merge_text_files", duplicate_cluster["canonical_skill"])
        self.assertIn("merge_text_files_generated", duplicate_cluster["archive_candidates"])
        archive_action = next(
            item
            for item in report["recommended_actions"]
            if item["action"] == "archive_duplicate_candidates" and item["canonical_skill"] == "merge_text_files"
        )
        self.assertIn("merge_text_files_generated", archive_action["skill_names"])
        self.assertEqual("mcp_tool_call", archive_action["host_operation"]["type"])
        self.assertEqual("archive_duplicate_candidates", archive_action["host_operation"]["tool_name"])
        self.assertIn(
            "merge_text_files_generated",
            archive_action["host_operation"]["arguments"]["skill_names"],
        )
        self.assertFalse(archive_action["host_operation"]["arguments"]["dry_run"])
        self.assertTrue(archive_action["host_operation"]["operation_id"])
        self.assertEqual("governance:archive_duplicate_candidates:merge_text_files", archive_action["host_operation"]["source_ref"])
        self.assertEqual("Archive duplicates", archive_action["host_operation"]["display_label"])
        self.assertTrue(archive_action["host_operation"]["effect_summary"])
        self.assertEqual("high", archive_action["host_operation"]["risk_level"])
        self.assertTrue(archive_action["host_operation"]["requires_confirmation"])
        self.assertTrue(archive_action["host_operation"]["confirmation_message"])
        self.assertEqual("array", archive_action["host_operation"]["argument_schema"]["skill_names"]["type"])
        self.assertTrue(archive_action["host_operation"]["argument_schema"]["skill_names"]["prefilled"])
        self.assertEqual("boolean", archive_action["host_operation"]["argument_schema"]["dry_run"]["type"])
        self.assertEqual(
            "archive_duplicate_candidates",
            archive_action["host_operation"]["preview"]["tool_name"],
        )
        self.assertTrue(archive_action["host_operation"]["preview"]["arguments"]["dry_run"])
        self.assertTrue(archive_action["host_operation"]["preview"]["operation_id"])
        self.assertEqual(
            "governance:archive_duplicate_candidates:merge_text_files:preview",
            archive_action["host_operation"]["preview"]["source_ref"],
        )
        self.assertEqual("Preview archive", archive_action["host_operation"]["preview"]["display_label"])
        self.assertTrue(archive_action["host_operation"]["preview"]["effect_summary"])
        self.assertEqual("low", archive_action["host_operation"]["preview"]["risk_level"])
        self.assertFalse(archive_action["host_operation"]["preview"]["requires_confirmation"])
        self.assertIsNone(archive_action["host_operation"]["preview"]["confirmation_message"])

    def test_mcp_governance_report_returns_host_ready_recommended_actions(self) -> None:
        server = build_mcp_server(ROOT)
        _, payload = asyncio.run(server.call_tool("governance_report", {}))

        self.assertEqual("ok", payload["status"])
        self.assertIn("recommended_actions", payload["data"])
        self.assertIn("available_host_operations", payload["data"])
        self.assertGreaterEqual(len(payload["data"]["available_host_operations"]), 2)
        archive_action = next(
            item
            for item in payload["data"]["recommended_actions"]
            if item["action"] == "archive_duplicate_candidates"
        )
        self.assertEqual("mcp_tool_call", archive_action["host_operation"]["type"])
        self.assertEqual("archive_duplicate_candidates", archive_action["host_operation"]["tool_name"])
        self.assertIn("arguments", archive_action["host_operation"])
        self.assertTrue(
            any(item["tool_name"] == "archive_duplicate_candidates" for item in payload["data"]["available_host_operations"])
        )
        self.assertTrue(
            any(item["operation_role"] == "preview" for item in payload["data"]["available_host_operations"])
        )
        self.assertEqual("preview", payload["data"]["available_host_operations"][0]["operation_role"])
        preview_count = 0
        for item in payload["data"]["available_host_operations"]:
            if item["operation_role"] == "preview":
                preview_count += 1
                continue
            break
        self.assertGreaterEqual(preview_count, 1)
        self.assertEqual("default", payload["data"]["available_host_operations"][preview_count]["operation_role"])

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

        canonical_skill.write_text('def run(tools, **kwargs):\n    return {"status": "completed"}\n', encoding="utf-8")
        duplicate_skill.write_text('def run(tools, **kwargs):\n    return {"status": "completed"}\n', encoding="utf-8")
        canonical_payload = {
            "skill_name": "dup_keep_skill",
            "file_path": str(canonical_skill.resolve()),
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
            "skill_name": "dup_test_skill",
            "file_path": str(duplicate_skill.resolve()),
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
        canonical_metadata.write_text(json.dumps(canonical_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        duplicate_metadata.write_text(json.dumps(duplicate_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        self.addCleanup(lambda: canonical_skill.unlink(missing_ok=True))
        self.addCleanup(lambda: canonical_metadata.unlink(missing_ok=True))
        self.addCleanup(lambda: duplicate_skill.unlink(missing_ok=True))
        self.addCleanup(lambda: duplicate_metadata.unlink(missing_ok=True))
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
        self.assertEqual("governance_report", result["recommended_host_operation"]["tool_name"])
        self.assertEqual("primary", result["available_host_operations"][0]["operation_role"])

    def test_archive_duplicate_candidates_dry_run_does_not_modify_files(self) -> None:
        active_dir = ROOT / "skill_store" / "active"
        archive_dir = ROOT / "skill_store" / "archive"
        archive_dir.mkdir(parents=True, exist_ok=True)

        canonical_skill = active_dir / "dup_preview_keep.py"
        canonical_metadata = active_dir / "dup_preview_keep.metadata.json"
        duplicate_skill = active_dir / "dup_preview_test.py"
        duplicate_metadata = active_dir / "dup_preview_test.metadata.json"

        canonical_skill.write_text('def run(tools, **kwargs):\n    return {"status": "completed"}\n', encoding="utf-8")
        duplicate_skill.write_text('def run(tools, **kwargs):\n    return {"status": "completed"}\n', encoding="utf-8")
        canonical_payload = {
            "skill_name": "dup_preview_keep",
            "file_path": str(canonical_skill.resolve()),
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
            "skill_name": "dup_preview_test",
            "file_path": str(duplicate_skill.resolve()),
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
        canonical_metadata.write_text(json.dumps(canonical_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        duplicate_metadata.write_text(json.dumps(duplicate_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        self.addCleanup(lambda: canonical_skill.unlink(missing_ok=True))
        self.addCleanup(lambda: canonical_metadata.unlink(missing_ok=True))
        self.addCleanup(lambda: duplicate_skill.unlink(missing_ok=True))
        self.addCleanup(lambda: duplicate_metadata.unlink(missing_ok=True))

        self.index.rebuild_from_directory(active_dir)
        result = self.service.archive_duplicate_candidates(skill_names=["dup_preview_test"], dry_run=True)

        self.assertTrue(result["dry_run"])
        self.assertIn("dup_preview_test", result["planned"])
        self.assertEqual([], result["archived"])
        self.assertTrue(duplicate_skill.exists())
        self.assertTrue(duplicate_metadata.exists())
        self.assertEqual("archive_duplicate_candidates", result["recommended_next_action"])
        self.assertEqual("archive_duplicate_candidates", result["recommended_host_operation"]["tool_name"])
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

        canonical_skill.write_text('def run(tools, **kwargs):\n    return {"status": "completed"}\n', encoding="utf-8")
        duplicate_skill.write_text('def run(tools, **kwargs):\n    return {"status": "completed"}\n', encoding="utf-8")
        canonical_payload = {
            "skill_name": "dup_mcp_keep",
            "file_path": str(canonical_skill.resolve()),
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
            "skill_name": "dup_mcp_test",
            "file_path": str(duplicate_skill.resolve()),
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
        canonical_metadata.write_text(json.dumps(canonical_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        duplicate_metadata.write_text(json.dumps(duplicate_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        self.addCleanup(lambda: canonical_skill.unlink(missing_ok=True))
        self.addCleanup(lambda: canonical_metadata.unlink(missing_ok=True))
        self.addCleanup(lambda: duplicate_skill.unlink(missing_ok=True))
        self.addCleanup(lambda: duplicate_metadata.unlink(missing_ok=True))
        self.addCleanup(lambda: (archive_dir / "dup_mcp_test.py").unlink(missing_ok=True))
        self.addCleanup(lambda: (archive_dir / "dup_mcp_test.metadata.json").unlink(missing_ok=True))

        self.index.rebuild_from_directory(active_dir)
        server = build_mcp_server(ROOT)
        _, payload = asyncio.run(
            server.call_tool(
                "archive_duplicate_candidates",
                {"skill_names": ["dup_mcp_test"], "dry_run": True},
            )
        )

        self.assertEqual("ok", payload["status"])
        self.assertEqual("archive_duplicate_candidates", payload["data"]["recommended_next_action"])
        self.assertEqual("mcp_tool_call", payload["data"]["recommended_host_operation"]["type"])
        self.assertEqual("archive_duplicate_candidates", payload["data"]["recommended_host_operation"]["tool_name"])
        self.assertEqual("primary", payload["data"]["available_host_operations"][0]["operation_role"])

    def test_unmatched_trajectory_uses_llm_fallback_artifact(self) -> None:
        trajectory = Trajectory(
            task_id="fallback_demo",
            session_id="session_fallback_demo",
            task_description="Generate a report from mixed observations without a known deterministic file rule.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="observe_state",
                    tool_input={"report_name": "weekly_report"},
                    observation="Collected mixed observations.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="summarize_notes",
                    tool_input={"topic": "weekly_report"},
                    observation="Summarized notes into a draft.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/fallback_report.txt"],
            started_at="2026-04-18T12:00:00",
            ended_at="2026-04-18T12:01:00",
        )

        generated = SkillGenerator(ROOT / "skill_store" / "staging").generate(
            trajectory, skill_name="fallback_rule_test"
        )
        self.assertEqual("llm_fallback", generated["metadata"].rule_name)
        self.assertEqual(0, generated["metadata"].rule_priority)
        self.assertIsNotNone(generated["fallback_artifact"])
        artifact_path = Path(generated["fallback_artifact"])
        self.assertTrue(artifact_path.exists())
        artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
        self.assertEqual("mock_fallback_provider", artifact["response"]["provider_name"])
        self.assertIn("Skill name: fallback_rule_test", artifact["request"]["prompt"])


if __name__ == "__main__":
    unittest.main()
