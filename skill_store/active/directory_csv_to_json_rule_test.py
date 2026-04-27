import csv
from io import StringIO
from pathlib import Path


def run(tools, **kwargs):
    """
    功能描述:
        Convert matching CSV files in one directory into JSON files in another directory.

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
    pattern = kwargs.get("pattern", "*.csv")
    delimiter = kwargs.get("delimiter", ",")

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

    written = []
    for file_path in tools.list_files(input_dir, pattern):
        source = Path(file_path)
        target = Path(output_dir) / f"{source.stem}.json"
        csv_text = tools.read_text(file_path)
        rows = list(csv.DictReader(StringIO(csv_text), delimiter=delimiter))
        tools.write_json(str(target), rows)
        written.append(str(target))

    return {
        "status": "completed",
        "skill_name": "directory_csv_to_json_rule_test",
        "summary": "Convert matching CSV files in one directory into JSON files in another directory.",
        "artifacts": written,
        "steps_executed": 3,
        "processed_files": len(written),
        "pattern": pattern,
    }
