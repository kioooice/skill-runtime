import json

from skill_runtime.api.models import Trajectory, TrajectoryStep
from skill_runtime.memory.trajectory_store import TrajectoryStore
from tests.runtime_test_support import ROOT


class RuntimeFileGeneratedSkillTestsMixin:
    def test_distilled_merge_skill_writes_output(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        output_path = sandbox_root / "demo" / "output" / "generated.md"

        trajectory = TrajectoryStore(sandbox_root / "trajectories").load("demo_merge_text_files")
        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="merge_text_files_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("text_merge", generated["metadata"].rule_name)
        self.assertIsNotNone(generated["metadata"].rule_reason)
        payload = self._execute_skill_cli(
            "merge_text_files_rule_test",
            args_file=sandbox_root / "demo" / "execute_args.json",
            root=sandbox_root,
        )
        self.assertTrue(output_path.exists())
        self.assertIn("hello from file a", output_path.read_text(encoding="utf-8"))

        search_results = sandbox_index.search("merge txt files into markdown", top_k=50)
        generated_match = next(
            result for result in search_results if result["skill_name"] == "merge_text_files_rule_test"
        )
        self.assertEqual("text_merge", generated_match["rule_name"])
        self.assertIn("merging txt files", generated_match["rule_reason"])

    def test_distilled_merge_skill_include_alias_uses_canonical_schema(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        output_path = sandbox_root / "demo" / "output" / "generated_include.md"

        trajectory = Trajectory(
            task_id="merge_include_alias_demo",
            session_id="session_merge_include_alias",
            task_description="Merge matching txt files into one markdown file.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"input_dir": "demo/input", "include": "*.txt"},
                    observation="Found txt files to merge.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_text",
                    tool_input={"input_dir": "demo/input"},
                    observation="Read each source file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_text",
                    tool_input={"output_text_file": "demo/output/generated_include.md"},
                    observation="Wrote merged markdown output.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/generated_include.md"],
            started_at="2026-04-25T12:40:00",
            ended_at="2026-04-25T12:41:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="merge_text_include_alias_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("text_merge", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_dir": "str", "output_path": "str", "pattern": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "merge_include_alias_args.json",
            {"input_dir": "demo/input", "output_path": "demo/output/generated_include.md", "pattern": "*.txt"},
            root=sandbox_root,
        )
        self._execute_skill_cli("merge_text_include_alias_rule_test", args_file=args_file, root=sandbox_root)
        self.assertTrue(output_path.exists())
        self.assertIn("hello from file a", output_path.read_text(encoding="utf-8"))

    def test_distilled_merge_skill_preserves_write_text_newline_input(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        output_path = sandbox_root / "demo" / "output" / "generated_crlf.md"

        trajectory = Trajectory(
            task_id="merge_text_newline_demo",
            session_id="session_merge_text_newline",
            task_description="Merge matching txt files into one markdown file.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"input_dir": "demo/input", "pattern": "*.txt"},
                    observation="Found txt files to merge.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_text",
                    tool_input={"input_dir": "demo/input"},
                    observation="Read each source file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_text",
                    tool_input={"output_path": "demo/output/generated_crlf.md", "newline": "\n"},
                    observation="Wrote merged markdown output with LF line endings.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/generated_crlf.md"],
            started_at="2026-04-26T22:10:00",
            ended_at="2026-04-26T22:11:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="merge_text_newline_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("text_merge", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_dir": "str", "newline": "str", "output_path": "str", "pattern": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "merge_newline_args.json",
            {
                "input_dir": "demo/input",
                "output_path": "demo/output/generated_crlf.md",
                "pattern": "*.txt",
                "newline": "\n",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("merge_text_newline_rule_test", args_file=args_file, root=sandbox_root)
        output_bytes = output_path.read_bytes()
        self.assertIn(b"\n", output_bytes)
        self.assertNotIn(b"\r\n", output_bytes)

    def test_distilled_single_file_transform_writes_output(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        output_path = sandbox_root / "demo" / "output" / "single_transform.txt"

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

        self._generate_and_activate_skill(
            trajectory,
            skill_name="single_file_transform_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        args_file = self._write_args_file(
            "single_transform_args.json",
            {"input_path": "demo/input/a.txt", "output_path": "demo/output/single_transform.txt"},
            root=sandbox_root,
        )
        self._execute_skill_cli("single_file_transform_rule_test", args_file=args_file, root=sandbox_root)
        self.assertTrue(output_path.exists())
        self.assertEqual("hello from file a\n", output_path.read_text(encoding="utf-8"))

    def test_distilled_single_file_transform_preserves_write_text_newline_input(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        output_path = sandbox_root / "demo" / "output" / "single_transform_crlf.txt"

        trajectory = Trajectory(
            task_id="single_transform_newline_demo",
            session_id="session_single_transform_newline",
            task_description="Read one text file and write it to a new output file.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="read_text",
                    tool_input={"input_path": "demo/input/a.txt"},
                    observation="Read the source file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="write_text",
                    tool_input={"output_path": "demo/output/single_transform_crlf.txt", "newline": "\n"},
                    observation="Wrote the transformed text with LF endings.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/single_transform_crlf.txt"],
            started_at="2026-04-26T22:12:00",
            ended_at="2026-04-26T22:13:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="single_file_transform_newline_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("single_file_transform", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_path": "str", "newline": "str", "output_path": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "single_transform_newline_args.json",
            {
                "input_path": "demo/input/a.txt",
                "output_path": "demo/output/single_transform_crlf.txt",
                "newline": "\n",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("single_file_transform_newline_rule_test", args_file=args_file, root=sandbox_root)
        output_bytes = output_path.read_bytes()
        self.assertIn(b"\n", output_bytes)
        self.assertNotIn(b"\r\n", output_bytes)

    def test_distilled_single_file_transform_source_destination_aliases_use_canonical_schema(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        output_path = sandbox_root / "demo" / "output" / "single_transform_source_destination.txt"

        trajectory = Trajectory(
            task_id="single_transform_source_destination_alias_demo",
            session_id="session_single_transform_source_destination_alias",
            task_description="Read one text file and write it to a new output file.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="read_text",
                    tool_input={"source": "demo/input/a.txt"},
                    observation="Read the source file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="write_text",
                    tool_input={"destination": "demo/output/single_transform_source_destination.txt"},
                    observation="Wrote the transformed text.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/single_transform_source_destination.txt"],
            started_at="2026-04-26T13:15:00",
            ended_at="2026-04-26T13:16:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="single_file_transform_source_destination_alias_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("single_file_transform", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_path": "str", "output_path": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "single_transform_source_destination_alias_args.json",
            {
                "input_path": "demo/input/a.txt",
                "output_path": "demo/output/single_transform_source_destination.txt",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli(
            "single_file_transform_source_destination_alias_rule_test",
            args_file=args_file,
            root=sandbox_root,
        )
        self.assertTrue(output_path.exists())
        self.assertEqual("hello from file a\n", output_path.read_text(encoding="utf-8"))

    def test_distilled_text_replace_writes_output(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        output_path = sandbox_root / "demo" / "output" / "replace_output.txt"

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

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="text_replace_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
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
            root=sandbox_root,
        )
        self._execute_skill_cli("text_replace_rule_test", args_file=args_file, root=sandbox_root)
        self.assertTrue(output_path.exists())
        self.assertIn("document a", output_path.read_text(encoding="utf-8"))

    def test_distilled_text_replace_preserves_write_text_newline_input(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        output_path = sandbox_root / "demo" / "output" / "replace_output_crlf.txt"

        trajectory = Trajectory(
            task_id="text_replace_newline_demo",
            session_id="session_text_replace_newline",
            task_description="Replace one string with another in a text file and write a new output file.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="read_text",
                    tool_input={"input_path": "demo/input/a.txt", "old_text": "file", "new_text": "document"},
                    observation="Read source text for replacement.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="write_text",
                    tool_input={"output_path": "demo/output/replace_output_crlf.txt", "newline": "\n"},
                    observation="Wrote replaced text output with LF endings.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/replace_output_crlf.txt"],
            started_at="2026-04-26T22:14:00",
            ended_at="2026-04-26T22:15:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="text_replace_newline_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("text_replace", generated["metadata"].rule_name)
        self.assertEqual(
            {
                "input_path": "str",
                "new_text": "str",
                "newline": "str",
                "old_text": "str",
                "output_path": "str",
            },
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "text_replace_newline_args.json",
            {
                "input_path": "demo/input/a.txt",
                "output_path": "demo/output/replace_output_crlf.txt",
                "old_text": "file",
                "new_text": "document",
                "newline": "\n",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("text_replace_newline_rule_test", args_file=args_file, root=sandbox_root)
        output_bytes = output_path.read_bytes()
        self.assertIn(b"\n", output_bytes)
        self.assertNotIn(b"\r\n", output_bytes)

    def test_distilled_text_replace_search_replace_aliases_use_canonical_schema(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        output_path = sandbox_root / "demo" / "output" / "replace_alias_output.txt"

        trajectory = Trajectory(
            task_id="text_replace_alias_demo",
            session_id="session_text_replace_alias",
            task_description="Replace one string with another in a text file and write a new output file.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="read_text",
                    tool_input={"input": "demo/input/a.txt", "search": "file", "replace": "document"},
                    observation="Read source text for replacement.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="write_text",
                    tool_input={"output": "demo/output/replace_alias_output.txt"},
                    observation="Wrote replaced text output.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/replace_alias_output.txt"],
            started_at="2026-04-25T12:00:00",
            ended_at="2026-04-25T12:01:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="text_replace_alias_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("text_replace", generated["metadata"].rule_name)
        self.assertEqual(
            {
                "input_path": "str",
                "new_text": "str",
                "old_text": "str",
                "output_path": "str",
            },
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "text_replace_alias_args.json",
            {
                "input_path": "demo/input/a.txt",
                "output_path": "demo/output/replace_alias_output.txt",
                "old_text": "file",
                "new_text": "document",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("text_replace_alias_rule_test", args_file=args_file, root=sandbox_root)
        self.assertTrue(output_path.exists())
        self.assertIn("document a", output_path.read_text(encoding="utf-8"))

    def test_distilled_single_file_copy_writes_output(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        output_path = sandbox_root / "demo" / "output" / "single_copy.txt"
        self.addCleanup(lambda: output_path.unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="single_copy_demo",
            session_id="session_single_copy",
            task_description="Copy one text file into a new output file.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="copy_file",
                    tool_input={"input_path": "demo/input/a.txt", "output_path": "demo/output/single_copy.txt"},
                    observation="Copied the source file.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/single_copy.txt"],
            started_at="2026-04-18T11:10:00",
            ended_at="2026-04-18T11:11:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="single_file_copy_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("single_file_copy", generated["metadata"].rule_name)
        args_file = self._write_args_file(
            "single_copy_args.json",
            {"input_path": "demo/input/a.txt", "output_path": "demo/output/single_copy.txt"},
            root=sandbox_root,
        )
        self._execute_skill_cli("single_file_copy_rule_test", args_file=args_file, root=sandbox_root)
        self.assertTrue(output_path.exists())
        self.assertEqual("hello from file a\n", output_path.read_text(encoding="utf-8"))

    def test_distilled_single_file_copy_input_output_aliases_use_canonical_schema(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        output_path = sandbox_root / "demo" / "output" / "single_copy_input_output.txt"
        self.addCleanup(lambda: output_path.unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="single_copy_input_output_alias_demo",
            session_id="session_single_copy_input_output_alias",
            task_description="Copy one text file into a new output file.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="copy_file",
                    tool_input={"input": "demo/input/a.txt", "output": "demo/output/single_copy_input_output.txt"},
                    observation="Copied the source file.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/single_copy_input_output.txt"],
            started_at="2026-04-26T12:15:00",
            ended_at="2026-04-26T12:16:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="single_file_copy_input_output_alias_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("single_file_copy", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_path": "str", "output_path": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "single_copy_input_output_alias_args.json",
            {"input_path": "demo/input/a.txt", "output_path": "demo/output/single_copy_input_output.txt"},
            root=sandbox_root,
        )
        self._execute_skill_cli("single_file_copy_input_output_alias_rule_test", args_file=args_file, root=sandbox_root)
        self.assertTrue(output_path.exists())
        self.assertEqual("hello from file a\n", output_path.read_text(encoding="utf-8"))

    def test_distilled_single_file_copy_source_target_aliases_use_canonical_schema(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        output_path = sandbox_root / "demo" / "output" / "single_copy_source_target.txt"
        self.addCleanup(lambda: output_path.unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="single_copy_source_target_alias_demo",
            session_id="session_single_copy_source_target_alias",
            task_description="Copy one text file into a new output file.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="copy_file",
                    tool_input={"source": "demo/input/a.txt", "target": "demo/output/single_copy_source_target.txt"},
                    observation="Copied the source file.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/single_copy_source_target.txt"],
            started_at="2026-04-26T12:30:00",
            ended_at="2026-04-26T12:31:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="single_file_copy_source_target_alias_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("single_file_copy", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_path": "str", "output_path": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "single_copy_source_target_alias_args.json",
            {"input_path": "demo/input/a.txt", "output_path": "demo/output/single_copy_source_target.txt"},
            root=sandbox_root,
        )
        self._execute_skill_cli("single_file_copy_source_target_alias_rule_test", args_file=args_file, root=sandbox_root)
        self.assertTrue(output_path.exists())
        self.assertEqual("hello from file a\n", output_path.read_text(encoding="utf-8"))

    def test_distilled_single_file_copy_destination_alias_use_canonical_schema(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        output_path = sandbox_root / "demo" / "output" / "single_copy_destination.txt"
        self.addCleanup(lambda: output_path.unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="single_copy_destination_alias_demo",
            session_id="session_single_copy_destination_alias",
            task_description="Copy one text file into a new output file.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="copy_file",
                    tool_input={"source_file": "demo/input/a.txt", "destination": "demo/output/single_copy_destination.txt"},
                    observation="Copied the source file.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/single_copy_destination.txt"],
            started_at="2026-04-26T12:32:00",
            ended_at="2026-04-26T12:33:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="single_file_copy_destination_alias_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("single_file_copy", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_path": "str", "output_path": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "single_copy_destination_alias_args.json",
            {"input_path": "demo/input/a.txt", "output_path": "demo/output/single_copy_destination.txt"},
            root=sandbox_root,
        )
        self._execute_skill_cli("single_file_copy_destination_alias_rule_test", args_file=args_file, root=sandbox_root)
        self.assertTrue(output_path.exists())
        self.assertEqual("hello from file a\n", output_path.read_text(encoding="utf-8"))

    def test_distilled_single_file_move_writes_output(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        input_path = sandbox_root / "demo" / "input" / "single_move_source.txt"
        output_path = sandbox_root / "demo" / "output" / "single_move.txt"
        input_path.write_text("move me\n", encoding="utf-8")
        self.addCleanup(lambda: input_path.unlink(missing_ok=True))
        self.addCleanup(lambda: output_path.unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="single_move_demo",
            session_id="session_single_move",
            task_description="Move one text file into a new output file.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="move_file",
                    tool_input={
                        "input_path": "demo/input/single_move_source.txt",
                        "output_path": "demo/output/single_move.txt",
                    },
                    observation="Moved the source file.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/single_move.txt"],
            started_at="2026-04-18T11:12:00",
            ended_at="2026-04-18T11:13:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="single_file_move_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("single_file_move", generated["metadata"].rule_name)
        args_file = self._write_args_file(
            "single_move_args.json",
            {
                "input_path": "demo/input/single_move_source.txt",
                "output_path": "demo/output/single_move.txt",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("single_file_move_rule_test", args_file=args_file, root=sandbox_root)
        self.assertFalse(input_path.exists())
        self.assertTrue(output_path.exists())
        self.assertEqual("move me\n", output_path.read_text(encoding="utf-8"))

    def test_distilled_single_file_move_from_to_aliases_use_canonical_schema(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        input_path = sandbox_root / "demo" / "input" / "single_move_from_to_source.txt"
        output_path = sandbox_root / "demo" / "output" / "single_move_from_to.txt"
        input_path.write_text("move me too\n", encoding="utf-8")
        self.addCleanup(lambda: input_path.unlink(missing_ok=True))
        self.addCleanup(lambda: output_path.unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="single_move_from_to_alias_demo",
            session_id="session_single_move_from_to_alias",
            task_description="Move one text file into a new output file.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="move_file",
                    tool_input={
                        "from": "demo/input/single_move_from_to_source.txt",
                        "to": "demo/output/single_move_from_to.txt",
                    },
                    observation="Moved the source file.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/single_move_from_to.txt"],
            started_at="2026-04-25T12:50:00",
            ended_at="2026-04-25T12:51:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="single_file_move_from_to_alias_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("single_file_move", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_path": "str", "output_path": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "single_move_from_to_alias_args.json",
            {
                "input_path": "demo/input/single_move_from_to_source.txt",
                "output_path": "demo/output/single_move_from_to.txt",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("single_file_move_from_to_alias_rule_test", args_file=args_file, root=sandbox_root)
        self.assertFalse(input_path.exists())
        self.assertTrue(output_path.exists())
        self.assertEqual("move me too\n", output_path.read_text(encoding="utf-8"))

    def test_distilled_single_file_move_input_output_aliases_use_canonical_schema(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        input_path = sandbox_root / "demo" / "input" / "single_move_input_output_source.txt"
        output_path = sandbox_root / "demo" / "output" / "single_move_input_output.txt"
        input_path.write_text("move me three\n", encoding="utf-8")
        self.addCleanup(lambda: input_path.unlink(missing_ok=True))
        self.addCleanup(lambda: output_path.unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="single_move_input_output_alias_demo",
            session_id="session_single_move_input_output_alias",
            task_description="Move one text file into a new output file.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="move_file",
                    tool_input={
                        "input": "demo/input/single_move_input_output_source.txt",
                        "output": "demo/output/single_move_input_output.txt",
                    },
                    observation="Moved the source file.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/single_move_input_output.txt"],
            started_at="2026-04-26T11:30:00",
            ended_at="2026-04-26T11:31:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="single_file_move_input_output_alias_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("single_file_move", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_path": "str", "output_path": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "single_move_input_output_alias_args.json",
            {
                "input_path": "demo/input/single_move_input_output_source.txt",
                "output_path": "demo/output/single_move_input_output.txt",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("single_file_move_input_output_alias_rule_test", args_file=args_file, root=sandbox_root)
        self.assertFalse(input_path.exists())
        self.assertTrue(output_path.exists())
        self.assertEqual("move me three\n", output_path.read_text(encoding="utf-8"))

    def test_distilled_single_file_rename_alias_writes_output(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        input_path = sandbox_root / "demo" / "input" / "single_rename_source.txt"
        output_path = sandbox_root / "demo" / "output" / "single_rename.txt"
        input_path.write_text("rename me\n", encoding="utf-8")
        self.addCleanup(lambda: input_path.unlink(missing_ok=True))
        self.addCleanup(lambda: output_path.unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="single_rename_alias_demo",
            session_id="session_single_rename_alias",
            task_description="Rename one text file to a new output path.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="rename_path",
                    tool_input={
                        "source": "demo/input/single_rename_source.txt",
                        "target": "demo/output/single_rename.txt",
                    },
                    observation="Renamed the source file.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/single_rename.txt"],
            started_at="2026-04-25T10:02:00",
            ended_at="2026-04-25T10:03:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="single_file_rename_alias_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("single_file_move", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_path": "str", "output_path": "str"},
            generated["metadata"].input_schema,
        )
        self.assertIn("tools.rename_path", generated["skill_file"].read_text(encoding="utf-8"))
        args_file = self._write_args_file(
            "single_rename_alias_args.json",
            {
                "input_path": "demo/input/single_rename_source.txt",
                "output_path": "demo/output/single_rename.txt",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("single_file_rename_alias_rule_test", args_file=args_file, root=sandbox_root)
        self.assertFalse(input_path.exists())
        self.assertTrue(output_path.exists())
        self.assertEqual("rename me\n", output_path.read_text(encoding="utf-8"))

    def test_distilled_single_file_rename_input_output_aliases_use_canonical_schema(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        input_path = sandbox_root / "demo" / "input" / "single_rename_input_output_source.txt"
        output_path = sandbox_root / "demo" / "output" / "single_rename_input_output.txt"
        input_path.write_text("rename me too\n", encoding="utf-8")
        self.addCleanup(lambda: input_path.unlink(missing_ok=True))
        self.addCleanup(lambda: output_path.unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="single_rename_input_output_alias_demo",
            session_id="session_single_rename_input_output_alias",
            task_description="Rename one text file to a new output path.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="rename_path",
                    tool_input={
                        "input": "demo/input/single_rename_input_output_source.txt",
                        "output": "demo/output/single_rename_input_output.txt",
                    },
                    observation="Renamed the source file.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/single_rename_input_output.txt"],
            started_at="2026-04-26T12:17:00",
            ended_at="2026-04-26T12:18:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="single_file_rename_input_output_alias_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("single_file_move", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_path": "str", "output_path": "str"},
            generated["metadata"].input_schema,
        )
        self.assertIn("tools.rename_path", generated["skill_file"].read_text(encoding="utf-8"))
        args_file = self._write_args_file(
            "single_rename_input_output_alias_args.json",
            {
                "input_path": "demo/input/single_rename_input_output_source.txt",
                "output_path": "demo/output/single_rename_input_output.txt",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("single_file_rename_input_output_alias_rule_test", args_file=args_file, root=sandbox_root)
        self.assertFalse(input_path.exists())
        self.assertTrue(output_path.exists())
        self.assertEqual("rename me too\n", output_path.read_text(encoding="utf-8"))

    def test_distilled_csv_to_json_writes_output(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        input_path = sandbox_root / "demo" / "input" / "table.csv"
        output_path = sandbox_root / "demo" / "output" / "table.json"
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

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="csv_to_json_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("csv_to_json", generated["metadata"].rule_name)
        args_file = self._write_args_file(
            "csv_to_json_args.json",
            {"input_path": "demo/input/table.csv", "output_path": "demo/output/table.json"},
            root=sandbox_root,
        )
        self._execute_skill_cli("csv_to_json_rule_test", args_file=args_file, root=sandbox_root)
        payload = json.loads(output_path.read_text(encoding="utf-8"))
        self.assertEqual("alice", payload[0]["name"])
        self.assertEqual("31", payload[1]["age"])

    def test_distilled_csv_to_json_sep_alias_uses_canonical_schema(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        input_path = sandbox_root / "demo" / "input" / "table_pipe.csv"
        output_path = sandbox_root / "demo" / "output" / "table_pipe.json"
        input_path.write_text("name|age\nalice|30\nbob|31\n", encoding="utf-8")
        self.addCleanup(lambda: input_path.unlink(missing_ok=True))
        self.addCleanup(lambda: output_path.unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="csv_to_json_sep_alias_demo",
            session_id="session_csv_to_json_sep_alias",
            task_description="Convert a CSV file into a JSON array file.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="read_text",
                    tool_input={"input": "demo/input/table_pipe.csv", "sep": "|"},
                    observation="Read pipe-delimited CSV input.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="write_json",
                    tool_input={"output": "demo/output/table_pipe.json"},
                    observation="Wrote JSON output.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/table_pipe.json"],
            started_at="2026-04-25T12:10:00",
            ended_at="2026-04-25T12:11:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="csv_to_json_sep_alias_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("csv_to_json", generated["metadata"].rule_name)
        self.assertEqual(
            {
                "delimiter": "str",
                "input_path": "str",
                "output_path": "str",
            },
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "csv_to_json_sep_alias_args.json",
            {
                "input_path": "demo/input/table_pipe.csv",
                "output_path": "demo/output/table_pipe.json",
                "delimiter": "|",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("csv_to_json_sep_alias_rule_test", args_file=args_file, root=sandbox_root)
        payload = json.loads(output_path.read_text(encoding="utf-8"))
        self.assertEqual("alice", payload[0]["name"])
        self.assertEqual("31", payload[1]["age"])

    def test_distilled_csv_to_json_csv_aliases_use_canonical_schema(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        input_path = sandbox_root / "demo" / "input" / "table_alias.csv"
        output_path = sandbox_root / "demo" / "output" / "table_alias.json"
        input_path.write_text("name,age\nalice,30\nbob,31\n", encoding="utf-8")
        self.addCleanup(lambda: input_path.unlink(missing_ok=True))
        self.addCleanup(lambda: output_path.unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="csv_to_json_csv_alias_demo",
            session_id="session_csv_to_json_csv_alias",
            task_description="Convert a CSV file into a JSON array file.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="read_text",
                    tool_input={"input_csv": "demo/input/table_alias.csv"},
                    observation="Read CSV input.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="write_json",
                    tool_input={"output_json": "demo/output/table_alias.json"},
                    observation="Wrote JSON output.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/table_alias.json"],
            started_at="2026-04-25T12:24:00",
            ended_at="2026-04-25T12:25:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="csv_to_json_csv_alias_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("csv_to_json", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_path": "str", "output_path": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "csv_to_json_csv_alias_args.json",
            {"input_path": "demo/input/table_alias.csv", "output_path": "demo/output/table_alias.json"},
            root=sandbox_root,
        )
        self._execute_skill_cli("csv_to_json_csv_alias_rule_test", args_file=args_file, root=sandbox_root)
        payload = json.loads(output_path.read_text(encoding="utf-8"))
        self.assertEqual("alice", payload[0]["name"])
        self.assertEqual("31", payload[1]["age"])

    def test_distilled_csv_to_json_source_destination_aliases_use_canonical_schema(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        input_path = sandbox_root / "demo" / "input" / "table_source_destination.csv"
        output_path = sandbox_root / "demo" / "output" / "table_source_destination.json"
        input_path.write_text("name,age\nalice,30\nbob,31\n", encoding="utf-8")
        self.addCleanup(lambda: input_path.unlink(missing_ok=True))
        self.addCleanup(lambda: output_path.unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="csv_to_json_source_destination_alias_demo",
            session_id="session_csv_to_json_source_destination_alias",
            task_description="Convert a CSV file into a JSON array file.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="read_text",
                    tool_input={"source": "demo/input/table_source_destination.csv"},
                    observation="Read CSV input.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="write_json",
                    tool_input={"destination": "demo/output/table_source_destination.json"},
                    observation="Wrote JSON output.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/table_source_destination.json"],
            started_at="2026-04-26T13:00:00",
            ended_at="2026-04-26T13:01:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="csv_to_json_source_destination_alias_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("csv_to_json", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_path": "str", "output_path": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "csv_to_json_source_destination_alias_args.json",
            {"input_path": "demo/input/table_source_destination.csv", "output_path": "demo/output/table_source_destination.json"},
            root=sandbox_root,
        )
        self._execute_skill_cli("csv_to_json_source_destination_alias_rule_test", args_file=args_file, root=sandbox_root)
        payload = json.loads(output_path.read_text(encoding="utf-8"))
        self.assertEqual("alice", payload[0]["name"])
        self.assertEqual("31", payload[1]["age"])

    def test_distilled_json_to_csv_writes_output(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        input_path = sandbox_root / "demo" / "input" / "table.json"
        output_path = sandbox_root / "demo" / "output" / "table.csv"
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

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="json_to_csv_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("json_to_csv", generated["metadata"].rule_name)
        args_file = self._write_args_file(
            "json_to_csv_args.json",
            {"input_path": "demo/input/table.json", "output_path": "demo/output/table.csv"},
            root=sandbox_root,
        )
        self._execute_skill_cli("json_to_csv_rule_test", args_file=args_file, root=sandbox_root)
        csv_text = output_path.read_text(encoding="utf-8")
        self.assertIn("name,age", csv_text)
        self.assertIn("alice,30", csv_text)

    def test_distilled_json_to_csv_csv_aliases_use_canonical_schema(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        input_path = sandbox_root / "demo" / "input" / "table_alias.json"
        output_path = sandbox_root / "demo" / "output" / "table_alias.csv"
        input_path.write_text(
            json.dumps([{"name": "alice", "age": "30"}, {"name": "bob", "age": "31"}], ensure_ascii=False),
            encoding="utf-8",
        )
        self.addCleanup(lambda: input_path.unlink(missing_ok=True))
        self.addCleanup(lambda: output_path.unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="json_to_csv_csv_alias_demo",
            session_id="session_json_to_csv_csv_alias",
            task_description="Convert a JSON array file into CSV format.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="read_json",
                    tool_input={"source_json": "demo/input/table_alias.json"},
                    observation="Read JSON input.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="write_text",
                    tool_input={"target_csv": "demo/output/table_alias.csv"},
                    observation="Wrote CSV output.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/table_alias.csv"],
            started_at="2026-04-25T12:26:00",
            ended_at="2026-04-25T12:27:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="json_to_csv_csv_alias_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("json_to_csv", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_path": "str", "output_path": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "json_to_csv_csv_alias_args.json",
            {"input_path": "demo/input/table_alias.json", "output_path": "demo/output/table_alias.csv"},
            root=sandbox_root,
        )
        self._execute_skill_cli("json_to_csv_csv_alias_rule_test", args_file=args_file, root=sandbox_root)
        csv_text = output_path.read_text(encoding="utf-8")
        self.assertIn("name,age", csv_text)
        self.assertIn("alice,30", csv_text)

    def test_distilled_json_to_csv_delimiter_alias_uses_canonical_schema(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        input_path = sandbox_root / "demo" / "input" / "table_pipe.json"
        output_path = sandbox_root / "demo" / "output" / "table_pipe.csv"
        input_path.write_text(
            json.dumps([{"name": "alice", "age": "30"}, {"name": "bob", "age": "31"}], ensure_ascii=False),
            encoding="utf-8",
        )
        self.addCleanup(lambda: input_path.unlink(missing_ok=True))
        self.addCleanup(lambda: output_path.unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="json_to_csv_delimiter_alias_demo",
            session_id="session_json_to_csv_delimiter_alias",
            task_description="Convert a JSON array file into CSV format.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="read_json",
                    tool_input={"file": "demo/input/table_pipe.json"},
                    observation="Read JSON input.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="write_text",
                    tool_input={"output": "demo/output/table_pipe.csv", "separator": "|"},
                    observation="Wrote pipe-delimited CSV output.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/table_pipe.csv"],
            started_at="2026-04-25T12:12:00",
            ended_at="2026-04-25T12:13:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="json_to_csv_delimiter_alias_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("json_to_csv", generated["metadata"].rule_name)
        self.assertEqual(
            {
                "delimiter": "str",
                "input_path": "str",
                "output_path": "str",
            },
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "json_to_csv_delimiter_alias_args.json",
            {
                "input_path": "demo/input/table_pipe.json",
                "output_path": "demo/output/table_pipe.csv",
                "delimiter": "|",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("json_to_csv_delimiter_alias_rule_test", args_file=args_file, root=sandbox_root)
        csv_text = output_path.read_text(encoding="utf-8")
        self.assertIn("name|age", csv_text)
        self.assertIn("alice|30", csv_text)

    def test_distilled_json_to_csv_source_destination_aliases_use_canonical_schema(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        input_path = sandbox_root / "demo" / "input" / "table_source_destination.json"
        output_path = sandbox_root / "demo" / "output" / "table_source_destination.csv"
        input_path.write_text(
            json.dumps([{"name": "alice", "age": "30"}, {"name": "bob", "age": "31"}], ensure_ascii=False),
            encoding="utf-8",
        )
        self.addCleanup(lambda: input_path.unlink(missing_ok=True))
        self.addCleanup(lambda: output_path.unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="json_to_csv_source_destination_alias_demo",
            session_id="session_json_to_csv_source_destination_alias",
            task_description="Convert a JSON array file into CSV format.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="read_json",
                    tool_input={"source": "demo/input/table_source_destination.json"},
                    observation="Read JSON input.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="write_text",
                    tool_input={"destination": "demo/output/table_source_destination.csv"},
                    observation="Wrote CSV output.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/table_source_destination.csv"],
            started_at="2026-04-26T13:02:00",
            ended_at="2026-04-26T13:03:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="json_to_csv_source_destination_alias_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("json_to_csv", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_path": "str", "output_path": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "json_to_csv_source_destination_alias_args.json",
            {"input_path": "demo/input/table_source_destination.json", "output_path": "demo/output/table_source_destination.csv"},
            root=sandbox_root,
        )
        self._execute_skill_cli("json_to_csv_source_destination_alias_rule_test", args_file=args_file, root=sandbox_root)
        csv_text = output_path.read_text(encoding="utf-8")
        self.assertIn("name,age", csv_text)
        self.assertIn("alice,30", csv_text)

    def test_distilled_json_to_csv_preserves_csv_writer_formatting_inputs(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        input_path = sandbox_root / "demo" / "input" / "table_csv_formatting.json"
        output_path = sandbox_root / "demo" / "output" / "table_csv_formatting.csv"
        input_path.write_text(
            json.dumps([{"name": "alice,smith", "age": "30"}], ensure_ascii=False),
            encoding="utf-8",
        )
        self.addCleanup(lambda: input_path.unlink(missing_ok=True))
        self.addCleanup(lambda: output_path.unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="json_to_csv_formatting_demo",
            session_id="session_json_to_csv_formatting",
            task_description="Convert a JSON array file into CSV format.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="read_json",
                    tool_input={"path": "demo/input/table_csv_formatting.json"},
                    observation="Read JSON input.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="write_text",
                    tool_input={
                        "path": "demo/output/table_csv_formatting.csv",
                        "quotechar": "'",
                        "quoting": "QUOTE_ALL",
                    },
                    observation="Wrote quoted CSV output.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/table_csv_formatting.csv"],
            started_at="2026-04-26T17:20:00",
            ended_at="2026-04-26T17:21:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="json_to_csv_formatting_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("json_to_csv", generated["metadata"].rule_name)
        self.assertEqual(
            {
                "input_path": "str",
                "output_path": "str",
                "quotechar": "str",
                "quoting": "str",
            },
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "json_to_csv_formatting_args.json",
            {
                "input_path": "demo/input/table_csv_formatting.json",
                "output_path": "demo/output/table_csv_formatting.csv",
                "quotechar": "'",
                "quoting": "QUOTE_ALL",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("json_to_csv_formatting_rule_test", args_file=args_file, root=sandbox_root)
        csv_text = output_path.read_text(encoding="utf-8")
        self.assertIn("'name','age'", csv_text)
        self.assertIn("'alice,smith','30'", csv_text)

    def test_distilled_json_to_csv_preserves_csv_writer_escape_inputs(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        input_path = sandbox_root / "demo" / "input" / "table_csv_escape.json"
        output_path = sandbox_root / "demo" / "output" / "table_csv_escape.csv"
        input_path.write_text(
            json.dumps([{"name": "alice's", "age": "30"}], ensure_ascii=False),
            encoding="utf-8",
        )
        self.addCleanup(lambda: input_path.unlink(missing_ok=True))
        self.addCleanup(lambda: output_path.unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="json_to_csv_escape_demo",
            session_id="session_json_to_csv_escape",
            task_description="Convert a JSON array file into CSV format.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="read_json",
                    tool_input={"path": "demo/input/table_csv_escape.json"},
                    observation="Read JSON input.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="write_text",
                    tool_input={
                        "path": "demo/output/table_csv_escape.csv",
                        "quotechar": "'",
                        "quoting": "QUOTE_ALL",
                        "escapechar": "\\",
                        "doublequote": False,
                    },
                    observation="Wrote escaped CSV output.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/table_csv_escape.csv"],
            started_at="2026-04-26T17:30:00",
            ended_at="2026-04-26T17:31:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="json_to_csv_escape_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("json_to_csv", generated["metadata"].rule_name)
        self.assertEqual(
            {
                "doublequote": "str",
                "escapechar": "str",
                "input_path": "str",
                "output_path": "str",
                "quotechar": "str",
                "quoting": "str",
            },
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "json_to_csv_escape_args.json",
            {
                "input_path": "demo/input/table_csv_escape.json",
                "output_path": "demo/output/table_csv_escape.csv",
                "quotechar": "'",
                "quoting": "QUOTE_ALL",
                "escapechar": "\\",
                "doublequote": False,
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("json_to_csv_escape_rule_test", args_file=args_file, root=sandbox_root)
        self.assertEqual("'name','age'\n'alice\\'s','30'\n", output_path.read_text(encoding="utf-8"))

    def test_distilled_json_to_csv_preserves_csv_writer_missing_value_inputs(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        input_path = sandbox_root / "demo" / "input" / "table_csv_missing_values.json"
        output_path = sandbox_root / "demo" / "output" / "table_csv_missing_values.csv"
        input_path.write_text(
            json.dumps(
                [
                    {"name": "alice", "age": "30"},
                    {"name": "bob", "extra": "ignore-me"},
                ],
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        self.addCleanup(lambda: input_path.unlink(missing_ok=True))
        self.addCleanup(lambda: output_path.unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="json_to_csv_missing_values_demo",
            session_id="session_json_to_csv_missing_values",
            task_description="Convert a JSON array file into CSV format.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="read_json",
                    tool_input={"path": "demo/input/table_csv_missing_values.json"},
                    observation="Read JSON table input.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="write_text",
                    tool_input={
                        "path": "demo/output/table_csv_missing_values.csv",
                        "restval": "NA",
                        "extrasaction": "ignore",
                    },
                    observation="Wrote CSV output while filling missing values and ignoring extra keys.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/table_csv_missing_values.csv"],
            started_at="2026-04-26T21:30:00",
            ended_at="2026-04-26T21:31:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="json_to_csv_missing_values_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("json_to_csv", generated["metadata"].rule_name)
        self.assertEqual(
            {
                "extrasaction": "str",
                "input_path": "str",
                "output_path": "str",
                "restval": "str",
            },
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "json_to_csv_missing_values_args.json",
            {
                "input_path": "demo/input/table_csv_missing_values.json",
                "output_path": "demo/output/table_csv_missing_values.csv",
                "restval": "NA",
                "extrasaction": "ignore",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("json_to_csv_missing_values_rule_test", args_file=args_file, root=sandbox_root)
        self.assertEqual("name,age\nalice,30\nbob,NA\n", output_path.read_text(encoding="utf-8"))

    def test_distilled_csv_to_json_preserves_write_json_formatting_inputs(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        input_path = sandbox_root / "demo" / "input" / "table_formatting.csv"
        output_path = sandbox_root / "demo" / "output" / "table_formatting.json"
        input_path.write_text("name,city\nalice,中文\n", encoding="utf-8")
        self.addCleanup(lambda: input_path.unlink(missing_ok=True))
        self.addCleanup(lambda: output_path.unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="csv_to_json_formatting_demo",
            session_id="session_csv_to_json_formatting",
            task_description="Convert a CSV file into JSON format.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="read_text",
                    tool_input={"path": "demo/input/table_formatting.csv"},
                    observation="Read CSV input.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="write_json",
                    tool_input={"path": "demo/output/table_formatting.json", "ensure_ascii": False, "indent": 4},
                    observation="Wrote formatted JSON output.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/table_formatting.json"],
            started_at="2026-04-26T16:30:00",
            ended_at="2026-04-26T16:31:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="csv_to_json_formatting_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("csv_to_json", generated["metadata"].rule_name)
        self.assertEqual(
            {"ensure_ascii": "str", "indent": "str", "input_path": "str", "output_path": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "csv_to_json_formatting_args.json",
            {
                "input_path": "demo/input/table_formatting.csv",
                "output_path": "demo/output/table_formatting.json",
                "ensure_ascii": False,
                "indent": 4,
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("csv_to_json_formatting_rule_test", args_file=args_file, root=sandbox_root)
        output_text = output_path.read_text(encoding="utf-8")
        self.assertIn('\n        "city": "中文"', output_text)
        self.assertNotIn("\\u4e2d\\u6587", output_text)

    def test_distilled_csv_to_json_preserves_csv_reader_formatting_inputs(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        input_path = sandbox_root / "demo" / "input" / "table_reader_formatting.csv"
        output_path = sandbox_root / "demo" / "output" / "table_reader_formatting.json"
        input_path.write_text("'name','city'\n'alice\\'s','中文'\n", encoding="utf-8")
        self.addCleanup(lambda: input_path.unlink(missing_ok=True))
        self.addCleanup(lambda: output_path.unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="csv_to_json_reader_formatting_demo",
            session_id="session_csv_to_json_reader_formatting",
            task_description="Convert a CSV file into JSON format.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="read_text",
                    tool_input={
                        "path": "demo/input/table_reader_formatting.csv",
                        "quotechar": "'",
                        "quoting": "QUOTE_ALL",
                        "escapechar": "\\",
                        "doublequote": False,
                    },
                    observation="Read quoted CSV input.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="write_json",
                    tool_input={"path": "demo/output/table_reader_formatting.json", "ensure_ascii": False, "indent": 4},
                    observation="Wrote formatted JSON output.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/table_reader_formatting.json"],
            started_at="2026-04-26T17:50:00",
            ended_at="2026-04-26T17:51:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="csv_to_json_reader_formatting_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("csv_to_json", generated["metadata"].rule_name)
        self.assertEqual(
            {
                "doublequote": "str",
                "ensure_ascii": "str",
                "escapechar": "str",
                "indent": "str",
                "input_path": "str",
                "output_path": "str",
                "quotechar": "str",
                "quoting": "str",
            },
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "csv_to_json_reader_formatting_args.json",
            {
                "input_path": "demo/input/table_reader_formatting.csv",
                "output_path": "demo/output/table_reader_formatting.json",
                "quotechar": "'",
                "quoting": "QUOTE_ALL",
                "escapechar": "\\",
                "doublequote": False,
                "ensure_ascii": False,
                "indent": 4,
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("csv_to_json_reader_formatting_rule_test", args_file=args_file, root=sandbox_root)
        payload = json.loads(output_path.read_text(encoding="utf-8"))
        self.assertEqual("alice's", payload[0]["name"])
        self.assertEqual("中文", payload[0]["city"])

    def test_distilled_csv_to_json_preserves_reader_spacing_and_json_sort_inputs(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        input_path = sandbox_root / "demo" / "input" / "table_reader_spacing.csv"
        output_path = sandbox_root / "demo" / "output" / "table_reader_spacing.json"
        input_path.write_text("name, city\nalice, 中文\n", encoding="utf-8")
        self.addCleanup(lambda: input_path.unlink(missing_ok=True))
        self.addCleanup(lambda: output_path.unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="csv_to_json_reader_spacing_demo",
            session_id="session_csv_to_json_reader_spacing",
            task_description="Convert a CSV file into JSON format.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="read_text",
                    tool_input={
                        "path": "demo/input/table_reader_spacing.csv",
                        "skipinitialspace": True,
                    },
                    observation="Read CSV input with spacing control.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="write_json",
                    tool_input={
                        "path": "demo/output/table_reader_spacing.json",
                        "sort_keys": True,
                    },
                    observation="Wrote sorted JSON output.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/table_reader_spacing.json"],
            started_at="2026-04-26T21:10:00",
            ended_at="2026-04-26T21:11:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="csv_to_json_reader_spacing_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("csv_to_json", generated["metadata"].rule_name)
        self.assertEqual(
            {
                "input_path": "str",
                "output_path": "str",
                "skipinitialspace": "str",
                "sort_keys": "str",
            },
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "csv_to_json_reader_spacing_args.json",
            {
                "input_path": "demo/input/table_reader_spacing.csv",
                "output_path": "demo/output/table_reader_spacing.json",
                "skipinitialspace": True,
                "sort_keys": True,
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("csv_to_json_reader_spacing_rule_test", args_file=args_file, root=sandbox_root)
        output_text = output_path.read_text(encoding="utf-8")
        self.assertIn('"city": "中文"', output_text)
        self.assertLess(output_text.index('"city"'), output_text.index('"name"'))

    def test_distilled_single_json_transform_json_aliases_use_canonical_schema(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        input_path = sandbox_root / "demo" / "input" / "normalize_alias.json"
        output_path = sandbox_root / "demo" / "output" / "normalized_alias.json"
        input_path.write_text(
            json.dumps({"name": "alice", "age": 30}, ensure_ascii=False),
            encoding="utf-8",
        )
        self.addCleanup(lambda: input_path.unlink(missing_ok=True))
        self.addCleanup(lambda: output_path.unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="single_json_transform_alias_demo",
            session_id="session_single_json_transform_alias",
            task_description="Read one JSON file and write it to a new JSON output file.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="read_json",
                    tool_input={"json_file": "demo/input/normalize_alias.json"},
                    observation="Read JSON input.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="write_json",
                    tool_input={"target_json": "demo/output/normalized_alias.json"},
                    observation="Wrote JSON output.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/normalized_alias.json"],
            started_at="2026-04-25T12:20:00",
            ended_at="2026-04-25T12:21:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="single_json_transform_alias_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("single_json_transform", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_path": "str", "output_path": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "single_json_transform_alias_args.json",
            {
                "input_path": "demo/input/normalize_alias.json",
                "output_path": "demo/output/normalized_alias.json",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("single_json_transform_alias_rule_test", args_file=args_file, root=sandbox_root)
        payload = json.loads(output_path.read_text(encoding="utf-8"))
        self.assertEqual("alice", payload["name"])
        self.assertEqual(30, payload["age"])

    def test_distilled_single_json_transform_source_destination_aliases_use_canonical_schema(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        input_path = sandbox_root / "demo" / "input" / "normalize_source_destination.json"
        output_path = sandbox_root / "demo" / "output" / "normalized_source_destination.json"
        input_path.write_text(
            json.dumps({"name": "alice", "age": 30}, ensure_ascii=False),
            encoding="utf-8",
        )
        self.addCleanup(lambda: input_path.unlink(missing_ok=True))
        self.addCleanup(lambda: output_path.unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="single_json_transform_source_destination_alias_demo",
            session_id="session_single_json_transform_source_destination_alias",
            task_description="Read one JSON file and write it to a new JSON output file.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="read_json",
                    tool_input={"source": "demo/input/normalize_source_destination.json"},
                    observation="Read JSON input.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="write_json",
                    tool_input={"destination": "demo/output/normalized_source_destination.json"},
                    observation="Wrote JSON output.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/normalized_source_destination.json"],
            started_at="2026-04-26T13:04:00",
            ended_at="2026-04-26T13:05:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="single_json_transform_source_destination_alias_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("single_json_transform", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_path": "str", "output_path": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "single_json_transform_source_destination_alias_args.json",
            {
                "input_path": "demo/input/normalize_source_destination.json",
                "output_path": "demo/output/normalized_source_destination.json",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("single_json_transform_source_destination_alias_rule_test", args_file=args_file, root=sandbox_root)
        payload = json.loads(output_path.read_text(encoding="utf-8"))
        self.assertEqual("alice", payload["name"])
        self.assertEqual(30, payload["age"])

    def test_distilled_single_json_transform_preserves_write_json_formatting_inputs(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        input_path = sandbox_root / "demo" / "input" / "normalize_formatting.json"
        output_path = sandbox_root / "demo" / "output" / "normalized_formatting.json"
        input_path.write_text(
            json.dumps({"name": "中文", "age": 30}, ensure_ascii=False),
            encoding="utf-8",
        )
        self.addCleanup(lambda: input_path.unlink(missing_ok=True))
        self.addCleanup(lambda: output_path.unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="single_json_transform_formatting_demo",
            session_id="session_single_json_transform_formatting",
            task_description="Read one JSON file and write it to a new JSON output file.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="read_json",
                    tool_input={"path": "demo/input/normalize_formatting.json"},
                    observation="Read JSON input.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="write_json",
                    tool_input={"path": "demo/output/normalized_formatting.json", "ensure_ascii": False, "indent": 4},
                    observation="Wrote formatted JSON output.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/normalized_formatting.json"],
            started_at="2026-04-26T16:20:00",
            ended_at="2026-04-26T16:21:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="single_json_transform_formatting_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("single_json_transform", generated["metadata"].rule_name)
        self.assertEqual(
            {"ensure_ascii": "str", "indent": "str", "input_path": "str", "output_path": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "single_json_transform_formatting_args.json",
            {
                "input_path": "demo/input/normalize_formatting.json",
                "output_path": "demo/output/normalized_formatting.json",
                "ensure_ascii": False,
                "indent": 4,
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("single_json_transform_formatting_rule_test", args_file=args_file, root=sandbox_root)
        output_text = output_path.read_text(encoding="utf-8")
        self.assertIn('\n    "name": "中文"', output_text)
        self.assertNotIn("\\u4e2d\\u6587", output_text)

    def test_distilled_single_json_transform_preserves_write_json_sort_keys_input(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        input_path = sandbox_root / "demo" / "input" / "normalize_sort_keys.json"
        output_path = sandbox_root / "demo" / "output" / "normalized_sort_keys.json"
        input_path.write_text('{"name":"alice","age":30}', encoding="utf-8")
        self.addCleanup(lambda: input_path.unlink(missing_ok=True))
        self.addCleanup(lambda: output_path.unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="single_json_transform_sort_keys_demo",
            session_id="session_single_json_transform_sort_keys",
            task_description="Read one JSON file and write it to a new JSON output file.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="read_json",
                    tool_input={"path": "demo/input/normalize_sort_keys.json"},
                    observation="Read JSON input.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="write_json",
                    tool_input={
                        "path": "demo/output/normalized_sort_keys.json",
                        "sort_keys": True,
                    },
                    observation="Wrote sorted JSON output.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/normalized_sort_keys.json"],
            started_at="2026-04-26T21:20:00",
            ended_at="2026-04-26T21:21:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="single_json_transform_sort_keys_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("single_json_transform", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_path": "str", "output_path": "str", "sort_keys": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "single_json_transform_sort_keys_args.json",
            {
                "input_path": "demo/input/normalize_sort_keys.json",
                "output_path": "demo/output/normalized_sort_keys.json",
                "sort_keys": True,
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("single_json_transform_sort_keys_rule_test", args_file=args_file, root=sandbox_root)
        output_text = output_path.read_text(encoding="utf-8")
        self.assertLess(output_text.index('"age"'), output_text.index('"name"'))

    def test_distilled_text_replace_text_path_aliases_use_canonical_schema(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        output_path = sandbox_root / "demo" / "output" / "replace_text_alias_output.txt"

        trajectory = Trajectory(
            task_id="text_replace_text_alias_demo",
            session_id="session_text_replace_text_alias",
            task_description="Replace one string with another in a text file and write a new output file.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="read_text",
                    tool_input={
                        "source_text_file": "demo/input/a.txt",
                        "search_text": "file",
                        "replacement_text": "document",
                    },
                    observation="Read source text for replacement.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="write_text",
                    tool_input={"destination_text_file": "demo/output/replace_text_alias_output.txt"},
                    observation="Wrote replaced text output.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/replace_text_alias_output.txt"],
            started_at="2026-04-25T12:22:00",
            ended_at="2026-04-25T12:23:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="text_replace_text_alias_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("text_replace", generated["metadata"].rule_name)
        self.assertEqual(
            {
                "input_path": "str",
                "new_text": "str",
                "old_text": "str",
                "output_path": "str",
            },
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "text_replace_text_alias_args.json",
            {
                "input_path": "demo/input/a.txt",
                "output_path": "demo/output/replace_text_alias_output.txt",
                "old_text": "file",
                "new_text": "document",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("text_replace_text_alias_rule_test", args_file=args_file, root=sandbox_root)
        self.assertTrue(output_path.exists())
        self.assertIn("document a", output_path.read_text(encoding="utf-8"))

    def test_distilled_text_replace_find_replacement_aliases_use_canonical_schema(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        output_path = sandbox_root / "demo" / "output" / "replace_find_replacement_output.txt"

        trajectory = Trajectory(
            task_id="text_replace_find_replacement_alias_demo",
            session_id="session_text_replace_find_replacement_alias",
            task_description="Replace one string with another in a text file and write a new output file.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="read_text",
                    tool_input={
                        "source_text_file": "demo/input/a.txt",
                        "find": "file",
                        "replacement": "document",
                    },
                    observation="Read source text for replacement.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="write_text",
                    tool_input={"destination_text_file": "demo/output/replace_find_replacement_output.txt"},
                    observation="Wrote replaced text output.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/replace_find_replacement_output.txt"],
            started_at="2026-04-26T09:00:00",
            ended_at="2026-04-26T09:01:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="text_replace_find_replacement_alias_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("text_replace", generated["metadata"].rule_name)
        self.assertEqual(
            {
                "input_path": "str",
                "new_text": "str",
                "old_text": "str",
                "output_path": "str",
            },
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "text_replace_find_replacement_alias_args.json",
            {
                "input_path": "demo/input/a.txt",
                "output_path": "demo/output/replace_find_replacement_output.txt",
                "old_text": "file",
                "new_text": "document",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli(
            "text_replace_find_replacement_alias_rule_test",
            args_file=args_file,
            root=sandbox_root,
        )
        self.assertTrue(output_path.exists())
        self.assertIn("document a", output_path.read_text(encoding="utf-8"))

    def test_distilled_text_replace_needle_replacement_value_aliases_use_canonical_schema(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        output_path = sandbox_root / "demo" / "output" / "replace_needle_replacement_value_output.txt"

        trajectory = Trajectory(
            task_id="text_replace_needle_replacement_value_alias_demo",
            session_id="session_text_replace_needle_replacement_value_alias",
            task_description="Replace one string with another in a text file and write a new output file.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="read_text",
                    tool_input={
                        "source_text_file": "demo/input/a.txt",
                        "needle": "file",
                        "replacement_value": "document",
                    },
                    observation="Read source text for replacement.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="write_text",
                    tool_input={"destination_text_file": "demo/output/replace_needle_replacement_value_output.txt"},
                    observation="Wrote replaced text output.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/replace_needle_replacement_value_output.txt"],
            started_at="2026-04-26T10:30:00",
            ended_at="2026-04-26T10:31:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="text_replace_needle_replacement_value_alias_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("text_replace", generated["metadata"].rule_name)
        self.assertEqual(
            {
                "input_path": "str",
                "new_text": "str",
                "old_text": "str",
                "output_path": "str",
            },
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "text_replace_needle_replacement_value_alias_args.json",
            {
                "input_path": "demo/input/a.txt",
                "output_path": "demo/output/replace_needle_replacement_value_output.txt",
                "old_text": "file",
                "new_text": "document",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli(
            "text_replace_needle_replacement_value_alias_rule_test",
            args_file=args_file,
            root=sandbox_root,
        )
        self.assertTrue(output_path.exists())
        self.assertIn("document a", output_path.read_text(encoding="utf-8"))

    def test_distilled_text_replace_source_destination_aliases_use_canonical_schema(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        output_path = sandbox_root / "demo" / "output" / "replace_source_destination_output.txt"

        trajectory = Trajectory(
            task_id="text_replace_source_destination_alias_demo",
            session_id="session_text_replace_source_destination_alias",
            task_description="Replace one string with another in a text file and write a new output file.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="read_text",
                    tool_input={"source": "demo/input/a.txt", "old_text": "file", "new_text": "document"},
                    observation="Read source text for replacement.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="write_text",
                    tool_input={"destination": "demo/output/replace_source_destination_output.txt"},
                    observation="Wrote replaced text output.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/replace_source_destination_output.txt"],
            started_at="2026-04-26T13:17:00",
            ended_at="2026-04-26T13:18:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="text_replace_source_destination_alias_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("text_replace", generated["metadata"].rule_name)
        self.assertEqual(
            {
                "input_path": "str",
                "new_text": "str",
                "old_text": "str",
                "output_path": "str",
            },
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "text_replace_source_destination_alias_args.json",
            {
                "input_path": "demo/input/a.txt",
                "output_path": "demo/output/replace_source_destination_output.txt",
                "old_text": "file",
                "new_text": "document",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli(
            "text_replace_source_destination_alias_rule_test",
            args_file=args_file,
            root=sandbox_root,
        )
        self.assertTrue(output_path.exists())
        self.assertIn("document a", output_path.read_text(encoding="utf-8"))

    def test_distilled_single_json_transform_writes_output(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        input_path = sandbox_root / "demo" / "input" / "normalize.json"
        output_path = sandbox_root / "demo" / "output" / "normalized.json"
        input_path.write_text(
            json.dumps({"name": "alice", "age": 30}, ensure_ascii=False),
            encoding="utf-8",
        )
        self.addCleanup(lambda: input_path.unlink(missing_ok=True))
        self.addCleanup(lambda: output_path.unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="single_json_transform_demo",
            session_id="session_single_json_transform",
            task_description="Read one JSON file and write it to a new JSON output file.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="read_json",
                    tool_input={"input_path": "demo/input/normalize.json"},
                    observation="Read JSON input.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="write_json",
                    tool_input={"output_path": "demo/output/normalized.json"},
                    observation="Wrote JSON output.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/output/normalized.json"],
            started_at="2026-04-18T11:29:00",
            ended_at="2026-04-18T11:30:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="single_json_transform_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("single_json_transform", generated["metadata"].rule_name)
        args_file = self._write_args_file(
            "single_json_transform_args.json",
            {
                "input_path": "demo/input/normalize.json",
                "output_path": "demo/output/normalized.json",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("single_json_transform_rule_test", args_file=args_file, root=sandbox_root)
        payload = json.loads(output_path.read_text(encoding="utf-8"))
        self.assertEqual("alice", payload["name"])
        self.assertEqual(30, payload["age"])
