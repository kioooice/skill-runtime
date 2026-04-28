import argparse
import os
from pathlib import Path

from skill_runtime.mcp import build_mcp_server


ROOT = Path(__file__).resolve().parent.parent


def resolve_runtime_root(configured_root: str | None = None) -> Path:
    candidate = configured_root or os.environ.get("SKILL_RUNTIME_ROOT")
    if not candidate:
        return ROOT

    path = Path(candidate)
    if not path.is_absolute():
        path = (ROOT / path).resolve()
    else:
        path = path.resolve()
    return path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="skill-runtime-mcp")
    parser.add_argument("--root", help="Path to the skill runtime project root.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    build_mcp_server(resolve_runtime_root(args.root)).run(transport="stdio")
    return 0


__all__ = ["ROOT", "build_parser", "main", "resolve_runtime_root"]
