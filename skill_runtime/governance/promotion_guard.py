import json
from pathlib import Path

from skill_runtime.api.models import AuditReport


class PromotionGuardError(ValueError):
    pass


class PromotionGuard:
    def __init__(self, audits_dir: str | Path) -> None:
        self.audits_dir = Path(audits_dir)

    def latest_report_path(self, skill_name: str) -> Path:
        report_path = self.audits_dir / f"{skill_name}.audit.json"
        if not report_path.exists():
            raise FileNotFoundError(f"audit report not found for skill: {skill_name}")
        return report_path

    def load_report(self, skill_name: str) -> AuditReport:
        report_path = self.latest_report_path(skill_name)
        payload = json.loads(report_path.read_text(encoding="utf-8"))
        required_fields = {
            "status",
            "security_score",
            "suggestions",
            "optimized_docstring",
            "refactored_code",
        }
        missing = sorted(required_fields - set(payload.keys()))
        if missing:
            raise PromotionGuardError(f"audit report missing fields: {missing}")
        return AuditReport(
            status=payload["status"],
            security_score=payload["security_score"],
            suggestions=payload["suggestions"],
            optimized_docstring=payload["optimized_docstring"],
            refactored_code=payload["refactored_code"],
            static_score=payload.get("static_score"),
            semantic_score=payload.get("semantic_score"),
            static_findings=payload.get("static_findings", []),
            semantic_findings=payload.get("semantic_findings", []),
            semantic_summary=payload.get("semantic_summary"),
        )

    def assert_promotable(self, skill_name: str) -> AuditReport:
        report = self.load_report(skill_name)
        if report.status != "passed":
            raise PromotionGuardError(f"latest audit did not pass for skill: {skill_name}")
        return report
