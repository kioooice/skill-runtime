import json
from dataclasses import asdict
from pathlib import Path

from skill_runtime.api.models import Trajectory, TrajectoryStep


class TrajectoryValidationError(ValueError):
    pass


class TrajectoryStore:
    def __init__(self, base_dir: str | Path) -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, trajectory: Trajectory) -> Path:
        self._validate_trajectory(trajectory)
        path = self.base_dir / f"{trajectory.task_id}.json"
        path.write_text(
            json.dumps(asdict(trajectory), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return path

    def load(self, task_id: str) -> Trajectory:
        return self.load_file(self.base_dir / f"{task_id}.json")

    def load_file(self, file_path: str | Path) -> Trajectory:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"trajectory file not found: {path}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        return self._from_dict(payload)

    def exists(self, task_id: str) -> bool:
        return (self.base_dir / f"{task_id}.json").exists()

    def list_task_ids(self) -> list[str]:
        return sorted(path.stem for path in self.base_dir.glob("*.json"))

    def register_file(self, file_path: str | Path) -> tuple[Trajectory, Path]:
        trajectory = self.load_file(file_path)
        saved_path = self.save(trajectory)
        return trajectory, saved_path

    def _from_dict(self, payload: dict) -> Trajectory:
        self._validate_payload(payload)
        steps = [
            TrajectoryStep(
                step_id=step["step_id"],
                tool_name=step["tool_name"],
                tool_input=step["tool_input"],
                observation=step["observation"],
                status=step["status"],
                thought_summary=step.get("thought_summary"),
            )
            for step in payload["steps"]
        ]
        return Trajectory(
            task_id=payload["task_id"],
            session_id=payload["session_id"],
            task_description=payload["task_description"],
            steps=steps,
            final_status=payload["final_status"],
            artifacts=payload["artifacts"],
            started_at=payload["started_at"],
            ended_at=payload["ended_at"],
        )

    def _validate_trajectory(self, trajectory: Trajectory) -> None:
        if not trajectory.task_id.strip():
            raise TrajectoryValidationError("task_id cannot be empty")
        if not trajectory.session_id.strip():
            raise TrajectoryValidationError("session_id cannot be empty")
        if not trajectory.task_description.strip():
            raise TrajectoryValidationError("task_description cannot be empty")
        if trajectory.final_status not in {"success", "failed", "partial"}:
            raise TrajectoryValidationError("final_status must be success, failed, or partial")
        if not trajectory.steps:
            raise TrajectoryValidationError("steps cannot be empty")

        for index, step in enumerate(trajectory.steps, start=1):
            if not step.step_id.strip():
                raise TrajectoryValidationError(f"step {index}: step_id cannot be empty")
            if not step.tool_name.strip():
                raise TrajectoryValidationError(f"step {index}: tool_name cannot be empty")
            if not isinstance(step.tool_input, dict):
                raise TrajectoryValidationError(f"step {index}: tool_input must be a dict")
            if step.status not in {"success", "failed", "partial"}:
                raise TrajectoryValidationError(
                    f"step {index}: status must be success, failed, or partial"
                )

    def _validate_payload(self, payload: dict) -> None:
        required_top_level = {
            "task_id",
            "session_id",
            "task_description",
            "steps",
            "final_status",
            "artifacts",
            "started_at",
            "ended_at",
        }
        missing = sorted(required_top_level - set(payload.keys()))
        if missing:
            raise TrajectoryValidationError(f"missing fields: {missing}")

        if not isinstance(payload["steps"], list) or not payload["steps"]:
            raise TrajectoryValidationError("steps must be a non-empty list")

        for index, step in enumerate(payload["steps"], start=1):
            required_step_fields = {
                "step_id",
                "tool_name",
                "tool_input",
                "observation",
                "status",
            }
            missing_step_fields = sorted(required_step_fields - set(step.keys()))
            if missing_step_fields:
                raise TrajectoryValidationError(
                    f"step {index} missing fields: {missing_step_fields}"
                )
