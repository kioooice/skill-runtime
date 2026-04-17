import argparse
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from skill_runtime.mcp import build_mcp_server


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


def main() -> int:
    parser = argparse.ArgumentParser(prog="skill_mcp_server")
    parser.add_argument("--root", help="Path to the skill runtime project root.")
    args = parser.parse_args()

    build_mcp_server(resolve_runtime_root(args.root)).run(transport="stdio")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
