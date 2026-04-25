from pathlib import Path


def run(tools, **kwargs):
    """
    功能描述:
        Move all log files from inbox to archive.

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
    pattern = kwargs.get("pattern", "*.log")

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

    moved = []
    for file_path in tools.list_files(input_dir, pattern):
        source = Path(file_path)
        target = Path(output_dir) / source.name
        tools.move_file(file_path, str(target))
        moved.append(str(target))

    return {
        "status": "completed",
        "skill_name": "cli_compact_observed_distill_promote_test",
        "summary": "Move all log files from inbox to archive.",
        "artifacts": moved,
        "steps_executed": 2,
        "moved_files": len(moved),
        "pattern": pattern,
    }
