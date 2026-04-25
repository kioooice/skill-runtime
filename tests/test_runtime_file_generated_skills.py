import json

from skill_runtime.api.models import Trajectory, TrajectoryStep
from skill_runtime.memory.trajectory_store import TrajectoryStore
from tests.runtime_test_support import ROOT


class RuntimeFileGeneratedSkillTestsMixin:
    def test_distilled_merge_skill_writes_output(self) -> None:
        output_path = ROOT / "demo" / "output" / "generated.md"
        if output_path.exists():
            output_path.unlink()

        trajectory = TrajectoryStore(ROOT / "trajectories").load("demo_merge_text_files")
        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="merge_text_files_rule_test",
        )
        self.assertEqual("text_merge", generated["metadata"].rule_name)
        self.assertIsNotNone(generated["metadata"].rule_reason)
        payload = self._execute_skill_cli(
            "merge_text_files_rule_test",
            args_file=ROOT / "demo" / "execute_args.json",
        )
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

        self._generate_and_activate_skill(trajectory, skill_name="single_file_transform_rule_test")
        args_file = self._write_args_file(
            "single_transform_args.json",
            {"input_path": "demo/input/a.txt", "output_path": "demo/output/single_transform.txt"},
        )
        self._execute_skill_cli("single_file_transform_rule_test", args_file=args_file)
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

        generated = self._generate_and_activate_skill(trajectory, skill_name="text_replace_rule_test")
        self.assertEqual("text_replace", generated["metadata"].rule_name)
        self.assertGreater(generated["metadata"].rule_priority, 0)
        args_file = self._write_args_file(
            "text_replace_args.json",
            {
                "input_path": "demo/input/a.txt",
                "output_path": "demo/output/replace_output.txt",
                "old_text": "file",
                "new_text": "document",
            },
        )
        self._execute_skill_cli("text_replace_rule_test", args_file=args_file)
        self.assertTrue(output_path.exists())
        self.assertIn("document a", output_path.read_text(encoding="utf-8"))

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

        generated = self._generate_and_activate_skill(trajectory, skill_name="csv_to_json_rule_test")
        self.assertEqual("csv_to_json", generated["metadata"].rule_name)
        args_file = self._write_args_file(
            "csv_to_json_args.json",
            {"input_path": "demo/input/table.csv", "output_path": "demo/output/table.json"},
        )
        self._execute_skill_cli("csv_to_json_rule_test", args_file=args_file)
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

        generated = self._generate_and_activate_skill(trajectory, skill_name="json_to_csv_rule_test")
        self.assertEqual("json_to_csv", generated["metadata"].rule_name)
        args_file = self._write_args_file(
            "json_to_csv_args.json",
            {"input_path": "demo/input/table.json", "output_path": "demo/output/table.csv"},
        )
        self._execute_skill_cli("json_to_csv_rule_test", args_file=args_file)
        csv_text = output_path.read_text(encoding="utf-8")
        self.assertIn("name,age", csv_text)
        self.assertIn("alice,30", csv_text)
