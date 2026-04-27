from __future__ import annotations

from typing import Any

from skill_runtime.mcp.operation_builders import (
    archive_duplicate_candidates_operation,
    collect_operations,
    refresh_governance_report_operation,
)
from skill_runtime.mcp.source_refs import (
    source_ref_archive_duplicate_candidates,
    source_ref_archive_duplicate_candidates_preview,
    source_ref_governance_fixture_review,
    source_ref_governance_report_refresh,
)

__all__ = [
    "action_host_operations",
    "governance_action",
    "archive_duplicate_candidates_action",
    "review_archive_volume_action",
    "review_fixture_noise_action",
    "governance_report_payload",
]


def action_host_operations(actions: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any] | None] = []
    for action in actions or []:
        if not isinstance(action, dict):
            continue
        host_operation = action.get("host_operation")
        if not isinstance(host_operation, dict):
            continue
        candidates.append(host_operation)
        preview = host_operation.get("preview")
        if isinstance(preview, dict):
            candidates.append(preview)
    return collect_operations(candidates)


def governance_action(
    action: str,
    reason: str,
    *,
    skill_names: list[str] | None = None,
    canonical_skill: str | None = None,
    cluster_count: int = 0,
    host_operation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "action": action,
        "reason": reason,
        "skill_names": list(skill_names or []),
        "canonical_skill": canonical_skill,
        "cluster_count": cluster_count,
        "host_operation": host_operation,
    }


def archive_duplicate_candidates_action(
    skill_names: list[str],
    *,
    canonical_skill: str,
    cluster_count: int,
    rule_name: str | None = None,
) -> dict[str, Any]:
    return governance_action(
        "archive_duplicate_candidates",
        (
            f'Keep "{canonical_skill}" as canonical for '
            f'{rule_name or "unclassified"} and archive lower-priority duplicates.'
        ),
        skill_names=skill_names,
        canonical_skill=canonical_skill,
        cluster_count=cluster_count,
        host_operation=archive_duplicate_candidates_operation(
            skill_names,
            dry_run=False,
            include_preview=True,
            source_ref=source_ref_archive_duplicate_candidates(canonical_skill),
            preview_source_ref=source_ref_archive_duplicate_candidates_preview(canonical_skill),
        ),
    )


def review_archive_volume_action() -> dict[str, Any]:
    return governance_action(
        "review_archive_volume",
        "Archived skills now outnumber active skills; review whether the library is fragmenting.",
        host_operation=refresh_governance_report_operation(
            source_ref=source_ref_governance_report_refresh()
        ),
    )


def review_fixture_noise_action(
    *,
    fixture_count: int,
    hidden_fixture_only_duplicate_clusters: int,
) -> dict[str, Any]:
    reasons: list[str] = []
    if fixture_count > 0:
        reasons.append(f"{fixture_count} fixture skills are active")
    if hidden_fixture_only_duplicate_clusters > 0:
        reasons.append(
            f"{hidden_fixture_only_duplicate_clusters} fixture-only duplicate clusters are hidden"
        )
    reason = "; ".join(reasons) or "Fixture skills are increasing and should be reviewed."
    return governance_action(
        "review_fixture_noise",
        f"{reason}; review whether fixture skills should stay active or be archived.",
        cluster_count=hidden_fixture_only_duplicate_clusters,
        host_operation=refresh_governance_report_operation(
            source_ref=source_ref_governance_fixture_review()
        ),
    )


def governance_report_payload(
    status_counts: dict[str, int],
    duplicate_candidates: list[dict[str, Any]],
    recommended_actions: list[dict[str, Any]],
    *,
    staging_count: int,
    archive_count: int,
    active_count: int,
    library_tier_counts: dict[str, int],
    library_tier_summary: dict[str, Any],
) -> dict[str, Any]:
    return {
        "status_counts": status_counts,
        "duplicate_candidates": duplicate_candidates,
        "recommended_actions": recommended_actions,
        "available_host_operations": action_host_operations(recommended_actions),
        "staging_count": staging_count,
        "archive_count": archive_count,
        "active_count": active_count,
        "library_tier_counts": library_tier_counts,
        "library_tier_summary": library_tier_summary,
    }
