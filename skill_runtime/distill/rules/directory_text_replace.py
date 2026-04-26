from skill_runtime.api.models import Trajectory
from skill_runtime.distill.rules.common import escape, indent_docstring

RULE_NAME = "directory_text_replace"
PRIORITY = 100


def matches(trajectory: Trajectory, input_schema: dict[str, str]) -> bool:
    description = trajectory.task_description.lower()
    tool_names = {step.tool_name.lower() for step in trajectory.steps}
    required_inputs = {"input_dir", "output_dir", "old_text", "new_text"}
    return (
        "list_files" in tool_names
        and "read_text" in tool_names
        and "write_text" in tool_names
        and required_inputs.issubset(set(input_schema.keys()))
        and "replace" in description
        and "directory" in description
    )


def explain_match(trajectory: Trajectory, input_schema: dict[str, str]) -> str:
    return "Matched directory_text_replace because the trajectory processes multiple files in a directory and replaces text across them."


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
    updated.setdefault("old_text", "str")
    updated.setdefault("new_text", "str")
    return updated


def build_code(skill_name: str, summary: str, docstring: str, trajectory: Trajectory) -> str:
    default_pattern = _observed_pattern(trajectory) or "*"

    return f'''from pathlib import Path


def run(tools, **kwargs):
    """
{indent_docstring(docstring)}
    """
    input_dir = kwargs.get("input_dir")
    output_dir = kwargs.get("output_dir")
    old_text = kwargs.get("old_text")
    new_text = kwargs.get("new_text")
    pattern = kwargs.get("pattern", "{escape(default_pattern)}")

    missing = [
        name
        for name, value in {{
            "input_dir": input_dir,
            "output_dir": output_dir,
            "old_text": old_text,
            "new_text": new_text,
        }}.items()
        if value is None or value == ""
    ]
    if missing:
        raise ValueError(f"Missing required inputs: {{missing}}")

    written = []
    for file_path in tools.list_files(input_dir, pattern):
        source = Path(file_path)
        target = Path(output_dir) / source.name
        text = tools.read_text(file_path)
        transformed = text.replace(old_text, new_text)
        tools.write_text(str(target), transformed)
        written.append(str(target))

    return {{
        "status": "completed",
        "skill_name": "{skill_name}",
        "summary": "{escape(summary)}",
        "artifacts": written,
        "steps_executed": {len(trajectory.steps)},
        "processed_files": len(written),
        "pattern": pattern,
    }}
'''
