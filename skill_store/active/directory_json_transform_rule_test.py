from pathlib import Path


def run(tools, **kwargs):
    """
    功能描述:
        Normalize matching JSON files from one directory into another directory.

    输入参数:
            - input_dir: str
            - output_dir: str
            - pattern: str

    输出结果:
            - status: str
            - artifacts: list[str]
            - steps_executed: int
    """
    input_dir = kwargs.get("input_dir")
    output_dir = kwargs.get("output_dir")
    pattern = kwargs.get("pattern", "*.json")

    missing = [
        name
        for name, value in {
            "input_dir": input_dir,
            "output_dir": output_dir,
        }.items()
        if not value
    ]
    if missing:
        raise ValueError(f"Missing required inputs: {missing}")

    written = []
    for file_path in tools.list_files(input_dir, pattern):
        source = Path(file_path)
        target = Path(output_dir) / source.name
        payload = tools.read_json(file_path)
        tools.write_json(str(target), payload)
        written.append(str(target))

    return {
        "status": "completed",
        "skill_name": "directory_json_transform_rule_test",
        "summary": "Normalize matching JSON files from one directory into another directory.",
        "artifacts": written,
        "steps_executed": 3,
        "processed_files": len(written),
        "pattern": pattern,
    }
