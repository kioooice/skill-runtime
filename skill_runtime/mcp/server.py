from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from skill_runtime.api.service import RuntimeService, RuntimeServiceError


def _wrap_tool(service: RuntimeService, handler_name: str, **kwargs: Any) -> dict[str, Any]:
    try:
        data = getattr(service, handler_name)(**kwargs)
    except RuntimeServiceError as exc:
        return {
            "status": "error",
            "message": exc.message,
            "code": exc.code,
            "details": exc.details,
        }
    return {"status": "ok", "data": data}


def build_mcp_server(root: str | Path) -> FastMCP:
    service = RuntimeService(root)
    server = FastMCP(
        name="skill-runtime",
        instructions=(
            "Codex-compatible self-evolving skill runtime. "
            "Use these tools to search, distill, audit, promote, execute, and govern local skills."
        ),
    )

    @server.tool(
        name="search_skill",
        description="Search the local active skill index for reusable skills relevant to a task.",
        structured_output=True,
    )
    def search_skill(query: str, top_k: int = 5) -> dict[str, Any]:
        return _wrap_tool(service, "search", query=query, top_k=top_k)

    @server.tool(
        name="execute_skill",
        description="Execute an active skill by name with structured keyword arguments.",
        structured_output=True,
    )
    def execute_skill(skill_name: str, args: dict[str, Any]) -> dict[str, Any]:
        return _wrap_tool(service, "execute", skill_name=skill_name, args=args)

    @server.tool(
        name="distill_trajectory",
        description="Distill a successful trajectory JSON file into a staging skill and metadata draft.",
        structured_output=True,
    )
    def distill_trajectory(trajectory_path: str, skill_name: str | None = None) -> dict[str, Any]:
        return _wrap_tool(service, "distill", trajectory_path=trajectory_path, skill_name=skill_name)

    @server.tool(
        name="distill_and_promote_candidate",
        description=(
            "Run the full reusable-skill pipeline for a trajectory: "
            "register it, distill it, audit it, and promote it if the audit passes."
        ),
        structured_output=True,
    )
    def distill_and_promote_candidate(
        trajectory_path: str,
        skill_name: str | None = None,
        register_trajectory: bool = True,
    ) -> dict[str, Any]:
        return _wrap_tool(
            service,
            "distill_and_promote",
            trajectory_path=trajectory_path,
            skill_name=skill_name,
            register_trajectory=register_trajectory,
        )

    @server.tool(
        name="audit_skill",
        description="Audit a staging skill for safety, generalization, atomicity, and retrievability.",
        structured_output=True,
    )
    def audit_skill(file_path: str, trajectory_path: str | None = None) -> dict[str, Any]:
        return _wrap_tool(service, "audit", file_path=file_path, trajectory_path=trajectory_path)

    @server.tool(
        name="promote_skill",
        description="Promote a staging skill into the active library after a passing audit report exists.",
        structured_output=True,
    )
    def promote_skill(file_path: str) -> dict[str, Any]:
        return _wrap_tool(service, "promote", file_path=file_path)

    @server.tool(
        name="log_trajectory",
        description="Validate and register a trajectory JSON file into the local trajectory store.",
        structured_output=True,
    )
    def log_trajectory(file_path: str) -> dict[str, Any]:
        return _wrap_tool(service, "log_trajectory", file_path=file_path)

    @server.tool(
        name="reindex_skills",
        description="Rebuild the active skill index from metadata files in the active skill store.",
        structured_output=True,
    )
    def reindex_skills() -> dict[str, Any]:
        return _wrap_tool(service, "reindex")

    @server.tool(
        name="backfill_skill_provenance",
        description="Backfill missing rule provenance for legacy active skills and update the index.",
        structured_output=True,
    )
    def backfill_skill_provenance() -> dict[str, Any]:
        return _wrap_tool(service, "backfill_provenance")

    return server
