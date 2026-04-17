from skill_runtime.api.models import Trajectory
from skill_runtime.distill.rules.common import escape, indent_docstring

RULE_NAME = "batch_rename"
PRIORITY = 80


def matches(trajectory: Trajectory, input_schema: dict[str, str]) -> bool:
    description = trajectory.task_description.lower()
    tool_names = {step.tool_name.lower() for step in trajectory.steps}
    rename_tools = {"rename_path", "rename_file", "move_file", "move_path"}
    required_inputs = {"input_dir", "prefix"}
    return (
        "list_files" in tool_names
        and bool(rename_tools & tool_names)
        and required_inputs.issubset(set(input_schema.keys()))
        and "rename" in description
    )


def explain_match(trajectory: Trajectory, input_schema: dict[str, str]) -> str:
    return "Matched batch_rename because the trajectory lists files, renames paths, and provides input_dir/prefix inputs."


def augment_input_schema(trajectory: Trajectory, input_schema: dict[str, str]) -> dict[str, str]:
    updated = dict(input_schema)
    updated.setdefault("pattern", "str")
    updated.setdefault("prefix", "str")
    return updated


def build_code(skill_name: str, summary: str, docstring: str, trajectory: Trajectory) -> str:
    default_pattern = "*"
    for step in trajectory.steps:
        pattern = step.tool_input.get("pattern")
        if pattern:
            default_pattern = pattern
            break

    return f'''from pathlib import Path


def run(tools, **kwargs):
    """
{indent_docstring(docstring)}
    """
    input_dir = kwargs.get("input_dir")
    prefix = kwargs.get("prefix")
    pattern = kwargs.get("pattern", "{escape(default_pattern)}")

    missing = [
        name
        for name, value in {{
            "input_dir": input_dir,
            "prefix": prefix,
        }}.items()
        if not value
    ]
    if missing:
        raise ValueError(f"Missing required inputs: {{missing}}")

    renamed = []
    for file_path in tools.list_files(input_dir, pattern):
        source = Path(file_path)
        target = source.with_name(prefix + source.name)
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
