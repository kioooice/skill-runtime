from skill_runtime.audit.semantic_checks import SemanticIssue
from skill_runtime.audit.semantic_provider import SemanticReviewRequest, SemanticReviewResponse


class MockSemanticReviewProvider:
    provider_name = "mock_semantic_review_provider"

    def review(self, request: SemanticReviewRequest) -> SemanticReviewResponse:
        issues: list[SemanticIssue] = []
        source = request.source

        if 'generated_by": "mock_fallback_provider"' in source or "generated_by\": \"mock_fallback_provider\"" in source:
            issues.append(
                SemanticIssue(
                    rule_id="provider-template-skill",
                    severity="medium",
                    message=(
                        "Provider review flagged the skill as fallback-generated template logic that may still "
                        "need stronger concrete runtime behavior before promotion."
                    ),
                )
            )

        if "steps_executed" in source and "tools." not in source:
            issues.append(
                SemanticIssue(
                    rule_id="provider-weak-runtime-alignment",
                    severity="medium",
                    message=(
                        "Provider review found summary-style output without clear runtime tool execution, "
                        "which can indicate a partially abstract or template skill."
                    ),
                )
            )

        summary = (
            "Provider-backed semantic review found no additional issues."
            if not issues
            else f"Provider-backed semantic review found {len(issues)} additional issue(s)."
        )
        return SemanticReviewResponse(
            provider_name=self.provider_name,
            summary=summary,
            issues=issues,
        )
