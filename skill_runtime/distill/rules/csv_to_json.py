from skill_runtime.api.models import Trajectory
from skill_runtime.distill.rules.common import escape, indent_docstring

RULE_NAME = "csv_to_json"
PRIORITY = 75


def matches(trajectory: Trajectory, input_schema: dict[str, str]) -> bool:
    description = trajectory.task_description.lower()
    tool_names = {step.tool_name.lower() for step in trajectory.steps}
    required_inputs = {"input_path", "output_path"}
    return (
        "read_text" in tool_names
        and "write_json" in tool_names
        and required_inputs.issubset(set(input_schema.keys()))
        and "csv" in description
        and "json" in description
    )


def explain_match(trajectory: Trajectory, input_schema: dict[str, str]) -> str:
    return "Matched csv_to_json because the trajectory reads text, writes JSON, and the task description mentions CSV and JSON."


def augment_input_schema(trajectory: Trajectory, input_schema: dict[str, str]) -> dict[str, str]:
    updated = dict(input_schema)
    delimiter = _observed_delimiter(trajectory)
    if delimiter is not None or "delimiter" in updated:
        updated["delimiter"] = "str"
    return updated


def _observed_delimiter(trajectory: Trajectory) -> str | None:
    for step in trajectory.steps:
        if step.tool_name.lower() != "read_text":
            continue
        value = step.tool_input.get("delimiter")
        if value:
            return value
        for alias in ("sep", "separator"):
            value = step.tool_input.get(alias)
            if value:
                return value
    return None


def build_code(skill_name: str, summary: str, docstring: str, trajectory: Trajectory) -> str:
    default_artifact = trajectory.artifacts[0] if trajectory.artifacts else "output.json"
    default_delimiter = escape(_observed_delimiter(trajectory) or ",")
    return f'''import csv
from io import StringIO


def run(tools, **kwargs):
    """
{indent_docstring(docstring)}
    """
    input_path = kwargs.get("input_path")
    output_path = kwargs.get("output_path")
    delimiter = kwargs.get("delimiter", "{default_delimiter}")

    missing = [
        name
        for name, value in {{"input_path": input_path, "output_path": output_path}}.items()
        if not value
    ]
    if missing:
        raise ValueError(f"Missing required inputs: {{missing}}")

    csv_text = tools.read_text(input_path)
    reader = csv.DictReader(StringIO(csv_text), delimiter=delimiter)
    rows = list(reader)
    tools.write_json(output_path, rows)

    return {{
        "status": "completed",
        "skill_name": "{escape(skill_name)}",
        "summary": "{escape(summary)}",
        "artifacts": [output_path or "{escape(default_artifact)}"],
        "steps_executed": {len(trajectory.steps)},
        "rows": len(rows),
    }}
'''
