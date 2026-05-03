import unittest

from tests.test_runtime_audit_lifecycle import RuntimeAuditLifecycleTestsMixin
from tests.test_runtime_directory_generated_skills import RuntimeDirectoryGeneratedSkillTestsMixin
from tests.test_runtime_file_generated_skills import RuntimeFileGeneratedSkillTestsMixin
from tests.test_runtime_generated_skill_regressions import RuntimeGeneratedSkillRegressionTestsMixin
from tests.runtime_test_support import RuntimeTestCase
from tests.test_runtime_architecture import RuntimeArchitectureTestsMixin
from tests.test_runtime_agent_orchestration import RuntimeAgentOrchestrationTestsMixin
from tests.test_runtime_collections import RuntimeCollectionsTestsMixin
from tests.test_runtime_contracts import RuntimeContractTestsMixin
from tests.test_runtime_core_dogfood_acceptance import RuntimeCoreDogfoodAcceptanceTestsMixin
from tests.test_runtime_dashboard import RuntimeDashboardTestsMixin
from tests.test_runtime_deepseek_provider_examples import RuntimeDeepSeekProviderExampleTestsMixin
from tests.test_runtime_distill_coverage import RuntimeDistillCoverageTestsMixin
from tests.test_runtime_execution_flow import RuntimeExecutionFlowTestsMixin
from tests.test_runtime_governance import RuntimeGovernanceTestsMixin
from tests.test_runtime_host_operations import RuntimeHostOperationTestsMixin
from tests.test_runtime_isolation import RuntimeIsolationTestsMixin
from tests.test_runtime_lifecycle import RuntimeLifecycleTestsMixin
from tests.test_runtime_mcp_smoke import RuntimeMcpSmokeTestsMixin
from tests.test_runtime_platform_inventory import RuntimePlatformInventoryTestsMixin
from tests.test_runtime_platform_export import RuntimePlatformExportTestsMixin
from tests.test_runtime_search_quality import RuntimeSearchQualityTestsMixin
from tests.test_runtime_skill_import import RuntimeSkillImportTestsMixin
from tests.test_runtime_trajectory_search import RuntimeTrajectorySearchTestsMixin


class RuntimeTests(
    RuntimeArchitectureTestsMixin,
    RuntimeAgentOrchestrationTestsMixin,
    RuntimeCollectionsTestsMixin,
    RuntimeContractTestsMixin,
    RuntimeCoreDogfoodAcceptanceTestsMixin,
    RuntimeDashboardTestsMixin,
    RuntimeDeepSeekProviderExampleTestsMixin,
    RuntimeDistillCoverageTestsMixin,
    RuntimeTrajectorySearchTestsMixin,
    RuntimeLifecycleTestsMixin,
    RuntimeExecutionFlowTestsMixin,
    RuntimeAuditLifecycleTestsMixin,
    RuntimeHostOperationTestsMixin,
    RuntimeIsolationTestsMixin,
    RuntimeMcpSmokeTestsMixin,
    RuntimePlatformExportTestsMixin,
    RuntimePlatformInventoryTestsMixin,
    RuntimeSearchQualityTestsMixin,
    RuntimeSkillImportTestsMixin,
    RuntimeFileGeneratedSkillTestsMixin,
    RuntimeDirectoryGeneratedSkillTestsMixin,
    RuntimeGeneratedSkillRegressionTestsMixin,
    RuntimeGovernanceTestsMixin,
    RuntimeTestCase,
):
    pass


if __name__ == "__main__":
    unittest.main()
