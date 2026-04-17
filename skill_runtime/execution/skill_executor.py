from pathlib import Path
from typing import Any

from skill_runtime.execution.skill_loader import SkillLoader
from skill_runtime.retrieval.skill_index import SkillIndex


class SkillExecutionError(ValueError):
    pass


class SkillExecutor:
    def __init__(self, index: SkillIndex, tools: Any | None = None) -> None:
        self.index = index
        self.tools = tools
        self.loader = SkillLoader()

    def execute(self, skill_name: str, kwargs: dict[str, Any]) -> dict[str, Any]:
        metadata = self.index.get(skill_name)
        if metadata is None:
            raise FileNotFoundError(f"skill not found: {skill_name}")
        if metadata.status != "active":
            raise SkillExecutionError(f"skill is not executable in status={metadata.status}")

        module = self.loader.load_from_file(Path(metadata.file_path), module_name=f"skill_{skill_name}")
        self.loader.validate_entrypoint(module)

        try:
            result = module.run(self.tools, **kwargs)
        except TypeError as exc:
            raise SkillExecutionError(f"skill argument mismatch: {exc}") from exc
        except Exception as exc:
            raise SkillExecutionError(f"skill execution failed: {exc}") from exc

        self.index.record_usage(skill_name)

        if result is None:
            return {"status": "completed"}
        if not isinstance(result, dict):
            return {"status": "completed", "raw_result": result}
        return result
