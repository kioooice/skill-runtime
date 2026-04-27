import ast
import importlib
import sys
from pathlib import Path


def _module_imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return imports


def _module_exports(path: Path) -> set[str] | None:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets):
            continue
        if not isinstance(node.value, (ast.List, ast.Tuple, ast.Set)):
            return None

        exports: set[str] = set()
        for element in node.value.elts:
            if not isinstance(element, ast.Constant) or not isinstance(element.value, str):
                return None
            exports.add(element.value)
        return exports
    return None


def _facade_has_only_reexports(path: Path) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if isinstance(node, ast.ImportFrom):
            continue
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets
        ):
            continue
        if (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ):
            continue
        return False
    return True


def check_mcp_architecture(root: Path) -> list[str]:
    mcp_root = root / "skill_runtime" / "mcp"
    runtime_root = root / "skill_runtime"
    readme_path = root / "README.md"
    readme_zh_path = root / "README.zh-CN.md"
    docs_path = root / "docs" / "mcp-integration.md"
    codex_docs_path = root / "docs" / "codex-integration.md"
    workflow_path = root / ".github" / "workflows" / "runtime-contracts.yml"
    service_path = runtime_root / "api" / "service.py"
    library_report_path = runtime_root / "governance" / "library_report.py"
    promotion_guard_path = runtime_root / "governance" / "promotion_guard.py"
    provenance_backfill_path = runtime_root / "governance" / "provenance_backfill.py"
    skill_index_path = runtime_root / "retrieval" / "skill_index.py"
    trajectory_capture_path = runtime_root / "memory" / "trajectory_capture.py"
    trajectory_store_path = runtime_root / "memory" / "trajectory_store.py"
    coverage_report_path = runtime_root / "distill" / "coverage_report.py"
    skill_generator_path = runtime_root / "distill" / "skill_generator.py"
    fallback_service_path = runtime_root / "distill" / "fallback" / "service.py"
    fallback_provider_path = runtime_root / "distill" / "fallback" / "provider.py"
    fallback_mock_provider_path = runtime_root / "distill" / "fallback" / "mock_provider.py"
    fallback_prompt_builder_path = runtime_root / "distill" / "fallback" / "prompt_builder.py"
    rules_registry_path = runtime_root / "distill" / "rules" / "registry.py"
    rules_common_path = runtime_root / "distill" / "rules" / "common.py"
    rules_init_path = runtime_root / "distill" / "rules" / "__init__.py"
    skill_auditor_path = runtime_root / "audit" / "skill_auditor.py"
    semantic_review_service_path = runtime_root / "audit" / "semantic_review_service.py"
    semantic_provider_path = runtime_root / "audit" / "semantic_provider.py"
    semantic_prompt_builder_path = runtime_root / "audit" / "semantic_prompt_builder.py"
    mock_semantic_provider_path = runtime_root / "audit" / "mock_semantic_provider.py"
    semantic_checks_path = runtime_root / "audit" / "semantic_checks.py"
    static_checks_path = runtime_root / "audit" / "static_checks.py"
    skill_executor_path = runtime_root / "execution" / "skill_executor.py"
    skill_loader_path = runtime_root / "execution" / "skill_loader.py"
    runtime_tools_path = runtime_root / "execution" / "runtime_tools.py"
    source_refs_path = mcp_root / "source_refs.py"
    operation_builders_path = mcp_root / "operation_builders.py"
    recommendation_builders_path = mcp_root / "recommendation_builders.py"
    governance_actions_path = mcp_root / "governance_actions.py"
    facade_path = mcp_root / "host_operations.py"

    violations: list[str] = []

    for module_path in (
        source_refs_path,
        operation_builders_path,
        recommendation_builders_path,
        governance_actions_path,
    ):
        if _module_exports(module_path) is None:
            violations.append(f"{module_path.name} must declare a literal __all__ export list.")

    if not _facade_has_only_reexports(facade_path):
        violations.append(
            "host_operations.py must remain a pure re-export facade with imports and __all__ only."
        )

    if not docs_path.exists():
        violations.append("docs/mcp-integration.md must exist and describe the MCP contract layout.")
    else:
        docs_text = docs_path.read_text(encoding="utf-8")
        for required_snippet in (
            "`source_refs.py`",
            "`operation_builders.py`",
            "`recommendation_builders.py`",
            "`governance_actions.py`",
            "`host_operations.py`",
            "`python scripts/check_mcp_architecture.py`",
            "`python scripts/check_runtime_contracts.py`",
        ):
            if required_snippet not in docs_text:
                violations.append(
                    f"docs/mcp-integration.md is missing required MCP architecture reference: {required_snippet}"
                )

    if not codex_docs_path.exists():
        violations.append(
            "docs/codex-integration.md must exist and describe the Codex-side MCP contract surface."
        )
    else:
        codex_docs_text = codex_docs_path.read_text(encoding="utf-8")
        for required_snippet in (
            "`skill_runtime.mcp.host_operations`",
            "`source_refs.py`",
            "`operation_builders.py`",
            "`recommendation_builders.py`",
            "`governance_actions.py`",
            "`python scripts/check_runtime_contracts.py`",
        ):
            if required_snippet not in codex_docs_text:
                violations.append(
                    f"docs/codex-integration.md is missing required Codex integration reference: {required_snippet}"
                )

    readme_requirements = {
        readme_path: (
            "./docs/mcp-integration.md",
            "./docs/codex-integration.md",
            "python scripts/check_mcp_architecture.py",
            "python scripts/check_runtime_contracts.py",
            "service / governance / retrieval",
            "memory / distill / audit / execution",
        ),
        readme_zh_path: (
            "./docs/mcp-integration.md",
            "./docs/codex-integration.md",
            "python scripts/check_mcp_architecture.py",
            "python scripts/check_runtime_contracts.py",
            "service / governance / retrieval",
            "memory / distill / audit / execution",
        ),
    }
    for path, required_snippets in readme_requirements.items():
        if not path.exists():
            violations.append(f"{path.name} must exist and describe the runtime contract guard.")
            continue
        text = path.read_text(encoding="utf-8")
        for required_snippet in required_snippets:
            if required_snippet not in text:
                violations.append(f"{path.name} is missing required runtime architecture reference: {required_snippet}")

    if not workflow_path.exists():
        violations.append(
            ".github/workflows/runtime-contracts.yml must exist and run the MCP architecture checks."
        )
    else:
        workflow_text = workflow_path.read_text(encoding="utf-8")
        for required_snippet in (
            "README.md",
            "README.zh-CN.md",
            "docs/mcp-integration.md",
            "docs/codex-integration.md",
            "python scripts/check_mcp_architecture.py",
            "python scripts/check_runtime_contracts.py",
            "python -m unittest tests.test_runtime -v",
        ):
            if required_snippet not in workflow_text:
                violations.append(
                    ".github/workflows/runtime-contracts.yml is missing required runtime contract coverage: "
                    + required_snippet
                )

    runtime_module_constraints = {
        service_path: {
            "skill_runtime.api.models",
            "skill_runtime.audit.skill_auditor",
            "skill_runtime.distill.coverage_report",
            "skill_runtime.distill.skill_generator",
            "skill_runtime.execution.runtime_tools",
            "skill_runtime.execution.skill_executor",
            "skill_runtime.governance.library_report",
            "skill_runtime.governance.promotion_guard",
            "skill_runtime.governance.provenance_backfill",
            "skill_runtime.mcp.host_operations",
            "skill_runtime.memory.trajectory_capture",
            "skill_runtime.memory.trajectory_store",
            "skill_runtime.retrieval.skill_index",
        },
        library_report_path: {
            "skill_runtime.api.models",
            "skill_runtime.library_tiers",
            "skill_runtime.mcp.host_operations",
            "skill_runtime.retrieval.skill_index",
        },
        promotion_guard_path: {"skill_runtime.api.models"},
        provenance_backfill_path: {
            "skill_runtime.api.models",
            "skill_runtime.retrieval.skill_index",
        },
        skill_index_path: {
            "skill_runtime.api.models",
            "skill_runtime.library_tiers",
            "skill_runtime.mcp.host_operations",
        },
        trajectory_capture_path: {"skill_runtime.api.models"},
        trajectory_store_path: {"skill_runtime.api.models"},
        coverage_report_path: {
            "skill_runtime.mcp.host_operations",
            "skill_runtime.distill.skill_generator",
            "skill_runtime.memory.trajectory_capture",
            "skill_runtime.memory.trajectory_store",
        },
        skill_generator_path: {
            "skill_runtime.api.models",
            "skill_runtime.distill.fallback.service",
            "skill_runtime.distill.rules",
            "skill_runtime.distill.rules.common",
            "skill_runtime.distill.rules.registry",
        },
        fallback_service_path: {
            "skill_runtime.api.models",
            "skill_runtime.distill.fallback.mock_provider",
            "skill_runtime.distill.fallback.prompt_builder",
            "skill_runtime.distill.fallback.provider",
        },
        fallback_provider_path: {"skill_runtime.api.models"},
        fallback_mock_provider_path: {
            "skill_runtime.distill.fallback.provider",
            "skill_runtime.distill.rules.common",
        },
        fallback_prompt_builder_path: {"skill_runtime.api.models"},
        rules_registry_path: {"skill_runtime.api.models"},
        rules_common_path: set(),
        rules_init_path: {
            "skill_runtime.distill.rules",
            "skill_runtime.distill.rules.registry",
        },
        skill_auditor_path: {
            "skill_runtime.api.models",
            "skill_runtime.audit.semantic_checks",
            "skill_runtime.audit.semantic_review_service",
            "skill_runtime.audit.static_checks",
        },
        semantic_review_service_path: {
            "skill_runtime.api.models",
            "skill_runtime.audit.mock_semantic_provider",
            "skill_runtime.audit.semantic_checks",
            "skill_runtime.audit.semantic_prompt_builder",
            "skill_runtime.audit.semantic_provider",
        },
        semantic_provider_path: {
            "skill_runtime.api.models",
            "skill_runtime.audit.semantic_checks",
        },
        semantic_prompt_builder_path: {
            "skill_runtime.api.models",
            "skill_runtime.audit.semantic_checks",
        },
        mock_semantic_provider_path: {
            "skill_runtime.audit.semantic_checks",
            "skill_runtime.audit.semantic_provider",
        },
        semantic_checks_path: {"skill_runtime.api.models"},
        static_checks_path: set(),
        skill_executor_path: {
            "skill_runtime.execution.skill_loader",
            "skill_runtime.retrieval.skill_index",
        },
        skill_loader_path: set(),
        runtime_tools_path: set(),
    }
    for rule_module_path in (runtime_root / "distill" / "rules").glob("*.py"):
        if rule_module_path.name in {"__init__.py", "common.py", "registry.py"}:
            continue
        runtime_module_constraints[rule_module_path] = {
            "skill_runtime.api.models",
            "skill_runtime.distill.rules.common",
        }
    for module_path, allowed_imports in runtime_module_constraints.items():
        if not module_path.exists():
            continue
        actual_imports = {
            name for name in _module_imports(module_path) if name.startswith("skill_runtime.")
        }
        if actual_imports != allowed_imports:
            violations.append(
                f"{module_path.name} imports {sorted(actual_imports)}, expected {sorted(allowed_imports)}"
            )

    source_ref_imports = {
        name for name in _module_imports(source_refs_path) if name.startswith("skill_runtime.mcp.")
    }
    if source_ref_imports:
        violations.append(
            "source_refs.py must not import internal MCP modules: "
            + ", ".join(sorted(source_ref_imports))
        )

    module_constraints = {
        operation_builders_path: {"skill_runtime.mcp.source_refs"},
        recommendation_builders_path: {
            "skill_runtime.mcp.operation_builders",
            "skill_runtime.mcp.source_refs",
        },
        governance_actions_path: {
            "skill_runtime.mcp.operation_builders",
            "skill_runtime.mcp.source_refs",
        },
        facade_path: {
            "skill_runtime.mcp.governance_actions",
            "skill_runtime.mcp.operation_builders",
            "skill_runtime.mcp.recommendation_builders",
            "skill_runtime.mcp.source_refs",
        },
    }
    for module_path, allowed_imports in module_constraints.items():
        actual_imports = {
            name for name in _module_imports(module_path) if name.startswith("skill_runtime.mcp.")
        }
        if actual_imports != allowed_imports:
            violations.append(
                f"{module_path.name} imports {sorted(actual_imports)}, expected {sorted(allowed_imports)}"
            )

    for module_path in root.glob("skill_runtime/**/*.py"):
        if "mcp" in module_path.parts:
            continue
        forbidden_imports = sorted(
            name
            for name in _module_imports(module_path)
            if name.startswith("skill_runtime.mcp.")
            and name not in {"skill_runtime.mcp.host_operations", "skill_runtime.mcp.server"}
        )
        if forbidden_imports:
            violations.append(
                f"{module_path.relative_to(root)} imports internal MCP modules: {', '.join(forbidden_imports)}"
            )

    source_refs = importlib.import_module("skill_runtime.mcp.source_refs")
    operation_builders = importlib.import_module("skill_runtime.mcp.operation_builders")
    recommendation_builders = importlib.import_module("skill_runtime.mcp.recommendation_builders")
    governance_actions = importlib.import_module("skill_runtime.mcp.governance_actions")
    host_operations = importlib.import_module("skill_runtime.mcp.host_operations")

    expected_exports = sorted(
        {
            *source_refs.__all__,
            *operation_builders.__all__,
            *recommendation_builders.__all__,
            *governance_actions.__all__,
        }
    )
    actual_exports = sorted(host_operations.__all__)
    if actual_exports != expected_exports:
        violations.append(
            "host_operations.__all__ must match the combined public exports from "
            "source_refs.__all__, operation_builders.__all__, "
            "recommendation_builders.__all__, and governance_actions.__all__"
        )

    return violations


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    violations = check_mcp_architecture(root)
    if not violations:
        print("MCP architecture check passed.")
        return 0

    print("MCP architecture check failed:")
    for violation in violations:
        print(f"- {violation}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
