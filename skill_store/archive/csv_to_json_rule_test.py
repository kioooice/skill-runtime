import csv
from io import StringIO


def run(tools, **kwargs):
    """
    功能描述:
        Convert a CSV file into a JSON array file.

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

    csv_text = tools.read_text(input_path)
    reader = csv.DictReader(StringIO(csv_text))
    rows = list(reader)
    tools.write_json(output_path, rows)

    return {
        "status": "completed",
        "skill_name": "csv_to_json_rule_test",
        "summary": "Convert a CSV file into a JSON array file.",
        "artifacts": [output_path or "demo/output/table.json"],
        "steps_executed": 2,
        "rows": len(rows),
    }
