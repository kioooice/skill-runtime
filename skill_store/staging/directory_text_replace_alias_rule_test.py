from pathlib import Path


def run(tools, **kwargs):
    """
    功能描述:
        Replace one string with another across all txt files in a directory and write outputs to another directory.

    输入参数:
            - input_dir: str
            - new_text: str
            - old_text: str
            - output_dir: str
            - pattern: str

    输出结果:
            - status: str
            - artifacts: list[str]
            - steps_executed: int
    """
    input_dir = kwargs.get("input_dir")
    output_dir = kwargs.get("output_dir")
    old_text = kwargs.get("old_text")
    new_text = kwargs.get("new_text")
    pattern = kwargs.get("pattern", "*.txt")

    missing = [
        name
        for name, value in {
            "input_dir": input_dir,
            "output_dir": output_dir,
            "old_text": old_text,
            "new_text": new_text,
        }.items()
        if value is None or value == ""
    ]
    if missing:
        raise ValueError(f"Missing required inputs: {missing}")

    written = []
    for file_path in tools.list_files(input_dir, pattern):
        source = Path(file_path)
        target = Path(output_dir) / source.name
        text = tools.read_text(file_path)
        transformed = text.replace(old_text, new_text)
        tools.write_text(str(target), transformed)
        written.append(str(target))

    return {
        "status": "completed",
        "skill_name": "directory_text_replace_alias_rule_test",
        "summary": "Replace one string with another across all txt files in a directory and write outputs to another directory.",
        "artifacts": written,
        "steps_executed": 3,
        "processed_files": len(written),
        "pattern": pattern,
    }
