from skill_runtime.api.models import Trajectory
from skill_runtime.distill.rules.common import escape, indent_docstring

RULE_NAME = "directory_move"
PRIORITY = 85


def matches(trajectory: Trajectory, input_schema: dict[str, str]) -> bool:
    description = trajectory.task_description.lower()
    tool_names = {step.tool_name.lower() for step in trajectory.steps}
    required_inputs = {"input_dir", "output_dir"}
    move_tools = {"move_file", "rename_path", "move_path"}
    return (
        "list_files" in tool_names
        and bool(move_tools & tool_names)
        and required_inputs.issubset(set(input_schema.keys()))
        and "move" in description
    )


def explain_match(trajectory: Trajectory, input_schema: dict[str, str]) -> str:
    return "Matched directory_move because the trajectory lists files, moves paths, and targets input_dir/output_dir."


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
    return updated


def _selected_move_tool(trajectory: Trajectory) -> str:
    observed_tools = [step.tool_name.lower() for step in trajectory.steps if step.status == "success"]
    for tool_name in ("rename_path", "move_file", "move_path"):
        if tool_name in observed_tools:
            return tool_name
    return "move_file"


def build_code(skill_name: str, summary: str, docstring: str, trajectory: Trajectory) -> str:
    default_pattern = _observed_pattern(trajectory) or "*"
    move_tool = _selected_move_tool(trajectory)

    return f'''from pathlib import Path


def run(tools, **kwargs):
    """
{indent_docstring(docstring)}
    """
    input_dir = kwargs.get("input_dir")
    output_dir = kwargs.get("output_dir")
    pattern = kwargs.get("pattern", "{escape(default_pattern)}")

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

    moved = []
    for file_path in tools.list_files(input_dir, pattern):
        source = Path(file_path)
        target = Path(output_dir) / source.name
        tools.{move_tool}(file_path, str(target))
        moved.append(str(target))

    return {{
        "status": "completed",
        "skill_name": "{escape(skill_name)}",
        "summary": "{escape(summary)}",
        "artifacts": moved,
        "steps_executed": {len(trajectory.steps)},
        "moved_files": len(moved),
        "pattern": pattern,
    }}
'''
