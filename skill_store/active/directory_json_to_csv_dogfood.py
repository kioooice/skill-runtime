import csv
from io import StringIO
from pathlib import Path


def run(tools, **kwargs):
    """
    功能描述:
        Batch export all JSON records in a folder into CSV files.

    输入参数:
            - delimiter: str
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
    pattern = kwargs.get("pattern", "**/*.json")
    delimiter = kwargs.get("delimiter", ",")
    quotechar = kwargs.get("quotechar", "\"")
    quoting = kwargs.get("quoting", "QUOTE_MINIMAL")
    escapechar = kwargs.get("escapechar", "\\")
    doublequote = kwargs.get("doublequote", True)
    restval = kwargs.get("restval", "")
    extrasaction = kwargs.get("extrasaction", "raise")
    prefix = kwargs.get("prefix", None)
    suffix = kwargs.get("suffix", None)
    normalized_doublequote = doublequote if isinstance(doublequote, bool) else str(doublequote).lower() == "true"
    normalized_prefix = "" if prefix is None else str(prefix)
    normalized_suffix = "" if suffix is None else str(suffix)

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

    written = []
    input_root = Path(tools.resolve_path(input_dir))
    for file_path in tools.list_files(input_dir, pattern):
        source = Path(file_path)
        relative_parent = source.relative_to(input_root).parent
        target = Path(output_dir) / relative_parent / f"{normalized_prefix}{source.stem}{normalized_suffix}.csv"
        rows = tools.read_json(file_path)
        if not isinstance(rows, list):
            raise ValueError("Expected JSON list of objects.")
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
        tools.write_text(str(target), buffer.getvalue())
        written.append(str(target))

    return {
        "status": "completed",
        "skill_name": "directory_json_to_csv_dogfood",
        "summary": "Batch export all JSON records in a folder into CSV files.",
        "artifacts": written,
        "steps_executed": 3,
        "processed_files": len(written),
        "pattern": pattern,
    }
