from skill_runtime.api.models import Trajectory
from skill_runtime.distill.rules.common import escape, indent_docstring

RULE_NAME = "single_json_transform"
PRIORITY = 30


def matches(trajectory: Trajectory, input_schema: dict[str, str]) -> bool:
    tool_names = {step.tool_name.lower() for step in trajectory.steps}
    required_inputs = {"input_path", "output_path"}
    return (
        "read_json" in tool_names
        and "write_json" in tool_names
        and required_inputs.issubset(set(input_schema.keys()))
    )


def explain_match(trajectory: Trajectory, input_schema: dict[str, str]) -> str:
    return "Matched single_json_transform because the trajectory reads one JSON file and writes one JSON file."


def augment_input_schema(trajectory: Trajectory, input_schema: dict[str, str]) -> dict[str, str]:
    return dict(input_schema)


def build_code(skill_name: str, summary: str, docstring: str, trajectory: Trajectory) -> str:
    default_artifact = trajectory.artifacts[0] if trajectory.artifacts else "output.json"
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

    payload = tools.read_json(input_path)
    tools.write_json(output_path, payload)

    return {{
        "status": "completed",
        "skill_name": "{escape(skill_name)}",
        "summary": "{escape(summary)}",
        "artifacts": [output_path or "{escape(default_artifact)}"],
        "steps_executed": {len(trajectory.steps)},
        "output_path": output_path,
    }}
'''
