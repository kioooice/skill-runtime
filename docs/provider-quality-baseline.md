# Provider Quality Baseline

Baseline date: 2026-05-05

## How To Run Evaluation

From the repository root:

```powershell
python scripts/evaluate_provider_quality.py
```

Optional JSON output:

```powershell
python scripts/evaluate_provider_quality.py --output .\provider-quality-report.json
```

The report prints full JSON to stdout. `--output` writes the same JSON to a caller-provided UTF-8 path.

Machine-readable baseline comparison:

```powershell
python scripts/evaluate_provider_quality.py --baseline docs/provider-quality-baseline.json
```

Regression-gated comparison:

```powershell
python scripts/evaluate_provider_quality.py --baseline docs/provider-quality-baseline.json --fail-on-regression
```

`docs/provider-quality-baseline.json` is the machine-readable source for fixture expectations. It records each fixture's `fixture_name`, `lifecycle_mode`, `expected_loop_stage`, `expected_provider`, and `expected_failure`.

When `--baseline` is provided, the script still prints the full evaluation report and adds `baseline_comparison`. The comparison includes matched fixtures, regressions, improvements, unexpected failures, unexpected passes, missing fixtures, and extra fixtures.

`--baseline` alone does not fail the command. `--fail-on-regression` returns non-zero only when the comparison finds a regression, unexpected failure, or missing fixture. Unexpected passes and extra fixtures remain visible but do not fail the command by themselves.

## Fixture Table

| Fixture | Lifecycle mode | Expected loop stage | Expected provider | Expected failure | What it proves |
| --- | --- | --- | --- | --- | --- |
| `demo_local_success` | `manual_provider_loop` | `execution_passed` | `local_copy_metadata_fallback_provider` | No | Local demo fallback plus local semantic pass can produce, audit, and execute a basic governed-learning candidate. |
| `mock_template_execute_failure` | `manual_provider_loop` | `audit_failed` | `mock_fallback_provider` | Yes | The default mock fallback still gets blocked when it only produces template or no-op style output. |
| `fake_deepseek_repair_success` | `manual_provider_loop` | `execution_passed` | `deepseek_fallback_provider` | No | The provider loop can surface one failed generation attempt, one repair attempt, and then a successful audit plus execution path. |
| `fake_deepseek_semantic_block` | `manual_provider_loop` | `audit_failed` | `deepseek_fallback_provider` | Yes | Provider-backed semantic review can still stop a candidate even when generation itself succeeds. |
| `fake_deepseek_generation_failure` | `manual_provider_loop` | `generation_failed` | `deepseek_fallback_provider` | Yes | Low-quality fallback output must fail visibly at generation time instead of being normalized into a fake pass. |
| `review_cleanup_provider_quality` | `manual_provider_loop` | `audit_failed` | `mock_fallback_provider` | Yes | Maintainer workflow review cleanup remains conservative when the mock fallback output is still template or no-op quality. |
| `review_cleanup_demo_provider_success` | `manual_provider_loop` | `execution_passed` | `local_review_cleanup_fallback_provider` | No | A controlled maintainer-workflow provider can read review comments and produce a cleanup plan without making code changes. |
| `runtime_service_distill_demo_provider` | `runtime_service_distill` | `execution_passed` | `local_copy_metadata_fallback_provider` | No | The formal `RuntimeService.capture_trajectory -> distill -> audit -> execution` path now preserves metadata sidecar behavior after fallback schema alignment. |

## Fixture Notes

### `demo_local_success`

- lifecycle_mode: `manual_provider_loop`
- expected loop_stage: `execution_passed`
- expected provider: `local_copy_metadata_fallback_provider`
- expected failure: no
- proves: the local demo provider path is still a working positive control for the evaluation loop

### `mock_template_execute_failure`

- lifecycle_mode: `manual_provider_loop`
- expected loop_stage: `audit_failed`
- expected provider: `mock_fallback_provider`
- expected failure: yes
- proves: template-heavy fallback output is still blocked by audit and should not silently reach execution

### `fake_deepseek_repair_success`

- lifecycle_mode: `manual_provider_loop`
- expected loop_stage: `execution_passed`
- expected provider: `deepseek_fallback_provider`
- expected failure: no
- proves: repair visibility works and the evaluation can distinguish repaired success from first-pass success

### `fake_deepseek_semantic_block`

- lifecycle_mode: `manual_provider_loop`
- expected loop_stage: `audit_failed`
- expected provider: `deepseek_fallback_provider`
- expected failure: yes
- proves: semantic review remains a real gate, not a reporting decoration

### `fake_deepseek_generation_failure`

- lifecycle_mode: `manual_provider_loop`
- expected loop_stage: `generation_failed`
- expected provider: `deepseek_fallback_provider`
- expected failure: yes
- proves: generation-time quality failures remain explicit and attributable

### `review_cleanup_provider_quality`

- lifecycle_mode: `manual_provider_loop`
- expected loop_stage: `audit_failed`
- expected provider: `mock_fallback_provider`
- expected failure: yes
- proves: maintainer workflow fixtures are allowed to remain expected failures when fallback output is still template or no-op quality

### `review_cleanup_demo_provider_success`

- lifecycle_mode: `manual_provider_loop`
- expected loop_stage: `execution_passed`
- expected provider: `local_review_cleanup_fallback_provider`
- expected failure: no
- proves: maintainer workflow evaluation can have a controlled positive control that reads review comments, writes a cleanup plan, and stops short of real code edits

### `runtime_service_distill_demo_provider`

- lifecycle_mode: `runtime_service_distill`
- expected loop_stage: `execution_passed`
- expected provider: `local_copy_metadata_fallback_provider`
- expected failure: no
- proves: the formal runtime lifecycle now survives fallback schema alignment and produces both the copied file and metadata sidecar

## Current Known Gaps

- `review_cleanup_provider_quality` is still an expected failure because the mock fallback output does not yet produce a maintainer-quality executable cleanup workflow.
- `review_cleanup_demo_provider_success` is only a controlled positive control. It does not prove that open-ended review cleanup should enter `default-in`, and it does not prove that arbitrary maintainer review synthesis is solved.
- The fake DeepSeek failure fixtures are expected failures by design. They exist to catch regression in failure visibility, not to turn the report green.
- The evaluation baseline is a local quality reference, not a claim of public traction.
- The evaluation baseline is not evidence for widening `default-in`. It only records governed-learning quality on a fixed local fixture set.
