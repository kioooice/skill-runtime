from __future__ import annotations

__all__ = [
    "source_ref_skill",
    "source_ref_search_recommended_skill",
    "source_ref_search_no_match",
    "source_ref_search_no_match_inline_capture",
    "source_ref_search_no_match_distill",
    "source_ref_search_no_match_inline_distill",
    "source_ref_observed_task",
    "source_ref_observed_task_rollback",
    "source_ref_distill",
    "source_ref_audit",
    "source_ref_promote",
    "source_ref_trajectory",
    "source_ref_log_trajectory",
    "source_ref_archive_duplicate_candidates",
    "source_ref_archive_duplicate_candidates_preview",
    "source_ref_archive_duplicate_candidates_follow_up",
    "source_ref_archive_duplicate_candidates_apply_follow_up",
    "source_ref_governance_report_refresh",
    "source_ref_governance_fixture_review",
    "source_ref_distill_coverage_report_refresh",
    "source_ref_distill_coverage_report_view",
]


def source_ref_skill(skill_name: str) -> str:
    return f"skill:{skill_name}"


def source_ref_search_recommended_skill(skill_name: str) -> str:
    return f"search:recommended_skill:{skill_name}"


def source_ref_search_no_match() -> str:
    return "search:no_strong_match"


def source_ref_search_no_match_inline_capture() -> str:
    return "search:no_strong_match:inline_capture"


def source_ref_search_no_match_distill() -> str:
    return "search:no_strong_match:distill"


def source_ref_search_no_match_inline_distill() -> str:
    return "search:no_strong_match:inline_distill"


def source_ref_observed_task(observed_task_path: str) -> str:
    return f"observed_task:{observed_task_path}"


def source_ref_observed_task_rollback(observed_task_path: str) -> str:
    return f"{source_ref_observed_task(observed_task_path)}:rollback"


def source_ref_distill(skill_name: str) -> str:
    return f"distill:{skill_name}"


def source_ref_audit(skill_name: str) -> str:
    return f"audit:{skill_name}"


def source_ref_promote(skill_name: str) -> str:
    return f"promote:{skill_name}"


def source_ref_trajectory(task_id: str) -> str:
    return f"trajectory:{task_id}"


def source_ref_log_trajectory(task_id: str) -> str:
    return f"log_trajectory:{task_id}"


def source_ref_archive_duplicate_candidates(canonical_skill: str) -> str:
    return f"governance:archive_duplicate_candidates:{canonical_skill}"


def source_ref_archive_duplicate_candidates_preview(canonical_skill: str) -> str:
    return f"{source_ref_archive_duplicate_candidates(canonical_skill)}:preview"


def source_ref_archive_duplicate_candidates_follow_up() -> str:
    return "archive_duplicate_candidates:follow_up"


def source_ref_archive_duplicate_candidates_apply_follow_up() -> str:
    return "archive_duplicate_candidates:apply_follow_up"


def source_ref_governance_report_refresh() -> str:
    return "governance:report_refresh"


def source_ref_governance_fixture_review() -> str:
    return "governance:fixture_review"


def source_ref_distill_coverage_report_refresh() -> str:
    return "distill_coverage:report_refresh"


def source_ref_distill_coverage_report_view(view_name: str) -> str:
    return f"distill_coverage:view:{view_name}"
