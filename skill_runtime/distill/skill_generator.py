import json
import re
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from skill_runtime.api.models import SkillMetadata, Trajectory
from skill_runtime.distill.fallback.service import FallbackService
from skill_runtime.distill.rules import RULES
from skill_runtime.distill.rules.common import compact_step, escape, indent_docstring
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
            normalized.append(key)
            canonical_key = self._canonicalize_tool_input_key(tool_name, key, tool_names)
            if canonical_key and canonical_key not in normalized:
                normalized.append(canonical_key)

        if "path" not in tool_input:
            inferred_prefix = self._infer_prefix_from_paths(
                tool_input.get("source_path"),
                tool_input.get("target_path"),
            )
            if inferred_prefix and "prefix" not in normalized:
                normalized.append("prefix")
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
        if key in {"input_dir", "output_dir", "input_path", "output_path", "prefix"}:
            return None

        if key in {"source_dir", "input_folder", "source_folder"}:
            return "input_dir"
        if key in {"target_dir", "output_folder", "destination_dir"}:
            return "output_dir"
        if key in {"input_file", "source_file"}:
            return "input_path"
        if key in {"output_file", "destination_file", "target_file"}:
            return "output_path"
        if key == "source":
            if tool_name in {"copy_file", "move_file", "rename_path", "move_path"}:
                return "input_path"
            return "input_dir" if "list_files" in tool_names else "input_path"
        if key == "target":
            if tool_name in {"copy_file", "move_file", "rename_path", "move_path"}:
                return "output_path"
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

    def _infer_prefix_from_paths(self, source_path: str | None, target_path: str | None) -> str | None:
        if not source_path or not target_path:
            return None

        source = Path(source_path)
        target = Path(target_path)
        if source.parent != target.parent:
            return None

        source_name = source.name
        target_name = target.name
        if target_name == source_name or not target_name.endswith(source_name):
            return None

        prefix = target_name[: -len(source_name)]
        return prefix or None

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
