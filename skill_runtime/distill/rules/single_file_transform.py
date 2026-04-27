from skill_runtime.api.models import Trajectory
from skill_runtime.distill.rules.common import escape, indent_docstring

RULE_NAME = "single_file_transform"
PRIORITY = 20


def matches(trajectory: Trajectory, input_schema: dict[str, str]) -> bool:
    tool_names = [step.tool_name.lower() for step in trajectory.steps]
    required_tools = {"read_text", "write_text"}
    required_inputs = {"input_path", "output_path"}
    return required_tools.issubset(set(tool_names)) and required_inputs.issubset(
        set(input_schema.keys())
    )


def explain_match(trajectory: Trajectory, input_schema: dict[str, str]) -> str:
    return "Matched single_file_transform because the trajectory reads one file and writes one file with input_path/output_path."


def augment_input_schema(trajectory: Trajectory, input_schema: dict[str, str]) -> dict[str, str]:
    updated = dict(input_schema)
    for step in trajectory.steps:
        if step.tool_name.lower() == "write_text" and "newline" in step.tool_input:
            updated.setdefault("newline", "str")
    return updated


def build_code(skill_name: str, summary: str, docstring: str, trajectory: Trajectory) -> str:
    default_artifact = trajectory.artifacts[0] if trajectory.artifacts else "output.txt"
    observed_newline = next(
        (step.tool_input.get("newline") for step in trajectory.steps if step.tool_name.lower() == "write_text" and "newline" in step.tool_input),
        None,
    )
    return f'''def run(tools, **kwargs):
    """
{indent_docstring(docstring)}
    """
    input_path = kwargs.get("input_path")
    output_path = kwargs.get("output_path")
    newline = kwargs.get("newline", {repr(observed_newline)})

    missing = [
        name
        for name, value in {{"input_path": input_path, "output_path": output_path}}.items()
        if not value
    ]
    if missing:
        raise ValueError(f"Missing required inputs: {{missing}}")

    text = tools.read_text(input_path)
    transformed = text.rstrip() + "\\n"
    tools.write_text(output_path, transformed, newline=newline)

    return {{
        "status": "completed",
        "skill_name": "{skill_name}",
        "summary": "{escape(summary)}",
        "artifacts": [output_path or "{escape(default_artifact)}"],
        "steps_executed": {len(trajectory.steps)},
        "output_path": output_path,
    }}
'''
