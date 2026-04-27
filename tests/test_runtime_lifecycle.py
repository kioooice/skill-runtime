import json

from skill_runtime.api.models import Trajectory, TrajectoryStep
from tests.runtime_test_support import ROOT


class RuntimeLifecycleTestsMixin:
    def test_service_distill_and_promote_from_inline_observed_single_file_transform_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()

        result = sandbox_service.distill_and_promote(
            observed_task={
                "task": "Normalize one text file into a cleaned output file.",
                "actions": [
                    {
                        "tool": "read_text",
                        "input": {"path": "demo/input/a.txt"},
                        "result": "Read text from demo/input/a.txt.",
                    },
                    {
                        "tool": "write_text",
                        "input": {"path": "demo/output/single_transform_inline.txt"},
                        "result": "Wrote text to demo/output/single_transform_inline.txt.",
                    },
                ],
                "outputs": ["demo/output/single_transform_inline.txt"],
            },
            skill_name="observed_inline_single_file_transform_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("single_file_transform", metadata["rule_name"])
        self.assertEqual("execute_skill", result["recommended_next_action"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_path", "output_path"),
        )
        self.assertIsNotNone(result["capture"])
        self.assertTrue(result["capture"]["captured"])
        self.assertIsNotNone(result["capture"]["trajectory_path"])

    def test_cli_distill_and_promote_from_inline_observed_single_file_transform_uses_rule_skill(self) -> None:
        sandbox_root, _, _ = self._make_runtime_sandbox()
        payload = self._run_cli(
            "distill-and-promote",
            "--observed-task-json",
            json.dumps(
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
                            "input": {"path": "demo/output/single_transform_cli_inline.txt"},
                            "result": "Wrote text to demo/output/single_transform_cli_inline.txt.",
                        },
                    ],
                    "outputs": ["demo/output/single_transform_cli_inline.txt"],
                }
            ),
            "--skill-name",
            "observed_cli_inline_single_file_transform_roundtrip_test",
            root=sandbox_root,
            expect_json=True,
        )
        metadata = self._read_json_file(__import__("pathlib").Path(payload["data"]["distillation"]["metadata_file"]))

        self.assertEqual("ok", payload["status"])
        self.assertTrue(payload["data"]["promoted"])
        self.assertEqual("single_file_transform", metadata["rule_name"])
        self.assertEqual("execute_skill", payload["data"]["recommended_next_action"])

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

    def test_service_distill_and_promote_from_observed_csv_to_json_source_destination_aliases_uses_rule_skill(
        self,
    ) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_csv_to_json_source_destination_aliases.json",
            {
                "task": "Convert one CSV file into a JSON output file.",
                "actions": [
                    {
                        "tool": "read_text",
                        "input": {"source": "demo/input/data.csv"},
                        "result": "Read text from demo/input/data.csv.",
                    },
                    {
                        "tool": "write_json",
                        "input": {"destination": "demo/output/data_source_destination.json"},
                        "result": "Wrote JSON to demo/output/data_source_destination.json.",
                    },
                ],
                "outputs": ["demo/output/data_source_destination.json"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_csv_to_json_source_destination_aliases_test",
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

    def test_service_distill_and_promote_from_observed_json_to_csv_source_destination_aliases_uses_rule_skill(
        self,
    ) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_json_to_csv_source_destination_aliases.json",
            {
                "task": "Convert one JSON file into a CSV output file.",
                "actions": [
                    {
                        "tool": "read_json",
                        "input": {"source": "demo/input/data.json"},
                        "result": "Read JSON from demo/input/data.json.",
                    },
                    {
                        "tool": "write_text",
                        "input": {"destination": "demo/output/data_source_destination.csv"},
                        "result": "Wrote text to demo/output/data_source_destination.csv.",
                    },
                ],
                "outputs": ["demo/output/data_source_destination.csv"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_json_to_csv_source_destination_aliases_test",
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

    def test_service_distill_and_promote_from_observed_single_json_transform_source_destination_aliases_uses_rule_skill(
        self,
    ) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_single_json_transform_source_destination_aliases.json",
            {
                "task": "Read one JSON file and write it to a new JSON output file.",
                "actions": [
                    {
                        "tool": "read_json",
                        "input": {"source": "demo/input/data.json"},
                        "result": "Read JSON from demo/input/data.json.",
                    },
                    {
                        "tool": "write_json",
                        "input": {"destination": "demo/output/data_source_destination_copy.json"},
                        "result": "Wrote JSON to demo/output/data_source_destination_copy.json.",
                    },
                ],
                "outputs": ["demo/output/data_source_destination_copy.json"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_single_json_transform_source_destination_aliases_test",
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

    def test_service_distill_and_promote_from_observed_single_file_transform_source_destination_aliases_uses_rule_skill(
        self,
    ) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_single_file_transform_source_destination_aliases.json",
            {
                "task": "Normalize one text file into a cleaned output file.",
                "actions": [
                    {
                        "tool": "read_text",
                        "input": {"source": "demo/input/a.txt"},
                        "result": "Read text from demo/input/a.txt.",
                    },
                    {
                        "tool": "write_text",
                        "input": {"destination": "demo/output/source_destination_transform.txt"},
                        "result": "Wrote text to demo/output/source_destination_transform.txt.",
                    },
                ],
                "outputs": ["demo/output/source_destination_transform.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_single_file_transform_source_destination_aliases_test",
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

    def test_service_distill_and_promote_from_observed_single_file_transform_with_newline_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_single_file_transform_newline.json",
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
                        "input": {"path": "demo/output/single_transform_crlf.txt", "newline": "\n"},
                        "result": "Wrote text to demo/output/single_transform_crlf.txt with LF endings.",
                    },
                ],
                "outputs": ["demo/output/single_transform_crlf.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_single_file_transform_newline_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("single_file_transform", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_path", "output_path", "newline"),
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

    def test_service_distill_and_promote_from_observed_text_replace_source_destination_aliases_uses_rule_skill(
        self,
    ) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_text_replace_source_destination_aliases.json",
            {
                "task": "Replace one string with another in a text file and write a new output file.",
                "actions": [
                    {
                        "tool": "read_text",
                        "input": {"source": "demo/input/a.txt", "old_text": "file", "new_text": "document"},
                        "result": "Read source text for replacement.",
                    },
                    {
                        "tool": "write_text",
                        "input": {"destination": "demo/output/replace_source_destination.txt"},
                        "result": "Wrote replaced text output.",
                    },
                ],
                "outputs": ["demo/output/replace_source_destination.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_text_replace_source_destination_aliases_test",
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

    def test_service_distill_and_promote_from_observed_text_replace_with_newline_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_text_replace_newline.json",
            {
                "task": "Replace one string with another in a text file and write a new output file.",
                "actions": [
                    {
                        "tool": "read_text",
                        "input": {"path": "demo/input/a.txt", "old_text": "file", "new_text": "document"},
                        "result": "Read source text for replacement.",
                    },
                    {
                        "tool": "write_text",
                        "input": {"path": "demo/output/replace_newline.txt", "newline": "\n"},
                        "result": "Wrote replaced text output with LF endings.",
                    },
                ],
                "outputs": ["demo/output/replace_newline.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_text_replace_newline_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("text_replace", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_path", "output_path", "old_text", "new_text", "newline"),
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

    def test_service_distill_and_promote_from_observed_single_file_copy_input_output_aliases_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_single_file_copy_input_output.json",
            {
                "task": "Copy one text file into a new output file.",
                "actions": [
                    {
                        "tool": "copy_file",
                        "input": {"input": "demo/input/a.txt", "output": "demo/output/copied_input_output.txt"},
                        "result": "Copied the source file.",
                    },
                ],
                "outputs": ["demo/output/copied_input_output.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_single_file_copy_input_output_aliases_test",
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

    def test_service_distill_and_promote_from_observed_single_file_copy_source_target_aliases_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_single_file_copy_source_target.json",
            {
                "task": "Copy one text file into a new output file.",
                "actions": [
                    {
                        "tool": "copy_file",
                        "input": {"source": "demo/input/a.txt", "target": "demo/output/copied_source_target.txt"},
                        "result": "Copied the source file.",
                    },
                ],
                "outputs": ["demo/output/copied_source_target.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_single_file_copy_source_target_aliases_test",
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

    def test_service_distill_and_promote_from_observed_single_file_copy_destination_alias_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_single_file_copy_destination.json",
            {
                "task": "Copy one text file into a new output file.",
                "actions": [
                    {
                        "tool": "copy_file",
                        "input": {"source_file": "demo/input/a.txt", "destination": "demo/output/copied_destination.txt"},
                        "result": "Copied the source file.",
                    },
                ],
                "outputs": ["demo/output/copied_destination.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_single_file_copy_destination_aliases_test",
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

    def test_service_distill_and_promote_from_observed_single_file_rename_input_output_aliases_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_single_file_rename_input_output.json",
            {
                "task": "Rename one text file to a new output path.",
                "actions": [
                    {
                        "tool": "rename_path",
                        "input": {"input": "demo/input/a.txt", "output": "demo/output/renamed_input_output.txt"},
                        "result": "Renamed the source file.",
                    },
                ],
                "outputs": ["demo/output/renamed_input_output.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_single_file_rename_input_output_aliases_test",
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

    def test_service_distill_and_promote_from_observed_directory_copy_source_target_aliases_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_directory_copy_source_target_aliases.json",
            {
                "task": "Copy matching txt files from one directory into another directory.",
                "actions": [
                    {
                        "tool": "list_files",
                        "input": {"source": "demo/copy_input", "pattern": "*.txt"},
                        "result": "Found 2 txt files.",
                    },
                    {
                        "tool": "copy_file",
                        "input": {"source": "demo/copy_input", "target": "demo/copy_output"},
                        "result": "Copied the matching files.",
                    },
                ],
                "outputs": ["demo/copy_output/keep_a.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_directory_copy_source_target_aliases_test",
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

    def test_service_distill_and_promote_from_observed_directory_copy_destination_alias_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_directory_copy_destination_aliases.json",
            {
                "task": "Copy matching txt files from one directory into another directory.",
                "actions": [
                    {
                        "tool": "list_files",
                        "input": {"source_dir": "demo/copy_input", "pattern": "*.txt"},
                        "result": "Found 2 txt files.",
                    },
                    {
                        "tool": "copy_file",
                        "input": {"source_dir": "demo/copy_input", "destination": "demo/copy_output"},
                        "result": "Copied the matching files.",
                    },
                ],
                "outputs": ["demo/copy_output/keep_a.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_directory_copy_destination_aliases_test",
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

    def test_service_distill_and_promote_from_observed_directory_copy_with_prefix_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_directory_copy_prefix.json",
            {
                "task": "Copy matching txt files from one directory into another directory.",
                "actions": [
                    {
                        "tool": "list_files",
                        "input": {"path": "demo/copy_prefix_input", "pattern": "*.txt"},
                        "result": "Found 2 txt files.",
                    },
                    {
                        "tool": "copy_file",
                        "input": {
                            "source_path": "demo/copy_prefix_input/a.txt",
                            "target_path": "demo/copy_prefix_output/done_a.txt",
                        },
                        "result": "Copied one prefixed txt file.",
                    },
                ],
                "outputs": ["demo/copy_prefix_output/done_a.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_directory_copy_prefix_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_copy", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern", "prefix"),
        )

    def test_service_distill_and_promote_from_observed_directory_move_with_suffix_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_directory_move_suffix.json",
            {
                "task": "Move matching log files from one directory into another directory.",
                "actions": [
                    {
                        "tool": "list_files",
                        "input": {"path": "demo/move_suffix_input", "pattern": "*.log"},
                        "result": "Found 2 log files.",
                    },
                    {
                        "tool": "move_file",
                        "input": {
                            "source_path": "demo/move_suffix_input/a.log",
                            "target_path": "demo/move_suffix_output/a_done.log",
                        },
                        "result": "Moved one suffixed log file.",
                    },
                ],
                "outputs": ["demo/move_suffix_output/a_done.log"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_directory_move_suffix_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_move", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern", "suffix"),
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

    def test_service_distill_and_promote_from_observed_directory_text_replace_with_prefix_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_directory_text_replace_prefix.json",
            {
                "task": "Replace one string with another across all txt files in a directory and write outputs to another directory.",
                "actions": [
                    {
                        "tool": "list_files",
                        "input": {"path": "demo/replace_dir_input", "pattern": "*.txt"},
                        "result": "Found txt files to rewrite.",
                    },
                    {
                        "tool": "read_text",
                        "input": {"path": "demo/replace_dir_input/a.txt", "old_text": "file", "new_text": "document"},
                        "result": "Read one text file for replacement.",
                    },
                    {
                        "tool": "write_text",
                        "input": {"path": "demo/replace_dir_output/done_a.txt"},
                        "result": "Wrote prefixed replaced output.",
                    },
                ],
                "outputs": ["demo/replace_dir_output/done_a.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_directory_text_replace_prefix_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_text_replace", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "old_text", "new_text", "pattern", "prefix"),
        )

    def test_service_distill_and_promote_from_observed_directory_text_replace_with_suffix_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_directory_text_replace_suffix.json",
            {
                "task": "Replace one string with another across all txt files in a directory and write outputs to another directory.",
                "actions": [
                    {
                        "tool": "list_files",
                        "input": {"path": "demo/replace_dir_input", "pattern": "*.txt"},
                        "result": "Found txt files to rewrite.",
                    },
                    {
                        "tool": "read_text",
                        "input": {"path": "demo/replace_dir_input/a.txt", "old_text": "file", "new_text": "document"},
                        "result": "Read one text file for replacement.",
                    },
                    {
                        "tool": "write_text",
                        "input": {"path": "demo/replace_dir_output/a_done.txt"},
                        "result": "Wrote suffixed replaced output.",
                    },
                ],
                "outputs": ["demo/replace_dir_output/a_done.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_directory_text_replace_suffix_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_text_replace", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "old_text", "new_text", "pattern", "suffix"),
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

    def test_service_distill_and_promote_from_observed_batch_rename_input_output_aliases_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_batch_rename_input_output_aliases.json",
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
                        "input": {"input": "demo/rename_input/a.txt", "output": "demo/rename_input/done_a.txt"},
                        "result": "Renamed the matching file.",
                    },
                ],
                "outputs": ["demo/rename_input/done_a.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_batch_rename_input_output_aliases_test",
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

    def test_service_distill_and_promote_from_observed_batch_rename_suffix_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_batch_rename_suffix.json",
            {
                "task": "Rename all txt files in a directory by suffixing them with a value.",
                "actions": [
                    {
                        "tool": "list_files",
                        "input": {"path": "demo/rename_input", "pattern": "*.txt"},
                        "result": "Found 2 txt files.",
                    },
                    {
                        "tool": "rename_path",
                        "input": {"source": "demo/rename_input/a.txt", "target": "demo/rename_input/a_done.txt"},
                        "result": "Renamed the matching file.",
                    },
                ],
                "outputs": ["demo/rename_input/a_done.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_batch_rename_suffix_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("batch_rename_suffix", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "suffix", "pattern"),
        )

    def test_service_distill_and_promote_from_observed_batch_rename_extension_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_batch_rename_extension.json",
            {
                "task_description": "Rename all txt files in a directory by changing their extension to md.",
                "steps": [
                    {
                        "tool_name": "list_files",
                        "tool_input": {"path": "demo/rename_extension_input", "pattern": "*.txt"},
                        "observation": "Found files to rename.",
                        "status": "success",
                    },
                    {
                        "tool_name": "rename_path",
                        "tool_input": {
                            "source": "demo/rename_extension_input/one.txt",
                            "target": "demo/rename_extension_input/one.md",
                        },
                        "observation": "Renamed matching files by changing their extension.",
                        "status": "success",
                    },
                ],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_batch_rename_extension_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("batch_rename_extension", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_extension", "pattern"),
        )

    def test_service_distill_and_promote_from_observed_batch_rename_replace_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_batch_rename_replace.json",
            {
                "task_description": "Rename all txt files in a directory by replacing draft with final in each filename.",
                "steps": [
                    {
                        "tool_name": "list_files",
                        "tool_input": {"path": "demo/rename_replace_input", "pattern": "*.txt"},
                        "observation": "Found files to rename.",
                        "status": "success",
                    },
                    {
                        "tool_name": "rename_path",
                        "tool_input": {
                            "source": "demo/rename_replace_input/draft_one.txt",
                            "target": "demo/rename_replace_input/final_one.txt",
                        },
                        "observation": "Renamed matching files by replacing part of each filename.",
                        "status": "success",
                    },
                ],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_batch_rename_replace_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("batch_rename_replace", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "old_text", "new_text", "pattern"),
        )

    def test_service_distill_and_promote_from_observed_batch_rename_case_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_batch_rename_case.json",
            {
                "task_description": "Rename all files in a directory to lowercase filenames.",
                "steps": [
                    {
                        "tool_name": "list_files",
                        "tool_input": {"path": "demo/rename_case_input", "pattern": "*.*"},
                        "observation": "Found files to rename.",
                        "status": "success",
                    },
                    {
                        "tool_name": "rename_path",
                        "tool_input": {
                            "source": "demo/rename_case_input/DraftOne.TXT",
                            "target": "demo/rename_case_input/draftone.txt",
                        },
                        "observation": "Renamed matching files to lowercase.",
                        "status": "success",
                    },
                ],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_batch_rename_case_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("batch_rename_case", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "filename_case", "pattern"),
        )

    def test_service_distill_and_promote_from_observed_batch_rename_source_destination_aliases_uses_rule_skill(
        self,
    ) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_batch_rename_source_destination_aliases.json",
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
                        "input": {"source": "demo/rename_input/a.txt", "destination": "demo/rename_input/done_a.txt"},
                        "result": "Renamed the matching file.",
                    },
                ],
                "outputs": ["demo/rename_input/done_a.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_batch_rename_source_destination_aliases_test",
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

    def test_service_distill_and_promote_from_observed_directory_json_transform_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_directory_json_transform.json",
            {
                "task": "Normalize matching JSON files from one directory into another directory.",
                "actions": [
                    {
                        "tool": "list_files",
                        "input": {"path": "demo/json_input", "pattern": "*.json"},
                        "result": "Found matching JSON files.",
                    },
                    {
                        "tool": "read_json",
                        "input": {"path": "demo/json_input/a.json"},
                        "result": "Read one JSON file.",
                    },
                    {
                        "tool": "write_json",
                        "input": {"path": "demo/json_output/a.json"},
                        "result": "Wrote one JSON file into the output directory.",
                    },
                ],
                "outputs": ["demo/json_output/a.json"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_directory_json_transform_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_json_transform", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern"),
        )

    def test_service_distill_and_promote_from_observed_directory_json_transform_with_prefix_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_directory_json_transform_prefix.json",
            {
                "task": "Normalize matching JSON files from one directory into another directory.",
                "actions": [
                    {
                        "tool": "list_files",
                        "input": {"path": "demo/json_input", "pattern": "*.json"},
                        "result": "Found matching JSON files.",
                    },
                    {
                        "tool": "read_json",
                        "input": {"path": "demo/json_input/a.json"},
                        "result": "Read one JSON file.",
                    },
                    {
                        "tool": "write_json",
                        "input": {"path": "demo/json_output/clean_a.json"},
                        "result": "Wrote one prefixed JSON file into the output directory.",
                    },
                ],
                "outputs": ["demo/json_output/clean_a.json"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_directory_json_transform_prefix_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_json_transform", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern", "prefix"),
        )

    def test_service_distill_and_promote_from_observed_directory_csv_to_json_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_directory_csv_to_json.json",
            {
                "task": "Convert matching CSV files in one directory into JSON files in another directory.",
                "actions": [
                    {
                        "tool": "list_files",
                        "input": {"path": "demo/csv_input", "pattern": "*.csv"},
                        "result": "Found matching CSV files.",
                    },
                    {
                        "tool": "read_text",
                        "input": {"path": "demo/csv_input/a.csv"},
                        "result": "Read one CSV file.",
                    },
                    {
                        "tool": "write_json",
                        "input": {"path": "demo/csv_output/a.json"},
                        "result": "Wrote one JSON file into the output directory.",
                    },
                ],
                "outputs": ["demo/csv_output/a.json"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_directory_csv_to_json_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_csv_to_json", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern"),
        )

    def test_service_distill_and_promote_from_observed_directory_csv_to_json_with_prefix_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_directory_csv_to_json_prefix.json",
            {
                "task": "Convert matching CSV files in one directory into JSON files in another directory.",
                "actions": [
                    {
                        "tool": "list_files",
                        "input": {"path": "demo/csv_input", "pattern": "*.csv"},
                        "result": "Found matching CSV files.",
                    },
                    {
                        "tool": "read_text",
                        "input": {"path": "demo/csv_input/a.csv"},
                        "result": "Read one CSV file.",
                    },
                    {
                        "tool": "write_json",
                        "input": {"path": "demo/csv_output/normalized_a.json"},
                        "result": "Wrote one prefixed JSON file into the output directory.",
                    },
                ],
                "outputs": ["demo/csv_output/normalized_a.json"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_directory_csv_to_json_prefix_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_csv_to_json", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern", "prefix"),
        )

    def test_service_distill_and_promote_from_observed_directory_json_to_csv_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_directory_json_to_csv.json",
            {
                "task": "Convert matching JSON files in one directory into CSV files in another directory.",
                "actions": [
                    {
                        "tool": "list_files",
                        "input": {"path": "demo/json_input", "pattern": "*.json"},
                        "result": "Found matching JSON files.",
                    },
                    {
                        "tool": "read_json",
                        "input": {"path": "demo/json_input/a.json"},
                        "result": "Read one JSON file.",
                    },
                    {
                        "tool": "write_text",
                        "input": {"path": "demo/json_output/a.csv"},
                        "result": "Wrote one CSV file into the output directory.",
                    },
                ],
                "outputs": ["demo/json_output/a.csv"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_directory_json_to_csv_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_json_to_csv", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern"),
        )

    def test_service_distill_and_promote_from_observed_directory_json_to_csv_with_suffix_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_directory_json_to_csv_suffix.json",
            {
                "task": "Convert matching JSON files in one directory into CSV files in another directory.",
                "actions": [
                    {
                        "tool": "list_files",
                        "input": {"path": "demo/json_input", "pattern": "*.json"},
                        "result": "Found matching JSON files.",
                    },
                    {
                        "tool": "read_json",
                        "input": {"path": "demo/json_input/a.json"},
                        "result": "Read one JSON file.",
                    },
                    {
                        "tool": "write_text",
                        "input": {"path": "demo/json_output/a_export.csv"},
                        "result": "Wrote one suffixed CSV file into the output directory.",
                    },
                ],
                "outputs": ["demo/json_output/a_export.csv"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_directory_json_to_csv_suffix_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_json_to_csv", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern", "suffix"),
        )

    def test_service_distill_and_promote_from_observed_directory_text_transform_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_directory_text_transform.json",
            {
                "task": "Normalize matching text files from one directory into another directory.",
                "actions": [
                    {
                        "tool": "list_files",
                        "input": {"path": "demo/text_input", "pattern": "*.txt"},
                        "result": "Found matching text files.",
                    },
                    {
                        "tool": "read_text",
                        "input": {"path": "demo/text_input/a.txt"},
                        "result": "Read one text file.",
                    },
                    {
                        "tool": "write_text",
                        "input": {"path": "demo/text_output/a.txt"},
                        "result": "Wrote one normalized text file into the output directory.",
                    },
                ],
                "outputs": ["demo/text_output/a.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_directory_text_transform_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_text_transform", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern"),
        )

    def test_service_distill_and_promote_from_observed_directory_text_transform_with_suffix_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_directory_text_transform_suffix.json",
            {
                "task": "Normalize matching text files from one directory into another directory.",
                "actions": [
                    {
                        "tool": "list_files",
                        "input": {"path": "demo/text_input", "pattern": "*.txt"},
                        "result": "Found matching text files.",
                    },
                    {
                        "tool": "read_text",
                        "input": {"path": "demo/text_input/a.txt"},
                        "result": "Read one text file.",
                    },
                    {
                        "tool": "write_text",
                        "input": {"path": "demo/text_output/a_done.txt"},
                        "result": "Wrote one suffixed text file into the output directory.",
                    },
                ],
                "outputs": ["demo/text_output/a_done.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_directory_text_transform_suffix_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_text_transform", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern", "suffix"),
        )

    def test_service_distill_and_promote_from_observed_directory_text_transform_with_newline_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        observed_path = self._write_json_file(
            sandbox_root / "demo" / "observed_directory_text_transform_newline.json",
            {
                "task": "Normalize matching text files from one directory into another directory.",
                "actions": [
                    {
                        "tool": "list_files",
                        "input": {"path": "demo/text_input", "pattern": "*.txt"},
                        "result": "Found matching text files.",
                    },
                    {
                        "tool": "read_text",
                        "input": {"path": "demo/text_input/a.txt"},
                        "result": "Read one text file.",
                    },
                    {
                        "tool": "write_text",
                        "input": {"path": "demo/text_output/a.txt", "newline": "\n"},
                        "result": "Wrote one normalized text file with LF endings.",
                    },
                ],
                "outputs": ["demo/text_output/a.txt"],
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="observed_directory_text_transform_newline_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_text_transform", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern", "newline"),
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

    def test_service_distill_and_promote_from_execute_observed_task_with_newline_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, _ = self._make_runtime_sandbox()
        execute_result = sandbox_service.execute(
            "merge_text_files",
            {
                "input_dir": "demo/input",
                "output_path": "demo/output/execute_roundtrip_merge_crlf.md",
                "newline": "\n",
            },
        )
        observed_path = execute_result["observed_task_record"]

        result = sandbox_service.distill_and_promote(
            observed_task_path=observed_path,
            skill_name="execute_observed_roundtrip_newline_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertIsNotNone(result["capture"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("text_merge", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_path", "pattern", "newline"),
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

    def test_service_distill_and_promote_from_execute_directory_move_with_nested_subdirs_observed_task_uses_rule_skill(
        self,
    ) -> None:
        sandbox_root, sandbox_service, sandbox_index = self._make_runtime_sandbox()
        input_dir = sandbox_root / "demo" / "move_exec_nested_input"
        nested_dir = input_dir / "nested"
        output_dir = sandbox_root / "demo" / "move_exec_nested_output"
        nested_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (nested_dir / "a.log").write_text("alpha\n", encoding="utf-8")

        trajectory = Trajectory(
            task_id="execute_directory_move_nested_roundtrip_demo",
            session_id="session_execute_directory_move_nested_roundtrip",
            task_description="Move matching log files from one directory into another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/move_exec_nested_input", "pattern": "**/*.log"},
                    observation="Found nested log files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="move_file",
                    tool_input={"source_path": "demo/move_exec_nested_input/nested/a.log", "target_path": "demo/move_exec_nested_output/nested/a.log"},
                    observation="Moved one nested log file.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-27T01:30:00",
            ended_at="2026-04-27T01:31:00",
        )
        self._generate_and_activate_skill(
            trajectory,
            skill_name="execute_directory_move_nested_roundtrip_skill",
            root=sandbox_root,
            index=sandbox_index,
        )

        execute_result = sandbox_service.execute(
            "execute_directory_move_nested_roundtrip_skill",
            {"input_dir": "demo/move_exec_nested_input", "output_dir": "demo/move_exec_nested_output", "pattern": "**/*.log"},
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=execute_result["observed_task_record"],
            skill_name="execute_directory_move_nested_roundtrip_test",
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

    def test_service_distill_and_promote_from_execute_directory_copy_with_nested_subdirs_observed_task_uses_rule_skill(
        self,
    ) -> None:
        sandbox_root, sandbox_service, sandbox_index = self._make_runtime_sandbox()
        input_dir = sandbox_root / "demo" / "copy_exec_nested_input"
        nested_dir = input_dir / "nested"
        output_dir = sandbox_root / "demo" / "copy_exec_nested_output"
        nested_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (nested_dir / "a.txt").write_text("alpha\n", encoding="utf-8")

        trajectory = Trajectory(
            task_id="execute_directory_copy_nested_roundtrip_demo",
            session_id="session_execute_directory_copy_nested_roundtrip",
            task_description="Copy matching txt files from one directory into another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/copy_exec_nested_input", "pattern": "**/*.txt"},
                    observation="Found nested txt files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="copy_file",
                    tool_input={"source_path": "demo/copy_exec_nested_input/nested/a.txt", "target_path": "demo/copy_exec_nested_output/nested/a.txt"},
                    observation="Copied one nested txt file.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-27T01:32:00",
            ended_at="2026-04-27T01:33:00",
        )
        self._generate_and_activate_skill(
            trajectory,
            skill_name="execute_directory_copy_nested_roundtrip_skill",
            root=sandbox_root,
            index=sandbox_index,
        )

        execute_result = sandbox_service.execute(
            "execute_directory_copy_nested_roundtrip_skill",
            {"input_dir": "demo/copy_exec_nested_input", "output_dir": "demo/copy_exec_nested_output", "pattern": "**/*.txt"},
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=execute_result["observed_task_record"],
            skill_name="execute_directory_copy_nested_roundtrip_test",
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

    def test_service_distill_and_promote_from_execute_directory_text_replace_observed_task_uses_rule_skill(self) -> None:
        sandbox_root, sandbox_service, sandbox_index = self._make_runtime_sandbox()
        input_dir = sandbox_root / "demo" / "replace_input"
        output_dir = sandbox_root / "demo" / "replace_output"
        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (input_dir / "a.txt").write_text("hello alpha\n", encoding="utf-8")
        (input_dir / "b.txt").write_text("hello beta\n", encoding="utf-8")

        trajectory = Trajectory(
            task_id="execute_directory_text_replace_roundtrip_demo",
            session_id="session_execute_directory_text_replace_roundtrip",
            task_description="Replace one string with another across all txt files in a directory and write outputs to another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/replace_input", "pattern": "*.txt"},
                    observation="Found matching txt files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_text",
                    tool_input={"path": "demo/replace_input/a.txt", "old_text": "hello", "new_text": "hi"},
                    observation="Read one text file for replacement.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_text",
                    tool_input={"path": "demo/replace_output/a.txt"},
                    observation="Wrote one replaced text file.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T14:05:00",
            ended_at="2026-04-26T14:06:00",
        )
        self._generate_and_activate_skill(
            trajectory,
            skill_name="execute_directory_text_replace_roundtrip_skill",
            root=sandbox_root,
            index=sandbox_index,
        )

        execute_result = sandbox_service.execute(
            "execute_directory_text_replace_roundtrip_skill",
            {
                "input_dir": "demo/replace_input",
                "output_dir": "demo/replace_output",
                "pattern": "*.txt",
                "old_text": "hello",
                "new_text": "hi",
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=execute_result["observed_task_record"],
            skill_name="execute_directory_text_replace_roundtrip_test",
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

    def test_service_distill_and_promote_from_execute_directory_text_replace_with_nested_subdirs_observed_task_uses_rule_skill(
        self,
    ) -> None:
        sandbox_root, sandbox_service, sandbox_index = self._make_runtime_sandbox()
        input_dir = sandbox_root / "demo" / "replace_exec_nested_input"
        nested_dir = input_dir / "nested"
        output_dir = sandbox_root / "demo" / "replace_exec_nested_output"
        nested_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (nested_dir / "a.txt").write_text("hello alpha\n", encoding="utf-8")

        trajectory = Trajectory(
            task_id="execute_directory_text_replace_nested_roundtrip_demo",
            session_id="session_execute_directory_text_replace_nested_roundtrip",
            task_description="Replace one string with another across all txt files in a directory and write outputs to another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/replace_exec_nested_input", "pattern": "**/*.txt"},
                    observation="Found nested txt files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_text",
                    tool_input={"path": "demo/replace_exec_nested_input/nested/a.txt", "old_text": "hello", "new_text": "hi"},
                    observation="Read one nested text file for replacement.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_text",
                    tool_input={"path": "demo/replace_exec_nested_output/nested/a.txt"},
                    observation="Wrote one nested replaced text file.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-27T01:34:00",
            ended_at="2026-04-27T01:35:00",
        )
        self._generate_and_activate_skill(
            trajectory,
            skill_name="execute_directory_text_replace_nested_roundtrip_skill",
            root=sandbox_root,
            index=sandbox_index,
        )

        execute_result = sandbox_service.execute(
            "execute_directory_text_replace_nested_roundtrip_skill",
            {"input_dir": "demo/replace_exec_nested_input", "output_dir": "demo/replace_exec_nested_output", "pattern": "**/*.txt", "old_text": "hello", "new_text": "hi"},
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=execute_result["observed_task_record"],
            skill_name="execute_directory_text_replace_nested_roundtrip_test",
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

    def test_service_distill_and_promote_from_execute_directory_text_replace_with_newline_observed_task_uses_rule_skill(
        self,
    ) -> None:
        sandbox_root, sandbox_service, sandbox_index = self._make_runtime_sandbox()
        input_dir = sandbox_root / "demo" / "replace_newline_input"
        output_dir = sandbox_root / "demo" / "replace_newline_output"
        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (input_dir / "a.txt").write_text("hello alpha\n", encoding="utf-8")
        (input_dir / "b.txt").write_text("hello beta\n", encoding="utf-8")

        trajectory = Trajectory(
            task_id="execute_directory_text_replace_newline_roundtrip_demo",
            session_id="session_execute_directory_text_replace_newline_roundtrip",
            task_description="Replace one string with another across all txt files in a directory and write outputs to another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/replace_newline_input", "pattern": "*.txt"},
                    observation="Found matching txt files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_text",
                    tool_input={"path": "demo/replace_newline_input/a.txt", "old_text": "hello", "new_text": "hi"},
                    observation="Read one text file for replacement.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_text",
                    tool_input={"path": "demo/replace_newline_output/a.txt", "newline": "\n"},
                    observation="Wrote one replaced text file with LF endings.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T22:20:00",
            ended_at="2026-04-26T22:21:00",
        )
        self._generate_and_activate_skill(
            trajectory,
            skill_name="execute_directory_text_replace_newline_roundtrip_skill",
            root=sandbox_root,
            index=sandbox_index,
        )

        execute_result = sandbox_service.execute(
            "execute_directory_text_replace_newline_roundtrip_skill",
            {
                "input_dir": "demo/replace_newline_input",
                "output_dir": "demo/replace_newline_output",
                "pattern": "*.txt",
                "old_text": "hello",
                "new_text": "hi",
                "newline": "\n",
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=execute_result["observed_task_record"],
            skill_name="execute_directory_text_replace_newline_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_text_replace", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "old_text", "new_text", "pattern", "newline"),
        )

    def test_service_distill_and_promote_from_execute_directory_text_replace_with_prefix_observed_task_uses_rule_skill(
        self,
    ) -> None:
        sandbox_root, sandbox_service, sandbox_index = self._make_runtime_sandbox()
        input_dir = sandbox_root / "demo" / "replace_prefix_exec_input"
        output_dir = sandbox_root / "demo" / "replace_prefix_exec_output"
        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (input_dir / "a.txt").write_text("hello alpha\n", encoding="utf-8")
        (input_dir / "b.txt").write_text("hello beta\n", encoding="utf-8")

        trajectory = Trajectory(
            task_id="execute_directory_text_replace_prefix_roundtrip_demo",
            session_id="session_execute_directory_text_replace_prefix_roundtrip",
            task_description="Replace one string with another across all txt files in a directory and write outputs to another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/replace_prefix_exec_input", "pattern": "*.txt"},
                    observation="Found matching txt files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_text",
                    tool_input={"path": "demo/replace_prefix_exec_input/a.txt", "old_text": "hello", "new_text": "hi"},
                    observation="Read one text file for replacement.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_text",
                    tool_input={"path": "demo/replace_prefix_exec_output/done_a.txt"},
                    observation="Wrote one prefixed replaced text file.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T23:04:00",
            ended_at="2026-04-26T23:05:00",
        )
        self._generate_and_activate_skill(
            trajectory,
            skill_name="execute_directory_text_replace_prefix_roundtrip_skill",
            root=sandbox_root,
            index=sandbox_index,
        )

        execute_result = sandbox_service.execute(
            "execute_directory_text_replace_prefix_roundtrip_skill",
            {
                "input_dir": "demo/replace_prefix_exec_input",
                "output_dir": "demo/replace_prefix_exec_output",
                "pattern": "*.txt",
                "old_text": "hello",
                "new_text": "hi",
                "prefix": "done_",
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=execute_result["observed_task_record"],
            skill_name="execute_directory_text_replace_prefix_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_text_replace", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "old_text", "new_text", "pattern", "prefix"),
        )

    def test_service_distill_and_promote_from_execute_directory_text_replace_with_suffix_observed_task_uses_rule_skill(
        self,
    ) -> None:
        sandbox_root, sandbox_service, sandbox_index = self._make_runtime_sandbox()
        input_dir = sandbox_root / "demo" / "replace_suffix_exec_input"
        output_dir = sandbox_root / "demo" / "replace_suffix_exec_output"
        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (input_dir / "a.txt").write_text("hello alpha\n", encoding="utf-8")
        (input_dir / "b.txt").write_text("hello beta\n", encoding="utf-8")

        trajectory = Trajectory(
            task_id="execute_directory_text_replace_suffix_roundtrip_demo",
            session_id="session_execute_directory_text_replace_suffix_roundtrip",
            task_description="Replace one string with another across all txt files in a directory and write outputs to another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/replace_suffix_exec_input", "pattern": "*.txt"},
                    observation="Found matching txt files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_text",
                    tool_input={"path": "demo/replace_suffix_exec_input/a.txt", "old_text": "hello", "new_text": "hi"},
                    observation="Read one text file for replacement.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_text",
                    tool_input={"path": "demo/replace_suffix_exec_output/a_done.txt"},
                    observation="Wrote one suffixed replaced text file.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T23:06:00",
            ended_at="2026-04-26T23:07:00",
        )
        self._generate_and_activate_skill(
            trajectory,
            skill_name="execute_directory_text_replace_suffix_roundtrip_skill",
            root=sandbox_root,
            index=sandbox_index,
        )

        execute_result = sandbox_service.execute(
            "execute_directory_text_replace_suffix_roundtrip_skill",
            {
                "input_dir": "demo/replace_suffix_exec_input",
                "output_dir": "demo/replace_suffix_exec_output",
                "pattern": "*.txt",
                "old_text": "hello",
                "new_text": "hi",
                "suffix": "_done",
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=execute_result["observed_task_record"],
            skill_name="execute_directory_text_replace_suffix_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_text_replace", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "old_text", "new_text", "pattern", "suffix"),
        )

    def test_service_distill_and_promote_from_execute_directory_copy_with_prefix_observed_task_uses_rule_skill(
        self,
    ) -> None:
        sandbox_root, sandbox_service, sandbox_index = self._make_runtime_sandbox()
        input_dir = sandbox_root / "demo" / "copy_prefix_exec_input"
        output_dir = sandbox_root / "demo" / "copy_prefix_exec_output"
        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (input_dir / "a.txt").write_text("alpha\n", encoding="utf-8")
        (input_dir / "b.txt").write_text("beta\n", encoding="utf-8")

        trajectory = Trajectory(
            task_id="execute_directory_copy_prefix_roundtrip_demo",
            session_id="session_execute_directory_copy_prefix_roundtrip",
            task_description="Copy matching txt files from one directory into another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/copy_prefix_exec_input", "pattern": "*.txt"},
                    observation="Found matching txt files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="copy_file",
                    tool_input={
                        "source_path": "demo/copy_prefix_exec_input/a.txt",
                        "target_path": "demo/copy_prefix_exec_output/done_a.txt",
                    },
                    observation="Copied one prefixed txt file into the output directory.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-27T00:20:00",
            ended_at="2026-04-27T00:21:00",
        )
        self._generate_and_activate_skill(
            trajectory,
            skill_name="execute_directory_copy_prefix_roundtrip_skill",
            root=sandbox_root,
            index=sandbox_index,
        )

        execute_result = sandbox_service.execute(
            "execute_directory_copy_prefix_roundtrip_skill",
            {
                "input_dir": "demo/copy_prefix_exec_input",
                "output_dir": "demo/copy_prefix_exec_output",
                "pattern": "*.txt",
                "prefix": "done_",
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=execute_result["observed_task_record"],
            skill_name="execute_directory_copy_prefix_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_copy", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern", "prefix"),
        )

    def test_service_distill_and_promote_from_execute_directory_move_with_suffix_observed_task_uses_rule_skill(
        self,
    ) -> None:
        sandbox_root, sandbox_service, sandbox_index = self._make_runtime_sandbox()
        input_dir = sandbox_root / "demo" / "move_suffix_exec_input"
        output_dir = sandbox_root / "demo" / "move_suffix_exec_output"
        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (input_dir / "a.log").write_text("alpha\n", encoding="utf-8")
        (input_dir / "b.log").write_text("beta\n", encoding="utf-8")

        trajectory = Trajectory(
            task_id="execute_directory_move_suffix_roundtrip_demo",
            session_id="session_execute_directory_move_suffix_roundtrip",
            task_description="Move matching log files from one directory into another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/move_suffix_exec_input", "pattern": "*.log"},
                    observation="Found matching log files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="move_file",
                    tool_input={
                        "source_path": "demo/move_suffix_exec_input/a.log",
                        "target_path": "demo/move_suffix_exec_output/a_done.log",
                    },
                    observation="Moved one suffixed log file into the output directory.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-27T00:22:00",
            ended_at="2026-04-27T00:23:00",
        )
        self._generate_and_activate_skill(
            trajectory,
            skill_name="execute_directory_move_suffix_roundtrip_skill",
            root=sandbox_root,
            index=sandbox_index,
        )

        execute_result = sandbox_service.execute(
            "execute_directory_move_suffix_roundtrip_skill",
            {
                "input_dir": "demo/move_suffix_exec_input",
                "output_dir": "demo/move_suffix_exec_output",
                "pattern": "*.log",
                "suffix": "_done",
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=execute_result["observed_task_record"],
            skill_name="execute_directory_move_suffix_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_move", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern", "suffix"),
        )

    def test_service_distill_and_promote_from_execute_directory_json_transform_observed_task_uses_rule_skill(
        self,
    ) -> None:
        sandbox_root, sandbox_service, sandbox_index = self._make_runtime_sandbox()
        input_dir = sandbox_root / "demo" / "json_exec_input"
        output_dir = sandbox_root / "demo" / "json_exec_output"
        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (input_dir / "a.json").write_text(__import__("json").dumps({"name": "alice"}), encoding="utf-8")
        (input_dir / "b.json").write_text(__import__("json").dumps({"name": "bob"}), encoding="utf-8")

        trajectory = Trajectory(
            task_id="execute_directory_json_transform_roundtrip_demo",
            session_id="session_execute_directory_json_transform_roundtrip",
            task_description="Normalize matching JSON files from one directory into another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/json_exec_input", "pattern": "*.json"},
                    observation="Found matching JSON files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_json",
                    tool_input={"path": "demo/json_exec_input/a.json"},
                    observation="Read one JSON file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_json",
                    tool_input={"path": "demo/json_exec_output/a.json"},
                    observation="Wrote one JSON file into the output directory.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T14:07:00",
            ended_at="2026-04-26T14:08:00",
        )
        self._generate_and_activate_skill(
            trajectory,
            skill_name="execute_directory_json_transform_roundtrip_skill",
            root=sandbox_root,
            index=sandbox_index,
        )

        execute_result = sandbox_service.execute(
            "execute_directory_json_transform_roundtrip_skill",
            {
                "input_dir": "demo/json_exec_input",
                "output_dir": "demo/json_exec_output",
                "pattern": "*.json",
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=execute_result["observed_task_record"],
            skill_name="execute_directory_json_transform_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_json_transform", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern"),
        )

    def test_service_distill_and_promote_from_execute_directory_json_transform_with_nested_subdirs_observed_task_uses_rule_skill(
        self,
    ) -> None:
        sandbox_root, sandbox_service, sandbox_index = self._make_runtime_sandbox()
        input_dir = sandbox_root / "demo" / "json_exec_nested_input"
        nested_dir = input_dir / "nested"
        output_dir = sandbox_root / "demo" / "json_exec_nested_output"
        nested_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (nested_dir / "a.json").write_text(__import__("json").dumps({"name": "alice"}), encoding="utf-8")

        trajectory = Trajectory(
            task_id="execute_directory_json_transform_nested_roundtrip_demo",
            session_id="session_execute_directory_json_transform_nested_roundtrip",
            task_description="Normalize matching JSON files from one directory into another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/json_exec_nested_input", "pattern": "**/*.json"},
                    observation="Found nested JSON files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_json",
                    tool_input={"path": "demo/json_exec_nested_input/nested/a.json"},
                    observation="Read one nested JSON file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_json",
                    tool_input={"path": "demo/json_exec_nested_output/nested/a.json"},
                    observation="Wrote one nested JSON file.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-27T01:36:00",
            ended_at="2026-04-27T01:37:00",
        )
        self._generate_and_activate_skill(
            trajectory,
            skill_name="execute_directory_json_transform_nested_roundtrip_skill",
            root=sandbox_root,
            index=sandbox_index,
        )

        execute_result = sandbox_service.execute(
            "execute_directory_json_transform_nested_roundtrip_skill",
            {"input_dir": "demo/json_exec_nested_input", "output_dir": "demo/json_exec_nested_output", "pattern": "**/*.json"},
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=execute_result["observed_task_record"],
            skill_name="execute_directory_json_transform_nested_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_json_transform", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern"),
        )

    def test_service_distill_and_promote_from_execute_directory_json_transform_with_prefix_observed_task_uses_rule_skill(
        self,
    ) -> None:
        sandbox_root, sandbox_service, sandbox_index = self._make_runtime_sandbox()
        input_dir = sandbox_root / "demo" / "json_exec_prefix_input"
        output_dir = sandbox_root / "demo" / "json_exec_prefix_output"
        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (input_dir / "a.json").write_text(__import__("json").dumps({"name": "alice"}), encoding="utf-8")
        (input_dir / "b.json").write_text(__import__("json").dumps({"name": "bob"}), encoding="utf-8")

        trajectory = Trajectory(
            task_id="execute_directory_json_transform_prefix_roundtrip_demo",
            session_id="session_execute_directory_json_transform_prefix_roundtrip",
            task_description="Normalize matching JSON files from one directory into another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/json_exec_prefix_input", "pattern": "*.json"},
                    observation="Found matching JSON files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_json",
                    tool_input={"path": "demo/json_exec_prefix_input/a.json"},
                    observation="Read one JSON file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_json",
                    tool_input={"path": "demo/json_exec_prefix_output/clean_a.json"},
                    observation="Wrote one prefixed JSON file into the output directory.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T22:40:00",
            ended_at="2026-04-26T22:41:00",
        )
        self._generate_and_activate_skill(
            trajectory,
            skill_name="execute_directory_json_transform_prefix_roundtrip_skill",
            root=sandbox_root,
            index=sandbox_index,
        )

        execute_result = sandbox_service.execute(
            "execute_directory_json_transform_prefix_roundtrip_skill",
            {
                "input_dir": "demo/json_exec_prefix_input",
                "output_dir": "demo/json_exec_prefix_output",
                "pattern": "*.json",
                "prefix": "clean_",
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=execute_result["observed_task_record"],
            skill_name="execute_directory_json_transform_prefix_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_json_transform", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern", "prefix"),
        )

    def test_service_distill_and_promote_from_execute_directory_json_transform_with_formatting_observed_task_uses_rule_skill(
        self,
    ) -> None:
        sandbox_root, sandbox_service, sandbox_index = self._make_runtime_sandbox()
        input_dir = sandbox_root / "demo" / "json_exec_format_input"
        output_dir = sandbox_root / "demo" / "json_exec_format_output"
        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (input_dir / "a.json").write_text(__import__("json").dumps({"name": "中文"}, ensure_ascii=False), encoding="utf-8")
        (input_dir / "b.json").write_text(__import__("json").dumps({"name": "内容"}, ensure_ascii=False), encoding="utf-8")

        trajectory = Trajectory(
            task_id="execute_directory_json_transform_format_roundtrip_demo",
            session_id="session_execute_directory_json_transform_format_roundtrip",
            task_description="Normalize matching JSON files from one directory into another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/json_exec_format_input", "pattern": "*.json"},
                    observation="Found matching JSON files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_json",
                    tool_input={"path": "demo/json_exec_format_input/a.json"},
                    observation="Read one JSON file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_json",
                    tool_input={"path": "demo/json_exec_format_output/a.json", "ensure_ascii": False, "indent": 4},
                    observation="Wrote formatted JSON output.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T16:24:00",
            ended_at="2026-04-26T16:25:00",
        )
        self._generate_and_activate_skill(
            trajectory,
            skill_name="execute_directory_json_transform_format_roundtrip_skill",
            root=sandbox_root,
            index=sandbox_index,
        )

        execute_result = sandbox_service.execute(
            "execute_directory_json_transform_format_roundtrip_skill",
            {
                "input_dir": "demo/json_exec_format_input",
                "output_dir": "demo/json_exec_format_output",
                "pattern": "*.json",
                "ensure_ascii": False,
                "indent": 4,
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=execute_result["observed_task_record"],
            skill_name="execute_directory_json_transform_format_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_json_transform", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern", "ensure_ascii", "indent"),
        )

    def test_service_distill_and_promote_from_execute_directory_json_transform_with_sort_keys_observed_task_uses_rule_skill(
        self,
    ) -> None:
        sandbox_root, sandbox_service, sandbox_index = self._make_runtime_sandbox()
        input_dir = sandbox_root / "demo" / "json_exec_sort_input"
        output_dir = sandbox_root / "demo" / "json_exec_sort_output"
        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (input_dir / "a.json").write_text('{"name":"alice","age":30}', encoding="utf-8")
        (input_dir / "b.json").write_text('{"name":"bob","age":31}', encoding="utf-8")

        trajectory = Trajectory(
            task_id="execute_directory_json_transform_sort_roundtrip_demo",
            session_id="session_execute_directory_json_transform_sort_roundtrip",
            task_description="Normalize matching JSON files from one directory into another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/json_exec_sort_input", "pattern": "*.json"},
                    observation="Found matching JSON files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_json",
                    tool_input={"path": "demo/json_exec_sort_input/a.json"},
                    observation="Read one JSON file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_json",
                    tool_input={"path": "demo/json_exec_sort_output/a.json", "sort_keys": True},
                    observation="Wrote sorted JSON output.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T21:40:00",
            ended_at="2026-04-26T21:41:00",
        )
        self._generate_and_activate_skill(
            trajectory,
            skill_name="execute_directory_json_transform_sort_roundtrip_skill",
            root=sandbox_root,
            index=sandbox_index,
        )

        execute_result = sandbox_service.execute(
            "execute_directory_json_transform_sort_roundtrip_skill",
            {
                "input_dir": "demo/json_exec_sort_input",
                "output_dir": "demo/json_exec_sort_output",
                "pattern": "*.json",
                "sort_keys": True,
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=execute_result["observed_task_record"],
            skill_name="execute_directory_json_transform_sort_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_json_transform", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern", "sort_keys"),
        )

    def test_service_distill_and_promote_from_execute_directory_csv_to_json_observed_task_uses_rule_skill(
        self,
    ) -> None:
        sandbox_root, sandbox_service, sandbox_index = self._make_runtime_sandbox()
        input_dir = sandbox_root / "demo" / "csv_exec_input"
        output_dir = sandbox_root / "demo" / "csv_exec_output"
        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (input_dir / "a.csv").write_text("name,age\nalice,30\n", encoding="utf-8")
        (input_dir / "b.csv").write_text("name,age\nbob,31\n", encoding="utf-8")

        trajectory = Trajectory(
            task_id="execute_directory_csv_to_json_roundtrip_demo",
            session_id="session_execute_directory_csv_to_json_roundtrip",
            task_description="Convert matching CSV files in one directory into JSON files in another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/csv_exec_input", "pattern": "*.csv"},
                    observation="Found matching CSV files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_text",
                    tool_input={"path": "demo/csv_exec_input/a.csv"},
                    observation="Read one CSV file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_json",
                    tool_input={"path": "demo/csv_exec_output/a.json"},
                    observation="Wrote one JSON file into the output directory.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T14:14:00",
            ended_at="2026-04-26T14:15:00",
        )
        self._generate_and_activate_skill(
            trajectory,
            skill_name="execute_directory_csv_to_json_roundtrip_skill",
            root=sandbox_root,
            index=sandbox_index,
        )

        execute_result = sandbox_service.execute(
            "execute_directory_csv_to_json_roundtrip_skill",
            {
                "input_dir": "demo/csv_exec_input",
                "output_dir": "demo/csv_exec_output",
                "pattern": "*.csv",
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=execute_result["observed_task_record"],
            skill_name="execute_directory_csv_to_json_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_csv_to_json", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern"),
        )

    def test_service_distill_and_promote_from_execute_directory_csv_to_json_with_prefix_observed_task_uses_rule_skill(
        self,
    ) -> None:
        sandbox_root, sandbox_service, sandbox_index = self._make_runtime_sandbox()
        input_dir = sandbox_root / "demo" / "csv_exec_prefix_input"
        output_dir = sandbox_root / "demo" / "csv_exec_prefix_output"
        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (input_dir / "a.csv").write_text("name,age\nalice,30\n", encoding="utf-8")
        (input_dir / "b.csv").write_text("name,age\nbob,31\n", encoding="utf-8")

        trajectory = Trajectory(
            task_id="execute_directory_csv_to_json_prefix_roundtrip_demo",
            session_id="session_execute_directory_csv_to_json_prefix_roundtrip",
            task_description="Convert matching CSV files in one directory into JSON files in another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/csv_exec_prefix_input", "pattern": "*.csv"},
                    observation="Found matching CSV files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_text",
                    tool_input={"path": "demo/csv_exec_prefix_input/a.csv"},
                    observation="Read one CSV file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_json",
                    tool_input={"path": "demo/csv_exec_prefix_output/normalized_a.json"},
                    observation="Wrote one prefixed JSON file into the output directory.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T22:42:00",
            ended_at="2026-04-26T22:43:00",
        )
        self._generate_and_activate_skill(
            trajectory,
            skill_name="execute_directory_csv_to_json_prefix_roundtrip_skill",
            root=sandbox_root,
            index=sandbox_index,
        )

        execute_result = sandbox_service.execute(
            "execute_directory_csv_to_json_prefix_roundtrip_skill",
            {
                "input_dir": "demo/csv_exec_prefix_input",
                "output_dir": "demo/csv_exec_prefix_output",
                "pattern": "*.csv",
                "prefix": "normalized_",
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=execute_result["observed_task_record"],
            skill_name="execute_directory_csv_to_json_prefix_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_csv_to_json", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern", "prefix"),
        )

    def test_service_distill_and_promote_from_execute_directory_csv_to_json_with_nested_subdirs_observed_task_uses_rule_skill(
        self,
    ) -> None:
        sandbox_root, sandbox_service, sandbox_index = self._make_runtime_sandbox()
        input_dir = sandbox_root / "demo" / "csv_exec_nested_input"
        nested_dir = input_dir / "nested"
        output_dir = sandbox_root / "demo" / "csv_exec_nested_output"
        nested_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (nested_dir / "a.csv").write_text("name,age\nalice,30\n", encoding="utf-8")

        trajectory = Trajectory(
            task_id="execute_directory_csv_to_json_nested_roundtrip_demo",
            session_id="session_execute_directory_csv_to_json_nested_roundtrip",
            task_description="Convert matching CSV files in one directory into JSON files in another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/csv_exec_nested_input", "pattern": "**/*.csv"},
                    observation="Found nested CSV files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_text",
                    tool_input={"path": "demo/csv_exec_nested_input/nested/a.csv"},
                    observation="Read one nested CSV file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_json",
                    tool_input={"path": "demo/csv_exec_nested_output/nested/a.json"},
                    observation="Wrote one nested JSON file.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-27T01:10:00",
            ended_at="2026-04-27T01:11:00",
        )
        self._generate_and_activate_skill(
            trajectory,
            skill_name="execute_directory_csv_to_json_nested_roundtrip_skill",
            root=sandbox_root,
            index=sandbox_index,
        )

        execute_result = sandbox_service.execute(
            "execute_directory_csv_to_json_nested_roundtrip_skill",
            {
                "input_dir": "demo/csv_exec_nested_input",
                "output_dir": "demo/csv_exec_nested_output",
                "pattern": "**/*.csv",
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=execute_result["observed_task_record"],
            skill_name="execute_directory_csv_to_json_nested_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_csv_to_json", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern"),
        )

    def test_service_distill_and_promote_from_execute_directory_csv_to_json_with_formatting_observed_task_uses_rule_skill(
        self,
    ) -> None:
        sandbox_root, sandbox_service, sandbox_index = self._make_runtime_sandbox()
        input_dir = sandbox_root / "demo" / "csv_exec_format_input"
        output_dir = sandbox_root / "demo" / "csv_exec_format_output"
        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (input_dir / "a.csv").write_text("name,city\nalice,中文\n", encoding="utf-8")
        (input_dir / "b.csv").write_text("name,city\nbob,内容\n", encoding="utf-8")

        trajectory = Trajectory(
            task_id="execute_directory_csv_to_json_format_roundtrip_demo",
            session_id="session_execute_directory_csv_to_json_format_roundtrip",
            task_description="Convert matching CSV files in one directory into JSON files in another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/csv_exec_format_input", "pattern": "*.csv"},
                    observation="Found matching CSV files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_text",
                    tool_input={"path": "demo/csv_exec_format_input/a.csv"},
                    observation="Read one CSV file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_json",
                    tool_input={"path": "demo/csv_exec_format_output/a.json", "ensure_ascii": False, "indent": 4},
                    observation="Wrote formatted JSON output.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T16:34:00",
            ended_at="2026-04-26T16:35:00",
        )
        self._generate_and_activate_skill(
            trajectory,
            skill_name="execute_directory_csv_to_json_format_roundtrip_skill",
            root=sandbox_root,
            index=sandbox_index,
        )

        execute_result = sandbox_service.execute(
            "execute_directory_csv_to_json_format_roundtrip_skill",
            {
                "input_dir": "demo/csv_exec_format_input",
                "output_dir": "demo/csv_exec_format_output",
                "pattern": "*.csv",
                "ensure_ascii": False,
                "indent": 4,
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=execute_result["observed_task_record"],
            skill_name="execute_directory_csv_to_json_format_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_csv_to_json", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern", "ensure_ascii", "indent"),
        )

    def test_service_distill_and_promote_from_execute_directory_csv_to_json_with_reader_formatting_observed_task_uses_rule_skill(
        self,
    ) -> None:
        sandbox_root, sandbox_service, sandbox_index = self._make_runtime_sandbox()
        input_dir = sandbox_root / "demo" / "csv_exec_reader_format_input"
        output_dir = sandbox_root / "demo" / "csv_exec_reader_format_output"
        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (input_dir / "a.csv").write_text("'name','city'\n'alice\\'s','中文'\n", encoding="utf-8")
        (input_dir / "b.csv").write_text("'name','city'\n'bob\\'s','内容'\n", encoding="utf-8")

        trajectory = Trajectory(
            task_id="execute_directory_csv_to_json_reader_format_roundtrip_demo",
            session_id="session_execute_directory_csv_to_json_reader_format_roundtrip",
            task_description="Convert matching CSV files in one directory into JSON files in another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/csv_exec_reader_format_input", "pattern": "*.csv"},
                    observation="Found matching CSV files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_text",
                    tool_input={
                        "path": "demo/csv_exec_reader_format_input/a.csv",
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
                    tool_input={"path": "demo/csv_exec_reader_format_output/a.json", "ensure_ascii": False, "indent": 4},
                    observation="Wrote formatted JSON output.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T17:54:00",
            ended_at="2026-04-26T17:55:00",
        )
        self._generate_and_activate_skill(
            trajectory,
            skill_name="execute_directory_csv_to_json_reader_format_roundtrip_skill",
            root=sandbox_root,
            index=sandbox_index,
        )

        execute_result = sandbox_service.execute(
            "execute_directory_csv_to_json_reader_format_roundtrip_skill",
            {
                "input_dir": "demo/csv_exec_reader_format_input",
                "output_dir": "demo/csv_exec_reader_format_output",
                "pattern": "*.csv",
                "quotechar": "'",
                "quoting": "QUOTE_ALL",
                "escapechar": "\\",
                "doublequote": False,
                "ensure_ascii": False,
                "indent": 4,
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=execute_result["observed_task_record"],
            skill_name="execute_directory_csv_to_json_reader_format_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_csv_to_json", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern", "quotechar", "quoting", "escapechar", "doublequote", "ensure_ascii", "indent"),
        )

    def test_service_distill_and_promote_from_execute_directory_csv_to_json_with_reader_spacing_and_json_sort_keys_observed_task_uses_rule_skill(
        self,
    ) -> None:
        sandbox_root, sandbox_service, sandbox_index = self._make_runtime_sandbox()
        input_dir = sandbox_root / "demo" / "csv_exec_reader_spacing_input"
        output_dir = sandbox_root / "demo" / "csv_exec_reader_spacing_output"
        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (input_dir / "a.csv").write_text("name, city\nalice, 中文\n", encoding="utf-8")
        (input_dir / "b.csv").write_text("name, city\nbob, 内容\n", encoding="utf-8")

        trajectory = Trajectory(
            task_id="execute_directory_csv_to_json_reader_spacing_roundtrip_demo",
            session_id="session_execute_directory_csv_to_json_reader_spacing_roundtrip",
            task_description="Convert matching CSV files in one directory into JSON files in another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/csv_exec_reader_spacing_input", "pattern": "*.csv"},
                    observation="Found matching CSV files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_text",
                    tool_input={"path": "demo/csv_exec_reader_spacing_input/a.csv", "skipinitialspace": True},
                    observation="Read CSV file with spacing control.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_json",
                    tool_input={"path": "demo/csv_exec_reader_spacing_output/a.json", "sort_keys": True},
                    observation="Wrote sorted JSON output.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T21:42:00",
            ended_at="2026-04-26T21:43:00",
        )
        self._generate_and_activate_skill(
            trajectory,
            skill_name="execute_directory_csv_to_json_reader_spacing_roundtrip_skill",
            root=sandbox_root,
            index=sandbox_index,
        )

        execute_result = sandbox_service.execute(
            "execute_directory_csv_to_json_reader_spacing_roundtrip_skill",
            {
                "input_dir": "demo/csv_exec_reader_spacing_input",
                "output_dir": "demo/csv_exec_reader_spacing_output",
                "pattern": "*.csv",
                "skipinitialspace": True,
                "sort_keys": True,
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=execute_result["observed_task_record"],
            skill_name="execute_directory_csv_to_json_reader_spacing_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_csv_to_json", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern", "skipinitialspace", "sort_keys"),
        )

    def test_service_distill_and_promote_from_execute_directory_json_to_csv_observed_task_uses_rule_skill(
        self,
    ) -> None:
        sandbox_root, sandbox_service, sandbox_index = self._make_runtime_sandbox()
        input_dir = sandbox_root / "demo" / "json_csv_exec_input"
        output_dir = sandbox_root / "demo" / "json_csv_exec_output"
        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (input_dir / "a.json").write_text(__import__("json").dumps([{"name": "alice", "age": 30}]), encoding="utf-8")
        (input_dir / "b.json").write_text(__import__("json").dumps([{"name": "bob", "age": 31}]), encoding="utf-8")

        trajectory = Trajectory(
            task_id="execute_directory_json_to_csv_roundtrip_demo",
            session_id="session_execute_directory_json_to_csv_roundtrip",
            task_description="Convert matching JSON files in one directory into CSV files in another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/json_csv_exec_input", "pattern": "*.json"},
                    observation="Found matching JSON files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_json",
                    tool_input={"path": "demo/json_csv_exec_input/a.json"},
                    observation="Read one JSON file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_text",
                    tool_input={"path": "demo/json_csv_exec_output/a.csv"},
                    observation="Wrote one CSV file into the output directory.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T14:16:00",
            ended_at="2026-04-26T14:17:00",
        )
        self._generate_and_activate_skill(
            trajectory,
            skill_name="execute_directory_json_to_csv_roundtrip_skill",
            root=sandbox_root,
            index=sandbox_index,
        )

        execute_result = sandbox_service.execute(
            "execute_directory_json_to_csv_roundtrip_skill",
            {
                "input_dir": "demo/json_csv_exec_input",
                "output_dir": "demo/json_csv_exec_output",
                "pattern": "*.json",
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=execute_result["observed_task_record"],
            skill_name="execute_directory_json_to_csv_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_json_to_csv", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern"),
        )

    def test_service_distill_and_promote_from_execute_directory_json_to_csv_with_nested_subdirs_observed_task_uses_rule_skill(
        self,
    ) -> None:
        sandbox_root, sandbox_service, sandbox_index = self._make_runtime_sandbox()
        input_dir = sandbox_root / "demo" / "json_csv_exec_nested_input"
        nested_dir = input_dir / "nested"
        output_dir = sandbox_root / "demo" / "json_csv_exec_nested_output"
        nested_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (nested_dir / "a.json").write_text(__import__("json").dumps([{"name": "alice", "age": 30}]), encoding="utf-8")

        trajectory = Trajectory(
            task_id="execute_directory_json_to_csv_nested_roundtrip_demo",
            session_id="session_execute_directory_json_to_csv_nested_roundtrip",
            task_description="Convert matching JSON files in one directory into CSV files in another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/json_csv_exec_nested_input", "pattern": "**/*.json"},
                    observation="Found nested JSON files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_json",
                    tool_input={"path": "demo/json_csv_exec_nested_input/nested/a.json"},
                    observation="Read one nested JSON file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_text",
                    tool_input={"path": "demo/json_csv_exec_nested_output/nested/a.csv"},
                    observation="Wrote one nested CSV file.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-27T01:38:00",
            ended_at="2026-04-27T01:39:00",
        )
        self._generate_and_activate_skill(
            trajectory,
            skill_name="execute_directory_json_to_csv_nested_roundtrip_skill",
            root=sandbox_root,
            index=sandbox_index,
        )

        execute_result = sandbox_service.execute(
            "execute_directory_json_to_csv_nested_roundtrip_skill",
            {"input_dir": "demo/json_csv_exec_nested_input", "output_dir": "demo/json_csv_exec_nested_output", "pattern": "**/*.json"},
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=execute_result["observed_task_record"],
            skill_name="execute_directory_json_to_csv_nested_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_json_to_csv", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern"),
        )

    def test_service_distill_and_promote_from_execute_directory_json_to_csv_with_suffix_observed_task_uses_rule_skill(
        self,
    ) -> None:
        sandbox_root, sandbox_service, sandbox_index = self._make_runtime_sandbox()
        input_dir = sandbox_root / "demo" / "json_csv_exec_suffix_input"
        output_dir = sandbox_root / "demo" / "json_csv_exec_suffix_output"
        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (input_dir / "a.json").write_text(__import__("json").dumps([{"name": "alice", "age": 30}]), encoding="utf-8")
        (input_dir / "b.json").write_text(__import__("json").dumps([{"name": "bob", "age": 31}]), encoding="utf-8")

        trajectory = Trajectory(
            task_id="execute_directory_json_to_csv_suffix_roundtrip_demo",
            session_id="session_execute_directory_json_to_csv_suffix_roundtrip",
            task_description="Convert matching JSON files in one directory into CSV files in another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/json_csv_exec_suffix_input", "pattern": "*.json"},
                    observation="Found matching JSON files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_json",
                    tool_input={"path": "demo/json_csv_exec_suffix_input/a.json"},
                    observation="Read one JSON file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_text",
                    tool_input={"path": "demo/json_csv_exec_suffix_output/a_export.csv"},
                    observation="Wrote one suffixed CSV file into the output directory.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T22:44:00",
            ended_at="2026-04-26T22:45:00",
        )
        self._generate_and_activate_skill(
            trajectory,
            skill_name="execute_directory_json_to_csv_suffix_roundtrip_skill",
            root=sandbox_root,
            index=sandbox_index,
        )

        execute_result = sandbox_service.execute(
            "execute_directory_json_to_csv_suffix_roundtrip_skill",
            {
                "input_dir": "demo/json_csv_exec_suffix_input",
                "output_dir": "demo/json_csv_exec_suffix_output",
                "pattern": "*.json",
                "suffix": "_export",
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=execute_result["observed_task_record"],
            skill_name="execute_directory_json_to_csv_suffix_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_json_to_csv", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern", "suffix"),
        )

    def test_service_distill_and_promote_from_execute_directory_json_to_csv_with_formatting_observed_task_uses_rule_skill(
        self,
    ) -> None:
        sandbox_root, sandbox_service, sandbox_index = self._make_runtime_sandbox()
        input_dir = sandbox_root / "demo" / "json_csv_exec_format_input"
        output_dir = sandbox_root / "demo" / "json_csv_exec_format_output"
        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (input_dir / "a.json").write_text(__import__("json").dumps([{"name": "alice,smith", "age": 30}]), encoding="utf-8")
        (input_dir / "b.json").write_text(__import__("json").dumps([{"name": "bob,jones", "age": 31}]), encoding="utf-8")

        trajectory = Trajectory(
            task_id="execute_directory_json_to_csv_format_roundtrip_demo",
            session_id="session_execute_directory_json_to_csv_format_roundtrip",
            task_description="Convert matching JSON files in one directory into CSV files in another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/json_csv_exec_format_input", "pattern": "*.json"},
                    observation="Found matching JSON files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_json",
                    tool_input={"path": "demo/json_csv_exec_format_input/a.json"},
                    observation="Read one JSON file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_text",
                    tool_input={
                        "path": "demo/json_csv_exec_format_output/a.csv",
                        "quotechar": "'",
                        "quoting": "QUOTE_ALL",
                    },
                    observation="Wrote quoted CSV output.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T17:24:00",
            ended_at="2026-04-26T17:25:00",
        )
        self._generate_and_activate_skill(
            trajectory,
            skill_name="execute_directory_json_to_csv_format_roundtrip_skill",
            root=sandbox_root,
            index=sandbox_index,
        )

        execute_result = sandbox_service.execute(
            "execute_directory_json_to_csv_format_roundtrip_skill",
            {
                "input_dir": "demo/json_csv_exec_format_input",
                "output_dir": "demo/json_csv_exec_format_output",
                "pattern": "*.json",
                "quotechar": "'",
                "quoting": "QUOTE_ALL",
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=execute_result["observed_task_record"],
            skill_name="execute_directory_json_to_csv_format_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_json_to_csv", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern", "quotechar", "quoting"),
        )

    def test_service_distill_and_promote_from_execute_directory_json_to_csv_with_escape_observed_task_uses_rule_skill(
        self,
    ) -> None:
        sandbox_root, sandbox_service, sandbox_index = self._make_runtime_sandbox()
        input_dir = sandbox_root / "demo" / "json_csv_exec_escape_input"
        output_dir = sandbox_root / "demo" / "json_csv_exec_escape_output"
        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (input_dir / "a.json").write_text(__import__("json").dumps([{"name": "alice's", "age": 30}]), encoding="utf-8")
        (input_dir / "b.json").write_text(__import__("json").dumps([{"name": "bob's", "age": 31}]), encoding="utf-8")

        trajectory = Trajectory(
            task_id="execute_directory_json_to_csv_escape_roundtrip_demo",
            session_id="session_execute_directory_json_to_csv_escape_roundtrip",
            task_description="Convert matching JSON files in one directory into CSV files in another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/json_csv_exec_escape_input", "pattern": "*.json"},
                    observation="Found matching JSON files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_json",
                    tool_input={"path": "demo/json_csv_exec_escape_input/a.json"},
                    observation="Read one JSON file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_text",
                    tool_input={
                        "path": "demo/json_csv_exec_escape_output/a.csv",
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
            started_at="2026-04-26T17:34:00",
            ended_at="2026-04-26T17:35:00",
        )
        self._generate_and_activate_skill(
            trajectory,
            skill_name="execute_directory_json_to_csv_escape_roundtrip_skill",
            root=sandbox_root,
            index=sandbox_index,
        )

        execute_result = sandbox_service.execute(
            "execute_directory_json_to_csv_escape_roundtrip_skill",
            {
                "input_dir": "demo/json_csv_exec_escape_input",
                "output_dir": "demo/json_csv_exec_escape_output",
                "pattern": "*.json",
                "quotechar": "'",
                "quoting": "QUOTE_ALL",
                "escapechar": "\\",
                "doublequote": False,
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=execute_result["observed_task_record"],
            skill_name="execute_directory_json_to_csv_escape_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_json_to_csv", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern", "quotechar", "quoting", "escapechar", "doublequote"),
        )

    def test_service_distill_and_promote_from_execute_directory_json_to_csv_with_missing_value_inputs_observed_task_uses_rule_skill(
        self,
    ) -> None:
        sandbox_root, sandbox_service, sandbox_index = self._make_runtime_sandbox()
        input_dir = sandbox_root / "demo" / "json_csv_exec_missing_input"
        output_dir = sandbox_root / "demo" / "json_csv_exec_missing_output"
        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (input_dir / "a.json").write_text(__import__("json").dumps([{"name": "alice", "age": 30}, {"name": "bob", "extra": "ignore-me"}]), encoding="utf-8")
        (input_dir / "b.json").write_text(__import__("json").dumps([{"name": "carol", "age": 32}, {"name": "dave", "extra": "ignore-me"}]), encoding="utf-8")

        trajectory = Trajectory(
            task_id="execute_directory_json_to_csv_missing_roundtrip_demo",
            session_id="session_execute_directory_json_to_csv_missing_roundtrip",
            task_description="Convert matching JSON files in one directory into CSV files in another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/json_csv_exec_missing_input", "pattern": "*.json"},
                    observation="Found matching JSON files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_json",
                    tool_input={"path": "demo/json_csv_exec_missing_input/a.json"},
                    observation="Read one JSON file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_text",
                    tool_input={"path": "demo/json_csv_exec_missing_output/a.csv", "restval": "NA", "extrasaction": "ignore"},
                    observation="Wrote CSV output while filling missing values and ignoring extra keys.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T21:44:00",
            ended_at="2026-04-26T21:45:00",
        )
        self._generate_and_activate_skill(
            trajectory,
            skill_name="execute_directory_json_to_csv_missing_roundtrip_skill",
            root=sandbox_root,
            index=sandbox_index,
        )

        execute_result = sandbox_service.execute(
            "execute_directory_json_to_csv_missing_roundtrip_skill",
            {
                "input_dir": "demo/json_csv_exec_missing_input",
                "output_dir": "demo/json_csv_exec_missing_output",
                "pattern": "*.json",
                "restval": "NA",
                "extrasaction": "ignore",
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=execute_result["observed_task_record"],
            skill_name="execute_directory_json_to_csv_missing_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_json_to_csv", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern", "restval", "extrasaction"),
        )

    def test_service_distill_and_promote_from_execute_directory_text_transform_observed_task_uses_rule_skill(
        self,
    ) -> None:
        sandbox_root, sandbox_service, sandbox_index = self._make_runtime_sandbox()
        input_dir = sandbox_root / "demo" / "text_exec_input"
        output_dir = sandbox_root / "demo" / "text_exec_output"
        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (input_dir / "a.txt").write_text("alpha", encoding="utf-8")
        (input_dir / "b.txt").write_text("beta\n", encoding="utf-8")

        trajectory = Trajectory(
            task_id="execute_directory_text_transform_roundtrip_demo",
            session_id="session_execute_directory_text_transform_roundtrip",
            task_description="Normalize matching text files from one directory into another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/text_exec_input", "pattern": "*.txt"},
                    observation="Found matching text files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_text",
                    tool_input={"path": "demo/text_exec_input/a.txt"},
                    observation="Read one text file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_text",
                    tool_input={"path": "demo/text_exec_output/a.txt"},
                    observation="Wrote one normalized text file into the output directory.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T14:22:00",
            ended_at="2026-04-26T14:23:00",
        )
        self._generate_and_activate_skill(
            trajectory,
            skill_name="execute_directory_text_transform_roundtrip_skill",
            root=sandbox_root,
            index=sandbox_index,
        )

        execute_result = sandbox_service.execute(
            "execute_directory_text_transform_roundtrip_skill",
            {
                "input_dir": "demo/text_exec_input",
                "output_dir": "demo/text_exec_output",
                "pattern": "*.txt",
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=execute_result["observed_task_record"],
            skill_name="execute_directory_text_transform_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_text_transform", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern"),
        )

    def test_service_distill_and_promote_from_execute_directory_text_transform_with_suffix_observed_task_uses_rule_skill(
        self,
    ) -> None:
        sandbox_root, sandbox_service, sandbox_index = self._make_runtime_sandbox()
        input_dir = sandbox_root / "demo" / "text_exec_suffix_input"
        output_dir = sandbox_root / "demo" / "text_exec_suffix_output"
        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (input_dir / "a.txt").write_text("alpha", encoding="utf-8")
        (input_dir / "b.txt").write_text("beta\n", encoding="utf-8")

        trajectory = Trajectory(
            task_id="execute_directory_text_transform_suffix_roundtrip_demo",
            session_id="session_execute_directory_text_transform_suffix_roundtrip",
            task_description="Normalize matching text files from one directory into another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/text_exec_suffix_input", "pattern": "*.txt"},
                    observation="Found matching text files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_text",
                    tool_input={"path": "demo/text_exec_suffix_input/a.txt"},
                    observation="Read one text file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_text",
                    tool_input={"path": "demo/text_exec_suffix_output/a_done.txt"},
                    observation="Wrote one suffixed text file into the output directory.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T22:46:00",
            ended_at="2026-04-26T22:47:00",
        )
        self._generate_and_activate_skill(
            trajectory,
            skill_name="execute_directory_text_transform_suffix_roundtrip_skill",
            root=sandbox_root,
            index=sandbox_index,
        )

        execute_result = sandbox_service.execute(
            "execute_directory_text_transform_suffix_roundtrip_skill",
            {
                "input_dir": "demo/text_exec_suffix_input",
                "output_dir": "demo/text_exec_suffix_output",
                "pattern": "*.txt",
                "suffix": "_done",
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=execute_result["observed_task_record"],
            skill_name="execute_directory_text_transform_suffix_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_text_transform", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern", "suffix"),
        )

    def test_service_distill_and_promote_from_execute_directory_text_transform_with_nested_subdirs_observed_task_uses_rule_skill(
        self,
    ) -> None:
        sandbox_root, sandbox_service, sandbox_index = self._make_runtime_sandbox()
        input_dir = sandbox_root / "demo" / "text_exec_nested_input"
        nested_dir = input_dir / "nested"
        output_dir = sandbox_root / "demo" / "text_exec_nested_output"
        nested_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (nested_dir / "a.txt").write_text("alpha", encoding="utf-8")

        trajectory = Trajectory(
            task_id="execute_directory_text_transform_nested_roundtrip_demo",
            session_id="session_execute_directory_text_transform_nested_roundtrip",
            task_description="Normalize matching text files from one directory into another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/text_exec_nested_input", "pattern": "**/*.txt"},
                    observation="Found nested text files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_text",
                    tool_input={"path": "demo/text_exec_nested_input/nested/a.txt"},
                    observation="Read one nested text file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_text",
                    tool_input={"path": "demo/text_exec_nested_output/nested/a.txt"},
                    observation="Wrote one nested normalized text file.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-27T01:12:00",
            ended_at="2026-04-27T01:13:00",
        )
        self._generate_and_activate_skill(
            trajectory,
            skill_name="execute_directory_text_transform_nested_roundtrip_skill",
            root=sandbox_root,
            index=sandbox_index,
        )

        execute_result = sandbox_service.execute(
            "execute_directory_text_transform_nested_roundtrip_skill",
            {
                "input_dir": "demo/text_exec_nested_input",
                "output_dir": "demo/text_exec_nested_output",
                "pattern": "**/*.txt",
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=execute_result["observed_task_record"],
            skill_name="execute_directory_text_transform_nested_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_text_transform", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern"),
        )

    def test_service_distill_and_promote_from_execute_directory_text_transform_with_newline_observed_task_uses_rule_skill(
        self,
    ) -> None:
        sandbox_root, sandbox_service, sandbox_index = self._make_runtime_sandbox()
        input_dir = sandbox_root / "demo" / "text_exec_newline_input"
        output_dir = sandbox_root / "demo" / "text_exec_newline_output"
        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)
        (input_dir / "a.txt").write_text("alpha", encoding="utf-8")
        (input_dir / "b.txt").write_text("beta\n", encoding="utf-8")

        trajectory = Trajectory(
            task_id="execute_directory_text_transform_newline_roundtrip_demo",
            session_id="session_execute_directory_text_transform_newline_roundtrip",
            task_description="Normalize matching text files from one directory into another directory.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/text_exec_newline_input", "pattern": "*.txt"},
                    observation="Found matching text files.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="read_text",
                    tool_input={"path": "demo/text_exec_newline_input/a.txt"},
                    observation="Read one text file.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="3",
                    tool_name="write_text",
                    tool_input={"path": "demo/text_exec_newline_output/a.txt", "newline": "\n"},
                    observation="Wrote one normalized text file with LF endings.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T22:22:00",
            ended_at="2026-04-26T22:23:00",
        )
        self._generate_and_activate_skill(
            trajectory,
            skill_name="execute_directory_text_transform_newline_roundtrip_skill",
            root=sandbox_root,
            index=sandbox_index,
        )

        execute_result = sandbox_service.execute(
            "execute_directory_text_transform_newline_roundtrip_skill",
            {
                "input_dir": "demo/text_exec_newline_input",
                "output_dir": "demo/text_exec_newline_output",
                "pattern": "*.txt",
                "newline": "\n",
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=execute_result["observed_task_record"],
            skill_name="execute_directory_text_transform_newline_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("directory_text_transform", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_dir", "pattern", "newline"),
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

    def test_service_distill_and_promote_from_execute_batch_rename_suffix_observed_task_uses_rule_skill(
        self,
    ) -> None:
        sandbox_root, sandbox_service, sandbox_index = self._make_runtime_sandbox()
        input_dir = sandbox_root / "demo" / "rename_suffix_exec_input"
        input_dir.mkdir(parents=True, exist_ok=True)
        (input_dir / "a.txt").write_text("alpha\n", encoding="utf-8")
        (input_dir / "b.txt").write_text("beta\n", encoding="utf-8")

        trajectory = Trajectory(
            task_id="execute_batch_rename_suffix_roundtrip_demo",
            session_id="session_execute_batch_rename_suffix_roundtrip",
            task_description="Rename all txt files in a directory by suffixing them with a value.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/rename_suffix_exec_input", "pattern": "*.txt"},
                    observation="Found files to rename.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="rename_path",
                    tool_input={"source": "demo/rename_suffix_exec_input/a.txt", "target": "demo/rename_suffix_exec_input/a_done.txt"},
                    observation="Renamed matching files with a suffix.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T14:32:00",
            ended_at="2026-04-26T14:33:00",
        )
        self._generate_and_activate_skill(
            trajectory,
            skill_name="execute_batch_rename_suffix_roundtrip_skill",
            root=sandbox_root,
            index=sandbox_index,
        )

        execute_result = sandbox_service.execute(
            "execute_batch_rename_suffix_roundtrip_skill",
            {
                "input_dir": "demo/rename_suffix_exec_input",
                "suffix": "_done",
                "pattern": "*.txt",
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=execute_result["observed_task_record"],
            skill_name="execute_batch_rename_suffix_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("batch_rename_suffix", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "suffix", "pattern"),
        )

    def test_service_distill_and_promote_from_execute_batch_rename_extension_observed_task_uses_rule_skill(
        self,
    ) -> None:
        sandbox_root, sandbox_service, sandbox_index = self._make_runtime_sandbox()
        input_dir = sandbox_root / "demo" / "rename_extension_exec_input"
        input_dir.mkdir(parents=True, exist_ok=True)
        (input_dir / "a.txt").write_text("alpha\n", encoding="utf-8")
        (input_dir / "b.txt").write_text("beta\n", encoding="utf-8")

        trajectory = Trajectory(
            task_id="execute_batch_rename_extension_roundtrip_demo",
            session_id="session_execute_batch_rename_extension_roundtrip",
            task_description="Rename all txt files in a directory by changing their extension to md.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/rename_extension_exec_input", "pattern": "*.txt"},
                    observation="Found files to rename.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="rename_path",
                    tool_input={"source": "demo/rename_extension_exec_input/a.txt", "target": "demo/rename_extension_exec_input/a.md"},
                    observation="Renamed matching files by changing their extension.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T15:02:00",
            ended_at="2026-04-26T15:03:00",
        )
        self._generate_and_activate_skill(
            trajectory,
            skill_name="execute_batch_rename_extension_roundtrip_skill",
            root=sandbox_root,
            index=sandbox_index,
        )

        execute_result = sandbox_service.execute(
            "execute_batch_rename_extension_roundtrip_skill",
            {
                "input_dir": "demo/rename_extension_exec_input",
                "output_extension": ".md",
                "pattern": "*.txt",
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=execute_result["observed_task_record"],
            skill_name="execute_batch_rename_extension_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("batch_rename_extension", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "output_extension", "pattern"),
        )

    def test_service_distill_and_promote_from_execute_batch_rename_replace_observed_task_uses_rule_skill(
        self,
    ) -> None:
        sandbox_root, sandbox_service, sandbox_index = self._make_runtime_sandbox()
        input_dir = sandbox_root / "demo" / "rename_replace_exec_input"
        input_dir.mkdir(parents=True, exist_ok=True)
        (input_dir / "draft_a.txt").write_text("alpha\n", encoding="utf-8")
        (input_dir / "draft_b.txt").write_text("beta\n", encoding="utf-8")

        trajectory = Trajectory(
            task_id="execute_batch_rename_replace_roundtrip_demo",
            session_id="session_execute_batch_rename_replace_roundtrip",
            task_description="Rename all txt files in a directory by replacing draft with final in each filename.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/rename_replace_exec_input", "pattern": "*.txt"},
                    observation="Found files to rename.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="rename_path",
                    tool_input={"source": "demo/rename_replace_exec_input/draft_a.txt", "target": "demo/rename_replace_exec_input/final_a.txt"},
                    observation="Renamed matching files by replacing part of each filename.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T15:22:00",
            ended_at="2026-04-26T15:23:00",
        )
        self._generate_and_activate_skill(
            trajectory,
            skill_name="execute_batch_rename_replace_roundtrip_skill",
            root=sandbox_root,
            index=sandbox_index,
        )

        execute_result = sandbox_service.execute(
            "execute_batch_rename_replace_roundtrip_skill",
            {
                "input_dir": "demo/rename_replace_exec_input",
                "old_text": "draft",
                "new_text": "final",
                "pattern": "*.txt",
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=execute_result["observed_task_record"],
            skill_name="execute_batch_rename_replace_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("batch_rename_replace", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "old_text", "new_text", "pattern"),
        )

    def test_service_distill_and_promote_from_execute_batch_rename_case_observed_task_uses_rule_skill(
        self,
    ) -> None:
        sandbox_root, sandbox_service, sandbox_index = self._make_runtime_sandbox()
        input_dir = sandbox_root / "demo" / "rename_case_exec_input"
        input_dir.mkdir(parents=True, exist_ok=True)
        (input_dir / "DraftA.TXT").write_text("alpha\n", encoding="utf-8")
        (input_dir / "DraftB.TXT").write_text("beta\n", encoding="utf-8")

        trajectory = Trajectory(
            task_id="execute_batch_rename_case_roundtrip_demo",
            session_id="session_execute_batch_rename_case_roundtrip",
            task_description="Rename all files in a directory to lowercase filenames.",
            steps=[
                TrajectoryStep(
                    step_id="1",
                    tool_name="list_files",
                    tool_input={"path": "demo/rename_case_exec_input", "pattern": "*.*"},
                    observation="Found files to rename.",
                    status="success",
                ),
                TrajectoryStep(
                    step_id="2",
                    tool_name="rename_path",
                    tool_input={"source": "demo/rename_case_exec_input/DraftA.TXT", "target": "demo/rename_case_exec_input/drafta.txt"},
                    observation="Renamed matching files to lowercase.",
                    status="success",
                ),
            ],
            final_status="success",
            artifacts=[],
            started_at="2026-04-26T16:02:00",
            ended_at="2026-04-26T16:03:00",
        )
        self._generate_and_activate_skill(
            trajectory,
            skill_name="execute_batch_rename_case_roundtrip_skill",
            root=sandbox_root,
            index=sandbox_index,
        )

        execute_result = sandbox_service.execute(
            "execute_batch_rename_case_roundtrip_skill",
            {
                "input_dir": "demo/rename_case_exec_input",
                "filename_case": "lower",
                "pattern": "*.*",
            },
        )

        result = sandbox_service.distill_and_promote(
            observed_task_path=execute_result["observed_task_record"],
            skill_name="execute_batch_rename_case_roundtrip_test",
        )
        metadata = self._read_json_file(__import__("pathlib").Path(result["distillation"]["metadata_file"]))

        self.assertTrue(result["promoted"])
        self.assertEqual("passed", result["audit"]["report"]["status"])
        self.assertEqual("batch_rename_case", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", result["distillation"])
        self._assert_execute_skill_schema(
            result["recommended_host_operation"],
            expected_args_fields=("input_dir", "filename_case", "pattern"),
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
