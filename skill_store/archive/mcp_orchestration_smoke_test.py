from pathlib import Path


def run(tools, **kwargs):
    """
    功能描述:
        Merge all txt files in a directory into one markdown file.

    输入参数:
            - input_dir: str
            - output_path: str
            - pattern: str

    输出结果:
            - status: str
            - artifacts: list[str]
            - steps_executed: int
    """
    input_dir = kwargs.get("input_dir")
    output_path = kwargs.get("output_path")
    pattern = kwargs.get("pattern", "*.txt")

    missing = [
        name
        for name, value in {"input_dir": input_dir, "output_path": output_path}.items()
        if not value
    ]
    if missing:
        raise ValueError(f"Missing required inputs: {missing}")

    files = tools.list_files(input_dir, pattern)
    contents = []
    for file_path in files:
        name = Path(file_path).name
        text = tools.read_text(file_path).strip()
        contents.append(f"# {name}\n\n{text}\n")

    merged = "\n".join(contents).strip() + "\n"
    tools.write_text(output_path, merged)

    return {
        "status": "completed",
        "skill_name": "mcp_orchestration_smoke_test",
        "summary": "Merge all txt files in a directory into one markdown file.",
        "artifacts": [output_path or "demo/output/merged.md"],
        "steps_executed": 3,
        "merged_files": len(files),
        "pattern": pattern,
    }
