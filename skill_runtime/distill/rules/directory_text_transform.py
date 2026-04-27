from skill_runtime.api.models import Trajectory
from skill_runtime.distill.rules.common import (
    escape,
    indent_docstring,
    infer_observed_filename_affix,
)

RULE_NAME = "directory_text_transform"
PRIORITY = 50


def matches(trajectory: Trajectory, input_schema: dict[str, str]) -> bool:
    tool_names = {step.tool_name.lower() for step in trajectory.steps}
    required_inputs = {"input_dir", "output_dir"}
    return (
        "list_files" in tool_names
        and "read_text" in tool_names
        and "write_text" in tool_names
        and required_inputs.issubset(set(input_schema.keys()))
    )


def explain_match(trajectory: Trajectory, input_schema: dict[str, str]) -> str:
    return "Matched directory_text_transform because the trajectory lists files, reads text files, and writes transformed text files into an output directory."


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
        read_tools={"read_text"},
        write_tools={"write_text"},
        mode="prefix",
    )
    if observed_prefix is not None:
        updated.setdefault("prefix", "str")
    observed_suffix = infer_observed_filename_affix(
        trajectory.steps,
        read_tools={"read_text"},
        write_tools={"write_text"},
        mode="suffix",
    )
    if observed_suffix is not None:
        updated.setdefault("suffix", "str")
    for step in trajectory.steps:
        if step.tool_name.lower() == "write_text" and "newline" in step.tool_input:
            updated.setdefault("newline", "str")
    return updated


def build_code(skill_name: str, summary: str, docstring: str, trajectory: Trajectory) -> str:
    default_pattern = _observed_pattern(trajectory) or "*.txt"
    observed_newline = next(
        (step.tool_input.get("newline") for step in trajectory.steps if step.tool_name.lower() == "write_text" and "newline" in step.tool_input),
        None,
    )
    observed_prefix = infer_observed_filename_affix(
        trajectory.steps,
        read_tools={"read_text"},
        write_tools={"write_text"},
        mode="prefix",
    )
    observed_suffix = infer_observed_filename_affix(
        trajectory.steps,
        read_tools={"read_text"},
        write_tools={"write_text"},
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
    newline = kwargs.get("newline", {repr(observed_newline)})
    prefix = kwargs.get("prefix", {repr(observed_prefix)})
    suffix = kwargs.get("suffix", {repr(observed_suffix)})
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
        text = tools.read_text(file_path)
        transformed = text.rstrip() + "\\n"
        tools.write_text(str(target), transformed, newline=newline)
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
