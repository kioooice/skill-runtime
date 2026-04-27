# Dogfood Log 001

## Goal

Run one real `search -> execute -> observed task record -> distill/promote -> reuse -> govern`
session against a temporary runtime root, then record where the workflow still feels rough.

## Session Design

Reference workflow: [dogfooding-workflow.md](/D:/02-Projects/vibe/docs/dogfooding-workflow.md)

Planned loop:

1. `search --query "merge txt files into markdown"`
2. `execute --skill merge_text_files --args-file <json>`
3. keep the returned `observed_task_record`
4. `distill-and-promote --observed-task <record> --skill-name dogfood_merge_text_files_session_001`
5. `execute --skill dogfood_merge_text_files_session_001 --args-file <json>`
6. `governance-report`

The session was run against a copied temporary runtime root so the real repository state stayed unchanged.

## Observed Results

- `search` returned `merge_text_files` as the top recommendation.
- `execute` completed successfully and emitted an `observed_task_record`.
- `distill-and-promote` completed successfully from that observed task record.
- the promoted skill executed successfully on the reuse pass.
- `governance-report` completed successfully and surfaced duplicate clusters plus host actions.

So the current runtime can already close one realistic local loop without hand-authoring a trajectory.

## Friction Found

1. CLI JSON file parsing was too strict for real shell usage.
The first session attempt failed because `execute --args-file` rejected a UTF-8 BOM JSON file. This is common from PowerShell-generated files, so it blocks real dogfooding too early.

2. Distilled merge skill input shape still feels noisier than the original task.
The promoted `dogfood_merge_text_files_session_001` skill exposed `newline` and `pattern` in addition to the core `input_dir` and `output_path` fields. That is technically valid, but it makes the reuse surface heavier than the original user intent.

3. Semantic audit still catches output-name overfitting.
The audit flagged a hardcoded artifact name (`dogfood_merge.md`) in the dogfood-generated merge skill. That means deterministic distillation is still not fully separating reusable output intent from one observed execution artifact.

4. Governance review is still noisy in a test-heavy library.
The session-level `governance-report` was actionable, but the duplicate list is dominated by test and promotion fixtures. The loop works, but the real review surface is harder to scan than it should be.

## Minimal Follow-Up Direction

For this stage, the highest-value next pass is not UI work. It is tightening reuse quality at distill time so the first promoted skill comes out with a cleaner input surface and less artifact-name leakage.

## Follow-Up Status

- `execute` now returns an `operation_log` baseline for applied and planned tool activity.
- dry-run execution now exposes `planned_changes` plus per-operation rollback hints, which should make the next rollback-focused dogfood pass easier to inspect.
