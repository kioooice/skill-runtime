def run(tools, **kwargs):
    """
    功能描述:
        Replace or update a word or text in one file and write the updated file.

    输入参数:
            - input_path: str
            - new_text: str
            - old_text: str
            - output_path: str

    输出结果:
            - status: str
            - artifacts: list[str]
            - steps_executed: int
    """
    input_path = kwargs.get("input_path")
    output_path = kwargs.get("output_path")
    old_text = kwargs.get("old_text")
    new_text = kwargs.get("new_text")
    newline = kwargs.get("newline", None)

    missing = [
        name
        for name, value in {
            "input_path": input_path,
            "output_path": output_path,
            "old_text": old_text,
            "new_text": new_text,
        }.items()
        if value is None
    ]
    if missing:
        raise ValueError(f"Missing required inputs: {missing}")

    text = tools.read_text(input_path)
    transformed = text.replace(old_text, new_text)
    tools.write_text(output_path, transformed, newline=newline)

    return {
        "status": "completed",
        "skill_name": "text_replace_dogfood",
        "summary": "Replace or update a word or text in one file and write the updated file.",
        "artifacts": [output_path or "demo/output/template_note_ready.txt"],
        "steps_executed": 2,
        "replaced_text": old_text,
    }
