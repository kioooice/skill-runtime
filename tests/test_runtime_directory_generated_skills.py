import json

from skill_runtime.api.models import Trajectory, TrajectoryStep
from tests.runtime_test_support import ROOT


class RuntimeDirectoryGeneratedSkillTestsMixin:
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

        self._generate_and_activate_skill(trajectory, skill_name="batch_rename_rule_test")
        args_file = self._write_args_file(
            "batch_rename_args.json",
            {
                "input_dir": "demo/rename_input",
                "pattern": "*.txt",
                "prefix": "renamed_",
            },
        )
        self._execute_skill_cli("batch_rename_rule_test", args_file=args_file)
        self.assertTrue((rename_dir / "renamed_one.txt").exists())
        self.assertTrue((rename_dir / "renamed_two.txt").exists())

    def test_distilled_batch_rename_glob_alias_uses_canonical_schema(self) -> None:
        rename_dir = ROOT / "demo" / "rename_glob_input"
        rename_dir.mkdir(parents=True, exist_ok=True)
        source_a = rename_dir / "one.txt"
        source_b = rename_dir / "two.txt"
        source_a.write_text("one", encoding="utf-8")
        source_b.write_text("two", encoding="utf-8")
        self.addCleanup(lambda: source_a.unlink(missing_ok=True))
        self.addCleanup(lambda: source_b.unlink(missing_ok=True))
        self.addCleanup(lambda: (rename_dir / "done_one.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (rename_dir / "done_two.txt").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="batch_rename_glob_alias_demo",
            session_id="session_batch_rename_glob_alias",
            task_description="Rename all txt files in a directory by prefixing them with a value.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"input_dir": "demo/rename_glob_input", "glob": "*.txt", "prefix": "done_"},
                    observation="Found files to rename.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="rename_path",
                    tool_input={"from_path": "demo/rename_glob_input/one.txt", "to_path": "demo/rename_glob_input/done_one.txt"},
                    observation="Renamed matching files.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-25T12:30:00",
            ended_at="2026-04-25T12:31:00",
        )

        generated = self._generate_and_activate_skill(trajectory, skill_name="batch_rename_glob_alias_rule_test")
        self.assertEqual("batch_rename", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_dir": "str", "pattern": "str", "prefix": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "batch_rename_glob_alias_args.json",
            {
                "input_dir": "demo/rename_glob_input",
                "pattern": "*.txt",
                "prefix": "done_",
            },
        )
        self._execute_skill_cli("batch_rename_glob_alias_rule_test", args_file=args_file)
        self.assertTrue((rename_dir / "done_one.txt").exists())
        self.assertTrue((rename_dir / "done_two.txt").exists())

    def test_distilled_batch_rename_name_prefix_alias_uses_canonical_schema(self) -> None:
        rename_dir = ROOT / "demo" / "rename_prefix_input"
        rename_dir.mkdir(parents=True, exist_ok=True)
        source_a = rename_dir / "one.txt"
        source_b = rename_dir / "two.txt"
        source_a.write_text("one", encoding="utf-8")
        source_b.write_text("two", encoding="utf-8")
        self.addCleanup(lambda: source_a.unlink(missing_ok=True))
        self.addCleanup(lambda: source_b.unlink(missing_ok=True))
        self.addCleanup(lambda: (rename_dir / "done_one.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (rename_dir / "done_two.txt").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="batch_rename_name_prefix_alias_demo",
            session_id="session_batch_rename_name_prefix_alias",
            task_description="Rename all txt files in a directory by prefixing them with a value.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"input_dir": "demo/rename_prefix_input", "pattern": "*.txt", "prefix_value": "done_"},
                    observation="Found files to rename.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="rename_path",
                    tool_input={"from_path": "demo/rename_prefix_input/one.txt", "to_path": "demo/rename_prefix_input/done_one.txt"},
                    observation="Renamed matching files.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T09:02:00",
            ended_at="2026-04-26T09:03:00",
        )

        generated = self._generate_and_activate_skill(trajectory, skill_name="batch_rename_name_prefix_alias_rule_test")
        self.assertEqual("batch_rename", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_dir": "str", "pattern": "str", "prefix": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "batch_rename_name_prefix_alias_args.json",
            {
                "input_dir": "demo/rename_prefix_input",
                "pattern": "*.txt",
                "prefix": "done_",
            },
        )
        self._execute_skill_cli("batch_rename_name_prefix_alias_rule_test", args_file=args_file)
        self.assertTrue((rename_dir / "done_one.txt").exists())
        self.assertTrue((rename_dir / "done_two.txt").exists())

    def test_distilled_batch_rename_from_to_aliases_use_canonical_schema(self) -> None:
        rename_dir = ROOT / "demo" / "rename_from_to_input"
        rename_dir.mkdir(parents=True, exist_ok=True)
        source_a = rename_dir / "one.txt"
        source_b = rename_dir / "two.txt"
        source_a.write_text("one", encoding="utf-8")
        source_b.write_text("two", encoding="utf-8")
        self.addCleanup(lambda: source_a.unlink(missing_ok=True))
        self.addCleanup(lambda: source_b.unlink(missing_ok=True))
        self.addCleanup(lambda: (rename_dir / "done_one.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (rename_dir / "done_two.txt").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="batch_rename_from_to_alias_demo",
            session_id="session_batch_rename_from_to_alias",
            task_description="Rename all txt files in a directory by prefixing them with a value.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"input_dir": "demo/rename_from_to_input", "pattern": "*.txt"},
                    observation="Found files to rename.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="rename_path",
                    tool_input={"from": "demo/rename_from_to_input/one.txt", "to": "demo/rename_from_to_input/done_one.txt"},
                    observation="Renamed matching files.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T11:20:00",
            ended_at="2026-04-26T11:21:00",
        )

        generated = self._generate_and_activate_skill(trajectory, skill_name="batch_rename_from_to_alias_rule_test")
        self.assertEqual("batch_rename", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_dir": "str", "pattern": "str", "prefix": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "batch_rename_from_to_alias_args.json",
            {
                "input_dir": "demo/rename_from_to_input",
                "pattern": "*.txt",
                "prefix": "done_",
            },
        )
        self._execute_skill_cli("batch_rename_from_to_alias_rule_test", args_file=args_file)
        self.assertTrue((rename_dir / "done_one.txt").exists())
        self.assertTrue((rename_dir / "done_two.txt").exists())

    def test_distilled_batch_rename_rename_prefix_alias_uses_canonical_schema(self) -> None:
        rename_dir = ROOT / "demo" / "rename_prefix_alias_input"
        rename_dir.mkdir(parents=True, exist_ok=True)
        source_a = rename_dir / "one.txt"
        source_b = rename_dir / "two.txt"
        source_a.write_text("one", encoding="utf-8")
        source_b.write_text("two", encoding="utf-8")
        self.addCleanup(lambda: source_a.unlink(missing_ok=True))
        self.addCleanup(lambda: source_b.unlink(missing_ok=True))
        self.addCleanup(lambda: (rename_dir / "done_one.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (rename_dir / "done_two.txt").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="batch_rename_rename_prefix_alias_demo",
            session_id="session_batch_rename_rename_prefix_alias",
            task_description="Rename all txt files in a directory by prefixing them with a value.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"input_dir": "demo/rename_prefix_alias_input", "pattern": "*.txt", "rename_prefix": "done_"},
                    observation="Found files to rename.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="rename_path",
                    tool_input={"from_path": "demo/rename_prefix_alias_input/one.txt", "to_path": "demo/rename_prefix_alias_input/done_one.txt"},
                    observation="Renamed matching files.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T10:32:00",
            ended_at="2026-04-26T10:33:00",
        )

        generated = self._generate_and_activate_skill(trajectory, skill_name="batch_rename_rename_prefix_alias_rule_test")
        self.assertEqual("batch_rename", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_dir": "str", "pattern": "str", "prefix": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "batch_rename_rename_prefix_alias_args.json",
            {
                "input_dir": "demo/rename_prefix_alias_input",
                "pattern": "*.txt",
                "prefix": "done_",
            },
        )
        self._execute_skill_cli("batch_rename_rename_prefix_alias_rule_test", args_file=args_file)
        self.assertTrue((rename_dir / "done_one.txt").exists())
        self.assertTrue((rename_dir / "done_two.txt").exists())

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

        self._generate_and_activate_skill(trajectory, skill_name="directory_copy_rule_test")
        args_file = self._write_args_file(
            "directory_copy_args.json",
            {
                "input_dir": "demo/copy_input",
                "output_dir": "demo/copy_output",
                "pattern": "*.txt",
            },
        )
        self._execute_skill_cli("directory_copy_rule_test", args_file=args_file)
        self.assertTrue((output_dir / "keep_a.txt").exists())
        self.assertTrue((output_dir / "keep_b.txt").exists())
        self.assertFalse((output_dir / "skip.md").exists())

    def test_distilled_directory_copy_input_output_aliases_use_canonical_schema(self) -> None:
        source_dir = ROOT / "demo" / "copy_input_output_input"
        output_dir = ROOT / "demo" / "copy_input_output_output"
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
            task_id="directory_copy_input_output_alias_demo",
            session_id="session_directory_copy_input_output_alias",
            task_description="Copy matching txt files from one directory into another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/copy_input_output_input", "pattern": "*.txt"},
                    observation="Found txt files to copy.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="copy_file",
                    tool_input={"input": "demo/copy_input_output_input", "output": "demo/copy_input_output_output"},
                    observation="Copied matching files into output directory.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T11:45:00",
            ended_at="2026-04-26T11:46:00",
        )

        generated = self._generate_and_activate_skill(trajectory, skill_name="directory_copy_input_output_alias_rule_test")
        self.assertEqual("directory_copy", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_dir": "str", "output_dir": "str", "pattern": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "directory_copy_input_output_alias_args.json",
            {
                "input_dir": "demo/copy_input_output_input",
                "output_dir": "demo/copy_input_output_output",
                "pattern": "*.txt",
            },
        )
        self._execute_skill_cli("directory_copy_input_output_alias_rule_test", args_file=args_file)
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

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="directory_text_replace_rule_test",
        )
        self.assertEqual("directory_text_replace", generated["metadata"].rule_name)
        self.assertIn("multiple files", generated["metadata"].rule_reason)
        args_file = self._write_args_file(
            "directory_text_replace_args.json",
            {
                "input_dir": "demo/replace_dir_input",
                "output_dir": "demo/replace_dir_output",
                "pattern": "*.txt",
                "old_text": "file",
                "new_text": "document",
            },
        )
        self._execute_skill_cli("directory_text_replace_rule_test", args_file=args_file)
        self.assertEqual("hello document a", (output_dir / "a.txt").read_text(encoding="utf-8"))
        self.assertEqual("hello document b", (output_dir / "b.txt").read_text(encoding="utf-8"))
        self.assertFalse((output_dir / "skip.md").exists())

    def test_distilled_directory_text_replace_search_replace_aliases_use_canonical_schema(self) -> None:
        source_dir = ROOT / "demo" / "replace_dir_alias_input"
        output_dir = ROOT / "demo" / "replace_dir_alias_output"
        source_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (source_dir / "a.txt").write_text("hello file a", encoding="utf-8")
        (source_dir / "b.txt").write_text("hello file b", encoding="utf-8")
        self.addCleanup(lambda: (source_dir / "a.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (source_dir / "b.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "a.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "b.txt").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="directory_text_replace_alias_demo",
            session_id="session_directory_text_replace_alias",
            task_description="Replace one string with another across all txt files in a directory and write outputs to another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={
                        "source_dir": "demo/replace_dir_alias_input",
                        "target_dir": "demo/replace_dir_alias_output",
                        "pattern": "*.txt",
                        "search": "file",
                        "replace": "document",
                    },
                    observation="Found txt files to rewrite.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_text",
                    tool_input={"source_dir": "demo/replace_dir_alias_input"},
                    observation="Read each source file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_text",
                    tool_input={"target_dir": "demo/replace_dir_alias_output"},
                    observation="Wrote replaced outputs.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/replace_dir_alias_output/a.txt"],
            started_at="2026-04-25T12:02:00",
            ended_at="2026-04-25T12:03:00",
        )

        generated = self._generate_and_activate_skill(trajectory, skill_name="directory_text_replace_alias_rule_test")
        self.assertEqual("directory_text_replace", generated["metadata"].rule_name)
        self.assertEqual(
            {
                "input_dir": "str",
                "new_text": "str",
                "old_text": "str",
                "output_dir": "str",
                "pattern": "str",
            },
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "directory_text_replace_alias_args.json",
            {
                "input_dir": "demo/replace_dir_alias_input",
                "output_dir": "demo/replace_dir_alias_output",
                "pattern": "*.txt",
                "old_text": "file",
                "new_text": "document",
            },
        )
        self._execute_skill_cli("directory_text_replace_alias_rule_test", args_file=args_file)
        self.assertEqual("hello document a", (output_dir / "a.txt").read_text(encoding="utf-8"))
        self.assertEqual("hello document b", (output_dir / "b.txt").read_text(encoding="utf-8"))

    def test_distilled_directory_text_replace_filter_aliases_use_canonical_schema(self) -> None:
        source_dir = ROOT / "demo" / "replace_dir_filter_input"
        output_dir = ROOT / "demo" / "replace_dir_filter_output"
        source_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (source_dir / "a.txt").write_text("hello file a", encoding="utf-8")
        (source_dir / "b.txt").write_text("hello file b", encoding="utf-8")
        self.addCleanup(lambda: (source_dir / "a.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (source_dir / "b.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "a.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "b.txt").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="directory_text_replace_filter_alias_demo",
            session_id="session_directory_text_replace_filter_alias",
            task_description="Replace one string with another across all txt files in a directory and write outputs to another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={
                        "source_dir": "demo/replace_dir_filter_input",
                        "target_dir": "demo/replace_dir_filter_output",
                        "filter": "*.txt",
                        "search": "file",
                        "replace": "document",
                    },
                    observation="Found txt files to rewrite.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_text",
                    tool_input={"source_dir": "demo/replace_dir_filter_input"},
                    observation="Read each source file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_text",
                    tool_input={"target_dir": "demo/replace_dir_filter_output"},
                    observation="Wrote replaced outputs.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/replace_dir_filter_output/a.txt"],
            started_at="2026-04-25T12:42:00",
            ended_at="2026-04-25T12:43:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="directory_text_replace_filter_alias_rule_test",
        )
        self.assertEqual("directory_text_replace", generated["metadata"].rule_name)
        self.assertEqual(
            {
                "input_dir": "str",
                "new_text": "str",
                "old_text": "str",
                "output_dir": "str",
                "pattern": "str",
            },
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "directory_text_replace_filter_alias_args.json",
            {
                "input_dir": "demo/replace_dir_filter_input",
                "output_dir": "demo/replace_dir_filter_output",
                "pattern": "*.txt",
                "old_text": "file",
                "new_text": "document",
            },
        )
        self._execute_skill_cli("directory_text_replace_filter_alias_rule_test", args_file=args_file)
        self.assertEqual("hello document a", (output_dir / "a.txt").read_text(encoding="utf-8"))
        self.assertEqual("hello document b", (output_dir / "b.txt").read_text(encoding="utf-8"))

    def test_distilled_directory_text_replace_directory_aliases_use_canonical_schema(self) -> None:
        source_dir = ROOT / "demo" / "replace_dir_directory_alias_input"
        output_dir = ROOT / "demo" / "replace_dir_directory_alias_output"
        source_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (source_dir / "a.txt").write_text("hello file a", encoding="utf-8")
        (source_dir / "b.txt").write_text("hello file b", encoding="utf-8")
        self.addCleanup(lambda: (source_dir / "a.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (source_dir / "b.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "a.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "b.txt").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="directory_text_replace_directory_alias_demo",
            session_id="session_directory_text_replace_directory_alias",
            task_description="Replace one string with another across all txt files in a directory and write outputs to another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={
                        "input_directory": "demo/replace_dir_directory_alias_input",
                        "output_directory": "demo/replace_dir_directory_alias_output",
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
                    tool_input={"input_directory": "demo/replace_dir_directory_alias_input"},
                    observation="Read each source file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_text",
                    tool_input={"output_directory": "demo/replace_dir_directory_alias_output"},
                    observation="Wrote replaced outputs.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=["demo/replace_dir_directory_alias_output/a.txt"],
            started_at="2026-04-26T11:00:00",
            ended_at="2026-04-26T11:01:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="directory_text_replace_directory_alias_rule_test",
        )
        self.assertEqual("directory_text_replace", generated["metadata"].rule_name)
        self.assertEqual(
            {
                "input_dir": "str",
                "new_text": "str",
                "old_text": "str",
                "output_dir": "str",
                "pattern": "str",
            },
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "directory_text_replace_directory_alias_args.json",
            {
                "input_dir": "demo/replace_dir_directory_alias_input",
                "output_dir": "demo/replace_dir_directory_alias_output",
                "pattern": "*.txt",
                "old_text": "file",
                "new_text": "document",
            },
        )
        self._execute_skill_cli("directory_text_replace_directory_alias_rule_test", args_file=args_file)
        self.assertEqual("hello document a", (output_dir / "a.txt").read_text(encoding="utf-8"))
        self.assertEqual("hello document b", (output_dir / "b.txt").read_text(encoding="utf-8"))

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

        generated = self._generate_and_activate_skill(trajectory, skill_name="directory_move_rule_test")
        self.assertEqual("directory_move", generated["metadata"].rule_name)
        args_file = self._write_args_file(
            "directory_move_args.json",
            {
                "input_dir": "demo/move_input",
                "output_dir": "demo/move_output",
                "pattern": "*.txt",
            },
        )
        self._execute_skill_cli("directory_move_rule_test", args_file=args_file)
        self.assertTrue((output_dir / "move_a.txt").exists())
        self.assertTrue((output_dir / "move_b.txt").exists())
        self.assertFalse((source_dir / "move_a.txt").exists())
        self.assertFalse((source_dir / "move_b.txt").exists())
        self.assertTrue((source_dir / "stay.md").exists())

    def test_distilled_directory_move_glob_alias_uses_canonical_schema(self) -> None:
        source_dir = ROOT / "demo" / "move_glob_input"
        output_dir = ROOT / "demo" / "move_glob_output"
        source_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (source_dir / "keep.log").write_text("alpha", encoding="utf-8")
        (source_dir / "skip.md").write_text("stay", encoding="utf-8")
        self.addCleanup(lambda: (source_dir / "keep.log").unlink(missing_ok=True))
        self.addCleanup(lambda: (source_dir / "skip.md").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "keep.log").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "skip.md").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="directory_move_glob_alias_demo",
            session_id="session_directory_move_glob_alias",
            task_description="Move matching log files from one directory into another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"source_dir": "demo/move_glob_input", "target_dir": "demo/move_glob_output", "glob": "*.log"},
                    observation="Found log files to move.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="move_file",
                    tool_input={"source_dir": "demo/move_glob_input", "target_dir": "demo/move_glob_output"},
                    observation="Moved matching files into output directory.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-25T12:32:00",
            ended_at="2026-04-25T12:33:00",
        )

        generated = self._generate_and_activate_skill(trajectory, skill_name="directory_move_glob_alias_rule_test")
        self.assertEqual("directory_move", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_dir": "str", "output_dir": "str", "pattern": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "directory_move_glob_alias_args.json",
            {
                "input_dir": "demo/move_glob_input",
                "output_dir": "demo/move_glob_output",
                "pattern": "*.log",
            },
        )
        self._execute_skill_cli("directory_move_glob_alias_rule_test", args_file=args_file)
        self.assertTrue((output_dir / "keep.log").exists())
        self.assertFalse((source_dir / "keep.log").exists())
        self.assertTrue((source_dir / "skip.md").exists())

    def test_distilled_directory_move_from_to_dir_aliases_use_canonical_schema(self) -> None:
        source_dir = ROOT / "demo" / "move_from_to_input"
        output_dir = ROOT / "demo" / "move_from_to_output"
        source_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (source_dir / "keep.log").write_text("alpha", encoding="utf-8")
        (source_dir / "skip.md").write_text("stay", encoding="utf-8")
        self.addCleanup(lambda: (source_dir / "keep.log").unlink(missing_ok=True))
        self.addCleanup(lambda: (source_dir / "skip.md").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "keep.log").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "skip.md").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="directory_move_from_to_dir_alias_demo",
            session_id="session_directory_move_from_to_dir_alias",
            task_description="Move matching log files from one directory into another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"from_dir": "demo/move_from_to_input", "pattern": "*.log"},
                    observation="Found log files to move.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="move_file",
                    tool_input={"from_dir": "demo/move_from_to_input", "to_dir": "demo/move_from_to_output"},
                    observation="Moved matching files into output directory.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-25T12:52:00",
            ended_at="2026-04-25T12:53:00",
        )

        generated = self._generate_and_activate_skill(trajectory, skill_name="directory_move_from_to_dir_alias_rule_test")
        self.assertEqual("directory_move", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_dir": "str", "output_dir": "str", "pattern": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "directory_move_from_to_dir_alias_args.json",
            {
                "input_dir": "demo/move_from_to_input",
                "output_dir": "demo/move_from_to_output",
                "pattern": "*.log",
            },
        )
        self._execute_skill_cli("directory_move_from_to_dir_alias_rule_test", args_file=args_file)
        self.assertTrue((output_dir / "keep.log").exists())
        self.assertFalse((source_dir / "keep.log").exists())
        self.assertTrue((source_dir / "skip.md").exists())

    def test_distilled_directory_move_input_output_aliases_use_canonical_schema(self) -> None:
        source_dir = ROOT / "demo" / "move_input_output_input"
        output_dir = ROOT / "demo" / "move_input_output_output"
        source_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (source_dir / "keep.log").write_text("alpha", encoding="utf-8")
        (source_dir / "skip.md").write_text("stay", encoding="utf-8")
        self.addCleanup(lambda: (source_dir / "keep.log").unlink(missing_ok=True))
        self.addCleanup(lambda: (source_dir / "skip.md").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "keep.log").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "skip.md").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="directory_move_input_output_alias_demo",
            session_id="session_directory_move_input_output_alias",
            task_description="Move matching log files from one directory into another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/move_input_output_input", "pattern": "*.log"},
                    observation="Found log files to move.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="move_file",
                    tool_input={"input": "demo/move_input_output_input", "output": "demo/move_input_output_output"},
                    observation="Moved matching files into output directory.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T11:32:00",
            ended_at="2026-04-26T11:33:00",
        )

        generated = self._generate_and_activate_skill(trajectory, skill_name="directory_move_input_output_alias_rule_test")
        self.assertEqual("directory_move", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_dir": "str", "output_dir": "str", "pattern": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "directory_move_input_output_alias_args.json",
            {
                "input_dir": "demo/move_input_output_input",
                "output_dir": "demo/move_input_output_output",
                "pattern": "*.log",
            },
        )
        self._execute_skill_cli("directory_move_input_output_alias_rule_test", args_file=args_file)
        self.assertTrue((output_dir / "keep.log").exists())
        self.assertFalse((source_dir / "keep.log").exists())
        self.assertTrue((source_dir / "skip.md").exists())

    def test_distilled_directory_move_directory_aliases_use_canonical_schema(self) -> None:
        source_dir = ROOT / "demo" / "move_directory_alias_input"
        output_dir = ROOT / "demo" / "move_directory_alias_output"
        source_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (source_dir / "keep.log").write_text("alpha", encoding="utf-8")
        (source_dir / "skip.md").write_text("stay", encoding="utf-8")
        self.addCleanup(lambda: (source_dir / "keep.log").unlink(missing_ok=True))
        self.addCleanup(lambda: (source_dir / "skip.md").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "keep.log").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "skip.md").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="directory_move_directory_alias_demo",
            session_id="session_directory_move_directory_alias",
            task_description="Move matching log files from one directory into another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"source_directory": "demo/move_directory_alias_input", "target_directory": "demo/move_directory_alias_output", "pattern": "*.log"},
                    observation="Found log files to move.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="move_file",
                    tool_input={"source_directory": "demo/move_directory_alias_input", "target_directory": "demo/move_directory_alias_output"},
                    observation="Moved matching files into output directory.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T11:02:00",
            ended_at="2026-04-26T11:03:00",
        )

        generated = self._generate_and_activate_skill(trajectory, skill_name="directory_move_directory_alias_rule_test")
        self.assertEqual("directory_move", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_dir": "str", "output_dir": "str", "pattern": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "directory_move_directory_alias_args.json",
            {
                "input_dir": "demo/move_directory_alias_input",
                "output_dir": "demo/move_directory_alias_output",
                "pattern": "*.log",
            },
        )
        self._execute_skill_cli("directory_move_directory_alias_rule_test", args_file=args_file)
        self.assertTrue((output_dir / "keep.log").exists())
        self.assertFalse((source_dir / "keep.log").exists())
        self.assertTrue((source_dir / "skip.md").exists())

    def test_distilled_directory_move_from_rename_path_uses_rename_tool(self) -> None:
        source_dir = ROOT / "demo" / "rename_move_input"
        output_dir = ROOT / "demo" / "rename_move_output"
        source_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (source_dir / "keep.log").write_text("alpha", encoding="utf-8")
        (source_dir / "skip.md").write_text("skip", encoding="utf-8")
        self.addCleanup(lambda: (source_dir / "keep.log").unlink(missing_ok=True))
        self.addCleanup(lambda: (source_dir / "skip.md").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "keep.log").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "skip.md").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="directory_move_rename_demo",
            session_id="session_directory_move_rename",
            task_description="Move matching log files from one directory into another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={
                        "input_dir": "demo/rename_move_input",
                        "output_dir": "demo/rename_move_output",
                        "pattern": "*.log",
                    },
                    observation="Found log files to move.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="rename_path",
                    tool_input={
                        "source_path": "demo/rename_move_input/keep.log",
                        "target_path": "demo/rename_move_output/keep.log",
                    },
                    observation="Moved matching files into output directory.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-25T10:04:00",
            ended_at="2026-04-25T10:05:00",
        )

        generated = self._generate_and_activate_skill(trajectory, skill_name="directory_move_rename_rule_test")
        self.assertEqual("directory_move", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_dir": "str", "output_dir": "str", "pattern": "str"},
            generated["metadata"].input_schema,
        )
        self.assertIn("tools.rename_path", generated["skill_file"].read_text(encoding="utf-8"))
        args_file = self._write_args_file(
            "directory_move_rename_args.json",
            {
                "input_dir": "demo/rename_move_input",
                "output_dir": "demo/rename_move_output",
                "pattern": "*.log",
            },
        )
        self._execute_skill_cli("directory_move_rename_rule_test", args_file=args_file)
        self.assertTrue((output_dir / "keep.log").exists())
        self.assertFalse((source_dir / "keep.log").exists())
        self.assertTrue((source_dir / "skip.md").exists())
