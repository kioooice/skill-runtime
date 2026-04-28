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
    prefix = kwargs.get("prefix", None)
    suffix = kwargs.get("suffix", None)
    normalized_prefix = "" if prefix is None else str(prefix)
    normalized_suffix = "" if suffix is None else str(suffix)

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

    input_root = Path(tools.resolve_path(input_dir))
    copied = []
    for file_path in tools.list_files(input_dir, pattern):
        source = Path(file_path)
        relative_parent = source.relative_to(input_root).parent
        target = Path(output_dir) / relative_parent / f"{normalized_prefix}{source.stem}{normalized_suffix}{source.suffix}"
        tools.copy_file(file_path, str(target))
        copied.append(str(target))

    return {
        "status": "completed",
        "skill_name": "directory_copy_destination_alias_rule_test",
        "summary": "Copy matching txt files from one directory into another directory.",
        "artifacts": copied,
        "steps_executed": 2,
        "copied_files": len(copied),
        "pattern": pattern,
    }
