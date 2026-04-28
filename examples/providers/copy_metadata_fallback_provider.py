import json
import sys


def main() -> int:
    raw_input = sys.stdin.read().lstrip("\ufeff")
    if not raw_input.strip():
        raise ValueError("copy metadata fallback provider expects a JSON request on stdin")
    request = json.loads(raw_input)
    task_summary = request.get("summary") or "Copy one file and write metadata."
    code = '''def run(tools, **kwargs):
    """
    功能描述:
        Copy one input file to an output path and write a JSON metadata sidecar.

    输入参数:
        - input_path: Source file path to copy.
        - output_path: Destination file path to create.
        - metadata_path: JSON sidecar path to write.

    输出结果:
        - dict with completion status, produced artifacts, and copied path.
    """
    input_path = kwargs.get("input_path")
    output_path = kwargs.get("output_path")
    metadata_path = kwargs.get("metadata_path")
    missing = [
        name
        for name, value in {
            "input_path": input_path,
            "output_path": output_path,
            "metadata_path": metadata_path,
        }.items()
        if value is None
    ]
    if missing:
        raise ValueError(f"Missing required inputs: {missing}")

    copied_path = tools.copy_file(input_path, output_path)
    tools.write_json(metadata_path, {"source": input_path, "copied_path": copied_path})
    return {
        "status": "completed",
        "artifacts": [output_path, metadata_path],
        "steps_executed": 2,
        "copied_path": copied_path,
        "generated_by": "local_copy_metadata_fallback_provider",
    }
'''
    print(
        json.dumps(
            {
                "code": code,
                "provider_name": "local_copy_metadata_fallback_provider",
                "reason": f"Generated a local file-copy metadata skill for: {task_summary}",
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
