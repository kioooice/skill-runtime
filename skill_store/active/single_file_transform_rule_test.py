def run(tools, **kwargs):
    """
    功能描述:
        Read one text file and write it to a new output file.

    输入参数:
            - input_path: str
            - output_path: str

    输出结果:
            - status: str
            - artifacts: list[str]
            - steps_executed: int
    """
    input_path = kwargs.get("input_path")
    output_path = kwargs.get("output_path")

    missing = [
        name
        for name, value in {"input_path": input_path, "output_path": output_path}.items()
        if not value
    ]
    if missing:
        raise ValueError(f"Missing required inputs: {missing}")

    text = tools.read_text(input_path)
    transformed = text.rstrip() + "\n"
    tools.write_text(output_path, transformed)

    return {
        "status": "completed",
        "skill_name": "single_file_transform_rule_test",
        "summary": "Read one text file and write it to a new output file.",
        "artifacts": [output_path or "demo/output/single_transform.txt"],
        "steps_executed": 2,
        "output_path": output_path,
    }
