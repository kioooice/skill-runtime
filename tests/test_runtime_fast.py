import unittest

from tests.runtime_test_support import RuntimeTestCase
from tests.test_runtime_core_dogfood_acceptance import RuntimeCoreDogfoodAcceptanceTestsMixin
from tests.test_runtime_deepseek_provider_examples import RuntimeDeepSeekProviderExampleTestsMixin
from tests.test_runtime_isolation import RuntimeIsolationTestsMixin
from tests.test_runtime_mcp_smoke import RuntimeMcpSmokeTestsMixin
from tests.test_runtime_search_quality import RuntimeSearchQualityTestsMixin


class RuntimeFastTests(
    RuntimeCoreDogfoodAcceptanceTestsMixin,
    RuntimeDeepSeekProviderExampleTestsMixin,
    RuntimeIsolationTestsMixin,
    RuntimeMcpSmokeTestsMixin,
    RuntimeSearchQualityTestsMixin,
    RuntimeTestCase,
):
    pass


if __name__ == "__main__":
    unittest.main()
