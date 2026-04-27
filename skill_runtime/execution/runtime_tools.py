import subprocess
import json
from shutil import copy2
from pathlib import Path
from typing import Any


class ToolPolicyError(ValueError):
    pass


class RuntimeTools:
    def __init__(
        self,
        workspace: str | Path = ".",
        *,
        scope_policy: dict[str, Any] | None = None,
        dry_run: bool = False,
    ) -> None:
        self.workspace = Path(workspace).resolve()
        self._records: list[dict[str, Any]] = []
        self._scope_policy = self._normalize_scope_policy(scope_policy)
        self._dry_run = dry_run

    def apply_scope_policy(self, scope_policy: dict[str, Any] | None) -> None:
        self._scope_policy = self._normalize_scope_policy(scope_policy)

    def set_dry_run(self, dry_run: bool) -> None:
        self._dry_run = dry_run

    def read_text(self, path: str | Path) -> str:
        target = self._resolve_path(path, enforce_extension=True)
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
        target = self._resolve_path(path, enforce_extension=True)
        self._validate_mutation_allowed("write_text")
        if self._dry_run:
            self._record(
                "write_text",
                {"path": str(path), "newline": newline},
                f"Would write text to {self._display_path(target)}.",
                artifacts=[self._display_path(target)],
                status="planned",
            )
            return str(target)
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
        target = self._resolve_path(path, enforce_extension=True)
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
        target = self._resolve_path(path, enforce_extension=True)
        self._validate_mutation_allowed("write_json")
        if self._dry_run:
            self._record(
                "write_json",
                {
                    "path": str(path),
                    "ensure_ascii": ensure_ascii,
                    "indent": indent,
                    "sort_keys": sort_keys,
                },
                f"Would write JSON to {self._display_path(target)}.",
                artifacts=[self._display_path(target)],
                status="planned",
            )
            return str(target)
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
        target = self._resolve_path(path, enforce_extension=False)
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
        source = self._resolve_path(source_path, enforce_extension=True)
        target = self._resolve_path(target_path, enforce_extension=True)
        self._validate_mutation_allowed("rename_path")
        if self._dry_run:
            self._record(
                "rename_path",
                {"source_path": str(source_path), "target_path": str(target_path)},
                f"Would rename {self._display_path(source)} to {self._display_path(target)}.",
                artifacts=[self._display_path(target)],
                status="planned",
            )
            return str(target)
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
        source = self._resolve_path(source_path, enforce_extension=True)
        target = self._resolve_path(target_path, enforce_extension=True)
        self._validate_mutation_allowed("copy_file")
        if self._dry_run:
            self._record(
                "copy_file",
                {"source_path": str(source_path), "target_path": str(target_path)},
                f"Would copy {self._display_path(source)} to {self._display_path(target)}.",
                artifacts=[self._display_path(target)],
                status="planned",
            )
            return str(target)
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
        if self._dry_run:
            self._record(
                "run_shell",
                {"command": command},
                f"Would run shell command: {' '.join(command)}.",
                status="planned",
            )
            return {
                "returncode": 0,
                "stdout": "",
                "stderr": "",
                "planned": True,
            }
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
        return str(self._resolve_path(path, enforce_extension=False))

    def _resolve_path(self, path: str | Path, *, enforce_extension: bool) -> Path:
        target = Path(path)
        if not target.is_absolute():
            target = (self.workspace / target).resolve()
        else:
            target = target.resolve()

        try:
            target.relative_to(self.workspace)
        except ValueError as exc:
            raise ToolPolicyError(f"path escapes workspace: {target}") from exc
        self._validate_scope_path(target, enforce_extension=enforce_extension)
        return target

    def _validate_command(self, command: list[str]) -> None:
        if not command:
            raise ToolPolicyError("empty command is not allowed")
        if not self._scope_policy["allow_shell"]:
            raise ToolPolicyError("shell access is not allowed for this skill")
        self._validate_mutation_allowed("run_shell")
        command_name = Path(command[0]).name.lower()
        if not self._scope_policy["allow_delete"] and command_name in {
            "rm",
            "del",
            "erase",
            "rmdir",
            "rd",
            "format",
            "shutdown",
            "mkfs",
        }:
            raise ToolPolicyError(f"delete-like shell command is not allowed: {command[0]}")

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

    def _normalize_scope_policy(self, scope_policy: dict[str, Any] | None) -> dict[str, Any]:
        policy = {
            "allow_shell": False,
            "allow_delete": False,
            "allowed_roots": None,
            "allowed_extensions": None,
            "requires_dry_run": False,
        }
        if not isinstance(scope_policy, dict):
            return policy

        if "allow_shell" in scope_policy:
            policy["allow_shell"] = bool(scope_policy["allow_shell"])
        if "allow_delete" in scope_policy:
            policy["allow_delete"] = bool(scope_policy["allow_delete"])
        if "requires_dry_run" in scope_policy:
            policy["requires_dry_run"] = bool(scope_policy["requires_dry_run"])

        allowed_roots = scope_policy.get("allowed_roots")
        if isinstance(allowed_roots, list):
            policy["allowed_roots"] = [
                self._normalize_root(root)
                for root in allowed_roots
                if isinstance(root, str) and root.strip()
            ] or None

        allowed_extensions = scope_policy.get("allowed_extensions")
        if isinstance(allowed_extensions, list):
            normalized_extensions = []
            for extension in allowed_extensions:
                if not isinstance(extension, str):
                    continue
                value = extension.strip().lower()
                if not value:
                    continue
                normalized_extensions.append(value if value.startswith(".") else f".{value}")
            policy["allowed_extensions"] = normalized_extensions or None

        return policy

    def _normalize_root(self, root: str) -> str:
        normalized = str(Path(root)).replace("\\", "/").strip("/")
        return normalized

    def _validate_mutation_allowed(self, tool_name: str) -> None:
        if self._scope_policy.get("requires_dry_run") and not self._dry_run:
            raise ToolPolicyError(
                f"dry-run execution is required for mutating tool: {tool_name}"
            )

    def _validate_scope_path(self, target: Path, *, enforce_extension: bool) -> None:
        allowed_roots = self._scope_policy.get("allowed_roots")
        if allowed_roots:
            display_target = self._display_path(target)
            if not any(
                display_target == root or display_target.startswith(f"{root}/")
                for root in allowed_roots
            ):
                raise ToolPolicyError(
                    f"path is outside allowed roots: {display_target}"
                )

        allowed_extensions = self._scope_policy.get("allowed_extensions")
        if enforce_extension and allowed_extensions:
            suffix = target.suffix.lower()
            if suffix not in allowed_extensions:
                raise ToolPolicyError(
                    f"path extension is not allowed: {self._display_path(target)}"
                )
