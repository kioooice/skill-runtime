import csv
from io import StringIO


def run(tools, **kwargs):
    """
    功能描述:
        Convert a JSON array file into CSV format.

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

    rows = tools.read_json(input_path)
    if not isinstance(rows, list):
        raise ValueError("Expected JSON list of objects.")

    fieldnames = list(rows[0].keys()) if rows else []
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    if fieldnames:
        writer.writeheader()
        writer.writerows(rows)

    tools.write_text(output_path, buffer.getvalue())

    return {
        "status": "completed",
        "skill_name": "json_to_csv_rule_test",
        "summary": "Convert a JSON array file into CSV format.",
        "artifacts": [output_path or "demo/output/table.csv"],
        "steps_executed": 2,
        "rows": len(rows),
    }
