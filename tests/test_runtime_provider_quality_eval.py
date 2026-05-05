import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from tests.runtime_test_support import ROOT
from skill_runtime.distill.fallback.service import FallbackService
from skill_runtime.memory.trajectory_store import TrajectoryStore


class RuntimeProviderQualityEvalTestsMixin:
    def test_fallback_service_includes_provider_guidance_in_request_artifact(self) -> None:
        artifact_dir = self.runtime_root / "skill_store" / "staging"
        trajectory = TrajectoryStore(self.service.trajectories_dir).load_file(
            self.service.capture_trajectory(
                observed_task={
                    "task": "Convert pull request review comments into a grouped maintainer cleanup plan.",
                    "actions": [
                        {
                            "tool": "read_json",
                            "input": {"path": "demo/maintainer_review_cleanup/review_comments.json"},
                            "result": "Read review comments.",
                        },
                        {
                            "tool": "write_text",
                            "input": {"path": "demo/maintainer_review_cleanup/generated_cleanup_plan.md"},
                            "result": "Wrote the cleanup plan.",
                        },
                    ],
                    "outputs": ["demo/maintainer_review_cleanup/generated_cleanup_plan.md"],
                },
                task_id="provider_quality_guidance_request",
                session_id="provider_quality_eval_tests",
            )["trajectory_path"]
        )
        _, _, artifact_path = FallbackService(artifact_dir).generate(
            "provider_quality_guidance_request",
            "Read review comments and write a grouped maintainer cleanup plan.",
            (
                "功能描述:\n"
                "    Read review comments and write a grouped maintainer cleanup plan.\n\n"
                "输入参数:\n"
                "    - input_path: str\n"
                "    - output_path: str\n"
                "    - metadata_path: str\n\n"
                "输出结果:\n"
                "    - status: str\n"
                "    - artifacts: list[str]\n"
                "    - steps_executed: int"
            ),
            trajectory,
            {
                "input_path": "str",
                "output_path": "str",
                "metadata_path": "str",
            },
        )
        artifact = self._read_json_file(Path(artifact_path))
        guidance = artifact["request"]["provider_guidance"]
        prompt = artifact["request"]["prompt"]

        self.assertIn("Generate executable workflow code", guidance)
        self.assertIn("not a template summary", guidance)
        self.assertIn("tools.read_json", guidance)
        self.assertIn("tools.write_text", guidance)
        self.assertIn("tools.write_json", guidance)
        self.assertIn("Parameterize input/output paths through kwargs", guidance)
        self.assertIn("Avoid hardcoding demo artifact names", guidance)
        self.assertIn("write a cleanup plan artifact", guidance)
        self.assertIn("rather than modifying source code", guidance)
        self.assertIn("Do not auto-resolve review comments", guidance)
        self.assertIn("Do not infer merge approval", guidance)
        self.assertIn("Do not bypass maintainer judgment", guidance)
        self.assertIn("Provider guidance:", prompt)
        self.assertIn(guidance, prompt)

    def test_single_file_copy_rule_still_matches_pure_copy_workflow(self) -> None:
        capture = self.service.capture_trajectory(
            observed_task={
                "task": "Copy one text file into a new output file.",
                "actions": [
                    {
                        "tool": "copy_file",
                        "input": {
                            "source_file": "demo/input/a.txt",
                            "destination_file": "demo/output/copied_a.txt",
                        },
                        "result": "Copied the source file.",
                    }
                ],
                "outputs": ["demo/output/copied_a.txt"],
            },
            task_id="provider_quality_pure_copy",
            session_id="provider_quality_eval_tests",
        )
        distill = self.service.distill(capture["trajectory_path"], skill_name="provider_quality_pure_copy_test")
        metadata = self._read_json_file(Path(distill["metadata_file"]))

        self.assertEqual("single_file_copy", metadata["rule_name"])
        self.assertNotIn("fallback_artifact", distill)

    def test_single_file_copy_rule_does_not_match_copy_plus_write_json_workflow(self) -> None:
        capture = self.service.capture_trajectory(
            observed_task={
                "task": "Copy one file and write a metadata sidecar for provider quality evaluation.",
                "actions": [
                    {
                        "tool": "copy_file",
                        "input": {
                            "source_path": "demo/input/provider_quality_source.txt",
                            "target_path": "demo/output/provider_quality_result.txt",
                        },
                        "result": "Copied the source file into the output directory.",
                    },
                    {
                        "tool": "write_json",
                        "input": {
                            "path": "demo/output/provider_quality_result.json",
                            "payload": {"source": "demo/input/provider_quality_source.txt"},
                        },
                        "result": "Wrote a JSON metadata sidecar.",
                    },
                ],
                "outputs": [
                    "demo/output/provider_quality_result.txt",
                    "demo/output/provider_quality_result.json",
                ],
            },
            task_id="provider_quality_copy_plus_json",
            session_id="provider_quality_eval_tests",
        )
        distill = self.service.distill(capture["trajectory_path"], skill_name="provider_quality_copy_plus_json_test")
        metadata = self._read_json_file(Path(distill["metadata_file"]))

        self.assertNotEqual("single_file_copy", metadata["rule_name"])
        self.assertIn("fallback_artifact", distill)

    def test_fallback_generated_metadata_schema_aligns_with_candidate_kwargs(self) -> None:
        fallback_provider = ROOT / "examples" / "providers" / "copy_metadata_fallback_provider.py"
        original_fallback = os.environ.get("SKILL_RUNTIME_FALLBACK_PROVIDER_CMD")
        os.environ["SKILL_RUNTIME_FALLBACK_PROVIDER_CMD"] = json.dumps(
            [sys.executable, str(fallback_provider)]
        )
        self.addCleanup(self._restore_env, "SKILL_RUNTIME_FALLBACK_PROVIDER_CMD", original_fallback)

        capture = self.service.capture_trajectory(
            observed_task={
                "task": "Copy one file and write a metadata sidecar for provider quality evaluation.",
                "actions": [
                    {
                        "tool": "copy_file",
                        "input": {
                            "source_path": "demo/input/provider_quality_source.txt",
                            "target_path": "demo/output/provider_quality_result.txt",
                        },
                        "result": "Copied the source file into the output directory.",
                    },
                    {
                        "tool": "write_json",
                        "input": {
                            "path": "demo/output/provider_quality_result.json",
                            "payload": {"source": "demo/input/provider_quality_source.txt"},
                        },
                        "result": "Wrote a JSON metadata sidecar.",
                    },
                ],
                "outputs": [
                    "demo/output/provider_quality_result.txt",
                    "demo/output/provider_quality_result.json",
                ],
            },
            task_id="provider_quality_fallback_schema_alignment",
            session_id="provider_quality_eval_tests",
        )
        distill = self.service.distill(capture["trajectory_path"], skill_name="provider_quality_schema_alignment")
        metadata = self._read_json_file(Path(distill["metadata_file"]))

        self.assertEqual("llm_fallback", metadata["rule_name"])
        self.assertEqual(
            ["input_path", "metadata_path", "output_path"],
            sorted(metadata["input_schema"].keys()),
        )
        self.assertEqual("fallback_candidate_kwargs", metadata["schema_source"])
        self.assertNotIn("payload", metadata["input_schema"])

    def test_provider_quality_evaluation_script_reports_fixture_outcomes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "evaluate_provider_quality.py")],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=str(ROOT),
            timeout=120,
            check=False,
        )

        self.assertEqual(0, result.returncode, msg=result.stderr or result.stdout)
        payload = json.loads(result.stdout)
        self.assertEqual("ok", payload["status"])
        fixtures = {item["fixture_name"]: item for item in payload["fixtures"]}
        for fixture in fixtures.values():
            self.assertIn("lifecycle_mode", fixture)
            self.assertIn("loop_stage", fixture)
            self.assertIn("staging_file", fixture)
            self.assertIn("generated_candidate_provider", fixture)
            self.assertIn("inferred_or_used_input_schema", fixture)
            self.assertIn("declared_input_schema_keys", fixture)
            self.assertIn("execution_arg_keys", fixture)
            self.assertIn("candidate_kwargs_keys", fixture)
            self.assertIn("schema_execution_arg_mismatch", fixture)
            self.assertIn("expected_artifacts", fixture)
            self.assertIn("produced_artifacts", fixture)
            self.assertIn("missing_artifacts", fixture)

        self.assertIn("demo_local_success", fixtures)
        self.assertIn("lifecycle_mode", fixtures["demo_local_success"])
        self.assertIn("loop_stage", fixtures["demo_local_success"])
        self.assertEqual("manual_provider_loop", fixtures["demo_local_success"]["lifecycle_mode"])
        self.assertEqual("passed", fixtures["demo_local_success"]["generated_candidate_status"])
        self.assertEqual("passed", fixtures["demo_local_success"]["audit_status"])
        self.assertEqual("passed", fixtures["demo_local_success"]["execution_smoke_status"])
        self.assertEqual("execution_passed", fixtures["demo_local_success"]["loop_stage"])

        self.assertIn("mock_template_execute_failure", fixtures)
        self.assertIn("lifecycle_mode", fixtures["mock_template_execute_failure"])
        self.assertIn("loop_stage", fixtures["mock_template_execute_failure"])
        self.assertEqual("manual_provider_loop", fixtures["mock_template_execute_failure"]["lifecycle_mode"])
        self.assertEqual("passed", fixtures["mock_template_execute_failure"]["generated_candidate_status"])
        self.assertEqual("needs_fix", fixtures["mock_template_execute_failure"]["audit_status"])
        self.assertEqual("skipped", fixtures["mock_template_execute_failure"]["execution_smoke_status"])
        self.assertEqual("audit_failed", fixtures["mock_template_execute_failure"]["loop_stage"])
        self.assertTrue(fixtures["mock_template_execute_failure"]["failure_reason"])

        self.assertIn("fake_deepseek_repair_success", fixtures)
        self.assertEqual("manual_provider_loop", fixtures["fake_deepseek_repair_success"]["lifecycle_mode"])
        self.assertEqual("passed", fixtures["fake_deepseek_repair_success"]["generated_candidate_status"])
        self.assertTrue(fixtures["fake_deepseek_repair_success"]["repair_attempted"])
        self.assertEqual("attempted", fixtures["fake_deepseek_repair_success"]["repair_status"])
        self.assertEqual("execution_passed", fixtures["fake_deepseek_repair_success"]["loop_stage"])

        self.assertIn("fake_deepseek_semantic_block", fixtures)
        self.assertEqual("manual_provider_loop", fixtures["fake_deepseek_semantic_block"]["lifecycle_mode"])
        self.assertEqual("needs_fix", fixtures["fake_deepseek_semantic_block"]["audit_status"])
        self.assertEqual("skipped", fixtures["fake_deepseek_semantic_block"]["execution_smoke_status"])
        self.assertEqual("audit_failed", fixtures["fake_deepseek_semantic_block"]["loop_stage"])
        self.assertTrue(fixtures["fake_deepseek_semantic_block"]["failure_reason"])

        self.assertIn("fake_deepseek_generation_failure", fixtures)
        self.assertEqual("manual_provider_loop", fixtures["fake_deepseek_generation_failure"]["lifecycle_mode"])
        self.assertEqual("failed", fixtures["fake_deepseek_generation_failure"]["generated_candidate_status"])
        self.assertEqual("skipped", fixtures["fake_deepseek_generation_failure"]["audit_status"])
        self.assertEqual("skipped", fixtures["fake_deepseek_generation_failure"]["execution_smoke_status"])
        self.assertEqual("generation_failed", fixtures["fake_deepseek_generation_failure"]["loop_stage"])
        self.assertTrue(fixtures["fake_deepseek_generation_failure"]["failure_reason"])

        self.assertIn("review_cleanup_provider_quality", fixtures)
        self.assertEqual("manual_provider_loop", fixtures["review_cleanup_provider_quality"]["lifecycle_mode"])
        self.assertIn("loop_stage", fixtures["review_cleanup_provider_quality"])
        self.assertEqual("audit_failed", fixtures["review_cleanup_provider_quality"]["loop_stage"])
        self.assertTrue(
            isinstance(fixtures["review_cleanup_provider_quality"]["repair_attempted"], bool)
        )
        self.assertTrue(fixtures["review_cleanup_provider_quality"]["failure_reason"])

        self.assertIn("review_cleanup_demo_provider_success", fixtures)
        review_cleanup_success = fixtures["review_cleanup_demo_provider_success"]
        self.assertEqual("manual_provider_loop", review_cleanup_success["lifecycle_mode"])
        self.assertEqual(
            "local_review_cleanup_fallback_provider",
            review_cleanup_success["generated_candidate_provider"],
        )
        self.assertEqual("passed", review_cleanup_success["generated_candidate_status"])
        self.assertEqual("passed", review_cleanup_success["audit_status"])
        self.assertEqual("passed", review_cleanup_success["execution_smoke_status"])
        self.assertEqual("execution_passed", review_cleanup_success["loop_stage"])
        self.assertIsNone(review_cleanup_success["failure_reason"])
        self.assertIn(
            "demo/maintainer_review_cleanup/generated_cleanup_plan.md",
            review_cleanup_success["produced_artifacts"],
        )

        self.assertIn("runtime_service_distill_demo_provider", fixtures)
        self.assertEqual(
            "runtime_service_distill",
            fixtures["runtime_service_distill_demo_provider"]["lifecycle_mode"],
        )
        self.assertIn("loop_stage", fixtures["runtime_service_distill_demo_provider"])
        runtime_service_fixture = fixtures["runtime_service_distill_demo_provider"]
        self.assertNotEqual(
            "deterministic_rule:single_file_copy",
            runtime_service_fixture["generated_candidate_provider"],
        )
        self.assertEqual(
            "local_copy_metadata_fallback_provider",
            runtime_service_fixture["generated_candidate_provider"],
        )
        self.assertEqual(
            ["input_path", "metadata_path", "output_path"],
            runtime_service_fixture["declared_input_schema_keys"],
        )
        self.assertIn("metadata_path", runtime_service_fixture["execution_arg_keys"])
        self.assertIn("metadata_path", runtime_service_fixture["candidate_kwargs_keys"])
        self.assertEqual(
            [],
            runtime_service_fixture["schema_execution_arg_mismatch"]["schema_not_in_execution_args"],
        )
        self.assertEqual(
            [],
            runtime_service_fixture["schema_execution_arg_mismatch"]["execution_args_not_in_schema"],
        )
        self.assertEqual(
            [],
            runtime_service_fixture["schema_execution_arg_mismatch"]["candidate_kwargs_not_in_schema"],
        )
        if runtime_service_fixture["failure_reason"]:
            self.assertTrue(runtime_service_fixture["failure_reason"])
            if runtime_service_fixture["loop_stage"] == "execution_failed":
                self.assertTrue(runtime_service_fixture["missing_artifacts"])
            else:
                self.assertTrue(runtime_service_fixture["failure_reason"])
        else:
            self.assertEqual("passed", runtime_service_fixture["generated_candidate_status"])
            self.assertEqual("passed", runtime_service_fixture["audit_status"])
            self.assertEqual("passed", runtime_service_fixture["execution_smoke_status"])
            self.assertEqual("execution_passed", runtime_service_fixture["loop_stage"])

    def test_provider_quality_evaluation_script_writes_output_file(self) -> None:
        with tempfile.TemporaryDirectory(prefix="provider-quality-eval-") as temp_dir:
            output_path = Path(temp_dir) / "provider-quality-report.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "evaluate_provider_quality.py"),
                    "--output",
                    str(output_path),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                cwd=str(ROOT),
                timeout=120,
                check=False,
            )

            self.assertEqual(0, result.returncode, msg=result.stderr or result.stdout)
            stdout_payload = json.loads(result.stdout)
            self.assertTrue(output_path.exists())
            file_payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(stdout_payload, file_payload)

    def test_provider_quality_evaluation_script_compares_machine_readable_baseline(self) -> None:
        baseline_path = ROOT / "docs" / "provider-quality-baseline.json"
        baseline_payload = json.loads(baseline_path.read_text(encoding="utf-8"))

        self.assertIn("fixtures", baseline_payload)
        self.assertTrue(baseline_payload["fixtures"])
        for fixture in baseline_payload["fixtures"]:
            self.assertIn("fixture_name", fixture)
            self.assertIn("lifecycle_mode", fixture)
            self.assertIn("expected_loop_stage", fixture)
            self.assertIn("expected_provider", fixture)
            self.assertIn("expected_failure", fixture)

        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "evaluate_provider_quality.py"),
                "--baseline",
                str(baseline_path),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=str(ROOT),
            timeout=120,
            check=False,
        )

        self.assertEqual(0, result.returncode, msg=result.stderr or result.stdout)
        payload = json.loads(result.stdout)
        comparison = payload["baseline_comparison"]
        self.assertEqual(8, len(comparison["matched"]))
        self.assertEqual([], comparison["regressions"])
        self.assertEqual([], comparison["improvements"])
        self.assertEqual([], comparison["unexpected_failures"])
        self.assertEqual([], comparison["unexpected_passes"])
        self.assertEqual([], comparison["missing_fixtures"])
        self.assertEqual([], comparison["extra_fixtures"])

    def test_provider_quality_fail_on_regression_passes_for_current_baseline(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "evaluate_provider_quality.py"),
                "--baseline",
                str(ROOT / "docs" / "provider-quality-baseline.json"),
                "--fail-on-regression",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=str(ROOT),
            timeout=120,
            check=False,
        )

        self.assertEqual(0, result.returncode, msg=result.stderr or result.stdout)

    def test_provider_quality_evaluation_script_detects_bad_baseline(self) -> None:
        with tempfile.TemporaryDirectory(prefix="provider-quality-baseline-") as temp_dir:
            baseline_path = Path(temp_dir) / "bad-baseline.json"
            baseline_path.write_text(
                json.dumps(
                    {
                        "fixtures": [
                            {
                                "fixture_name": "mock_template_execute_failure",
                                "lifecycle_mode": "manual_provider_loop",
                                "expected_loop_stage": "execution_passed",
                                "expected_provider": "mock_fallback_provider",
                                "expected_failure": False,
                            }
                        ]
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "evaluate_provider_quality.py"),
                    "--baseline",
                    str(baseline_path),
                    "--fail-on-regression",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                cwd=str(ROOT),
                timeout=120,
                check=False,
            )

        self.assertNotEqual(0, result.returncode)
        payload = json.loads(result.stdout)
        comparison = payload["baseline_comparison"]
        self.assertEqual([], comparison["matched"])
        self.assertTrue(comparison["unexpected_failures"])
        self.assertTrue(comparison["extra_fixtures"])
