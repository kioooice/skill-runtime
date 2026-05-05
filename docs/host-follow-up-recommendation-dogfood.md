# Host Follow-Up Recommendation Dogfood

Date: 2026-05-05

## Purpose

Verify that the top-level follow-up recommendation contract is usable across the three highest-value operator paths:

- `background_hint`
- `distill_trajectory`
- `review_evolution_candidate`

This is not a UI exercise. The goal is to confirm that a host can render a concrete next step without reading payload-specific nested shapes.

## Verified Cases

### 1. Reuse hint stays non-automatic but bubbles a concrete next step

Input shape:

- task: `merge txt files into markdown`
- known inputs: only `input_dir`
- expected outputs: one markdown output path

Observed result:

- reuse decision: `background_hint`
- top-level next action: `execute_skill`
- recommended skill: `merge_text_files`
- missing input stays explicit: `output_path`

Why this matters:

- the runtime does not silently execute when required inputs are missing
- the host still gets one concrete next step to render

## 2. Captured workflow bubbles distillation at the top level

Command used:

`python -m skill_runtime.cli --root D:\02-Projects\vibe capture-trajectory --file demo\maintainer_review_cleanup\observed_task.json --task-id recommendation_dogfood_review_cleanup --session-id recommendation_dogfood`

Observed result:

- capture succeeded
- top-level next action: `distill_trajectory`
- alternate operations remained available for active/global promotion paths

Why this matters:

- the host does not need to inspect nested capture-specific payloads to discover the next step
- the governed learning path still stays explicit and non-automatic

## 3. Concrete existing-skill gap bubbles manual evolution review

Input shape:

- task: improve direction review workflow after user correction
- no silent reuse
- successful execution payload with explicit `skill_gap.evidence` and `skill_gap.proposed_changes`

Observed result:

- learning decision: `improve_existing_skill_candidate`
- top-level next action: `review_evolution_candidate`
- the same review operation remains present inside the capture payload for provenance

Why this matters:

- the host can render the manual-review next step directly
- the lifecycle stays governed; no global skill edit is performed automatically

## Operator Conclusion

The contract is now good enough for host rendering:

- reuse hints surface one direct execution action
- captured workflows surface one direct distillation action
- existing-skill improvements surface one direct manual-review action

The host can prefer top-level recommendation fields and treat nested recommendation payloads as provenance, not as the primary integration surface.

## Follow-Up

The next worthwhile dogfood is not more dashboard work.

It is targeted sampling of real maintainer tasks to judge whether these three recommendations feel natural in sequence:

- `background_hint` before manual execution
- `distill_trajectory` after observed capture
- `review_evolution_candidate` after concrete existing-skill gap detection
