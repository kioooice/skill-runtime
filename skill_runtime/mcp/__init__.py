__all__ = ["build_mcp_server"]


def build_mcp_server(*args, **kwargs):
    from skill_runtime.mcp.server import build_mcp_server as _build_mcp_server

    return _build_mcp_server(*args, **kwargs)
