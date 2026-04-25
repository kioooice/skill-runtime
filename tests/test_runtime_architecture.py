import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.check_mcp_architecture import check_mcp_architecture
from tests.runtime_test_support import ROOT


class RuntimeArchitectureTestsMixin:
    def test_mcp_module_boundaries_and_public_import_surface(self) -> None:
        source_refs_path = ROOT / "skill_runtime" / "mcp" / "source_refs.py"
        operation_builders_path = ROOT / "skill_runtime" / "mcp" / "operation_builders.py"
        recommendation_builders_path = ROOT / "skill_runtime" / "mcp" / "recommendation_builders.py"
        governance_actions_path = ROOT / "skill_runtime" / "mcp" / "governance_actions.py"
        facade_path = ROOT / "skill_runtime" / "mcp" / "host_operations.py"

        self.assertFalse(
            any(name.startswith("skill_runtime.mcp.") for name in self._module_imports(source_refs_path))
        )

        self.assertEqual(
            {"skill_runtime.mcp.source_refs"},
            {
                name
                for name in self._module_imports(operation_builders_path)
                if name.startswith("skill_runtime.mcp.")
            },
        )
        self.assertEqual(
            {"skill_runtime.mcp.operation_builders", "skill_runtime.mcp.source_refs"},
            {
                name
                for name in self._module_imports(recommendation_builders_path)
                if name.startswith("skill_runtime.mcp.")
            },
        )
        self.assertEqual(
            {"skill_runtime.mcp.operation_builders", "skill_runtime.mcp.source_refs"},
            {
                name
                for name in self._module_imports(governance_actions_path)
                if name.startswith("skill_runtime.mcp.")
            },
        )
        self.assertEqual(
            {
                "skill_runtime.mcp.governance_actions",
                "skill_runtime.mcp.operation_builders",
                "skill_runtime.mcp.recommendation_builders",
                "skill_runtime.mcp.source_refs",
            },
            {
                name
                for name in self._module_imports(facade_path)
                if name.startswith("skill_runtime.mcp.")
            },
        )

        forbidden_public_imports: list[str] = []
        for module_path in ROOT.glob("skill_runtime/**/*.py"):
            if "mcp" in module_path.parts:
                continue
            imports = self._module_imports(module_path)
            forbidden_public_imports.extend(
                sorted(
                    name
                    for name in imports
                    if name.startswith("skill_runtime.mcp.")
                    and name not in {"skill_runtime.mcp.host_operations", "skill_runtime.mcp.server"}
                )
            )

        self.assertEqual([], forbidden_public_imports)

    def test_runtime_service_governance_and_retrieval_module_boundaries(self) -> None:
        service_path = ROOT / "skill_runtime" / "api" / "service.py"
        library_report_path = ROOT / "skill_runtime" / "governance" / "library_report.py"
        promotion_guard_path = ROOT / "skill_runtime" / "governance" / "promotion_guard.py"
        provenance_backfill_path = ROOT / "skill_runtime" / "governance" / "provenance_backfill.py"
        skill_index_path = ROOT / "skill_runtime" / "retrieval" / "skill_index.py"

        self.assertEqual(
            {
                "skill_runtime.api.models",
                "skill_runtime.audit.skill_auditor",
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
            {
                name
                for name in self._module_imports(service_path)
                if name.startswith("skill_runtime.")
            },
        )
        self.assertEqual(
            {
                "skill_runtime.api.models",
                "skill_runtime.mcp.host_operations",
                "skill_runtime.retrieval.skill_index",
            },
            {
                name
                for name in self._module_imports(library_report_path)
                if name.startswith("skill_runtime.")
            },
        )
        self.assertEqual(
            {"skill_runtime.api.models"},
            {
                name
                for name in self._module_imports(promotion_guard_path)
                if name.startswith("skill_runtime.")
            },
        )
        self.assertEqual(
            {"skill_runtime.api.models", "skill_runtime.retrieval.skill_index"},
            {
                name
                for name in self._module_imports(provenance_backfill_path)
                if name.startswith("skill_runtime.")
            },
        )
        self.assertEqual(
            {"skill_runtime.api.models", "skill_runtime.mcp.host_operations"},
            {
                name
                for name in self._module_imports(skill_index_path)
                if name.startswith("skill_runtime.")
            },
        )

    def test_runtime_memory_distill_audit_and_execution_module_boundaries(self) -> None:
        trajectory_capture_path = ROOT / "skill_runtime" / "memory" / "trajectory_capture.py"
        trajectory_store_path = ROOT / "skill_runtime" / "memory" / "trajectory_store.py"
        skill_generator_path = ROOT / "skill_runtime" / "distill" / "skill_generator.py"
        skill_auditor_path = ROOT / "skill_runtime" / "audit" / "skill_auditor.py"
        skill_executor_path = ROOT / "skill_runtime" / "execution" / "skill_executor.py"
        skill_loader_path = ROOT / "skill_runtime" / "execution" / "skill_loader.py"
        runtime_tools_path = ROOT / "skill_runtime" / "execution" / "runtime_tools.py"

        self.assertEqual(
            {"skill_runtime.api.models"},
            {
                name
                for name in self._module_imports(trajectory_capture_path)
                if name.startswith("skill_runtime.")
            },
        )
        self.assertEqual(
            {"skill_runtime.api.models"},
            {
                name
                for name in self._module_imports(trajectory_store_path)
                if name.startswith("skill_runtime.")
            },
        )
        self.assertEqual(
            {
                "skill_runtime.api.models",
                "skill_runtime.distill.fallback.service",
                "skill_runtime.distill.rules",
                "skill_runtime.distill.rules.common",
                "skill_runtime.distill.rules.registry",
            },
            {
                name
                for name in self._module_imports(skill_generator_path)
                if name.startswith("skill_runtime.")
            },
        )
        self.assertEqual(
            {
                "skill_runtime.api.models",
                "skill_runtime.audit.semantic_checks",
                "skill_runtime.audit.semantic_review_service",
                "skill_runtime.audit.static_checks",
            },
            {
                name
                for name in self._module_imports(skill_auditor_path)
                if name.startswith("skill_runtime.")
            },
        )
        self.assertEqual(
            {"skill_runtime.execution.skill_loader", "skill_runtime.retrieval.skill_index"},
            {
                name
                for name in self._module_imports(skill_executor_path)
                if name.startswith("skill_runtime.")
            },
        )
        self.assertEqual(set(), {name for name in self._module_imports(skill_loader_path) if name.startswith("skill_runtime.")})
        self.assertEqual(set(), {name for name in self._module_imports(runtime_tools_path) if name.startswith("skill_runtime.")})

    def test_runtime_distill_fallback_rules_and_audit_sublayer_boundaries(self) -> None:
        fallback_service_path = ROOT / "skill_runtime" / "distill" / "fallback" / "service.py"
        fallback_provider_path = ROOT / "skill_runtime" / "distill" / "fallback" / "provider.py"
        fallback_mock_provider_path = ROOT / "skill_runtime" / "distill" / "fallback" / "mock_provider.py"
        fallback_prompt_builder_path = ROOT / "skill_runtime" / "distill" / "fallback" / "prompt_builder.py"
        rules_registry_path = ROOT / "skill_runtime" / "distill" / "rules" / "registry.py"
        rules_common_path = ROOT / "skill_runtime" / "distill" / "rules" / "common.py"
        rules_init_path = ROOT / "skill_runtime" / "distill" / "rules" / "__init__.py"
        semantic_review_service_path = ROOT / "skill_runtime" / "audit" / "semantic_review_service.py"
        semantic_provider_path = ROOT / "skill_runtime" / "audit" / "semantic_provider.py"
        semantic_prompt_builder_path = ROOT / "skill_runtime" / "audit" / "semantic_prompt_builder.py"
        mock_semantic_provider_path = ROOT / "skill_runtime" / "audit" / "mock_semantic_provider.py"
        semantic_checks_path = ROOT / "skill_runtime" / "audit" / "semantic_checks.py"
        static_checks_path = ROOT / "skill_runtime" / "audit" / "static_checks.py"

        self.assertEqual(
            {
                "skill_runtime.api.models",
                "skill_runtime.distill.fallback.mock_provider",
                "skill_runtime.distill.fallback.prompt_builder",
                "skill_runtime.distill.fallback.provider",
            },
            {
                name
                for name in self._module_imports(fallback_service_path)
                if name.startswith("skill_runtime.")
            },
        )
        self.assertEqual(
            {"skill_runtime.api.models"},
            {
                name
                for name in self._module_imports(fallback_provider_path)
                if name.startswith("skill_runtime.")
            },
        )
        self.assertEqual(
            {
                "skill_runtime.distill.fallback.provider",
                "skill_runtime.distill.rules.common",
            },
            {
                name
                for name in self._module_imports(fallback_mock_provider_path)
                if name.startswith("skill_runtime.")
            },
        )
        self.assertEqual(
            {"skill_runtime.api.models"},
            {
                name
                for name in self._module_imports(fallback_prompt_builder_path)
                if name.startswith("skill_runtime.")
            },
        )
        self.assertEqual(
            {"skill_runtime.api.models"},
            {
                name
                for name in self._module_imports(rules_registry_path)
                if name.startswith("skill_runtime.")
            },
        )
        self.assertEqual(set(), {name for name in self._module_imports(rules_common_path) if name.startswith("skill_runtime.")})
        self.assertEqual(
            {"skill_runtime.distill.rules", "skill_runtime.distill.rules.registry"},
            {
                name
                for name in self._module_imports(rules_init_path)
                if name.startswith("skill_runtime.")
            },
        )
        for rule_name in (
            "batch_rename.py",
            "csv_to_json.py",
            "directory_copy.py",
            "directory_move.py",
            "directory_text_replace.py",
            "json_to_csv.py",
            "single_file_transform.py",
            "text_merge.py",
            "text_replace.py",
        ):
            rule_path = ROOT / "skill_runtime" / "distill" / "rules" / rule_name
            self.assertEqual(
                {"skill_runtime.api.models", "skill_runtime.distill.rules.common"},
                {
                    name
                    for name in self._module_imports(rule_path)
                    if name.startswith("skill_runtime.")
                },
                msg=f"Unexpected imports in {rule_name}",
            )

        self.assertEqual(
            {
                "skill_runtime.api.models",
                "skill_runtime.audit.mock_semantic_provider",
                "skill_runtime.audit.semantic_checks",
                "skill_runtime.audit.semantic_prompt_builder",
                "skill_runtime.audit.semantic_provider",
            },
            {
                name
                for name in self._module_imports(semantic_review_service_path)
                if name.startswith("skill_runtime.")
            },
        )
        self.assertEqual(
            {"skill_runtime.api.models", "skill_runtime.audit.semantic_checks"},
            {
                name
                for name in self._module_imports(semantic_provider_path)
                if name.startswith("skill_runtime.")
            },
        )
        self.assertEqual(
            {"skill_runtime.api.models", "skill_runtime.audit.semantic_checks"},
            {
                name
                for name in self._module_imports(semantic_prompt_builder_path)
                if name.startswith("skill_runtime.")
            },
        )
        self.assertEqual(
            {"skill_runtime.audit.semantic_checks", "skill_runtime.audit.semantic_provider"},
            {
                name
                for name in self._module_imports(mock_semantic_provider_path)
                if name.startswith("skill_runtime.")
            },
        )
        self.assertEqual(
            {"skill_runtime.api.models"},
            {
                name
                for name in self._module_imports(semantic_checks_path)
                if name.startswith("skill_runtime.")
            },
        )
        self.assertEqual(set(), {name for name in self._module_imports(static_checks_path) if name.startswith("skill_runtime.")})

    def test_check_mcp_architecture_script_passes(self) -> None:
        script = ROOT / "scripts" / "check_mcp_architecture.py"
        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(
            0,
            result.returncode,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        self.assertIn("MCP architecture check passed.", result.stdout)

    def test_mcp_facade_exports_match_internal_module_exports(self) -> None:
        from skill_runtime.mcp import governance_actions, host_operations, operation_builders
        from skill_runtime.mcp import recommendation_builders, source_refs

        expected_exports = sorted(
            {
                *source_refs.__all__,
                *operation_builders.__all__,
                *recommendation_builders.__all__,
                *governance_actions.__all__,
            }
        )

        self.assertEqual(expected_exports, sorted(host_operations.__all__))

    def test_check_mcp_architecture_script_mentions_export_surface(self) -> None:
        script = ROOT / "scripts" / "check_mcp_architecture.py"
        script_source = script.read_text(encoding="utf-8")
        self.assertIn("host_operations.__all__", script_source)
        self.assertIn("source_refs.__all__", script_source)
        self.assertIn("check_runtime_contracts.py", script_source)

    def test_check_mcp_architecture_detects_missing_internal_module_exports(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            mcp_root = root / "skill_runtime" / "mcp"
            mcp_root.mkdir(parents=True)
            (root / "skill_runtime" / "__init__.py").write_text("", encoding="utf-8")
            (mcp_root / "__init__.py").write_text("", encoding="utf-8")
            (mcp_root / "source_refs.py").write_text("VALUE = 1\n", encoding="utf-8")
            (mcp_root / "operation_builders.py").write_text(
                "from skill_runtime.mcp.source_refs import VALUE\n__all__ = ['VALUE']\n",
                encoding="utf-8",
            )
            (mcp_root / "recommendation_builders.py").write_text(
                "from skill_runtime.mcp.operation_builders import VALUE\n"
                "from skill_runtime.mcp.source_refs import VALUE as SOURCE\n"
                "__all__ = ['VALUE', 'SOURCE']\n",
                encoding="utf-8",
            )
            (mcp_root / "governance_actions.py").write_text(
                "from skill_runtime.mcp.operation_builders import VALUE\n"
                "from skill_runtime.mcp.source_refs import VALUE as SOURCE\n"
                "__all__ = ['VALUE', 'SOURCE']\n",
                encoding="utf-8",
            )
            (mcp_root / "host_operations.py").write_text(
                "from skill_runtime.mcp.governance_actions import *\n"
                "from skill_runtime.mcp.governance_actions import __all__ as _governance_all\n"
                "from skill_runtime.mcp.operation_builders import *\n"
                "from skill_runtime.mcp.operation_builders import __all__ as _operations_all\n"
                "from skill_runtime.mcp.recommendation_builders import *\n"
                "from skill_runtime.mcp.recommendation_builders import __all__ as _recommendations_all\n"
                "from skill_runtime.mcp.source_refs import *\n"
                "from skill_runtime.mcp.source_refs import __all__ as _source_refs_all\n"
                "__all__ = [*_operations_all, *_recommendations_all, *_governance_all, *_source_refs_all]\n",
                encoding="utf-8",
            )

            violations = check_mcp_architecture(root)

        self.assertTrue(any("source_refs.py" in violation and "__all__" in violation for violation in violations))

    def test_check_mcp_architecture_detects_facade_implementation_logic(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            mcp_root = root / "skill_runtime" / "mcp"
            mcp_root.mkdir(parents=True)
            (root / "skill_runtime" / "__init__.py").write_text("", encoding="utf-8")
            (mcp_root / "__init__.py").write_text("", encoding="utf-8")
            (mcp_root / "source_refs.py").write_text("__all__ = ['VALUE']\nVALUE = 1\n", encoding="utf-8")
            (mcp_root / "operation_builders.py").write_text(
                "from skill_runtime.mcp.source_refs import VALUE\n__all__ = ['VALUE']\n",
                encoding="utf-8",
            )
            (mcp_root / "recommendation_builders.py").write_text(
                "from skill_runtime.mcp.operation_builders import VALUE\n"
                "from skill_runtime.mcp.source_refs import VALUE as SOURCE\n"
                "__all__ = ['VALUE', 'SOURCE']\n",
                encoding="utf-8",
            )
            (mcp_root / "governance_actions.py").write_text(
                "from skill_runtime.mcp.operation_builders import VALUE\n"
                "from skill_runtime.mcp.source_refs import VALUE as SOURCE\n"
                "__all__ = ['VALUE', 'SOURCE']\n",
                encoding="utf-8",
            )
            (mcp_root / "host_operations.py").write_text(
                "from skill_runtime.mcp.governance_actions import *\n"
                "from skill_runtime.mcp.governance_actions import __all__ as _governance_all\n"
                "from skill_runtime.mcp.operation_builders import *\n"
                "from skill_runtime.mcp.operation_builders import __all__ as _operations_all\n"
                "from skill_runtime.mcp.recommendation_builders import *\n"
                "from skill_runtime.mcp.recommendation_builders import __all__ as _recommendations_all\n"
                "from skill_runtime.mcp.source_refs import *\n"
                "from skill_runtime.mcp.source_refs import __all__ as _source_refs_all\n"
                "def leaked_helper():\n"
                "    return 'should not exist'\n"
                "__all__ = [*_operations_all, *_recommendations_all, *_governance_all, *_source_refs_all]\n",
                encoding="utf-8",
            )

            violations = check_mcp_architecture(root)

        self.assertTrue(any("host_operations.py" in violation and "re-export" in violation for violation in violations))

    def test_check_mcp_architecture_detects_mcp_docs_layout_drift(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            docs_root = root / "docs"
            mcp_root = root / "skill_runtime" / "mcp"
            docs_root.mkdir(parents=True)
            mcp_root.mkdir(parents=True)
            (root / "skill_runtime" / "__init__.py").write_text("", encoding="utf-8")
            (mcp_root / "__init__.py").write_text("", encoding="utf-8")
            (mcp_root / "source_refs.py").write_text("__all__ = ['VALUE']\nVALUE = 1\n", encoding="utf-8")
            (mcp_root / "operation_builders.py").write_text(
                "from skill_runtime.mcp.source_refs import VALUE\n__all__ = ['VALUE']\n",
                encoding="utf-8",
            )
            (mcp_root / "recommendation_builders.py").write_text(
                "from skill_runtime.mcp.operation_builders import VALUE\n"
                "from skill_runtime.mcp.source_refs import VALUE as SOURCE\n"
                "__all__ = ['VALUE', 'SOURCE']\n",
                encoding="utf-8",
            )
            (mcp_root / "governance_actions.py").write_text(
                "from skill_runtime.mcp.operation_builders import VALUE\n"
                "from skill_runtime.mcp.source_refs import VALUE as SOURCE\n"
                "__all__ = ['VALUE', 'SOURCE']\n",
                encoding="utf-8",
            )
            (mcp_root / "host_operations.py").write_text(
                "from skill_runtime.mcp.governance_actions import *\n"
                "from skill_runtime.mcp.governance_actions import __all__ as _governance_all\n"
                "from skill_runtime.mcp.operation_builders import *\n"
                "from skill_runtime.mcp.operation_builders import __all__ as _operations_all\n"
                "from skill_runtime.mcp.recommendation_builders import *\n"
                "from skill_runtime.mcp.recommendation_builders import __all__ as _recommendations_all\n"
                "from skill_runtime.mcp.source_refs import *\n"
                "from skill_runtime.mcp.source_refs import __all__ as _source_refs_all\n"
                "__all__ = [*_operations_all, *_recommendations_all, *_governance_all, *_source_refs_all]\n",
                encoding="utf-8",
            )
            (docs_root / "mcp-integration.md").write_text(
                "# MCP Integration\n\n- `source_refs.py`\n- `host_operations.py`\n",
                encoding="utf-8",
            )

            violations = check_mcp_architecture(root)

        self.assertTrue(any("docs/mcp-integration.md" in violation for violation in violations))

    def test_check_mcp_architecture_detects_workflow_coverage_drift(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            docs_root = root / "docs"
            workflows_root = root / ".github" / "workflows"
            mcp_root = root / "skill_runtime" / "mcp"
            docs_root.mkdir(parents=True)
            workflows_root.mkdir(parents=True)
            mcp_root.mkdir(parents=True)
            (root / "skill_runtime" / "__init__.py").write_text("", encoding="utf-8")
            (mcp_root / "__init__.py").write_text("", encoding="utf-8")
            (mcp_root / "source_refs.py").write_text("__all__ = ['VALUE']\nVALUE = 1\n", encoding="utf-8")
            (mcp_root / "operation_builders.py").write_text(
                "from skill_runtime.mcp.source_refs import VALUE\n__all__ = ['VALUE']\n",
                encoding="utf-8",
            )
            (mcp_root / "recommendation_builders.py").write_text(
                "from skill_runtime.mcp.operation_builders import VALUE\n"
                "from skill_runtime.mcp.source_refs import VALUE as SOURCE\n"
                "__all__ = ['VALUE', 'SOURCE']\n",
                encoding="utf-8",
            )
            (mcp_root / "governance_actions.py").write_text(
                "from skill_runtime.mcp.operation_builders import VALUE\n"
                "from skill_runtime.mcp.source_refs import VALUE as SOURCE\n"
                "__all__ = ['VALUE', 'SOURCE']\n",
                encoding="utf-8",
            )
            (mcp_root / "host_operations.py").write_text(
                "from skill_runtime.mcp.governance_actions import *\n"
                "from skill_runtime.mcp.governance_actions import __all__ as _governance_all\n"
                "from skill_runtime.mcp.operation_builders import *\n"
                "from skill_runtime.mcp.operation_builders import __all__ as _operations_all\n"
                "from skill_runtime.mcp.recommendation_builders import *\n"
                "from skill_runtime.mcp.recommendation_builders import __all__ as _recommendations_all\n"
                "from skill_runtime.mcp.source_refs import *\n"
                "from skill_runtime.mcp.source_refs import __all__ as _source_refs_all\n"
                "__all__ = [*_operations_all, *_recommendations_all, *_governance_all, *_source_refs_all]\n",
                encoding="utf-8",
            )
            (docs_root / "mcp-integration.md").write_text(
                "# MCP Integration\n\n"
                "- `source_refs.py`\n"
                "- `operation_builders.py`\n"
                "- `recommendation_builders.py`\n"
                "- `governance_actions.py`\n"
                "- `host_operations.py`\n"
                "- `python scripts/check_mcp_architecture.py`\n",
                encoding="utf-8",
            )
            (workflows_root / "runtime-contracts.yml").write_text(
                "name: Runtime Contracts\njobs:\n  runtime-contracts:\n    steps:\n"
                "      - run: python -m unittest tests.test_runtime -v\n",
                encoding="utf-8",
            )

            violations = check_mcp_architecture(root)

        self.assertTrue(any("runtime-contracts.yml" in violation for violation in violations))

    def test_check_mcp_architecture_detects_codex_docs_drift(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            docs_root = root / "docs"
            workflows_root = root / ".github" / "workflows"
            mcp_root = root / "skill_runtime" / "mcp"
            docs_root.mkdir(parents=True)
            workflows_root.mkdir(parents=True)
            mcp_root.mkdir(parents=True)
            (root / "skill_runtime" / "__init__.py").write_text("", encoding="utf-8")
            (mcp_root / "__init__.py").write_text("", encoding="utf-8")
            (mcp_root / "source_refs.py").write_text("__all__ = ['VALUE']\nVALUE = 1\n", encoding="utf-8")
            (mcp_root / "operation_builders.py").write_text(
                "from skill_runtime.mcp.source_refs import VALUE\n__all__ = ['VALUE']\n",
                encoding="utf-8",
            )
            (mcp_root / "recommendation_builders.py").write_text(
                "from skill_runtime.mcp.operation_builders import VALUE\n"
                "from skill_runtime.mcp.source_refs import VALUE as SOURCE\n"
                "__all__ = ['VALUE', 'SOURCE']\n",
                encoding="utf-8",
            )
            (mcp_root / "governance_actions.py").write_text(
                "from skill_runtime.mcp.operation_builders import VALUE\n"
                "from skill_runtime.mcp.source_refs import VALUE as SOURCE\n"
                "__all__ = ['VALUE', 'SOURCE']\n",
                encoding="utf-8",
            )
            (mcp_root / "host_operations.py").write_text(
                "from skill_runtime.mcp.governance_actions import *\n"
                "from skill_runtime.mcp.governance_actions import __all__ as _governance_all\n"
                "from skill_runtime.mcp.operation_builders import *\n"
                "from skill_runtime.mcp.operation_builders import __all__ as _operations_all\n"
                "from skill_runtime.mcp.recommendation_builders import *\n"
                "from skill_runtime.mcp.recommendation_builders import __all__ as _recommendations_all\n"
                "from skill_runtime.mcp.source_refs import *\n"
                "from skill_runtime.mcp.source_refs import __all__ as _source_refs_all\n"
                "__all__ = [*_operations_all, *_recommendations_all, *_governance_all, *_source_refs_all]\n",
                encoding="utf-8",
            )
            (docs_root / "mcp-integration.md").write_text(
                "# MCP Integration\n\n"
                "- `source_refs.py`\n"
                "- `operation_builders.py`\n"
                "- `recommendation_builders.py`\n"
                "- `governance_actions.py`\n"
                "- `host_operations.py`\n"
                "- `python scripts/check_mcp_architecture.py`\n",
                encoding="utf-8",
            )
            (docs_root / "codex-integration.md").write_text(
                "# Codex Integration\n\n`skill_runtime.mcp.host_operations`\n",
                encoding="utf-8",
            )
            (workflows_root / "runtime-contracts.yml").write_text(
                "name: Runtime Contracts\n"
                "on:\n  push:\n    paths:\n      - \"docs/mcp-integration.md\"\n      - \"docs/codex-integration.md\"\n"
                "jobs:\n  runtime-contracts:\n    steps:\n"
                "      - run: python scripts/check_mcp_architecture.py\n"
                "      - run: python -m unittest tests.test_runtime -v\n",
                encoding="utf-8",
            )

            violations = check_mcp_architecture(root)

        self.assertTrue(any("docs/codex-integration.md" in violation for violation in violations))

    def test_check_mcp_architecture_detects_runtime_layer_dependency_drift(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            docs_root = root / "docs"
            workflows_root = root / ".github" / "workflows"
            for package in (
                root / "skill_runtime",
                root / "skill_runtime" / "api",
                root / "skill_runtime" / "governance",
                root / "skill_runtime" / "retrieval",
                root / "skill_runtime" / "mcp",
            ):
                package.mkdir(parents=True, exist_ok=True)
                (package / "__init__.py").write_text("", encoding="utf-8")

            docs_root.mkdir(parents=True)
            workflows_root.mkdir(parents=True)
            (root / "skill_runtime" / "api" / "models.py").write_text("", encoding="utf-8")
            (root / "skill_runtime" / "api" / "service.py").write_text(
                "from skill_runtime.retrieval.skill_index import SkillIndex\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "governance" / "library_report.py").write_text(
                "from skill_runtime.api.service import RuntimeService\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "governance" / "promotion_guard.py").write_text(
                "from skill_runtime.api.models import AuditReport\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "governance" / "provenance_backfill.py").write_text(
                "from skill_runtime.api.models import SkillMetadata\n"
                "from skill_runtime.retrieval.skill_index import SkillIndex\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "retrieval" / "skill_index.py").write_text(
                "from skill_runtime.api.models import SkillMetadata\n"
                "from skill_runtime.api.service import RuntimeService\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "mcp" / "source_refs.py").write_text("__all__ = []\n", encoding="utf-8")
            (root / "skill_runtime" / "mcp" / "operation_builders.py").write_text(
                "from skill_runtime.mcp.source_refs import *\n__all__ = []\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "mcp" / "recommendation_builders.py").write_text(
                "from skill_runtime.mcp.operation_builders import *\n"
                "from skill_runtime.mcp.source_refs import *\n"
                "__all__ = []\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "mcp" / "governance_actions.py").write_text(
                "from skill_runtime.mcp.operation_builders import *\n"
                "from skill_runtime.mcp.source_refs import *\n"
                "__all__ = []\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "mcp" / "host_operations.py").write_text(
                "from skill_runtime.mcp.governance_actions import *\n"
                "from skill_runtime.mcp.governance_actions import __all__ as _governance_all\n"
                "from skill_runtime.mcp.operation_builders import *\n"
                "from skill_runtime.mcp.operation_builders import __all__ as _operations_all\n"
                "from skill_runtime.mcp.recommendation_builders import *\n"
                "from skill_runtime.mcp.recommendation_builders import __all__ as _recommendations_all\n"
                "from skill_runtime.mcp.source_refs import *\n"
                "from skill_runtime.mcp.source_refs import __all__ as _source_refs_all\n"
                "__all__ = [*_operations_all, *_recommendations_all, *_governance_all, *_source_refs_all]\n",
                encoding="utf-8",
            )
            (docs_root / "mcp-integration.md").write_text(
                "# MCP Integration\n\n"
                "- `source_refs.py`\n- `operation_builders.py`\n- `recommendation_builders.py`\n"
                "- `governance_actions.py`\n- `host_operations.py`\n"
                "- `python scripts/check_mcp_architecture.py`\n",
                encoding="utf-8",
            )
            (docs_root / "codex-integration.md").write_text(
                "# Codex Integration\n\n"
                "`skill_runtime.mcp.host_operations`\n`source_refs.py`\n`operation_builders.py`\n"
                "`recommendation_builders.py`\n`governance_actions.py`\n",
                encoding="utf-8",
            )
            (workflows_root / "runtime-contracts.yml").write_text(
                "name: Runtime Contracts\n"
                "on:\n  push:\n    paths:\n      - \"docs/mcp-integration.md\"\n      - \"docs/codex-integration.md\"\n"
                "jobs:\n  runtime-contracts:\n    steps:\n"
                "      - run: python scripts/check_mcp_architecture.py\n"
                "      - run: python -m unittest tests.test_runtime -v\n",
                encoding="utf-8",
            )

            violations = check_mcp_architecture(root)

        self.assertTrue(any("library_report.py" in violation for violation in violations))
        self.assertTrue(any("skill_index.py" in violation for violation in violations))

    def test_check_mcp_architecture_detects_memory_distill_audit_execution_dependency_drift(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            docs_root = root / "docs"
            workflows_root = root / ".github" / "workflows"
            for package in (
                root / "skill_runtime",
                root / "skill_runtime" / "api",
                root / "skill_runtime" / "governance",
                root / "skill_runtime" / "retrieval",
                root / "skill_runtime" / "mcp",
                root / "skill_runtime" / "memory",
                root / "skill_runtime" / "distill",
                root / "skill_runtime" / "distill" / "fallback",
                root / "skill_runtime" / "distill" / "rules",
                root / "skill_runtime" / "audit",
                root / "skill_runtime" / "execution",
            ):
                package.mkdir(parents=True, exist_ok=True)
                (package / "__init__.py").write_text("", encoding="utf-8")

            docs_root.mkdir(parents=True)
            workflows_root.mkdir(parents=True)
            (root / "skill_runtime" / "api" / "models.py").write_text("", encoding="utf-8")
            (root / "skill_runtime" / "api" / "service.py").write_text(
                "from skill_runtime.retrieval.skill_index import SkillIndex\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "governance" / "library_report.py").write_text(
                "from skill_runtime.retrieval.skill_index import SkillIndex\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "governance" / "promotion_guard.py").write_text(
                "from skill_runtime.api.models import AuditReport\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "governance" / "provenance_backfill.py").write_text(
                "from skill_runtime.api.models import SkillMetadata\n"
                "from skill_runtime.retrieval.skill_index import SkillIndex\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "retrieval" / "skill_index.py").write_text(
                "from skill_runtime.api.models import SkillMetadata\n"
                "from skill_runtime.mcp.host_operations import search_result_payload\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "memory" / "trajectory_capture.py").write_text(
                "from skill_runtime.api.models import Trajectory\n"
                "from skill_runtime.api.service import RuntimeService\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "memory" / "trajectory_store.py").write_text(
                "from skill_runtime.api.models import Trajectory\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "distill" / "fallback" / "service.py").write_text("", encoding="utf-8")
            (root / "skill_runtime" / "distill" / "rules" / "common.py").write_text("", encoding="utf-8")
            (root / "skill_runtime" / "distill" / "rules" / "registry.py").write_text("", encoding="utf-8")
            (root / "skill_runtime" / "distill" / "rules" / "__init__.py").write_text("", encoding="utf-8")
            (root / "skill_runtime" / "distill" / "skill_generator.py").write_text(
                "from skill_runtime.api.models import SkillMetadata\n"
                "from skill_runtime.api.service import RuntimeService\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "audit" / "semantic_checks.py").write_text("", encoding="utf-8")
            (root / "skill_runtime" / "audit" / "semantic_review_service.py").write_text("", encoding="utf-8")
            (root / "skill_runtime" / "audit" / "static_checks.py").write_text("", encoding="utf-8")
            (root / "skill_runtime" / "audit" / "skill_auditor.py").write_text(
                "from skill_runtime.api.models import AuditReport\n"
                "from skill_runtime.execution.skill_executor import SkillExecutor\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "execution" / "skill_loader.py").write_text("", encoding="utf-8")
            (root / "skill_runtime" / "execution" / "runtime_tools.py").write_text("", encoding="utf-8")
            (root / "skill_runtime" / "execution" / "skill_executor.py").write_text(
                "from skill_runtime.execution.skill_loader import SkillLoader\n"
                "from skill_runtime.api.service import RuntimeService\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "mcp" / "source_refs.py").write_text("__all__ = []\n", encoding="utf-8")
            (root / "skill_runtime" / "mcp" / "operation_builders.py").write_text(
                "from skill_runtime.mcp.source_refs import *\n__all__ = []\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "mcp" / "recommendation_builders.py").write_text(
                "from skill_runtime.mcp.operation_builders import *\nfrom skill_runtime.mcp.source_refs import *\n__all__ = []\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "mcp" / "governance_actions.py").write_text(
                "from skill_runtime.mcp.operation_builders import *\nfrom skill_runtime.mcp.source_refs import *\n__all__ = []\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "mcp" / "host_operations.py").write_text(
                "from skill_runtime.mcp.governance_actions import *\n"
                "from skill_runtime.mcp.governance_actions import __all__ as _governance_all\n"
                "from skill_runtime.mcp.operation_builders import *\n"
                "from skill_runtime.mcp.operation_builders import __all__ as _operations_all\n"
                "from skill_runtime.mcp.recommendation_builders import *\n"
                "from skill_runtime.mcp.recommendation_builders import __all__ as _recommendations_all\n"
                "from skill_runtime.mcp.source_refs import *\n"
                "from skill_runtime.mcp.source_refs import __all__ as _source_refs_all\n"
                "__all__ = [*_operations_all, *_recommendations_all, *_governance_all, *_source_refs_all]\n",
                encoding="utf-8",
            )
            (docs_root / "mcp-integration.md").write_text(
                "# MCP Integration\n\n- `source_refs.py`\n- `operation_builders.py`\n- `recommendation_builders.py`\n- `governance_actions.py`\n- `host_operations.py`\n- `python scripts/check_mcp_architecture.py`\n",
                encoding="utf-8",
            )
            (docs_root / "codex-integration.md").write_text(
                "# Codex Integration\n\n`skill_runtime.mcp.host_operations`\n`source_refs.py`\n`operation_builders.py`\n`recommendation_builders.py`\n`governance_actions.py`\n",
                encoding="utf-8",
            )
            (workflows_root / "runtime-contracts.yml").write_text(
                "name: Runtime Contracts\non:\n  push:\n    paths:\n      - \"docs/mcp-integration.md\"\n      - \"docs/codex-integration.md\"\n"
                "jobs:\n  runtime-contracts:\n    steps:\n      - run: python scripts/check_mcp_architecture.py\n      - run: python -m unittest tests.test_runtime -v\n",
                encoding="utf-8",
            )

            violations = check_mcp_architecture(root)

        self.assertTrue(any("trajectory_capture.py" in violation for violation in violations))
        self.assertTrue(any("skill_generator.py" in violation for violation in violations))
        self.assertTrue(any("skill_auditor.py" in violation for violation in violations))
        self.assertTrue(any("skill_executor.py" in violation for violation in violations))

    def test_check_mcp_architecture_detects_distill_and_audit_sublayer_drift(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            docs_root = root / "docs"
            workflows_root = root / ".github" / "workflows"
            for package in (
                root / "skill_runtime",
                root / "skill_runtime" / "api",
                root / "skill_runtime" / "governance",
                root / "skill_runtime" / "retrieval",
                root / "skill_runtime" / "mcp",
                root / "skill_runtime" / "memory",
                root / "skill_runtime" / "distill",
                root / "skill_runtime" / "distill" / "fallback",
                root / "skill_runtime" / "distill" / "rules",
                root / "skill_runtime" / "audit",
                root / "skill_runtime" / "execution",
            ):
                package.mkdir(parents=True, exist_ok=True)
                (package / "__init__.py").write_text("", encoding="utf-8")

            docs_root.mkdir(parents=True)
            workflows_root.mkdir(parents=True)
            (root / "skill_runtime" / "api" / "models.py").write_text("", encoding="utf-8")
            (root / "skill_runtime" / "api" / "service.py").write_text(
                "from skill_runtime.retrieval.skill_index import SkillIndex\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "governance" / "library_report.py").write_text(
                "from skill_runtime.retrieval.skill_index import SkillIndex\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "governance" / "promotion_guard.py").write_text(
                "from skill_runtime.api.models import AuditReport\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "governance" / "provenance_backfill.py").write_text(
                "from skill_runtime.api.models import SkillMetadata\nfrom skill_runtime.retrieval.skill_index import SkillIndex\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "retrieval" / "skill_index.py").write_text(
                "from skill_runtime.api.models import SkillMetadata\nfrom skill_runtime.mcp.host_operations import search_result_payload\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "memory" / "trajectory_capture.py").write_text(
                "from skill_runtime.api.models import Trajectory\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "memory" / "trajectory_store.py").write_text(
                "from skill_runtime.api.models import Trajectory\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "distill" / "skill_generator.py").write_text(
                "from skill_runtime.api.models import SkillMetadata\n"
                "from skill_runtime.distill.fallback.service import FallbackService\n"
                "from skill_runtime.distill.rules import RULES\n"
                "from skill_runtime.distill.rules.common import escape\n"
                "from skill_runtime.distill.rules.registry import explain_match\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "distill" / "fallback" / "service.py").write_text(
                "from skill_runtime.api.models import Trajectory\n"
                "from skill_runtime.api.service import RuntimeService\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "distill" / "fallback" / "provider.py").write_text(
                "from skill_runtime.api.models import Trajectory\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "distill" / "fallback" / "mock_provider.py").write_text(
                "from skill_runtime.distill.fallback.provider import FallbackRequest\n"
                "from skill_runtime.api.service import RuntimeService\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "distill" / "fallback" / "prompt_builder.py").write_text(
                "from skill_runtime.api.models import Trajectory\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "distill" / "rules" / "registry.py").write_text(
                "from skill_runtime.api.models import Trajectory\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "distill" / "rules" / "common.py").write_text("", encoding="utf-8")
            (root / "skill_runtime" / "distill" / "rules" / "__init__.py").write_text(
                "from skill_runtime.distill.rules import batch_rename\nfrom skill_runtime.distill.rules.registry import get_rule_priority\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "distill" / "rules" / "batch_rename.py").write_text(
                "from skill_runtime.api.models import Trajectory\nfrom skill_runtime.api.service import RuntimeService\n",
                encoding="utf-8",
            )
            for rule_name in (
                "csv_to_json.py",
                "directory_copy.py",
                "directory_move.py",
                "directory_text_replace.py",
                "json_to_csv.py",
                "single_file_transform.py",
                "text_merge.py",
                "text_replace.py",
            ):
                (root / "skill_runtime" / "distill" / "rules" / rule_name).write_text(
                    "from skill_runtime.api.models import Trajectory\nfrom skill_runtime.distill.rules.common import escape\n",
                    encoding="utf-8",
                )
            (root / "skill_runtime" / "audit" / "semantic_checks.py").write_text(
                "from skill_runtime.api.models import Trajectory\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "audit" / "semantic_provider.py").write_text(
                "from skill_runtime.api.models import Trajectory\nfrom skill_runtime.audit.semantic_checks import SemanticIssue\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "audit" / "semantic_prompt_builder.py").write_text(
                "from skill_runtime.api.models import Trajectory\nfrom skill_runtime.audit.semantic_checks import SemanticIssue\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "audit" / "mock_semantic_provider.py").write_text(
                "from skill_runtime.audit.semantic_checks import SemanticIssue\nfrom skill_runtime.audit.semantic_provider import SemanticReviewResponse\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "audit" / "semantic_review_service.py").write_text(
                "from skill_runtime.api.models import Trajectory\nfrom skill_runtime.audit.mock_semantic_provider import MockSemanticReviewProvider\n"
                "from skill_runtime.audit.semantic_checks import SemanticIssue\nfrom skill_runtime.audit.semantic_prompt_builder import build_semantic_review_prompt\n"
                "from skill_runtime.audit.semantic_provider import SemanticReviewRequest\nfrom skill_runtime.api.service import RuntimeService\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "audit" / "static_checks.py").write_text(
                "from skill_runtime.api.service import RuntimeService\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "audit" / "skill_auditor.py").write_text(
                "from skill_runtime.api.models import AuditReport\nfrom skill_runtime.audit.semantic_checks import SemanticChecks\n"
                "from skill_runtime.audit.semantic_review_service import SemanticReviewService\nfrom skill_runtime.audit.static_checks import StaticChecks\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "execution" / "skill_loader.py").write_text("", encoding="utf-8")
            (root / "skill_runtime" / "execution" / "runtime_tools.py").write_text("", encoding="utf-8")
            (root / "skill_runtime" / "execution" / "skill_executor.py").write_text(
                "from skill_runtime.execution.skill_loader import SkillLoader\nfrom skill_runtime.retrieval.skill_index import SkillIndex\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "mcp" / "source_refs.py").write_text("__all__ = []\n", encoding="utf-8")
            (root / "skill_runtime" / "mcp" / "operation_builders.py").write_text("from skill_runtime.mcp.source_refs import *\n__all__ = []\n", encoding="utf-8")
            (root / "skill_runtime" / "mcp" / "recommendation_builders.py").write_text("from skill_runtime.mcp.operation_builders import *\nfrom skill_runtime.mcp.source_refs import *\n__all__ = []\n", encoding="utf-8")
            (root / "skill_runtime" / "mcp" / "governance_actions.py").write_text("from skill_runtime.mcp.operation_builders import *\nfrom skill_runtime.mcp.source_refs import *\n__all__ = []\n", encoding="utf-8")
            (root / "skill_runtime" / "mcp" / "host_operations.py").write_text(
                "from skill_runtime.mcp.governance_actions import *\n"
                "from skill_runtime.mcp.governance_actions import __all__ as _governance_all\n"
                "from skill_runtime.mcp.operation_builders import *\n"
                "from skill_runtime.mcp.operation_builders import __all__ as _operations_all\n"
                "from skill_runtime.mcp.recommendation_builders import *\n"
                "from skill_runtime.mcp.recommendation_builders import __all__ as _recommendations_all\n"
                "from skill_runtime.mcp.source_refs import *\n"
                "from skill_runtime.mcp.source_refs import __all__ as _source_refs_all\n"
                "__all__ = [*_operations_all, *_recommendations_all, *_governance_all, *_source_refs_all]\n",
                encoding="utf-8",
            )
            (docs_root / "mcp-integration.md").write_text(
                "# MCP Integration\n\n- `source_refs.py`\n- `operation_builders.py`\n- `recommendation_builders.py`\n- `governance_actions.py`\n- `host_operations.py`\n- `python scripts/check_mcp_architecture.py`\n",
                encoding="utf-8",
            )
            (docs_root / "codex-integration.md").write_text(
                "# Codex Integration\n\n`skill_runtime.mcp.host_operations`\n`source_refs.py`\n`operation_builders.py`\n`recommendation_builders.py`\n`governance_actions.py`\n",
                encoding="utf-8",
            )
            (workflows_root / "runtime-contracts.yml").write_text(
                "name: Runtime Contracts\non:\n  push:\n    paths:\n      - \"docs/mcp-integration.md\"\n      - \"docs/codex-integration.md\"\n"
                "jobs:\n  runtime-contracts:\n    steps:\n      - run: python scripts/check_mcp_architecture.py\n      - run: python -m unittest tests.test_runtime -v\n",
                encoding="utf-8",
            )

            violations = check_mcp_architecture(root)

        self.assertTrue(any("mock_provider.py" in violation and "api.service" in violation for violation in violations))
        self.assertTrue(any("batch_rename.py" in violation and "api.service" in violation for violation in violations))
        self.assertTrue(any("semantic_review_service.py" in violation and "api.service" in violation for violation in violations))
        self.assertTrue(any("static_checks.py" in violation and "api.service" in violation for violation in violations))

    def test_check_mcp_architecture_detects_readme_contract_drift(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            docs_root = root / "docs"
            workflows_root = root / ".github" / "workflows"
            for package in (
                root / "skill_runtime",
                root / "skill_runtime" / "api",
                root / "skill_runtime" / "governance",
                root / "skill_runtime" / "retrieval",
                root / "skill_runtime" / "mcp",
                root / "skill_runtime" / "memory",
                root / "skill_runtime" / "distill",
                root / "skill_runtime" / "distill" / "fallback",
                root / "skill_runtime" / "distill" / "rules",
                root / "skill_runtime" / "audit",
                root / "skill_runtime" / "execution",
            ):
                package.mkdir(parents=True, exist_ok=True)
                (package / "__init__.py").write_text("", encoding="utf-8")

            docs_root.mkdir(parents=True)
            workflows_root.mkdir(parents=True)
            (root / "README.md").write_text("# Skill Runtime\n", encoding="utf-8")
            (root / "README.zh-CN.md").write_text("# Skill Runtime\n", encoding="utf-8")
            (root / "skill_runtime" / "api" / "models.py").write_text("", encoding="utf-8")
            (root / "skill_runtime" / "api" / "service.py").write_text(
                "from skill_runtime.retrieval.skill_index import SkillIndex\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "governance" / "library_report.py").write_text(
                "from skill_runtime.api.models import SkillMetadata\nfrom skill_runtime.mcp.host_operations import governance_report_payload\nfrom skill_runtime.retrieval.skill_index import SkillIndex\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "governance" / "promotion_guard.py").write_text(
                "from skill_runtime.api.models import AuditReport\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "governance" / "provenance_backfill.py").write_text(
                "from skill_runtime.api.models import SkillMetadata\nfrom skill_runtime.retrieval.skill_index import SkillIndex\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "retrieval" / "skill_index.py").write_text(
                "from skill_runtime.api.models import SkillMetadata\nfrom skill_runtime.mcp.host_operations import search_result_payload\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "memory" / "trajectory_capture.py").write_text(
                "from skill_runtime.api.models import Trajectory\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "memory" / "trajectory_store.py").write_text(
                "from skill_runtime.api.models import Trajectory\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "distill" / "skill_generator.py").write_text(
                "from skill_runtime.api.models import SkillMetadata\n"
                "from skill_runtime.distill.fallback.service import FallbackService\n"
                "from skill_runtime.distill.rules import RULES\n"
                "from skill_runtime.distill.rules.common import escape\n"
                "from skill_runtime.distill.rules.registry import explain_match\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "distill" / "fallback" / "service.py").write_text(
                "from skill_runtime.api.models import Trajectory\n"
                "from skill_runtime.distill.fallback.mock_provider import MockFallbackProvider\n"
                "from skill_runtime.distill.fallback.prompt_builder import build_prompt\n"
                "from skill_runtime.distill.fallback.provider import FallbackRequest\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "distill" / "fallback" / "provider.py").write_text(
                "from skill_runtime.api.models import Trajectory\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "distill" / "fallback" / "mock_provider.py").write_text(
                "from skill_runtime.distill.fallback.provider import FallbackRequest\nfrom skill_runtime.distill.rules.common import escape\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "distill" / "fallback" / "prompt_builder.py").write_text(
                "from skill_runtime.api.models import Trajectory\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "distill" / "rules" / "registry.py").write_text(
                "from skill_runtime.api.models import Trajectory\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "distill" / "rules" / "common.py").write_text("", encoding="utf-8")
            (root / "skill_runtime" / "distill" / "rules" / "__init__.py").write_text(
                "from skill_runtime.distill.rules import batch_rename\nfrom skill_runtime.distill.rules.registry import get_rule_priority\n",
                encoding="utf-8",
            )
            for rule_name in (
                "batch_rename.py",
                "csv_to_json.py",
                "directory_copy.py",
                "directory_move.py",
                "directory_text_replace.py",
                "json_to_csv.py",
                "single_file_transform.py",
                "text_merge.py",
                "text_replace.py",
            ):
                (root / "skill_runtime" / "distill" / "rules" / rule_name).write_text(
                    "from skill_runtime.api.models import Trajectory\nfrom skill_runtime.distill.rules.common import escape\n",
                    encoding="utf-8",
                )
            (root / "skill_runtime" / "audit" / "semantic_checks.py").write_text(
                "from skill_runtime.api.models import Trajectory\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "audit" / "semantic_provider.py").write_text(
                "from skill_runtime.api.models import Trajectory\nfrom skill_runtime.audit.semantic_checks import SemanticIssue\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "audit" / "semantic_prompt_builder.py").write_text(
                "from skill_runtime.api.models import Trajectory\nfrom skill_runtime.audit.semantic_checks import SemanticIssue\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "audit" / "mock_semantic_provider.py").write_text(
                "from skill_runtime.audit.semantic_checks import SemanticIssue\nfrom skill_runtime.audit.semantic_provider import SemanticReviewResponse\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "audit" / "semantic_review_service.py").write_text(
                "from skill_runtime.api.models import Trajectory\nfrom skill_runtime.audit.mock_semantic_provider import MockSemanticReviewProvider\n"
                "from skill_runtime.audit.semantic_checks import SemanticIssue\nfrom skill_runtime.audit.semantic_prompt_builder import build_semantic_review_prompt\n"
                "from skill_runtime.audit.semantic_provider import SemanticReviewRequest\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "audit" / "static_checks.py").write_text("", encoding="utf-8")
            (root / "skill_runtime" / "audit" / "skill_auditor.py").write_text(
                "from skill_runtime.api.models import AuditReport\nfrom skill_runtime.audit.semantic_checks import SemanticChecks\n"
                "from skill_runtime.audit.semantic_review_service import SemanticReviewService\nfrom skill_runtime.audit.static_checks import StaticChecks\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "execution" / "skill_loader.py").write_text("", encoding="utf-8")
            (root / "skill_runtime" / "execution" / "runtime_tools.py").write_text("", encoding="utf-8")
            (root / "skill_runtime" / "execution" / "skill_executor.py").write_text(
                "from skill_runtime.execution.skill_loader import SkillLoader\nfrom skill_runtime.retrieval.skill_index import SkillIndex\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "mcp" / "source_refs.py").write_text("__all__ = ['VALUE']\nVALUE = 1\n", encoding="utf-8")
            (root / "skill_runtime" / "mcp" / "operation_builders.py").write_text(
                "from skill_runtime.mcp.source_refs import VALUE\n__all__ = ['VALUE']\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "mcp" / "recommendation_builders.py").write_text(
                "from skill_runtime.mcp.operation_builders import VALUE\nfrom skill_runtime.mcp.source_refs import VALUE as SOURCE\n__all__ = ['VALUE', 'SOURCE']\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "mcp" / "governance_actions.py").write_text(
                "from skill_runtime.mcp.operation_builders import VALUE\nfrom skill_runtime.mcp.source_refs import VALUE as SOURCE\n__all__ = ['VALUE', 'SOURCE']\n",
                encoding="utf-8",
            )
            (root / "skill_runtime" / "mcp" / "host_operations.py").write_text(
                "from skill_runtime.mcp.governance_actions import *\n"
                "from skill_runtime.mcp.governance_actions import __all__ as _governance_all\n"
                "from skill_runtime.mcp.operation_builders import *\n"
                "from skill_runtime.mcp.operation_builders import __all__ as _operations_all\n"
                "from skill_runtime.mcp.recommendation_builders import *\n"
                "from skill_runtime.mcp.recommendation_builders import __all__ as _recommendations_all\n"
                "from skill_runtime.mcp.source_refs import *\n"
                "from skill_runtime.mcp.source_refs import __all__ as _source_refs_all\n"
                "__all__ = [*_operations_all, *_recommendations_all, *_governance_all, *_source_refs_all]\n",
                encoding="utf-8",
            )
            (docs_root / "mcp-integration.md").write_text(
                "# MCP Integration\n\n- `source_refs.py`\n- `operation_builders.py`\n- `recommendation_builders.py`\n- `governance_actions.py`\n- `host_operations.py`\n- `python scripts/check_mcp_architecture.py`\n",
                encoding="utf-8",
            )
            (docs_root / "codex-integration.md").write_text(
                "# Codex Integration\n\n`skill_runtime.mcp.host_operations`\n`source_refs.py`\n`operation_builders.py`\n`recommendation_builders.py`\n`governance_actions.py`\n",
                encoding="utf-8",
            )
            (workflows_root / "runtime-contracts.yml").write_text(
                "name: Runtime Contracts\non:\n  push:\n    paths:\n      - \"README.md\"\n      - \"README.zh-CN.md\"\n      - \"docs/mcp-integration.md\"\n      - \"docs/codex-integration.md\"\n"
                "jobs:\n  runtime-contracts:\n    steps:\n      - run: python scripts/check_mcp_architecture.py\n      - run: python -m unittest tests.test_runtime -v\n",
                encoding="utf-8",
            )

            violations = check_mcp_architecture(root)

        self.assertTrue(any("README.md" in violation for violation in violations))
        self.assertTrue(any("README.zh-CN.md" in violation for violation in violations))
