import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from skill_runtime.api.models import SkillMetadata
from skill_runtime.audit.skill_auditor import SkillAuditor
from skill_runtime.distill.skill_generator import SkillGenerationError, SkillGenerator
from skill_runtime.execution.runtime_tools import RuntimeTools
from skill_runtime.execution.skill_executor import SkillExecutionError, SkillExecutor
from skill_runtime.governance.promotion_guard import PromotionGuard, PromotionGuardError
from skill_runtime.governance.provenance_backfill import ProvenanceBackfill
from skill_runtime.memory.trajectory_store import TrajectoryStore, TrajectoryValidationError
from skill_runtime.retrieval.skill_index import SkillIndex, SkillIndexError


class RuntimeServiceError(ValueError):
    def __init__(self, message: str, code: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


class RuntimeService:
    RECOMMENDED_EXECUTION_SCORE = 0.75

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()
        self.index_path = self.root / "skill_store" / "index.json"
        self.active_dir = self.root / "skill_store" / "active"
        self.staging_dir = self.root / "skill_store" / "staging"
        self.trajectories_dir = self.root / "trajectories"
        self.audits_dir = self.root / "audits"

    def search(self, query: str, top_k: int = 5) -> dict[str, Any]:
        if not query.strip():
            raise RuntimeServiceError("query cannot be empty", "INVALID_QUERY")

        try:
            results = SkillIndex(self.index_path).search(query, top_k=top_k)
        except SkillIndexError as exc:
            raise RuntimeServiceError("search failed", "SEARCH_FAILED", {"reason": str(exc)}) from exc

        if results and results[0]["score"] >= self.RECOMMENDED_EXECUTION_SCORE:
            return {
                "query": query,
                "results": results,
                "recommended_next_action": "execute_skill",
                "recommended_skill_name": results[0]["skill_name"],
            }

        return {
            "query": query,
            "results": results,
            "recommended_next_action": "distill_and_promote_candidate",
            "recommended_skill_name": None,
        }

    def execute(self, skill_name: str, args: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(args, dict):
            raise RuntimeServiceError(
                "--args must decode to a JSON object",
                "INVALID_ARGS_OBJECT",
                {"received_type": type(args).__name__},
            )

        try:
            result = SkillExecutor(
                index=SkillIndex(self.index_path),
                tools=RuntimeTools(self.root),
            ).execute(skill_name, args)
        except FileNotFoundError as exc:
            raise RuntimeServiceError("skill not found", "SKILL_NOT_FOUND", {"skill_name": skill_name}) from exc
        except SkillExecutionError as exc:
            raise RuntimeServiceError(
                "skill execution failed",
                "SKILL_EXECUTION_FAILED",
                {"reason": str(exc)},
            ) from exc

        return {"skill_name": skill_name, "result": result}

    def distill(self, trajectory_path: str | Path, skill_name: str | None = None) -> dict[str, Any]:
        try:
            trajectory = TrajectoryStore(self.trajectories_dir).load_file(trajectory_path)
        except FileNotFoundError as exc:
            raise RuntimeServiceError(
                "trajectory file not found",
                "TRAJECTORY_NOT_FOUND",
                {"path": str(trajectory_path)},
            ) from exc
        except TrajectoryValidationError as exc:
            raise RuntimeServiceError(
                "trajectory is invalid",
                "INVALID_TRAJECTORY",
                {"reason": str(exc)},
            ) from exc

        try:
            generated = SkillGenerator(self.staging_dir).generate(trajectory, skill_name=skill_name)
        except SkillGenerationError as exc:
            raise RuntimeServiceError(
                "skill generation failed",
                "SKILL_GENERATION_FAILED",
                {"reason": str(exc)},
            ) from exc

        payload = {
            "trajectory_path": str(Path(trajectory_path).resolve()),
            "skill_name": generated["skill_name"],
            "staging_file": str(generated["skill_file"].resolve()),
            "metadata_file": str(generated["metadata_file"].resolve()),
            "summary": generated["summary"],
        }
        if generated.get("fallback_artifact"):
            payload["fallback_artifact"] = str(Path(generated["fallback_artifact"]).resolve())
        return payload

    def audit(self, file_path: str | Path, trajectory_path: str | Path | None = None) -> dict[str, Any]:
        file_ref = Path(file_path)
        if not file_ref.exists():
            raise RuntimeServiceError(
                "skill file not found",
                "SKILL_FILE_NOT_FOUND",
                {"path": str(file_ref)},
            )

        if trajectory_path and not Path(trajectory_path).exists():
            raise RuntimeServiceError(
                "trajectory file not found",
                "TRAJECTORY_NOT_FOUND",
                {"path": str(trajectory_path)},
            )

        trajectory = None
        if trajectory_path:
            try:
                trajectory = TrajectoryStore(self.trajectories_dir).load_file(trajectory_path)
            except TrajectoryValidationError as exc:
                raise RuntimeServiceError(
                    "trajectory is invalid",
                    "INVALID_TRAJECTORY",
                    {"reason": str(exc)},
                ) from exc

        report = SkillAuditor().audit(file_ref, trajectory=trajectory)
        self.audits_dir.mkdir(parents=True, exist_ok=True)
        report_file = self.audits_dir / f"{file_ref.stem}.audit.json"
        report_file.write_text(json.dumps(asdict(report), ensure_ascii=False, indent=2), encoding="utf-8")
        return {"report": asdict(report), "report_file": str(report_file.resolve())}

    def promote(self, file_path: str | Path) -> dict[str, Any]:
        file_ref = Path(file_path)
        if not file_ref.exists():
            raise RuntimeServiceError(
                "staging skill file not found",
                "SKILL_FILE_NOT_FOUND",
                {"path": str(file_ref)},
            )

        if "staging" not in {part.lower() for part in file_ref.parts}:
            raise RuntimeServiceError(
                "only staging skills can be promoted",
                "INVALID_PROMOTION_SOURCE",
                {"path": str(file_ref)},
            )

        skill_name = file_ref.stem
        try:
            report = PromotionGuard(self.audits_dir).assert_promotable(skill_name)
        except FileNotFoundError as exc:
            raise RuntimeServiceError("audit report not found", "AUDIT_NOT_FOUND", {"skill_name": skill_name}) from exc
        except PromotionGuardError as exc:
            raise RuntimeServiceError(
                "latest audit did not pass",
                "AUDIT_NOT_PASSED",
                {"skill_name": skill_name, "reason": str(exc)},
            ) from exc

        self.active_dir.mkdir(parents=True, exist_ok=True)
        active_file = self.active_dir / file_ref.name
        active_file.write_text(file_ref.read_text(encoding="utf-8"), encoding="utf-8")

        staging_metadata = file_ref.with_name(f"{skill_name}.metadata.json")
        if staging_metadata.exists():
            payload = json.loads(staging_metadata.read_text(encoding="utf-8"))
            metadata = SkillMetadata(
                skill_name=payload["skill_name"],
                file_path=str(active_file.resolve()),
                summary=payload["summary"],
                docstring=report.optimized_docstring,
                input_schema=payload["input_schema"],
                output_schema=payload["output_schema"],
                source_trajectory_ids=payload["source_trajectory_ids"],
                created_at=payload["created_at"],
                last_used_at=payload["last_used_at"],
                usage_count=payload["usage_count"],
                status="active",
                audit_score=report.security_score,
                rule_name=payload.get("rule_name"),
                rule_priority=payload.get("rule_priority"),
                rule_reason=payload.get("rule_reason"),
                tags=payload.get("tags", []),
            )
        else:
            metadata = SkillMetadata(
                skill_name=skill_name,
                file_path=str(active_file.resolve()),
                summary=f"Promoted skill {skill_name}",
                docstring=report.optimized_docstring,
                input_schema={},
                output_schema={},
                source_trajectory_ids=[],
                created_at=datetime.now(timezone.utc).isoformat(),
                last_used_at=None,
                usage_count=0,
                status="active",
                audit_score=report.security_score,
                rule_name=None,
                rule_priority=None,
                rule_reason=None,
                tags=[],
            )

        metadata_path = self.active_dir / f"{skill_name}.metadata.json"
        metadata_path.write_text(json.dumps(asdict(metadata), ensure_ascii=False, indent=2), encoding="utf-8")
        SkillIndex(self.index_path).upsert(metadata)

        return {
            "skill_name": skill_name,
            "active_file": str(active_file.resolve()),
            "metadata_file": str(metadata_path.resolve()),
            "audit_score": report.security_score,
            "index_updated": True,
        }

    def log_trajectory(self, file_path: str | Path) -> dict[str, Any]:
        try:
            trajectory, saved_path = TrajectoryStore(self.trajectories_dir).register_file(file_path)
        except FileNotFoundError as exc:
            raise RuntimeServiceError(
                "trajectory file not found",
                "TRAJECTORY_NOT_FOUND",
                {"path": str(file_path)},
            ) from exc
        except TrajectoryValidationError as exc:
            raise RuntimeServiceError(
                "trajectory is invalid",
                "INVALID_TRAJECTORY",
                {"reason": str(exc)},
            ) from exc

        return {"trajectory_path": str(saved_path.resolve()), "task_id": trajectory.task_id, "registered": True}

    def reindex(self) -> dict[str, Any]:
        try:
            index = SkillIndex(self.index_path)
            index_path = index.rebuild_from_directory(self.active_dir)
            skill_count = len(index.load_all())
        except FileNotFoundError as exc:
            raise RuntimeServiceError(
                "active skill directory not found",
                "ACTIVE_DIR_NOT_FOUND",
                {"path": str(self.active_dir)},
            ) from exc

        return {"index_path": str(index_path.resolve()), "skill_count": skill_count}

    def archive_cold(self, days: int) -> dict[str, Any]:
        if days < 1:
            raise RuntimeServiceError("days must be >= 1", "INVALID_DAYS", {"days": days})
        archive_dir = self.root / "skill_store" / "archive"
        archive_dir.mkdir(parents=True, exist_ok=True)
        return {"days": days, "archived": []}

    def backfill_provenance(self) -> dict[str, Any]:
        updated = ProvenanceBackfill(self.active_dir, SkillIndex(self.index_path)).run()
        return {"updated": updated, "updated_count": len(updated)}

    def distill_and_promote(
        self,
        trajectory_path: str | Path,
        skill_name: str | None = None,
        register_trajectory: bool = True,
    ) -> dict[str, Any]:
        trajectory_result = self.log_trajectory(trajectory_path) if register_trajectory else None
        distill_result = self.distill(trajectory_path, skill_name=skill_name)
        audit_result = self.audit(distill_result["staging_file"], trajectory_path=trajectory_path)

        promoted = audit_result["report"]["status"] == "passed"
        promotion_result: dict[str, Any] | None = None
        skipped_reason: str | None = None
        if promoted:
            promotion_result = self.promote(distill_result["staging_file"])
        else:
            skipped_reason = "promotion skipped because audit did not pass"

        return {
            "trajectory": trajectory_result,
            "distillation": distill_result,
            "audit": audit_result,
            "promotion": promotion_result,
            "promoted": promoted,
            "skipped_reason": skipped_reason,
        }
