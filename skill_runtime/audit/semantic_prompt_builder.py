from pathlib import Path

from skill_runtime.api.models import Trajectory
from skill_runtime.audit.semantic_checks import SemanticIssue


def build_semantic_review_prompt(
    file_path: str | Path,
    source: str,
    trajectory: Trajectory | None,
    heuristic_issues: list[SemanticIssue],
) -> str:
    trajectory_block = "No trajectory provided."
    if trajectory is not None:
        steps = "\n".join(
            f"- {step.tool_name} input={step.tool_input} observation={step.observation}"
            for step in trajectory.steps
        )
        trajectory_block = (
            f"Task: {trajectory.task_description}\n"
            f"Final status: {trajectory.final_status}\n"
            f"Artifacts: {trajectory.artifacts}\n"
            f"Steps:\n{steps}"
        )

    heuristic_block = (
        "\n".join(f"- [{issue.severity}] {issue.rule_id}: {issue.message}" for issue in heuristic_issues)
        if heuristic_issues
        else "- No heuristic semantic issues found."
    )

    return (
        f"Review the candidate skill at {Path(file_path).name}.\n\n"
        f"Trajectory context:\n{trajectory_block}\n\n"
        f"Heuristic semantic findings:\n{heuristic_block}\n\n"
        "Focus on:\n"
        "- trajectory alignment\n"
        "- overfitting or template behavior\n"
        "- parameter coverage\n"
        "- atomicity and retrievability\n\n"
        f"Skill source:\n{source}"
    )
