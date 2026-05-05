# Main Demo Walkthrough

Date: 2026-05-05

## Maintainer Pain

Open-source maintainers repeatedly do work that is useful, structured, and expensive, but should not be silently automated.

Review cleanup is a good example:

- pull request comments need to be grouped into required fixes and follow-up work
- the output should help the maintainer decide what happens before merge
- the system should not auto-edit code or auto-promote a new skill just because the task looks familiar

This is the main public demo because it looks like real maintainer work and shows the boundary Skill Runtime is trying to enforce.

## What Codex Normally Does

Without a governed runtime layer, Codex can still read comments and write a cleanup plan.

The usual problem is what happens after that:

- the workflow is easy to lose in chat history
- there is no explicit follow-up contract for the host
- there is no governed path from one successful workflow to a reusable skill candidate
- it is too easy to slide from "helpful plan" into "silent automation" without clear review boundaries

## What Skill Runtime Adds

Skill Runtime adds two things around the normal Codex task:

1. an explicit runtime gate that can say "do not auto-enter this lane"
2. a governed learning path that can still capture the successful workflow for later distillation

For review cleanup, that means:

- the runtime stays conservative at task start
- the maintainer still gets a usable plan
- the successful workflow can be captured
- the next recommended action stays explicit

## Demo Commands

Run these commands from the repository root in PowerShell.

1. Validate the review cleanup fixtures:

   ```powershell
   python -m json.tool demo/maintainer_review_cleanup/review_comments.json > $null
   python -m json.tool demo/maintainer_review_cleanup/observed_task.json > $null
   ```

2. Inspect the maintainer-facing expected output:

   - Open `demo/maintainer_review_cleanup/expected_cleanup_plan.md`

3. Show that review cleanup stays outside automatic runtime entry:

   ```powershell
   $repoRoot = (Get-Location).Path
   $root = ".tmp_review_cleanup_mainline"
   New-Item -ItemType Directory -Force $root | Out-Null
   python -m skill_runtime.cli --root $root codex-run --task-description "Group pull request review comments into a maintainer cleanup plan." --working-directory "$repoRoot" --risk-level low --task-kind workflow --disable-silent-reuse
   ```

4. Capture the successful workflow and inspect the follow-up recommendation:

   ```powershell
   python -m skill_runtime.cli --root $root capture-trajectory --file demo/maintainer_review_cleanup/observed_task.json --task-id maintainer_review_cleanup_demo --session-id demo_review_cleanup
   ```

5. Clean up the temporary runtime root:

   ```powershell
   Remove-Item -Recurse -Force $root
   ```

## Expected Outputs

From `codex-run`:

- `status: "ok"`
- `task_classification.bucket == "default-out"`
- `runtime_lane_status == "skipped"`
- the reason says the task is dominated by open-ended reasoning or external-system state

From `capture-trajectory`:

- `captured == true`
- `trajectory_path` exists under the temporary runtime root
- `recommended_next_action == "distill_trajectory"`
- `recommended_host_operation.tool_name == "distill_trajectory"`
- `available_host_operations` also includes `distill_and_promote_candidate`

## What `recommended_next_action` Means

`recommended_next_action` is the runtime's explicit host follow-up.

In this demo, it does not mean "the runtime already changed the library." It means:

- the observed workflow was captured successfully
- the host now has a concrete next governed step
- the next step is `distill_trajectory`, not silent promotion

That is the public value of the contract: a maintainer or host can see what to do next without losing control of the workflow.

## Why This Stays Safe

This demo stays safe for four reasons:

1. review cleanup starts as `default-out`, so open-ended review judgment is not auto-entered
2. the demo output is a cleanup plan, not an automatic code mutation
3. capture creates a trajectory artifact, not an active skill
4. the recommended follow-up is explicit and governed instead of hidden

This is exactly why review cleanup is the right main demo. It shows useful runtime help without pretending that maintainers want silent review automation.

## What This Proves

This demo proves that Skill Runtime can:

- support a realistic open-source maintainer workflow
- expose a concrete `recommended_next_action`
- capture successful maintainer work into a governed learning artifact
- stay conservative when the task should not be auto-run

## What This Does Not Prove

This demo does not prove that:

- review cleanup should be moved into `default-in`
- the runtime should auto-edit code from review comments
- governed capture is the same thing as safe autonomous maintenance
- one demo is enough evidence for broader automatic entry policies

## Next Product Milestone

Keep this review cleanup path as the stable public maintainer demo, then validate the same boundary on more real maintainer artifacts before changing runtime entry policy.

The next milestone is stronger evidence, not a broader `default-in`.
