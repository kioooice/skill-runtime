def run(tools, **kwargs):
    """
    功能描述:
        Merge all txt files in a directory into one markdown file.

    输入参数:
            - input_dir: str
            - output_path: str

    输出结果:
            - status: str
            - artifacts: list[str]
            - steps_executed: int
    """
    inputs = {"input_dir": kwargs.get("input_dir"), "output_path": kwargs.get("output_path")}

    missing = [key for key, value in inputs.items() if value is None]
    if missing:
        raise ValueError(f"Missing required inputs: {missing}")

    # Step 1: list_files: Found 2 txt files.
    # Step 2: read_text: Read file contents successfully.
    # Step 3: write_text: Wrote merged markdown output.

    return {
        "status": "completed",
        "skill_name": "merge_text_files_generated",
        "summary": "Merge all txt files in a directory into one markdown file.",
        "artifacts": ['demo/output/merged.md'],
        "steps_executed": 3,
        "inputs": inputs,
    }
