# Host Follow-Up Recommendation Dogfood

Date: 2026-05-05

## Purpose

Verify that the current top-level follow-up recommendation contract is actually usable for maintainers, without adding new rules, widening `default-in`, or building a new presentation layer.

## Case 1 - `background_hint -> execute_skill`

- Input task:
  `merge txt files into markdown`
  with `known_inputs={"input_dir":"demo/input"}` and one expected output path
- runtime_lane_status:
  `entered`
- reuse_decision / learning_decision:
  `background_hint` / `none`
- recommended_next_action:
  `execute_skill`
- recommended_host_operation.tool_name:
  `execute_skill`
- Did this feel natural for a maintainer:
  Yes. The runtime did not auto-run a partially specified workflow, but it still surfaced one clear next step.
- Noise or misleading behavior:
  Low noise. The missing input `output_path` stayed explicit, which prevented the hint from reading like an automatic approval.

## Case 2 - `new_skill_candidate -> distill_trajectory`

- Input task:
  Development-style workflow finalize path: update a runtime test plus observation log with a successful write-backed execution payload
- runtime_lane_status:
  `used`
- reuse_decision / learning_decision:
  `skip` / `new_skill_candidate`
- recommended_next_action:
  `distill_trajectory`
- recommended_host_operation.tool_name:
  `distill_trajectory`
- Did this feel natural for a maintainer:
  Yes. After a concrete successful workflow, the next step being “distill this trajectory” is consistent and easy to understand.
- Noise or misleading behavior:
  Minor wording caveat only: this path is clear for `new_skill_candidate`, but maintainers still need to know that weaker `observed_only` cases may require capture-first behavior instead of immediate distill.

## Case 3 - `improve_existing_skill_candidate -> review_evolution_candidate`

- Input task:
  Improve the direction review workflow after a user correction, with a successful payload carrying explicit `skill_gap.evidence` and `skill_gap.proposed_changes`
- runtime_lane_status:
  `used` on the Codex-facing finalize path, or `not set` on plain host finalization
- reuse_decision / learning_decision:
  `skip` / `improve_existing_skill_candidate`
- recommended_next_action:
  `review_evolution_candidate`
- recommended_host_operation.tool_name:
  `review_evolution_candidate`
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
