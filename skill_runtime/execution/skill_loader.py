import importlib.util
from pathlib import Path
from types import ModuleType


class SkillLoadError(ValueError):
    pass


class SkillLoader:
    def load_from_file(self, file_path: str | Path, module_name: str | None = None) -> ModuleType:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"skill file not found: {path}")
        resolved_name = module_name or f"skill_{path.stem}"
        spec = importlib.util.spec_from_file_location(resolved_name, path)
        if spec is None or spec.loader is None:
            raise SkillLoadError(f"failed to create import spec for: {path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def validate_entrypoint(self, module: ModuleType) -> None:
        run_fn = getattr(module, "run", None)
        if run_fn is None or not callable(run_fn):
            raise SkillLoadError("skill module must define callable run(tools, **kwargs)")
