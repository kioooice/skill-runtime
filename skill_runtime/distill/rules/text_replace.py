from skill_runtime.api.models import Trajectory
from skill_runtime.distill.rules.common import escape, indent_docstring

RULE_NAME = "text_replace"
PRIORITY = 90


def matches(trajectory: Trajectory, input_schema: dict[str, str]) -> bool:
    description = trajectory.task_description.lower()
    tool_names = [step.tool_name.lower() for step in trajectory.steps]
    required_tools = {"read_text", "write_text"}
    required_inputs = {"input_path", "output_path", "old_text", "new_text"}
    return (
        required_tools.issubset(set(tool_names))
        and required_inputs.issubset(set(input_schema.keys()))
        and "replace" in description
    )


def explain_match(trajectory: Trajectory, input_schema: dict[str, str]) -> str:
    return "Matched text_replace because the trajectory reads and writes one file, includes old_text/new_text inputs, and the task description mentions replacement."


def augment_input_schema(trajectory: Trajectory, input_schema: dict[str, str]) -> dict[str, str]:
    updated = dict(input_schema)
    updated.setdefault("old_text", "str")
    updated.setdefault("new_text", "str")
    return updated


def build_code(skill_name: str, summary: str, docstring: str, trajectory: Trajectory) -> str:
    default_artifact = trajectory.artifacts[0] if trajectory.artifacts else "output.txt"
    return f'''def run(tools, **kwargs):
    """
{indent_docstring(docstring)}
    """
    input_path = kwargs.get("input_path")
    output_path = kwargs.get("output_path")
    old_text = kwargs.get("old_text")
    new_text = kwargs.get("new_text")

    missing = [
        name
        for name, value in {{
            "input_path": input_path,
            "output_path": output_path,
            "old_text": old_text,
            "new_text": new_text,
        }}.items()
        if value is None
    ]
    if missing:
        raise ValueError(f"Missing required inputs: {{missing}}")

    text = tools.read_text(input_path)
    transformed = text.replace(old_text, new_text)
    tools.write_text(output_path, transformed)

    return {{
        "status": "completed",
        "skill_name": "{skill_name}",
        "summary": "{escape(summary)}",
        "artifacts": [output_path or "{escape(default_artifact)}"],
        "steps_executed": {len(trajectory.steps)},
        "replaced_text": old_text,
    }}
'''
