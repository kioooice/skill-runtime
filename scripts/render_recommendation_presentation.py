from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from skill_runtime.presentation.recommendation import (  # noqa: E402
    format_recommendation_card,
    format_recommendation_text,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render a recommendation payload as operator-facing presentation output.",
    )
    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Path to a recommendation payload JSON file.",
    )
    parser.add_argument(
        "--format",
        choices=("json", "text"),
        default="text",
        help="Output format. Defaults to text.",
    )
    args = parser.parse_args(argv)

    payload = _load_payload(args.input)
    if payload is None:
        return 1

    if args.format == "json":
        output: dict[str, Any] = {
            "card": format_recommendation_card(payload),
            "text": format_recommendation_text(payload),
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0

    print(format_recommendation_text(payload))
    return 0


def _load_payload(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        print(f"Input file not found: {path}", file=sys.stderr)
        return None

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON in {path}: {exc}", file=sys.stderr)
        return None
    except OSError as exc:
        print(f"Could not read input file {path}: {exc}", file=sys.stderr)
        return None

    if not isinstance(payload, dict):
        print(f"Payload must be a JSON object: {path}", file=sys.stderr)
        return None

    return payload


if __name__ == "__main__":
    raise SystemExit(main())
