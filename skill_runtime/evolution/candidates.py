from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class EvolutionCandidateStore:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()
        self.candidate_dir = self.root / ".skill_runtime" / "evolution_candidates"

    def create_candidate(
        self,
        *,
        target_skill_name: str,
        source_task_description: str,
        reason: str,
        evidence: list[str] | None = None,
        proposed_changes: list[str] | None = None,
        source_trajectory_path: str | None = None,
        risk_level: str = "medium",
        change_type: str = "workflow_rule",
    ) -> dict[str, Any]:
        self.candidate_dir.mkdir(parents=True, exist_ok=True)
        now = datetime.now(timezone.utc).isoformat()
        candidate_id = self._candidate_id(target_skill_name, source_task_description, now)
        payload = {
            "candidate_id": candidate_id,
            "status": "proposed",
            "target_skill_name": target_skill_name,
            "source_task_description": source_task_description,
            "reason": reason,
            "evidence": [str(item) for item in evidence or [] if str(item).strip()],
            "proposed_changes": [str(item) for item in proposed_changes or [] if str(item).strip()],
            "source_trajectory_path": source_trajectory_path,
            "risk_level": risk_level,
            "change_type": change_type,
            "created_at": now,
            "updated_at": now,
        }
        candidate_path = self.candidate_dir / f"{candidate_id}.json"
        candidate_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return {**payload, "candidate_path": str(candidate_path.resolve())}

    def list_candidates(self, *, limit: int = 50) -> list[dict[str, Any]]:
        if not self.candidate_dir.exists():
            return []
        candidates: list[dict[str, Any]] = []
        for candidate_path in sorted(self.candidate_dir.glob("*.json")):
            try:
                payload = json.loads(candidate_path.read_text(encoding="utf-8-sig"))
            except (json.JSONDecodeError, OSError):
                continue
            if not isinstance(payload, dict):
                continue
            payload["candidate_path"] = str(candidate_path.resolve())
            candidates.append(payload)
        candidates.sort(key=lambda item: str(item.get("created_at") or ""), reverse=True)
        return candidates[: max(1, limit)]

    def load_candidate(self, candidate_ref: str | Path) -> tuple[dict[str, Any], Path]:
        candidate_path = self._resolve_candidate_path(candidate_ref)
        if not candidate_path.exists():
            raise FileNotFoundError(f"evolution candidate not found: {candidate_ref}")
        payload = json.loads(candidate_path.read_text(encoding="utf-8-sig"))
        if not isinstance(payload, dict):
            raise ValueError("evolution candidate must be a JSON object")
        payload["candidate_path"] = str(candidate_path.resolve())
        return payload, candidate_path

    def update_candidate(self, candidate_path: str | Path, updates: dict[str, Any]) -> dict[str, Any]:
        payload, resolved_path = self.load_candidate(candidate_path)
        now = datetime.now(timezone.utc).isoformat()
        payload.update(updates)
        payload["updated_at"] = now
        payload.pop("candidate_path", None)
        resolved_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        payload["candidate_path"] = str(resolved_path.resolve())
        return payload

    def create_review(self, candidate: dict[str, Any], review_payload: dict[str, Any]) -> dict[str, Any]:
        review_dir = self.root / ".skill_runtime" / "evolution_reviews"
        review_dir.mkdir(parents=True, exist_ok=True)
        candidate_id = str(candidate.get("candidate_id") or "evolution_candidate")
        review_path = review_dir / f"{candidate_id}.review.json"
        diff_path = review_dir / f"{candidate_id}.diff"
        payload = dict(review_payload)
        payload["candidate_id"] = candidate_id
        payload["candidate_path"] = candidate.get("candidate_path")
        payload["created_at"] = datetime.now(timezone.utc).isoformat()
        proposed_diff = payload.get("proposed_diff")
        if isinstance(proposed_diff, str) and proposed_diff:
            diff_path.write_text(proposed_diff, encoding="utf-8")
            payload["diff_path"] = str(diff_path.resolve())
        review_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        payload["review_path"] = str(review_path.resolve())
        return payload

    def create_application(self, candidate: dict[str, Any], application_payload: dict[str, Any]) -> dict[str, Any]:
        apply_dir = self.root / ".skill_runtime" / "evolution_applications"
        apply_dir.mkdir(parents=True, exist_ok=True)
        candidate_id = str(candidate.get("candidate_id") or "evolution_candidate")
        apply_path = apply_dir / f"{candidate_id}.apply.json"
        payload = dict(application_payload)
        payload["candidate_id"] = candidate_id
        payload["candidate_path"] = candidate.get("candidate_path")
        payload["created_at"] = datetime.now(timezone.utc).isoformat()
        apply_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        payload["application_path"] = str(apply_path.resolve())
        return payload

    def create_rollback(self, candidate: dict[str, Any], rollback_payload: dict[str, Any]) -> dict[str, Any]:
        rollback_dir = self.root / ".skill_runtime" / "evolution_rollbacks"
        rollback_dir.mkdir(parents=True, exist_ok=True)
        candidate_id = str(candidate.get("candidate_id") or "evolution_candidate")
        rollback_path = rollback_dir / f"{candidate_id}.rollback.json"
        payload = dict(rollback_payload)
        payload["candidate_id"] = candidate_id
        payload["candidate_path"] = candidate.get("candidate_path")
        payload["created_at"] = datetime.now(timezone.utc).isoformat()
        rollback_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        payload["rollback_path"] = str(rollback_path.resolve())
        return payload

    def _candidate_id(self, target_skill_name: str, source_task_description: str, created_at: str) -> str:
        slug_source = f"{target_skill_name} {source_task_description}"
        slug = re.sub(r"[^a-z0-9]+", "_", slug_source.lower()).strip("_")
        if not slug:
            slug = "skill_evolution"
        stamp = datetime.fromisoformat(created_at).strftime("%Y%m%d%H%M%S%f")
        return f"{slug[:56]}_{stamp}"

    def _resolve_candidate_path(self, candidate_ref: str | Path) -> Path:
        raw_path = Path(candidate_ref)
        if raw_path.exists() or raw_path.suffix == ".json":
            return raw_path.resolve()
        return (self.candidate_dir / f"{candidate_ref}.json").resolve()
