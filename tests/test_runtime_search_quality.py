from scripts.evaluate_search_quality import evaluate


class RuntimeSearchQualityTestsMixin:
    def test_active_skill_search_quality_fixture_passes(self) -> None:
        payload = evaluate(self.runtime_root)

        self.assertTrue(payload["passed"], payload)
        self.assertEqual(payload["total_count"], payload["passed_count"])
