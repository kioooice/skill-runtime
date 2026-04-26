from pathlib import Path


def run(tools, **kwargs):
    """
    功能描述:
        Copy matching txt files from one directory into another directory.

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
    pattern = kwargs.get("pattern", "*.txt")

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

    copied = []
    for file_path in tools.list_files(input_dir, pattern):
        source = Path(file_path)
        target = Path(output_dir) / source.name
        tools.copy_file(file_path, str(target))
        copied.append(str(target))

    return {
        "status": "completed",
        "skill_name": "directory_copy_input_output_alias_rule_test",
        "summary": "Copy matching txt files from one directory into another directory.",
        "artifacts": copied,
        "steps_executed": 2,
        "copied_files": len(copied),
        "pattern": pattern,
    }
