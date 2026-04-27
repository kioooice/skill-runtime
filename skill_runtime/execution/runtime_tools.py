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
        self._records: list[dict[str, Any]] = []

    def read_text(self, path: str | Path) -> str:
        target = self._resolve_path(path)
        content = target.read_text(encoding="utf-8")
        self._record(
            "read_text",
            {"path": str(path)},
            f"Read text from {self._display_path(target)}.",
        )
        return content

    def write_text(
        self,
        path: str | Path,
        content: str,
        *,
        newline: str | None = None,
    ) -> str:
        target = self._resolve_path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8", newline=newline)
        self._record(
            "write_text",
            {"path": str(path), "newline": newline},
            f"Wrote text to {self._display_path(target)}.",
            artifacts=[self._display_path(target)],
        )
        return str(target)

    def read_json(self, path: str | Path) -> Any:
        target = self._resolve_path(path)
        payload = json.loads(target.read_text(encoding="utf-8"))
        self._record(
            "read_json",
            {"path": str(path)},
            f"Read JSON from {self._display_path(target)}.",
        )
        return payload

    def write_json(
        self,
        path: str | Path,
        payload: Any,
        *,
        ensure_ascii: bool = False,
        indent: int = 2,
        sort_keys: bool = False,
    ) -> str:
        target = self._resolve_path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(payload, ensure_ascii=ensure_ascii, indent=indent, sort_keys=sort_keys),
            encoding="utf-8",
        )
        self._record(
            "write_json",
            {
                "path": str(path),
                "ensure_ascii": ensure_ascii,
                "indent": indent,
                "sort_keys": sort_keys,
            },
            f"Wrote JSON to {self._display_path(target)}.",
            artifacts=[self._display_path(target)],
        )
        return str(target)

    def list_files(self, path: str | Path, pattern: str = "*") -> list[str]:
        target = self._resolve_path(path)
        if not target.exists():
            self._record(
                "list_files",
                {"path": str(path), "pattern": pattern},
                f"No files found because {self._display_path(target)} does not exist.",
            )
            return []
        files = [str(p) for p in sorted(target.glob(pattern)) if p.is_file()]
        self._record(
            "list_files",
            {"path": str(path), "pattern": pattern},
            f"Found {len(files)} matching files in {self._display_path(target)}.",
        )
        return files

    def rename_path(self, source_path: str | Path, target_path: str | Path) -> str:
        source = self._resolve_path(source_path)
        target = self._resolve_path(target_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        source.rename(target)
        self._record(
            "rename_path",
            {"source_path": str(source_path), "target_path": str(target_path)},
            f"Renamed {self._display_path(source)} to {self._display_path(target)}.",
            artifacts=[self._display_path(target)],
        )
        return str(target)

    def move_file(self, source_path: str | Path, target_path: str | Path) -> str:
        return self.rename_path(source_path, target_path)

    def copy_file(self, source_path: str | Path, target_path: str | Path) -> str:
        source = self._resolve_path(source_path)
        target = self._resolve_path(target_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        copy2(source, target)
        self._record(
            "copy_file",
            {"source_path": str(source_path), "target_path": str(target_path)},
            f"Copied {self._display_path(source)} to {self._display_path(target)}.",
            artifacts=[self._display_path(target)],
        )
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

    def export_records(self) -> list[dict[str, Any]]:
        return [dict(record) for record in self._records]

    def resolve_path(self, path: str | Path) -> str:
        return str(self._resolve_path(path))

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

    def _record(
        self,
        tool_name: str,
        tool_input: dict[str, Any],
        observation: str,
        artifacts: list[str] | None = None,
        status: str = "success",
    ) -> None:
        entry: dict[str, Any] = {
            "tool_name": tool_name,
            "tool_input": tool_input,
            "observation": observation,
            "status": status,
        }
        if artifacts:
            entry["artifacts"] = artifacts
        self._records.append(entry)

    def _display_path(self, path: Path) -> str:
        try:
            return str(path.relative_to(self.workspace)).replace("\\", "/")
        except ValueError:
            return str(path)
