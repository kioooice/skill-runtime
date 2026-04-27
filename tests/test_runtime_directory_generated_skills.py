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

    def test_distilled_batch_rename_suffix_renames_files(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        rename_dir = sandbox_root / "demo" / "rename_suffix_input"
        rename_dir.mkdir(parents=True, exist_ok=True)
        source_a = rename_dir / "one.txt"
        source_b = rename_dir / "two.txt"
        source_a.write_text("one", encoding="utf-8")
        source_b.write_text("two", encoding="utf-8")
        self.addCleanup(lambda: source_a.unlink(missing_ok=True))
        self.addCleanup(lambda: source_b.unlink(missing_ok=True))
        self.addCleanup(lambda: (rename_dir / "one_done.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (rename_dir / "two_done.txt").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="batch_rename_suffix_demo",
            session_id="session_batch_rename_suffix",
            task_description="Rename all txt files in a directory by suffixing them with a value.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/rename_suffix_input", "pattern": "*.txt"},
                    observation="Found files to rename.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="rename_path",
                    tool_input={"source": "demo/rename_suffix_input/one.txt", "target": "demo/rename_suffix_input/one_done.txt"},
                    observation="Renamed matching files with a suffix.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T14:30:00",
            ended_at="2026-04-26T14:31:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="batch_rename_suffix_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("batch_rename_suffix", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_dir": "str", "pattern": "str", "suffix": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "batch_rename_suffix_args.json",
            {
                "input_dir": "demo/rename_suffix_input",
                "pattern": "*.txt",
                "suffix": "_done",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("batch_rename_suffix_rule_test", args_file=args_file, root=sandbox_root)
        self.assertTrue((rename_dir / "one_done.txt").exists())
        self.assertTrue((rename_dir / "two_done.txt").exists())

    def test_distilled_batch_rename_extension_renames_files(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        rename_dir = sandbox_root / "demo" / "rename_extension_input"
        rename_dir.mkdir(parents=True, exist_ok=True)
        source_a = rename_dir / "one.txt"
        source_b = rename_dir / "two.txt"
        source_a.write_text("one", encoding="utf-8")
        source_b.write_text("two", encoding="utf-8")
        self.addCleanup(lambda: source_a.unlink(missing_ok=True))
        self.addCleanup(lambda: source_b.unlink(missing_ok=True))
        self.addCleanup(lambda: (rename_dir / "one.md").unlink(missing_ok=True))
        self.addCleanup(lambda: (rename_dir / "two.md").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="batch_rename_extension_demo",
            session_id="session_batch_rename_extension",
            task_description="Rename all txt files in a directory by changing their extension to md.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/rename_extension_input", "pattern": "*.txt"},
                    observation="Found files to rename.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="rename_path",
                    tool_input={"source": "demo/rename_extension_input/one.txt", "target": "demo/rename_extension_input/one.md"},
                    observation="Renamed matching files by changing their extension.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T15:00:00",
            ended_at="2026-04-26T15:01:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="batch_rename_extension_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("batch_rename_extension", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_dir": "str", "output_extension": "str", "pattern": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "batch_rename_extension_args.json",
            {
                "input_dir": "demo/rename_extension_input",
                "pattern": "*.txt",
                "output_extension": ".md",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("batch_rename_extension_rule_test", args_file=args_file, root=sandbox_root)
        self.assertTrue((rename_dir / "one.md").exists())
        self.assertTrue((rename_dir / "two.md").exists())

    def test_distilled_batch_rename_replace_renames_files(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        rename_dir = sandbox_root / "demo" / "rename_replace_input"
        rename_dir.mkdir(parents=True, exist_ok=True)
        source_a = rename_dir / "draft_one.txt"
        source_b = rename_dir / "draft_two.txt"
        source_a.write_text("one", encoding="utf-8")
        source_b.write_text("two", encoding="utf-8")
        self.addCleanup(lambda: source_a.unlink(missing_ok=True))
        self.addCleanup(lambda: source_b.unlink(missing_ok=True))
        self.addCleanup(lambda: (rename_dir / "final_one.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (rename_dir / "final_two.txt").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="batch_rename_replace_demo",
            session_id="session_batch_rename_replace",
            task_description="Rename all txt files in a directory by replacing draft with final in each filename.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/rename_replace_input", "pattern": "*.txt"},
                    observation="Found files to rename.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="rename_path",
                    tool_input={"source": "demo/rename_replace_input/draft_one.txt", "target": "demo/rename_replace_input/final_one.txt"},
                    observation="Renamed matching files by replacing part of each filename.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T15:20:00",
            ended_at="2026-04-26T15:21:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="batch_rename_replace_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("batch_rename_replace", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_dir": "str", "new_text": "str", "old_text": "str", "pattern": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "batch_rename_replace_args.json",
            {
                "input_dir": "demo/rename_replace_input",
                "pattern": "*.txt",
                "old_text": "draft",
                "new_text": "final",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("batch_rename_replace_rule_test", args_file=args_file, root=sandbox_root)
        self.assertTrue((rename_dir / "final_one.txt").exists())
        self.assertTrue((rename_dir / "final_two.txt").exists())

    def test_distilled_batch_rename_case_renames_files(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        rename_dir = sandbox_root / "demo" / "rename_case_input"
        rename_dir.mkdir(parents=True, exist_ok=True)
        source_a = rename_dir / "DraftOne.TXT"
        source_b = rename_dir / "DraftTwo.TXT"
        source_a.write_text("one", encoding="utf-8")
        source_b.write_text("two", encoding="utf-8")
        self.addCleanup(lambda: source_a.unlink(missing_ok=True))
        self.addCleanup(lambda: source_b.unlink(missing_ok=True))
        self.addCleanup(lambda: (rename_dir / "draftone.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (rename_dir / "drafttwo.txt").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="batch_rename_case_demo",
            session_id="session_batch_rename_case",
            task_description="Rename all files in a directory to lowercase filenames.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/rename_case_input", "pattern": "*.*"},
                    observation="Found files to rename.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="rename_path",
                    tool_input={"source": "demo/rename_case_input/DraftOne.TXT", "target": "demo/rename_case_input/draftone.txt"},
                    observation="Renamed matching files to lowercase.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T16:00:00",
            ended_at="2026-04-26T16:01:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="batch_rename_case_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("batch_rename_case", generated["metadata"].rule_name)
        self.assertEqual(
            {"filename_case": "str", "input_dir": "str", "pattern": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "batch_rename_case_args.json",
            {
                "input_dir": "demo/rename_case_input",
                "pattern": "*.*",
                "filename_case": "lower",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("batch_rename_case_rule_test", args_file=args_file, root=sandbox_root)
        self.assertTrue((rename_dir / "draftone.txt").exists())
        self.assertTrue((rename_dir / "drafttwo.txt").exists())

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

    def test_distilled_batch_rename_input_output_aliases_use_canonical_schema(self) -> None:
        rename_dir = ROOT / "demo" / "rename_input_output_input"
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
            task_id="batch_rename_input_output_alias_demo",
            session_id="session_batch_rename_input_output_alias",
            task_description="Rename all txt files in a directory by prefixing them with a value.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"input_dir": "demo/rename_input_output_input", "pattern": "*.txt"},
                    observation="Found files to rename.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="rename_path",
                    tool_input={"input": "demo/rename_input_output_input/one.txt", "output": "demo/rename_input_output_input/done_one.txt"},
                    observation="Renamed matching files.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T12:45:00",
            ended_at="2026-04-26T12:46:00",
        )

        generated = self._generate_and_activate_skill(trajectory, skill_name="batch_rename_input_output_alias_rule_test")
        self.assertEqual("batch_rename", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_dir": "str", "pattern": "str", "prefix": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "batch_rename_input_output_alias_args.json",
            {
                "input_dir": "demo/rename_input_output_input",
                "pattern": "*.txt",
                "prefix": "done_",
            },
        )
        self._execute_skill_cli("batch_rename_input_output_alias_rule_test", args_file=args_file)
        self.assertTrue((rename_dir / "done_one.txt").exists())
        self.assertTrue((rename_dir / "done_two.txt").exists())

    def test_distilled_batch_rename_source_destination_aliases_use_canonical_schema(self) -> None:
        rename_dir = ROOT / "demo" / "rename_source_destination_input"
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
            task_id="batch_rename_source_destination_alias_demo",
            session_id="session_batch_rename_source_destination_alias",
            task_description="Rename all txt files in a directory by prefixing them with a value.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"input_dir": "demo/rename_source_destination_input", "pattern": "*.txt"},
                    observation="Found files to rename.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="rename_path",
                    tool_input={"source": "demo/rename_source_destination_input/one.txt", "destination": "demo/rename_source_destination_input/done_one.txt"},
                    observation="Renamed matching files.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T12:47:00",
            ended_at="2026-04-26T12:48:00",
        )

        generated = self._generate_and_activate_skill(trajectory, skill_name="batch_rename_source_destination_alias_rule_test")
        self.assertEqual("batch_rename", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_dir": "str", "pattern": "str", "prefix": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "batch_rename_source_destination_alias_args.json",
            {
                "input_dir": "demo/rename_source_destination_input",
                "pattern": "*.txt",
                "prefix": "done_",
            },
        )
        self._execute_skill_cli("batch_rename_source_destination_alias_rule_test", args_file=args_file)
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

    def test_distilled_directory_copy_source_target_aliases_use_canonical_schema(self) -> None:
        source_dir = ROOT / "demo" / "copy_source_target_input"
        output_dir = ROOT / "demo" / "copy_source_target_output"
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
            task_id="directory_copy_source_target_alias_demo",
            session_id="session_directory_copy_source_target_alias",
            task_description="Copy matching txt files from one directory into another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"source": "demo/copy_source_target_input", "pattern": "*.txt"},
                    observation="Found txt files to copy.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="copy_file",
                    tool_input={"source": "demo/copy_source_target_input", "target": "demo/copy_source_target_output"},
                    observation="Copied matching files into output directory.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T12:00:00",
            ended_at="2026-04-26T12:01:00",
        )

        generated = self._generate_and_activate_skill(trajectory, skill_name="directory_copy_source_target_alias_rule_test")
        self.assertEqual("directory_copy", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_dir": "str", "output_dir": "str", "pattern": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "directory_copy_source_target_alias_args.json",
            {
                "input_dir": "demo/copy_source_target_input",
                "output_dir": "demo/copy_source_target_output",
                "pattern": "*.txt",
            },
        )
        self._execute_skill_cli("directory_copy_source_target_alias_rule_test", args_file=args_file)
        self.assertTrue((output_dir / "keep_a.txt").exists())
        self.assertTrue((output_dir / "keep_b.txt").exists())
        self.assertFalse((output_dir / "skip.md").exists())

    def test_distilled_directory_copy_destination_alias_use_canonical_schema(self) -> None:
        source_dir = ROOT / "demo" / "copy_destination_input"
        output_dir = ROOT / "demo" / "copy_destination_output"
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
            task_id="directory_copy_destination_alias_demo",
            session_id="session_directory_copy_destination_alias",
            task_description="Copy matching txt files from one directory into another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"source_dir": "demo/copy_destination_input", "pattern": "*.txt"},
                    observation="Found txt files to copy.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="copy_file",
                    tool_input={"source_dir": "demo/copy_destination_input", "destination": "demo/copy_destination_output"},
                    observation="Copied matching files into output directory.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T12:02:00",
            ended_at="2026-04-26T12:03:00",
        )

        generated = self._generate_and_activate_skill(trajectory, skill_name="directory_copy_destination_alias_rule_test")
        self.assertEqual("directory_copy", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_dir": "str", "output_dir": "str", "pattern": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "directory_copy_destination_alias_args.json",
            {
                "input_dir": "demo/copy_destination_input",
                "output_dir": "demo/copy_destination_output",
                "pattern": "*.txt",
            },
        )
        self._execute_skill_cli("directory_copy_destination_alias_rule_test", args_file=args_file)
        self.assertTrue((output_dir / "keep_a.txt").exists())
        self.assertTrue((output_dir / "keep_b.txt").exists())
        self.assertFalse((output_dir / "skip.md").exists())

    def test_distilled_directory_copy_preserves_output_prefix_input(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        source_dir = sandbox_root / "demo" / "copy_prefix_input"
        output_dir = sandbox_root / "demo" / "copy_prefix_output"
        source_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (source_dir / "a.txt").write_text("alpha", encoding="utf-8")
        (source_dir / "b.txt").write_text("beta", encoding="utf-8")
        self.addCleanup(lambda: (source_dir / "a.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (source_dir / "b.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "done_a.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "done_b.txt").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="directory_copy_prefix_demo",
            session_id="session_directory_copy_prefix",
            task_description="Copy matching txt files from one directory into another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/copy_prefix_input", "pattern": "*.txt"},
                    observation="Found txt files to copy.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="copy_file",
                    tool_input={
                        "source_path": "demo/copy_prefix_input/a.txt",
                        "target_path": "demo/copy_prefix_output/done_a.txt",
                    },
                    observation="Copied one prefixed txt file into the output directory.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-27T00:10:00",
            ended_at="2026-04-27T00:11:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="directory_copy_prefix_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("directory_copy", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_dir": "str", "output_dir": "str", "pattern": "str", "prefix": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "directory_copy_prefix_args.json",
            {
                "input_dir": "demo/copy_prefix_input",
                "output_dir": "demo/copy_prefix_output",
                "pattern": "*.txt",
                "prefix": "done_",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("directory_copy_prefix_rule_test", args_file=args_file, root=sandbox_root)
        self.assertTrue((output_dir / "done_a.txt").exists())
        self.assertTrue((output_dir / "done_b.txt").exists())

    def test_distilled_directory_copy_preserves_nested_relative_structure(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        source_dir = sandbox_root / "demo" / "copy_nested_input"
        nested_dir = source_dir / "nested"
        output_dir = sandbox_root / "demo" / "copy_nested_output"
        nested_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (nested_dir / "a.txt").write_text("alpha", encoding="utf-8")
        self.addCleanup(lambda: (nested_dir / "a.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "nested" / "a.txt").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="directory_copy_nested_demo",
            session_id="session_directory_copy_nested",
            task_description="Copy matching txt files from one directory into another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/copy_nested_input", "pattern": "**/*.txt"},
                    observation="Found nested txt files to copy.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="copy_file",
                    tool_input={
                        "source_path": "demo/copy_nested_input/nested/a.txt",
                        "target_path": "demo/copy_nested_output/nested/a.txt",
                    },
                    observation="Copied one nested txt file into the output directory.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-27T01:00:00",
            ended_at="2026-04-27T01:01:00",
        )

        self._generate_and_activate_skill(
            trajectory,
            skill_name="directory_copy_nested_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        args_file = self._write_args_file(
            "directory_copy_nested_args.json",
            {
                "input_dir": "demo/copy_nested_input",
                "output_dir": "demo/copy_nested_output",
                "pattern": "**/*.txt",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("directory_copy_nested_rule_test", args_file=args_file, root=sandbox_root)
        self.assertTrue((output_dir / "nested" / "a.txt").exists())
        self.assertFalse((output_dir / "a.txt").exists())

    def test_distilled_directory_move_preserves_output_suffix_input(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        source_dir = sandbox_root / "demo" / "move_suffix_input"
        output_dir = sandbox_root / "demo" / "move_suffix_output"
        source_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (source_dir / "a.log").write_text("alpha", encoding="utf-8")
        (source_dir / "b.log").write_text("beta", encoding="utf-8")
        self.addCleanup(lambda: (source_dir / "a.log").unlink(missing_ok=True))
        self.addCleanup(lambda: (source_dir / "b.log").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "a_done.log").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "b_done.log").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="directory_move_suffix_demo",
            session_id="session_directory_move_suffix",
            task_description="Move matching log files from one directory into another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/move_suffix_input", "pattern": "*.log"},
                    observation="Found log files to move.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="move_file",
                    tool_input={
                        "source_path": "demo/move_suffix_input/a.log",
                        "target_path": "demo/move_suffix_output/a_done.log",
                    },
                    observation="Moved one suffixed log file into the output directory.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-27T00:12:00",
            ended_at="2026-04-27T00:13:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="directory_move_suffix_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("directory_move", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_dir": "str", "output_dir": "str", "pattern": "str", "suffix": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "directory_move_suffix_args.json",
            {
                "input_dir": "demo/move_suffix_input",
                "output_dir": "demo/move_suffix_output",
                "pattern": "*.log",
                "suffix": "_done",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("directory_move_suffix_rule_test", args_file=args_file, root=sandbox_root)
        self.assertTrue((output_dir / "a_done.log").exists())
        self.assertTrue((output_dir / "b_done.log").exists())
        self.assertFalse((source_dir / "a.log").exists())
        self.assertFalse((source_dir / "b.log").exists())

    def test_distilled_directory_move_preserves_nested_relative_structure(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        source_dir = sandbox_root / "demo" / "move_nested_input"
        nested_dir = source_dir / "nested"
        output_dir = sandbox_root / "demo" / "move_nested_output"
        nested_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (nested_dir / "a.log").write_text("alpha", encoding="utf-8")
        self.addCleanup(lambda: (nested_dir / "a.log").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "nested" / "a.log").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="directory_move_nested_demo",
            session_id="session_directory_move_nested",
            task_description="Move matching log files from one directory into another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/move_nested_input", "pattern": "**/*.log"},
                    observation="Found nested log files to move.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="move_file",
                    tool_input={
                        "source_path": "demo/move_nested_input/nested/a.log",
                        "target_path": "demo/move_nested_output/nested/a.log",
                    },
                    observation="Moved one nested log file into the output directory.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-27T01:02:00",
            ended_at="2026-04-27T01:03:00",
        )

        self._generate_and_activate_skill(
            trajectory,
            skill_name="directory_move_nested_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        args_file = self._write_args_file(
            "directory_move_nested_args.json",
            {
                "input_dir": "demo/move_nested_input",
                "output_dir": "demo/move_nested_output",
                "pattern": "**/*.log",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("directory_move_nested_rule_test", args_file=args_file, root=sandbox_root)
        self.assertTrue((output_dir / "nested" / "a.log").exists())
        self.assertFalse((source_dir / "nested" / "a.log").exists())
        self.assertFalse((output_dir / "a.log").exists())

    def test_distilled_directory_json_transform_writes_outputs(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        source_dir = sandbox_root / "demo" / "json_transform_input"
        output_dir = sandbox_root / "demo" / "json_transform_output"
        source_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (source_dir / "a.json").write_text(json.dumps({"name": "alice"}, ensure_ascii=False), encoding="utf-8")
        (source_dir / "b.json").write_text(json.dumps({"name": "bob"}, ensure_ascii=False), encoding="utf-8")
        self.addCleanup(lambda: (source_dir / "a.json").unlink(missing_ok=True))
        self.addCleanup(lambda: (source_dir / "b.json").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "a.json").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "b.json").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="directory_json_transform_demo",
            session_id="session_directory_json_transform",
            task_description="Normalize matching JSON files from one directory into another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/json_transform_input", "pattern": "*.json"},
                    observation="Found matching JSON files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_json",
                    tool_input={"path": "demo/json_transform_input/a.json"},
                    observation="Read one JSON file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_json",
                    tool_input={"path": "demo/json_transform_output/a.json"},
                    observation="Wrote one JSON file to the output directory.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T14:00:00",
            ended_at="2026-04-26T14:01:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="directory_json_transform_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("directory_json_transform", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_dir": "str", "output_dir": "str", "pattern": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "directory_json_transform_args.json",
            {
                "input_dir": "demo/json_transform_input",
                "output_dir": "demo/json_transform_output",
                "pattern": "*.json",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("directory_json_transform_rule_test", args_file=args_file, root=sandbox_root)
        self.assertEqual({"name": "alice"}, json.loads((output_dir / "a.json").read_text(encoding="utf-8")))
        self.assertEqual({"name": "bob"}, json.loads((output_dir / "b.json").read_text(encoding="utf-8")))

    def test_distilled_directory_json_transform_preserves_nested_relative_structure(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        source_dir = sandbox_root / "demo" / "json_nested_input"
        nested_dir = source_dir / "nested"
        output_dir = sandbox_root / "demo" / "json_nested_output"
        nested_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (nested_dir / "a.json").write_text(json.dumps({"name": "alice"}, ensure_ascii=False), encoding="utf-8")
        self.addCleanup(lambda: (nested_dir / "a.json").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "nested" / "a.json").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="directory_json_transform_nested_demo",
            session_id="session_directory_json_transform_nested",
            task_description="Normalize matching JSON files from one directory into another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/json_nested_input", "pattern": "**/*.json"},
                    observation="Found nested JSON files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_json",
                    tool_input={"path": "demo/json_nested_input/nested/a.json"},
                    observation="Read one nested JSON file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_json",
                    tool_input={"path": "demo/json_nested_output/nested/a.json"},
                    observation="Wrote one nested JSON file.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-27T01:20:00",
            ended_at="2026-04-27T01:21:00",
        )

        self._generate_and_activate_skill(
            trajectory,
            skill_name="directory_json_transform_nested_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        args_file = self._write_args_file(
            "directory_json_transform_nested_args.json",
            {
                "input_dir": "demo/json_nested_input",
                "output_dir": "demo/json_nested_output",
                "pattern": "**/*.json",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("directory_json_transform_nested_rule_test", args_file=args_file, root=sandbox_root)
        self.assertEqual({"name": "alice"}, json.loads((output_dir / "nested" / "a.json").read_text(encoding="utf-8")))
        self.assertFalse((output_dir / "a.json").exists())

    def test_distilled_directory_json_transform_preserves_write_json_formatting_inputs(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        source_dir = sandbox_root / "demo" / "json_transform_format_input"
        output_dir = sandbox_root / "demo" / "json_transform_format_output"
        source_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (source_dir / "a.json").write_text(json.dumps({"name": "中文"}, ensure_ascii=False), encoding="utf-8")
        (source_dir / "b.json").write_text(json.dumps({"name": "内容"}, ensure_ascii=False), encoding="utf-8")
        self.addCleanup(lambda: (source_dir / "a.json").unlink(missing_ok=True))
        self.addCleanup(lambda: (source_dir / "b.json").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "a.json").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "b.json").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="directory_json_transform_formatting_demo",
            session_id="session_directory_json_transform_formatting",
            task_description="Normalize matching JSON files from one directory into another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/json_transform_format_input", "pattern": "*.json"},
                    observation="Found matching JSON files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_json",
                    tool_input={"path": "demo/json_transform_format_input/a.json"},
                    observation="Read one JSON file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_json",
                    tool_input={"path": "demo/json_transform_format_output/a.json", "ensure_ascii": False, "indent": 4},
                    observation="Wrote formatted JSON output.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T16:22:00",
            ended_at="2026-04-26T16:23:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="directory_json_transform_formatting_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("directory_json_transform", generated["metadata"].rule_name)
        self.assertEqual(
            {"ensure_ascii": "str", "indent": "str", "input_dir": "str", "output_dir": "str", "pattern": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "directory_json_transform_formatting_args.json",
            {
                "input_dir": "demo/json_transform_format_input",
                "output_dir": "demo/json_transform_format_output",
                "pattern": "*.json",
                "ensure_ascii": False,
                "indent": 4,
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("directory_json_transform_formatting_rule_test", args_file=args_file, root=sandbox_root)
        output_text = (output_dir / "a.json").read_text(encoding="utf-8")
        self.assertIn('\n    "name": "中文"', output_text)
        self.assertNotIn("\\u4e2d\\u6587", output_text)

    def test_distilled_directory_json_transform_preserves_write_json_sort_keys_input(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        source_dir = sandbox_root / "demo" / "json_transform_sort_input"
        output_dir = sandbox_root / "demo" / "json_transform_sort_output"
        source_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (source_dir / "a.json").write_text('{"name":"alice","age":30}', encoding="utf-8")
        (source_dir / "b.json").write_text('{"name":"bob","age":31}', encoding="utf-8")
        self.addCleanup(lambda: (source_dir / "a.json").unlink(missing_ok=True))
        self.addCleanup(lambda: (source_dir / "b.json").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "a.json").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "b.json").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="directory_json_transform_sort_keys_demo",
            session_id="session_directory_json_transform_sort_keys",
            task_description="Normalize matching JSON files from one directory into another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/json_transform_sort_input", "pattern": "*.json"},
                    observation="Found matching JSON files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_json",
                    tool_input={"path": "demo/json_transform_sort_input/a.json"},
                    observation="Read one JSON file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_json",
                    tool_input={"path": "demo/json_transform_sort_output/a.json", "sort_keys": True},
                    observation="Wrote sorted JSON output.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T21:22:00",
            ended_at="2026-04-26T21:23:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="directory_json_transform_sort_keys_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("directory_json_transform", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_dir": "str", "output_dir": "str", "pattern": "str", "sort_keys": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "directory_json_transform_sort_keys_args.json",
            {
                "input_dir": "demo/json_transform_sort_input",
                "output_dir": "demo/json_transform_sort_output",
                "pattern": "*.json",
                "sort_keys": True,
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("directory_json_transform_sort_keys_rule_test", args_file=args_file, root=sandbox_root)
        output_text = (output_dir / "a.json").read_text(encoding="utf-8")
        self.assertLess(output_text.index('"age"'), output_text.index('"name"'))

    def test_distilled_directory_json_transform_preserves_output_prefix_input(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        source_dir = sandbox_root / "demo" / "json_transform_prefix_input"
        output_dir = sandbox_root / "demo" / "json_transform_prefix_output"
        source_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (source_dir / "a.json").write_text(json.dumps({"name": "alice"}, ensure_ascii=False), encoding="utf-8")
        (source_dir / "b.json").write_text(json.dumps({"name": "bob"}, ensure_ascii=False), encoding="utf-8")
        self.addCleanup(lambda: (source_dir / "a.json").unlink(missing_ok=True))
        self.addCleanup(lambda: (source_dir / "b.json").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "clean_a.json").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "clean_b.json").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="directory_json_transform_prefix_demo",
            session_id="session_directory_json_transform_prefix",
            task_description="Normalize matching JSON files from one directory into another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/json_transform_prefix_input", "pattern": "*.json"},
                    observation="Found matching JSON files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_json",
                    tool_input={"path": "demo/json_transform_prefix_input/a.json"},
                    observation="Read one JSON file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_json",
                    tool_input={"path": "demo/json_transform_prefix_output/clean_a.json"},
                    observation="Wrote one JSON file to the output directory with a prefix.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T22:30:00",
            ended_at="2026-04-26T22:31:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="directory_json_transform_prefix_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("directory_json_transform", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_dir": "str", "output_dir": "str", "pattern": "str", "prefix": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "directory_json_transform_prefix_args.json",
            {
                "input_dir": "demo/json_transform_prefix_input",
                "output_dir": "demo/json_transform_prefix_output",
                "pattern": "*.json",
                "prefix": "clean_",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("directory_json_transform_prefix_rule_test", args_file=args_file, root=sandbox_root)
        self.assertEqual({"name": "alice"}, json.loads((output_dir / "clean_a.json").read_text(encoding="utf-8")))
        self.assertEqual({"name": "bob"}, json.loads((output_dir / "clean_b.json").read_text(encoding="utf-8")))

    def test_distilled_directory_csv_to_json_writes_outputs(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        source_dir = sandbox_root / "demo" / "csv_directory_input"
        output_dir = sandbox_root / "demo" / "csv_directory_output"
        source_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (source_dir / "a.csv").write_text("name,age\nalice,30\n", encoding="utf-8")
        (source_dir / "b.csv").write_text("name,age\nbob,31\n", encoding="utf-8")
        self.addCleanup(lambda: (source_dir / "a.csv").unlink(missing_ok=True))
        self.addCleanup(lambda: (source_dir / "b.csv").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "a.json").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "b.json").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="directory_csv_to_json_demo",
            session_id="session_directory_csv_to_json",
            task_description="Convert matching CSV files in one directory into JSON files in another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/csv_directory_input", "pattern": "*.csv"},
                    observation="Found matching CSV files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_text",
                    tool_input={"path": "demo/csv_directory_input/a.csv"},
                    observation="Read one CSV file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_json",
                    tool_input={"path": "demo/csv_directory_output/a.json"},
                    observation="Wrote one JSON file to the output directory.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T14:10:00",
            ended_at="2026-04-26T14:11:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="directory_csv_to_json_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("directory_csv_to_json", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_dir": "str", "output_dir": "str", "pattern": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "directory_csv_to_json_args.json",
            {
                "input_dir": "demo/csv_directory_input",
                "output_dir": "demo/csv_directory_output",
                "pattern": "*.csv",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("directory_csv_to_json_rule_test", args_file=args_file, root=sandbox_root)
        self.assertEqual([{"name": "alice", "age": "30"}], json.loads((output_dir / "a.json").read_text(encoding="utf-8")))
        self.assertEqual([{"name": "bob", "age": "31"}], json.loads((output_dir / "b.json").read_text(encoding="utf-8")))

    def test_distilled_directory_csv_to_json_preserves_write_json_formatting_inputs(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        source_dir = sandbox_root / "demo" / "csv_directory_format_input"
        output_dir = sandbox_root / "demo" / "csv_directory_format_output"
        source_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (source_dir / "a.csv").write_text("name,city\nalice,中文\n", encoding="utf-8")
        (source_dir / "b.csv").write_text("name,city\nbob,内容\n", encoding="utf-8")
        self.addCleanup(lambda: (source_dir / "a.csv").unlink(missing_ok=True))
        self.addCleanup(lambda: (source_dir / "b.csv").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "a.json").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "b.json").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="directory_csv_to_json_formatting_demo",
            session_id="session_directory_csv_to_json_formatting",
            task_description="Convert matching CSV files in one directory into JSON files in another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/csv_directory_format_input", "pattern": "*.csv"},
                    observation="Found matching CSV files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_text",
                    tool_input={"path": "demo/csv_directory_format_input/a.csv"},
                    observation="Read one CSV file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_json",
                    tool_input={"path": "demo/csv_directory_format_output/a.json", "ensure_ascii": False, "indent": 4},
                    observation="Wrote formatted JSON output.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T16:32:00",
            ended_at="2026-04-26T16:33:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="directory_csv_to_json_formatting_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("directory_csv_to_json", generated["metadata"].rule_name)
        self.assertEqual(
            {"ensure_ascii": "str", "indent": "str", "input_dir": "str", "output_dir": "str", "pattern": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "directory_csv_to_json_formatting_args.json",
            {
                "input_dir": "demo/csv_directory_format_input",
                "output_dir": "demo/csv_directory_format_output",
                "pattern": "*.csv",
                "ensure_ascii": False,
                "indent": 4,
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("directory_csv_to_json_formatting_rule_test", args_file=args_file, root=sandbox_root)
        output_text = (output_dir / "a.json").read_text(encoding="utf-8")
        self.assertIn('\n        "city": "中文"', output_text)
        self.assertNotIn("\\u4e2d\\u6587", output_text)

    def test_distilled_directory_csv_to_json_preserves_csv_reader_formatting_inputs(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        source_dir = sandbox_root / "demo" / "csv_directory_reader_format_input"
        output_dir = sandbox_root / "demo" / "csv_directory_reader_format_output"
        source_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (source_dir / "a.csv").write_text("'name','city'\n'alice\\'s','中文'\n", encoding="utf-8")
        (source_dir / "b.csv").write_text("'name','city'\n'bob\\'s','内容'\n", encoding="utf-8")
        self.addCleanup(lambda: (source_dir / "a.csv").unlink(missing_ok=True))
        self.addCleanup(lambda: (source_dir / "b.csv").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "a.json").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "b.json").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="directory_csv_to_json_reader_formatting_demo",
            session_id="session_directory_csv_to_json_reader_formatting",
            task_description="Convert matching CSV files in one directory into JSON files in another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/csv_directory_reader_format_input", "pattern": "*.csv"},
                    observation="Found matching CSV files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_text",
                    tool_input={
                        "path": "demo/csv_directory_reader_format_input/a.csv",
                        "quotechar": "'",
                        "quoting": "QUOTE_ALL",
                        "escapechar": "\\",
                        "doublequote": False,
                    },
                    observation="Read quoted CSV file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_json",
                    tool_input={"path": "demo/csv_directory_reader_format_output/a.json", "ensure_ascii": False, "indent": 4},
                    observation="Wrote formatted JSON output.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T17:52:00",
            ended_at="2026-04-26T17:53:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="directory_csv_to_json_reader_formatting_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("directory_csv_to_json", generated["metadata"].rule_name)
        self.assertEqual(
            {
                "doublequote": "str",
                "ensure_ascii": "str",
                "escapechar": "str",
                "indent": "str",
                "input_dir": "str",
                "output_dir": "str",
                "pattern": "str",
                "quotechar": "str",
                "quoting": "str",
            },
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "directory_csv_to_json_reader_formatting_args.json",
            {
                "input_dir": "demo/csv_directory_reader_format_input",
                "output_dir": "demo/csv_directory_reader_format_output",
                "pattern": "*.csv",
                "quotechar": "'",
                "quoting": "QUOTE_ALL",
                "escapechar": "\\",
                "doublequote": False,
                "ensure_ascii": False,
                "indent": 4,
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("directory_csv_to_json_reader_formatting_rule_test", args_file=args_file, root=sandbox_root)
        self.assertEqual([{"name": "alice's", "city": "中文"}], json.loads((output_dir / "a.json").read_text(encoding="utf-8")))
        self.assertEqual([{"name": "bob's", "city": "内容"}], json.loads((output_dir / "b.json").read_text(encoding="utf-8")))

    def test_distilled_directory_csv_to_json_preserves_reader_spacing_and_json_sort_inputs(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        source_dir = sandbox_root / "demo" / "csv_directory_reader_spacing_input"
        output_dir = sandbox_root / "demo" / "csv_directory_reader_spacing_output"
        source_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (source_dir / "a.csv").write_text("name, city\nalice, 中文\n", encoding="utf-8")
        (source_dir / "b.csv").write_text("name, city\nbob, 内容\n", encoding="utf-8")
        self.addCleanup(lambda: (source_dir / "a.csv").unlink(missing_ok=True))
        self.addCleanup(lambda: (source_dir / "b.csv").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "a.json").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "b.json").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="directory_csv_to_json_reader_spacing_demo",
            session_id="session_directory_csv_to_json_reader_spacing",
            task_description="Convert matching CSV files in one directory into JSON files in another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/csv_directory_reader_spacing_input", "pattern": "*.csv"},
                    observation="Found matching CSV files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_text",
                    tool_input={
                        "path": "demo/csv_directory_reader_spacing_input/a.csv",
                        "skipinitialspace": True,
                    },
                    observation="Read CSV file with spacing control.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_json",
                    tool_input={"path": "demo/csv_directory_reader_spacing_output/a.json", "sort_keys": True},
                    observation="Wrote sorted JSON output.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T21:24:00",
            ended_at="2026-04-26T21:25:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="directory_csv_to_json_reader_spacing_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("directory_csv_to_json", generated["metadata"].rule_name)
        self.assertEqual(
            {
                "input_dir": "str",
                "output_dir": "str",
                "pattern": "str",
                "skipinitialspace": "str",
                "sort_keys": "str",
            },
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "directory_csv_to_json_reader_spacing_args.json",
            {
                "input_dir": "demo/csv_directory_reader_spacing_input",
                "output_dir": "demo/csv_directory_reader_spacing_output",
                "pattern": "*.csv",
                "skipinitialspace": True,
                "sort_keys": True,
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("directory_csv_to_json_reader_spacing_rule_test", args_file=args_file, root=sandbox_root)
        output_text = (output_dir / "a.json").read_text(encoding="utf-8")
        self.assertIn('"city": "中文"', output_text)
        self.assertLess(output_text.index('"city"'), output_text.index('"name"'))

    def test_distilled_directory_csv_to_json_preserves_output_prefix_input(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        source_dir = sandbox_root / "demo" / "csv_directory_prefix_input"
        output_dir = sandbox_root / "demo" / "csv_directory_prefix_output"
        source_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (source_dir / "a.csv").write_text("name,age\nalice,30\n", encoding="utf-8")
        (source_dir / "b.csv").write_text("name,age\nbob,31\n", encoding="utf-8")
        self.addCleanup(lambda: (source_dir / "a.csv").unlink(missing_ok=True))
        self.addCleanup(lambda: (source_dir / "b.csv").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "normalized_a.json").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "normalized_b.json").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="directory_csv_to_json_prefix_demo",
            session_id="session_directory_csv_to_json_prefix",
            task_description="Convert matching CSV files in one directory into JSON files in another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/csv_directory_prefix_input", "pattern": "*.csv"},
                    observation="Found matching CSV files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_text",
                    tool_input={"path": "demo/csv_directory_prefix_input/a.csv"},
                    observation="Read one CSV file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_json",
                    tool_input={"path": "demo/csv_directory_prefix_output/normalized_a.json"},
                    observation="Wrote one JSON file into the output directory with a prefix.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T22:32:00",
            ended_at="2026-04-26T22:33:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="directory_csv_to_json_prefix_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("directory_csv_to_json", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_dir": "str", "output_dir": "str", "pattern": "str", "prefix": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "directory_csv_to_json_prefix_args.json",
            {
                "input_dir": "demo/csv_directory_prefix_input",
                "output_dir": "demo/csv_directory_prefix_output",
                "pattern": "*.csv",
                "prefix": "normalized_",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("directory_csv_to_json_prefix_rule_test", args_file=args_file, root=sandbox_root)
        self.assertEqual([{"name": "alice", "age": "30"}], json.loads((output_dir / "normalized_a.json").read_text(encoding="utf-8")))
        self.assertEqual([{"name": "bob", "age": "31"}], json.loads((output_dir / "normalized_b.json").read_text(encoding="utf-8")))

    def test_distilled_directory_csv_to_json_preserves_nested_relative_structure(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        source_dir = sandbox_root / "demo" / "csv_nested_input"
        nested_dir = source_dir / "nested"
        output_dir = sandbox_root / "demo" / "csv_nested_output"
        nested_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (nested_dir / "a.csv").write_text("name,age\nalice,30\n", encoding="utf-8")
        self.addCleanup(lambda: (nested_dir / "a.csv").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "nested" / "a.json").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="directory_csv_to_json_nested_demo",
            session_id="session_directory_csv_to_json_nested",
            task_description="Convert matching CSV files in one directory into JSON files in another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/csv_nested_input", "pattern": "**/*.csv"},
                    observation="Found nested CSV files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_text",
                    tool_input={"path": "demo/csv_nested_input/nested/a.csv"},
                    observation="Read one nested CSV file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_json",
                    tool_input={"path": "demo/csv_nested_output/nested/a.json"},
                    observation="Wrote one nested JSON file.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-27T01:04:00",
            ended_at="2026-04-27T01:05:00",
        )

        self._generate_and_activate_skill(
            trajectory,
            skill_name="directory_csv_to_json_nested_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        args_file = self._write_args_file(
            "directory_csv_to_json_nested_args.json",
            {
                "input_dir": "demo/csv_nested_input",
                "output_dir": "demo/csv_nested_output",
                "pattern": "**/*.csv",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("directory_csv_to_json_nested_rule_test", args_file=args_file, root=sandbox_root)
        self.assertEqual([{"name": "alice", "age": "30"}], json.loads((output_dir / "nested" / "a.json").read_text(encoding="utf-8")))
        self.assertFalse((output_dir / "a.json").exists())

    def test_distilled_directory_json_to_csv_writes_outputs(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        source_dir = sandbox_root / "demo" / "json_directory_input"
        output_dir = sandbox_root / "demo" / "json_directory_output"
        source_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (source_dir / "a.json").write_text(json.dumps([{"name": "alice", "age": 30}], ensure_ascii=False), encoding="utf-8")
        (source_dir / "b.json").write_text(json.dumps([{"name": "bob", "age": 31}], ensure_ascii=False), encoding="utf-8")
        self.addCleanup(lambda: (source_dir / "a.json").unlink(missing_ok=True))
        self.addCleanup(lambda: (source_dir / "b.json").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "a.csv").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "b.csv").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="directory_json_to_csv_demo",
            session_id="session_directory_json_to_csv",
            task_description="Convert matching JSON files in one directory into CSV files in another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/json_directory_input", "pattern": "*.json"},
                    observation="Found matching JSON files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_json",
                    tool_input={"path": "demo/json_directory_input/a.json"},
                    observation="Read one JSON file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_text",
                    tool_input={"path": "demo/json_directory_output/a.csv"},
                    observation="Wrote one CSV file to the output directory.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T14:12:00",
            ended_at="2026-04-26T14:13:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="directory_json_to_csv_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("directory_json_to_csv", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_dir": "str", "output_dir": "str", "pattern": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "directory_json_to_csv_args.json",
            {
                "input_dir": "demo/json_directory_input",
                "output_dir": "demo/json_directory_output",
                "pattern": "*.json",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("directory_json_to_csv_rule_test", args_file=args_file, root=sandbox_root)
        self.assertEqual("name,age\nalice,30\n", (output_dir / "a.csv").read_text(encoding="utf-8"))
        self.assertEqual("name,age\nbob,31\n", (output_dir / "b.csv").read_text(encoding="utf-8"))

    def test_distilled_directory_json_to_csv_preserves_nested_relative_structure(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        source_dir = sandbox_root / "demo" / "json_csv_nested_input"
        nested_dir = source_dir / "nested"
        output_dir = sandbox_root / "demo" / "json_csv_nested_output"
        nested_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (nested_dir / "a.json").write_text(json.dumps([{"name": "alice", "age": 30}], ensure_ascii=False), encoding="utf-8")
        self.addCleanup(lambda: (nested_dir / "a.json").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "nested" / "a.csv").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="directory_json_to_csv_nested_demo",
            session_id="session_directory_json_to_csv_nested",
            task_description="Convert matching JSON files in one directory into CSV files in another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/json_csv_nested_input", "pattern": "**/*.json"},
                    observation="Found nested JSON files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_json",
                    tool_input={"path": "demo/json_csv_nested_input/nested/a.json"},
                    observation="Read one nested JSON file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_text",
                    tool_input={"path": "demo/json_csv_nested_output/nested/a.csv"},
                    observation="Wrote one nested CSV file.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-27T01:22:00",
            ended_at="2026-04-27T01:23:00",
        )

        self._generate_and_activate_skill(
            trajectory,
            skill_name="directory_json_to_csv_nested_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        args_file = self._write_args_file(
            "directory_json_to_csv_nested_args.json",
            {
                "input_dir": "demo/json_csv_nested_input",
                "output_dir": "demo/json_csv_nested_output",
                "pattern": "**/*.json",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("directory_json_to_csv_nested_rule_test", args_file=args_file, root=sandbox_root)
        self.assertEqual("name,age\nalice,30\n", (output_dir / "nested" / "a.csv").read_text(encoding="utf-8"))
        self.assertFalse((output_dir / "a.csv").exists())

    def test_distilled_directory_json_to_csv_preserves_csv_writer_formatting_inputs(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        source_dir = sandbox_root / "demo" / "json_directory_csv_format_input"
        output_dir = sandbox_root / "demo" / "json_directory_csv_format_output"
        source_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (source_dir / "a.json").write_text(json.dumps([{"name": "alice,smith", "age": 30}]), encoding="utf-8")
        (source_dir / "b.json").write_text(json.dumps([{"name": "bob,jones", "age": 31}]), encoding="utf-8")
        self.addCleanup(lambda: (source_dir / "a.json").unlink(missing_ok=True))
        self.addCleanup(lambda: (source_dir / "b.json").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "a.csv").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "b.csv").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="directory_json_to_csv_formatting_demo",
            session_id="session_directory_json_to_csv_formatting",
            task_description="Convert matching JSON files in one directory into CSV files in another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/json_directory_csv_format_input", "pattern": "*.json"},
                    observation="Found matching JSON files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_json",
                    tool_input={"path": "demo/json_directory_csv_format_input/a.json"},
                    observation="Read one JSON file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_text",
                    tool_input={
                        "path": "demo/json_directory_csv_format_output/a.csv",
                        "quotechar": "'",
                        "quoting": "QUOTE_ALL",
                    },
                    observation="Wrote quoted CSV output.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T17:22:00",
            ended_at="2026-04-26T17:23:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="directory_json_to_csv_formatting_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("directory_json_to_csv", generated["metadata"].rule_name)
        self.assertEqual(
            {
                "input_dir": "str",
                "output_dir": "str",
                "pattern": "str",
                "quotechar": "str",
                "quoting": "str",
            },
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "directory_json_to_csv_formatting_args.json",
            {
                "input_dir": "demo/json_directory_csv_format_input",
                "output_dir": "demo/json_directory_csv_format_output",
                "pattern": "*.json",
                "quotechar": "'",
                "quoting": "QUOTE_ALL",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("directory_json_to_csv_formatting_rule_test", args_file=args_file, root=sandbox_root)
        self.assertEqual("'name','age'\n'alice,smith','30'\n", (output_dir / "a.csv").read_text(encoding="utf-8"))
        self.assertEqual("'name','age'\n'bob,jones','31'\n", (output_dir / "b.csv").read_text(encoding="utf-8"))

    def test_distilled_directory_json_to_csv_preserves_csv_writer_escape_inputs(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        source_dir = sandbox_root / "demo" / "json_directory_csv_escape_input"
        output_dir = sandbox_root / "demo" / "json_directory_csv_escape_output"
        source_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (source_dir / "a.json").write_text(json.dumps([{"name": "alice's", "age": 30}]), encoding="utf-8")
        (source_dir / "b.json").write_text(json.dumps([{"name": "bob's", "age": 31}]), encoding="utf-8")
        self.addCleanup(lambda: (source_dir / "a.json").unlink(missing_ok=True))
        self.addCleanup(lambda: (source_dir / "b.json").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "a.csv").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "b.csv").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="directory_json_to_csv_escape_demo",
            session_id="session_directory_json_to_csv_escape",
            task_description="Convert matching JSON files in one directory into CSV files in another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/json_directory_csv_escape_input", "pattern": "*.json"},
                    observation="Found matching JSON files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_json",
                    tool_input={"path": "demo/json_directory_csv_escape_input/a.json"},
                    observation="Read one JSON file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_text",
                    tool_input={
                        "path": "demo/json_directory_csv_escape_output/a.csv",
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
            artifacts=[],
            started_at="2026-04-26T17:32:00",
            ended_at="2026-04-26T17:33:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="directory_json_to_csv_escape_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("directory_json_to_csv", generated["metadata"].rule_name)
        self.assertEqual(
            {
                "doublequote": "str",
                "escapechar": "str",
                "input_dir": "str",
                "output_dir": "str",
                "pattern": "str",
                "quotechar": "str",
                "quoting": "str",
            },
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "directory_json_to_csv_escape_args.json",
            {
                "input_dir": "demo/json_directory_csv_escape_input",
                "output_dir": "demo/json_directory_csv_escape_output",
                "pattern": "*.json",
                "quotechar": "'",
                "quoting": "QUOTE_ALL",
                "escapechar": "\\",
                "doublequote": False,
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("directory_json_to_csv_escape_rule_test", args_file=args_file, root=sandbox_root)
        self.assertEqual("'name','age'\n'alice\\'s','30'\n", (output_dir / "a.csv").read_text(encoding="utf-8"))
        self.assertEqual("'name','age'\n'bob\\'s','31'\n", (output_dir / "b.csv").read_text(encoding="utf-8"))

    def test_distilled_directory_json_to_csv_preserves_csv_writer_missing_value_inputs(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        source_dir = sandbox_root / "demo" / "json_directory_csv_missing_input"
        output_dir = sandbox_root / "demo" / "json_directory_csv_missing_output"
        source_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (source_dir / "a.json").write_text(
            json.dumps([{"name": "alice", "age": "30"}, {"name": "bob", "extra": "ignore-me"}]),
            encoding="utf-8",
        )
        (source_dir / "b.json").write_text(
            json.dumps([{"name": "carol", "age": "32"}, {"name": "dave", "extra": "ignore-me"}]),
            encoding="utf-8",
        )
        self.addCleanup(lambda: (source_dir / "a.json").unlink(missing_ok=True))
        self.addCleanup(lambda: (source_dir / "b.json").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "a.csv").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "b.csv").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="directory_json_to_csv_missing_values_demo",
            session_id="session_directory_json_to_csv_missing_values",
            task_description="Convert matching JSON files in one directory into CSV files in another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/json_directory_csv_missing_input", "pattern": "*.json"},
                    observation="Found matching JSON files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_json",
                    tool_input={"path": "demo/json_directory_csv_missing_input/a.json"},
                    observation="Read one JSON file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_text",
                    tool_input={
                        "path": "demo/json_directory_csv_missing_output/a.csv",
                        "restval": "NA",
                        "extrasaction": "ignore",
                    },
                    observation="Wrote CSV output while filling missing values and ignoring extra keys.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T21:32:00",
            ended_at="2026-04-26T21:33:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="directory_json_to_csv_missing_values_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("directory_json_to_csv", generated["metadata"].rule_name)
        self.assertEqual(
            {
                "extrasaction": "str",
                "input_dir": "str",
                "output_dir": "str",
                "pattern": "str",
                "restval": "str",
            },
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "directory_json_to_csv_missing_values_args.json",
            {
                "input_dir": "demo/json_directory_csv_missing_input",
                "output_dir": "demo/json_directory_csv_missing_output",
                "pattern": "*.json",
                "restval": "NA",
                "extrasaction": "ignore",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("directory_json_to_csv_missing_values_rule_test", args_file=args_file, root=sandbox_root)
        self.assertEqual("name,age\nalice,30\nbob,NA\n", (output_dir / "a.csv").read_text(encoding="utf-8"))
        self.assertEqual("name,age\ncarol,32\ndave,NA\n", (output_dir / "b.csv").read_text(encoding="utf-8"))

    def test_distilled_directory_json_to_csv_preserves_output_suffix_input(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        source_dir = sandbox_root / "demo" / "json_directory_csv_suffix_input"
        output_dir = sandbox_root / "demo" / "json_directory_csv_suffix_output"
        source_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (source_dir / "a.json").write_text(json.dumps([{"name": "alice", "age": 30}]), encoding="utf-8")
        (source_dir / "b.json").write_text(json.dumps([{"name": "bob", "age": 31}]), encoding="utf-8")
        self.addCleanup(lambda: (source_dir / "a.json").unlink(missing_ok=True))
        self.addCleanup(lambda: (source_dir / "b.json").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "a_export.csv").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "b_export.csv").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="directory_json_to_csv_suffix_demo",
            session_id="session_directory_json_to_csv_suffix",
            task_description="Convert matching JSON files in one directory into CSV files in another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/json_directory_csv_suffix_input", "pattern": "*.json"},
                    observation="Found matching JSON files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_json",
                    tool_input={"path": "demo/json_directory_csv_suffix_input/a.json"},
                    observation="Read one JSON file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_text",
                    tool_input={"path": "demo/json_directory_csv_suffix_output/a_export.csv"},
                    observation="Wrote one CSV file into the output directory with a suffix.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T22:34:00",
            ended_at="2026-04-26T22:35:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="directory_json_to_csv_suffix_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("directory_json_to_csv", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_dir": "str", "output_dir": "str", "pattern": "str", "suffix": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "directory_json_to_csv_suffix_args.json",
            {
                "input_dir": "demo/json_directory_csv_suffix_input",
                "output_dir": "demo/json_directory_csv_suffix_output",
                "pattern": "*.json",
                "suffix": "_export",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("directory_json_to_csv_suffix_rule_test", args_file=args_file, root=sandbox_root)
        self.assertEqual("name,age\nalice,30\n", (output_dir / "a_export.csv").read_text(encoding="utf-8"))
        self.assertEqual("name,age\nbob,31\n", (output_dir / "b_export.csv").read_text(encoding="utf-8"))

    def test_distilled_directory_text_transform_writes_outputs(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        source_dir = sandbox_root / "demo" / "text_transform_input"
        output_dir = sandbox_root / "demo" / "text_transform_output"
        source_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (source_dir / "a.txt").write_text("alpha", encoding="utf-8")
        (source_dir / "b.txt").write_text("beta\n", encoding="utf-8")
        self.addCleanup(lambda: (source_dir / "a.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (source_dir / "b.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "a.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "b.txt").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="directory_text_transform_demo",
            session_id="session_directory_text_transform",
            task_description="Normalize matching text files from one directory into another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/text_transform_input", "pattern": "*.txt"},
                    observation="Found matching text files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_text",
                    tool_input={"path": "demo/text_transform_input/a.txt"},
                    observation="Read one text file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_text",
                    tool_input={"path": "demo/text_transform_output/a.txt"},
                    observation="Wrote one normalized text file to the output directory.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T14:20:00",
            ended_at="2026-04-26T14:21:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="directory_text_transform_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("directory_text_transform", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_dir": "str", "output_dir": "str", "pattern": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "directory_text_transform_args.json",
            {
                "input_dir": "demo/text_transform_input",
                "output_dir": "demo/text_transform_output",
                "pattern": "*.txt",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("directory_text_transform_rule_test", args_file=args_file, root=sandbox_root)
        self.assertEqual("alpha\n", (output_dir / "a.txt").read_text(encoding="utf-8"))
        self.assertEqual("beta\n", (output_dir / "b.txt").read_text(encoding="utf-8"))

    def test_distilled_directory_text_transform_preserves_write_text_newline_input(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        source_dir = sandbox_root / "demo" / "text_transform_crlf_input"
        output_dir = sandbox_root / "demo" / "text_transform_crlf_output"
        source_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (source_dir / "a.txt").write_text("alpha", encoding="utf-8")
        (source_dir / "b.txt").write_text("beta\n", encoding="utf-8")
        self.addCleanup(lambda: (source_dir / "a.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (source_dir / "b.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "a.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "b.txt").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="directory_text_transform_newline_demo",
            session_id="session_directory_text_transform_newline",
            task_description="Normalize matching text files from one directory into another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/text_transform_crlf_input", "pattern": "*.txt"},
                    observation="Found matching text files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_text",
                    tool_input={"path": "demo/text_transform_crlf_input/a.txt"},
                    observation="Read one text file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_text",
                    tool_input={"path": "demo/text_transform_crlf_output/a.txt", "newline": "\n"},
                    observation="Wrote one normalized text file with LF endings.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T22:16:00",
            ended_at="2026-04-26T22:17:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="directory_text_transform_newline_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("directory_text_transform", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_dir": "str", "newline": "str", "output_dir": "str", "pattern": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "directory_text_transform_newline_args.json",
            {
                "input_dir": "demo/text_transform_crlf_input",
                "output_dir": "demo/text_transform_crlf_output",
                "pattern": "*.txt",
                "newline": "\n",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("directory_text_transform_newline_rule_test", args_file=args_file, root=sandbox_root)
        output_bytes = (output_dir / "a.txt").read_bytes()
        self.assertIn(b"\n", output_bytes)
        self.assertNotIn(b"\r\n", output_bytes)

    def test_distilled_directory_text_transform_preserves_output_suffix_input(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        source_dir = sandbox_root / "demo" / "text_transform_suffix_input"
        output_dir = sandbox_root / "demo" / "text_transform_suffix_output"
        source_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (source_dir / "a.txt").write_text("alpha", encoding="utf-8")
        (source_dir / "b.txt").write_text("beta\n", encoding="utf-8")
        self.addCleanup(lambda: (source_dir / "a.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (source_dir / "b.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "a_done.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "b_done.txt").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="directory_text_transform_suffix_demo",
            session_id="session_directory_text_transform_suffix",
            task_description="Normalize matching text files from one directory into another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/text_transform_suffix_input", "pattern": "*.txt"},
                    observation="Found matching text files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_text",
                    tool_input={"path": "demo/text_transform_suffix_input/a.txt"},
                    observation="Read one text file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_text",
                    tool_input={"path": "demo/text_transform_suffix_output/a_done.txt"},
                    observation="Wrote one normalized text file into the output directory with a suffix.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T22:36:00",
            ended_at="2026-04-26T22:37:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="directory_text_transform_suffix_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("directory_text_transform", generated["metadata"].rule_name)
        self.assertEqual(
            {"input_dir": "str", "output_dir": "str", "pattern": "str", "suffix": "str"},
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "directory_text_transform_suffix_args.json",
            {
                "input_dir": "demo/text_transform_suffix_input",
                "output_dir": "demo/text_transform_suffix_output",
                "pattern": "*.txt",
                "suffix": "_done",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("directory_text_transform_suffix_rule_test", args_file=args_file, root=sandbox_root)
        self.assertEqual("alpha\n", (output_dir / "a_done.txt").read_text(encoding="utf-8"))
        self.assertEqual("beta\n", (output_dir / "b_done.txt").read_text(encoding="utf-8"))

    def test_distilled_directory_text_transform_preserves_nested_relative_structure(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        source_dir = sandbox_root / "demo" / "text_nested_input"
        nested_dir = source_dir / "nested"
        output_dir = sandbox_root / "demo" / "text_nested_output"
        nested_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (nested_dir / "a.txt").write_text("alpha", encoding="utf-8")
        self.addCleanup(lambda: (nested_dir / "a.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "nested" / "a.txt").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="directory_text_transform_nested_demo",
            session_id="session_directory_text_transform_nested",
            task_description="Normalize matching text files from one directory into another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/text_nested_input", "pattern": "**/*.txt"},
                    observation="Found nested text files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_text",
                    tool_input={"path": "demo/text_nested_input/nested/a.txt"},
                    observation="Read one nested text file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_text",
                    tool_input={"path": "demo/text_nested_output/nested/a.txt"},
                    observation="Wrote one nested normalized text file.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-27T01:06:00",
            ended_at="2026-04-27T01:07:00",
        )

        self._generate_and_activate_skill(
            trajectory,
            skill_name="directory_text_transform_nested_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        args_file = self._write_args_file(
            "directory_text_transform_nested_args.json",
            {
                "input_dir": "demo/text_nested_input",
                "output_dir": "demo/text_nested_output",
                "pattern": "**/*.txt",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("directory_text_transform_nested_rule_test", args_file=args_file, root=sandbox_root)
        self.assertEqual("alpha\n", (output_dir / "nested" / "a.txt").read_text(encoding="utf-8"))
        self.assertFalse((output_dir / "a.txt").exists())

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

    def test_distilled_directory_text_replace_preserves_nested_relative_structure(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        source_dir = sandbox_root / "demo" / "replace_nested_input"
        nested_dir = source_dir / "nested"
        output_dir = sandbox_root / "demo" / "replace_nested_output"
        nested_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (nested_dir / "a.txt").write_text("hello file a", encoding="utf-8")
        self.addCleanup(lambda: (nested_dir / "a.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "nested" / "a.txt").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="directory_text_replace_nested_demo",
            session_id="session_directory_text_replace_nested",
            task_description="Replace one string with another across all txt files in a directory and write outputs to another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/replace_nested_input", "pattern": "**/*.txt"},
                    observation="Found nested txt files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_text",
                    tool_input={"path": "demo/replace_nested_input/nested/a.txt", "old_text": "file", "new_text": "document"},
                    observation="Read one nested text file for replacement.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_text",
                    tool_input={"path": "demo/replace_nested_output/nested/a.txt"},
                    observation="Wrote one nested replaced text file.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-27T01:24:00",
            ended_at="2026-04-27T01:25:00",
        )

        self._generate_and_activate_skill(
            trajectory,
            skill_name="directory_text_replace_nested_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        args_file = self._write_args_file(
            "directory_text_replace_nested_args.json",
            {
                "input_dir": "demo/replace_nested_input",
                "output_dir": "demo/replace_nested_output",
                "pattern": "**/*.txt",
                "old_text": "file",
                "new_text": "document",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("directory_text_replace_nested_rule_test", args_file=args_file, root=sandbox_root)
        self.assertEqual("hello document a", (output_dir / "nested" / "a.txt").read_text(encoding="utf-8"))
        self.assertFalse((output_dir / "a.txt").exists())

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

    def test_distilled_directory_text_replace_preserves_write_text_newline_input(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        source_dir = sandbox_root / "demo" / "replace_crlf_input"
        output_dir = sandbox_root / "demo" / "replace_crlf_output"
        source_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (source_dir / "a.txt").write_text("hello alpha\n", encoding="utf-8")
        (source_dir / "b.txt").write_text("hello beta\n", encoding="utf-8")
        self.addCleanup(lambda: (source_dir / "a.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (source_dir / "b.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "a.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "b.txt").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="directory_text_replace_newline_demo",
            session_id="session_directory_text_replace_newline",
            task_description="Replace one string with another across all txt files in a directory and write outputs to another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/replace_crlf_input", "pattern": "*.txt"},
                    observation="Found matching txt files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_text",
                    tool_input={"path": "demo/replace_crlf_input/a.txt", "old_text": "hello", "new_text": "hi"},
                    observation="Read one text file for replacement.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_text",
                    tool_input={"path": "demo/replace_crlf_output/a.txt", "newline": "\n"},
                    observation="Wrote one replaced text file with LF endings.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T22:18:00",
            ended_at="2026-04-26T22:19:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="directory_text_replace_newline_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("directory_text_replace", generated["metadata"].rule_name)
        self.assertEqual(
            {
                "input_dir": "str",
                "new_text": "str",
                "newline": "str",
                "old_text": "str",
                "output_dir": "str",
                "pattern": "str",
            },
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "directory_text_replace_newline_args.json",
            {
                "input_dir": "demo/replace_crlf_input",
                "output_dir": "demo/replace_crlf_output",
                "pattern": "*.txt",
                "old_text": "hello",
                "new_text": "hi",
                "newline": "\n",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("directory_text_replace_newline_rule_test", args_file=args_file, root=sandbox_root)
        output_bytes = (output_dir / "a.txt").read_bytes()
        self.assertIn(b"\n", output_bytes)
        self.assertNotIn(b"\r\n", output_bytes)

    def test_distilled_directory_text_replace_preserves_output_prefix_input(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        source_dir = sandbox_root / "demo" / "replace_prefix_input"
        output_dir = sandbox_root / "demo" / "replace_prefix_output"
        source_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (source_dir / "a.txt").write_text("hello alpha", encoding="utf-8")
        (source_dir / "b.txt").write_text("hello beta", encoding="utf-8")
        self.addCleanup(lambda: (source_dir / "a.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (source_dir / "b.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "done_a.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "done_b.txt").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="directory_text_replace_prefix_demo",
            session_id="session_directory_text_replace_prefix",
            task_description="Replace one string with another across all txt files in a directory and write outputs to another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/replace_prefix_input", "pattern": "*.txt"},
                    observation="Found matching txt files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_text",
                    tool_input={"path": "demo/replace_prefix_input/a.txt", "old_text": "hello", "new_text": "hi"},
                    observation="Read one text file for replacement.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_text",
                    tool_input={"path": "demo/replace_prefix_output/done_a.txt"},
                    observation="Wrote one prefixed replaced text file.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T23:00:00",
            ended_at="2026-04-26T23:01:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="directory_text_replace_prefix_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("directory_text_replace", generated["metadata"].rule_name)
        self.assertEqual(
            {
                "input_dir": "str",
                "new_text": "str",
                "old_text": "str",
                "output_dir": "str",
                "pattern": "str",
                "prefix": "str",
            },
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "directory_text_replace_prefix_args.json",
            {
                "input_dir": "demo/replace_prefix_input",
                "output_dir": "demo/replace_prefix_output",
                "pattern": "*.txt",
                "old_text": "hello",
                "new_text": "hi",
                "prefix": "done_",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("directory_text_replace_prefix_rule_test", args_file=args_file, root=sandbox_root)
        self.assertEqual("hi alpha", (output_dir / "done_a.txt").read_text(encoding="utf-8"))
        self.assertEqual("hi beta", (output_dir / "done_b.txt").read_text(encoding="utf-8"))

    def test_distilled_directory_text_replace_preserves_output_suffix_input(self) -> None:
        sandbox_root, _, sandbox_index = self._make_runtime_sandbox()
        source_dir = sandbox_root / "demo" / "replace_suffix_input"
        output_dir = sandbox_root / "demo" / "replace_suffix_output"
        source_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (source_dir / "a.txt").write_text("hello alpha", encoding="utf-8")
        (source_dir / "b.txt").write_text("hello beta", encoding="utf-8")
        self.addCleanup(lambda: (source_dir / "a.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (source_dir / "b.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "a_done.txt").unlink(missing_ok=True))
        self.addCleanup(lambda: (output_dir / "b_done.txt").unlink(missing_ok=True))

        trajectory = Trajectory(
            task_id="directory_text_replace_suffix_demo",
            session_id="session_directory_text_replace_suffix",
            task_description="Replace one string with another across all txt files in a directory and write outputs to another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/replace_suffix_input", "pattern": "*.txt"},
                    observation="Found matching txt files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_text",
                    tool_input={"path": "demo/replace_suffix_input/a.txt", "old_text": "hello", "new_text": "hi"},
                    observation="Read one text file for replacement.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_text",
                    tool_input={"path": "demo/replace_suffix_output/a_done.txt"},
                    observation="Wrote one suffixed replaced text file.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T23:02:00",
            ended_at="2026-04-26T23:03:00",
        )

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="directory_text_replace_suffix_rule_test",
            root=sandbox_root,
            index=sandbox_index,
        )
        self.assertEqual("directory_text_replace", generated["metadata"].rule_name)
        self.assertEqual(
            {
                "input_dir": "str",
                "new_text": "str",
                "old_text": "str",
                "output_dir": "str",
                "pattern": "str",
                "suffix": "str",
            },
            generated["metadata"].input_schema,
        )
        args_file = self._write_args_file(
            "directory_text_replace_suffix_args.json",
            {
                "input_dir": "demo/replace_suffix_input",
                "output_dir": "demo/replace_suffix_output",
                "pattern": "*.txt",
                "old_text": "hello",
                "new_text": "hi",
                "suffix": "_done",
            },
            root=sandbox_root,
        )
        self._execute_skill_cli("directory_text_replace_suffix_rule_test", args_file=args_file, root=sandbox_root)
        self.assertEqual("hi alpha", (output_dir / "a_done.txt").read_text(encoding="utf-8"))
        self.assertEqual("hi beta", (output_dir / "b_done.txt").read_text(encoding="utf-8"))

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
