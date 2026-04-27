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
    updated = dict(input_schema)
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
    default_artifact = trajectory.artifacts[0] if trajectory.artifacts else "output.json"
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
    return f'''def run(tools, **kwargs):
    """
{indent_docstring(docstring)}
    """
    input_path = kwargs.get("input_path")
    output_path = kwargs.get("output_path")
    ensure_ascii = kwargs.get("ensure_ascii", {repr(observed_ensure_ascii)})
    indent = int(kwargs.get("indent", {repr(observed_indent)}))
    sort_keys = kwargs.get("sort_keys", {repr(observed_sort_keys)})
    normalized_ensure_ascii = ensure_ascii if isinstance(ensure_ascii, bool) else str(ensure_ascii).lower() == "true"
    normalized_sort_keys = sort_keys if isinstance(sort_keys, bool) else str(sort_keys).lower() == "true"

    missing = [
        name
        for name, value in {{"input_path": input_path, "output_path": output_path}}.items()
        if not value
    ]
    if missing:
        raise ValueError(f"Missing required inputs: {{missing}}")

    payload = tools.read_json(input_path)
    tools.write_json(
        output_path,
        payload,
        ensure_ascii=normalized_ensure_ascii,
        indent=indent,
        sort_keys=normalized_sort_keys,
    )

    return {{
        "status": "completed",
        "skill_name": "{escape(skill_name)}",
        "summary": "{escape(summary)}",
        "artifacts": [output_path or "{escape(default_artifact)}"],
        "steps_executed": {len(trajectory.steps)},
        "output_path": output_path,
    }}
'''
