from pathlib import Path


def run(tools, **kwargs):
    """
    功能描述:
        Merge all .txt files in the input directory into one output markdown file.

    输入参数:
        - input_dir: str
        - output_path: str

    输出结果:
        - status: str
        - output_path: str
        - merged_files: int
    """
    input_dir = kwargs.get("input_dir")
    output_path = kwargs.get("output_path")

    missing = [name for name, value in {"input_dir": input_dir, "output_path": output_path}.items() if not value]
    if missing:
        raise ValueError(f"Missing required inputs: {missing}")

    files = tools.list_files(input_dir, "*.txt")
    contents: list[str] = []
    for file_path in files:
        name = Path(file_path).name
        text = tools.read_text(file_path)
        contents.append(f"# {name}\n\n{text.strip()}\n")

    merged = "\n".join(contents).strip() + "\n"
    tools.write_text(output_path, merged)

    return {
        "status": "completed",
        "output_path": output_path,
        "merged_files": len(files),
    }
