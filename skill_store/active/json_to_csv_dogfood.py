import csv
from io import StringIO


def run(tools, **kwargs):
    """
    功能描述:
        Convert a JSON list of records into a CSV file.

    输入参数:
            - delimiter: str
            - input_path: str
            - output_path: str

    输出结果:
            - status: str
            - artifacts: list[str]
            - steps_executed: int
    """
    input_path = kwargs.get("input_path")
    output_path = kwargs.get("output_path")
    delimiter = kwargs.get("delimiter", ",")
    quotechar = kwargs.get("quotechar", "\"")
    quoting = kwargs.get("quoting", "QUOTE_MINIMAL")
    escapechar = kwargs.get("escapechar", "\\")
    doublequote = kwargs.get("doublequote", True)
    restval = kwargs.get("restval", "")
    extrasaction = kwargs.get("extrasaction", "raise")
    normalized_doublequote = doublequote if isinstance(doublequote, bool) else str(doublequote).lower() == "true"

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

    quoting_mapping = {
        "QUOTE_MINIMAL": csv.QUOTE_MINIMAL,
        "QUOTE_ALL": csv.QUOTE_ALL,
        "QUOTE_NONNUMERIC": csv.QUOTE_NONNUMERIC,
        "QUOTE_NONE": csv.QUOTE_NONE,
    }
    normalized_quoting = quoting
    if not isinstance(normalized_quoting, int):
        normalized_text = str(normalized_quoting).strip().upper()
        normalized_quoting = (
            int(normalized_text)
            if normalized_text.isdigit()
            else quoting_mapping.get(normalized_text, csv.QUOTE_MINIMAL)
        )

    fieldnames = list(rows[0].keys()) if rows else []
    buffer = StringIO()
    writer = csv.DictWriter(
        buffer,
        fieldnames=fieldnames,
        delimiter=delimiter,
        quotechar=quotechar,
        quoting=normalized_quoting,
        escapechar=escapechar,
        doublequote=normalized_doublequote,
        restval=restval,
        extrasaction=str(extrasaction),
        lineterminator="\n",
    )
    if fieldnames:
        writer.writeheader()
        writer.writerows(rows)

    tools.write_text(output_path, buffer.getvalue())

    return {
        "status": "completed",
        "skill_name": "json_to_csv_dogfood",
        "summary": "Convert a JSON list of records into a CSV file.",
        "artifacts": [output_path or "demo/output/records.csv"],
        "steps_executed": 2,
        "rows": len(rows),
    }
