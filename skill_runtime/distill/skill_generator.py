import json
import re
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from skill_runtime.api.models import SkillMetadata, Trajectory
from skill_runtime.distill.fallback.service import FallbackService
from skill_runtime.distill.rules import RULES
from skill_runtime.distill.rules.common import compact_step, escape, indent_docstring
from skill_runtime.distill.rules.common import infer_filename_prefix, infer_filename_suffix
from skill_runtime.distill.rules.registry import explain_match, get_rule_name, get_rule_priority


class SkillGenerationError(ValueError):
    pass


class SkillGenerator:
    def __init__(self, staging_dir: str | Path) -> None:
        self.staging_dir = Path(staging_dir)
        self.staging_dir.mkdir(parents=True, exist_ok=True)
        self.fallback_service = FallbackService(self.staging_dir)

    def generate(self, trajectory: Trajectory, skill_name: str | None = None) -> dict:
        if trajectory.final_status != "success":
            raise SkillGenerationError("only successful trajectories can be distilled")

        resolved_skill_name = skill_name or self._derive_skill_name(trajectory.task_description)
        summary = self._build_summary(trajectory.task_description)
        input_schema = self._infer_input_schema(trajectory)
        input_schema = self._augment_input_schema_for_rules(trajectory, input_schema)
        selected_rule = self._select_rule(trajectory, input_schema)
        output_schema = {
            "status": "str",
            "artifacts": "list[str]",
            "steps_executed": "int",
        }
        docstring = self._build_docstring(summary, input_schema, output_schema)
        code = self._build_skill_code(
            skill_name=resolved_skill_name,
            summary=summary,
            docstring=docstring,
            trajectory=trajectory,
            input_schema=input_schema,
            selected_rule=selected_rule,
        )
        fallback_artifact: str | None = None
        fallback_provider: str | None = None
        if not selected_rule:
            code, fallback_provider, fallback_artifact = self.fallback_service.generate(
                resolved_skill_name,
                summary,
                docstring,
                trajectory,
                input_schema,
            )

        skill_file = self.staging_dir / f"{resolved_skill_name}.py"
        skill_file.write_text(code, encoding="utf-8")

        metadata = SkillMetadata(
            skill_name=resolved_skill_name,
            file_path=str(skill_file.resolve()),
            summary=summary,
            docstring=docstring,
            input_schema=input_schema,
            output_schema=output_schema,
            source_trajectory_ids=[trajectory.task_id],
            created_at=datetime.now(timezone.utc).isoformat(),
            last_used_at=None,
            usage_count=0,
            status="staging",
            audit_score=None,
            rule_name=get_rule_name(selected_rule) if selected_rule else "llm_fallback",
            rule_priority=get_rule_priority(selected_rule) if selected_rule else 0,
            rule_reason=explain_match(selected_rule, trajectory, input_schema) if selected_rule else f"No deterministic rule matched; fallback provider {fallback_provider} generated a candidate skill.",
            tags=self._derive_tags(trajectory.task_description, input_schema),
        )

        metadata_file = self.staging_dir / f"{resolved_skill_name}.metadata.json"
        metadata_file.write_text(
            json.dumps(asdict(metadata), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        return {
            "skill_name": resolved_skill_name,
            "skill_file": skill_file,
            "metadata_file": metadata_file,
            "summary": summary,
            "metadata": metadata,
            "fallback_artifact": fallback_artifact,
            "fallback_provider": fallback_provider,
        }

    def _derive_skill_name(self, task_description: str) -> str:
        normalized = re.sub(r"[^A-Za-z0-9\u4e00-\u9fff]+", "_", task_description.strip().lower())
        normalized = normalized.strip("_")
        return (normalized or "generated_skill")[:64]

    def _build_summary(self, task_description: str) -> str:
        return task_description.strip().rstrip(".") + "."

    def _infer_input_schema(self, trajectory: Trajectory) -> dict[str, str]:
        keys: set[str] = set()
        tool_names = {step.tool_name.lower() for step in trajectory.steps}
        for step in trajectory.steps:
            for key in self._normalized_input_keys(step.tool_name.lower(), step.tool_input, tool_names):
                if self._looks_generalizable(key):
                    keys.add(key)
        if "list_files" in tool_names and self._infer_directory_output_dir(trajectory):
            keys.discard("output_path")
            keys.add("output_dir")
        inferred = {key: "str" for key in sorted(keys)}
        return inferred or {"task_input": "str"}

    def _looks_generalizable(self, key: str) -> bool:
        return key.lower() not in {"confirm", "retry", "timeout", "sleep", "debug", "path", "pattern"}

    def _normalized_input_keys(
        self,
        tool_name: str,
        tool_input: dict[str, str],
        tool_names: set[str],
    ) -> list[str]:
        normalized: list[str] = []
        for key in tool_input.keys():
            if key == "path":
                continue
            canonical_key = self._canonicalize_tool_input_key(tool_name, key, tool_names)
            if self._should_preserve_raw_input_key(key, canonical_key):
                normalized.append(key)
            if canonical_key and canonical_key not in normalized:
                normalized.append(canonical_key)

        rename_tools = {"rename_path", "rename_file", "move_file", "move_path"}
        if "path" not in tool_input and tool_name in rename_tools:
            source_path = self._path_alias_value(tool_input, "source")
            target_path = self._path_alias_value(tool_input, "target")
            inferred_filename_case = self._infer_filename_case_from_paths(source_path, target_path)
            if inferred_filename_case and "filename_case" not in normalized:
                normalized.append("filename_case")
            inferred_stem_replace = self._infer_stem_replace_from_paths(source_path, target_path)
            if inferred_stem_replace:
                if "old_text" not in normalized:
                    normalized.append("old_text")
                if "new_text" not in normalized:
                    normalized.append("new_text")
            inferred_suffix = self._infer_suffix_from_paths(source_path, target_path)
            if inferred_suffix and "suffix" not in normalized:
                normalized.append("suffix")
            inferred_output_extension = self._infer_output_extension_from_paths(source_path, target_path)
            if inferred_output_extension and "output_extension" not in normalized:
                normalized.append("output_extension")
            inferred_prefix = self._infer_prefix_from_paths(source_path, target_path)
            if (
                inferred_prefix
                and not inferred_filename_case
                and not inferred_stem_replace
                and not inferred_suffix
                and not inferred_output_extension
                and "prefix" not in normalized
            ):
                normalized.append("prefix")
            return normalized
        if "path" not in tool_input:
            return normalized

        if tool_name == "list_files":
            normalized.append("input_dir")
        elif tool_name.startswith("write_"):
            normalized.append("output_path")
        elif tool_name.startswith("read_") and "list_files" not in tool_names:
            normalized.append("input_path")

        return normalized

    def _canonicalize_tool_input_key(
        self,
        tool_name: str,
        key: str,
        tool_names: set[str],
    ) -> str | None:
        if key in {"input_dir", "output_dir", "input_path", "output_path", "prefix", "delimiter", "pattern", "output_extension", "filename_case"}:
            return None

        if key == "input":
            if tool_name in {"copy_file", "move_file", "rename_path", "move_path"}:
                return "input_dir" if "list_files" in tool_names else "input_path"
            return "input_path" if tool_name.startswith("read_") else None
        if key == "output":
            if tool_name in {"copy_file", "move_file", "rename_path", "move_path"}:
                return "output_dir" if "list_files" in tool_names else "output_path"
            return "output_path" if tool_name.startswith("write_") else None
        if key == "file":
            if tool_name.startswith("read_"):
                return "input_path"
            if tool_name.startswith("write_"):
                return "output_path"
            return None
        if key in {"old", "search", "search_text", "find_text", "old_value", "find", "search_value", "needle"}:
            return "old_text"
        if key in {
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
        if key in {"sep", "separator"}:
            return "delimiter"
        if key in {"glob", "file_glob", "match_pattern", "filter", "include", "file_pattern"}:
            return "pattern"
        if key in {"name_prefix", "prefix_value", "rename_prefix", "prefix_text"}:
            return "prefix"
        if key in {"extension", "new_extension", "target_extension", "destination_extension"}:
            return "output_extension"
        if key in {"case", "name_case"}:
            return "filename_case"
        if key in {"input_text", "text_file", "input_text_file", "source_text_file"}:
            return "input_path"
        if key in {"output_text", "output_text_file", "target_text_file", "destination_text_file"}:
            return "output_path"
        if key in {"input_json", "json_file", "source_json"}:
            return "input_path"
        if key in {"output_json", "target_json", "destination_json"}:
            return "output_path"
        if key in {"input_csv", "csv_file", "source_csv"}:
            return "input_path"
        if key in {"output_csv", "target_csv", "destination_csv"}:
            return "output_path"
        if key in {"src_dir", "from_dir", "src_directory", "input_directory", "source_directory"}:
            return "input_dir"
        if key in {"dst_dir", "to_dir", "dst_directory", "output_directory", "target_directory", "destination_directory"}:
            return "output_dir"
        if key in {"source_dir", "input_folder", "source_folder"}:
            return "input_dir"
        if key in {"target_dir", "output_folder", "destination_dir"}:
            return "output_dir"
        if key == "destination":
            return "output_dir" if "list_files" in tool_names else "output_path"
        if key in {"input_file", "source_file"}:
            return "input_path"
        if key in {"output_file", "destination_file", "target_file"}:
            return "output_path"
        if key == "from":
            return "input_dir" if "list_files" in tool_names else "input_path"
        if key == "to":
            return "output_dir" if "list_files" in tool_names else "output_path"
        if key == "source":
            return "input_dir" if "list_files" in tool_names else "input_path"
        if key == "target":
            return "output_dir" if "list_files" in tool_names else "output_path"
        if key in {"src", "src_path", "from_path"}:
            return "input_dir" if "list_files" in tool_names else "input_path"
        if key in {"dst", "dst_path", "to_path"}:
            return "output_dir" if "list_files" in tool_names else "output_path"

        if key == "source_path":
            return "input_dir" if "list_files" in tool_names else "input_path"
        if key in {"target_path", "destination_path"}:
            return "output_dir" if "list_files" in tool_names else "output_path"
        if key == "file_path" and tool_name.startswith("read_"):
            return "input_path"
        if key == "file_path" and tool_name.startswith("write_"):
            return "output_path"
        return None

    def _should_preserve_raw_input_key(self, key: str, canonical_key: str | None) -> bool:
        if canonical_key is None:
            return True
        semantic_aliases = {
            "input",
            "output",
            "file",
            "old",
            "new",
            "search",
            "replace",
            "search_text",
            "replace_text",
            "find_text",
            "replacement_text",
            "old_value",
            "new_value",
            "find",
            "search_value",
            "needle",
            "replacement",
            "replace_value",
            "replacement_value",
            "sep",
            "separator",
            "glob",
            "file_glob",
            "match_pattern",
            "filter",
            "include",
            "file_pattern",
            "name_prefix",
            "prefix_value",
            "rename_prefix",
            "prefix_text",
            "case",
            "name_case",
            "extension",
            "new_extension",
            "target_extension",
            "destination_extension",
            "input_text",
            "output_text",
            "text_file",
            "input_text_file",
            "output_text_file",
            "source_text_file",
            "target_text_file",
            "destination_text_file",
            "input_json",
            "output_json",
            "json_file",
            "source_json",
            "target_json",
            "destination_json",
            "input_csv",
            "output_csv",
            "csv_file",
            "source_csv",
            "target_csv",
            "destination_csv",
            "src_dir",
            "dst_dir",
            "from_dir",
            "to_dir",
            "src_directory",
            "dst_directory",
            "input_directory",
            "output_directory",
            "source_directory",
            "target_directory",
            "destination_directory",
            "from",
            "to",
            "source",
            "target",
            "src",
            "dst",
            "source_dir",
            "target_dir",
            "input_folder",
            "output_folder",
            "source_folder",
            "destination_dir",
            "destination",
            "input_file",
            "output_file",
            "source_file",
            "destination_file",
            "target_file",
            "source_path",
            "target_path",
            "destination_path",
            "src_path",
            "dst_path",
            "from_path",
            "to_path",
            "file_path",
        }
        return key not in semantic_aliases

    def _infer_prefix_from_paths(self, source_path: str | None, target_path: str | None) -> str | None:
        if not source_path or not target_path:
            return None

        source = Path(source_path)
        target = Path(target_path)
        if source.parent != target.parent or source.suffix != target.suffix:
            return None

        return infer_filename_prefix(source_path, target_path)

    def _infer_suffix_from_paths(self, source_path: str | None, target_path: str | None) -> str | None:
        if not source_path or not target_path:
            return None

        source = Path(source_path)
        target = Path(target_path)
        if source.parent != target.parent or source.suffix != target.suffix:
            return None

        return infer_filename_suffix(source_path, target_path)

    def _infer_output_extension_from_paths(self, source_path: str | None, target_path: str | None) -> str | None:
        if not source_path or not target_path:
            return None

        source = Path(source_path)
        target = Path(target_path)
        if source.parent != target.parent or source.stem != target.stem:
            return None
        if source.suffix == target.suffix:
            return None

        return target.suffix or None

    def _infer_filename_case_from_paths(self, source_path: str | None, target_path: str | None) -> str | None:
        if not source_path or not target_path:
            return None

        source = Path(source_path)
        target = Path(target_path)
        if source.parent != target.parent or source.name == target.name:
            return None
        if target.name == source.name.lower():
            return "lower"
        if target.name == source.name.upper():
            return "upper"

        return None

    def _infer_stem_replace_from_paths(
        self,
        source_path: str | None,
        target_path: str | None,
    ) -> tuple[str, str] | None:
        if not source_path or not target_path:
            return None

        source = Path(source_path)
        target = Path(target_path)
        if source.parent != target.parent or source.suffix != target.suffix or source.stem == target.stem:
            return None

        source_stem = source.stem
        target_stem = target.stem

        prefix_len = 0
        while (
            prefix_len < len(source_stem)
            and prefix_len < len(target_stem)
            and source_stem[prefix_len] == target_stem[prefix_len]
        ):
            prefix_len += 1

        suffix_len = 0
        max_suffix = min(len(source_stem), len(target_stem)) - prefix_len
        while (
            suffix_len < max_suffix
            and source_stem[len(source_stem) - 1 - suffix_len] == target_stem[len(target_stem) - 1 - suffix_len]
        ):
            suffix_len += 1

        source_mid_end = len(source_stem) - suffix_len if suffix_len else len(source_stem)
        target_mid_end = len(target_stem) - suffix_len if suffix_len else len(target_stem)
        old_text = source_stem[prefix_len:source_mid_end]
        new_text = target_stem[prefix_len:target_mid_end]
        if not old_text:
            return None
        if source_stem.replace(old_text, new_text, 1) != target_stem:
            return None

        return old_text, new_text

    def _path_alias_value(self, tool_input: dict[str, str], direction: str) -> str | None:
        aliases = {
            "source": ("source_path", "source", "src_path", "src", "from_path", "from", "input"),
            "target": (
                "target_path",
                "destination_path",
                "target",
                "destination",
                "dst_path",
                "dst",
                "to_path",
                "to",
                "output",
            ),
        }
        for key in aliases[direction]:
            value = tool_input.get(key)
            if value:
                return value
        return None

    def _infer_directory_output_dir(self, trajectory: Trajectory) -> str | None:
        input_dir = self._infer_directory_input_dir(trajectory)
        candidate_dirs: set[str] = set()
        for index, step in enumerate(trajectory.steps):
            output_path = self._step_output_path(step.tool_name.lower(), step.tool_input)
            if not output_path:
                continue

            source_path = self._nearest_read_path(trajectory.steps, index)
            if not source_path:
                continue

            if (
                Path(source_path).stem != Path(output_path).stem
                and not infer_filename_prefix(source_path, output_path)
                and not infer_filename_suffix(source_path, output_path)
            ):
                continue

            candidate_dirs.add(self._infer_common_output_root(source_path, output_path, input_dir))

        if len(candidate_dirs) == 1:
            return next(iter(candidate_dirs))
        return None

    def _infer_directory_input_dir(self, trajectory: Trajectory) -> str | None:
        candidates: set[str] = set()
        for step in trajectory.steps:
            if step.tool_name.lower() != "list_files":
                continue
            path = step.tool_input.get("path") or self._path_alias_value(step.tool_input, "source")
            if path:
                candidates.add(str(Path(path)).replace("\\", "/"))

        if len(candidates) == 1:
            return next(iter(candidates))
        return None

    def _infer_common_output_root(self, source_path: str, output_path: str, input_dir: str | None) -> str:
        output_parent = Path(output_path).parent
        if not input_dir:
            return str(output_parent).replace("\\", "/")

        try:
            relative_parent = Path(source_path).parent.relative_to(Path(input_dir))
        except ValueError:
            return str(output_parent).replace("\\", "/")

        if not relative_parent.parts:
            return str(output_parent).replace("\\", "/")
        if output_parent.parts[-len(relative_parent.parts) :] != relative_parent.parts:
            return str(output_parent).replace("\\", "/")
        return str(output_parent.parents[len(relative_parent.parts) - 1]).replace("\\", "/")

    def _nearest_read_path(self, steps, before_index: int) -> str | None:
        for step in reversed(steps[:before_index]):
            tool_name = step.tool_name.lower()
            if not tool_name.startswith("read_"):
                continue

            tool_input = step.tool_input
            path = tool_input.get("path")
            if path:
                return path

            aliased = self._path_alias_value(tool_input, "source")
            if aliased:
                return aliased
        return None

    def _step_output_path(self, tool_name: str, tool_input: dict[str, str]) -> str | None:
        if tool_name.startswith("write_"):
            path = tool_input.get("path")
            if path:
                return path

        aliased = self._path_alias_value(tool_input, "target")
        if aliased:
            return aliased
        return None

    def _augment_input_schema_for_rules(
        self,
        trajectory: Trajectory,
        input_schema: dict[str, str],
    ) -> dict[str, str]:
        updated = dict(input_schema)
        for rule in RULES:
            if rule.matches(trajectory, updated):
                updated = rule.augment_input_schema(trajectory, updated)
        return updated

    def _build_docstring(
        self,
        summary: str,
        input_schema: dict[str, str],
        output_schema: dict[str, str],
    ) -> str:
        input_lines = "\n".join(
            f"        - {name}: {type_name}" for name, type_name in input_schema.items()
        )
        output_lines = "\n".join(
            f"        - {name}: {type_name}" for name, type_name in output_schema.items()
        )
        return (
            f"功能描述:\n"
            f"    {summary}\n\n"
            f"输入参数:\n"
            f"{input_lines}\n\n"
            f"输出结果:\n"
            f"{output_lines}"
        )

    def _build_skill_code(
        self,
        skill_name: str,
        summary: str,
        docstring: str,
        trajectory: Trajectory,
        input_schema: dict[str, str],
        selected_rule,
    ) -> str:
        if selected_rule:
            return selected_rule.build_code(skill_name, summary, docstring, trajectory)
        return ""

    def _derive_tags(self, task_description: str, input_schema: dict[str, str]) -> list[str]:
        tokens = re.findall(r"[A-Za-z0-9_]+", task_description.lower())
        tags = sorted(set(token for token in tokens if len(token) >= 3))
        tags.extend(name.lower() for name in input_schema.keys())
        return sorted(set(tags))[:12]

    def _select_rule(self, trajectory: Trajectory, input_schema: dict[str, str]):
        for rule in RULES:
            if rule.matches(trajectory, input_schema):
                return rule
        return None
