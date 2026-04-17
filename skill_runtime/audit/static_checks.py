import ast
import re
from dataclasses import dataclass
from pathlib import Path


DANGEROUS_COMMAND_PATTERNS = [
    r"\brm\s+-rf\b",
    r"\bshutdown\b",
    r"\bformat\s+[A-Za-z]:\b",
    r"\bdel\s+/f\s+/s\s+/q\b",
    r"\bmkfs\b",
]

ABSOLUTE_PATH_PATTERNS = [
    r"[A-Za-z]:\\",
    r"/home/",
    r"/Users/",
]

USERNAME_HINT_PATTERNS = [
    r"Administrator",
    r"Admin",
    r"/Users/[^/]+",
    r"[A-Za-z]:\\Users\\[^\\]+",
]


@dataclass
class StaticIssue:
    rule_id: str
    severity: str
    message: str
    line: int | None = None


class StaticChecks:
    def run(self, file_path: str | Path) -> list[StaticIssue]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"file not found: {path}")

        source = path.read_text(encoding="utf-8")
        issues: list[StaticIssue] = []
        issues.extend(self._check_dangerous_commands(source))
        issues.extend(self._check_absolute_paths(source))
        issues.extend(self._check_username_hints(source))
        issues.extend(self._check_missing_docstring(source))
        issues.extend(self._check_long_run_function(source))
        issues.extend(self._check_shell_true(source))
        return issues

    def _check_dangerous_commands(self, source: str) -> list[StaticIssue]:
        issues: list[StaticIssue] = []
        for line_no, line in enumerate(source.splitlines(), start=1):
            for pattern in DANGEROUS_COMMAND_PATTERNS:
                if re.search(pattern, line, flags=re.IGNORECASE):
                    issues.append(
                        StaticIssue(
                            rule_id="dangerous-command",
                            severity="high",
                            message=f"Potential dangerous command detected: {line.strip()}",
                            line=line_no,
                        )
                    )
        return issues

    def _check_absolute_paths(self, source: str) -> list[StaticIssue]:
        issues: list[StaticIssue] = []
        for line_no, line in enumerate(source.splitlines(), start=1):
            for pattern in ABSOLUTE_PATH_PATTERNS:
                if re.search(pattern, line):
                    issues.append(
                        StaticIssue(
                            rule_id="hardcoded-path",
                            severity="medium",
                            message="Hardcoded absolute path detected. Convert it to a function parameter.",
                            line=line_no,
                        )
                    )
        return issues

    def _check_username_hints(self, source: str) -> list[StaticIssue]:
        issues: list[StaticIssue] = []
        for line_no, line in enumerate(source.splitlines(), start=1):
            for pattern in USERNAME_HINT_PATTERNS:
                if re.search(pattern, line):
                    issues.append(
                        StaticIssue(
                            rule_id="hardcoded-user",
                            severity="medium",
                            message="Possible hardcoded username or user-specific path detected.",
                            line=line_no,
                        )
                    )
        return issues

    def _check_missing_docstring(self, source: str) -> list[StaticIssue]:
        try:
            tree = ast.parse(source)
        except SyntaxError as exc:
            return [
                StaticIssue(
                    rule_id="syntax-error",
                    severity="high",
                    message=f"Syntax error: {exc.msg}",
                    line=exc.lineno,
                )
            ]

        run_node = self._find_run_function(tree)
        if run_node is None:
            return [
                StaticIssue(
                    rule_id="missing-run",
                    severity="high",
                    message="Skill must define run(tools, **kwargs).",
                    line=None,
                )
            ]

        if not ast.get_docstring(run_node):
            return [
                StaticIssue(
                    rule_id="missing-docstring",
                    severity="medium",
                    message="run() is missing a docstring with function, inputs, and outputs.",
                    line=run_node.lineno,
                )
            ]

        return []

    def _check_long_run_function(self, source: str) -> list[StaticIssue]:
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return []

        run_node = self._find_run_function(tree)
        if run_node is None:
            return []

        start = run_node.lineno
        end = getattr(run_node, "end_lineno", start)
        length = end - start + 1
        if length > 120:
            return [
                StaticIssue(
                    rule_id="overgrown-skill",
                    severity="medium",
                    message=f"run() is too long ({length} lines). Consider splitting into smaller skills.",
                    line=start,
                )
            ]
        return []

    def _check_shell_true(self, source: str) -> list[StaticIssue]:
        issues: list[StaticIssue] = []
        try:
            tree = ast.parse(source)
        except SyntaxError:
            return issues

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue

            func_name = self._call_name(node)
            if func_name not in {"subprocess.run", "subprocess.Popen", "os.system"}:
                continue

            if func_name == "os.system":
                issues.append(
                    StaticIssue(
                        rule_id="shell-invocation",
                        severity="high",
                        message="os.system detected. Prefer a restricted tool wrapper instead.",
                        line=node.lineno,
                    )
                )
                continue

            for keyword in node.keywords:
                if keyword.arg == "shell" and isinstance(keyword.value, ast.Constant) and keyword.value.value is True:
                    issues.append(
                        StaticIssue(
                            rule_id="shell-true",
                            severity="high",
                            message="subprocess call uses shell=True. This should be restricted or removed.",
                            line=node.lineno,
                        )
                    )
        return issues

    def _find_run_function(self, tree: ast.AST) -> ast.FunctionDef | None:
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == "run":
                return node
        return None

    def _call_name(self, node: ast.Call) -> str | None:
        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            return f"{node.func.value.id}.{node.func.attr}"
        if isinstance(node.func, ast.Name):
            return node.func.id
        return None
