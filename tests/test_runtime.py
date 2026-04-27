import unittest

from tests.test_runtime_audit_lifecycle import RuntimeAuditLifecycleTestsMixin
from tests.test_runtime_directory_generated_skills import RuntimeDirectoryGeneratedSkillTestsMixin
from tests.test_runtime_file_generated_skills import RuntimeFileGeneratedSkillTestsMixin
from tests.test_runtime_generated_skill_regressions import RuntimeGeneratedSkillRegressionTestsMixin
from tests.runtime_test_support import RuntimeTestCase
from tests.test_runtime_architecture import RuntimeArchitectureTestsMixin
from tests.test_runtime_contracts import RuntimeContractTestsMixin
from tests.test_runtime_distill_coverage import RuntimeDistillCoverageTestsMixin
from tests.test_runtime_execution_flow import RuntimeExecutionFlowTestsMixin
from tests.test_runtime_governance import RuntimeGovernanceTestsMixin
from tests.test_runtime_host_operations import RuntimeHostOperationTestsMixin
from tests.test_runtime_lifecycle import RuntimeLifecycleTestsMixin
from tests.test_runtime_trajectory_search import RuntimeTrajectorySearchTestsMixin


class RuntimeTests(
    RuntimeArchitectureTestsMixin,
    RuntimeContractTestsMixin,
    RuntimeDistillCoverageTestsMixin,
    RuntimeTrajectorySearchTestsMixin,
    RuntimeLifecycleTestsMixin,
    RuntimeExecutionFlowTestsMixin,
    RuntimeAuditLifecycleTestsMixin,
    RuntimeHostOperationTestsMixin,
    RuntimeFileGeneratedSkillTestsMixin,
    RuntimeDirectoryGeneratedSkillTestsMixin,
    RuntimeGeneratedSkillRegressionTestsMixin,
    RuntimeGovernanceTestsMixin,
    RuntimeTestCase,
):
    pass


if __name__ == "__main__":
    unittest.main()
