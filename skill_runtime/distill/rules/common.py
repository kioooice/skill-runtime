import re


def escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


def indent_docstring(text: str) -> str:
    return "\n".join(f"    {line}" if line else "" for line in text.splitlines())


def compact_step(tool_name: str, observation: str) -> str:
    text = re.sub(r"\s+", " ", f"{tool_name}: {observation}".strip())
    return escape(text[:100])
