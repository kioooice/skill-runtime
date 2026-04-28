from pathlib import Path

from skill_runtime.memory.trajectory_store import TrajectoryStore
from tests.runtime_test_support import ROOT


class RuntimeIsolationTestsMixin:
    def test_default_runtime_service_uses_isolated_root(self) -> None:
        self.assertNotEqual(ROOT, self.runtime_root)
        self.assertTrue((self.runtime_root / "skill_store" / "active").exists())
        self.assertTrue((self.runtime_root / "observed_tasks").exists())

    def test_default_execute_writes_observed_task_outside_repo_root(self) -> None:
        repo_output = ROOT / "demo" / "output" / "default_root_execute.md"
        repo_observed_before = {path.name for path in (ROOT / "observed_tasks").glob("*.json")}
        self.addCleanup(lambda: repo_output.unlink(missing_ok=True))

        result = self.service.execute(
            "merge_text_files",
            {"input_dir": "demo/input", "output_path": "demo/output/default_root_execute.md"},
        )

        observed_path = Path(result["observed_task_record"])
        self.addCleanup(lambda: observed_path.unlink(missing_ok=True))
        self.addCleanup(lambda: (self.runtime_root / "demo" / "output" / "default_root_execute.md").unlink(missing_ok=True))

        self.assertTrue(str(observed_path).startswith(str(self.runtime_root)))
        self.assertTrue(observed_path.exists())
        self.assertFalse(repo_output.exists())
        repo_observed_after = {path.name for path in (ROOT / "observed_tasks").glob("*.json")}
        self.assertEqual(repo_observed_before, repo_observed_after)

    def test_generate_and_activate_skill_uses_isolated_staging_root(self) -> None:
        trajectory = TrajectoryStore(ROOT / "trajectories").load_file(ROOT / "trajectories" / "demo_merge_text_files.json")
        repo_staging_skill = ROOT / "skill_store" / "staging" / "isolation_generated_skill_test.py"
        repo_staging_metadata = ROOT / "skill_store" / "staging" / "isolation_generated_skill_test.metadata.json"
        repo_active_skill = ROOT / "skill_store" / "active" / "isolation_generated_skill_test.py"
        repo_active_metadata = ROOT / "skill_store" / "active" / "isolation_generated_skill_test.metadata.json"
        repo_staging_skill.unlink(missing_ok=True)
        repo_staging_metadata.unlink(missing_ok=True)
        repo_active_skill.unlink(missing_ok=True)
        repo_active_metadata.unlink(missing_ok=True)

        generated = self._generate_and_activate_skill(
            trajectory,
            skill_name="isolation_generated_skill_test",
        )

        skill_file = Path(generated["skill_file"])
        metadata_file = Path(generated["metadata_file"])
        active_skill = self.runtime_root / "skill_store" / "active" / "isolation_generated_skill_test.py"
        active_metadata = self.runtime_root / "skill_store" / "active" / "isolation_generated_skill_test.metadata.json"

        self.addCleanup(lambda: skill_file.unlink(missing_ok=True))
        self.addCleanup(lambda: metadata_file.unlink(missing_ok=True))
        self.addCleanup(lambda: active_skill.unlink(missing_ok=True))
        self.addCleanup(lambda: active_metadata.unlink(missing_ok=True))
        self.addCleanup(lambda: repo_staging_skill.unlink(missing_ok=True))
        self.addCleanup(lambda: repo_staging_metadata.unlink(missing_ok=True))
        self.addCleanup(lambda: repo_active_skill.unlink(missing_ok=True))
        self.addCleanup(lambda: repo_active_metadata.unlink(missing_ok=True))

        self.assertTrue(str(skill_file).startswith(str(self.runtime_root)))
        self.assertTrue(str(metadata_file).startswith(str(self.runtime_root)))
        self.assertFalse(repo_staging_skill.exists())
        self.assertFalse(repo_staging_metadata.exists())
