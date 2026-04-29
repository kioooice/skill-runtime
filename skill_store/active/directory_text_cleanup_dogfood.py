from pathlib import Path


def run(tools, **kwargs):
    """
    功能描述:
        Clean and normalize text files in a directory or folder by trimming trailing whitespace.

    输入参数:
            - input_dir: str
            - output_dir: str
            - pattern: str
            - suffix: str

    输出结果:
            - status: str
            - artifacts: list[str]
            - steps_executed: int
    """
    input_dir = kwargs.get("input_dir")
    output_dir = kwargs.get("output_dir")
    pattern = kwargs.get("pattern", "**/*.txt")
    newline = kwargs.get("newline", None)
    prefix = kwargs.get("prefix", None)
    suffix = kwargs.get("suffix", "_clean")
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
    written = []
    for file_path in tools.list_files(input_dir, pattern):
        source = Path(file_path)
        relative_parent = source.relative_to(input_root).parent
        target = Path(output_dir) / relative_parent / f"{normalized_prefix}{source.stem}{normalized_suffix}{source.suffix}"
        text = tools.read_text(file_path)
        transformed = text.rstrip() + "\n"
        tools.write_text(str(target), transformed, newline=newline)
        written.append(str(target))

    return {
        "status": "completed",
        "skill_name": "directory_text_cleanup_dogfood",
        "summary": "Clean and normalize text files in a directory or folder by trimming trailing whitespace.",
        "artifacts": written,
        "steps_executed": 3,
        "processed_files": len(written),
        "pattern": pattern,
    }
