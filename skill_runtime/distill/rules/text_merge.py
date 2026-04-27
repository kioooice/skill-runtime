from skill_runtime.api.models import Trajectory
from skill_runtime.distill.rules.common import escape, indent_docstring

RULE_NAME = "text_merge"
PRIORITY = 70


def matches(trajectory: Trajectory, input_schema: dict[str, str]) -> bool:
    tool_names = [step.tool_name.lower() for step in trajectory.steps]
    description = trajectory.task_description.lower()
    required_tools = {"list_files", "read_text", "write_text"}
    required_inputs = {"input_dir", "output_path"}
    return (
        required_tools.issubset(set(tool_names))
        and required_inputs.issubset(set(input_schema.keys()))
        and "merge" in description
        and "txt" in description
    )


def explain_match(trajectory: Trajectory, input_schema: dict[str, str]) -> str:
    return "Matched text_merge because the trajectory lists files, reads text, writes text, and the task description mentions merging txt files."


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
    for step in trajectory.steps:
        if step.tool_name.lower() == "write_text" and "newline" in step.tool_input:
            updated.setdefault("newline", "str")
    return updated


def build_code(skill_name: str, summary: str, docstring: str, trajectory: Trajectory) -> str:
    default_artifact = trajectory.artifacts[0] if trajectory.artifacts else "output.md"
    default_pattern = _observed_pattern(trajectory) or "*.txt"
    observed_newline = next(
        (step.tool_input.get("newline") for step in trajectory.steps if step.tool_name.lower() == "write_text" and "newline" in step.tool_input),
        None,
    )

    return f'''from pathlib import Path


def run(tools, **kwargs):
    """
{indent_docstring(docstring)}
    """
    input_dir = kwargs.get("input_dir")
    output_path = kwargs.get("output_path")
    pattern = kwargs.get("pattern", "{escape(default_pattern)}")
    newline = kwargs.get("newline", {repr(observed_newline)})

    missing = [
        name
        for name, value in {{"input_dir": input_dir, "output_path": output_path}}.items()
        if not value
    ]
    if missing:
        raise ValueError(f"Missing required inputs: {{missing}}")

    files = tools.list_files(input_dir, pattern)
    contents = []
    for file_path in files:
        name = Path(file_path).name
        text = tools.read_text(file_path).strip()
        contents.append(f"# {{name}}\\n\\n{{text}}\\n")

    merged = "\\n".join(contents).strip() + "\\n"
    tools.write_text(output_path, merged, newline=newline)

    return {{
        "status": "completed",
        "skill_name": "{skill_name}",
        "summary": "{escape(summary)}",
        "artifacts": [output_path or "{escape(default_artifact)}"],
        "steps_executed": {len(trajectory.steps)},
        "merged_files": len(files),
        "pattern": pattern,
    }}
'''
