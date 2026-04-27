from skill_runtime.api.models import Trajectory
from skill_runtime.distill.rules.common import (
    escape,
    indent_docstring,
    infer_observed_filename_affix,
)

RULE_NAME = "directory_json_to_csv"
PRIORITY = 74


def matches(trajectory: Trajectory, input_schema: dict[str, str]) -> bool:
    description = trajectory.task_description.lower()
    tool_names = {step.tool_name.lower() for step in trajectory.steps}
    required_inputs = {"input_dir", "output_dir"}
    return (
        "list_files" in tool_names
        and "read_json" in tool_names
        and "write_text" in tool_names
        and required_inputs.issubset(set(input_schema.keys()))
        and "json" in description
        and "csv" in description
    )


def explain_match(trajectory: Trajectory, input_schema: dict[str, str]) -> str:
    return "Matched directory_json_to_csv because the trajectory lists files, reads JSON files, writes CSV text files, and the task description mentions JSON and CSV."


def _observed_pattern(trajectory: Trajectory) -> str | None:
    for step in trajectory.steps:
        for key in ("pattern", "glob", "file_glob", "match_pattern", "filter", "include", "file_pattern"):
            pattern = step.tool_input.get(key)
            if pattern:
                return pattern
    return None


def _observed_delimiter(trajectory: Trajectory) -> str | None:
    for step in trajectory.steps:
        if step.tool_name.lower() != "write_text":
            continue
        value = step.tool_input.get("delimiter")
        if value:
            return value
        for alias in ("sep", "separator"):
            value = step.tool_input.get(alias)
            if value:
                return value
    return None


def _observed_quotechar(trajectory: Trajectory) -> str | None:
    for step in trajectory.steps:
        if step.tool_name.lower() != "write_text":
            continue
        value = step.tool_input.get("quotechar")
        if value:
            return value
    return None


def _observed_quoting(trajectory: Trajectory) -> str | None:
    for step in trajectory.steps:
        if step.tool_name.lower() != "write_text":
            continue
        value = step.tool_input.get("quoting")
        if value is not None:
            return str(value)
    return None


def _observed_escapechar(trajectory: Trajectory) -> str | None:
    for step in trajectory.steps:
        if step.tool_name.lower() != "write_text":
            continue
        value = step.tool_input.get("escapechar")
        if value:
            return value
    return None


def _observed_doublequote(trajectory: Trajectory) -> bool | None:
    for step in trajectory.steps:
        if step.tool_name.lower() != "write_text":
            continue
        if "doublequote" in step.tool_input:
            return bool(step.tool_input.get("doublequote"))
    return None


def _observed_restval(trajectory: Trajectory) -> str | None:
    for step in trajectory.steps:
        if step.tool_name.lower() != "write_text":
            continue
        value = step.tool_input.get("restval")
        if value is not None:
            return str(value)
    return None


def _observed_extrasaction(trajectory: Trajectory) -> str | None:
    for step in trajectory.steps:
        if step.tool_name.lower() != "write_text":
            continue
        value = step.tool_input.get("extrasaction")
        if value:
            return str(value)
    return None


def augment_input_schema(trajectory: Trajectory, input_schema: dict[str, str]) -> dict[str, str]:
    updated = dict(input_schema)
    if _observed_pattern(trajectory):
        updated.setdefault("pattern", "str")
    observed_prefix = infer_observed_filename_affix(
        trajectory.steps,
        read_tools={"read_json"},
        write_tools={"write_text"},
        mode="prefix",
    )
    if observed_prefix is not None:
        updated.setdefault("prefix", "str")
    observed_suffix = infer_observed_filename_affix(
        trajectory.steps,
        read_tools={"read_json"},
        write_tools={"write_text"},
        mode="suffix",
    )
    if observed_suffix is not None:
        updated.setdefault("suffix", "str")
    delimiter = _observed_delimiter(trajectory)
    if delimiter is not None or "delimiter" in updated:
        updated["delimiter"] = "str"
    quotechar = _observed_quotechar(trajectory)
    if quotechar is not None or "quotechar" in updated:
        updated["quotechar"] = "str"
    quoting = _observed_quoting(trajectory)
    if quoting is not None or "quoting" in updated:
        updated["quoting"] = "str"
    escapechar = _observed_escapechar(trajectory)
    if escapechar is not None or "escapechar" in updated:
        updated["escapechar"] = "str"
    if _observed_doublequote(trajectory) is not None or "doublequote" in updated:
        updated["doublequote"] = "str"
    if _observed_restval(trajectory) is not None or "restval" in updated:
        updated["restval"] = "str"
    if _observed_extrasaction(trajectory) is not None or "extrasaction" in updated:
        updated["extrasaction"] = "str"
    return updated


def build_code(skill_name: str, summary: str, docstring: str, trajectory: Trajectory) -> str:
    default_pattern = escape(_observed_pattern(trajectory) or "*.json")
    default_delimiter = escape(_observed_delimiter(trajectory) or ",")
    default_quotechar = escape(_observed_quotechar(trajectory) or '"')
    default_quoting = escape(_observed_quoting(trajectory) or "QUOTE_MINIMAL")
    default_escapechar = escape(_observed_escapechar(trajectory) or "\\")
    default_doublequote = _observed_doublequote(trajectory)
    default_restval = escape(_observed_restval(trajectory) or "")
    default_extrasaction = escape(_observed_extrasaction(trajectory) or "raise")
    observed_prefix = infer_observed_filename_affix(
        trajectory.steps,
        read_tools={"read_json"},
        write_tools={"write_text"},
        mode="prefix",
    )
    observed_suffix = infer_observed_filename_affix(
        trajectory.steps,
        read_tools={"read_json"},
        write_tools={"write_text"},
        mode="suffix",
    )

    return f'''import csv
from io import StringIO
from pathlib import Path


def run(tools, **kwargs):
    """
{indent_docstring(docstring)}
    """
    input_dir = kwargs.get("input_dir")
    output_dir = kwargs.get("output_dir")
    pattern = kwargs.get("pattern", "{default_pattern}")
    delimiter = kwargs.get("delimiter", "{default_delimiter}")
    quotechar = kwargs.get("quotechar", "{default_quotechar}")
    quoting = kwargs.get("quoting", "{default_quoting}")
    escapechar = kwargs.get("escapechar", "{default_escapechar}")
    doublequote = kwargs.get("doublequote", {repr(True if default_doublequote is None else default_doublequote)})
    restval = kwargs.get("restval", "{default_restval}")
    extrasaction = kwargs.get("extrasaction", "{default_extrasaction}")
    prefix = kwargs.get("prefix", {repr(observed_prefix)})
    suffix = kwargs.get("suffix", {repr(observed_suffix)})
    normalized_doublequote = doublequote if isinstance(doublequote, bool) else str(doublequote).lower() == "true"
    normalized_prefix = "" if prefix is None else str(prefix)
    normalized_suffix = "" if suffix is None else str(suffix)

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

    quoting_mapping = {{
        "QUOTE_MINIMAL": csv.QUOTE_MINIMAL,
        "QUOTE_ALL": csv.QUOTE_ALL,
        "QUOTE_NONNUMERIC": csv.QUOTE_NONNUMERIC,
        "QUOTE_NONE": csv.QUOTE_NONE,
    }}
    normalized_quoting = quoting
    if not isinstance(normalized_quoting, int):
        normalized_text = str(normalized_quoting).strip().upper()
        normalized_quoting = (
            int(normalized_text)
            if normalized_text.isdigit()
            else quoting_mapping.get(normalized_text, csv.QUOTE_MINIMAL)
        )

    written = []
    input_root = Path(tools.resolve_path(input_dir))
    for file_path in tools.list_files(input_dir, pattern):
        source = Path(file_path)
        relative_parent = source.relative_to(input_root).parent
        target = Path(output_dir) / relative_parent / f"{{normalized_prefix}}{{source.stem}}{{normalized_suffix}}.csv"
        rows = tools.read_json(file_path)
        if not isinstance(rows, list):
            raise ValueError("Expected JSON list of objects.")
        fieldnames = list(rows[0].keys()) if rows else []
        buffer = StringIO()
        writer = csv.DictWriter(
            buffer,
            fieldnames=fieldnames,
            delimiter=delimiter,
            quotechar=quotechar,
            quoting=normalized_quoting,
            escapechar=escapechar,
            doublequote=normalized_doublequote,
            restval=restval,
            extrasaction=str(extrasaction),
            lineterminator="\\n",
        )
        if fieldnames:
            writer.writeheader()
            writer.writerows(rows)
        tools.write_text(str(target), buffer.getvalue())
        written.append(str(target))

    return {{
        "status": "completed",
        "skill_name": "{escape(skill_name)}",
        "summary": "{escape(summary)}",
        "artifacts": written,
        "steps_executed": {len(trajectory.steps)},
        "processed_files": len(written),
        "pattern": pattern,
    }}
'''
