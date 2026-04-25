from pathlib import Path

from skill_runtime.api.models import AuditReport, Trajectory
from skill_runtime.audit.semantic_checks import SemanticChecks, SemanticIssue
from skill_runtime.audit.semantic_review_service import SemanticReviewService
from skill_runtime.audit.static_checks import StaticChecks, StaticIssue


class SkillAuditor:
    def __init__(self, audits_dir: str | Path = "audits") -> None:
        self.static_checks = StaticChecks()
        self.semantic_checks = SemanticChecks()
        self.semantic_review = SemanticReviewService(audits_dir)

    def audit(self, file_path: str | Path, trajectory: Trajectory | None = None) -> AuditReport:
        source = Path(file_path).read_text(encoding="utf-8")
        static_issues = self.static_checks.run(file_path)
        heuristic_semantic_issues = self.semantic_checks.run(file_path, trajectory=trajectory)
        provider_issues, provider_summary, artifact_path = self.semantic_review.review(
            file_path,
            source,
            heuristic_semantic_issues,
            trajectory=trajectory,
        )
        semantic_issues = [*heuristic_semantic_issues, *provider_issues]
        static_score = self._score_static(static_issues)
        semantic_score = self._score_semantic(semantic_issues)
        return AuditReport(
            status="passed" if self._is_pass(static_issues, semantic_issues) else "needs_fix",
            security_score=min(static_score, semantic_score),
            suggestions=self._suggestions(static_issues, semantic_issues),
            optimized_docstring=self._optimized_docstring(file_path),
            refactored_code="",
            static_score=static_score,
            semantic_score=semantic_score,
            static_findings=[issue.message for issue in static_issues],
            semantic_findings=[issue.message for issue in semantic_issues],
            semantic_summary=self._semantic_summary(semantic_issues, provider_summary),
            semantic_provider=self.semantic_review.provider.provider_name,
            semantic_artifact=artifact_path,
        )

    def _score_static(self, issues: list[StaticIssue]) -> int:
        score = 100
        for issue in issues:
            if issue.severity == "high":
                score -= 25
            elif issue.severity == "medium":
                score -= 10
            else:
                score -= 5
        return max(score, 0)

    def _score_semantic(self, issues: list[SemanticIssue]) -> int:
        score = 100
        for issue in issues:
            if issue.severity == "high":
                score -= 25
            elif issue.severity == "medium":
                score -= 10
            else:
                score -= 5
        return max(score, 0)

    def _is_pass(self, static_issues: list[StaticIssue], semantic_issues: list[SemanticIssue]) -> bool:
        return not any(issue.severity == "high" for issue in [*static_issues, *semantic_issues])

    def _suggestions(self, static_issues: list[StaticIssue], semantic_issues: list[SemanticIssue]) -> list[str]:
        if not static_issues and not semantic_issues:
            return ["No blocking issues found."]

        static_mapping = {
            "dangerous-command": "Remove or strictly constrain dangerous system commands.",
            "hardcoded-path": "Convert absolute paths into function parameters such as input_path or output_path.",
            "hardcoded-user": "Remove user-specific values and replace them with explicit parameters.",
            "missing-docstring": "Add a precise docstring covering function description, input parameters, and output result.",
            "missing-run": "Expose a single run(tools, **kwargs) entry point.",
            "overgrown-skill": "Split the skill into smaller single-purpose skills or helper functions.",
            "shell-true": "Avoid shell=True and prefer safe subprocess argument lists or runtime tool wrappers.",
            "shell-invocation": "Replace direct shell invocation with restricted runtime tools.",
            "syntax-error": "Fix syntax errors before the skill can be promoted.",
        }
        semantic_mapping = {
            "docstring-structure": "Restructure the docstring so it clearly states function, inputs, and outputs for retrieval and review.",
            "semantic-atomicity": "Split the workflow into smaller single-purpose skills or helpers with clearer boundaries.",
            "trajectory-alignment": "Revise the implementation so the runtime tool usage matches the successful trajectory.",
            "template-skill": "Replace template-style placeholder logic with real runtime operations before promotion.",
            "parameter-coverage": "Expose more trajectory-derived inputs as explicit kwargs so the skill generalizes correctly.",
            "artifact-overfit": "Remove hardcoded artifact names and parameterize the output path or target resource.",
        }

        suggestions: list[str] = []
        seen: set[str] = set()
        for issue in static_issues:
            suggestion = static_mapping.get(issue.rule_id)
            if suggestion and suggestion not in seen:
                suggestions.append(suggestion)
                seen.add(suggestion)
        for issue in semantic_issues:
            suggestion = semantic_mapping.get(issue.rule_id)
            if suggestion and suggestion not in seen:
                suggestions.append(suggestion)
                seen.add(suggestion)
        return suggestions

    def _optimized_docstring(self, file_path: str | Path) -> str:
        skill_name = Path(file_path).stem
        return (
            f"功能描述:\n"
            f'    Execute the "{skill_name}" skill as a reusable, parameterized workflow.\n\n'
            f"输入参数:\n"
            f"    - tools: Runtime tool adapter provided by the host agent.\n"
            f"    - **kwargs: Named input parameters required by the skill, such as input_path, output_path, url, or query.\n\n"
            f"输出结果:\n"
            f"    - Return a dict describing execution status, produced artifacts, and any structured result fields.\n"
        )

    def _semantic_summary(self, issues: list[SemanticIssue], provider_summary: str | None = None) -> str:
        if not issues:
            summary = "Semantic review found no blocking alignment or generalization issues."
            return f"{summary} {provider_summary}".strip() if provider_summary else summary
        highest = "high" if any(issue.severity == "high" for issue in issues) else "medium"
        summary = f"Semantic review found {len(issues)} issue(s); highest severity: {highest}."
        return f"{summary} {provider_summary}".strip() if provider_summary else summary
