from __future__ import annotations

from pathlib import Path
from typing import Any

from skill_runtime.api.models import (
    AgentOrchestrationResult,
    AgentTaskRequest,
    LearningDecision,
    ReuseDecision,
)
from skill_runtime.api.service import RuntimeService
from skill_runtime.evolution.candidates import EvolutionCandidateStore
from skill_runtime.retrieval.skill_index import SkillIndex


class AgentOrchestrationService:
    AUTO_EXECUTION_SCORE = 0.85
    HIGH_RISK_LEVELS = {"high", "destructive"}
    SUCCESS_STATUSES = {"completed", "success"}

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()
        self.runtime = RuntimeService(self.root)
        self.index = SkillIndex(self.runtime.index_path)

    def start_task(self, request: AgentTaskRequest) -> AgentOrchestrationResult:
        reuse_decision = self.plan_reuse(request)
        selected_skill_name = reuse_decision.skill_name if reuse_decision.decision == "auto_execute" else None
        selected_skill_args = dict(request.known_inputs) if selected_skill_name else {}
        return AgentOrchestrationResult(
            request=request,
            reuse_decision=reuse_decision,
            learning_decision=None,
            task_classification=None,
            selected_skill_name=selected_skill_name,
            selected_skill_args=selected_skill_args,
            execution_payload=None,
            learning_capture_payload=None,
        )

    def finalize_task(
        self,
        plan: AgentOrchestrationResult,
        execution_payload: dict[str, Any],
    ) -> AgentOrchestrationResult:
        learning_decision = self.plan_learning(plan.request, execution_payload)
        learning_capture_payload = self._capture_learning_trajectory(
            plan.request,
            execution_payload,
            learning_decision,
        )
        learning_capture_payload = self._attach_evolution_candidate(
            plan.request,
            execution_payload,
            learning_decision,
            learning_capture_payload,
        )
        return AgentOrchestrationResult(
            request=plan.request,
            reuse_decision=plan.reuse_decision,
            learning_decision=learning_decision,
            task_classification=plan.task_classification,
            selected_skill_name=plan.selected_skill_name,
            selected_skill_args=dict(plan.selected_skill_args),
            execution_payload=execution_payload,
            learning_capture_payload=learning_capture_payload,
        )

    def run_task(self, request: AgentTaskRequest) -> AgentOrchestrationResult:
        plan = self.start_task(request)
        if plan.reuse_decision.decision != "auto_execute" or not plan.selected_skill_name:
            return plan

        execution_payload = self.runtime.execute(plan.selected_skill_name, dict(plan.selected_skill_args))
        return self.finalize_task(plan, execution_payload)

    def plan_reuse(self, request: AgentTaskRequest) -> ReuseDecision:
        if not request.allow_silent_reuse:
            return ReuseDecision("skip", "silent reuse is disabled for this request")
        if request.task_kind != "workflow":
            return ReuseDecision("skip", "task kind is not workflow-like enough for silent reuse")
        if request.risk_level in self.HIGH_RISK_LEVELS:
            return ReuseDecision("skip", "task risk is too high for silent reuse")

        search_payload = self.runtime.search(request.task_description, top_k=5)
        results = search_payload.get("results") or []
        if not results:
            return ReuseDecision(
                "skip",
                "no reusable skill matched the task strongly enough",
                search_query=request.task_description,
            )

        top_result = results[0]
        score = float(top_result.get("score", 0.0))
        skill_name = top_result.get("skill_name")
        if not isinstance(skill_name, str):
            return ReuseDecision("skip", "top search result did not include a valid skill name")
        if score < self.runtime.RECOMMENDED_EXECUTION_SCORE:
            return ReuseDecision(
                "skip",
                "top match is below the reusable recommendation threshold",
                skill_name=skill_name,
                search_query=request.task_description,
                search_score=score,
            )

        metadata = self.index.get(skill_name)
        missing_inputs = self._missing_required_inputs(metadata.input_schema if metadata else {}, request.known_inputs)
        if (
            score >= self.AUTO_EXECUTION_SCORE
            and not missing_inputs
            and self._scope_is_compatible(metadata.scope_policy if metadata else None, request)
        ):
            return ReuseDecision(
                "auto_execute",
                "strong reusable match with complete known inputs",
                skill_name=skill_name,
                search_query=request.task_description,
                search_score=score,
            )

        return ReuseDecision(
            "background_hint",
            "a plausible reusable match exists, but the agent should keep solving normally",
            skill_name=skill_name,
            search_query=request.task_description,
            search_score=score,
            missing_inputs=missing_inputs,
        )

    def plan_learning(self, request: AgentTaskRequest, execution_payload: dict[str, Any]) -> LearningDecision:
        if not request.allow_learning:
            return LearningDecision("skip", "learning is disabled for this request")
        if request.task_kind != "workflow":
            return LearningDecision("skip", "task kind is not suitable for automatic distillation")

        status = str((execution_payload.get("result") or {}).get("status", "")).lower()
        if status not in self.SUCCESS_STATUSES:
            return LearningDecision("skip", "task did not complete successfully")

        improvement_signal = self._skill_improvement_signal(request, execution_payload)
        if execution_payload.get("skill_name") and improvement_signal is not None:
            return LearningDecision(
                "improve_existing_skill_candidate",
                improvement_signal["reason"],
                related_skill_name=improvement_signal["target_skill_name"],
                should_capture_trajectory=True,
                should_distill_now=False,
            )
        if execution_payload.get("skill_name"):
            return LearningDecision("skip", "existing skill reuse already solved the task cleanly")

        operation_log = execution_payload.get("operation_log")
        if not isinstance(operation_log, list) or not operation_log:
            return LearningDecision(
                "observed_only",
                "task succeeded, but there is not enough structured execution history to distill now",
                should_capture_trajectory=True,
                should_distill_now=False,
            )
        if request.risk_level in self.HIGH_RISK_LEVELS:
            return LearningDecision(
                "observed_only",
                "task succeeded, but the risk level is too high for immediate automatic distillation",
                should_capture_trajectory=True,
                should_distill_now=False,
            )
        if improvement_signal is not None:
            return LearningDecision(
                "improve_existing_skill_candidate",
                improvement_signal["reason"],
                related_skill_name=improvement_signal["target_skill_name"],
                should_capture_trajectory=True,
                should_distill_now=False,
            )
        if not request.expected_outputs:
            return LearningDecision(
                "observed_only",
                "task succeeded, but expected outputs are not stable enough for immediate distillation",
                should_capture_trajectory=True,
                should_distill_now=False,
            )

        return LearningDecision(
            "new_skill_candidate",
            "task succeeded with a concrete under-covered workflow pattern",
            should_capture_trajectory=True,
            should_distill_now=True,
        )

    def _capture_learning_trajectory(
        self,
        request: AgentTaskRequest,
        execution_payload: dict[str, Any],
        learning_decision: LearningDecision,
    ) -> dict[str, Any] | None:
        if not learning_decision.should_capture_trajectory:
            return None
        observed_task = self._build_observed_task_payload(request, execution_payload)
        if observed_task is None:
            return None
        return self.runtime.capture_trajectory(observed_task=observed_task)

    def _attach_evolution_candidate(
        self,
        request: AgentTaskRequest,
        execution_payload: dict[str, Any],
        learning_decision: LearningDecision,
        learning_capture_payload: dict[str, Any] | None,
    ) -> dict[str, Any] | None:
        if learning_decision.decision != "improve_existing_skill_candidate":
            return learning_capture_payload
        signal = self._skill_improvement_signal(request, execution_payload)
        if signal is None:
            return learning_capture_payload
        trajectory_path = None
        if isinstance(learning_capture_payload, dict):
            raw_path = learning_capture_payload.get("trajectory_path")
            if isinstance(raw_path, str):
                trajectory_path = raw_path
        candidate = EvolutionCandidateStore(self.root).create_candidate(
            target_skill_name=signal["target_skill_name"],
            source_task_description=request.task_description,
            reason=signal["reason"],
            evidence=signal["evidence"],
            proposed_changes=signal["proposed_changes"],
            source_trajectory_path=trajectory_path,
            risk_level=request.risk_level,
            change_type=signal["change_type"],
        )
        payload = dict(learning_capture_payload or {})
        payload["evolution_candidate"] = candidate
        payload["evolution_candidate_path"] = candidate["candidate_path"]
        payload["recommended_next_action"] = "review_evolution_candidate"
        payload["available_host_operations"] = [
            {
                "type": "manual_review",
                "tool_name": "review_evolution_candidate",
                "display_label": "Review skill evolution candidate",
                "effect_summary": "Review the proposed existing-skill improvement before editing any global skill.",
                "risk_level": "low",
                "requires_confirmation": True,
            }
        ]
        return payload

    def _build_observed_task_payload(
        self,
        request: AgentTaskRequest,
        execution_payload: dict[str, Any],
    ) -> dict[str, Any] | None:
        operation_log = execution_payload.get("operation_log")
        if not isinstance(operation_log, list) or not operation_log:
            return None

        actions: list[dict[str, Any]] = []
        for entry in operation_log:
            if not isinstance(entry, dict):
                continue
            tool_name = entry.get("tool_name")
            if not isinstance(tool_name, str) or not tool_name.strip():
                continue
            actions.append(
                {
                    "tool_name": tool_name,
                    "tool_input": self._extract_tool_input(entry),
                    "observation": self._entry_observation(entry),
                    "status": self._entry_status(entry),
                }
            )

        if not actions:
            return None

        result = execution_payload.get("result")
        artifacts = result.get("artifacts") if isinstance(result, dict) else []
        if not isinstance(artifacts, list):
            artifacts = []

        final_status = "success"
        if isinstance(result, dict):
            raw_status = str(result.get("status", "")).lower()
            if raw_status in {"failed", "error"}:
                final_status = "failed"
            elif raw_status == "partial":
                final_status = "partial"

        return {
            "task_description": request.task_description,
            "skill_args": dict(request.known_inputs),
            "actions": actions,
            "artifacts": [str(item) for item in artifacts],
            "final_status": final_status,
        }

    def _extract_tool_input(self, entry: dict[str, Any]) -> dict[str, Any]:
        if isinstance(entry.get("tool_input"), dict):
            return dict(entry["tool_input"])
        if isinstance(entry.get("arguments"), dict):
            return dict(entry["arguments"])

        ignored_keys = {
            "tool_name",
            "status",
            "observation",
            "message",
            "rollback_hint",
            "operation_id",
            "timestamp",
        }
        payload: dict[str, Any] = {}
        for key, value in entry.items():
            if key in ignored_keys:
                continue
            if isinstance(value, (str, int, float, bool)) or value is None:
                payload[key] = value
            elif isinstance(value, list) and all(isinstance(item, (str, int, float, bool)) for item in value):
                payload[key] = list(value)
        return payload

    def _entry_observation(self, entry: dict[str, Any]) -> str:
        for key in ("observation", "message"):
            value = entry.get(key)
            if isinstance(value, str) and value.strip():
                return value
        tool_name = str(entry.get("tool_name", "tool"))
        status = str(entry.get("status", "success"))
        path = entry.get("path")
        if isinstance(path, str) and path.strip():
            return f"{tool_name} {status}: {path}"
        return f"{tool_name} {status}"

    def _entry_status(self, entry: dict[str, Any]) -> str:
        value = str(entry.get("status", "success")).lower()
        if value in self.SUCCESS_STATUSES:
            return "success"
        if value in {"failed", "error"}:
            return "failed"
        if value == "partial":
            return "partial"
        return "success"

    def _skill_improvement_signal(
        self,
        request: AgentTaskRequest,
        execution_payload: dict[str, Any],
    ) -> dict[str, Any] | None:
        raw_signal = self._raw_skill_improvement_signal(execution_payload)
        if raw_signal is None:
            return None

        target_skill_name = self._signal_string(raw_signal, "target_skill_name", "related_skill_name", "skill_name")
        if not target_skill_name:
            target_skill_name = self._matched_related_skill_name(request)
        if not target_skill_name:
            return None

        reason = self._signal_string(raw_signal, "reason", "gap", "summary")
        if not reason:
            reason = f"successful task revealed an improvement opportunity for {target_skill_name}"
        evidence = self._signal_list(raw_signal, "evidence", "observed_gaps", "examples")
        proposed_changes = self._signal_list(raw_signal, "proposed_changes", "changes", "recommendations")
        change_type = self._signal_string(raw_signal, "change_type", "gap_type", "improvement_type")
        return {
            "target_skill_name": target_skill_name,
            "reason": reason,
            "evidence": evidence,
            "proposed_changes": proposed_changes,
            "change_type": change_type or "workflow_rule",
        }

    def _raw_skill_improvement_signal(self, execution_payload: dict[str, Any]) -> dict[str, Any] | None:
        for key in ("skill_gap", "skill_improvement", "evolution_candidate"):
            value = execution_payload.get(key)
            if isinstance(value, dict):
                return value
        result = execution_payload.get("result")
        if isinstance(result, dict):
            for key in ("skill_gap", "skill_improvement", "evolution_candidate"):
                value = result.get(key)
                if isinstance(value, dict):
                    return value
        return None

    def _matched_related_skill_name(self, request: AgentTaskRequest) -> str | None:
        try:
            results = self.runtime.search(request.task_description, top_k=1).get("results") or []
        except Exception:
            return None
        if not results:
            return None
        top_result = results[0]
        score = float(top_result.get("score", 0.0))
        skill_name = top_result.get("skill_name")
        if score < 0.55 or not isinstance(skill_name, str):
            return None
        return skill_name

    def _signal_string(self, signal: dict[str, Any], *keys: str) -> str:
        for key in keys:
            value = signal.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return ""

    def _signal_list(self, signal: dict[str, Any], *keys: str) -> list[str]:
        for key in keys:
            value = signal.get(key)
            if isinstance(value, list):
                return [str(item).strip() for item in value if str(item).strip()]
            if isinstance(value, str) and value.strip():
                return [value.strip()]
        return []

    def _missing_required_inputs(self, input_schema: dict[str, Any], known_inputs: dict[str, Any]) -> list[str]:
        required = input_schema.get("required", [])
        if isinstance(required, list) and required:
            required_fields = [field_name for field_name in required if isinstance(field_name, str)]
        elif input_schema and all(isinstance(key, str) for key in input_schema):
            required_fields = [field_name for field_name in input_schema.keys() if field_name != "required"]
        else:
            required_fields = []
        missing: list[str] = []
        for field_name in required_fields:
            value = known_inputs.get(field_name)
            if value is None or (isinstance(value, str) and not value.strip()):
                missing.append(field_name)
        return missing

    def _scope_is_compatible(self, scope_policy: dict[str, Any] | None, request: AgentTaskRequest) -> bool:
        if not scope_policy or not request.working_directory:
            return True
        allowed_roots = scope_policy.get("allowed_roots")
        if not isinstance(allowed_roots, list) or not allowed_roots:
            return True
        working_directory = Path(request.working_directory).resolve()
        for raw_root in allowed_roots:
            if not isinstance(raw_root, str) or not raw_root.strip():
                continue
            candidate = Path(raw_root)
            candidate_root = (self.root / candidate).resolve() if not candidate.is_absolute() else candidate.resolve()
            try:
                working_directory.relative_to(candidate_root)
                return True
            except ValueError:
                continue
        return False
