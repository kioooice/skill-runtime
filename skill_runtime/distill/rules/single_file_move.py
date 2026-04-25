from skill_runtime.api.models import Trajectory
from skill_runtime.distill.rules.common import escape, indent_docstring

RULE_NAME = "single_file_move"
PRIORITY = 65


def matches(trajectory: Trajectory, input_schema: dict[str, str]) -> bool:
    description = trajectory.task_description.lower()
    tool_names = {step.tool_name.lower() for step in trajectory.steps}
    move_tools = {"move_file", "rename_path", "move_path"}
    required_inputs = {"input_path", "output_path"}
    return (
        "list_files" not in tool_names
        and bool(move_tools & tool_names)
        and required_inputs.issubset(set(input_schema.keys()))
        and ("move" in description or "rename" in description)
    )


def explain_match(trajectory: Trajectory, input_schema: dict[str, str]) -> str:
    return "Matched single_file_move because the trajectory moves one file with input_path/output_path."


def augment_input_schema(trajectory: Trajectory, input_schema: dict[str, str]) -> dict[str, str]:
    return dict(input_schema)


def _selected_move_tool(trajectory: Trajectory) -> str:
    observed_tools = [step.tool_name.lower() for step in trajectory.steps if step.status == "success"]
    for tool_name in ("rename_path", "move_file", "move_path"):
        if tool_name in observed_tools:
            return tool_name
    return "move_file"


def build_code(skill_name: str, summary: str, docstring: str, trajectory: Trajectory) -> str:
    move_tool = _selected_move_tool(trajectory)
    default_artifact = "moved_output.txt"
    return f'''def run(tools, **kwargs):
    """
{indent_docstring(docstring)}
    """
    input_path = kwargs.get("input_path")
    output_path = kwargs.get("output_path")

    missing = [
        name
        for name, value in {{"input_path": input_path, "output_path": output_path}}.items()
        if not value
    ]
    if missing:
        raise ValueError(f"Missing required inputs: {{missing}}")

    tools.{move_tool}(input_path, output_path)

    return {{
        "status": "completed",
        "skill_name": "{escape(skill_name)}",
        "summary": "{escape(summary)}",
        "artifacts": [output_path or "{escape(default_artifact)}"],
        "steps_executed": {len(trajectory.steps)},
        "output_path": output_path,
    }}
'''
