from pathlib import Path


def run(tools, **kwargs):
    """
    功能描述:
        Rename all txt files in a directory by prefixing them with a value.

    输入参数:
            - input_dir: str
            - prefix: str
            - pattern: str

    输出结果:
            - status: str
            - artifacts: list[str]
            - steps_executed: int
    """
    input_dir = kwargs.get("input_dir")
    prefix = kwargs.get("prefix")
    pattern = kwargs.get("pattern", "*.txt")

    missing = [
        name
        for name, value in {
            "input_dir": input_dir,
            "prefix": prefix,
        }.items()
        if not value
    ]
    if missing:
        raise ValueError(f"Missing required inputs: {missing}")

    renamed = []
    for file_path in tools.list_files(input_dir, pattern):
        source = Path(file_path)
        target = source.with_name(prefix + source.name)
        tools.rename_path(file_path, str(target))
        renamed.append(str(target))

    return {
        "status": "completed",
        "skill_name": "batch_rename_name_prefix_alias_rule_test",
        "summary": "Rename all txt files in a directory by prefixing them with a value.",
        "artifacts": renamed,
        "steps_executed": 2,
        "renamed_files": len(renamed),
        "pattern": pattern,
    }
