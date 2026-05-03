from __future__ import annotations

from skill_runtime.api.models import AgentTaskRequest, CodexTaskClassification


class CodexTaskClassifier:
    HIGH_RISK_LEVELS = {"high", "destructive"}
    TEXT_TRANSFORM_KEYWORDS = {"merge", "clean", "normalize", "replace", "format", "rewrite"}
    STRUCTURED_CONVERSION_KEYWORDS = {"convert", "export", "transform", "json", "csv", "tsv"}
    WORKSPACE_ORGANIZATION_KEYWORDS = {"copy", "rename", "archive", "organize", "move", "sort"}
    STATE_FILE_ACTION_KEYWORDS = {"update", "refresh", "sync", "record"}
    DEVELOPMENT_WORKFLOW_KEYWORDS = {
        "add",
        "bug",
        "config",
        "dashboard",
        "dev",
        "docs",
        "feature",
        "fix",
        "implement",
        "module",
        "regression",
        "refactor",
        "runtime",
        "test",
        "ui",
        "workflow",
        "修复",
        "实现",
        "开发",
        "接入",
        "测试",
        "重构",
        "配置",
        "文档",
        "观察",
        "面板",
        "工作流",
    }
    OPEN_ENDED_KEYWORDS = {
        "review",
        "architecture",
        "roadmap",
        "investigate",
        "strategy",
        "explain",
        "discuss",
        "design",
        "analyze",
    }
    EXTERNAL_SYSTEM_KEYWORDS = {
        "browser",
        "website",
        "remote",
        "production",
        "deploy",
        "login",
        "account",
        "third-party",
        "api",
    }
    EXTERNAL_DOMINANT_KEYWORDS = {
        "browser",
        "website",
        "remote",
        "production",
        "deploy",
        "login",
        "account",
        "third-party",
    }
    PATH_MARKERS = (
        "_path",
        "_dir",
        "_file",
        "_root",
        "path",
        "dir",
        "file",
        "folder",
    )
    STATE_FILE_NAMES = {"handoff.md", "tasks.md", "decisions.md"}
    DEVELOPMENT_OUTPUT_PREFIXES = (
        ".github/",
        "docs/",
        "scripts/",
        "skill_runtime/",
        "tests/",
    )
    DEVELOPMENT_OUTPUT_EXTENSIONS = {
        ".js",
        ".jsx",
        ".json",
        ".md",
        ".py",
        ".toml",
        ".ts",
        ".tsx",
        ".yaml",
        ".yml",
    }
    ALLOWED_DEFAULT_IN_FAMILIES = {
        "project-state-maintenance",
        "local-text-transformation",
        "structured-format-conversion",
        "low-risk-workspace-organization",
        "development-workflow-observation",
    }

    def classify(self, request: AgentTaskRequest) -> CodexTaskClassification:
        signals: list[str] = []
        description = request.task_description.lower()

        if request.risk_level in self.HIGH_RISK_LEVELS:
            return CodexTaskClassification(
                bucket="default-out",
                reason="task risk is too high for Codex default runtime entry",
                matched_signals=["high-risk"],
            )
        if request.task_kind != "workflow":
            return CodexTaskClassification(
                bucket="default-out",
                reason="task is not workflow-like enough for Codex default runtime entry",
                matched_signals=["non-workflow"],
            )

        local_targets = self._has_local_targets(request)
        open_ended = self._has_keyword(description, self.OPEN_ENDED_KEYWORDS)
        external = self._has_keyword(description, self.EXTERNAL_SYSTEM_KEYWORDS)
        state_file_task = self._touches_state_files(request)
        default_in_family = self._default_in_family(request, description)

        if local_targets:
            signals.append("local-targets")
        if request.working_directory:
            signals.append("workspace-scoped")
        if state_file_task:
            signals.append("state-files")
        if default_in_family:
            signals.append(f"family:{default_in_family}")
        if open_ended:
            signals.append("open-ended-language")
        if external:
            signals.append("external-system-language")

        if (open_ended and not local_targets) or self._is_external_dominant_task(description):
            return CodexTaskClassification(
                bucket="default-out",
                reason="task is dominated by open-ended reasoning or external-system state",
                matched_signals=signals or ["open-ended"],
            )

        if default_in_family in self.ALLOWED_DEFAULT_IN_FAMILIES and local_targets:
            return CodexTaskClassification(
                bucket="default-in",
                reason=f"task matches the phase-one default-in family: {default_in_family}",
                matched_signals=signals or ["local-targets"],
            )

        if local_targets or request.working_directory:
            return CodexTaskClassification(
                bucket="guarded-in",
                reason="task looks local and reusable, but it does not match a phase-one default-in family yet",
                matched_signals=signals or ["workspace-scoped"],
            )

        return CodexTaskClassification(
            bucket="default-out",
            reason="task does not expose a stable local workflow shape for default runtime entry",
            matched_signals=signals or ["no-stable-local-shape"],
        )

    def _has_keyword(self, description: str, keywords: set[str]) -> bool:
        return any(keyword in description for keyword in keywords)

    def _has_local_targets(self, request: AgentTaskRequest) -> bool:
        if request.expected_outputs:
            return True
        for key, value in request.known_inputs.items():
            lowered_key = key.lower()
            if any(marker in lowered_key for marker in self.PATH_MARKERS):
                return True
            if isinstance(value, str) and any(token in value.lower() for token in ("/", "\\", ".md", ".txt", ".json", ".csv")):
                return True
        return False

    def _touches_state_files(self, request: AgentTaskRequest) -> bool:
        for value in request.known_inputs.values():
            if isinstance(value, str) and value.lower() in self.STATE_FILE_NAMES:
                return True
        for value in request.expected_outputs:
            if isinstance(value, str) and value.lower() in self.STATE_FILE_NAMES:
                return True
        description = request.task_description.lower()
        return any(name in description for name in self.STATE_FILE_NAMES)

    def _default_in_family(self, request: AgentTaskRequest, description: str) -> str | None:
        if self._is_project_state_maintenance(request, description):
            return "project-state-maintenance"
        if self._is_text_transformation(request, description):
            return "local-text-transformation"
        if self._is_structured_conversion(request, description):
            return "structured-format-conversion"
        if self._is_workspace_organization(request, description):
            return "low-risk-workspace-organization"
        if self._is_development_workflow(request, description):
            return "development-workflow-observation"
        return None

    def _is_project_state_maintenance(self, request: AgentTaskRequest, description: str) -> bool:
        return self._touches_state_files(request) and self._has_keyword(description, self.STATE_FILE_ACTION_KEYWORDS)

    def _is_text_transformation(self, request: AgentTaskRequest, description: str) -> bool:
        if not self._has_keyword(description, self.TEXT_TRANSFORM_KEYWORDS):
            return False
        return self._mentions_extension_or_path(request, {".txt", ".md"})

    def _is_structured_conversion(self, request: AgentTaskRequest, description: str) -> bool:
        if not self._has_keyword(description, self.STRUCTURED_CONVERSION_KEYWORDS):
            return False
        return self._mentions_extension_or_path(request, {".json", ".csv", ".tsv"})

    def _is_workspace_organization(self, request: AgentTaskRequest, description: str) -> bool:
        if not self._has_keyword(description, self.WORKSPACE_ORGANIZATION_KEYWORDS):
            return False
        return self._has_local_targets(request)

    def _is_development_workflow(self, request: AgentTaskRequest, description: str) -> bool:
        if not request.working_directory or not request.expected_outputs:
            return False
        if self._has_keyword(description, self.DEVELOPMENT_WORKFLOW_KEYWORDS):
            return self._mentions_extension_or_path(
                request,
                {".py", ".js", ".jsx", ".ts", ".tsx", ".md", ".toml", ".yaml", ".yml", ".json"},
            )
        return self._has_development_output_path(request)

    def _has_development_output_path(self, request: AgentTaskRequest) -> bool:
        for value in request.expected_outputs:
            if not isinstance(value, str):
                continue
            normalized = value.replace("\\", "/").lower()
            if not any(normalized.startswith(prefix) for prefix in self.DEVELOPMENT_OUTPUT_PREFIXES):
                continue
            if any(normalized.endswith(extension) for extension in self.DEVELOPMENT_OUTPUT_EXTENSIONS):
                return True
        return False

    def _mentions_extension_or_path(self, request: AgentTaskRequest, extensions: set[str]) -> bool:
        values = list(request.known_inputs.values()) + list(request.expected_outputs)
        for value in values:
            if not isinstance(value, str):
                continue
            lowered = value.lower()
            if any(ext in lowered for ext in extensions):
                return True
        description = request.task_description.lower()
        return any(ext in description for ext in extensions)

    def _is_external_dominant_task(self, description: str) -> bool:
        return any(keyword in description for keyword in self.EXTERNAL_DOMINANT_KEYWORDS)
