import json
import re
from dataclasses import asdict
from datetime import datetime, timezone
from difflib import unified_diff
from hashlib import sha256
from pathlib import Path
from shutil import rmtree
from typing import Any

from skill_runtime.api.models import SkillMetadata
from skill_runtime.audit.skill_auditor import SkillAuditor
from skill_runtime.distill.coverage_report import DistillCoverageReport
from skill_runtime.distill.skill_generator import SkillGenerationError, SkillGenerator
from skill_runtime.execution.runtime_tools import RuntimeTools
from skill_runtime.execution.skill_executor import SkillExecutionError, SkillExecutor
from skill_runtime.evolution.candidates import EvolutionCandidateStore
from skill_runtime.governance.library_report import LibraryReport
from skill_runtime.governance.promotion_guard import PromotionGuard, PromotionGuardError
from skill_runtime.governance.provenance_backfill import ProvenanceBackfill
from skill_runtime.library_tiers import classify_skill_name
from skill_runtime.mcp.host_operations import (
    archive_duplicate_candidates_follow_up_recommendation,
    archive_fixture_skills_follow_up_recommendation,
    applied_evolution_candidate_follow_up_recommendation,
    captured_trajectory_recommendation,
    distilled_skill_audit_recommendation,
    executed_skill_promotion_recommendation,
    governance_report_recommendation,
    no_recommendation,
    promote_global_codex_skill_recommendation,
    promote_skill_recommendation,
    promoted_skill_execution_recommendation,
    recommendation_from_payload,
    registered_trajectory_recommendation,
    reviewed_evolution_candidate_recommendation,
    rolled_back_evolution_candidate_follow_up_recommendation,
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
            staging_metadata = self._load_staging_metadata(file_ref)
            if _prefers_global_codex_skill(staging_metadata):
                payload = with_recommendation(
                    payload,
                    promote_global_codex_skill_recommendation(
                        str(file_ref.resolve()),
                        display_label="Promote global Codex skill",
                        effect_summary=(
                            "Promote this reusable workflow into the global Codex skill library."
                        ),
                        risk_level="medium",
                        requires_confirmation=False,
                        source_ref=source_ref_audit(file_ref.stem),
                        reason=(
                            "The audit passed and the skill is marked as a reusable workflow, so the "
                            "authoritative copy should live in the global Codex skill library."
                        ),
                        additional_operations=[
                            promote_skill_recommendation(
                                str(file_ref.resolve()),
                                display_label="Promote project active skill",
                                effect_summary=(
                                    "Promote this staging skill into the project active runtime library instead."
                                ),
                                risk_level="medium",
                                requires_confirmation=False,
                                source_ref=source_ref_audit(file_ref.stem),
                            )["recommended_host_operation"]
                        ],
                    )
                )
            else:
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

    def promote_to_global_codex_skill(
        self,
        file_path: str | Path,
        *,
        global_skills_dir: str | Path | None = None,
        global_skill_name: str | None = None,
        overwrite: bool = False,
    ) -> dict[str, Any]:
        file_ref = Path(file_path)
        if not file_ref.exists():
            raise RuntimeServiceError(
                "staging skill file not found",
                "SKILL_FILE_NOT_FOUND",
                {"path": str(file_ref)},
            )

        if "staging" not in {part.lower() for part in file_ref.parts}:
            raise RuntimeServiceError(
                "only staging skills can be promoted to a global Codex skill",
                "INVALID_PROMOTION_SOURCE",
                {"path": str(file_ref)},
            )

        runtime_skill_name = file_ref.stem
        try:
            report = PromotionGuard(self.audits_dir).assert_promotable(runtime_skill_name)
        except FileNotFoundError as exc:
            raise RuntimeServiceError(
                "audit report not found",
                "AUDIT_NOT_FOUND",
                {"skill_name": runtime_skill_name},
            ) from exc
        except PromotionGuardError as exc:
            raise RuntimeServiceError(
                "latest audit did not pass",
                "AUDIT_NOT_PASSED",
                {"skill_name": runtime_skill_name, "reason": str(exc)},
            ) from exc

        metadata = self._load_staging_metadata(file_ref)
        target_root = self._resolve_global_skills_dir(global_skills_dir)
        resolved_global_skill_name = _global_skill_directory_name(global_skill_name or runtime_skill_name)
        target_dir = target_root / resolved_global_skill_name
        skill_file = target_dir / "SKILL.md"
        agent_file = target_dir / "agents" / "openai.yaml"

        if target_dir.exists() and not overwrite:
            raise RuntimeServiceError(
                "global Codex skill already exists",
                "GLOBAL_SKILL_EXISTS",
                {"global_skill_name": resolved_global_skill_name, "target_dir": str(target_dir)},
            )

        target_dir.mkdir(parents=True, exist_ok=True)
        agent_file.parent.mkdir(parents=True, exist_ok=True)

        description = self._global_skill_description(metadata, report.optimized_docstring, runtime_skill_name)
        skill_file.write_text(
            _render_global_skill_markdown(
                global_skill_name=resolved_global_skill_name,
                description=description,
                runtime_skill_name=runtime_skill_name,
                optimized_docstring=report.optimized_docstring,
                metadata=metadata,
            ),
            encoding="utf-8",
        )
        agent_file.write_text(
            _render_global_skill_openai_yaml(resolved_global_skill_name, description),
            encoding="utf-8",
        )

        return {
            "runtime_skill_name": runtime_skill_name,
            "global_skill_name": resolved_global_skill_name,
            "global_skill_path": str(target_dir.resolve()),
            "skill_file": str(skill_file.resolve()),
            "agent_file": str(agent_file.resolve()),
            "source_role": "authoritative_global_skill",
            "audit_score": report.security_score,
            "index_updated": False,
            "active_copy_created": False,
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
        changed_metadata: list[SkillMetadata] = []

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
                changed_metadata.append(metadata)

        if changed_metadata:
            index.save_merged(changed_metadata)
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

    def review_evolution_candidate(
        self,
        candidate: str | Path,
        global_skills_dir: str | Path | None = None,
    ) -> dict[str, Any]:
        store = EvolutionCandidateStore(self.root)
        try:
            candidate_payload, candidate_path = store.load_candidate(candidate)
        except FileNotFoundError as exc:
            raise RuntimeServiceError(
                "evolution candidate not found",
                "EVOLUTION_CANDIDATE_NOT_FOUND",
                {"candidate": str(candidate)},
            ) from exc
        except (json.JSONDecodeError, ValueError) as exc:
            raise RuntimeServiceError(
                "evolution candidate is invalid",
                "INVALID_EVOLUTION_CANDIDATE",
                {"candidate": str(candidate), "reason": str(exc)},
            ) from exc

        target_skill_name = _required_candidate_string(candidate_payload, "target_skill_name")
        reason = _required_candidate_string(candidate_payload, "reason")
        evidence = _candidate_string_list(candidate_payload.get("evidence"))
        proposed_changes = _candidate_string_list(candidate_payload.get("proposed_changes"))
        target_skill_path = self._resolve_global_skill_file(target_skill_name, global_skills_dir)

        if target_skill_path is None:
            review = store.create_review(
                candidate_payload,
                {
                    "decision": "rejected",
                    "reason": "target global skill could not be found",
                    "target_skill_name": target_skill_name,
                    "target_skill_path": None,
                    "required_next_action": "check_target_skill_name",
                    "proposed_diff": "",
                },
            )
            updated = store.update_candidate(
                candidate_path,
                {
                    "status": "rejected",
                    "review_decision": "rejected",
                    "review_reason": review["reason"],
                    "review_path": review["review_path"],
                },
            )
            return with_recommendation(
                {"candidate": updated, "review": review, "mutated_global_skill": False},
                no_recommendation("Target global skill could not be found. Fix the target before reviewing again."),
            )

        if not evidence or not proposed_changes:
            review = store.create_review(
                candidate_payload,
                {
                    "decision": "needs_more_evidence",
                    "reason": "candidate needs both evidence and proposed changes before a skill patch is useful",
                    "target_skill_name": target_skill_name,
                    "target_skill_path": str(target_skill_path.resolve()),
                    "required_next_action": "collect_more_evidence",
                    "proposed_diff": "",
                },
            )
            updated = store.update_candidate(
                candidate_path,
                {
                    "status": "needs_more_evidence",
                    "review_decision": "needs_more_evidence",
                    "review_reason": review["reason"],
                    "review_path": review["review_path"],
                },
            )
            return with_recommendation(
                {"candidate": updated, "review": review, "mutated_global_skill": False},
                no_recommendation("Add clearer evidence and proposed changes before this candidate can move to apply."),
            )

        proposed_diff = self._build_evolution_candidate_diff(
            target_skill_path,
            candidate_payload,
            reason=reason,
            evidence=evidence,
            proposed_changes=proposed_changes,
        )
        proposed_apply_text = self._build_evolution_candidate_apply_text(
            candidate_payload,
            reason=reason,
            evidence=evidence,
            proposed_changes=proposed_changes,
        )
        review = store.create_review(
            candidate_payload,
            {
                "decision": "ready_for_manual_diff",
                "reason": "candidate has enough evidence for manual skill patch review",
                "target_skill_name": target_skill_name,
                "target_skill_path": str(target_skill_path.resolve()),
                "target_content_hash": _file_sha256(target_skill_path),
                "required_next_action": "review_diff_before_editing_global_skill",
                "proposed_diff": proposed_diff,
                "proposed_apply_text": proposed_apply_text,
            },
        )
        updated = store.update_candidate(
            candidate_path,
            {
                "status": "reviewed",
                "review_decision": "ready_for_manual_diff",
                "review_reason": review["reason"],
                "review_path": review["review_path"],
                "diff_path": review.get("diff_path"),
            },
        )
        return with_recommendation(
            {"candidate": updated, "review": review, "mutated_global_skill": False},
            reviewed_evolution_candidate_recommendation(
                str(candidate_path),
                str(candidate_payload.get("candidate_id") or ""),
                global_skills_dir=str(global_skills_dir) if global_skills_dir is not None else None,
                reason="Review completed. Apply only after manually checking the proposed diff and confirming the target should change.",
            ),
        )

    def apply_evolution_candidate(
        self,
        candidate: str | Path,
        *,
        confirm_apply: bool = False,
        global_skills_dir: str | Path | None = None,
    ) -> dict[str, Any]:
        if not confirm_apply:
            raise RuntimeServiceError(
                "confirm_apply must be true before applying an evolution candidate",
                "EVOLUTION_APPLY_CONFIRMATION_REQUIRED",
            )

        store = EvolutionCandidateStore(self.root)
        try:
            candidate_payload, candidate_path = store.load_candidate(candidate)
        except FileNotFoundError as exc:
            raise RuntimeServiceError(
                "evolution candidate not found",
                "EVOLUTION_CANDIDATE_NOT_FOUND",
                {"candidate": str(candidate)},
            ) from exc
        except (json.JSONDecodeError, ValueError) as exc:
            raise RuntimeServiceError(
                "evolution candidate is invalid",
                "INVALID_EVOLUTION_CANDIDATE",
                {"candidate": str(candidate), "reason": str(exc)},
            ) from exc

        review_path = candidate_payload.get("review_path")
        if not isinstance(review_path, str) or not review_path.strip():
            raise RuntimeServiceError(
                "evolution candidate has not been reviewed",
                "EVOLUTION_CANDIDATE_NOT_REVIEWED",
                {"candidate": str(candidate_path)},
            )
        review = _load_json_object(Path(review_path), "evolution review")
        if review.get("decision") != "ready_for_manual_diff":
            raise RuntimeServiceError(
                "only ready_for_manual_diff reviews can be applied",
                "EVOLUTION_REVIEW_NOT_APPLICABLE",
                {"decision": review.get("decision")},
            )

        target_skill_path = Path(_required_candidate_string(review, "target_skill_path")).resolve()
        if global_skills_dir is not None:
            allowed_root = self._resolve_global_skills_dir(global_skills_dir)
            try:
                target_skill_path.relative_to(allowed_root)
            except ValueError as exc:
                raise RuntimeServiceError(
                    "review target escapes the requested global skills directory",
                    "INVALID_EVOLUTION_TARGET",
                    {"target_skill_path": str(target_skill_path), "global_skills_dir": str(allowed_root)},
                ) from exc
        if not target_skill_path.exists():
            raise RuntimeServiceError(
                "review target global skill no longer exists",
                "EVOLUTION_TARGET_NOT_FOUND",
                {"target_skill_path": str(target_skill_path)},
            )

        expected_hash = _required_candidate_string(review, "target_content_hash")
        current_hash = _file_sha256(target_skill_path)
        if current_hash != expected_hash:
            raise RuntimeServiceError(
                "review target changed after review; regenerate the review before applying",
                "EVOLUTION_TARGET_CHANGED",
                {
                    "target_skill_path": str(target_skill_path),
                    "expected_hash": expected_hash,
                    "current_hash": current_hash,
                },
            )

        apply_text = _required_candidate_string(review, "proposed_apply_text")
        original_text = target_skill_path.read_text(encoding="utf-8-sig")
        next_text = original_text.rstrip() + "\n\n" + apply_text.strip() + "\n"
        backup_path = self._write_evolution_backup(candidate_payload, target_skill_path, original_text)
        target_skill_path.write_text(next_text, encoding="utf-8")
        application = store.create_application(
            candidate_payload,
            {
                "decision": "applied",
                "target_skill_name": review.get("target_skill_name"),
                "target_skill_path": str(target_skill_path),
                "backup_path": str(backup_path.resolve()),
                "review_path": str(Path(review_path).resolve()),
                "previous_content_hash": expected_hash,
                "new_content_hash": _file_sha256(target_skill_path),
                "rollback_hint": {
                    "strategy": "restore_backup_file",
                    "backup_path": str(backup_path.resolve()),
                    "target_path": str(target_skill_path),
                },
            },
        )
        updated = store.update_candidate(
            candidate_path,
            {
                "status": "applied",
                "application_path": application["application_path"],
                "applied_at": application["created_at"],
                "backup_path": application["backup_path"],
            },
        )
        return with_recommendation(
            {"candidate": updated, "application": application, "mutated_global_skill": True},
            applied_evolution_candidate_follow_up_recommendation(
                str(candidate_path),
                str(candidate_payload.get("candidate_id") or ""),
                global_skills_dir=str(global_skills_dir) if global_skills_dir is not None else None,
                reason="The reviewed evolution was applied. Keep explicit rollback available while you inspect the updated global skill.",
            ),
        )

    def rollback_evolution_candidate(
        self,
        candidate: str | Path,
        *,
        confirm_rollback: bool = False,
        global_skills_dir: str | Path | None = None,
    ) -> dict[str, Any]:
        if not confirm_rollback:
            raise RuntimeServiceError(
                "confirm_rollback must be true before rolling back an applied evolution candidate",
                "EVOLUTION_ROLLBACK_CONFIRMATION_REQUIRED",
            )

        store = EvolutionCandidateStore(self.root)
        try:
            candidate_payload, candidate_path = store.load_candidate(candidate)
        except FileNotFoundError as exc:
            raise RuntimeServiceError(
                "evolution candidate not found",
                "EVOLUTION_CANDIDATE_NOT_FOUND",
                {"candidate": str(candidate)},
            ) from exc
        except (json.JSONDecodeError, ValueError) as exc:
            raise RuntimeServiceError(
                "evolution candidate is invalid",
                "INVALID_EVOLUTION_CANDIDATE",
                {"candidate": str(candidate), "reason": str(exc)},
            ) from exc

        if candidate_payload.get("status") != "applied":
            raise RuntimeServiceError(
                "only applied evolution candidates can be rolled back",
                "EVOLUTION_CANDIDATE_NOT_APPLIED",
                {"candidate": str(candidate_path), "status": candidate_payload.get("status")},
            )
        application_path = candidate_payload.get("application_path")
        if not isinstance(application_path, str) or not application_path.strip():
            raise RuntimeServiceError(
                "applied evolution candidate is missing its application record",
                "EVOLUTION_APPLICATION_NOT_FOUND",
                {"candidate": str(candidate_path)},
            )
        application = _load_json_object(Path(application_path), "evolution application")
        rollback_hint = application.get("rollback_hint")
        if not isinstance(rollback_hint, dict):
            raise RuntimeServiceError(
                "applied evolution candidate is missing a rollback hint",
                "INVALID_EVOLUTION_ROLLBACK_HINT",
                {"application_path": str(application_path)},
            )
        if rollback_hint.get("strategy") != "restore_backup_file":
            raise RuntimeServiceError(
                "evolution candidate rollback strategy is unsupported",
                "UNSUPPORTED_EVOLUTION_ROLLBACK_STRATEGY",
                {"strategy": rollback_hint.get("strategy")},
            )

        target_skill_path = Path(_required_record_string(rollback_hint, "target_path", "rollback hint")).resolve()
        backup_path = Path(_required_record_string(rollback_hint, "backup_path", "rollback hint")).resolve()
        if global_skills_dir is not None:
            allowed_root = self._resolve_global_skills_dir(global_skills_dir)
            try:
                target_skill_path.relative_to(allowed_root)
            except ValueError as exc:
                raise RuntimeServiceError(
                    "rollback target escapes the requested global skills directory",
                    "INVALID_EVOLUTION_TARGET",
                    {"target_skill_path": str(target_skill_path), "global_skills_dir": str(allowed_root)},
                ) from exc
        if not target_skill_path.exists():
            raise RuntimeServiceError(
                "rollback target global skill no longer exists",
                "EVOLUTION_TARGET_NOT_FOUND",
                {"target_skill_path": str(target_skill_path)},
            )
        if not backup_path.exists():
            raise RuntimeServiceError(
                "evolution rollback backup file not found",
                "EVOLUTION_BACKUP_NOT_FOUND",
                {"backup_path": str(backup_path)},
            )

        expected_current_hash = _required_record_string(application, "new_content_hash", "evolution application")
        current_hash = _file_sha256(target_skill_path)
        if current_hash != expected_current_hash:
            raise RuntimeServiceError(
                "target changed after evolution apply; refusing to overwrite it with rollback backup",
                "EVOLUTION_TARGET_CHANGED_AFTER_APPLY",
                {
                    "target_skill_path": str(target_skill_path),
                    "expected_hash": expected_current_hash,
                    "current_hash": current_hash,
                },
            )

        restored_text = backup_path.read_text(encoding="utf-8-sig")
        target_skill_path.write_text(restored_text, encoding="utf-8")
        rollback = store.create_rollback(
            candidate_payload,
            {
                "decision": "rolled_back",
                "target_skill_name": application.get("target_skill_name"),
                "target_skill_path": str(target_skill_path),
                "backup_path": str(backup_path),
                "application_path": str(Path(application_path).resolve()),
                "review_path": application.get("review_path") or candidate_payload.get("review_path"),
                "previous_content_hash": current_hash,
                "restored_content_hash": _file_sha256(target_skill_path),
                "rollback_hint": {
                    "strategy": "restore_backup_file",
                    "backup_path": str(backup_path),
                    "target_path": str(target_skill_path),
                },
            },
        )
        updated = store.update_candidate(
            candidate_path,
            {
                "status": "rolled_back",
                "rollback_path": rollback["rollback_path"],
                "rolled_back_at": rollback["created_at"],
            },
        )
        return with_recommendation(
            {"candidate": updated, "rollback": rollback, "mutated_global_skill": True},
            rolled_back_evolution_candidate_follow_up_recommendation(
                str(candidate_payload.get("candidate_id") or ""),
                reason="Rollback completed. Refresh governance to confirm the rolled-back lifecycle state and current library health.",
            ),
        )

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
        changed_metadata: list[SkillMetadata] = []
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
                    changed_metadata.append(metadata)

        if not dry_run and changed_metadata:
            index.save_merged(changed_metadata)
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
        changed_metadata: list[SkillMetadata] = []

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
                changed_metadata.append(metadata)

        if not dry_run and changed_metadata:
            index.save_merged(changed_metadata)
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

    def _load_staging_metadata(self, file_ref: Path) -> dict[str, Any]:
        metadata_path = file_ref.with_name(f"{file_ref.stem}.metadata.json")
        if not metadata_path.exists():
            return {}
        try:
            payload = json.loads(metadata_path.read_text(encoding="utf-8-sig"))
        except (json.JSONDecodeError, OSError):
            return {}
        return payload if isinstance(payload, dict) else {}

    def _resolve_global_skills_dir(self, global_skills_dir: str | Path | None) -> Path:
        if global_skills_dir is not None:
            return Path(global_skills_dir).expanduser().resolve()
        home = Path.home()
        return (home / ".codex" / "skills").resolve()

    def _resolve_global_skill_file(
        self,
        target_skill_name: str,
        global_skills_dir: str | Path | None,
    ) -> Path | None:
        skills_dir = self._resolve_global_skills_dir(global_skills_dir)
        candidates = [
            skills_dir / target_skill_name / "SKILL.md",
            skills_dir / target_skill_name.replace("_", "-") / "SKILL.md",
            skills_dir / target_skill_name.replace("-", "_") / "SKILL.md",
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        if not skills_dir.exists():
            return None
        for skill_file in sorted(skills_dir.glob("*/SKILL.md")):
            try:
                header = skill_file.read_text(encoding="utf-8-sig")[:500]
            except OSError:
                continue
            if f"name: {target_skill_name}" in header or f"name: {target_skill_name.replace('_', '-')}" in header:
                return skill_file
        return None

    def _build_evolution_candidate_diff(
        self,
        target_skill_path: Path,
        candidate: dict[str, Any],
        *,
        reason: str,
        evidence: list[str],
        proposed_changes: list[str],
    ) -> str:
        original_text = target_skill_path.read_text(encoding="utf-8-sig")
        original_lines = original_text.splitlines(keepends=True)
        block_lines = [
            "\n",
            "## Evolution Candidate Proposal\n",
            "\n",
            "This block is a generated proposal for manual review. Integrate the useful parts into the correct workflow section before applying.\n",
            "\n",
            f"- Source task: {candidate.get('source_task_description') or 'unknown'}\n",
            f"- Reason: {reason}\n",
            "- Evidence:\n",
            *[f"  - {item}\n" for item in evidence],
            "- Proposed changes:\n",
            *[f"  - {item}\n" for item in proposed_changes],
        ]
        proposed_lines = original_lines + block_lines
        return "".join(
            unified_diff(
                original_lines,
                proposed_lines,
                fromfile=str(target_skill_path),
                tofile=f"{target_skill_path} (proposal)",
            )
        )

    def _build_evolution_candidate_apply_text(
        self,
        candidate: dict[str, Any],
        *,
        reason: str,
        evidence: list[str],
        proposed_changes: list[str],
    ) -> str:
        lines = [
            "## Evolution Update",
            "",
            f"- Source task: {candidate.get('source_task_description') or 'unknown'}",
            f"- Reason: {reason}",
            "- Evidence:",
            *[f"  - {item}" for item in evidence],
            "- Applied workflow changes:",
            *[f"  - {item}" for item in proposed_changes],
        ]
        return "\n".join(lines)

    def _write_evolution_backup(self, candidate: dict[str, Any], target_skill_path: Path, content: str) -> Path:
        candidate_id = str(candidate.get("candidate_id") or "evolution_candidate")
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
        backup_dir = self.root / ".skill_runtime" / "evolution_backups" / candidate_id
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = backup_dir / f"{target_skill_path.name}.{stamp}.bak"
        backup_path.write_text(content, encoding="utf-8")
        return backup_path

    def _global_skill_description(
        self,
        metadata: dict[str, Any],
        optimized_docstring: str,
        runtime_skill_name: str,
    ) -> str:
        summary = metadata.get("summary")
        if isinstance(summary, str) and summary.strip():
            return _single_line(summary)
        if optimized_docstring.strip():
            return _single_line(optimized_docstring)
        return f"Reusable workflow promoted from runtime skill {runtime_skill_name}."

    def distill_and_promote(
        self,
        trajectory_path: str | Path | None = None,
        observed_task_path: str | Path | None = None,
        observed_task: dict[str, Any] | None = None,
        skill_name: str | None = None,
        register_trajectory: bool = True,
        promotion_target: str = "active",
        global_skills_dir: str | Path | None = None,
        global_skill_name: str | None = None,
        overwrite_global_skill: bool = False,
    ) -> dict[str, Any]:
        resolved_promotion_target = _normalize_promotion_target(promotion_target)
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
            if resolved_promotion_target == "global_codex":
                promotion_result = self.promote_to_global_codex_skill(
                    distill_result["staging_file"],
                    global_skills_dir=global_skills_dir,
                    global_skill_name=global_skill_name,
                    overwrite=overwrite_global_skill,
                )
                recommendation = no_recommendation(
                    "The workflow was promoted to the global Codex skill library."
                )
            else:
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
                "promotion_target": resolved_promotion_target,
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


def _global_skill_directory_name(raw_name: str) -> str:
    name = raw_name.strip().replace("_", "-").lower()
    name = re.sub(r"[^a-z0-9-]+", "-", name)
    name = re.sub(r"-{2,}", "-", name).strip("-")
    if not name:
        raise RuntimeServiceError("global skill name cannot be empty", "INVALID_GLOBAL_SKILL_NAME")
    return name


def _normalize_promotion_target(raw_target: str) -> str:
    target = raw_target.strip().replace("-", "_").lower()
    if target not in {"active", "global_codex"}:
        raise RuntimeServiceError(
            "promotion_target must be active or global_codex",
            "INVALID_PROMOTION_TARGET",
            {"promotion_target": raw_target},
        )
    return target


def _prefers_global_codex_skill(metadata: dict[str, Any]) -> bool:
    tags = metadata.get("tags")
    if not isinstance(tags, list):
        return False
    normalized = {str(tag).strip().lower() for tag in tags}
    return bool({"workflow", "global-workflow", "codex-skill"} & normalized)


def _single_line(value: str) -> str:
    return " ".join(value.strip().split())


def _required_candidate_string(candidate: dict[str, Any], key: str) -> str:
    value = candidate.get(key)
    if isinstance(value, str) and value.strip():
        return value.strip()
    raise RuntimeServiceError(
        "evolution candidate is missing a required field",
        "INVALID_EVOLUTION_CANDIDATE",
        {"field": key},
    )


def _candidate_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _required_record_string(record: dict[str, Any], key: str, label: str) -> str:
    value = record.get(key)
    if isinstance(value, str) and value.strip():
        return value.strip()
    raise RuntimeServiceError(
        f"{label} is missing a required field",
        "INVALID_EVOLUTION_RECORD",
        {"field": key},
    )


def _file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _load_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError as exc:
        raise RuntimeServiceError(
            f"{label} file not found",
            "EVOLUTION_REVIEW_NOT_FOUND",
            {"path": str(path)},
        ) from exc
    except json.JSONDecodeError as exc:
        raise RuntimeServiceError(
            f"{label} file is invalid",
            "INVALID_EVOLUTION_REVIEW",
            {"path": str(path), "reason": str(exc)},
        ) from exc
    if not isinstance(payload, dict):
        raise RuntimeServiceError(
            f"{label} must be a JSON object",
            "INVALID_EVOLUTION_REVIEW",
            {"path": str(path)},
        )
    return payload


def _yaml_double_quoted(value: str) -> str:
    return json.dumps(_single_line(value), ensure_ascii=False)


def _markdown_heading_from_name(name: str) -> str:
    return " ".join(part.capitalize() for part in name.split("-") if part)


def _render_global_skill_markdown(
    *,
    global_skill_name: str,
    description: str,
    runtime_skill_name: str,
    optimized_docstring: str,
    metadata: dict[str, Any],
) -> str:
    trajectory_ids = metadata.get("source_trajectory_ids")
    if not isinstance(trajectory_ids, list):
        trajectory_ids = []
    source_note = ", ".join(str(item) for item in trajectory_ids) or "not recorded"
    body_description = optimized_docstring.strip() or description
    return (
        "---\n"
        f"name: {global_skill_name}\n"
        f"description: {_yaml_double_quoted(description)}\n"
        "---\n\n"
        f"# {_markdown_heading_from_name(global_skill_name)}\n\n"
        f"{body_description.strip()}\n\n"
        "## Workflow\n\n"
        "- Use this global Codex skill as the authoritative workflow instruction.\n"
        f"- Treat the source runtime skill `{runtime_skill_name}` as promotion history, not the runtime owner.\n"
        "- Keep project-local runtime skills as thin adapters only when a project needs explicit routing.\n\n"
        "## Provenance\n\n"
        f"- source runtime skill: `{runtime_skill_name}`\n"
        f"- source trajectories: {source_note}\n"
    )


def _render_global_skill_openai_yaml(global_skill_name: str, description: str) -> str:
    return (
        "interface:\n"
        f"  display_name: {_yaml_double_quoted(_markdown_heading_from_name(global_skill_name))}\n"
        f"  short_description: {_yaml_double_quoted(description)}\n"
        f"  default_prompt: {_yaml_double_quoted(f'Use ${global_skill_name} for this workflow.')}\n"
    )
