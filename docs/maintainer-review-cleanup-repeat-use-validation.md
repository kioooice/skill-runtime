# Maintainer Review Cleanup Repeat-Use Validation

Date: 2026-05-06

## Goal

Validate `maintainer_review_cleanup` beyond the first demo and beyond workflow-search proof.

The question for this slice is:

`Would the same bounded workflow still be useful on a second maintainer review artifact?`

## Repeat-Use Fixture

This validation adds a second structured review-cleanup case:

- input: `demo/maintainer_review_cleanup_repeat/review_comments.json`
- maintainer plan: `demo/maintainer_review_cleanup_repeat/expected_cleanup_plan.md`
- metadata: `demo/maintainer_review_cleanup_repeat/cleanup_plan.metadata.json`
- observed task: `demo/maintainer_review_cleanup_repeat/observed_task.json`

The second case uses provider-quality baseline review comments instead of dashboard export comments, so it is not just a renamed copy of the original demo.

## Result

The workflow remained useful on the second artifact:

- required fixes were separated from follow-up documentation
- source comment ids were preserved
- verification commands were specific to the reviewed area
- the maintainer decision stayed explicit
- no code fixes were applied
- no review comments were resolved
- no merge approval was inferred
- `default-in` was not widened

## What This Proves

This is stronger than the earlier search-only proof because it exercises the workflow shape on a second realistic review bundle.

It supports the current narrow active ownership claim:

`structured review comments -> maintainer cleanup artifact`

## What It Still Does Not Prove

This does not prove open-ended review automation.

It does not justify:

- applying review fixes automatically
- resolving review comments
- deciding merge readiness
- widening the Codex runtime `default-in` lane
- treating arbitrary review synthesis as solved

## Verification

Minimum verification for this fixture:

```powershell
python -m json.tool demo/maintainer_review_cleanup_repeat/review_comments.json > $null
python -m json.tool demo/maintainer_review_cleanup_repeat/cleanup_plan.metadata.json > $null
python -m json.tool demo/maintainer_review_cleanup_repeat/observed_task.json > $null
python -m skill_runtime.cli --root .tmp_review_cleanup_repeat capture-trajectory --file demo/maintainer_review_cleanup_repeat/observed_task.json --task-id maintainer_review_cleanup_repeat_use --session-id demo_review_cleanup_repeat
git diff --check
```

Expected capture result:

- `.tmp_review_cleanup_repeat/trajectories/maintainer_review_cleanup_repeat_use.json` exists
- the command recommends explicit distillation
- no active skill is promoted

## Current Conclusion

`maintainer_review_cleanup` now has repeat-use evidence as a bounded maintainer workflow. The next useful validation is real maintainer adoption friction: whether the global Codex skill instructions and thin runtime adapter are natural enough to use during an actual PR cleanup round.
