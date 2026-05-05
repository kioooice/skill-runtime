from scripts.evaluate_search_quality import evaluate


class RuntimeSearchQualityTestsMixin:
    def test_active_skill_search_quality_report_contains_required_fields(self) -> None:
        payload = evaluate(self.runtime_root)

        self.assertEqual("ok", payload["status"])
        self.assertTrue(payload["fixture_skills"])
        self.assertTrue(payload["queries"])
        self.assertIn("summary", payload)
        for item in payload["queries"]:
            self.assertIn("query_id", item)
            self.assertIn("query", item)
            self.assertIn("expected_top_skill", item)
            self.assertIn("expected_skills", item)
            self.assertIn("actual_top_skill", item)
            self.assertIn("matched", item)
            self.assertIn("top_k", item)
            self.assertIn("failure_reason", item)
            self.assertIn("rank_diagnostics", item)
            self.assertIn("top_results", item)

    def test_active_skill_search_quality_matches_at_least_one_positive_query(self) -> None:
        payload = evaluate(self.runtime_root)
        positive_queries = [item for item in payload["queries"] if item["expected_top_skill"]]

        self.assertTrue(positive_queries)
        self.assertTrue(any(item["matched"] for item in positive_queries), payload)
        chinese_query = next(item for item in payload["queries"] if item["query_id"] == "chinese_merge_query")
        self.assertTrue(chinese_query["matched"], payload)
        self.assertEqual("merge_text_files", chinese_query["actual_recommended_skill"])

    def test_active_skill_search_quality_negative_query_is_not_fake_pass(self) -> None:
        payload = evaluate(self.runtime_root)
        negative_queries = [
            item
            for item in payload["queries"]
            if item["query_id"] in {"negative_email_newsletter", "negative_chinese_email_campaign"}
        ]

        self.assertEqual(2, len(negative_queries))
        for negative_query in negative_queries:
            self.assertIsNone(negative_query["expected_top_skill"])
            if negative_query["matched"]:
                self.assertIsNone(negative_query["actual_recommended_skill"])
            else:
                self.assertTrue(negative_query["failure_reason"])
