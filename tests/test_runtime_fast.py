import unittest

from tests.runtime_test_support import RuntimeTestCase
from tests.test_runtime_agent_orchestration import RuntimeAgentOrchestrationTestsMixin
from tests.test_runtime_collections import RuntimeCollectionsTestsMixin
from tests.test_runtime_core_dogfood_acceptance import RuntimeCoreDogfoodAcceptanceTestsMixin
from tests.test_runtime_dashboard import RuntimeDashboardTestsMixin
from tests.test_runtime_deepseek_provider_examples import RuntimeDeepSeekProviderExampleTestsMixin
from tests.test_runtime_governance import RuntimeGovernanceFastTestsMixin
from tests.test_runtime_isolation import RuntimeIsolationTestsMixin
from tests.test_runtime_mcp_smoke import RuntimeMcpSmokeTestsMixin
from tests.test_runtime_platform_inventory import RuntimePlatformInventoryTestsMixin
from tests.test_runtime_platform_export import RuntimePlatformExportTestsMixin
from tests.test_runtime_provider_quality_eval import RuntimeProviderQualityEvalTestsMixin
from tests.test_runtime_recommendation_presentation import RuntimeRecommendationPresentationTestsMixin
from tests.test_runtime_search_quality import RuntimeSearchQualityTestsMixin
from tests.test_runtime_skill_import import RuntimeSkillImportTestsMixin
from tests.test_runtime_workflow_search_quality import RuntimeWorkflowSearchQualityTestsMixin


class RuntimeFastTests(
    RuntimeAgentOrchestrationTestsMixin,
    RuntimeCollectionsTestsMixin,
    RuntimeCoreDogfoodAcceptanceTestsMixin,
    RuntimeDashboardTestsMixin,
    RuntimeDeepSeekProviderExampleTestsMixin,
    RuntimeGovernanceFastTestsMixin,
    RuntimeIsolationTestsMixin,
    RuntimeMcpSmokeTestsMixin,
    RuntimePlatformExportTestsMixin,
    RuntimePlatformInventoryTestsMixin,
    RuntimeProviderQualityEvalTestsMixin,
    RuntimeRecommendationPresentationTestsMixin,
    RuntimeSearchQualityTestsMixin,
    RuntimeSkillImportTestsMixin,
    RuntimeWorkflowSearchQualityTestsMixin,
    RuntimeTestCase,
):
    pass


if __name__ == "__main__":
    unittest.main()
