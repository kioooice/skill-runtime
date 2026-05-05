import argparse
import json
from pathlib import Path

from skill_runtime.dashboard.collector import export_dashboard_operator_summary_data


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="export-operator-summary-for-dashboard")
    parser.add_argument("--root", default=".")
    parser.add_argument("--output")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    payload, output_path = export_dashboard_operator_summary_data(
        Path(args.root).resolve(),
        output_path=args.output,
    )
    print(
        json.dumps(
            {
                "status": "ok",
                "data": {
                    "output_path": str(output_path),
                    "generated_at": payload.get("generated_at"),
                    "quality_gate_statuses": {
                        key: value.get("status")
                        for key, value in payload.get("quality_gates", {}).items()
                        if isinstance(value, dict)
                    },
                },
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
