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

    def test_search_returns_active_skill(self) -> None:
        results = self.index.search("merge txt files into markdown", top_k=20)
        self.assertTrue(results)
        names = {result["skill_name"] for result in results}
        self.assertIn("merge_text_files", names)
        first = results[0]
        self.assertEqual("execute_skill", first["recommended_next_action"])
        self.assertIn("rule_name", first)
        self.assertIn("rule_reason", first)

    def test_service_search_matches_cli_shape(self) -> None:
        payload = self.service.search("merge txt files into markdown", top_k=3)
        self.assertEqual("merge txt files into markdown", payload["query"])
        self.assertTrue(payload["results"])
        self.assertEqual("execute_skill", payload["recommended_next_action"])
        self.assertIsNotNone(payload["recommended_skill_name"])
        self.assertIn("why_matched", payload["results"][0])

    def test_mcp_search_tool_returns_structured_payload(self) -> None:
        server = build_mcp_server(ROOT)
        _, payload = asyncio.run(
            server.call_tool("search_skill", {"query": "merge txt files into markdown", "top_k": 3})
        )
        self.assertEqual("ok", payload["status"])
        self.assertTrue(payload["data"]["results"])
        self.assertEqual("execute_skill", payload["data"]["recommended_next_action"])
        self.assertIn("rule_name", payload["data"]["results"][0])

    def test_service_search_without_matches_recommends_distill_and_promote(self) -> None:
        payload = self.service.search("nonexistent workflow phrase for zero matches", top_k=3)
        self.assertEqual("distill_and_promote_candidate", payload["recommended_next_action"])
        self.assertIsNone(payload["recommended_skill_name"])
        self.assertTrue(payload["results"])
        self.assertLess(payload["results"][0]["score"], self.service.RECOMMENDED_EXECUTION_SCORE)

    def test_mcp_server_root_resolution(self) -> None:
        self.assertEqual(ROOT, resolve_runtime_root())
        self.assertEqual(ROOT, resolve_runtime_root(str(ROOT)))

    def test_service_distill_and_promote_flow(self) -> None:
        result = self.service.distill_and_promote(
            ROOT / "trajectories" / "demo_merge_text_files.json",
            skill_name="service_distill_and_promote_test",
        )
        self.assertTrue(result["promoted"])
        self.assertIsNotNone(result["trajectory"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("service_distill_and_promote_test", result["promotion"]["skill_name"])

        promoted = self.index.get("service_distill_and_promote_test")
        self.assertIsNotNone(promoted)
        self.assertEqual("active", promoted.status)

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

        after = self.index.get("merge_text_files")
        self.assertIsNotNone(after)
        self.assertEqual(before_usage + 1, after.usage_count)
        self.assertIsNotNone(after.last_used_at)

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
