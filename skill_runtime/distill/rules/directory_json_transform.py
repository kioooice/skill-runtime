from skill_runtime.api.models import Trajectory
from skill_runtime.distill.rules.common import (
    escape,
    indent_docstring,
    infer_observed_filename_affix,
)

RULE_NAME = "directory_json_transform"
PRIORITY = 60


def matches(trajectory: Trajectory, input_schema: dict[str, str]) -> bool:
    tool_names = {step.tool_name.lower() for step in trajectory.steps}
    required_inputs = {"input_dir", "output_dir"}
    return (
        "list_files" in tool_names
        and "read_json" in tool_names
        and "write_json" in tool_names
        and required_inputs.issubset(set(input_schema.keys()))
    )


def explain_match(trajectory: Trajectory, input_schema: dict[str, str]) -> str:
    return "Matched directory_json_transform because the trajectory lists files, reads JSON files, and writes JSON files into an output directory."


def _observed_pattern(trajectory: Trajectory) -> str | None:
    for step in trajectory.steps:
        for key in ("pattern", "glob", "file_glob", "match_pattern", "filter", "include", "file_pattern"):
            pattern = step.tool_input.get(key)
            if pattern:
                return pattern
    return None


def augment_input_schema(trajectory: Trajectory, input_schema: dict[str, str]) -> dict[str, str]:
    updated = dict(input_schema)
    if _observed_pattern(trajectory):
        updated.setdefault("pattern", "str")
    observed_prefix = infer_observed_filename_affix(
        trajectory.steps,
        read_tools={"read_json"},
        write_tools={"write_json"},
        mode="prefix",
    )
    if observed_prefix is not None:
        updated.setdefault("prefix", "str")
    observed_suffix = infer_observed_filename_affix(
        trajectory.steps,
        read_tools={"read_json"},
        write_tools={"write_json"},
        mode="suffix",
    )
    if observed_suffix is not None:
        updated.setdefault("suffix", "str")
    for step in trajectory.steps:
        if step.tool_name.lower() != "write_json":
            continue
        if "ensure_ascii" in step.tool_input:
            updated.setdefault("ensure_ascii", "str")
        if "indent" in step.tool_input:
            updated.setdefault("indent", "str")
        if "sort_keys" in step.tool_input:
            updated.setdefault("sort_keys", "str")
    return updated


def build_code(skill_name: str, summary: str, docstring: str, trajectory: Trajectory) -> str:
    default_pattern = _observed_pattern(trajectory) or "*.json"
    observed_ensure_ascii = next(
        (step.tool_input.get("ensure_ascii") for step in trajectory.steps if step.tool_name.lower() == "write_json" and "ensure_ascii" in step.tool_input),
        False,
    )
    observed_indent = next(
        (step.tool_input.get("indent") for step in trajectory.steps if step.tool_name.lower() == "write_json" and "indent" in step.tool_input),
        2,
    )
    observed_sort_keys = next(
        (step.tool_input.get("sort_keys") for step in trajectory.steps if step.tool_name.lower() == "write_json" and "sort_keys" in step.tool_input),
        False,
    )
    observed_prefix = infer_observed_filename_affix(
        trajectory.steps,
        read_tools={"read_json"},
        write_tools={"write_json"},
        mode="prefix",
    )
    observed_suffix = infer_observed_filename_affix(
        trajectory.steps,
        read_tools={"read_json"},
        write_tools={"write_json"},
        mode="suffix",
    )

    return f'''from pathlib import Path


def run(tools, **kwargs):
    """
{indent_docstring(docstring)}
    """
    input_dir = kwargs.get("input_dir")
    output_dir = kwargs.get("output_dir")
    pattern = kwargs.get("pattern", "{escape(default_pattern)}")
    ensure_ascii = kwargs.get("ensure_ascii", {repr(observed_ensure_ascii)})
    indent = int(kwargs.get("indent", {repr(observed_indent)}))
    sort_keys = kwargs.get("sort_keys", {repr(observed_sort_keys)})
    prefix = kwargs.get("prefix", {repr(observed_prefix)})
    suffix = kwargs.get("suffix", {repr(observed_suffix)})
    normalized_ensure_ascii = ensure_ascii if isinstance(ensure_ascii, bool) else str(ensure_ascii).lower() == "true"
    normalized_sort_keys = sort_keys if isinstance(sort_keys, bool) else str(sort_keys).lower() == "true"
    normalized_prefix = "" if prefix is None else str(prefix)
    normalized_suffix = "" if suffix is None else str(suffix)

    missing = [
        name
        for name, value in {{
            "input_dir": input_dir,
            "output_dir": output_dir,
        }}.items()
        if not value
    ]
    if missing:
        raise ValueError(f"Missing required inputs: {{missing}}")

    input_root = Path(tools.resolve_path(input_dir))
    written = []
    for file_path in tools.list_files(input_dir, pattern):
        source = Path(file_path)
        relative_parent = source.relative_to(input_root).parent
        target = Path(output_dir) / relative_parent / f"{{normalized_prefix}}{{source.stem}}{{normalized_suffix}}{{source.suffix}}"
        payload = tools.read_json(file_path)
        tools.write_json(
            str(target),
            payload,
            ensure_ascii=normalized_ensure_ascii,
            indent=indent,
            sort_keys=normalized_sort_keys,
        )
        written.append(str(target))

    return {{
        "status": "completed",
        "skill_name": "{escape(skill_name)}",
        "summary": "{escape(summary)}",
        "artifacts": written,
        "steps_executed": {len(trajectory.steps)},
        "processed_files": len(written),
        "pattern": pattern,
    }}
'''
