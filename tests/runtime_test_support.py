import asyncio
import ast
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from dataclasses import asdict
from pathlib import Path

from skill_runtime.api.models import Trajectory
from skill_runtime.distill.skill_generator import SkillGenerator
from skill_runtime.api.service import RuntimeService
from skill_runtime.mcp.server import build_mcp_server
from skill_runtime.retrieval.skill_index import SkillIndex


ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / "scripts" / "skill_cli.py"


class RuntimeTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.index = SkillIndex(ROOT / "skill_store" / "index.json")
        self.index.rebuild_from_directory(ROOT / "skill_store" / "active")
        self.service = RuntimeService(ROOT)

    def _activate_generated_skill(
        self,
        generated: dict,
        *,
        root: Path = ROOT,
        index: SkillIndex | None = None,
    ) -> None:
        module_path = generated["skill_file"]
        metadata = generated["metadata"]

        target_index = index or self.index
        active_dir = root / "skill_store" / "active"
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
        target_index.upsert(metadata)

    def _generate_and_activate_skill(
        self,
        trajectory: Trajectory,
        *,
        skill_name: str,
        root: Path = ROOT,
        index: SkillIndex | None = None,
    ) -> dict:
        generated = SkillGenerator(root / "skill_store" / "staging").generate(
            trajectory,
            skill_name=skill_name,
        )
        self._activate_generated_skill(generated, root=root, index=index)
        return generated

    def _write_args_file(self, file_name: str, payload: dict, *, root: Path = ROOT) -> Path:
        args_file = root / "demo" / file_name
        args_file.write_text(json.dumps(payload), encoding="utf-8")
        self.addCleanup(args_file.unlink)
        return args_file

    def _write_demo_json(self, file_name: str, payload: dict, *, root: Path = ROOT) -> Path:
        file_path = root / "demo" / file_name
        file_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        self.addCleanup(file_path.unlink)
        return file_path

    def _write_json_file(self, path: Path, payload: dict) -> Path:
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        self.addCleanup(lambda: path.unlink(missing_ok=True))
        return path

    def _read_json_file(self, path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    def _build_move_logs_observed_task(
        self,
        *,
        variant: str = "steps",
        input_dir: str = "demo/move_input",
        output_dir: str = "demo/move_output",
        task_text: str = "Move all log files from inbox to archive.",
        list_observation: str = "Found matching log files.",
        move_observation: str = "Moved matching log files.",
        artifact: str | None = "demo/move_output/job1.log",
    ) -> dict:
        if variant == "steps":
            payload = {
                "task_description": task_text,
                "steps": [
                    {
                        "tool_name": "list_files",
                        "tool_input": {"input_dir": input_dir, "pattern": "*.log"},
                        "observation": list_observation,
                    },
                    {
                        "tool_name": "move_file",
                        "tool_input": {"input_dir": input_dir, "output_dir": output_dir},
                        "observation": move_observation,
                    },
                ],
            }
            if artifact is not None:
                payload["artifacts"] = [artifact]
            return payload

        if variant == "compact":
            payload = {
                "task": task_text,
                "actions": [
                    {
                        "tool": "list_files",
                        "input": {"input_dir": input_dir, "pattern": "*.log"},
                        "result": list_observation,
                    },
                    {
                        "tool": "move_file",
                        "input": {"input_dir": input_dir, "output_dir": output_dir},
                        "result": move_observation,
                    },
                ],
            }
            if artifact is not None:
                payload["outputs"] = [artifact]
            return payload

        if variant == "nested":
            payload = {
                "goal": task_text,
                "records": [
                    {
                        "tool": {
                            "name": "list_files",
                            "arguments": {"input_dir": input_dir, "pattern": "*.log"},
                        },
                        "result": {"message": list_observation, "status": "success"},
                    },
                    {
                        "tool": {
                            "name": "move_file",
                            "arguments": {"input_dir": input_dir, "output_dir": output_dir},
                        },
                        "result": {
                            "output": move_observation,
                            "success": True,
                        },
                    },
                ],
            }
            if artifact is not None:
                payload["records"][1]["result"]["outputs"] = [artifact]
            return payload

        raise ValueError(f"Unsupported observed task variant: {variant}")

    def _write_active_skill_fixture(
        self,
        skill_name: str,
        metadata: dict,
        *,
        source: str | None = None,
        root: Path = ROOT,
    ) -> tuple[Path, Path]:
        active_dir = root / "skill_store" / "active"
        skill_path = active_dir / f"{skill_name}.py"
        metadata_path = active_dir / f"{skill_name}.metadata.json"
        skill_source = source or 'def run(tools, **kwargs):\n    return {"status": "completed"}\n'
        skill_path.write_text(skill_source, encoding="utf-8")
        self.addCleanup(lambda: skill_path.unlink(missing_ok=True))
        payload = dict(metadata)
        payload["skill_name"] = skill_name
        payload["file_path"] = str(skill_path.resolve())
        self._write_json_file(metadata_path, payload)
        return skill_path, metadata_path

    def _execute_skill_cli(self, skill_name: str, *, args_file: Path, root: Path = ROOT) -> dict:
        payload = self._run_cli(
            "execute",
            "--skill",
            skill_name,
            "--args-file",
            str(args_file),
            root=root,
            expect_json=True,
        )
        self.assertEqual("ok", payload["status"])
        return payload

    def _run_cli(self, *args: str, root: Path = ROOT, expect_json: bool = False):
        result = subprocess.run(
            [sys.executable, str(CLI), "--root", str(root), *args],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        self.assertEqual(0, result.returncode, msg=result.stderr or result.stdout)
        if expect_json:
            return json.loads(result.stdout)
        return result

    def _call_mcp_tool(self, tool_name: str, arguments: dict, *, root: Path = ROOT) -> dict:
        server = build_mcp_server(root)
        _, payload = asyncio.run(server.call_tool(tool_name, arguments))
        self.assertEqual("ok", payload["status"])
        return payload

    def _make_runtime_sandbox(self) -> tuple[Path, RuntimeService, SkillIndex]:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        sandbox_root = Path(temp_dir.name)

        shutil.copytree(ROOT / "demo", sandbox_root / "demo")
        shutil.copytree(ROOT / "skill_store", sandbox_root / "skill_store")
        shutil.copytree(ROOT / "trajectories", sandbox_root / "trajectories")
        (sandbox_root / "audits").mkdir(parents=True, exist_ok=True)
        (sandbox_root / "observed_tasks").mkdir(parents=True, exist_ok=True)

        for metadata_path in (sandbox_root / "skill_store").rglob("*.metadata.json"):
            payload = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
            payload["file_path"] = str(
                metadata_path.with_name(metadata_path.name.replace(".metadata.json", ".py")).resolve()
            )
            metadata_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

        index = SkillIndex(sandbox_root / "skill_store" / "index.json")
        index.rebuild_from_directory(sandbox_root / "skill_store" / "active")
        return sandbox_root, RuntimeService(sandbox_root), index

    def _assert_host_operation_basics(
        self,
        operation: dict,
        *,
        tool_name: str,
        operation_type: str = "mcp_tool_call",
        source_ref: str | None = None,
        display_label: str | None = None,
        risk_level: str | None = None,
        requires_confirmation: bool | None = None,
    ) -> None:
        self.assertEqual(operation_type, operation["type"])
        self.assertEqual(tool_name, operation["tool_name"])
        self.assertTrue(operation["operation_id"])
        if source_ref is not None:
            self.assertEqual(source_ref, operation["source_ref"])
        if display_label is not None:
            self.assertEqual(display_label, operation["display_label"])
        self.assertTrue(operation["effect_summary"])
        if risk_level is not None:
            self.assertEqual(risk_level, operation["risk_level"])
        if requires_confirmation is not None:
            self.assertEqual(requires_confirmation, operation["requires_confirmation"])
            if requires_confirmation:
                self.assertTrue(operation["confirmation_message"])
            else:
                self.assertIsNone(operation["confirmation_message"])

    def _assert_operation_role(self, operation: dict, expected_role: str) -> None:
        self.assertEqual(expected_role, operation["operation_role"])

    def _assert_argument_schema_entry(
        self,
        schema: dict,
        field_name: str,
        *,
        field_type: str,
        required: bool | None = None,
        prefilled: bool | None = None,
    ) -> dict:
        self.assertIn(field_name, schema)
        field = schema[field_name]
        self.assertEqual(field_type, field["type"])
        if required is not None:
            self.assertEqual(required, field["required"])
        if prefilled is not None:
            self.assertEqual(prefilled, field["prefilled"])
        return field

    def _assert_object_argument_schema(
        self,
        schema: dict,
        field_name: str,
        *,
        required: bool | None = None,
        prefilled: bool | None = None,
    ) -> dict:
        field = self._assert_argument_schema_entry(
            schema,
            field_name,
            field_type="object",
            required=required,
            prefilled=prefilled,
        )
        self.assertIn("properties", field)
        return field["properties"]

    def _find_action(self, actions: list[dict], action_name: str, **criteria) -> dict:
        for action in actions:
            if action.get("action") != action_name:
                continue
            if all(action.get(key) == value for key, value in criteria.items()):
                return action
        raise AssertionError(f"Action not found: {action_name} with {criteria}")

    def _assert_observed_skill_record(
        self,
        payload: dict,
        *,
        skill_name: str,
        status: str | None = None,
        first_tool: str | None = None,
        last_tool: str | None = None,
        contains_tool: str | None = None,
    ) -> None:
        self.assertEqual(skill_name, payload["skill_name"])
        self.assertTrue(payload["actions"])
        if status is not None:
            self.assertEqual(status, payload["result"]["status"])
        if first_tool is not None:
            self.assertEqual(first_tool, payload["actions"][0]["tool_name"])
        if last_tool is not None:
            self.assertEqual(last_tool, payload["actions"][-1]["tool_name"])
        if contains_tool is not None:
            self.assertTrue(any(step["tool_name"] == contains_tool for step in payload["actions"]))

    def _assert_observed_task_follow_up(
        self,
        operation: dict,
        *,
        observed_task_path: str,
        tool_name: str = "distill_and_promote_candidate",
        display_label: str | None = None,
        risk_level: str | None = None,
    ) -> None:
        kwargs = {
            "tool_name": tool_name,
            "source_ref": f"observed_task:{observed_task_path}",
            "requires_confirmation": False,
        }
        if display_label is not None:
            kwargs["display_label"] = display_label
        if risk_level is not None:
            kwargs["risk_level"] = risk_level
        self._assert_host_operation_basics(operation, **kwargs)
        self.assertEqual(observed_task_path, operation["arguments"]["observed_task_path"])
        self._assert_argument_schema_entry(
            operation["argument_schema"],
            "observed_task_path",
            field_type="string",
            prefilled=True,
        )

    def _assert_execute_skill_schema(
        self,
        operation: dict,
        *,
        skill_name_prefilled: bool = True,
        expected_args_fields: tuple[str, ...] | None = ("input_dir", "output_path"),
    ) -> dict:
        self._assert_argument_schema_entry(
            operation["argument_schema"],
            "skill_name",
            field_type="string",
            prefilled=skill_name_prefilled,
        )
        args_properties = self._assert_object_argument_schema(
            operation["argument_schema"],
            "args",
        )
        if expected_args_fields is not None:
            for field_name in expected_args_fields:
                self._assert_argument_schema_entry(
                    args_properties,
                    field_name,
                    field_type="string",
                )
        return args_properties

    def _module_imports(self, path: Path) -> set[str]:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        imports: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)
        return imports
