from tests.runtime_test_support import ROOT


class RuntimeLifecycleTestsMixin:
    def test_service_distill_and_promote_from_observed_single_file_transform_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_single_file_transform_service.json",
            {
                "task": "Normalize one text file into a cleaned output file.",
                "actions": [
                    {
                        "tool": "read_text",
                        "input": {"path": "demo/input/a.txt"},
                        "result": "Read text from demo/input/a.txt.",
                    },
                    {
                        "tool": "write_text",
                        "input": {"path": "demo/output/single_transform.txt"},
                        "result": "Wrote text to demo/output/single_transform.txt.",
                    },
                ],
                "outputs": ["demo/output/single_transform.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_single_file_transform_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("single_file_transform", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self.assertEqual("execute_skill", result["recommended_next_action"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_path", "output_path"),
        )

    def test_service_distill_and_promote_from_observed_csv_to_json_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_csv_to_json_service.json",
            {
                "task": "Convert one CSV file into a JSON output file.",
                "actions": [
                    {
                        "tool": "read_text",
                        "input": {"path": "demo/input/data.csv"},
                        "result": "Read text from demo/input/data.csv.",
                    },
                    {
                        "tool": "write_json",
                        "input": {"path": "demo/output/data.json"},
                        "result": "Wrote JSON to demo/output/data.json.",
                    },
                ],
                "outputs": ["demo/output/data.json"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_csv_to_json_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("csv_to_json", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self.assertEqual("execute_skill", result["recommended_next_action"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_path", "output_path"),
        )

    def test_service_distill_and_promote_from_observed_csv_to_json_input_output_aliases_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_csv_to_json_input_output_aliases.json",
            {
                "task": "Convert one CSV file into a JSON output file.",
                "actions": [
                    {
                        "tool": "read_text",
                        "input": {"input": "demo/input/data.csv"},
                        "result": "Read text from demo/input/data.csv.",
                    },
                    {
                        "tool": "write_json",
                        "input": {"output": "demo/output/data_alias.json"},
                        "result": "Wrote JSON to demo/output/data_alias.json.",
                    },
                ],
                "outputs": ["demo/output/data_alias.json"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_csv_to_json_input_output_aliases_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("csv_to_json", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_path", "output_path"),
        )

    def test_service_distill_and_promote_from_observed_csv_to_json_sep_alias_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_csv_to_json_sep_alias.json",
            {
                "task": "Convert one CSV file into a JSON output file.",
                "actions": [
                    {
                        "tool": "read_text",
                        "input": {"input": "demo/input/data_pipe.csv", "sep": "|"},
                        "result": "Read text from demo/input/data_pipe.csv.",
                    },
                    {
                        "tool": "write_json",
                        "input": {"output": "demo/output/data_pipe.json"},
                        "result": "Wrote JSON to demo/output/data_pipe.json.",
                    },
                ],
                "outputs": ["demo/output/data_pipe.json"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_csv_to_json_sep_alias_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("csv_to_json", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("delimiter", "input_path", "output_path"),
        )

    def test_service_distill_and_promote_from_observed_csv_to_json_csv_aliases_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_csv_to_json_csv_aliases.json",
            {
                "task": "Convert one CSV file into a JSON output file.",
                "actions": [
                    {
                        "tool": "read_text",
                        "input": {"csv_file": "demo/input/data.csv"},
                        "result": "Read text from demo/input/data.csv.",
                    },
                    {
                        "tool": "write_json",
                        "input": {"target_json": "demo/output/data_from_csv_alias.json"},
                        "result": "Wrote JSON to demo/output/data_from_csv_alias.json.",
                    },
                ],
                "outputs": ["demo/output/data_from_csv_alias.json"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_csv_to_json_csv_aliases_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("csv_to_json", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_path", "output_path"),
        )

    def test_service_distill_and_promote_from_observed_json_to_csv_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_json_to_csv_service.json",
            {
                "task": "Convert one JSON file into a CSV output file.",
                "actions": [
                    {
                        "tool": "read_json",
                        "input": {"path": "demo/input/data.json"},
                        "result": "Read JSON from demo/input/data.json.",
                    },
                    {
                        "tool": "write_text",
                        "input": {"path": "demo/output/data.csv"},
                        "result": "Wrote text to demo/output/data.csv.",
                    },
                ],
                "outputs": ["demo/output/data.csv"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_json_to_csv_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("json_to_csv", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self.assertEqual("execute_skill", result["recommended_next_action"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_path", "output_path"),
        )

    def test_service_distill_and_promote_from_observed_json_to_csv_delimiter_alias_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_json_to_csv_delimiter_alias.json",
            {
                "task": "Convert one JSON file into a CSV output file.",
                "actions": [
                    {
                        "tool": "read_json",
                        "input": {"file": "demo/input/data_pipe.json"},
                        "result": "Read JSON from demo/input/data_pipe.json.",
                    },
                    {
                        "tool": "write_text",
                        "input": {"output": "demo/output/data_pipe.csv", "delimiter": "|"},
                        "result": "Wrote text to demo/output/data_pipe.csv.",
                    },
                ],
                "outputs": ["demo/output/data_pipe.csv"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_json_to_csv_delimiter_alias_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("json_to_csv", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("delimiter", "input_path", "output_path"),
        )

    def test_service_distill_and_promote_from_observed_json_to_csv_csv_aliases_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_json_to_csv_csv_aliases.json",
            {
                "task": "Convert one JSON file into a CSV output file.",
                "actions": [
                    {
                        "tool": "read_json",
                        "input": {"source_json": "demo/input/data.json"},
                        "result": "Read JSON from demo/input/data.json.",
                    },
                    {
                        "tool": "write_text",
                        "input": {"output_csv": "demo/output/data_from_json_alias.csv"},
                        "result": "Wrote text to demo/output/data_from_json_alias.csv.",
                    },
                ],
                "outputs": ["demo/output/data_from_json_alias.csv"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_json_to_csv_csv_aliases_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("json_to_csv", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_path", "output_path"),
        )

    def test_service_distill_and_promote_from_observed_json_to_csv_file_output_aliases_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_json_to_csv_file_output_aliases.json",
            {
                "task": "Convert one JSON file into a CSV output file.",
                "actions": [
                    {
                        "tool": "read_json",
                        "input": {"file": "demo/input/data.json"},
                        "result": "Read JSON from demo/input/data.json.",
                    },
                    {
                        "tool": "write_text",
                        "input": {"output": "demo/output/data_alias.csv"},
                        "result": "Wrote text to demo/output/data_alias.csv.",
                    },
                ],
                "outputs": ["demo/output/data_alias.csv"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_json_to_csv_file_output_aliases_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("json_to_csv", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_path", "output_path"),
        )

    def test_service_distill_and_promote_from_observed_single_json_transform_json_aliases_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_single_json_transform_json_aliases.json",
            {
                "task": "Read one JSON file and write it to a new JSON output file.",
                "actions": [
                    {
                        "tool": "read_json",
                        "input": {"input_json": "demo/input/data.json"},
                        "result": "Read JSON from demo/input/data.json.",
                    },
                    {
                        "tool": "write_json",
                        "input": {"output_json": "demo/output/data_alias_copy.json"},
                        "result": "Wrote JSON to demo/output/data_alias_copy.json.",
                    },
                ],
                "outputs": ["demo/output/data_alias_copy.json"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_single_json_transform_json_aliases_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("single_json_transform", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_path", "output_path"),
        )

    def test_service_distill_and_promote_from_observed_single_json_transform_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_single_json_transform.json",
            {
                "task": "Read one JSON file and write it to a new JSON output file.",
                "actions": [
                    {
                        "tool": "read_json",
                        "input": {"input_file": "demo/input/data.json"},
                        "result": "Read JSON from demo/input/data.json.",
                    },
                    {
                        "tool": "write_json",
                        "input": {"output_file": "demo/output/data_copy.json"},
                        "result": "Wrote JSON to demo/output/data_copy.json.",
                    },
                ],
                "outputs": ["demo/output/data_copy.json"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_single_json_transform_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("single_json_transform", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_path", "output_path"),
        )

    def test_service_distill_and_promote_from_observed_text_transform_text_aliases_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_text_transform_text_aliases.json",
            {
                "task": "Normalize one text file into a cleaned output file.",
                "actions": [
                    {
                        "tool": "read_text",
                        "input": {"source_text_file": "demo/input/a.txt"},
                        "result": "Read text from demo/input/a.txt.",
                    },
                    {
                        "tool": "write_text",
                        "input": {"target_text_file": "demo/output/text_alias_transform.txt"},
                        "result": "Wrote text to demo/output/text_alias_transform.txt.",
                    },
                ],
                "outputs": ["demo/output/text_alias_transform.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_text_transform_text_aliases_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("single_file_transform", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_path", "output_path"),
        )

    def test_service_distill_and_promote_from_observed_input_output_file_aliases_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_input_output_file_aliases.json",
            {
                "task": "Normalize one text file into a cleaned output file.",
                "actions": [
                    {
                        "tool": "read_text",
                        "input": {"input_file": "demo/input/a.txt"},
                        "result": "Read text from demo/input/a.txt.",
                    },
                    {
                        "tool": "write_text",
                        "input": {"output_file": "demo/output/alias_single_transform.txt"},
                        "result": "Wrote text to demo/output/alias_single_transform.txt.",
                    },
                ],
                "outputs": ["demo/output/alias_single_transform.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_input_output_file_alias_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("single_file_transform", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_path", "output_path"),
        )

    def test_service_distill_and_promote_from_observed_text_replace_old_new_aliases_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_text_replace_old_new_aliases.json",
            {
                "task": "Replace one string with another in a text file and write a new output file.",
                "actions": [
                    {
                        "tool": "read_text",
                        "input": {"input_file": "demo/input/a.txt", "old": "file", "new": "document"},
                        "result": "Read source text for replacement.",
                    },
                    {
                        "tool": "write_text",
                        "input": {"output_file": "demo/output/replace_old_new.txt"},
                        "result": "Wrote replaced text output.",
                    },
                ],
                "outputs": ["demo/output/replace_old_new.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_text_replace_old_new_aliases_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("text_replace", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_path", "output_path", "old_text", "new_text"),
        )

    def test_service_distill_and_promote_from_observed_text_replace_find_replacement_aliases_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_text_replace_find_replacement_aliases.json",
            {
                "task": "Replace one string with another in a text file and write a new output file.",
                "actions": [
                    {
                        "tool": "read_text",
                        "input": {"source_text_file": "demo/input/a.txt", "find": "file", "replacement": "document"},
                        "result": "Read source text for replacement.",
                    },
                    {
                        "tool": "write_text",
                        "input": {"destination_text_file": "demo/output/replace_find_replacement.txt"},
                        "result": "Wrote replaced text output.",
                    },
                ],
                "outputs": ["demo/output/replace_find_replacement.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_text_replace_find_replacement_aliases_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("text_replace", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_path", "output_path", "old_text", "new_text"),
        )

    def test_service_distill_and_promote_from_observed_text_replace_needle_replacement_value_aliases_uses_rule_skill(
        self,
    ) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_text_replace_needle_replacement_value_aliases.json",
            {
                "task": "Replace one string with another in a text file and write a new output file.",
                "actions": [
                    {
                        "tool": "read_text",
                        "input": {"source_text_file": "demo/input/a.txt", "needle": "file", "replacement_value": "document"},
                        "result": "Read source text for replacement.",
                    },
                    {
                        "tool": "write_text",
                        "input": {"destination_text_file": "demo/output/replace_needle_replacement_value.txt"},
                        "result": "Wrote replaced text output.",
                    },
                ],
                "outputs": ["demo/output/replace_needle_replacement_value.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_text_replace_needle_replacement_value_aliases_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("text_replace", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_path", "output_path", "old_text", "new_text"),
        )

    def test_service_distill_and_promote_from_observed_single_file_copy_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_single_file_copy.json",
            {
                "task": "Copy one text file into a new output file.",
                "actions": [
                    {
                        "tool": "copy_file",
                        "input": {"source_file": "demo/input/a.txt", "destination_file": "demo/output/copied_a.txt"},
                        "result": "Copied the source file.",
                    },
                ],
                "outputs": ["demo/output/copied_a.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_single_file_copy_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("single_file_copy", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_path", "output_path"),
        )

    def test_service_distill_and_promote_from_observed_single_file_move_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_single_file_move.json",
            {
                "task": "Move one text file into a new output file.",
                "actions": [
                    {
                        "tool": "move_file",
                        "input": {"source_path": "demo/input/a.txt", "target_path": "demo/output/moved_a.txt"},
                        "result": "Moved the source file.",
                    },
                ],
                "outputs": ["demo/output/moved_a.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_single_file_move_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("single_file_move", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_path", "output_path"),
        )

    def test_service_distill_and_promote_from_observed_single_file_move_src_dst_aliases_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_single_file_move_src_dst.json",
            {
                "task": "Move one text file into a new output file.",
                "actions": [
                    {
                        "tool": "move_file",
                        "input": {"src": "demo/input/a.txt", "dst": "demo/output/moved_src_dst.txt"},
                        "result": "Moved the source file.",
                    },
                ],
                "outputs": ["demo/output/moved_src_dst.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_single_file_move_src_dst_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("single_file_move", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_path", "output_path"),
        )

    def test_service_distill_and_promote_from_observed_single_file_move_from_to_aliases_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_single_file_move_from_to.json",
            {
                "task": "Move one text file into a new output file.",
                "actions": [
                    {
                        "tool": "move_file",
                        "input": {"from": "demo/input/a.txt", "to": "demo/output/moved_from_to.txt"},
                        "result": "Moved the source file.",
                    },
                ],
                "outputs": ["demo/output/moved_from_to.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_single_file_move_from_to_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("single_file_move", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_path", "output_path"),
        )

    def test_service_distill_and_promote_from_observed_single_file_move_input_output_aliases_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_single_file_move_input_output.json",
            {
                "task": "Move one text file into a new output file.",
                "actions": [
                    {
                        "tool": "move_file",
                        "input": {"input": "demo/input/a.txt", "output": "demo/output/moved_input_output.txt"},
                        "result": "Moved the source file.",
                    },
                ],
                "outputs": ["demo/output/moved_input_output.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_single_file_move_input_output_aliases_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("single_file_move", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_path", "output_path"),
        )

    def test_service_distill_and_promote_from_observed_single_file_rename_source_target_aliases_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_single_file_rename_source_target.json",
            {
                "task": "Rename one text file to a new output path.",
                "actions": [
                    {
                        "tool": "rename_path",
                        "input": {"source": "demo/input/a.txt", "target": "demo/output/renamed_a.txt"},
                        "result": "Renamed the source file.",
                    },
                ],
                "outputs": ["demo/output/renamed_a.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_single_file_rename_source_target_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("single_file_move", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_path", "output_path"),
        )

    def test_service_distill_and_promote_from_observed_source_target_dir_aliases_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_source_target_dir_aliases.json",
            {
                "task": "Move all log files from inbox to archive.",
                "actions": [
                    {
                        "tool": "list_files",
                        "input": {"source_dir": "demo/inbox", "pattern": "*.log"},
                        "result": "Found 2 log files.",
                    },
                    {
                        "tool": "move_file",
                        "input": {"source_dir": "demo/inbox", "target_dir": "demo/archive"},
                        "result": "Moved the matching files.",
                    },
                ],
                "outputs": ["demo/archive/job1.log"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_source_target_dir_alias_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_move", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern"),
        )

    def test_service_distill_and_promote_from_observed_directory_move_from_to_dir_aliases_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_directory_move_from_to_dir_aliases.json",
            {
                "task": "Move all log files from inbox to archive.",
                "actions": [
                    {
                        "tool": "list_files",
                        "input": {"from_dir": "demo/inbox", "pattern": "*.log"},
                        "result": "Found 2 log files.",
                    },
                    {
                        "tool": "move_file",
                        "input": {"from_dir": "demo/inbox", "to_dir": "demo/archive"},
                        "result": "Moved the matching files.",
                    },
                ],
                "outputs": ["demo/archive/job1.log"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_directory_move_from_to_dir_aliases_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_move", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern"),
        )

    def test_service_distill_and_promote_from_observed_directory_move_input_output_aliases_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_directory_move_input_output_aliases.json",
            {
                "task": "Move all log files from inbox to archive.",
                "actions": [
                    {
                        "tool": "list_files",
                        "input": {"path": "demo/inbox", "pattern": "*.log"},
                        "result": "Found 2 log files.",
                    },
                    {
                        "tool": "move_file",
                        "input": {"input": "demo/inbox", "output": "demo/archive"},
                        "result": "Moved the matching files.",
                    },
                ],
                "outputs": ["demo/archive/job1.log"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_directory_move_input_output_aliases_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_move", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern"),
        )

    def test_service_distill_and_promote_from_observed_directory_copy_input_output_aliases_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_directory_copy_input_output_aliases.json",
            {
                "task": "Copy matching txt files from one directory into another directory.",
                "actions": [
                    {
                        "tool": "list_files",
                        "input": {"path": "demo/copy_input", "pattern": "*.txt"},
                        "result": "Found 2 txt files.",
                    },
                    {
                        "tool": "copy_file",
                        "input": {"input": "demo/copy_input", "output": "demo/copy_output"},
                        "result": "Copied the matching files.",
                    },
                ],
                "outputs": ["demo/copy_output/keep_a.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_directory_copy_input_output_aliases_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_copy", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern"),
        )

    def test_service_distill_and_promote_from_observed_directory_move_directory_aliases_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_directory_move_directory_aliases.json",
            {
                "task": "Move all log files from inbox to archive.",
                "actions": [
                    {
                        "tool": "list_files",
                        "input": {"source_directory": "demo/inbox", "pattern": "*.log"},
                        "result": "Found 2 log files.",
                    },
                    {
                        "tool": "move_file",
                        "input": {"source_directory": "demo/inbox", "target_directory": "demo/archive"},
                        "result": "Moved the matching files.",
                    },
                ],
                "outputs": ["demo/archive/job1.log"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_directory_move_directory_aliases_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_move", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern"),
        )

    def test_service_distill_and_promote_from_observed_directory_move_glob_alias_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_directory_move_glob_alias.json",
            {
                "task": "Move all log files from inbox to archive.",
                "actions": [
                    {
                        "tool": "list_files",
                        "input": {"source_dir": "demo/inbox", "glob": "*.log"},
                        "result": "Found 2 log files.",
                    },
                    {
                        "tool": "move_file",
                        "input": {"source_dir": "demo/inbox", "target_dir": "demo/archive"},
                        "result": "Moved the matching files.",
                    },
                ],
                "outputs": ["demo/archive/job1.log"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_directory_move_glob_alias_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_move", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern"),
        )

    def test_service_distill_and_promote_from_observed_directory_text_replace_search_replace_aliases_uses_rule_skill(
        self,
    ) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_directory_text_replace_search_replace_aliases.json",
            {
                "task": "Replace one string with another across all txt files in a directory and write outputs to another directory.",
                "actions": [
                    {
                        "tool": "list_files",
                        "input": {
                            "source_dir": "demo/replace_dir_input",
                            "target_dir": "demo/replace_dir_output",
                            "pattern": "*.txt",
                            "search": "file",
                            "replace": "document",
                        },
                        "result": "Found txt files to rewrite.",
                    },
                    {
                        "tool": "read_text",
                        "input": {"source_dir": "demo/replace_dir_input"},
                        "result": "Read each source file.",
                    },
                    {
                        "tool": "write_text",
                        "input": {"target_dir": "demo/replace_dir_output"},
                        "result": "Wrote replaced outputs.",
                    },
                ],
                "outputs": ["demo/replace_dir_output/a.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_directory_text_replace_search_replace_aliases_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_text_replace", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "old_text", "new_text", "pattern"),
        )

    def test_service_distill_and_promote_from_observed_directory_text_replace_filter_alias_uses_rule_skill(
        self,
    ) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_directory_text_replace_filter_alias.json",
            {
                "task": "Replace one string with another across all txt files in a directory and write outputs to another directory.",
                "actions": [
                    {
                        "tool": "list_files",
                        "input": {
                            "source_dir": "demo/replace_dir_input",
                            "target_dir": "demo/replace_dir_output",
                            "filter": "*.txt",
                            "search": "file",
                            "replace": "document",
                        },
                        "result": "Found txt files to rewrite.",
                    },
                    {
                        "tool": "read_text",
                        "input": {"source_dir": "demo/replace_dir_input"},
                        "result": "Read each source file.",
                    },
                    {
                        "tool": "write_text",
                        "input": {"target_dir": "demo/replace_dir_output"},
                        "result": "Wrote replaced outputs.",
                    },
                ],
                "outputs": ["demo/replace_dir_output/a.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_directory_text_replace_filter_alias_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_text_replace", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "old_text", "new_text", "pattern"),
        )

    def test_service_distill_and_promote_from_observed_directory_text_replace_directory_aliases_uses_rule_skill(
        self,
    ) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_directory_text_replace_directory_aliases.json",
            {
                "task": "Replace one string with another across all txt files in a directory and write outputs to another directory.",
                "actions": [
                    {
                        "tool": "list_files",
                        "input": {
                            "input_directory": "demo/replace_dir_input",
                            "output_directory": "demo/replace_dir_output",
                            "pattern": "*.txt",
                            "old_text": "file",
                            "new_text": "document",
                        },
                        "result": "Found txt files to rewrite.",
                    },
                    {
                        "tool": "read_text",
                        "input": {"input_directory": "demo/replace_dir_input"},
                        "result": "Read each source file.",
                    },
                    {
                        "tool": "write_text",
                        "input": {"output_directory": "demo/replace_dir_output"},
                        "result": "Wrote replaced outputs.",
                    },
                ],
                "outputs": ["demo/replace_dir_output/a.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_directory_text_replace_directory_aliases_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_text_replace", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "old_text", "new_text", "pattern"),
        )

    def test_service_distill_and_promote_from_observed_batch_rename_glob_alias_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_batch_rename_glob_alias.json",
            {
                "task": "Rename all txt files in a directory by prefixing them with a value.",
                "actions": [
                    {
                        "tool": "list_files",
                        "input": {"path": "demo/rename_input", "glob": "*.txt"},
                        "result": "Found 2 txt files.",
                    },
                    {
                        "tool": "rename_path",
                        "input": {"from_path": "demo/rename_input/a.txt", "to_path": "demo/rename_input/done_a.txt"},
                        "result": "Renamed the matching file.",
                    },
                ],
                "outputs": ["demo/rename_input/done_a.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_batch_rename_glob_alias_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("batch_rename", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "prefix", "pattern"),
        )

    def test_service_distill_and_promote_from_observed_batch_rename_name_prefix_alias_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_batch_rename_name_prefix_alias.json",
            {
                "task": "Rename all txt files in a directory by prefixing them with a value.",
                "actions": [
                    {
                        "tool": "list_files",
                        "input": {"path": "demo/rename_input", "pattern": "*.txt", "name_prefix": "done_"},
                        "result": "Found 2 txt files.",
                    },
                    {
                        "tool": "rename_path",
                        "input": {"from_path": "demo/rename_input/a.txt", "to_path": "demo/rename_input/done_a.txt"},
                        "result": "Renamed the matching file.",
                    },
                ],
                "outputs": ["demo/rename_input/done_a.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_batch_rename_name_prefix_alias_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("batch_rename", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "prefix", "pattern"),
        )

    def test_service_distill_and_promote_from_observed_batch_rename_rename_prefix_alias_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_batch_rename_rename_prefix_alias.json",
            {
                "task": "Rename all txt files in a directory by prefixing them with a value.",
                "actions": [
                    {
                        "tool": "list_files",
                        "input": {"path": "demo/rename_input", "pattern": "*.txt", "rename_prefix": "done_"},
                        "result": "Found 2 txt files.",
                    },
                    {
                        "tool": "rename_path",
                        "input": {"from_path": "demo/rename_input/a.txt", "to_path": "demo/rename_input/done_a.txt"},
                        "result": "Renamed the matching file.",
                    },
                ],
                "outputs": ["demo/rename_input/done_a.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_batch_rename_rename_prefix_alias_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("batch_rename", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "prefix", "pattern"),
        )

    def test_service_distill_and_promote_from_observed_batch_rename_from_to_path_aliases_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_batch_rename_from_to_path_aliases.json",
            {
                "task": "Rename all txt files in a directory by prefixing them with a value.",
                "actions": [
                    {
                        "tool": "list_files",
                        "input": {"path": "demo/rename_input", "pattern": "*.txt"},
                        "result": "Found 2 txt files.",
                    },
                    {
                        "tool": "rename_path",
                        "input": {"from_path": "demo/rename_input/a.txt", "to_path": "demo/rename_input/done_a.txt"},
                        "result": "Renamed the matching file.",
                    },
                ],
                "outputs": ["demo/rename_input/done_a.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_batch_rename_from_to_path_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("batch_rename", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "prefix", "pattern"),
        )

    def test_service_distill_and_promote_from_observed_batch_rename_from_to_aliases_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_batch_rename_from_to_aliases.json",
            {
                "task": "Rename all txt files in a directory by prefixing them with a value.",
                "actions": [
                    {
                        "tool": "list_files",
                        "input": {"path": "demo/rename_input", "pattern": "*.txt"},
                        "result": "Found 2 txt files.",
                    },
                    {
                        "tool": "rename_path",
                        "input": {"from": "demo/rename_input/a.txt", "to": "demo/rename_input/done_a.txt"},
                        "result": "Renamed the matching file.",
                    },
                ],
                "outputs": ["demo/rename_input/done_a.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_batch_rename_from_to_aliases_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("batch_rename", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "prefix", "pattern"),
        )

    def test_service_distill_and_promote_from_execute_observed_task_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        execute_result = sandbox_service.execute(
            "merge_text_files",
            {"input_dir": "demo/input", "output_path": "demo/output/execute_roundtrip_merge.md"},
        )
        observed_path = execute_result["observed_task_record"]

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="execute_observed_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertIsNotNone(result["capture"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("execute_observed_roundtrip_test", result["promotion"]["skill_name"])
        self.assertEqual("text_merge", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self.assertEqual("execute_skill", result["recommended_next_action"])
        self._assert_host_operation_basics(
            result["recommended_host_operation"],
            tool_name="execute_skill",
        )
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_path", "pattern"),
        )

    def test_service_distill_and_promote_from_execute_directory_move_observed_task_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        inbox = sandbox_root / "demo" / "inbox"
        archive = sandbox_root / "demo" / "archive"
        inbox.mkdir(parents=True, exist_ok=True)
        archive.mkdir(parents=True, exist_ok=True)
        (inbox / "job1.log").write_text("alpha\n", encoding="utf-8")
        (inbox / "job2.log").write_text("beta\n", encoding="utf-8")

        execute_result = sandbox_service.execute(
            "archive_log_files_dogfood",
            {"input_dir": "demo/inbox", "output_dir": "demo/archive", "pattern": "*.log"},
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=execute_result["observed_task_record"],
            skill_name="execute_directory_move_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_move", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern"),
        )

    def test_service_distill_and_promote_from_execute_directory_copy_observed_task_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        source_dir = sandbox_root / "demo" / "copy_input"
        target_dir = sandbox_root / "demo" / "copy_output"
        source_dir.mkdir(parents=True, exist_ok=True)
        target_dir.mkdir(parents=True, exist_ok=True)
        (source_dir / "a.txt").write_text("alpha\n", encoding="utf-8")
        (source_dir / "b.txt").write_text("beta\n", encoding="utf-8")

        execute_result = sandbox_service.execute(
            "directory_copy_rule_test",
            {"input_dir": "demo/copy_input", "output_dir": "demo/copy_output", "pattern": "*.txt"},
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=execute_result["observed_task_record"],
            skill_name="execute_directory_copy_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_copy", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern"),
        )

    def test_service_distill_and_promote_from_execute_batch_rename_observed_task_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        input_dir = sandbox_root / "demo" / "rename_input"
        input_dir.mkdir(parents=True, exist_ok=True)
        (input_dir / "a.txt").write_text("alpha\n", encoding="utf-8")
        (input_dir / "b.txt").write_text("beta\n", encoding="utf-8")

        execute_result = sandbox_service.execute(
            "batch_rename_rule_test",
            {"input_dir": "demo/rename_input", "prefix": "done_", "pattern": "*.txt"},
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=execute_result["observed_task_record"],
            skill_name="execute_batch_rename_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("batch_rename", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "prefix", "pattern"),
        )

    def test_service_distill_and_promote_flow(self) -> None:
        sandbox_root, sandbox_service, sandbox_index = self._make_runtime_sandbox()
        result = sandbox_service.distill_and_promote(
            trajectory_path=sandbox_root / "trajectories" / "demo_merge_text_files.json",
            skill_name="service_distill_and_promote_test",
        )
        self.assertTrue(result["promoted"])
        self.assertIsNotNone(result["trajectory"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("service_distill_and_promote_test", result["promotion"]["skill_name"])

        promoted = sandbox_index.get("service_distill_and_promote_test")
        self.assertIsNotNone(promoted)
        self.assertEqual("active", promoted.status)
        self.assertEqual("execute_skill", result["recommended_next_action"])
        self._assert_host_operation_basics(
            result["recommended_host_operation"],
            tool_name="execute_skill",
        )
        self.assertEqual(
            "service_distill_and_promote_test",
            result["recommended_host_operation"]["arguments"]["skill_name"],
        )
        self._assert_execute_skill_schema(result["recommended_host_operation"])

    def test_service_distill_returns_audit_follow_up_host_operation(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        result = sandbox_service.distill(
            sandbox_root / "trajectories" / "demo_merge_text_files.json",
            skill_name="service_distill_followup_test",
        )
        self.assertEqual("audit_skill", result["recommended_next_action"])
        self._assert_host_operation_basics(
            result["recommended_host_operation"],
            tool_name="audit_skill",
        )
        self.assertEqual(result["staging_file"], result["recommended_host_operation"]["arguments"]["file_path"])
        self.assertEqual(
            result["trajectory_path"],
            result["recommended_host_operation"]["arguments"]["trajectory_path"],
        )
        self._assert_operation_role(result["available_host_operations"][0], "primary")

    def test_service_distill_and_promote_from_observed_task(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_distill_promote_service.json",
            self._build_move_logs_observed_task(variant="steps"),
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_distill_promote_service_test",
        )
        self.assertTrue(result["promoted"])
        self.assertIsNotNone(result["capture"])
        self.assertIsNone(result["trajectory"])
        self.assertEqual("observed_distill_promote_service_test", result["promotion"]["skill_name"])
        self.assertEqual("execute_skill", result["recommended_next_action"])
        self._assert_host_operation_basics(
            result["recommended_host_operation"],
            tool_name="execute_skill",
        )
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern"),
        )

    def test_mcp_distill_and_promote_tool_returns_promoted_skill(self) -> None:
        sandbox_root, _, _ = self._make_runtime_sandbox()
        payload = self._call_mcp_tool(
            "distill_and_promote_candidate",
            {
                "trajectory_path": str(sandbox_root / "trajectories" / "demo_merge_text_files.json"),
                "skill_name": "mcp_distill_and_promote_test",
                "register_trajectory": True,
            },
            root=sandbox_root,
        )
        self.assertTrue(payload["data"]["promoted"])
        self.assertEqual("mcp_distill_and_promote_test", payload["data"]["promotion"]["skill_name"])
        self.assertEqual("execute_skill", payload["data"]["recommended_next_action"])
        self._assert_host_operation_basics(
            payload["data"]["recommended_host_operation"],
            tool_name="execute_skill",
        )
        self._assert_execute_skill_schema(
            payload["data"]["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_path", "pattern"),
        )

    def test_mcp_distill_and_promote_tool_accepts_observed_task(self) -> None:
        sandbox_root, _, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_distill_promote_mcp.json",
            self._build_move_logs_observed_task(variant="steps", artifact=None),
        )

        payload = self._call_mcp_tool(
            "distill_and_promote_candidate",
            {
                "observed_task_path": str(observed_path),
                "skill_name": "mcp_observed_distill_promote_test",
            },
            root=sandbox_root,
        )
        self.assertTrue(payload["data"]["promoted"])
        self.assertIsNotNone(payload["data"]["capture"])
        self.assertEqual("execute_skill", payload["data"]["recommended_next_action"])
        self._assert_host_operation_basics(
            payload["data"]["recommended_host_operation"],
            tool_name="execute_skill",
        )
        self._assert_execute_skill_schema(
            payload["data"]["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern"),
        )

    def test_cli_distill_and_promote_accepts_observed_task(self) -> None:
        sandbox_root, _, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_distill_promote_cli.json",
            self._build_move_logs_observed_task(variant="steps", artifact=None),
        )

        payload = self._run_cli(
            "distill-and-promote",
            "--observed-task",
            str(observed_path),
            "--skill-name",
            "cli_observed_distill_promote_test",
            root=sandbox_root,
            expect_json=True,
        )
        self.assertEqual("ok", payload["status"])
        self.assertTrue(payload["data"]["promoted"])
        self.assertIsNotNone(payload["data"]["capture"])

    def test_cli_distill_and_promote_accepts_compact_observed_task(self) -> None:
        sandbox_root, _, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_distill_promote_compact_cli.json",
            self._build_move_logs_observed_task(variant="compact"),
        )

        payload = self._run_cli(
            "distill-and-promote",
            "--observed-task",
            str(observed_path),
            "--skill-name",
            "cli_compact_observed_distill_promote_test",
            root=sandbox_root,
            expect_json=True,
        )
        self.assertEqual("ok", payload["status"])
        self.assertTrue(payload["data"]["promoted"])
        self.assertIsNotNone(payload["data"]["capture"])

    def test_cli_distill_and_promote_accepts_nested_tool_call_logs(self) -> None:
        sandbox_root, _, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_distill_promote_nested_cli.json",
            self._build_move_logs_observed_task(variant="nested"),
        )

        payload = self._run_cli(
            "distill-and-promote",
            "--observed-task",
            str(observed_path),
            "--skill-name",
            "cli_nested_observed_distill_promote_test",
            root=sandbox_root,
            expect_json=True,
        )
        self.assertEqual("ok", payload["status"])
        self.assertTrue(payload["data"]["promoted"])
        self.assertIsNotNone(payload["data"]["capture"])
