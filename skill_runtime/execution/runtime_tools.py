import subprocess
import json
from shutil import copy2
from pathlib import Path
from typing import Any


class ToolPolicyError(ValueError):
    pass


class RuntimeTools:
    def __init__(self, workspace: str | Path = ".") -> None:
        self.workspace = Path(workspace).resolve()

    def read_text(self, path: str | Path) -> str:
        target = self._resolve_path(path)
        return target.read_text(encoding="utf-8")

    def write_text(self, path: str | Path, content: str) -> str:
        target = self._resolve_path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return str(target)

    def read_json(self, path: str | Path) -> Any:
        target = self._resolve_path(path)
        return json.loads(target.read_text(encoding="utf-8"))

    def write_json(self, path: str | Path, payload: Any) -> str:
        target = self._resolve_path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return str(target)

    def list_files(self, path: str | Path, pattern: str = "*") -> list[str]:
        target = self._resolve_path(path)
        if not target.exists():
            return []
        return [str(p) for p in sorted(target.glob(pattern)) if p.is_file()]

    def rename_path(self, source_path: str | Path, target_path: str | Path) -> str:
        source = self._resolve_path(source_path)
        target = self._resolve_path(target_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        source.rename(target)
        return str(target)

    def move_file(self, source_path: str | Path, target_path: str | Path) -> str:
        return self.rename_path(source_path, target_path)

    def copy_file(self, source_path: str | Path, target_path: str | Path) -> str:
        source = self._resolve_path(source_path)
        target = self._resolve_path(target_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        copy2(source, target)
        return str(target)

    def run_shell(self, command: list[str]) -> dict[str, Any]:
        self._validate_command(command)
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd=str(self.workspace),
            shell=False,
        )
        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    def _resolve_path(self, path: str | Path) -> Path:
        target = Path(path)
        if not target.is_absolute():
            target = (self.workspace / target).resolve()
        else:
            target = target.resolve()

        try:
            target.relative_to(self.workspace)
        except ValueError as exc:
            raise ToolPolicyError(f"path escapes workspace: {target}") from exc
        return target

    def _validate_command(self, command: list[str]) -> None:
        if not command:
            raise ToolPolicyError("empty command is not allowed")
        if command[0].lower() in {"rm", "del", "format", "shutdown", "mkfs"}:
            raise ToolPolicyError(f"blocked command: {command[0]}")
