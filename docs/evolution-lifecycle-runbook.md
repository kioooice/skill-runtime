# Evolution Lifecycle Runbook

Date: 2026-05-05

## Purpose

Exercise the governed evolution lifecycle end to end:

`candidate -> review -> apply -> rollback`

This runbook follows:

- `docs/evolution-lifecycle-acceptance.md`

The goal is not to prove dashboard visibility. The goal is to prove that a maintainer can inspect, apply, and if needed revert a global skill change through an explicit, auditable path.

## What This Runbook Uses

- a temporary runtime root
- a temporary global skill fixture
- one evolution candidate targeting an existing workflow skill

## Step 1 - Create A Temporary Global Skill Fixture

Prepare a temporary global skill directory with one target skill:

```powershell
New-Item -ItemType Directory -Force .tmp_evolution_lifecycle\global-skills\pre-implementation-workflow-review | Out-Null
Set-Content .tmp_evolution_lifecycle\global-skills\pre-implementation-workflow-review\SKILL.md @'
---
name: pre-implementation-workflow-review
description: Review direction before implementation.
---

# Skill

Review value before building.
'@
```

Expected result:

- the target global skill file exists

## Step 2 - Create And Review A Candidate

Use the RuntimeService CLI path to review a candidate after creating one in the temporary root.

Expected result:

- candidate status becomes `reviewed`
- review decision is `ready_for_manual_diff`
- `.skill_runtime/evolution_reviews/*.review.json` exists
- `.diff` exists
- the global skill file is still unchanged

Host-facing expectation:

- the response recommends `apply_evolution_candidate`

## Step 3 - Apply The Reviewed Candidate

Run apply with explicit confirmation.

Expected result:

- candidate status becomes `applied`
- `.skill_runtime/evolution_backups/*` exists
- `.skill_runtime/evolution_applications/*.apply.json` exists
- the global skill file now includes the evolution update

Host-facing expectation:

- the response recommends `rollback_evolution_candidate`
- `governance_report` is available as a secondary action

## Step 4 - Roll Back The Applied Candidate

Run rollback with explicit confirmation.

Expected result:

- candidate status becomes `rolled_back`
- `.skill_runtime/evolution_rollbacks/*.rollback.json` exists
- the global skill file matches the exact original pre-apply bytes
- the rollback record includes:
  - `application_path`
  - `review_path`
  - backup linkage
  - restored hash matching the pre-apply target hash

Host-facing expectation:

- the response recommends `governance_report`

## Step 5 - Judge The Lifecycle

The runbook passes if all of these are true:

1. Review produced a proposal without mutating the global skill.
2. Apply required confirmation and wrote a backup plus application record.
3. Rollback required confirmation and restored only from the recorded backup.
4. Rollback refused no guards and left an auditable record.
5. Host-facing next actions stayed explicit at each phase.

## What A Failure Looks Like

Treat the run as failed if any of these happen:

- review edits the skill directly
- apply happens without confirmation
- rollback writes over a target that changed after apply
- rollback cannot be traced back to review and apply
- host receives raw lifecycle output without a clear next action

## Current Conclusion

With the current boundary, the evolution lifecycle already proves:

- existing workflow skills can improve through a governed path
- apply is no longer a one-way mutation
- rollback is not only possible, but auditable
- host-facing next actions now make the manual path explicit

What it does not prove yet:

- that the operator-facing lifecycle needs richer UI
- that any part of this path should become automatic

That is acceptable for now.

## Optional Cleanup

```powershell
Remove-Item -Recurse -Force .tmp_evolution_lifecycle
```
