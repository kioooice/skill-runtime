# Host Follow-Up Recommendation Dogfood

Date: 2026-05-05

## Purpose

Verify that the current top-level follow-up recommendation contract is actually usable for maintainers, without adding new rules, widening `default-in`, or building a new presentation layer.

## Case 1 - `background_hint -> execute_skill`

- Input task:
  `merge txt files into markdown`
  with `known_inputs={"input_dir":"demo/input"}` and one expected output path
- Repro command:
  `python -m skill_runtime.cli --root ./.tmp_recommendation_dogfood_case1 codex-run --task-description "merge txt files into markdown" --known-inputs-json "{\"input_dir\":\"demo/input\"}" --expected-outputs-json "[\"demo/output/recommendation_dogfood_background.md\"]"`
- runtime_lane_status:
  `entered`
- reuse_decision / learning_decision:
  `background_hint` / `none`
- recommended_next_action:
  `execute_skill`
- recommended_host_operation.tool_name:
  `execute_skill`
- Expected fields:
  - `runtime_lane_status == "entered"`
  - `reuse_decision.decision == "background_hint"`
  - `recommended_next_action == "execute_skill"`
  - `recommended_host_operation.tool_name == "execute_skill"`
  - `reuse_decision.missing_inputs` includes `output_path`
- Failure signs:
  - `auto_execute` appears instead of `background_hint`
  - `recommended_next_action` is missing
  - `missing_inputs` does not mention `output_path`
- Did this feel natural for a maintainer:
  Yes. The runtime did not auto-run a partially specified workflow, but it still surfaced one clear next step.
- Noise or misleading behavior:
  Low noise. The missing input `output_path` stayed explicit, which prevented the hint from reading like an automatic approval.

## Case 2 - `new_skill_candidate -> distill_trajectory`

- Input task:
  Development-style workflow finalize path: update a runtime test plus observation log with a successful write-backed execution payload
- Repro command:
  `python -m skill_runtime.cli --root ./.tmp_recommendation_dogfood_case2 capture-trajectory --file demo/maintainer_review_cleanup/observed_task.json --task-id recommendation_dogfood_review_cleanup --session-id recommendation_dogfood`
- runtime_lane_status:
  `not set on capture-trajectory output`
- reuse_decision / learning_decision:
  `not applicable on direct capture output`
- recommended_next_action:
  `distill_trajectory`
- recommended_host_operation.tool_name:
  `distill_trajectory`
- Expected fields:
  - `captured == true`
  - `recommended_next_action == "distill_trajectory"`
  - `recommended_host_operation.tool_name == "distill_trajectory"`
  - `available_host_operations` includes `distill_and_promote_candidate`
- Failure signs:
  - `captured` is false
  - `recommended_next_action` is missing
  - `recommended_host_operation.tool_name` is not `distill_trajectory`
- Did this feel natural for a maintainer:
  Yes. After a concrete successful workflow, the next step being “distill this trajectory” is consistent and easy to understand.
- Noise or misleading behavior:
  Minor wording caveat only: this path is clear for `new_skill_candidate`, but maintainers still need to know that weaker `observed_only` cases may require capture-first behavior instead of immediate distill.

## Case 3 - `improve_existing_skill_candidate -> review_evolution_candidate`

- Input task:
  Improve the direction review workflow after a user correction, with a successful payload carrying explicit `skill_gap.evidence` and `skill_gap.proposed_changes`
- Repro files:
  - finalize payload:
    [`demo/recommendation_dogfood_case3_execution_payload.json`](../demo/recommendation_dogfood_case3_execution_payload.json)
- Repro command (PowerShell):
  1. Create a disposable runtime root and a matching global-skill fixture:
     ```powershell
     $root = "./.tmp_recommendation_dogfood_case3"
     New-Item -ItemType Directory -Force "$root/global-skills/pre-implementation-workflow-review" | Out-Null
     @'
     ---
     name: pre-implementation-workflow-review
     ---

     # Skill
     '@ | Set-Content "$root/global-skills/pre-implementation-workflow-review/SKILL.md"
     ```
  2. Save the `agent-plan` output to a temporary JSON file:
     ```powershell
     $planResponse = python -m skill_runtime.cli --root $root agent-plan --task-description "Improve the direction review workflow after a user correction." --working-directory . --expected-outputs-json "[\"./.tmp_recommendation_dogfood_case3/global-skills/pre-implementation-workflow-review/SKILL.md\"]" --disable-silent-reuse | ConvertFrom-Json
     $planResponse.data | ConvertTo-Json -Depth 20 | Set-Content "$root/plan.json"
     ```
  3. Reuse that saved plan with the execution payload:
     ```powershell
     python -m skill_runtime.cli --root $root agent-plan-learning --plan-json-file "$root/plan.json" --execution-json-file "demo/recommendation_dogfood_case3_execution_payload.json"
     ```
  4. Cleanup when done:
     ```powershell
     Remove-Item $root -Recurse -Force
     ```
- runtime_lane_status:
  `not set on plain host-finalize style reproduction`
- reuse_decision / learning_decision:
  `skip` / `improve_existing_skill_candidate`
- recommended_next_action:
  `review_evolution_candidate`
- recommended_host_operation.tool_name:
  `review_evolution_candidate`
- Expected fields:
  - `learning_decision.decision == "improve_existing_skill_candidate"`
  - `recommended_next_action == "review_evolution_candidate"`
  - `recommended_host_operation.tool_name == "review_evolution_candidate"`
  - `learning_capture_payload.evolution_candidate_path` exists
- Failure signs:
  - the fixture command was skipped or edited incorrectly and the expected output path no longer points at `./.tmp_recommendation_dogfood_case3/global-skills/pre-implementation-workflow-review/SKILL.md` (`setup failure`)
  - `plan.json` still contains the top-level `status` / `data` wrapper instead of the internal plan object with `request` and `reuse_decision`
  - `observed_only` appears despite explicit evidence and proposed changes
  - `recommended_next_action` is missing
  - no `evolution_candidate_path` is emitted (`recommendation contract failure`)
- Did this feel natural for a maintainer:
  Yes. The recommendation correctly routes to manual review instead of pretending the existing skill should change automatically.
- Noise or misleading behavior:
  Low noise. The strongest remaining caveat is that host-only flows may not always expose `runtime_lane_status`, so maintainers should read the learning decision and recommendation together.

## Conclusion

The current recommendation contract is usable:

- `background_hint` gives a conservative but actionable next step
- `new_skill_candidate` gives a concrete distillation step
- `improve_existing_skill_candidate` gives a governed manual-review step

## Real Issues Found

1. `observed_only` and `new_skill_candidate` are adjacent in maintainer mental models, but only the concrete `new_skill_candidate` case was a clean top-level `distill_trajectory` recommendation in this round.
2. `runtime_lane_status` is clearest on Codex-facing entry/finalize paths; plain host-finalize paths can still be useful, but they are less uniform as dogfood artifacts.

## Recommendation

Do not widen `default-in` based on this evidence.

The contract is good enough to keep dogfooding, but there is no evidence here that broader automatic entry would improve maintainer outcomes.

All three cases should be run against disposable runtime roots such as `./.tmp_recommendation_dogfood_case*` and those directories can be deleted after the check.
