import json
import re
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from skill_runtime.api.models import Trajectory, TrajectoryStep


class TrajectoryCaptureError(ValueError):
    pass


class TrajectoryCapture:
    TASK_DESCRIPTION_KEYS = ("task_description", "task", "goal")
    STEP_LIST_KEYS = ("steps", "actions", "events", "records", "entries", "logs", "tool_calls")
    TOOL_NAME_KEYS = ("tool_name", "tool", "action", "name")
    TOOL_INPUT_KEYS = ("tool_input", "input", "args", "params")
    OBSERVATION_KEYS = ("observation", "result", "output", "note")
    STATUS_KEYS = ("status", "state")
    ARTIFACT_KEYS = ("artifacts", "outputs", "files")

    def __init__(self, output_dir: str | Path) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def capture(
        self,
        source_path: str | Path,
        task_id: str | None = None,
        session_id: str | None = None,
    ) -> tuple[Trajectory, Path]:
        source_ref = Path(source_path)
        if not source_ref.exists():
            raise FileNotFoundError(f"observed task file not found: {source_ref}")

        payload = json.loads(source_ref.read_text(encoding="utf-8"))
        trajectory = self._to_trajectory(payload, task_id=task_id, session_id=session_id)
        output_path = self.output_dir / f"{trajectory.task_id}.json"
        output_path.write_text(
            json.dumps(asdict(trajectory), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return trajectory, output_path

    def _to_trajectory(
        self,
        payload: dict[str, Any],
        task_id: str | None = None,
        session_id: str | None = None,
    ) -> Trajectory:
        task_description = str(self._pick(payload, self.TASK_DESCRIPTION_KEYS, "")).strip()
        if not task_description:
            raise TrajectoryCaptureError("task_description cannot be empty")

        observed_steps = self._pick(payload, self.STEP_LIST_KEYS)
        if not isinstance(observed_steps, list) or not observed_steps:
            raise TrajectoryCaptureError("steps must be a non-empty list")

        now = datetime.now(timezone.utc).isoformat()
        started_at = payload.get("started_at") or now
        ended_at = payload.get("ended_at") or now
        final_status = payload.get("final_status") or "success"
        if final_status not in {"success", "failed", "partial"}:
            raise TrajectoryCaptureError("final_status must be success, failed, or partial")

        resolved_task_id = task_id or payload.get("task_id") or self._derive_task_id(task_description)
        resolved_session_id = session_id or payload.get("session_id") or f"capture_{resolved_task_id}"

        steps: list[TrajectoryStep] = []
        collected_artifacts: list[str] = []
        for index, step in enumerate(observed_steps, start=1):
            if not isinstance(step, dict):
                raise TrajectoryCaptureError(f"step {index} must be an object")

            tool_name = self._extract_tool_name(step)
            if not tool_name:
                raise TrajectoryCaptureError(f"step {index}: tool_name cannot be empty")

            tool_input = self._extract_tool_input(step)
            if tool_input is None:
                tool_input = {}
            if not isinstance(tool_input, dict):
                raise TrajectoryCaptureError(f"step {index}: tool_input must be a dict")

            observation = self._extract_observation(step)
            if not observation:
                raise TrajectoryCaptureError(f"step {index}: observation cannot be empty")

            status = self._extract_status(step) or "success"
            if status not in {"success", "failed", "partial"}:
                raise TrajectoryCaptureError(
                    f"step {index}: status must be success, failed, or partial"
                )

            collected_artifacts.extend(self._extract_step_artifacts(step))
            steps.append(
                TrajectoryStep(
                    step_id=str(step.get("step_id") or index),
                    tool_name=tool_name,
                    tool_input=tool_input,
                    observation=observation,
                    status=status,
                    thought_summary=step.get("thought_summary") or step.get("thought"),
                )
            )

        artifacts = self._pick(payload, self.ARTIFACT_KEYS, [])
        if artifacts is None:
            artifacts = []
        if not artifacts and collected_artifacts:
            artifacts = collected_artifacts
        if not isinstance(artifacts, list):
            raise TrajectoryCaptureError("artifacts must be a list")

        return Trajectory(
            task_id=resolved_task_id,
            session_id=resolved_session_id,
            task_description=task_description,
            steps=steps,
            final_status=final_status,
            artifacts=[str(item) for item in artifacts],
            started_at=str(started_at),
            ended_at=str(ended_at),
        )

    def _derive_task_id(self, task_description: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "_", task_description.lower()).strip("_")
        if not slug:
            slug = "captured_task"
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        return f"{slug[:48]}_{stamp}"

    def _pick(
        self,
        payload: dict[str, Any],
        keys: tuple[str, ...],
        default: Any = None,
    ) -> Any:
        for key in keys:
            if key in payload:
                return payload[key]
        return default

    def _extract_tool_name(self, step: dict[str, Any]) -> str:
        value = self._pick(step, self.TOOL_NAME_KEYS, "")
        if isinstance(value, dict):
            nested = self._pick(value, ("name", "tool_name", "tool", "action"), "")
            return str(nested).strip()
        if isinstance(step.get("call"), dict):
            nested = self._pick(step["call"], ("name", "tool_name", "tool", "action"), "")
            return str(nested).strip()
        return str(value).strip()

    def _extract_tool_input(self, step: dict[str, Any]) -> dict[str, Any]:
        value = self._pick(step, self.TOOL_INPUT_KEYS)
        if isinstance(value, dict):
            return value

        nested_tool = step.get("tool")
        if isinstance(nested_tool, dict):
            nested_input = self._pick(nested_tool, ("input", "args", "params", "arguments"), {})
            if isinstance(nested_input, dict):
                return nested_input

        if isinstance(step.get("call"), dict):
            nested_input = self._pick(step["call"], ("input", "args", "params", "arguments"), {})
            if isinstance(nested_input, dict):
                return nested_input

        return {}

    def _extract_observation(self, step: dict[str, Any]) -> str:
        value = self._pick(step, self.OBSERVATION_KEYS, "")
        if isinstance(value, dict):
            nested = self._pick(
                value,
                ("observation", "result", "output", "content", "message", "summary"),
                "",
            )
            return str(nested).strip()

        nested_result = step.get("result")
        if isinstance(nested_result, dict):
            nested = self._pick(
                nested_result,
                ("output", "content", "message", "summary", "note"),
                "",
            )
            return str(nested).strip()

        return str(value).strip()

    def _extract_status(self, step: dict[str, Any]) -> str | None:
        value = self._pick(step, self.STATUS_KEYS)
        if isinstance(value, str):
            return value

        nested_result = step.get("result")
        if isinstance(nested_result, dict):
            nested = self._pick(nested_result, ("status", "state"))
            if isinstance(nested, str):
                return nested
            if "success" in nested_result:
                return "success" if nested_result["success"] else "failed"

        if "success" in step:
            return "success" if step["success"] else "failed"

        return None

    def _extract_step_artifacts(self, step: dict[str, Any]) -> list[str]:
        artifacts = self._pick(step, self.ARTIFACT_KEYS)
        if isinstance(artifacts, list):
            return [str(item) for item in artifacts]

        nested_result = step.get("result")
        if isinstance(nested_result, dict):
            nested_artifacts = self._pick(nested_result, self.ARTIFACT_KEYS)
            if isinstance(nested_artifacts, list):
                return [str(item) for item in nested_artifacts]

        return []
