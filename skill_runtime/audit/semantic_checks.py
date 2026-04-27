import ast
import re
from dataclasses import dataclass
from pathlib import Path

from skill_runtime.api.models import Trajectory


GENERALIZATION_BLOCKLIST = {"confirm", "retry", "timeout", "sleep", "debug"}


@dataclass
class SemanticIssue:
    rule_id: str
    severity: str
    message: str


class SemanticChecks:
    def run(self, file_path: str | Path, trajectory: Trajectory | None = None) -> list[SemanticIssue]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"file not found: {path}")

        source = path.read_text(encoding="utf-8")
        issues: list[SemanticIssue] = []
        issues.extend(self._check_docstring_structure(source))
        issues.extend(self._check_atomicity(source))

        if trajectory is not None:
            issues.extend(self._check_trajectory_alignment(source, trajectory))
            issues.extend(self._check_parameter_coverage(source, trajectory))
            issues.extend(self._check_overfit_artifacts(source, trajectory))

        return issues

    def _check_docstring_structure(self, source: str) -> list[SemanticIssue]:
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return []

        run_node = self._find_run_function(tree)
        if run_node is None:
            return []

        docstring = ast.get_docstring(run_node) or ""
        required_sections = ["功能描述", "输入参数", "输出结果"]
        missing = [section for section in required_sections if section not in docstring]
        if missing:
            return [
                SemanticIssue(
                    rule_id="docstring-structure",
                    severity="medium",
                    message=f"Docstring is missing semantic sections: {', '.join(missing)}.",
                )
            ]
        return []

    def _check_atomicity(self, source: str) -> list[SemanticIssue]:
        tool_names = self._tool_names_in_source(source)
        if len(tool_names) > 4:
            return [
                SemanticIssue(
                    rule_id="semantic-atomicity",
                    severity="medium",
                    message=(
                        "Skill appears to combine too many distinct runtime tool actions; "
                        "consider splitting it into smaller workflows."
                    ),
                )
            ]
        return []

    def _check_trajectory_alignment(self, source: str, trajectory: Trajectory) -> list[SemanticIssue]:
        trajectory_tools = {step.tool_name for step in trajectory.steps if step.status == "success"}
        source_tools = self._tool_names_in_source(source)
        if not trajectory_tools:
            return []

        if source_tools:
            overlap = trajectory_tools & source_tools
            if overlap:
                return []
            return [
                SemanticIssue(
                    rule_id="trajectory-alignment",
                    severity="high",
                    message=(
                        "Skill tool usage does not align with the successful trajectory tools. "
                        f"Trajectory tools: {sorted(trajectory_tools)}; source tools: {sorted(source_tools)}."
                    ),
                )
            ]

        if trajectory_tools and self._looks_like_template_skill(source):
            return [
                SemanticIssue(
                    rule_id="template-skill",
                    severity="high",
                    message=(
                        "Skill looks like a template or no-op and does not appear to implement the "
                        "observed successful trajectory."
                    ),
                )
            ]

        return [
            SemanticIssue(
                rule_id="trajectory-alignment",
                severity="medium",
                message=(
                    "Skill does not appear to call runtime tools from the successful trajectory. "
                    "Confirm that the implementation is not overly abstract or incomplete."
                ),
            )
        ]

    def _check_parameter_coverage(self, source: str, trajectory: Trajectory) -> list[SemanticIssue]:
        expected = self._expected_trajectory_inputs(trajectory)
        if not expected:
            return []

        kwargs_keys = set(re.findall(r'kwargs\.get\("([A-Za-z0-9_]+)"\)', source))
        if not kwargs_keys:
            return [
                SemanticIssue(
                    rule_id="parameter-coverage",
                    severity="medium",
                    message="Skill does not expose trajectory-derived inputs through kwargs parameters.",
                )
            ]

        overlap = expected & kwargs_keys
        if len(overlap) >= max(1, len(expected) // 2):
            return []

        return [
            SemanticIssue(
                rule_id="parameter-coverage",
                severity="medium",
                message=(
                    "Skill parameters only weakly cover the successful trajectory inputs. "
                    f"Expected from trajectory: {sorted(expected)}; found in skill: {sorted(kwargs_keys)}."
                ),
            )
        ]

    def _expected_trajectory_inputs(self, trajectory: Trajectory) -> set[str]:
        tool_names = {step.tool_name.lower() for step in trajectory.steps}
        expected: set[str] = set()
        for step in trajectory.steps:
            tool_name = step.tool_name.lower()
            for key in step.tool_input.keys():
                normalized_key = self._canonicalize_input_key(tool_name, key, tool_names)
                if normalized_key and normalized_key.lower() not in GENERALIZATION_BLOCKLIST:
                    expected.add(normalized_key)
        return expected

    def _canonicalize_input_key(self, tool_name: str, key: str, tool_names: set[str]) -> str | None:
        normalized = key.lower()
        if normalized in GENERALIZATION_BLOCKLIST:
            return None
        if normalized in {"input_dir", "output_dir", "input_path", "output_path", "prefix", "pattern", "delimiter", "output_extension", "filename_case"}:
            return normalized
        if normalized == "input":
            if tool_name in {"copy_file", "move_file", "rename_path", "move_path"}:
                return "input_dir" if "list_files" in tool_names else "input_path"
            return "input_path" if tool_name.startswith("read_") else None
        if normalized == "output":
            if tool_name in {"copy_file", "move_file", "rename_path", "move_path"}:
                return "output_dir" if "list_files" in tool_names else "output_path"
            return "output_path" if tool_name.startswith("write_") else None
        if normalized == "file":
            if tool_name.startswith("read_"):
                return "input_path"
            if tool_name.startswith("write_"):
                return "output_path"
            return None
        if normalized in {"old", "search", "search_text", "find_text", "old_value", "find", "search_value", "needle"}:
            return "old_text"
        if normalized in {
            "new",
            "replace",
            "replace_text",
            "replacement_text",
            "new_value",
            "replacement",
            "replace_value",
            "replacement_value",
        }:
            return "new_text"
        if normalized in {"sep", "separator"}:
            return "delimiter"
        if normalized in {"glob", "file_glob", "match_pattern", "filter", "include", "file_pattern"}:
            return "pattern"
        if normalized in {"name_prefix", "prefix_value", "rename_prefix", "prefix_text"}:
            return "prefix"
        if normalized in {"extension", "new_extension", "target_extension", "destination_extension"}:
            return "output_extension"
        if normalized in {"case", "name_case"}:
            return "filename_case"
        if normalized in {"input_text", "text_file", "input_text_file", "source_text_file"}:
            return "input_path"
        if normalized in {"output_text", "output_text_file", "target_text_file", "destination_text_file"}:
            return "output_path"
        if normalized in {"input_json", "json_file", "source_json"}:
            return "input_path"
        if normalized in {"output_json", "target_json", "destination_json"}:
            return "output_path"
        if normalized in {"input_csv", "csv_file", "source_csv"}:
            return "input_path"
        if normalized in {"output_csv", "target_csv", "destination_csv"}:
            return "output_path"
        if normalized in {"src_dir", "from_dir", "src_directory", "input_directory", "source_directory"}:
            return "input_dir"
        if normalized in {"dst_dir", "to_dir", "dst_directory", "output_directory", "target_directory", "destination_directory"}:
            return "output_dir"
        if normalized in {"source_dir", "input_folder", "source_folder"}:
            return "input_dir"
        if normalized in {"target_dir", "output_folder", "destination_dir"}:
            return "output_dir"
        if normalized == "destination":
            return "output_dir" if "list_files" in tool_names else "output_path"
        if normalized in {"input_file", "source_file"}:
            return "input_path"
        if normalized in {"output_file", "destination_file", "target_file"}:
            return "output_path"
        if normalized == "from":
            return "input_dir" if "list_files" in tool_names else "input_path"
        if normalized == "to":
            return "output_dir" if "list_files" in tool_names else "output_path"
        if normalized == "source_path":
            return "input_dir" if "list_files" in tool_names else "input_path"
        if normalized in {"target_path", "destination_path"}:
            return "output_dir" if "list_files" in tool_names else "output_path"
        if normalized == "source":
            return "input_dir" if "list_files" in tool_names else "input_path"
        if normalized == "target":
            return "output_dir" if "list_files" in tool_names else "output_path"
        if normalized in {"src", "src_path", "from_path"}:
            return "input_dir" if "list_files" in tool_names else "input_path"
        if normalized in {"dst", "dst_path", "to_path"}:
            return "output_dir" if "list_files" in tool_names else "output_path"
        if normalized == "path":
            if tool_name == "list_files":
                return "input_dir"
            if tool_name.startswith("write_"):
                return "output_path"
            if tool_name.startswith("read_") and "list_files" not in tool_names:
                return "input_path"
            return None
        if normalized == "file_path":
            if tool_name.startswith("read_"):
                return "input_path"
            if tool_name.startswith("write_"):
                return "output_path"
        return normalized

    def _check_overfit_artifacts(self, source: str, trajectory: Trajectory) -> list[SemanticIssue]:
        artifact_names = {Path(artifact).name for artifact in trajectory.artifacts}
        hardcoded = sorted(name for name in artifact_names if name and name in source)
        if not hardcoded:
            return []

        return [
            SemanticIssue(
                rule_id="artifact-overfit",
                severity="medium",
                message=(
                    "Skill appears to hardcode trajectory artifact names instead of parameterizing outputs: "
                    f"{hardcoded}."
                ),
            )
        ]

    def _tool_names_in_source(self, source: str) -> set[str]:
        return set(re.findall(r"tools\.([A-Za-z0-9_]+)\(", source))

    def _looks_like_template_skill(self, source: str) -> bool:
        markers = ['"inputs": inputs', '"steps_executed"', '"summary":', "missing = [key for key, value in inputs.items()"]
        return sum(marker in source for marker in markers) >= 2

    def _find_run_function(self, tree: ast.AST) -> ast.FunctionDef | None:
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == "run":
                return node
        return None
