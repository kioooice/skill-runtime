# Review Cleanup Plan

Pull request: #58 - Normalize provider quality report schema

## Required Fixes

1. Remove volatile fields from baseline comparison.
   - Source comment: `RC-201`
   - File: `scripts/evaluate_provider_quality.py`
   - Action: normalize or exclude `generated_at` before comparing provider quality output to the checked-in baseline.
   - Verification: re-run the provider-quality evaluator twice and confirm unchanged quality data produces the same comparison result.

2. Add regression coverage for normalized baseline comparison.
   - Source comment: `RC-202`
   - File: `tests/test_runtime_provider_quality_eval.py`
   - Action: test that volatile timestamps are omitted before baseline comparison.
   - Verification: run the focused provider-quality evaluator tests.

## Follow-Up Documentation

1. Document excluded baseline fields.
   - Source comment: `RC-203`
   - File: `docs/provider-quality-baseline.md`
   - Action: mention that volatile run metadata is intentionally excluded from regression comparison.

2. Link the provider-quality baseline from release validation docs.
   - Source comment: `RC-204`
   - File: `README.md`
   - Action: consider adding the baseline doc link near the release validation commands if this PR already touches that area.

## Suggested Verification

```powershell
python -m unittest tests.test_runtime_provider_quality_eval -v
python scripts/evaluate_provider_quality.py --baseline docs/provider-quality-baseline.json --fail-on-regression
git diff --check
```

## Maintainer Decision

Do the two required fixes before merge. The documentation follow-ups can land in the same pull request if the touched files are already open; otherwise, keep them as a follow-up issue. This plan does not apply code changes or mark review comments resolved.
