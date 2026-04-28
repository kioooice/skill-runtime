from skill_runtime.mcp import build_mcp_server
from tests.runtime_test_support import ROOT


class RuntimeMcpSmokeTestsMixin:
    def test_build_mcp_server_smoke_constructs_server(self) -> None:
        server = build_mcp_server(ROOT)

        self.assertIsNotNone(server)
        self.assertTrue(callable(getattr(server, "call_tool", None)))
