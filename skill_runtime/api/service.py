import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from shutil import rmtree
from typing import Any

from skill_runtime.api.models import SkillMetadata
from skill_runtime.audit.skill_auditor import SkillAuditor
from skill_runtime.distill.coverage_report import DistillCoverageReport
from skill_runtime.distill.skill_generator import SkillGenerationError, SkillGenerator
from skill_runtime.execution.runtime_tools import RuntimeTools
from skill_runtime.execution.skill_executor import SkillExecutionError, SkillExecutor
from skill_runtime.governance.library_report import LibraryReport
from skill_runtime.governance.promotion_guard import PromotionGuard, PromotionGuardError
from skill_runtime.governance.provenance_backfill import ProvenanceBackfill
from skill_runtime.library_tiers import classify_skill_name
from skill_runtime.mcp.host_operations import (
    archive_duplicate_candidates_follow_up_recommendation,
    archive_fixture_skills_follow_up_recommendation,
    captured_trajectory_recommendation,
    distilled_skill_audit_recommendation,
    executed_skill_promotion_recommendation,
    governance_report_recommendation,
    no_recommendation,
    promote_skill_recommendation,
    promoted_skill_execution_recommendation,
    recommendation_from_payload,
    registered_trajectory_recommendation,
    source_ref_audit,
    search_response_payload,
    search_recommended_skill_recommendation,
    search_no_match_recommendation,
    with_recommendation,
)
from skill_runtime.memory.trajectory_capture import TrajectoryCapture, TrajectoryCaptureError
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
        self.observed_tasks_dir = self.root / "observed_tasks"

    def search(self, query: str, top_k: int = 5) -> dict[str, Any]:
        if not query.strip():
            raise RuntimeServiceError("query cannot be empty", "INVALID_QUERY")

        try:
            results = SkillIndex(self.index_path).search(query, top_k=top_k)
        except SkillIndexError as exc:
            raise RuntimeServiceError("search failed", "SEARCH_FAILED", {"reason": str(exc)}) from exc

        if results and results[0]["score"] >= self.RECOMMENDED_EXECUTION_SCORE:
            return search_response_payload(
                query,
                results,
                results[0]["skill_name"],
                search_recommended_skill_recommendation(
                    results[0]["skill_name"],
                    results[0]["host_operation"]["argument_schema"].get("args", {}).get("properties", {}),
                    additional_operations=[
                        {**item["host_operation"], "operation_role": "default"} for item in results[1:]
                    ],
                ),
            )

        return search_response_payload(
            query,
            results,
            None,
            search_no_match_recommendation(),
        )

    def execute(self, skill_name: str, args: dict[str, Any], *, dry_run: bool = False) -> dict[str, Any]:
        if not isinstance(args, dict):
            raise RuntimeServiceError(
                "--args must decode to a JSON object",
                "INVALID_ARGS_OBJECT",
                {"received_type": type(args).__name__},
            )

        index = SkillIndex(self.index_path)
        metadata = index.get(skill_name)
        if metadata is None:
            raise RuntimeServiceError("skill not found", "SKILL_NOT_FOUND", {"skill_name": skill_name})

        tools = RuntimeTools(self.root, dry_run=dry_run)
        try:
            result = SkillExecutor(
                index=index,
                tools=tools,
            ).execute(skill_name, args)
        except FileNotFoundError as exc:
            raise RuntimeServiceError("skill not found", "SKILL_NOT_FOUND", {"skill_name": skill_name}) from exc
        except SkillExecutionError as exc:
            raise RuntimeServiceError(
                "skill execution failed",
                "SKILL_EXECUTION_FAILED",
                {"reason": str(exc)},
            ) from exc

        operation_log = tools.export_records()
        observed_record, observed_payload = self._save_execution_observed_record(
            metadata,
            args,
            result,
            operation_log,
        )
        return with_recommendation(
            {
                "skill_name": skill_name,
                "dry_run": dry_run,
                "result": result,
                "operation_log": operation_log,
                "planned_changes": [
                    dict(record)
                    for record in operation_log
                    if record.get("status") == "planned"
                ],
                "observed_task_record": str(observed_record.resolve()),
                "observed_task": observed_payload,
            },
            executed_skill_promotion_recommendation(
                str(observed_record.resolve()),
                observed_task=observed_payload,
                operation_log=operation_log,
            ),
        )

    def rollback_operations(
        self,
        operation_log: list[dict[str, Any]],
        operation_ids: list[str] | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        if not isinstance(operation_log, list):
            raise RuntimeServiceError(
                "operation_log must be a list",
                "INVALID_OPERATION_LOG",
            )
        target_ids = None
        if operation_ids is not None:
            if not isinstance(operation_ids, list) or not all(isinstance(item, str) for item in operation_ids):
                raise RuntimeServiceError(
                    "operation_ids must be a list of strings",
                    "INVALID_OPERATION_IDS",
                )
            target_ids = set(operation_ids)

        rollback_results: list[dict[str, Any]] = []
        rolled_back: list[str] = []
        planned: list[str] = []
        for entry in reversed(operation_log):
            if not isinstance(entry, dict):
                continue
            operation_id = entry.get("operation_id")
            if not isinstance(operation_id, str):
                continue
            if target_ids is not None and operation_id not in target_ids:
                continue
            if entry.get("status") != "success":
                rollback_results.append(
                    {
                        "operation_id": operation_id,
                        "status": "skipped",
                        "reason": "only successful operations can be rolled back",
                    }
                )
                continue
            rollback_hint = entry.get("rollback_hint")
            if not isinstance(rollback_hint, dict):
                rollback_results.append(
                    {
                        "operation_id": operation_id,
                        "status": "unsupported",
                        "reason": "rollback hint is missing",
                    }
                )
                continue

            strategy = rollback_hint.get("strategy")
            if strategy == "delete_created_file":
                target_path = rollback_hint.get("target_path")
                if not isinstance(target_path, str) or not target_path.strip():
                    rollback_results.append(
                        {
                            "operation_id": operation_id,
                            "status": "unsupported",
                            "reason": "delete_created_file requires target_path",
                        }
                    )
                    continue
                resolved_target = self._resolve_rollback_path(target_path)
                if dry_run:
                    planned.append(operation_id)
                    rollback_results.append(
                        {
                            "operation_id": operation_id,
                            "status": "planned",
                            "strategy": strategy,
                            "target_path": str(target_path),
                        }
                    )
                    continue
                if resolved_target.is_file():
                    resolved_target.unlink()
                    rolled_back.append(operation_id)
                    rollback_results.append(
                        {
                            "operation_id": operation_id,
                            "status": "rolled_back",
                            "strategy": strategy,
                            "target_path": str(target_path),
                        }
                    )
                    continue
                if resolved_target.is_dir():
                    rmtree(resolved_target)
                    rolled_back.append(operation_id)
                    rollback_results.append(
                        {
                            "operation_id": operation_id,
                            "status": "rolled_back",
                            "strategy": strategy,
                            "target_path": str(target_path),
                        }
                    )
                    continue
                rollback_results.append(
                    {
                        "operation_id": operation_id,
                        "status": "skipped",
                        "strategy": strategy,
                        "reason": "target path does not exist",
                        "target_path": str(target_path),
                    }
                )
                continue

            if strategy == "rename_back":
                from_path = rollback_hint.get("from_path")
                to_path = rollback_hint.get("to_path")
                if not isinstance(from_path, str) or not isinstance(to_path, str):
                    rollback_results.append(
                        {
                            "operation_id": operation_id,
                            "status": "unsupported",
                            "reason": "rename_back requires from_path and to_path",
                        }
                    )
                    continue
                resolved_from = self._resolve_rollback_path(from_path)
                resolved_to = self._resolve_rollback_path(to_path)
                if dry_run:
                    planned.append(operation_id)
                    rollback_results.append(
                        {
                            "operation_id": operation_id,
                            "status": "planned",
                            "strategy": strategy,
                            "from_path": from_path,
                            "to_path": to_path,
                        }
                    )
                    continue
                if not resolved_from.exists():
                    rollback_results.append(
                        {
                            "operation_id": operation_id,
                            "status": "skipped",
                            "strategy": strategy,
                            "reason": "rollback source does not exist",
                            "from_path": from_path,
                            "to_path": to_path,
                        }
                    )
                    continue
                if resolved_to.exists():
                    rollback_results.append(
                        {
                            "operation_id": operation_id,
                            "status": "skipped",
                            "strategy": strategy,
                            "reason": "rollback destination already exists",
                            "from_path": from_path,
                            "to_path": to_path,
                        }
                    )
                    continue
                resolved_to.parent.mkdir(parents=True, exist_ok=True)
                resolved_from.rename(resolved_to)
                rolled_back.append(operation_id)
                rollback_results.append(
                    {
                        "operation_id": operation_id,
                        "status": "rolled_back",
                        "strategy": strategy,
                        "from_path": from_path,
                        "to_path": to_path,
                    }
                )
                continue

            rollback_results.append(
                {
                    "operation_id": operation_id,
                    "status": "unsupported",
                    "strategy": strategy,
                    "reason": "rollback strategy is not supported",
                }
            )

        return {
            "dry_run": dry_run,
            "rolled_back_operation_ids": rolled_back,
            "planned_operation_ids": planned,
            "results": rollback_results,
        }

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

        resolved_trajectory_path = str(Path(trajectory_path).resolve())
        payload = {
            "trajectory_path": resolved_trajectory_path,
            "skill_name": generated["skill_name"],
            "staging_file": str(generated["skill_file"].resolve()),
            "metadata_file": str(generated["metadata_file"].resolve()),
            "summary": generated["summary"],
        }
        payload = with_recommendation(
            payload,
            distilled_skill_audit_recommendation(
                str(generated["skill_file"].resolve()),
                resolved_trajectory_path,
                generated["skill_name"],
            ),
        )
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

        report = SkillAuditor(self.audits_dir).audit(file_ref, trajectory=trajectory)
        self.audits_dir.mkdir(parents=True, exist_ok=True)
        report_file = self.audits_dir / f"{file_ref.stem}.audit.json"
        report_file.write_text(json.dumps(asdict(report), ensure_ascii=False, indent=2), encoding="utf-8")
        payload = {"report": asdict(report), "report_file": str(report_file.resolve())}
        if report.status == "passed":
            payload = with_recommendation(
                payload,
                promote_skill_recommendation(
                    str(file_ref.resolve()),
                    display_label="Promote audited skill",
                    effect_summary="Promote this staging skill now that the audit has passed.",
                    risk_level="medium",
                    requires_confirmation=False,
                    source_ref=source_ref_audit(file_ref.stem),
                    reason="The audit passed, so this staging skill can be promoted.",
                )
            )
        else:
            payload = with_recommendation(
                payload,
                no_recommendation("The audit did not pass, so no promotion action is recommended."),
            )
        return payload

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
                scope_policy=payload.get("scope_policy"),
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

        return with_recommendation(
            {
                "skill_name": skill_name,
                "active_file": str(active_file.resolve()),
                "metadata_file": str(metadata_path.resolve()),
                "audit_score": report.security_score,
                "index_updated": True,
            },
            promoted_skill_execution_recommendation(skill_name, metadata.input_schema),
        )

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

        return with_recommendation(
            {
                "trajectory_path": str(saved_path.resolve()),
                "task_id": trajectory.task_id,
                "registered": True,
            },
            registered_trajectory_recommendation(str(saved_path.resolve()), task_id=trajectory.task_id),
        )

    def capture_trajectory(
        self,
        file_path: str | Path | None = None,
        observed_task: dict[str, Any] | None = None,
        task_id: str | None = None,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        if bool(file_path) == bool(observed_task):
            raise RuntimeServiceError(
                "provide exactly one of file_path or observed_task",
                "INVALID_CAPTURE_INPUT",
            )
        try:
            capturer = TrajectoryCapture(self.trajectories_dir)
            if observed_task is not None:
                trajectory, saved_path = capturer.capture_payload(
                    observed_task,
                    task_id=task_id,
                    session_id=session_id,
                )
            else:
                trajectory, saved_path = capturer.capture(
                    file_path,
                    task_id=task_id,
                    session_id=session_id,
                )
        except FileNotFoundError as exc:
            raise RuntimeServiceError(
                "observed task file not found",
                "OBSERVED_TASK_NOT_FOUND",
                {"path": str(file_path)},
            ) from exc
        except (TrajectoryCaptureError, json.JSONDecodeError) as exc:
            raise RuntimeServiceError(
                "observed task record is invalid",
                "INVALID_OBSERVED_TASK",
                {"reason": str(exc)},
            ) from exc

        return with_recommendation(
            {
                "trajectory_path": str(saved_path.resolve()),
                "task_id": trajectory.task_id,
                "session_id": trajectory.session_id,
                "captured": True,
            },
            captured_trajectory_recommendation(str(saved_path.resolve()), task_id=trajectory.task_id),
        )

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

        return with_recommendation(
            {"index_path": str(index_path.resolve()), "skill_count": skill_count},
            governance_report_recommendation(
                display_label="Refresh governance report",
                effect_summary=(
                    "Refresh the governance report to review the latest indexed skill inventory and maintenance actions."
                ),
                risk_level="low",
                requires_confirmation=False,
                reason="Reindex changes the active library snapshot. Refresh governance_report next.",
            ),
        )

    def archive_cold(self, days: int) -> dict[str, Any]:
        if days < 1:
            raise RuntimeServiceError("days must be >= 1", "INVALID_DAYS", {"days": days})
        cutoff = datetime.now(timezone.utc).timestamp() - (days * 86400)
        index = SkillIndex(self.index_path)
        skills = index.load_all()
        archived: list[str] = []

        for metadata in skills:
            if metadata.status != "active":
                continue

            reference_time = metadata.last_used_at or metadata.created_at
            try:
                reference_timestamp = datetime.fromisoformat(reference_time).timestamp()
            except ValueError:
                continue

            if reference_timestamp > cutoff:
                continue
            if self._archive_skill_metadata(metadata):
                archived.append(metadata.skill_name)

        index.save_all(skills)
        return with_recommendation(
            {"days": days, "archived": archived},
            governance_report_recommendation(
                display_label="Refresh governance report",
                effect_summary=(
                    "Refresh the governance report to review the latest archived and active skill counts."
                ),
                risk_level="low",
                requires_confirmation=False,
                reason="Cold-skill archival changes library state. Refresh governance_report next.",
            ),
        )

    def backfill_provenance(self) -> dict[str, Any]:
        updated = ProvenanceBackfill(self.active_dir, SkillIndex(self.index_path)).run()
        return with_recommendation(
            {"updated": updated, "updated_count": len(updated)},
            governance_report_recommendation(
                display_label="Refresh governance report",
                effect_summary=(
                    "Refresh the governance report to review the latest rule provenance and active skill counts."
                ),
                risk_level="low",
                requires_confirmation=False,
                reason="Provenance backfill updates active-skill metadata. Refresh governance_report next.",
            ),
        )

    def governance_report(self) -> dict[str, Any]:
        return LibraryReport(self.root, SkillIndex(self.index_path)).build()

    def distill_coverage_report(
        self,
        observed_task_scope: str = "all",
        max_family_items: int | None = None,
        min_family_count: int = 1,
    ) -> dict[str, Any]:
        allowed_scopes = DistillCoverageReport.OBSERVED_TASK_SCOPES
        if observed_task_scope not in allowed_scopes:
            raise RuntimeServiceError(
                "observed_task_scope must be one of all, backlog, or execution",
                "INVALID_OBSERVED_TASK_SCOPE",
                {"observed_task_scope": observed_task_scope, "allowed": sorted(allowed_scopes)},
            )
        if max_family_items is not None and max_family_items < 1:
            raise RuntimeServiceError(
                "max_family_items must be >= 1 when provided",
                "INVALID_MAX_FAMILY_ITEMS",
                {"max_family_items": max_family_items},
            )
        if min_family_count < 1:
            raise RuntimeServiceError(
                "min_family_count must be >= 1",
                "INVALID_MIN_FAMILY_COUNT",
                {"min_family_count": min_family_count},
            )
        return DistillCoverageReport(self.root).build(
            observed_task_scope=observed_task_scope,
            max_family_items=max_family_items,
            min_family_count=min_family_count,
        )

    def archive_duplicate_candidates(
        self,
        skill_names: list[str] | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        index = SkillIndex(self.index_path)
        skills = index.load_all()
        metadata_by_name = {skill.skill_name: skill for skill in skills}
        report = LibraryReport(self.root, index).build()
        archived: list[str] = []
        planned: list[str] = []
        target_names = set(skill_names or [])

        for cluster in report["duplicate_candidates"]:
            for skill_name in cluster["archive_candidates"]:
                if target_names and skill_name not in target_names:
                    continue
                metadata = metadata_by_name.get(skill_name)
                if metadata is None or metadata.status != "active":
                    continue
                planned.append(skill_name)
                if dry_run:
                    continue
                if self._archive_skill_metadata(metadata):
                    archived.append(skill_name)

        if not dry_run:
            index.save_all(skills)
        recommendation = archive_duplicate_candidates_follow_up_recommendation(
            sorted(set(planned)),
            dry_run=dry_run,
        )
        return with_recommendation(
            {
                "dry_run": dry_run,
                "planned": sorted(set(planned)),
                "planned_count": len(set(planned)),
                "archived": archived,
                "archived_count": len(archived),
            },
            recommendation,
        )

    def archive_fixture_skills(
        self,
        skill_names: list[str] | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        index = SkillIndex(self.index_path)
        skills = index.load_all()
        target_names = set(skill_names or [])
        archived: list[str] = []
        planned: list[str] = []

        for metadata in skills:
            if metadata.status != "active":
                continue
            if classify_skill_name(metadata.skill_name) != "fixture":
                continue
            if target_names and metadata.skill_name not in target_names:
                continue
            planned.append(metadata.skill_name)
            if dry_run:
                continue
            if self._archive_skill_metadata(metadata):
                archived.append(metadata.skill_name)

        if not dry_run:
            index.save_all(skills)
        recommendation = archive_fixture_skills_follow_up_recommendation(
            sorted(set(planned)),
            dry_run=dry_run,
        )
        return with_recommendation(
            {
                "dry_run": dry_run,
                "planned": sorted(set(planned)),
                "planned_count": len(set(planned)),
                "archived": archived,
                "archived_count": len(archived),
            },
            recommendation,
        )

    def distill_and_promote(
        self,
        trajectory_path: str | Path | None = None,
        observed_task_path: str | Path | None = None,
        observed_task: dict[str, Any] | None = None,
        skill_name: str | None = None,
        register_trajectory: bool = True,
    ) -> dict[str, Any]:
        provided_inputs = [
            value
            for value in (trajectory_path, observed_task_path, observed_task)
            if value is not None
        ]
        if len(provided_inputs) != 1:
            raise RuntimeServiceError(
                "provide exactly one of trajectory_path, observed_task_path, or observed_task",
                "INVALID_DISTILL_PROMOTE_INPUT",
            )

        capture_result: dict[str, Any] | None = None
        resolved_trajectory_path = trajectory_path
        if observed_task_path or observed_task is not None:
            capture_result = self.capture_trajectory(file_path=observed_task_path, observed_task=observed_task)
            resolved_trajectory_path = capture_result["trajectory_path"]
            register_trajectory = False

        trajectory_result = self.log_trajectory(resolved_trajectory_path) if register_trajectory else None
        distill_result = self.distill(resolved_trajectory_path, skill_name=skill_name)
        audit_result = self.audit(distill_result["staging_file"], trajectory_path=resolved_trajectory_path)

        promoted = audit_result["report"]["status"] == "passed"
        promotion_result: dict[str, Any] | None = None
        skipped_reason: str | None = None
        if promoted:
            promotion_result = self.promote(distill_result["staging_file"])
            recommendation = recommendation_from_payload(promotion_result)
        else:
            skipped_reason = "promotion skipped because audit did not pass"
            recommendation = no_recommendation(
                "The workflow was not promoted, so no execution action is recommended."
            )

        return with_recommendation(
            {
                "capture": capture_result,
                "trajectory": trajectory_result,
                "distillation": distill_result,
                "audit": audit_result,
                "promotion": promotion_result,
                "promoted": promoted,
                "skipped_reason": skipped_reason,
            },
            recommendation,
        )

    def _archive_skill_metadata(self, metadata: SkillMetadata) -> bool:
        archive_dir = self.root / "skill_store" / "archive"
        archive_dir.mkdir(parents=True, exist_ok=True)
        source_path = Path(metadata.file_path)
        metadata_path = source_path.with_name(f"{metadata.skill_name}.metadata.json")
        if not source_path.exists() or not metadata_path.exists():
            return False

        archived_skill = archive_dir / source_path.name
        archived_metadata = archive_dir / metadata_path.name
        archived_skill.write_text(source_path.read_text(encoding="utf-8"), encoding="utf-8")
        archived_metadata.write_text(metadata_path.read_text(encoding="utf-8"), encoding="utf-8")
        source_path.unlink()
        metadata_path.unlink()

        metadata.file_path = str(archived_skill.resolve())
        metadata.status = "archived"
        archived_metadata.write_text(json.dumps(asdict(metadata), ensure_ascii=False, indent=2), encoding="utf-8")
        return True

    def _save_execution_observed_record(
        self,
        metadata: SkillMetadata,
        args: dict[str, Any],
        result: dict[str, Any],
        steps: list[dict[str, Any]],
    ) -> tuple[Path, dict[str, Any]]:
        self.observed_tasks_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        output_path = self.observed_tasks_dir / f"execute_{metadata.skill_name}_{stamp}.json"

        artifacts = result.get("artifacts")
        if not isinstance(artifacts, list):
            artifacts = []

        payload = {
            "task": metadata.summary or f"Execute skill {metadata.skill_name}.",
            "skill_name": metadata.skill_name,
            "skill_summary": metadata.summary,
            "skill_args": args,
            "actions": steps,
            "operation_log": steps,
            "result": {
                "status": result.get("status", "completed"),
                "outputs": artifacts,
            },
        }
        output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return output_path, payload

    def _resolve_rollback_path(self, path: str | Path) -> Path:
        target = Path(path)
        if not target.is_absolute():
            target = (self.root / target).resolve()
        else:
            target = target.resolve()
        try:
            target.relative_to(self.root)
        except ValueError as exc:
            raise RuntimeServiceError(
                "rollback path escapes runtime root",
                "INVALID_ROLLBACK_PATH",
                {"path": str(path)},
            ) from exc
        return target
