import re
from pathlib import Path


def escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


def indent_docstring(text: str) -> str:
    return "\n".join(f"    {line}" if line else "" for line in text.splitlines())


def compact_step(tool_name: str, observation: str) -> str:
    text = re.sub(r"\s+", " ", f"{tool_name}: {observation}".strip())
    return escape(text[:100])


def infer_filename_prefix(source_path: str | None, target_path: str | None) -> str | None:
    if not source_path or not target_path:
        return None

    source_stem = Path(source_path).stem
    target_stem = Path(target_path).stem
    if target_stem == source_stem or not target_stem.endswith(source_stem):
        return None

    prefix = target_stem[: -len(source_stem)]
    return prefix or None


def infer_filename_suffix(source_path: str | None, target_path: str | None) -> str | None:
    if not source_path or not target_path:
        return None

    source_stem = Path(source_path).stem
    target_stem = Path(target_path).stem
    if target_stem == source_stem or not target_stem.startswith(source_stem):
        return None

    suffix = target_stem[len(source_stem) :]
    return suffix or None


def infer_observed_filename_affix(
    steps,
    *,
    read_tools: set[str],
    write_tools: set[str],
    mode: str,
) -> str | None:
    observed_values: set[str] = set()
    for index, step in enumerate(steps):
        if step.tool_name.lower() not in write_tools:
            continue

        target_path = step.tool_input.get("path")
        if not target_path:
            continue

        source_path = None
        for prior in reversed(steps[:index]):
            if prior.tool_name.lower() not in read_tools:
                continue
            source_path = prior.tool_input.get("path")
            if source_path:
                break
        if not source_path:
            continue

        value = (
            infer_filename_prefix(source_path, target_path)
            if mode == "prefix"
            else infer_filename_suffix(source_path, target_path)
        )
        if not value:
            return None
        observed_values.add(value)

    if len(observed_values) == 1:
        return next(iter(observed_values))
    return None


def infer_observed_path_affix(
    steps,
    *,
    tool_names: set[str],
    source_keys: tuple[str, ...] = ("source_path", "input_path", "path", "source", "input"),
    target_keys: tuple[str, ...] = ("target_path", "output_path", "destination_path", "target", "output", "destination"),
    mode: str,
) -> str | None:
    observed_values: set[str] = set()
    for step in steps:
        if step.tool_name.lower() not in tool_names:
            continue

        source_path = next((step.tool_input.get(key) for key in source_keys if step.tool_input.get(key)), None)
        target_path = next((step.tool_input.get(key) for key in target_keys if step.tool_input.get(key)), None)
        if not source_path or not target_path:
            continue

        value = (
            infer_filename_prefix(source_path, target_path)
            if mode == "prefix"
            else infer_filename_suffix(source_path, target_path)
        )
        if not value:
            return None
        observed_values.add(value)

    if len(observed_values) == 1:
        return next(iter(observed_values))
    return None
