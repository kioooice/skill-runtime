from __future__ import annotations


FIXTURE_PATTERNS = (
    "test",
    "demo",
    "readme",
    "bridge",
    "provenance",
    "cli_",
    "mcp_",
    "service_",
    "codex_",
)

EXPERIMENTAL_PATTERNS = (
    "generated",
)


def classify_skill_name(skill_name: str) -> str:
    lowered = skill_name.lower()
    if any(pattern in lowered for pattern in FIXTURE_PATTERNS):
        return "fixture"
    if any(pattern in lowered for pattern in EXPERIMENTAL_PATTERNS):
        return "experimental"
    return "stable"
