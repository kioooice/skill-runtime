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
