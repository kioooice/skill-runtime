from skill_runtime.api.models import Trajectory
from skill_runtime.distill.rules.common import escape, indent_docstring

RULE_NAME = "batch_rename_case"
PRIORITY = 76


def matches(trajectory: Trajectory, input_schema: dict[str, str]) -> bool:
    description = trajectory.task_description.lower()
    tool_names = {step.tool_name.lower() for step in trajectory.steps}
    rename_tools = {"rename_path", "rename_file", "move_file", "move_path"}
    required_inputs = {"input_dir", "filename_case"}
    return (
        "list_files" in tool_names
        and bool(rename_tools & tool_names)
        and required_inputs.issubset(set(input_schema.keys()))
        and "rename" in description
        and "case" in description
    )


def explain_match(trajectory: Trajectory, input_schema: dict[str, str]) -> str:
    return "Matched batch_rename_case because the trajectory lists files, renames paths, and provides input_dir/filename_case inputs."


def _observed_pattern(trajectory: Trajectory) -> str | None:
    for step in trajectory.steps:
        for key in ("pattern", "glob", "file_glob", "match_pattern", "filter", "include", "file_pattern"):
            pattern = step.tool_input.get(key)
            if pattern:
                return pattern
    return None


def augment_input_schema(trajectory: Trajectory, input_schema: dict[str, str]) -> dict[str, str]:
    updated = dict(input_schema)
    updated.pop("output_dir", None)
    if _observed_pattern(trajectory):
        updated.setdefault("pattern", "str")
    updated.setdefault("filename_case", "str")
    return updated


def build_code(skill_name: str, summary: str, docstring: str, trajectory: Trajectory) -> str:
    default_pattern = _observed_pattern(trajectory) or "*"

    return f'''from pathlib import Path


def run(tools, **kwargs):
    """
{indent_docstring(docstring)}
    """
    input_dir = kwargs.get("input_dir")
    filename_case = kwargs.get("filename_case")
    pattern = kwargs.get("pattern", "{escape(default_pattern)}")

    missing = [
        name
        for name, value in {{
            "input_dir": input_dir,
            "filename_case": filename_case,
        }}.items()
        if value is None or value == ""
    ]
    if missing:
        raise ValueError(f"Missing required inputs: {{missing}}")

    normalized_case = str(filename_case).lower()
    if normalized_case not in {{"lower", "upper"}}:
        raise ValueError("filename_case must be 'lower' or 'upper'")

    renamed = []
    for file_path in tools.list_files(input_dir, pattern):
        source = Path(file_path)
        transformed_name = source.name.lower() if normalized_case == "lower" else source.name.upper()
        target = source.with_name(transformed_name)
        tools.rename_path(file_path, str(target))
        renamed.append(str(target))

    return {{
        "status": "completed",
        "skill_name": "{skill_name}",
        "summary": "{escape(summary)}",
        "artifacts": renamed,
        "steps_executed": {len(trajectory.steps)},
        "renamed_files": len(renamed),
        "pattern": pattern,
    }}
'''
