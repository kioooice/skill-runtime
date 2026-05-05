# Decisions

## Decision Log

### 2026-05-06 - Dashboard CLI Should Always Report Current Operator Summary Status, Even Without Refresh

**Decision**

After adding the explicit `--refresh-operator-summary` option, extend the `dashboard` CLI success payload so it always reports the current local operator-summary status: whether the export exists, what its freshness status is, where it lives, and which `generated_at` value is currently visible.

**Reason**

Refreshing the export and rendering HTML in one command removed one friction point, but the command still did not answer the operator’s immediate status question unless they opened the generated page. Returning the local summary state directly in the CLI payload finishes the closed loop: operators can inspect, refresh, and verify summary status from the same command family without adding control-plane behavior.

**Impact**

- `dashboard` CLI payloads now include `operator_summary_available`
- payloads now include `operator_summary_freshness_status`
- `operator_summary_output_path` and `operator_summary_generated_at` are now populated from the current local export state, not only from the refresh path
- when no export exists and no refresh is requested, the command explicitly reports unavailable state instead of fabricating metadata
- this remains read-only status reporting: no evaluator execution, no lifecycle mutation, no hidden refresh, and no justification for widening `default-in`

### 2026-05-06 - Operator Summary Refresh Should Be An Explicit Dashboard CLI Option, Not A Silent Default

**Decision**

Add an explicit `--refresh-operator-summary` option to the existing `dashboard` command, including `--global`, so operators can refresh the stable summary export in the same step that renders dashboard HTML. Do not make this refresh implicit in every dashboard run.

**Reason**

The product gap after the dashboard wording cleanup was not more UI data; it was refresh ergonomics. Requiring a separate export command before every dashboard run adds friction, but making refresh automatic would blur side effects and make `dashboard` less predictable. An explicit flag gives the mainline a usable closed loop while keeping the boundary honest.

**Impact**

- `python -m skill_runtime.cli dashboard --refresh-operator-summary` now refreshes `.skill_runtime/dashboard/operator-summary.json` before rendering HTML
- the same flag works with `dashboard --global`
- CLI success payloads now include `operator_summary_refreshed`, `operator_summary_output_path`, and `operator_summary_generated_at`
- default `dashboard` behavior remains unchanged when the flag is omitted
- this still does not run evaluator scripts, execute host operations, promote/apply lifecycle actions, or justify widening `default-in`

### 2026-05-06 - Dashboard Copy Must Be Professional And Neutral, Not Internal Or Conversational

**Decision**

After removing internal implementation labels from the dashboard, tighten the new copy again so it uses short, neutral product language rather than explanatory conversational phrasing.

**Reason**

The first rewrite fixed the comprehension failure caused by internal names such as `provider_quality`, but it overcorrected into guidance-heavy phrases like `先看这里` and `这块只回答...`. That still reads like narration instead of product UI. The correct target is concise operational language: clear enough to understand, restrained enough to scan.

**Impact**

- navigation now prefers `总览`, `可复用流程`, `待审核项`, `近期记录`, `系统状态`, and `数据来源`
- overview metrics now use shorter operational labels such as `现有流程`, `自动处理`, `观察中`, and `常规处理`
- operator-summary copy is tightened to `系统摘要`, `现有流程`, `待审核候选`, `任务轨迹`, `建议操作`, `提供器状态`, `基础检索状态`, and `工作流检索状态`
- grouped workflow copy remains visible but no longer reads like guided onboarding text
- this is still a wording-only slice: no data-shape expansion, no write actions, no evaluator execution, and no justification for widening `default-in`

### 2026-05-06 - Dashboard First Screen Must Use User-Facing Language And Separate System Checks From Primary Status

**Decision**

Keep the existing read-only dashboard shell, but redesign the first-screen information architecture so it speaks in operator-facing language instead of implementation names. The default landing view must be `overview`, the main navigation must describe user-visible meaning, and the three quality gates must be shown as secondary `系统检查`, not as peer business-state cards.

**Reason**

After the stable `operator-summary` slice landed, the next real product failure was comprehension rather than data access. A user could open the dashboard and still not know what `活跃技能 / 候选技能 / 轨迹记录 / provider_quality` meant or what to read first. That is an information architecture failure, not a missing-field problem. The right move is to relabel and reorder the existing surface before adding more data or actions.

**Impact**

- dashboard title, nav, and section headers now use user-facing labels such as `运行状态总览`, `现在先看什么`, `可直接复用的流程`, `待你决定的事项`, `最近发生了什么`, `系统检查`, and `来源与范围`
- overview is now the true default view in both initial HTML state and client-side script state
- operator-summary cards now use `可直接复用的流程`, `待审核流程`, `已记录任务样本`, and `待你确认的建议`
- quality gates are rendered as `提供器质量`, `基础技能检索质量`, and `工作流检索质量`, framed as system self-checks rather than primary product status
- the grouped workflow surface inside the skill-tree page is now expressed as `流程分组`, not a separate internal library concept
- this slice does not add write actions, full item-list dependencies, evaluator execution, promote/apply behavior, or any justification for widening `default-in`

### 2026-05-06 - Render Stable Operator Summary On Existing Dashboard Surfaces Without Turning Dashboard Into A New Control Plane

**Decision**

Expose the exported stable `operator-summary` subset on the existing read-only dashboard surfaces: the local `overview` page and each project card in `global-dashboard`.

**Reason**

The prior slices already proved that `operator-summary` could be exported and consumed safely by collectors. At that point the remaining product gap was no longer data access; it was first-glance operator visibility. Keeping the render scope small closes that gap without reintroducing page churn, unstable full-list dependencies, or any confusion that dashboard itself executes lifecycle work.

**Impact**

- local dashboard overview now renders a read-only `operator-summary` section when export data exists
- the section shows only stable fields: summary freshness, generated time, count-only inventory, gate status/freshness, safe next steps, missing/unavailable items, and non-automatic boundary text
- global project cards now show operator-summary freshness plus per-gate status/freshness when metadata exists
- existing dashboard/global-dashboard navigation and collector boundaries stay intact
- dashboard still does not consume full item lists from `operator-summary`
- dashboard still does not execute host operations, evaluator scripts, promote, or apply evolution candidates
- this still does not justify widening `default-in`

### 2026-05-06 - Add Freshness Semantics At The Export And Collector Layer Before Any Dashboard UI Change

**Decision**

Add explicit freshness-policy fields to the dashboard-oriented `operator-summary` export, and let existing collectors compute `fresh / stale / unknown` summary metadata from those fields, without changing dashboard page rendering.

**Reason**

The collector can now consume the exported operator summary, but availability alone is not enough for an operator workbench. The next missing product answer is whether a visible summary or persisted quality-gate snapshot is still current enough to trust. This belongs in the collector/data layer first, not in page templates and not in ad hoc consumer logic.

**Impact**

- exported `.skill_runtime/dashboard/operator-summary.json` now includes top-level `freshness_policy`
- exported gate objects now include per-gate `freshness_policy`
- local collector enriches imported operator-summary payloads with top-level and per-gate `freshness`
- global collector now reports `operator_summary_freshness_status` and `operator_quality_gate_freshness_statuses`
- stale/missing timestamps remain honest as `stale` or `unknown`; nothing is coerced into `fresh`
- dashboard page rendering remains unchanged
- no evaluator runs were added
- no host operation is executed
- no skill is promoted
- no evolution candidate is applied
- this still does not justify widening `default-in`

### 2026-05-06 - Treat PowerShell Chaining And Validation Timeouts As Durable Workflow Corrections

**Decision**

Record two repeated process mistakes as durable workflow corrections for this workspace:

1. do not use `&&` when sending shell commands in the PowerShell environment
2. do not describe a timed-out validation command as a failure until it has been rerun or otherwise verified

**Reason**

Both mistakes have now repeated across turns:

- PowerShell in this environment rejects `&&`, so using it creates avoidable command failures during staging/commit flows
- the fast runtime suite is long enough that a too-short timeout can expire even when the suite would pass, so treating timeout as failure produces a false status report

These are workflow mistakes, not product behavior issues. They need durable guards so the next action changes before the mistake repeats.

**Impact**

- when using PowerShell shell commands, chain sequential commands with `;` or split them into separate tool calls
- when long-running validation times out, report `timed out / not yet verified`, then rerun with a longer timeout before claiming failure
- prefer a longer timeout up front for `python -m unittest tests.test_runtime_fast -v`
- record the correction in state files instead of bloating `AGENTS.md`
- next trigger: any commit/push shell command in PowerShell, and any long-running validation command whose timeout is close to prior observed duration

### 2026-05-06 - Let Existing Dashboard Collectors Consume Exported Operator Summary Before Any UI Change

**Decision**

Keep dashboard/global-dashboard page rendering unchanged, but let the existing collector layer optionally read the exported stable `operator-summary` JSON.

**Reason**

The export path already gave the project a stable operator-facing payload. The next low-risk step is not a new page or render rewrite; it is making existing collectors aware of that payload so future dashboard/operator workbench work can build on a shared read-only source. This preserves the boundary that pages should not depend directly on unstable low-level runtime files or full inventory item lists.

**Impact**

- `collect_dashboard_data(...)` now returns `operator_summary` when `.skill_runtime/dashboard/operator-summary.json` exists
- `collect_global_dashboard_data(...)` now annotates each discovered project with operator-summary availability, generation time, and gate-status metadata
- added tests proving local/global collector behavior with and without the export file
- `skill_runtime/dashboard/render.py` and existing dashboard/global-dashboard HTML pages remain unchanged
- no evaluator runs were added
- no host operation is executed
- no skill is promoted
- no evolution candidate is applied
- this still does not justify widening `default-in`

### 2026-05-06 - Advance Dashboard Integration Through A Read-Only Operator Summary Export, Not A Page Rewrite

**Decision**

Use a read-only export layer as the next integration step between `operator-summary` and the existing dashboard/global-dashboard surfaces.

**Reason**

The repository already has working read-only dashboard pages. The next product problem is not missing UI; it is the lack of a stable, scriptable bridge from `operator-summary` into future collector work. A narrow export file lets dashboard/operator workbench consumers depend on stable fields without binding pages directly to low-level runtime files or to the full `operator-summary` item lists too early.

**Impact**

- chose scheme A instead of changing dashboard page rendering
- added `docs/dashboard-operator-summary-integration-plan.md`
- added `collect_dashboard_operator_summary_data(...)` and `export_dashboard_operator_summary_data(...)`
- added `scripts/export_operator_summary_for_dashboard.py`
- writes a stable subset to `.skill_runtime/dashboard/operator-summary.json`
- existing dashboard/global-dashboard HTML pages remain unchanged
- export does not run evaluator scripts, execute host operations, promote skills, or apply evolution candidates
- this still does not justify widening `default-in`

### 2026-05-06 - Stabilize operator-summary v1 before any dashboard workbench integration

**Decision**

Treat `operator-summary` as the stable v1 Operator Workbench data source first, and keep the existing read-only dashboard unchanged until the summary contract is stable enough to consume.

**Reason**

The repository already has read-only dashboard and global-dashboard surfaces. Reworking those pages again would increase UI churn without solving the more important product problem: the runtime needs one stable, scriptable summary contract that operators and future surfaces can trust. Persisted gate status also belongs in that summary contract, not in ad hoc dashboard-only logic.

**Impact**

- added `docs/operator-summary-contract.md`
- `operator-summary` v1 now documents stable top-level fields, allowed unavailable fields, and explicit non-automatic boundaries
- provider/search/workflow evaluator scripts now support optional `--write-operator-status`
- persisted gate status is stored only under `.skill_runtime/operator_status/*.json`
- `RuntimeService.operator_summary()` now reads those files when present and otherwise stays `unavailable`
- dashboard pages were not changed in this slice
- this still does not justify widening `default-in`

### 2026-05-06 - Pause Release Packaging And Start v0.3 Product Completeness With A Read-Only Operator Summary

**Decision**

Pause the release/tag packaging mainline and move the next product slice to `v0.3 product completeness`, starting with a minimal read-only Operator Workbench summary exposed as `python -m skill_runtime.cli --root . operator-summary`.

**Reason**

`v0.2.0rc1` already proved the narrow claim it needed to prove: governed maintainer-workflow capture, explicit follow-up recommendation, reproducible quality gates, and explicit non-automatic boundaries. What it did not solve is everyday operator visibility. Runtime state is still scattered across trajectories, skill stores, audits, and runtime events, which makes the system harder to use daily than it should be.

The right next slice is therefore not more release packaging. It is a single read-only surface that shows what the runtime already knows and what it can safely do next, without widening automation boundaries.

**Impact**

- added `docs/v0.3-product-completeness-plan.md`
- added `operator-summary` CLI support with default JSON and optional text rendering
- `operator-summary` surfaces active skills, staging candidates, captured trajectories, recent audits, recent runtime events, safe next steps, and intentionally non-automatic actions
- text rendering is expected to express the same state groups as the JSON summary, not a separate prose-only view
- provider/search/workflow baseline status is shown only when a local persisted report exists; otherwise it is marked `unavailable`
- existing read-only dashboard/global-dashboard stays in place; this slice does not rewrite dashboard pages
- the intended future connection is for dashboard/operator workbench to consume `operator-summary` as a stable data source once the summary contract settles
- no host operation is executed
- no skill is promoted
- no evolution candidate is applied
- no runtime state is mutated
- this still does not justify widening `default-in`

### 2026-05-06 - Call The Current Repository State v0.2.0rc1

**Decision**

After the release gate checks passed, package the current repository state as `v0.2.0rc1` and treat it as the valid v0.2 release candidate.

**Reason**

The repository now has all required release-candidate evidence in one place:

- maintainer-facing proof bundle is checked in and reproducible
- provider quality baseline passes
- utility search baseline passes
- workflow search baseline passes
- architecture, runtime contract, and fast-suite verification all pass
- changelog and version entry now expose a v0.2 RC surface

The remaining gaps are real, but they are already documented as non-blocking and do not undermine the narrow maintainer-governance product claim for v0.2.

**Impact**

- added `docs/v0.2-release-candidate-checklist.md`
- updated `CHANGELOG.md` with a `v0.2.0-rc1` section
- updated `pyproject.toml` version to `0.2.0rc1`
- added a minimal README link to the RC checklist
- current blocking gap status for the RC gate is `none`
- this still does not justify widening `default-in`

### 2026-05-06 - Package The Accepted Capture-Trajectory Path As The v0.2 Maintainer Proof Bundle

**Decision**

Use the already accepted `capture-trajectory --render-recommendation text` path, with the `maintainer_review_cleanup` observed task and the existing provider/search/workflow baseline gates, as the official v0.2 maintainer-facing proof bundle.

**Reason**

The project needs one fast external proof that it is not just a local utility-script library. The accepted `capture-trajectory` path already has the right evidence shape: a maintainer workflow input, an auditable JSON output, an operator-readable governed recommendation, and an explicit non-automatic boundary. Packaging that path is lower risk and more honest than inventing a broader demo or claiming dashboard-level proof.

**Impact**

- added `docs/v0.2-maintainer-proof-bundle.md`
- added `scripts/run_v0_2_proof_bundle.py`
- added checked-in artifacts under `docs/fixtures/v0.2-proof-bundle/`
- updated README with a narrow proof-bundle link only
- no runtime decision logic changed
- no follow-up operation was executed
- this still does not justify widening `default-in`

### 2026-05-06 - Prefer Larger Complete Slices Over Narrow Documentation-Only Rounds

**Decision**

Switch the default development cadence to larger complete slices. Unless a task hits a genuinely high-risk boundary, each round should try to include the decision, the smallest complete implementation, the relevant tests, the related docs/runbook/summary updates, repository state updates, baseline gate verification, and commit/push in one pass.

**Reason**

The recent work has been correct but too fragmented. The user wants faster momentum and fewer rounds that only produce a plan, a summary page, or one narrow acceptance checkpoint. The project already has strong hard boundaries, so the safer improvement is to increase slice size without relaxing those boundaries.

**Impact**

- future rounds should default to complete vertical slices rather than micro-steps
- the hard boundaries remain unchanged:
  - do not widen `default-in`
  - do not auto-promote
  - do not auto-apply evolution candidates
  - do not force expected gaps into passes
  - do not present lifecycle operations as ordinary active skills
  - do not skip baseline gates for presentation progress
  - do not do dashboard overhauls without explicit acceptance criteria

### 2026-05-06 - Tighten README Positioning Without Reframing The Product

**Decision**

Keep the current maintainer/workflow/governed-learning README narrative, but tighten the wording around rule-based utility coverage and make the v0.2 baseline gates directly discoverable from the main README.

**Reason**

The public story is already mostly correct: the project is positioned as a local workflow governance layer for repeatable maintainer automation, not a generic script bundle. The remaining risk is emphasis drift. The `Distillation` rule registry can still pull attention toward utility/file-transform examples, and the three v0.2 quality gates were easier to miss than they should be for release-readiness.

**Impact**

- added `docs/v0.2-release-readiness-review.md`
- updated `README.md` wording to frame rule-based utilities as coverage/control examples rather than the main value story
- added the provider / utility search / workflow search baseline commands to README
- no runtime behavior, baseline JSON, ranking, workflow query, or `default-in` boundary changed
- this still does not justify widening `default-in`

### 2026-05-06 - Adopt Capture-Trajectory Recommendation Text Narrowly In README And Runbook

**Decision**

Recommend `capture-trajectory --render-recommendation text` in README and the relevant payload-rendering runbook as the narrow operator path for governed follow-up.

**Reason**

The implementation and acceptance evidence are complete for this one command path. The operator text is clear, the JSON audit payload stays intact, and no host operation execution, promotion, or apply side effect occurs. That is enough for narrow documentation adoption, but not enough for broader CLI or host-surface claims.

**Impact**

- added `docs/cli-recommendation-adoption-decision.md`
- updated README quick path wording
- updated `docs/real-host-payload-rendering-runbook.md`
- adoption remains opt-in and `capture-trajectory`-only
- this still does not justify widening `default-in`

### 2026-05-06 - Treat Accepted Capture-Trajectory Recommendation Text As A Candidate Operator Path, Not Final Adoption

**Decision**

Treat the accepted `capture-trajectory --render-recommendation text` path as an available CLI/operator surface, but do not yet declare it the default operator path in README or runbooks.

**Reason**

Implementation and acceptance are complete for one narrow command path. The remaining question is adoption, not feature expansion. That decision should be made explicitly rather than inferred from the existence of the flag.

**Impact**

- added `docs/cli-recommendation-presentation-summary.md`
- updated `docs/v0.2-core-quality-summary.md`
- next slice should ask whether README/runbook should recommend this flag as the default operator path
- this still does not justify widening `default-in`

### 2026-05-06 - Accept Capture-Trajectory CLI Recommendation Surface As-Is

**Decision**

Accept the current `capture-trajectory --render-recommendation text` CLI surface without further CLI logic changes.

**Reason**

A real run now has checked-in `stdout` and `stderr` artifacts. The JSON audit payload remained intact on `stdout`, the operator-facing recommendation text was clear on `stderr`, and no `distill_trajectory`, promote, or apply operation was executed.

**Impact**

- added `docs/fixtures/cli-recommendation-presentation/stdout.capture-trajectory.json`
- added `docs/fixtures/cli-recommendation-presentation/stderr.capture-trajectory.txt`
- added `docs/cli-recommendation-presentation-acceptance.md`
- no CLI logic change was required from acceptance
- this still does not justify widening `default-in`

### 2026-05-06 - Keep CLI Recommendation Rendering Opt-In And Separate From JSON Audit Output

**Decision**

Use an explicit `capture-trajectory --render-recommendation text` flag for the first real CLI/operator integration. Keep the normal JSON response unchanged on `stdout`, and print the human-readable recommendation text to `stderr`.

**Reason**

This is the smallest safe integration that matches the current placement decision. It gives operators an in-flow text surface without changing payload shape, without hiding the raw JSON audit payload, and without implying automatic execution of governed follow-up operations.

**Impact**

- added `docs/cli-recommendation-presentation-integration-plan.md`
- `capture-trajectory` now accepts `--render-recommendation text`
- default CLI JSON output remains unchanged
- recommendation text is opt-in and presentation-only
- this does not execute `recommended_host_operation`
- this still does not justify widening `default-in`

### 2026-05-06 - Start Real Host Integration With CLI Operator Text, Not Dashboard

**Decision**

Use CLI/operator text output, paired with the original JSON payload for audit, as the first real host integration surface for governed follow-up rendering.

**Reason**

The current evidence proves renderer output works in fixture payloads and one real CLI payload path. It does not prove dashboard ergonomics or placement. Starting with dashboard would force a larger surface decision before the actual placement question is settled.

**Impact**

- added `docs/host-integration-placement-decision.md`
- recommended first surface is CLI/operator text output or an equivalent renderer command reference
- dashboard is explicitly not the first integration surface
- next step should define operator acceptance criteria for that placement
- this still does not justify widening `default-in`

### 2026-05-06 - Close Host Operator Validation At The Evidence Boundary

**Decision**

Close the current host/operator validation slice with a summary page and do not keep expanding fixtures or presentation behavior by default.

**Reason**

The current evidence chain is now complete enough for this slice:

- fixture payload dogfood proved the main governed follow-up families render cleanly
- the real payload runbook proved no new capture helper is needed
- the real CLI validation proved one actual service response can be captured, extracted, and rendered clearly

What remains unresolved is no longer rendering capability. It is the integration decision: where current renderer output should appear in a real host/operator flow.

**Impact**

- added `docs/host-operator-validation-summary.md`
- updated `docs/v0.2-core-quality-summary.md`
- next recommended slice is `real host integration decision: where should renderer output appear?`
- this still does not justify widening `default-in`

### 2026-05-06 - Treat Capture-Trajectory As The First Real Payload Validation Target

**Decision**

Use `capture-trajectory` as the first real CLI payload validation target for host recommendation rendering, and keep the current presentation helper unchanged after this run.

**Reason**

The command already appears in the README quick path, already returns top-level recommendation fields, and produces a clean governed follow-up case: `distill_trajectory`. The real run confirmed that the only meaningful interpretation risk remains the raw `requires_confirmation=false` field, and the current renderer already resolves that risk by keeping the non-automatic promotion boundary explicit.

**Impact**

- added checked-in real artifacts under `docs/fixtures/real-host-payload-rendering/`
- added `docs/real-host-payload-rendering-report.md`
- confirmed the current helper is sufficient for this real CLI path
- no service recommendation logic changed
- this still does not justify widening `default-in`

### 2026-05-06 - Use Existing CLI JSON Output For Real Payload Rendering Validation

**Decision**

Do not add a new payload-capture helper for the first real host payload rendering round. Use the existing CLI JSON response, save it, and extract the inner `.data` payload object before rendering.

**Reason**

The current codebase already emits real recommendation-bearing JSON from service and orchestration commands. The actual integration gap is not missing capture logic. It is operator clarity around the outer `status/data` CLI envelope versus the inner payload object expected by the renderer. A runbook closes that gap with less risk than adding another script surface.

**Impact**

- added `docs/real-host-payload-rendering-runbook.md`
- updated `docs/host-integration-dogfood-report.md` with the next validation target
- no new capture script was added
- no service recommendation logic changed
- this still does not justify widening `default-in`

### 2026-05-06 - Keep Host Recommendation Presentation Stable After First Operator Dogfood

**Decision**

Do not expand the current recommendation presentation helper after the first host/operator dogfood round. Treat the current formatter, fixture demo, payload renderer CLI, and checked-in payload fixtures as sufficient for now.

**Reason**

The first dogfood round covered the three main governed follow-up families that matter for host integration:

- `background_hint -> execute_skill` with missing inputs
- `new_skill_candidate -> distill_trajectory`
- `improve_existing_skill_candidate -> review_evolution_candidate`

Those payloads rendered cleanly through the current formatter and renderer. The operator could understand the next step and the governance boundary in each case, and the output kept the no-automatic-execution, no-automatic-promotion, and no-automatic-apply boundaries visible. No blocking ambiguity appeared that justified changing helper behavior.

**Impact**

- added `docs/host-integration-dogfood-plan.md`
- added checked-in payload fixtures under `docs/fixtures/recommendation-payloads/`
- added `scripts/dogfood_recommendation_presentation.py`
- added `docs/host-integration-dogfood-report.md`
- presentation helper remains unchanged
- next recommended slice is real host integration dogfood / operator validation
- this does not justify widening `default-in`

### 2026-05-06 - Split Workflow Search Quality From The Utility Fixture Baseline

**Decision**

Create a separate workflow-focused search baseline instead of extending the existing utility-heavy search baseline in place.

**Reason**

Utility skills still matter as fixtures, smoke targets, and control cases, but they are no longer the main product proof. The real product value is whether maintainer workflow intents can find the right workflow skill or whether the system honestly shows that a workflow is still only represented as a demo or host follow-up path. Mixing those two goals into one baseline would blur the signal and encourage more utility optimization than the product needs.

**Impact**

- added `docs/workflow-search-quality-plan.md`
- added `docs/workflow-search-quality-baseline.json`
- added `scripts/evaluate_workflow_search_quality.py`
- added workflow-search evaluator tests and wired them into `tests.test_runtime_fast` / `tests.test_runtime`
- current workflow baseline records two real workflow matches and two honest expected gaps
- utility skills remain in the repository as fixtures and controls, not the main workflow value proof
- this still does not justify widening `default-in`

### 2026-05-05 - Prefer Metadata Tightening Before Search Weight Tuning

**Decision**

After reviewing the fixed baseline ranking diagnostics, prefer metadata quality tightening before any ranking-weight change.

**Reason**

The current baseline is still fully matched, negative queries are clean, and the strongest false neighbors are explainable by broad metadata rather than an obviously broken scoring mix. Adjusting weights now would risk hiding metadata breadth instead of clarifying where retrieval quality actually needs work.

**Impact**

- added `docs/search-ranking-diagnostics.md`
- current recommendation is to tighten broad text/file metadata before revisiting ranking weights
- no search algorithm or weight change is justified yet on the current fixed baseline
- this remains retrieval-quality analysis only and is not evidence for widening `default-in`

### 2026-05-05 - Close v0.2 Search Quality With A One-Page Summary

**Decision**

Close the current `v0.2-search-quality` slice with a single summary page instead of adding more queries or changing retrieval behavior.

**Reason**

The baseline, alias-driven recall improvement, and machine-comparable gate are now all in place. At this point the useful move is not more scope. It is to lock the current evidence into one operator-readable page so later search work starts from a stable, explicit boundary.

**Impact**

- added `docs/v0.2-search-quality-summary.md`
- recorded the current search gate command and current `matched=7` baseline status
- documented that Chinese support is explicit-alias only
- documented that no embedding, external service, or LLM retrieval is involved
- reinforced that this is still not evidence for widening `default-in`

### 2026-05-05 - Promote Search Quality Baseline To A Machine-Readable Gate

**Decision**

Treat `docs/search-quality-baseline.json` as the machine-readable expectation set for the local search-quality query set, and let `scripts/evaluate_search_quality.py --baseline ...` compare current retrieval behavior against it.

**Reason**

The local search-quality evaluator was already honest and reproducible, but it was still only a report. To detect retrieval drift the same way provider quality now does, the query set needs a machine-comparable baseline that distinguishes stable matches, regressions, negative-query failures, and missing coverage without forcing a search-algorithm rewrite.

**Impact**

- `--baseline` now adds `baseline_comparison` to the search-quality report
- `--fail-on-regression` now returns non-zero only for regressions, unexpected failures, or missing queries
- the current baseline captures 7 queries and currently matches all 7
- this remains a local lexical-retrieval quality gate; it is not semantic retrieval and not evidence for widening `default-in`

### 2026-05-05 - Use Explicit Metadata Aliases For Narrow Chinese Search Recall

**Decision**

Add optional `search_aliases` to skill metadata and let local lexical search use those aliases as a small metadata-driven recall signal.

**Reason**

The first search-quality baseline exposed a concrete gap: known Chinese intent for `merge_text_files` produced no usable recall because the current search path is still ASCII-heavy and lexical. The narrowest honest improvement is not semantic retrieval or algorithm rewrite. It is explicit alias metadata that can teach the local search path a few known intents while keeping the retrieval contract local, inspectable, and reproducible.

**Impact**

- `SkillMetadata` now supports `search_aliases`
- `SkillIndex.search` now includes aliases in searchable text and a lightweight score boost
- `merge_text_files` now declares explicit Chinese aliases for known merge-document intents
- `scripts/evaluate_search_quality.py` now treats the Chinese merge query as an expected pass and adds a Chinese negative query
- this remains metadata-driven recall only; it is not semantic retrieval, does not introduce embeddings or external services, and is not evidence for widening `default-in`

### 2026-05-05 - Measure Search Quality Before Rewriting Retrieval

**Decision**

Start the next core slice with a local search-quality baseline instead of changing the retrieval algorithm first.

**Reason**

Search and reuse were still being judged mostly through scattered tests and a previous all-green script that ran directly against the real runtime root. That shape was too optimistic and not reproducible enough for honest baseline work. A local evaluator using a temporary runtime root and a fixed small fixture set gives a stable view of current retrieval behavior, including known failures.

**Impact**

- added `docs/v0.2-search-quality-plan.md`
- rewrote `scripts/evaluate_search_quality.py` to use a temporary runtime root and a selected active-skill fixture subset
- the search-quality report now shows per-query outcomes, top results, and failure reasons instead of only a boolean all-pass result
- current baseline exposes a real limitation: pure Chinese search intent does not retrieve `merge_text_files`
- this is measurement only; it does not change retrieval behavior and is not evidence for widening `default-in`

### 2026-05-05 - Treat Provider Guidance As Part Of The Formal Fallback Request Contract

**Decision**

Record `provider_guidance` as an explicit field in the fallback provider request contract and document it in the provider integration guide.

**Reason**

Once the minimal review-cleanup guidance was wired into request construction, leaving it as an undocumented implementation detail would make external providers and future provider examples guess whether the field was stable, optional, or merely temporary prompt text. The contract should say clearly that `provider_guidance` is a first-class request field, while also preserving prompt-based compatibility for simpler providers.

**Impact**

- `docs/provider-integration.md` now lists the fallback request fields explicitly
- providers may consume `provider_guidance` directly or ignore it and rely on `prompt`
- bundled provider examples remain compatible without widening their authority
- `provider_guidance` is explicitly not permission to relax audit, auto-promote, or bypass maintainer judgment
- baseline expectations remain unchanged; this is contract clarification, not default-lane evidence

### 2026-05-05 - Carry Minimal Provider Guidance In The Fallback Request

**Decision**

Carry a dedicated `provider_guidance` field in the fallback provider request and embed the same guidance into the fallback prompt.

**Reason**

The review-cleanup gap analysis showed that the negative fixture fails mainly because the mock fallback path produces template-like summaries instead of executable planning workflows. The narrowest useful intervention is to strengthen the provider-side request contract with explicit guidance, without changing audit thresholds, widening runtime entry, or forcing the mock negative control to pass.

**Impact**

- fallback requests now carry explicit provider guidance alongside summary, docstring, input schema, trajectory, and prompt
- the guidance emphasizes executable workflow code, matching runtime tools, kwargs-based path parameterization, and avoiding hardcoded demo artifact names
- review-cleanup requests also state that providers should write a cleanup plan artifact and should not modify source code, auto-resolve review comments, infer merge approval, or bypass maintainer judgment
- deterministic rule matches still bypass the fallback path
- this is a provider-fidelity prompt/request improvement only; it is not evidence for widening `default-in`

### 2026-05-05 - Promote Provider Quality Baseline To A Machine-Readable Check

**Decision**

Treat `docs/provider-quality-baseline.json` as the machine-readable expectation set for the provider quality evaluation fixtures, and let `scripts/evaluate_provider_quality.py --baseline ...` compare current fixture behavior against it.

**Reason**

The Markdown baseline made the expected provider-quality outcomes readable, but it could not act as a repeatable quality gate. A JSON baseline lets the same local fixture run produce a structured `baseline_comparison` with matched fixtures, regressions, improvements, unexpected failures, unexpected passes, missing fixtures, and extra fixtures.

**Impact**

- `--baseline` adds comparison data while still printing the full JSON report
- `--fail-on-regression` returns non-zero only for regressions, unexpected failures, or missing fixtures
- Unexpected passes and extra fixtures stay visible without failing the command by default
- This is a provider-quality check only; it is not a dashboard, not an automatic promotion path, and not evidence for widening `default-in`

### 2026-05-05 - Bubble Follow-Up Recommendations To The Top-Level Orchestration Result

**Decision**

Treat host-facing next actions as part of the primary `AgentOrchestrationResult` contract instead of leaving them only inside nested payloads such as `learning_capture_payload`.

**Reason**

Operator-facing follow-up actions were becoming inconsistent. Evolution review/apply/rollback already had explicit host recommendations, but reuse hints and learning capture recommendations were still buried in nested payloads. That forced hosts to special-case search results, capture payloads, and evolution payloads differently. The host should be able to render one top-level next action contract regardless of whether the workflow is reuse, capture, or existing-skill evolution.

**Impact**

- `AgentOrchestrationResult` now carries top-level recommendation fields
- `background_hint` now bubbles a top-level `execute_skill` recommendation
- `new_skill_candidate` now bubbles `distill_trajectory` to the top level after capture
- `improve_existing_skill_candidate` now bubbles `review_evolution_candidate` to the top level
- CLI and MCP plan/result reconstruction now preserve the same recommendation fields end to end
- Added regression coverage for host, MCP, and finalizer recommendation propagation

### 2026-05-05 - Prefer Top-Level Recommendations As The Host Integration Surface

**Decision**

Treat nested recommendation payloads as provenance only. Hosts should prefer the top-level recommendation fields on `AgentOrchestrationResult`.

**Reason**

Targeted dogfood across `background_hint`, `capture-trajectory`, and explicit existing-skill evolution showed that the top-level contract now carries the right next step in all three cases. Continuing to integrate against nested payload-specific shapes would reintroduce branching and make host behavior harder to keep consistent.

**Impact**

- host integrations can render one next-step contract across reuse and learning paths
- nested recommendation payloads remain available for debugging and provenance
- follow-up dogfood should now focus on whether the recommendation sequence feels natural in real maintainer tasks, not on payload-shape differences

### 2026-05-05 - Treat Recommendation Consumption As An Operator Sequence

**Decision**

Treat `background_hint`, `distill_trajectory`, and `review_evolution_candidate` as one operator-facing sequence family, not as three unrelated point features.

**Reason**

After the top-level contract was unified, the next real question was whether these recommendations still felt fragmented in practice. Acceptance-style sequencing showed they can already form a coherent non-automatic flow: the host can first surface a hint, then a capture follow-up, then a governed existing-skill review step. That is a stronger product boundary than three isolated examples.

**Impact**

- added a dedicated sequence runbook
- added acceptance-style coverage for the three-step operator sequence
- the next product question shifts from payload shape to whether a narrow host presentation layer is warranted

### 2026-05-05 - Do Not Build A Narrow Host Presentation Layer Yet

**Decision**

Do not immediately build a new host UI / CLI presentation layer for follow-up recommendations. Use `manual_validation_first`.

**Reason**

The product boundary is now clear enough to validate without new code: the host already has a top-level recommendation contract, a dogfood note, and a sequence runbook. Building another surface right now would risk packaging work before the operator pain is proven.

**Impact**

- no new presentation command or host UI layer is added yet
- the next validation step is operator use across 2-3 real maintainer flows
- implementation should reopen only if the gap is clearly presentation-specific rather than another workflow-boundary issue

### 2026-05-05 - Preserve Original Bytes Across Evolution Rollback

**Decision**

Treat evolution backups and rollbacks as byte-preserving file operations. Do not reconstruct the original global skill file from decoded text during rollback.

**Reason**

Real operator-facing dogfood of the evolution lifecycle exposed a gap: a BOM-backed `SKILL.md` could be semantically restored but still lose its original bytes because apply wrote the backup from decoded text and rollback rewrote the file in normalized UTF-8. That made `restored_content_hash` drift from the pre-apply hash even though the visible content looked the same. The lifecycle is only trustworthy if rollback restores the exact original file bytes.

**Impact**

- `apply_evolution_candidate` now records the backup from `target_skill_path.read_bytes()`
- `rollback_evolution_candidate` now restores the target with `write_bytes()` from the recorded backup
- Added a regression test covering BOM-backed skill files and exact hash restoration
- The operator-facing lifecycle runbook has now been dogfooded against a real byte-preservation scenario

### 2026-05-05 - Require Concrete Existing-Skill Gap Evidence Before Evolution

**Decision**

Do not let finalization create `improve_existing_skill_candidate` from a weak or vague `skill_gap` hint. Existing-skill evolution now requires concrete `evidence` and `proposed_changes`.

**Reason**

The governed evolution lifecycle is only useful if candidates represent real gaps in an existing workflow skill. A payload that merely says “maybe improve this later” is not enough. Without a stricter boundary, any task loosely related to a known skill could create noisy evolution candidates and blur the difference between observed execution, new workflow distillation, and real existing-skill improvement.

**Impact**

- `plan_learning` now treats weak existing-skill gap hints as `observed_only`
- `finalize_task` no longer persists evolution candidates from vague `skill_gap` payloads
- Existing-skill evolution still proceeds when the payload carries explicit `evidence` and `proposed_changes`
- Added acceptance-style tests covering weak-gap downgrade and explicit-gap approval after reuse

### 2026-05-05 - Require Concrete Output Signals Before New Skill Distillation

**Decision**

Do not let finalization create `new_skill_candidate` from a merely successful workflow plus declared `expected_outputs`. Immediate distillation now requires a concrete output signal: successful write-like operations and expected outputs that match real artifacts or written paths.

**Reason**

The under-covered workflow path should only distill tasks that actually produced stable, inspectable outputs. A read-only task, or a task whose declared outputs do not match the files it really wrote, is still useful to observe but is not stable enough to crystallize into a new reusable skill.

**Impact**

- `plan_learning` now downgrades read-only success with declared outputs to `observed_only`
- `plan_learning` now downgrades output-mismatch cases to `observed_only`
- `new_skill_candidate` still proceeds for concrete write-backed workflows whose expected outputs match the actual written artifacts
- Added acceptance-style tests covering read-only success, output mismatch, and preserved positive cases

### 2026-05-05 - Require Expected Output Alignment Before Silent Reuse

**Decision**

Do not allow `auto_execute` when the request declares `expected_outputs` that do not line up with the known output parameters for the reusable skill.

**Reason**

Strong search score and complete required inputs are not enough if the caller says the task should produce output A while the known output arguments point at B. In that situation the reusable skill may still be relevant, but the runtime should only surface it as `background_hint`, not silently take over execution.

**Impact**

- `plan_reuse` now keeps `auto_execute` only when declared expected outputs align with known output-like inputs such as `output_path`
- mismatched output declarations now downgrade to `background_hint`
- strict scope-policy mismatch remains a confirmed `background_hint` case
- added acceptance-style tests for scope mismatch and expected-output mismatch

### 2026-05-05 - Publish Finalizer Learning Decision Matrix

**Decision**

Promote the hardened finalizer rules into a dedicated operator-facing matrix document.

**Reason**

The project now has enough decision boundaries that tests alone are not an adequate explanation layer. Operators need a single document that explains why a task became `skip`, `observed_only`, `new_skill_candidate`, or `improve_existing_skill_candidate`.

**Impact**

- Added `docs/finalizer-learning-decision-matrix.md`
- The matrix now explains reuse-aware learning, weak-gap downgrade, output-driven new-skill distillation, and clean-reuse skip behavior
- Future boundary work should update this matrix instead of relying on scattered notes

### 2026-05-05 - Establish Review Cleanup As The Second Maintainer Mainline

**Decision**

Use `review cleanup` as the second maintainer-facing mainline after `handoff continuation`.

**Reason**

This workflow is highly representative of real open-source maintenance work, but it also tests an important product truth: some valuable maintainer workflows should remain conservative in the Codex-facing runtime gate because they are dominated by open-ended review judgment. That makes it a strong companion to the more structured handoff continuation path.

**Impact**

- Added `docs/maintainer-review-cleanup-mainline-acceptance.md`
- Added `docs/maintainer-review-cleanup-mainline-runbook.md`
- Verified that the current gate classifies this family as `default-out / skipped`
- Verified that governed learning still works through `capture-trajectory` and explicit `distill_trajectory` follow-up

### 2026-05-05 - Choose Docs-First Open Source Readiness Route

**Decision**

Use the docs-first open-source readiness release as Stage 4. Do not move into CLI hardening or Codex plugin implementation yet.

**Reason**

The repository already has runtime, CLI, MCP, dashboard, and maintainer demos. The highest current application risk is public trust and onboarding, not missing plugin code. Community files, release-readiness docs, and an application draft directly improve reviewability without overbuilding.

**Impact**

- Added `CONTRIBUTING.md`, `SECURITY.md`, and `CODE_OF_CONDUCT.md`
- Added `.env` ignore rules
- Added `docs/open-source-release-readiness-checklist.md`
- Added `docs/codex-open-source-application-draft.md`
- Updated README docs links and readiness documents
- Plugin path remains a later option only if a concrete maintainer workflow requires it

### 2026-05-05 - Adopt MIT License

**Decision**

License the project under the MIT License and record it in package and README metadata.

**Reason**

The project is an early open-source developer tool and Codex workflow/runtime layer. MIT keeps adoption friction low for individual maintainers, tool authors, and organizations evaluating the project. This fits the current goal of improving open-source readiness before any Codex for Open Source or open source fund application.

**Impact**

- Added `LICENSE` with MIT License text
- Added license, author, URLs, keywords, and classifiers to `pyproject.toml`
- Added license notes to `README.md`, `README.zh-CN.md`, and `README.en.md`
- Editable install now accepts the updated package metadata

### 2026-05-05 - Aim Project Toward Codex For Open Source Readiness

**Decision**

Set a new strategic target: prepare this project to become a credible open-source Codex workflow/plugin layer that could later apply for OpenAI Codex for Open Source or the Codex open source fund.

**Reason**

The user wants to orient the project toward Codex open-source support, including the possibility of 6 months of ChatGPT Pro through Codex for Open Source. The official application asks for a public GitHub profile, public repository, maintainer role, why the repository qualifies, and how API credits would be used. That means the real work is proving public maintainer value, not simply packaging code as a plugin.

**Impact**

- Verdict: `manual_validation_first`
- Do not promise eligibility or free membership
- Do not build plugin features only for application optics
- Next step is an open-source readiness audit
- Required evidence includes public repo readiness, license, README, install/demo path, real maintainer workflows, and concise application copy
- Treat plugin packaging as one possible route only after the value and distribution gaps are clear

### 2026-05-04 - Add Parallel Subagent Orchestration Skill

**Decision**

Create `parallel-subagent-orchestration` as a global Codex skill for complex parallelizable work. In this workflow, the current Codex thread acts as the main agent: it frames the goal, keeps the critical path, delegates bounded parallel subtasks, reviews subagent results, integrates accepted work, verifies, and reports the final outcome.

**Reason**

Complex tasks often contain independent exploration, implementation, verification, or research slices. A default main-agent/subagent workflow can reduce latency without losing accountability, as long as the main agent remains responsible for scope control, review quality, conflict resolution, and final verification.

**Impact**

- The authoritative skill lives at `C:\Users\Administrator\.codex\skills\parallel-subagent-orchestration`
- Project and global `AGENTS.md` route to the skill with one short line instead of duplicating the full workflow
- The workflow applies only when subagent use is authorized by user request, project rules, or active tool policy
- Subagents must receive clear ownership boundaries and produce reviewable outputs
- The main agent remains responsible for final integration and verification

### 2026-05-03 - Skill Evolution Rollback Requires Confirmation And Stale Checks

**Decision**

Add a rollback path for applied skill evolution candidates. `rollback_evolution_candidate` restores the backup recorded by `apply_evolution_candidate`, but only when the caller explicitly confirms rollback.

**Reason**

Skill evolution can modify global Codex skills, so undo must be available before this loop is trustworthy. At the same time, rollback must not overwrite later manual edits. The rollback path therefore checks that the current target hash still matches the apply record's `new_content_hash` before restoring the backup.

**Impact**

- RuntimeService, CLI, and MCP now expose `rollback_evolution_candidate`
- CLI requires `--confirm-rollback`
- The only supported rollback strategy is `restore_backup_file`
- Rollback records are written to `.skill_runtime/evolution_rollbacks/*.rollback.json`
- Candidates move from `applied` to `rolled_back` after a successful rollback
- If the target skill changed after apply, rollback fails with `EVOLUTION_TARGET_CHANGED_AFTER_APPLY`
- Dashboard status labels now include `已回滚`

### 2026-05-03 - Add Plan Progress Tracker Skill

**Decision**

Create `plan-progress-tracker` as a global Codex skill for multi-stage plan execution. It records and reports the active plan coordinate: stage number, stage name, status, completed stages, next action, and drift risk.

**Reason**

The user loses orientation after a plan is listed and development proceeds step by step. A generic "continue" loop hides which stage is active and whether the work is still following the plan. The assistant should maintain this progress coordinate instead of relying on the user to remember it.

**Impact**

- The authoritative skill lives at `C:\Users\Administrator\.codex\skills\plan-progress-tracker`
- Global and project `AGENTS.md` only contain a short routing line
- Auto-mode and stage reports should include the plan coordinate when planned work is active
- Session handoff files should store the plan coordinate for resume and compaction recovery
- Context compaction audit should recover the active plan coordinate before continuing substantial planned work

### 2026-05-03 - Add Context Compaction Audit Skill

**Decision**

Create `context-compaction-audit` as a global Codex skill. It runs after context compaction or summary-based resume and decides whether the current thread should continue, checkpoint first, finish a narrow stage then reopen, or reopen immediately.

**Reason**

Long development threads lose precision after compaction. The useful decision is not just "summarize what happened"; it is whether the next stage is still safe in the current compressed context. Exact token compression metrics are usually unavailable, so the skill must report exact values only when measurable and otherwise use estimates or mark the metric unavailable.

**Impact**

- The authoritative skill lives at `C:\Users\Administrator\.codex\skills\context-compaction-audit`
- Global and project `AGENTS.md` only contain a short routing line
- The skill checks durable state files before relying on compressed chat memory
- The skill coordinates with `session-handoff-maintenance` whenever checkpointing or reopening is recommended
- Output includes compaction evidence, timing, ratio availability, loss risk, missing context, and a reopen recommendation
- Reopen recommendations include a compact handoff prompt for the next chat

### 2026-05-03 - Central Skill Library Owns Workflow Grouping

**Decision**

Use `中央技能库` as the single workflow-skill browsing surface. It now renders the functional groups directly and the separate `技能集合` view is removed.

**Reason**

The user clarified that the functional grouping is valuable, but showing the same workflow skills through both `中央技能库` and `技能集合` creates duplicate navigation. The central library should not be a scattered one-by-one skill list; it should show grouped workflow capability.

**Impact**

- Sidebar no longer renders `技能集合`
- `中央技能库` count remains the active workflow-skill count, currently 8
- The main central-library page renders `方向与策略`、`自动推进`、`运行时与验证`、`会话接续`
- Basic local helper skills remain available to runtime/search, but stay out of the default visual surface
- Skills inside each group can still open the detail drawer
- Tests protect the removed collections route and grouped central-library rendering

### 2026-05-03 - Platform Inventory Uses Compact Skill Cards

**Decision**

Render `平台与项目` inventory entries as compact skill-library-style cards instead of expanded project cards. Each card now shows the skill name, one-line path, short clamped summary, normalized source tags, and a single source-root row.

**Reason**

The previous platform view repeated raw paths, long descriptions, `角色：...`, and `来源：...` lines. That made the page feel like an internal dump instead of a management panel. The user asked to condense the information or make it like the skill library.

**Impact**

- Platform cards use `platform-skill-card` and `platform-card-grid`
- Long descriptions are shown as `platform-summary` and visually clamped
- Role/source fields are mapped into Chinese labels such as `全局权威`、`外部`、`只读来源`
- Expanded debug-style prefixes `角色：` and `来源：` are removed from platform cards
- A regression test protects this compact platform-card structure

### 2026-05-03 - Trigger Log Defaults To Used Events

**Decision**

Add status filters to the dashboard `触发日志` page and default the visible list to `已使用`. The page now separates `已使用`、`进入观察`、`已跳过` so users can first see where Skill Runtime actually participated, then switch to observation-only or skipped records when needed.

**Reason**

The combined trigger log mixed three different meanings: runtime actually reused a skill, runtime only observed, and Codex handled the task directly. The user asked for that distinction and specifically wanted the default view to show the useful participation records.

**Impact**

- Trigger-log sections start with `data-active-event-filter="used"`
- Event cards carry `data-event-status` for static CSS filtering and JS switching
- The status labels use Chinese product wording: `已使用`、`进入观察`、`已跳过`
- The generated dashboard opens trigger logs on used records by default, with empty states for statuses that have no records
- Tests and Playwright checks protect the default used-only display and click switching behavior

### 2026-05-03 - Trigger Log Uses User-Readable Chinese

**Decision**

Render dashboard trigger-log events as Chinese user-facing records instead of raw runtime internals. Each event card now shows task, time, handling method, and result. Common English task descriptions and runtime reasons are mapped to Chinese explanations.

**Reason**

The raw event view exposed internal strings such as `task bucket guarded-in skipped...`, which are useful for debugging but unclear to the user. The dashboard should explain what happened: whether runtime participated, only observed, or Codex handled the task directly.

**Impact**

- `runtime lane` wording in the page subtitle is replaced with Chinese `运行时`
- Event cards use `任务 / 时间 / 处理方式 / 结果`
- Common skipped/used/entered reasons are translated into plain Chinese
- Tests protect that global trigger logs no longer render raw English reason strings for common cases

### 2026-05-03 - Dashboard Collections Hide Basic Local Skills

**Decision**

The dashboard `能力集合` page now shows only active workflow skills. Default collections are grouped by workflow function: `方向与策略`, `自动推进`, `运行时与验证`, and `会话接续`. Basic local helper collections such as `基础本地技能`, `文本处理`, `格式转换`, and `文件整理` are no longer rendered in the default dashboard.

**Reason**

The user clarified that basic local file helpers have little value in the visual management surface. Showing them keeps attention on low-level utilities instead of the workflow skills that matter for judging project direction and Codex behavior.

**Impact**

- The 8 workflow skills are split into four readable functional groups
- Basic local skills remain available to the runtime and explicit search, but not as default dashboard content
- The central skill tree no longer explains where basic helpers were moved
- Tests protect workflow-only default collections and the absence of basic helper rows in rendered dashboard HTML

### 2026-05-03 - Dashboard Overview Chrome Stays Minimal

**Decision**

Keep the dashboard overview as a clean summary surface: no path subtitle under the title, no local "current view" search row, and no separate `全局日志` navigation item. In global mode, cross-workspace events are merged into the single `触发日志` page. The `中央技能库` navigation count represents active workflow skills only, not all active basic helper skills.

**Reason**

The user marked the subtitle/search chrome as visual noise and clarified that the central skill library currently means workflow skills. Keeping both `触发日志` and `全局日志` also duplicates the same kind of runtime event surface.

**Impact**

- Overview pages focus on section metrics instead of repeating workspace path and page-level search
- `中央技能库` count now matches the visible workflow-skill surface and currently displays 8
- Global runtime events remain visible through `触发日志`, while the sidebar has one log entry
- Tests protect the workflow-only count, removed overview chrome, and absence of the duplicate global-log route

### 2026-05-03 - Read-Only Panel Starts With Detail Inspection

**Decision**

Upgrade the dashboard from a static read-only page into a read-only interactive panel, starting with skill card detail inspection. This stage allows clicking visible workflow skill cards and opening a side drawer, but does not add promote, reject, edit, archive, install, or cross-project write actions.

**Reason**

The user clarified that "real panel" currently means clicking to see information, not operating on runtime state. Starting with a read-only drawer gives the panel a real interaction loop while preserving the safety boundary and avoiding a premature operations console.

**Impact**

- `docs/runtime-readonly-panel-plan.md` defines the first-stage boundary
- Central skill cards now expose escaped detail data through static `data-*` attributes
- Visible read-only labels are removed from the dashboard chrome; the no-write boundary remains a behavior rule, not repeated UI text
- Skill detail descriptions combine the short summary with `docstring` context when available, so workflow adapters explain the global authoritative skill relationship
- The front-end drawer fills content with `textContent`
- The dashboard remains static HTML and does not require a backend server
- Future read-only details for events, collections, and projects can reuse the same drawer pattern

### 2026-05-03 - Dashboard Overview Is The Summary Surface

**Decision**

Treat `总览` as the only summary surface for global/project runtime status. It should use product-readable wording, compact metric cards, and short explanatory text. Other dashboard pages should keep their top area focused on that page's title and purpose.

**Reason**

The user flagged the overview copy and layout as still rough. Keeping every page wrapped in the same global explanation made the interface feel noisy, while metric labels such as `runtime 参与` and `标签 - 说明` made the page read like internal debug output.

**Impact**

- The overview title is now `全局运行时总览` or `运行时总览`
- Metric cards use number, label, and short caption instead of hyphenated label text
- `运行时参与` replaces mixed Chinese/English metric wording
- Current-project and cross-workspace section descriptions sit under their section headings
- Tests protect the new overview labels and page structure

### 2026-05-03 - Capability Collections Are Workflow-First

**Decision**

Show workflow-oriented capability collections before basic local file utility collections. The dashboard now renders `能力集合` as two sections: `工作流技能` first, then `基础本地技能` containing the local helper groups such as basic skills, text processing, format conversion, and file organization.

**Reason**

The user wants to evaluate workflow skills first. Showing basic local helpers at the top makes the project look centered on low-level file utilities, which repeats the earlier route problem.

**Impact**

- Default collection definitions now order workflow collections before basic local collections
- The dashboard visually separates workflow skills from basic local skills
- Candidate counts and candidate list rows are hidden from default dashboard views; staging/governance data still exists for explicit review paths
- Basic local helpers remain visible, but they no longer occupy the first screen of the collections page
- Global dashboard explanation and local view search belong only on the `总览` page; other pages use the same top area for their own page title
- Tests protect the default collection order

### 2026-05-03 - Dashboard UI Follows Skills-Manage App Shell

**Decision**

Redesign the static runtime dashboard around the `iamzhihuix/skills-manage` interface pattern: desktop app shell, top global search, left navigation, content header, local search row, and two-column skill cards. The old radial skill tree is no longer the primary layout.

**Reason**

The user rejected the previous visual direction as too ugly. The reference project already solves the same product category with a clearer management-app structure, so matching that visual language is a higher-value path than continuing to polish the custom radial tree.

**Impact**

- The dashboard keeps the existing read-only data model and static HTML output
- The visible UI now uses a Catppuccin Latte-style palette, mono UI typography, purple selected nav state, compact sidebar, and card grid layout
- Workflow skills remain the default central skill library surface; basic local skills stay in the secondary collection
- Tests now protect the app-shell layout and prevent the old radial-tree classes from returning as the default view

### 2026-05-03 - Basic Local Skills Are Secondary To Workflow Skills

**Decision**

Dashboard and collection surfaces now treat ordinary local file-processing skills as `basic` skills, not as the primary workflow skill surface. The default skill tree shows only workflow skills. Basic local skills are still available through the `基础本地技能` capability collection.

**Reason**

The user does not need to see low-level local helpers such as text merge, JSON to CSV, or cleanup skills when reviewing workflow capability. Keeping them in the main skill tree makes the project look like it is still centered on basic dogfood utilities instead of reusable workflow judgment and governance.

**Impact**

- Dashboard collection data now marks each skill with `skill_surface`
- Global/imported workflow candidates and workflow-tagged skills remain visible in the default tree
- Ordinary local file-processing skills move to the built-in `basic-skills` collection
- Tests now protect that default skill tree excludes basic helper groups while the collection still exposes them

### 2026-05-03 - Workflow Error Correction Is A Prevention Guard

**Decision**

Refocus `workflow-error-correction` from a recording tool into a known-error prevention guard. Its primary outcome is fewer repeated mistakes. Recording is only a fallback when a genuinely new error pattern appears.

**Reason**

The user clarified that the desired effect is not "Codex has a place to record mistakes." The desired effect is that Codex uses known mistakes to change behavior before repeating them.

**Impact**

- The global skill now says the primary outcome is fewer repeated mistakes, not a better error log
- It defines known mistake guards for AGENTS edits, runtime validation loops, direction-before-implementation, repeated correction requests, auto-mode drift, and AGENTS bloat
- It requires changing the next action immediately when a known guard applies
- The fast regression now protects this prevention-first guard language

### 2026-05-03 - Recorded Workflow Mistakes Must Be Reused Before New Records

**Decision**

`workflow-error-correction` is not a passive log. When a similar situation appears, Codex must first check existing correction records and apply the prevention rule. A new error record is only created when the pattern is new, materially broader, or lacks a usable prevention rule.

**Reason**

The user should not need to repeatedly say "you made this same mistake again." Recording an error only has value if future sessions reuse the record to avoid the same behavior.

**Impact**

- The global skill now starts with "check existing correction records before creating a new one"
- It explicitly says not to require the user to repeat an already recorded mistake
- A fast regression test protects this prevention-first behavior
- Future corrections should report whether they reused an existing correction or created a new record

### 2026-05-03 - Workflow Error Records Do Not Belong In AGENTS

**Decision**

Create the global `workflow-error-correction` skill for recurring process mistakes, route drift, and avoidable assistant workflow errors. Keep `AGENTS.md` as lightweight standing rules and workflow routing, not a running incident log.

**Reason**

The user pointed out that the previous route-correction text should not have been added as detailed AGENTS rules. It was useful as a correction, but the durable place for this kind of mistake is a workflow that records the error pattern, prevention rule, and storage target.

**Impact**

- Project and global `AGENTS.md` no longer contain the two specific runtime-validation-loop mistake bullets
- Both AGENTS files now keep one generic lightweight-boundary rule and route to `workflow-error-correction`
- The new global skill defines how to classify, record, and prevent repeated workflow mistakes without bloating AGENTS
- A fast regression test protects both project and global AGENTS from reintroducing those case-specific rules

### 2026-05-03 - Pre-Implementation Review Becomes The Main Development Gate

**Decision**

Upgrade the global `pre-implementation-workflow-review` skill from a general checklist into the main workflow gate before new development directions. The workflow now blocks implementation unless it reaches a `build_now` verdict; otherwise it returns `manual_validation_first`, `revise_direction`, or `do_not_build_now`.

**Reason**

The user clarified that the important capability is not more local skills or runtime samples. Codex should challenge a proposed direction before implementation: whether the problem is real, whether existing/manual alternatives already solve it, whether the smallest validation loop is clear, and whether building now has value.

**Impact**

- The authoritative global skill now defines a build gate, output contract, current-alternative research behavior, and runtime-loop guardrail
- Project and global `AGENTS.md` now say only `build_now` permits same-flow implementation
- A fast regression test protects the global skill from losing the main-process guardrails
- Future work should apply this gate before new product routes instead of continuing internal runtime validation by default

### 2026-05-03 - Runtime Validation Is Not The Product Goal

**Decision**

Stop treating additional Skill Runtime trigger validation, `entered / used` sample collection, dashboard events, or local skill growth as a default development goal. Future work must route back through the development-direction value gate when it starts to look like "keep proving the runtime works".

**Reason**

The user caught a repeat of the earlier failure mode: continuing to validate local skills and runtime behavior can create busy progress without proving project value. If the user had not pointed it out, the workflow could have drifted back into adding skills and collecting samples instead of preventing low-value development.

**Impact**

- Project and global `AGENTS.md` now explicitly block runtime-validation loops as a default route
- The main product value is restated as pre-development direction/value review
- Runtime work remains allowed only when it directly supports valuable decisions or prevents low-value implementation

### 2026-05-03 - GitNexus Index Refreshed To Current Commit

**Decision**

Refresh the local GitNexus index for this repository after the runtime lane and workflow-skill changes. Keep the Windows degraded query strategy in place, but treat the local index as current again for impact analysis.

**Reason**

The repository index was still at `992f36e` while the working branch had advanced to `c9f2c2c`. Relying on stale GitNexus results would make structure lookup and impact analysis less trustworthy.

**Impact**

- `gitnexus status` reports `up-to-date` at commit `c9f2c2c`
- CLI `cypher`, `query`, and `context RuntimeService` all exit successfully
- Search ranking is still subject to the local Windows FTS fallback described in `docs/gitnexus-local-runbook.md`

### 2026-05-03 - Runtime Test Profiler Can Write JSON Reports

**Decision**

Add `--json-output` to `scripts/profile_runtime_tests.py` and expose a small `write_timing_json_report` helper for stable machine-readable timing reports.

**Reason**

The profiler previously printed only text. That is enough for a one-off inspection, but it makes before/after comparison and future trend tracking difficult when the fast suite is near two minutes.

**Impact**

- Profiling runs can now save `successful`, `tests_run`, total elapsed time, and slowest tests as JSON
- The existing text output remains unchanged
- Contract tests cover the JSON report shape without running a full suite

### 2026-05-03 - Governance Index Writes Merge Only Changed Metadata

**Decision**

Governance write paths now call `save_merged` with only the metadata objects they actually changed. Archive and provenance backfill paths no longer pass the full pre-operation index snapshot back into the merge step.

**Reason**

Passing the full loaded skill list preserves newly added skills, but it can still overwrite a late update to an existing non-target skill with stale metadata from the beginning of the operation. This showed up in an archive fixture regression where a concurrent same-skill summary update was lost.

**Impact**

- Archive cold, archive duplicate, archive fixture, and provenance backfill preserve late same-name index updates for untouched skills
- Existing archive behavior and governance follow-ups remain unchanged
- The regression is covered by a targeted governance test

### 2026-05-03 - Codex CLI JSON Inputs Can Be Passed By File

**Decision**

Add `--known-inputs-json-file`, `--expected-outputs-json-file`, `--plan-json-file`, and `--execution-json-file` support to the Codex-facing CLI commands. Inline JSON remains supported, but each JSON field now has a file-based alternative.
The global `runtime-gate-workflow` skill now also tells future sessions to prefer file-based JSON flags when using CLI fallback from PowerShell.

**Reason**

PowerShell can mangle nested JSON passed as a command-line argument, especially for `codex-run` and `codex-finalize`. File-based JSON inputs make runtime gate and finalizer dogfooding reliable without requiring fragile shell escaping.

**Impact**

- `agent-plan`, `agent-plan-learning`, `codex-classify`, `codex-run`, and `codex-finalize` can read structured JSON from files
- Existing inline JSON flags remain compatible
- `codex-finalize` can now accept `--execution-json-file` instead of requiring inline `--execution-json`
- New Codex sessions get this guidance through `C:\Users\Administrator\.codex\skills\runtime-gate-workflow\SKILL.md`

### 2026-05-03 - Runtime Event Payloads Use One Shared Builder

**Decision**

Move runtime event JSON payload assembly into `skill_runtime.observability.events` and have both the CLI `runtime-events` command and MCP `runtime_events` tool call the same local/global builder functions.

**Reason**

The CLI and MCP entrypoints intentionally expose the same read-only event shape. Keeping separate payload construction in both places makes future follow-up fields or count changes easy to update in one entrypoint and miss in the other.

**Impact**

- CLI and MCP runtime event inspection now share the same payload contract
- Future event fields and count changes have one implementation point
- The change is internal and preserves the existing command/tool output shape

### 2026-05-03 - Runtime Events Are Exposed Through MCP

**Decision**

Add a read-only MCP tool named `runtime_events`. It mirrors the CLI event inspection shape for local and cross-project runtime lane events, including counts, recent events, and learning follow-up labels.

**Reason**

Codex app sessions should not have to fall back to shell commands just to inspect whether the runtime lane entered, used, or skipped a task. Exposing the same read-only event data through MCP keeps observability available through the host integration surface without adding mutation controls.

**Impact**

- MCP hosts can inspect recent local runtime lane events
- MCP hosts can aggregate sibling project events via `global_events=true`
- The tool is read-only and does not execute, promote, archive, or edit skills

### 2026-05-03 - Runtime Events Have A Read-Only CLI

**Decision**

Add `python -m skill_runtime.cli runtime-events` as a read-only command for inspecting recent runtime lane events. It returns JSON with event counts, recent events, and learning follow-up fields; `--global --scan-root <dir>` returns the same shape across project roots.

**Reason**

The dashboard can show follow-up actions, but automated checks and cross-workspace inspection also need a lightweight command that does not generate HTML or open a browser. This keeps observability scriptable without adding mutation controls.

**Impact**

- Local runtime events are inspectable through CLI JSON
- Global cross-project events are inspectable through CLI JSON
- Follow-up labels and recommended next actions are available to scripts and tests

### 2026-05-03 - Runtime Events Record Learning Follow-Up Actions

**Decision**

Runtime lane events now persist finalizer learning follow-up fields: `recommended_next_action`, available host operation count, operation labels, and operation tool names. The dashboard trigger log renders the next action and the visible follow-up operation labels for both project and global log rows.

**Reason**

After capture recommendations learned to expose one-step promotion follow-ups, the event log still only showed lane status and a trajectory path. That made the real next step visible in the API response but invisible in the dashboard users inspect later.

**Impact**

- `used` runtime events can show the captured workflow's next action
- Dashboard trigger logs can surface promotion follow-ups without adding mutation buttons
- The dashboard remains read-only

### 2026-05-03 - Development Observation Can Be Triggered By Explicit Output Paths

**Decision**

The Codex task classifier now treats explicit development output paths as a valid `development-workflow-observation` signal, even when the task description uses neutral wording. Outputs under project development areas such as `skill_runtime/`, `tests/`, `docs/`, `scripts/`, and `.github/` with development file extensions can enter `default-in`.

**Reason**

Real Codex development requests often say what changed without using words like implement, refactor, test, or docs. The previous classifier could skip an obvious code/test/documentation task simply because the description was neutral, even though expected outputs clearly pointed at project development files.

**Impact**

- Clear code/test/doc/config output paths can enter the runtime observation lane
- Broad local work without explicit outputs remains `guarded-in`
- Silent reuse is still disabled for broad development tasks when requested

### 2026-05-03 - Captured Trajectories Expose One-Step Promotion Follow-Ups

**Decision**

When finalizer capture produces a reusable trajectory, the recommendation payload still keeps `distill_trajectory` as the primary next action, but now also exposes two `distill_and_promote_candidate` host operations: one for project active promotion and one with `promotion_target="global_codex"` for global Codex skill promotion.

**Reason**

The previous capture payload stopped at “distill this trajectory,” even after the full `distill_and_promote` global target path existed. That made the closed loop available by command line, but not discoverable from the real finalizer output that captures successful work. Adding follow-up host operations connects capture to promotion without making promotion automatic.

**Impact**

- Captured trajectory recommendations now include one-step project and global promotion options
- The default recommendation remains conservative: distill first
- Global promotion is explicit through `promotion_target="global_codex"`
- Fast verification remains 92 tests OK

### 2026-05-03 - Distill-And-Promote Can Target Global Codex Skills

**Decision**

`distill_and_promote` now accepts a promotion target. The default remains project `active`, but callers can pass `promotion_target="global_codex"` or CLI `--promotion-target global-codex` to run the full `capture/register -> distill -> audit -> promote` path into the global Codex skill library.

**Reason**

The previous global promotion path still required a staging skill to already exist, then a separate command to promote it globally. That left a gap in the real lifecycle: successful reusable workflows could still be easiest to promote into project active. Adding the target to `distill_and_promote` closes the workflow loop without adding UI or broader platform writes.

**Impact**

- Service, CLI, and MCP `distill_and_promote_candidate` support the global target
- Global target writes `SKILL.md` and `agents/openai.yaml`
- Global target does not create a project active copy or update the active index
- Fast verification now passes 90 tests; search quality remains 23/23

### 2026-05-03 - Reusable Workflow Promotion Defaults To Global Codex Skills

**Decision**

Staging Runtime skills that are tagged as reusable workflows should recommend `promote_global_codex_skill` after a passing audit. This path writes a global Codex `SKILL.md` and `agents/openai.yaml`, and deliberately avoids creating a project `skill_store/active` copy or updating the project active index.

**Reason**

The earlier source-of-truth decision said global Codex skills are authoritative, but the lifecycle still only had a concrete promotion path into project active skills. That would make the old behavior the easiest behavior and would recreate duplicate workflow copies. The promotion path now matches the policy.

**Impact**

- Added `RuntimeService.promote_to_global_codex_skill(...)`
- Added CLI `promote-global-codex-skill`
- Added MCP/host operation `promote_global_codex_skill`
- Passing audits on metadata tagged `workflow`, `global-workflow`, or `codex-skill` now recommend global promotion first, with project active promotion kept as an alternate operation
- Fast verification now passes 87 tests; search quality remains 23/23

### 2026-05-03 - 项目内 Workflow Runtime Skills 降级为全局 Skill Adapters

**Decision**

保留 `skill_store/active` 中的 workflow 条目用于 Runtime 搜索、执行测试和 dashboard 可见性，但它们不再保存完整工作流逻辑。它们现在调用共享 `global_skill_adapter`，执行时只写出全局 Codex skill 的引用报告。

**Reason**

用户确认后续新技能应以全局 Codex skills 为权威来源。如果项目 active skill 继续保存完整流程，就会产生第二份可执行真相。改成薄 adapter 后，Runtime 仍能检索和记录这些 workflow，但真正的流程说明只维护在全局 `C:\Users\Administrator\.codex\skills`。

**Impact**

- 新增 `skill_runtime/execution/global_skill_adapter.py`
- 8 个项目 workflow active skills 现在只返回 `adapter_role: global_codex_skill_adapter`、`global_skill_name`、`global_skill_path`、`source_role: authoritative_global_skill`
- active metadata 已改成 adapter 口径，保留输入 schema 以维持搜索和执行参数提示
- 搜索质量仍为 23/23，快验为 85 tests OK

### 2026-05-03 - Global Codex Skill 是通用工作流的唯一权威来源

**Decision**

后续新建的通用工作流技能默认放到全局 `C:\Users\Administrator\.codex\skills`。项目 `AGENTS.md` 只做路由，Skill Runtime active skill 只做可执行适配、实验、测试和治理，不再作为通用工作流说明的最终归宿。

**Reason**

如果全局 Codex skill 和项目 `skill_store/active` 都保存完整流程，就会形成两份真相，后续修改必然漂移。全局 Codex skill 才能被新会话和其他项目直接发现；项目内只应保留局部约束、引用、索引或薄适配。

**Impact**

- 新增 `docs/global-skill-source-of-truth-policy.md`
- 项目和全局 `AGENTS.md` 都写明新通用 workflow skill 的默认落点是全局 skills 目录
- platform inventory 现在解析全局 `SKILL.md` frontmatter，并将外部 Codex skills 标记为 `source_role: authoritative_global_skill`
- dashboard 平台视图会显示 global skill 的 source role 和 description，帮助区分“权威全局 skill”和“项目/Runtime 适配层”

### 2026-05-03 - Workflow Skills 同步为全局 Codex Skills

**Decision**

将全局 `C:\Users\Administrator\.codex\AGENTS.md` 同步为短规则和 workflow skill routing，并把这批工作流安装到 `C:\Users\Administrator\.codex\skills` 作为全局 Codex skills。全局 skill 名使用 Codex 标准连字符命名，例如 `pre-implementation-workflow-review`；项目内 Skill Runtime active skill 继续保留下划线命名，例如 `pre_implementation_workflow_review`。

**Reason**

只在 `vibe` 的 `AGENTS.md` 和 `skill_store/active` 中保留工作流，会导致其他项目或新 Codex 会话只能看到规则的一部分，无法通过 Codex 的全局 skill 发现机制稳定触发。把流程做成全局 skills 后，方向审核、自动模式、部署判断、handoff、runtime gate、验证选择、仓库影响分析和非技术阶段报告都能跨工作区复用。

**Impact**

- 全局 `AGENTS.md` 保留通用默认规则，并新增全局 workflow skill routing
- 新增 8 个全局 Codex skills：`pre-implementation-workflow-review`、`auto-mode-stage-runner`、`deployment-strategy-review`、`session-handoff-maintenance`、`runtime-gate-workflow`、`runtime-verification-selector`、`repo-impact-analysis`、`nontechnical-stage-report`
- 8 个全局 skills 均通过 `skill-creator` 的 `quick_validate.py`
- 项目 `AGENTS.md` 的路由名已对齐全局 Codex skill 名；直接调用 Skill Runtime active skill 时仍使用 `skill_store/active` 中的下划线名

### 2026-05-03 - AGENTS 只保留常驻规则，长流程下沉为 Workflow Skills

**Decision**

将 `AGENTS.md` 从长操作手册收成短规则和 workflow skill 路由。自动模式、部署策略、session handoff、runtime gate、验证选择、仓库影响分析和非技术阶段报告都转为 active runtime workflow skills。

**Reason**

`AGENTS.md` 原本混合了常驻红线、流程细节和报告模板，导致每次会话都携带过多上下文。真正需要常驻的是“什么时候触发什么流程”，而不是每个流程的完整执行细节。把长流程下沉到技能后，默认上下文更轻，流程仍可复用、可搜索、可测试。

**Impact**

- 新增 7 个 active workflow skills：`auto_mode_stage_runner`、`deployment_strategy_review`、`session_handoff_maintenance`、`runtime_gate_workflow`、`runtime_verification_selector`、`repo_impact_analysis`、`nontechnical_stage_report`
- `AGENTS.md` 保留 workspace purpose、standing rules、skill routing 和 minimal handoff rule
- active skill 数量从 7 增加到 14
- 搜索质量基线扩展到 23/23
- 新增执行测试覆盖这些从 `AGENTS.md` 下沉的 workflow skills

### 2026-05-03 - 开发方向价值门禁沉淀为 Active Skill

**Decision**

新增并升级 `pre_implementation_workflow_review` active skill。它在实现前审核开发方向、候选方案、预期产物、替代路线、已知上下文和用户价值假设，输出 `recommendation`、`risk_flags`、`must_answer_questions`、`research_queries`、`validation_plan`、`stop_condition` 和 JSON 报告。重点不是只拦截低价值本地基础技能，而是把“方向是否有价值、是否值得继续做”放在实现前。

**Reason**

用户指出，低风险本地文件技能在 Codex 日常开发里价值有限，这个判断本应在项目前期路线审核中出现，而不是开发几天后才通过 dashboard 观察反证。用户进一步明确，希望以后给出开发方向时，Codex 先持续询问、搜索、补全和判断方向是否正确、有无价值，直到项目有真正开发意义，再进入实现。需要把这类方向判断变成默认工作流和可复用技能，而不是只靠聊天中的临时反思。

**Impact**

- active skill 数量从 6 个增加到 7 个
- 搜索质量基线新增开工前 review / audit / direction value 查询，当前 16/16 通过
- 项目 `AGENTS.md` 新增 Development Direction Value Gate，要求新方向先审价值、用户、替代方案、成功指标和停止条件
- 该技能不会替代用户决策，但会在实现前明确指出低价值路线、缺少问题验证、已有本地工具重叠、缺少成功指标和需要继续搜索/追问的问题

### 2026-05-03 - 开发工作流进入 Runtime Observation Lane

**Decision**

Codex 默认通道新增 `development-workflow-observation` 家族。它覆盖有明确工作区和明确产物的开发工作流，例如代码、测试、dashboard、文档和配置改动。该家族进入 `default-in`，让 runtime 可以参与检索、观察和收尾学习；但对这类广义开发任务仍建议使用 `allow_silent_reuse=false`，避免未知开发工作被静默自动执行。

**Reason**

用户指出当前 dashboard 中真实项目开发任务基本都是 `skipped`，而此前 `default-in` 的低风险本地文件任务在实际 Codex 开发里价值不高，因为 Codex 自己就能直接用 Python 或本地命令处理。要证明 Skill Runtime 真正参与主线，默认接入点必须覆盖可复用的开发流程，而不是只覆盖简单文件工具。

**Impact**

- 本地开发工作流可以显示为 `entered`，不再只显示为普通 Codex 路径 `skipped`
- 完成后如有结构化执行日志，finalizer 可以捕获 trajectory，并在 dashboard 中形成 `used` 样本
- dashboard 总览新增 `已进入` 指标，区分“runtime 已观察但未自动执行”和“完全跳过”
- 低风险文件技能仍保留，但不再被视为默认接入的唯一代表样本

### 2026-05-03 - GitHub Import 和 Rich UI 继续设计门控

**Decision**

在完成 platform inventory、export preview、local import-to-staging、dashboard provenance、capability collections 和 privacy/provenance 文档后，不默认马上进入 GitHub import 或 rich UI。GitHub/marketplace import 只有在 provenance、凭据、staging-only 和外部数据流边界清楚后才实现；rich UI 只有在静态 dashboard 被真实使用证明不足后才启动。

**Reason**

当前 `skills-manage` 的可借鉴 control-plane 经验已经覆盖了观察、预览、导入候选、组织和隐私说明。继续直接做网络 import 或管理后台，会增加外部 side effect、凭据和 UI 复杂度，而这些需求还没有被真实重复使用证明。

**Impact**

- 新增 `docs/privacy-and-provenance.md`
- README / README.en 增加隐私与 provenance 入口
- 下一步默认回到真实使用观察，而不是自动扩展 GitHub import 或桌面/本地 Web UI

### 2026-05-03 - Capability Collections 是只读组织层

**Decision**

新增 capability collections 作为 `skill_store/collections.json` 支持的持久组织层。集合只引用现有 `skill_name`，dashboard 会解析集合成员、生命周期数量和缺失引用，并新增只读 `能力集合` 页面。没有集合文件时使用默认集合兜底，但不会自动写文件。

**Reason**

dashboard 里的能力组已经证明“按能力理解技能库”比只看原始技能列表更适合用户。但集合不能变成第五种 lifecycle，也不能影响复用、搜索、审核、提升或归档。把集合做成只读 overlay，可以吸收 `skills-manage` 的组织经验，同时保持 Skill Runtime 的治理边界。

**Impact**

- 新增 `docs/capability-collections-design.md`
- 新增 `skill_runtime/collections/model.py` 和 `skill_runtime/collections/store.py`
- dashboard 数据新增 `capability_collections`
- dashboard 新增 `能力集合` 页面
- 下一步推荐补隐私与 provenance 文档，再考虑 GitHub import

### 2026-05-03 - 导入候选必须在 Dashboard 中显示来源和审核状态

**Decision**

本地导入到 staging 的外部 skill 不只写入 metadata，还必须在 dashboard 的候选详情中可见。dashboard collector 会保留 `audit_status`、`import_source`、`imported_at`、`content_hash`、`provenance` 和 `is_imported`；HTML 详情会显示“外部导入”“需要审核”、来源路径和短 hash。该展示仍然只读，不增加 promote、安装或编辑按钮。

**Reason**

如果外部 skill 只进入 staging 但用户看不见来源和审核状态，后续 GitHub/marketplace import 会变成不可解释的黑箱。先让本地导入候选可见，可以验证 provenance 和治理语言是否清楚，再决定是否接网络来源。

**Impact**

- dashboard 能区分普通候选和外部导入候选
- 导入候选的 `requires_review` 状态对用户可见
- GitHub import 继续延后，下一步优先做 capability collections

### 2026-05-03 - 外部 Skill 先本地导入 Staging

**Decision**

第三阶段只支持本地 `import-skill-to-staging --source <path>`，且导入结果只能进入 `skill_store/staging/`。导入会复制外部 `SKILL.md` 目录到 `skill_store/staging/imported/<skill_name>/`，并写入 staging metadata，标记 `audit_status: requires_review`、source path、content hash 和 provenance。不会写入 `skill_store/active/`，不会把外部 skill 变成可静默复用的 active skill。

**Reason**

`skills-manage` 的 import 体验有价值，但 Skill Runtime 的治理边界更重要。外部技能必须先作为候选被观察和审核，不能绕过 audit/promote 生命周期。先做本地导入也避免过早引入 GitHub/marketplace 网络导入和凭据风险。

**Impact**

- 新增 `docs/import-to-staging-policy.md`
- 新增 `skill_runtime/importers/local_skill_importer.py`
- 新增 CLI：`python -m skill_runtime.cli import-skill-to-staging --source <path>`
- 新增测试覆盖本地导入、缺少 `SKILL.md` 拒绝、CLI 输出和不进入 active
- 下一步推荐做 dashboard provenance 展示，再考虑 GitHub import

### 2026-05-03 - Platform Export 先做预览不写目录

**Decision**

平台导出第二阶段只新增 `platform-export-plan` 预览能力，不执行 copy、不创建 symlink、不创建平台目录。只有 `active` 技能可以得到 eligible 预览；staging、archived、rejected 或未知技能都会被标记为 `skill_not_active`。真实目录或文件冲突会被标记为不 eligible。

**Reason**

`skills-manage` 的跨平台安装体验有借鉴价值，但 Skill Runtime 当前主线仍是蒸馏、审核和治理。先做导出预览可以让用户看清目标路径、冲突和 link/copy 计划，同时避免过早引入外部目录写操作风险。

**Impact**

- 新增 `docs/platform-export-policy.md`
- 新增 `skill_runtime/platforms/export_plan.py`
- 新增 CLI：`python -m skill_runtime.cli platform-export-plan --skill <skill> --platform <platform>`
- 新增测试覆盖 active-only、真实目录冲突、只读无写入和 CLI JSON 输出
- 下一阶段如继续吸收 `skills-manage` 经验，应做本地 `import-skill-to-staging`，外部技能仍不能直接进入 active

### 2026-05-03 - 平台与项目 Inventory 第一阶段保持只读

**Decision**

平台与项目 skill inventory 第一阶段只做发现和展示，不创建平台目录、不复制 skill、不创建 symlink、不安装或卸载任何技能。dashboard 新增 `平台与项目` 视图，用来显示 Codex、Claude Code、Cursor、Gemini CLI 和 Shared Agents 等已知平台 skill 目录里的 `SKILL.md` 技能。

**Reason**

当前目标是吸收 `skills-manage` 的 control-plane 可见性经验，而不是把 Skill Runtime 变成写平台目录的管理器。先只读观察可以验证目录模型、归属判断和 dashboard 信息结构，避免过早引入外部目录写操作风险。

**Impact**

- 新增 `docs/platform-skill-inventory-design.md`
- 新增 `skill_runtime/platforms/registry.py`
- 新增 `skill_runtime/platforms/discovery.py`
- dashboard 数据中包含 `platform_inventory`
- dashboard 新增 `平台与项目` 页面
- 下一阶段如继续推进，应先做 `platform-export-plan` 预览命令，仍然不写平台目录

### 2026-05-03 - 吸收 skills-manage 的 Control Plane 经验但不改主线

**Decision**

`iamzhihuix/skills-manage` 的经验应作为 Skill Runtime 的外围 control-plane 参考，而不是作为主产品形态替代。当前只吸收中央技能库、平台目录观察、导出规划、import-to-staging、collections、隐私与 provenance 表达等经验；Skill Runtime 的主线仍然是任务触发、复用、记录、蒸馏、审核、提升和治理。

**Reason**

`skills-manage` 解决的是“已有 skill 资产如何跨平台管理”，而 Skill Runtime 要解决的是“skill 如何从真实任务中生成、沉淀、进化并受治理”。如果直接转向桌面技能管理器，会稀释当前最有差异化的 runtime lane 和学习闭环。

**Impact**

- 新方案写入 `docs/superpowers/plans/2026-05-03-skills-manage-lessons-integration.md`
- 第一阶段推荐做 read-only 平台/项目 inventory，而不是马上做平台写操作
- 外部 skill 导入默认进入 staging，不能绕过 audit 进入 active
- 暂不启动 Tauri 或完整管理后台路线，除非 dashboard/control-plane 静态方案被真实使用证明不够

### 2026-05-02 - GitNexus Windows 查询路径采用降级保活策略

**Decision**

当前本机 GitNexus 继续保留为可用的辅助能力，但在 Windows 查询路径上不再强行加载 LadybugDB FTS/VECTOR 扩展。全局安装包里的临时补丁让 pooled read path 跳过 FTS/VECTOR 加载，并让 BM25 搜索在 Windows 下退回 `CONTAINS` 图扫描。仓库索引已重建到当前提交 `992f36e`。

**Reason**

排查确认：GitNexus 已安装、仓库已注册，之前“没效果”的直接表现是 MCP `Transport closed`，真实根因是 LadybugDB FTS/VECTOR 扩展加载触发 native crash。继续追求完整 FTS/vector 路径会让 MCP 反复被带崩；先保住结构查询、上下文查询和基础关键词查询更有价值。

**Impact**

- `gitnexus status` 当前为 up-to-date
- CLI 的 `cypher` / `query` / `context` 已恢复可用
- 关键词搜索排序质量低于正常 FTS/vector 路径，复杂定位优先用 `cypher` 或 `context`
- 当前 Codex 会话里的 GitNexus MCP transport 已被早先崩溃打断，需要新会话或重启后复测 MCP
- 这些是本机补丁，GitNexus 升级或重装后可能被覆盖，恢复步骤记录在 `docs/gitnexus-local-runbook.md`

### 2026-05-01 - 全局 Dashboard 合并当前项目视图

**Decision**

新增全局 dashboard 时，不再做成和普通 dashboard 割裂的独立页面。`dashboard --global` 仍然显示当前项目的技能树、触发日志和治理快照，同时增加“全局项目”和“全局日志”两页。全局部分只聚合各工作区的 `.skill_runtime/runtime_lane_events.jsonl` 调用记录，不跨项目编辑技能、不做 promote/archive，也不把其他项目的技能库合并到当前项目。

**Reason**

用户需要的是“一个面板里既能看技能树、日志、治理，也能看其他工作区有没有触发 Skill Runtime”。因此全局能力应当是普通观察面板的增强，而不是另一个只显示日志的页面。跨项目问题只需要可见性，不需要跨项目写操作。

**Impact**

- 新命令 `dashboard --global --scan-root <目录>` 会生成统一观察面板
- 同一页面内可看当前项目技能树、当前项目触发日志、当前项目治理快照、全局项目概览和全局触发日志
- 默认只扫描指定目录下一层项目，避免全盘扫描带来的慢和误读
- 后续如果要做跨项目治理或统一 skill registry，需要另起设计，不应塞进这个只读 dashboard

### 2026-05-01 - 开发任务默认先走 Skill Runtime Gate

**Decision**

Codex 做具体项目开发任务时，不再只依赖“已配置 skill_runtime MCP”。新的默认规则是：在实质性读代码、改代码、改文档、改配置、写测试或做项目维护前，先调用 Codex-facing runtime gate。优先使用 `mcp__skill_runtime__.run_codex_task_experimental`；如果 MCP 不可用或没有返回可见 runtime lane 状态，则用 `python -m skill_runtime.cli --root <workspace> codex-run ...` 兜底。任务完成后，如果有结构化执行结果或操作日志，再调用 `finalize_codex_task_experimental`。

**Reason**

过去几天虽然全局 MCP 已配置，但 Codex 没有主动调用 runtime gate，所以 dashboard 没有触发日志，用户也感知不到 runtime 存在。必须把“任务开始先 gate、任务结束可 finalize”写成 Agent 规则，才能从“可调用工具”变成“默认开发流程的一部分”。

**Impact**

- 之后真实开发任务会先产生 `runtime_lane_status` / `runtime_lane_reason`
- dashboard 的触发日志能用于观察 runtime 是否参与
- 广泛或不确定任务默认只观察和分类，不让 runtime 静默接管
- 如果 runtime 不可用，不阻塞开发，只说明本次未走 gate

### 2026-05-01 - 技能树中心节点避开组别卡片

**Decision**

dashboard 技能树的中心“运行时根节点”不再贴近上方组别卡片。布局上将中心节点放到上下分支之间，并拉开上下两排分支的间距，避免视觉重叠。

**Reason**

中心节点如果压到组别卡片，会让用户误以为节点之间存在遮挡或层级错误。技能树应优先保持结构清楚，中心节点需要作为视觉锚点，而不是覆盖组别内容。

**Impact**

- 技能树上下分支之间的留白增加
- 中心节点更清楚地表达“运行时根节点”
- 页面高度略有增加，但换来更稳定的可读性

### 2026-05-01 - 组别展开使用居中详情界面

**Decision**

dashboard 技能树里的能力组点击后，不再在原卡片内直接展开技能列表，也不再把页面滚到下方详情区或打开侧边抽屉。组别卡片保持紧凑，组内技能显示在居中的详情界面中，并提供“收起详情”按钮。

**Reason**

内联展开会把树枝撑长，甚至压到中心节点或其他分支；下方详情面板会改变用户当前视线位置；侧边抽屉容易带来页面和抽屉两个滚动条。居中详情界面能把“总览”和“细节”分开，同时让背景弱化、细节凸显，并锁住页面滚动。

**Impact**

- 技能树点击组别后不会变形
- 打开组别不会触发页面滚动
- 组内技能列表集中在居中详情界面中展示，更适合显示较多候选或归档技能
- 当前仍是只读查看，不增加编辑、提升或归档操作

### 2026-05-01 - 技能树去掉交叉线和硬分界线

**Decision**

dashboard 技能树不再显示中心向外的交叉连接线，也不再在状态分支旁显示硬竖向分界线。结构关系改由中心节点、四象限位置、状态标题圆点和能力组别卡片表达。

**Reason**

交叉线和分界线会让页面看起来杂乱，抢走用户对“有哪些能力组”的注意力。当前用户更需要快速理解能力地图，而不是看到强连接线。

**Impact**

- 技能树视觉更干净，减少线条干扰
- 层级表达更依赖位置、标题和卡片分组
- 如果后续觉得层级不够明显，应优先增加柔和背景区块，而不是恢复硬线条

### 2026-05-01 - 技能树第一层展示能力组别而不是单个技能

**Decision**

dashboard 技能树的状态分支内不再直接铺开单个技能。第一层展示能力组别，例如“格式转换”“文本处理”“文件整理”“运行时治理”。单个技能保留在组别详情中折叠展示，并继续保留原始英文 `skill_name` 作为内部定位信息。

**Reason**

用户要看的不是技能清单，而是这套 runtime 当前具备哪些能力类型。按组别展示能减少视觉噪音，也更接近“能力地图”的产品表达。

**Impact**

- 默认技能树更聚焦能力类别，不再逐个技能堆叠
- 单个技能仍可在组内查看，不丢失排查信息
- 当前分组是 dashboard 展示层规则，不回写 skill metadata 或索引

### 2026-05-01 - 技能树改为分支簇和叶子节点布局

**Decision**

dashboard 的技能树不再把每个技能渲染成纵向长卡片。新的默认形态是：运行时根节点放在中心，active / staging / archived / rejected 四类状态分支分布在四个象限，每个状态分支里用紧凑的叶子节点展示技能；技能说明保留在可展开叶子中，候选和归档分支只展示代表性节点，其余用“还有 N 个”收起。

**Reason**

用户反馈原来的“技能树”仍然像长条列表，不像树。分支簇和叶子节点能更直接表达生命周期分叉，也减少候选和归档技能把页面撑长的问题。

**Impact**

- 技能树视觉上更接近中心向四周发散的枝干结构，而不是长列表
- 默认视图更紧凑，适合快速扫一眼 active / staging / archived / rejected 状态
- 技能中文说明仍保留，但需要展开叶子查看，避免首屏被说明文字挤满

### 2026-05-01 - Dashboard 治理快照拆为独立视图

**Decision**

dashboard 顶部视图从两个扩为三个：`技能树`、`触发日志`、`治理快照`。治理快照不再跟在触发日志页下方，而是作为独立页面式视图，只在用户点击治理入口时显示。

**Reason**

触发日志回答“最近发生了什么”，治理快照回答“技能库是否健康”。两者有关联，但不属于同一类信息。混在一起会让用户误以为治理问题是日志的一部分，降低页面可读性。

**Impact**

- dashboard 信息结构变成三页：技能资产、触发行为、库健康状态
- 后续治理展示可以单独增强，不影响触发日志页面
- 当前仍保持只读，不新增治理按钮或写操作

### 2026-05-01 - Runtime dashboard 的技能树采用状态分支视图

**Decision**

dashboard 的 Skill Tree 不再用单列卡片列表展示技能，而是改为 `Runtime Root -> active / staging / archive / rejected` 的分支结构。每个分支显示完整数量，分支内展示代表性技能节点，过长分支用剩余数量提示收起。

**Reason**

用户需要看到“技能树”的结构关系，而不是换了标题的长列表。按状态分叉更接近真实的技能生命周期，也能让 active 技能、候选技能和历史归档技能的边界一眼可见。

**Impact**

- dashboard 现在更适合用来解释 runtime 里技能处于哪个阶段
- archive 这类长分支不会继续把页面拖成不可读长条
- 当前仍保持只读，不新增编辑、promote、archive 等高风险操作

### 2026-05-01 - Trigger Log 拆成独立 dashboard 视图

**Decision**

dashboard 不再把 Trigger Log 放在 Skill Tree 旁边或同一块内容区域中，而是拆成独立的 `Trigger Log View`。页面顶部增加轻量视图导航，用于在 `Skill Tree View` 和 `Trigger Log View` 之间切换。导航不再使用同页锚点滚动，而是页面式视图切换：默认只显示技能树页，点击触发日志后只显示日志页并回到页面顶部。

**Reason**

技能树回答“系统里有哪些技能、处于什么阶段”，触发日志回答“最近有没有被 Codex 触发、为什么触发”。这两个问题不同，放在同一块区域会让用户把日志误解成技能树的附属信息。

**Impact**

- dashboard 的信息结构更清楚：总览、技能树视图、触发日志视图、治理快照
- 后续优化日志卡片时可以只改 `Trigger Log View`
- 用户点击触发日志时看到的是独立页面式内容，不再是滚动到技能树下方
- 当前仍保持只读，不新增后台服务或写操作

### 2026-05-01 - Dashboard 打开体验采用 CLI `--open`

**Decision**

在现有 `dashboard` 命令上增加 `--open` 参数：

```bash
python -m skill_runtime.cli dashboard --open
```

安装命令入口可用时也支持：

```bash
skill-runtime dashboard --open
```

该参数会先生成 `.skill_runtime/dashboard.html`，再用系统默认浏览器打开生成的本地文件。

**Reason**

用户需要的是“一键打开观察面板”，不是手动找 HTML 文件，也不是新增常驻 Web 服务。复用现有静态 HTML 生成能力并增加打开动作，是最小、低风险、跨平台的实现路径。

**Impact**

- dashboard 仍然是本地静态只读页面
- CLI JSON 输出新增 `dashboard_url` 和 `opened`
- 不引入后台服务、端口占用或写操作风险
- 如果系统默认浏览器无法打开，页面文件仍会生成，可根据 `dashboard_url` 手动访问

### 2026-05-01 - Dashboard 默认采用中文展示

**Decision**

dashboard 的固定界面文案默认使用中文，包括标题、总览、技能树视图、触发日志视图、治理快照、状态标签和空状态提示。技能名称和技能摘要也在 dashboard 展示层转换为中文；内部执行、检索、索引和调用仍使用原始英文 `skill_name`。

**Reason**

当前仓库默认说明已经切为中文，用户也明确要求中文界面。用户看界面时应理解技能用途，而不是被英文 ID 和英文摘要打断；但真正执行技能时必须保持英文 `skill_name`，否则会破坏索引、调用契约和已有技能文件。

**Impact**

- dashboard HTML 标记为 `lang="zh-CN"`
- 状态 badge 从 `active/staging/archived/rejected` 改为中文展示
- 技能卡片展示中文名称和中文说明
- 原始英文 `skill_name` 保留在 HTML `data-skill-name` 中，供内部定位和排查使用
- 当前中文展示是 dashboard 渲染层能力，不会回写 metadata、索引或技能文件

### 2026-05-01 - Runtime dashboard 第一版保持本地静态只读

**Decision**

第一版 dashboard 通过 `skill-runtime dashboard` / `python -m skill_runtime.cli dashboard` 生成本地静态 HTML，不启动常驻 Web 服务，也不提供编辑、promote 或 archive 操作。

**Reason**

当前目标是让用户看见 Skill Runtime 是否参与任务，而不是新增一个高风险管理后台。静态只读页面能先解决“看不见”的问题，同时避免引入权限、误操作和跨工作区聚合复杂度。

**Impact**

- 新增 `.skill_runtime/runtime_lane_events.jsonl` 作为 runtime lane 触发事件日志
- 新增 `.skill_runtime/dashboard.html` 作为默认本地观察面板输出
- 后续如果要加治理按钮、自动打开浏览器或跨工作区汇总，必须在只读观察面板稳定之后单独设计

### 2026-05-01 - 可视化界面第一版采用只读观察面板

**Decision**

第一版可视化界面不做完整后台，也不做 skill 编辑、promote、archive 等操作能力。先做只读观察面板，围绕当前 runtime root 展示：

- 技能树
- runtime lane 触发日志
- 技能状态概览
- 治理风险快照

**Reason**

当前最需要解决的问题是“用户怎么知道 Skill Runtime 有没有工作”，不是新增一个复杂管理后台。只读面板能最快补上可观察性，同时避免一开始就引入误操作、权限、跨工作区聚合和前端服务复杂度。

**Impact**

- 后续实现优先新增本地静态 dashboard 生成能力
- 第一版推荐命令是 `skill-runtime dashboard`
- runtime lane 事件需要自动写入 `.skill_runtime/runtime_lane_events.jsonl`
- 后续只有只读面板稳定后，才考虑治理按钮或跨工作区视图

### 2026-05-01 - Codex 默认通道必须返回触发可见性

**Decision**

Codex-facing orchestration 结果统一返回：

- `runtime_lane_status`
- `runtime_lane_reason`

其中 `runtime_lane_status` 只表达三种状态：

- `used`：runtime lane 实际自动执行了复用技能，或捕获了可沉淀的任务经验
- `entered`：任务进入过 runtime lane 判断，但本次没有实际复用或捕获
- `skipped`：任务留在普通 Codex 路径，没有进入 runtime lane

**Reason**

全局配置和默认规则已经把 Skill Runtime 上收为 Codex 背景能力层，但用户在其他项目里无法判断它到底有没有参与。没有可见状态时，这层能力容易退回“存在但感知不到”的状态，也很难做观察期判断。

**Impact**

- host API、CLI、MCP payload 重建路径都会保留这两个字段
- 观察期可以用这两个字段判断真实任务是否进入或使用 runtime lane
- 这不是扩大能力范围，只是让现有默认通道可解释、可排查
- 后续如果要做更深的 Codex 集成，应继续把可见性保持在结果 contract 中

### 2026-04-30 - 仓库对外描述从 MCP 工具集改写为 Codex 背景能力层

**Decision**

更新仓库主说明，明确这次形态变化不应再表述为“从一个 MCP skill 工具集继续扩展”，而应表述为：

- 本体是 Codex 下方的背景能力层
- MCP、CLI、脚本是接口层和传输层
- 默认产品形态是 `task -> Codex -> runtime gate -> normal execution -> runtime finalize`
- 显式 MCP 工具链退居为手动控制、调试、治理和集成接口

**Reason**

如果仓库主文档还停留在 “MCP tools + skill lifecycle” 口径，那么即使代码和全局配置已经往背景能力层演进，用户和后续新会话仍会把它理解成“一个主要靠手动调用的技能系统”。这会直接把产品理解拉回旧方向。

**Impact**

- README / README.zh-CN 已明确写出：
  - 背景能力层是本体
  - MCP 只是接口层之一
- `docs/codex-integration.md` 已明确写出：
  - 以前是 MCP-first
  - 现在更准确是 Codex-first background capability routing
- `docs/mcp-integration.md` 已明确写出：
  - 该文档只负责接口与 contract，不再充当主产品描述
- 后续对外介绍这套系统时，优先使用“Codex 背景能力层 / runtime lane”口径，而不是“本地 MCP skill 工具集”

### 2026-04-30 - 仓库默认入口改为中文，并补多宿主适配方案

**Decision**

将仓库根入口切为中文默认：

- `README.md` 作为中文主入口
- `README.en.md` 保留英文版

同时新增一份给外部阅读的多宿主适配方案文档，明确这套系统未来如何从 Codex 扩展到其他应用。

**Reason**

当前主要读者和推进语境都以中文为主，仓库默认入口继续用英文会增加理解成本。与此同时，既然已经把产品形态改写成“背景能力层”，就需要一份对外说明文档，清楚解释未来如果适配其他宿主，应该复用 runtime core，而不是再复制出一套新的技能系统。

**Impact**

- 根入口现在默认中文
- 英文说明仍保留在 `README.en.md`
- 新增 `docs/multi-host-adaptation-plan.md`
- README / README.zh-CN / README.en.md 都已补上该文档入口

### 2026-04-30 - skill_runtime 先升级为 Codex 全局默认背景能力

**Decision**

不再把 `skill_runtime` 只当成 `vibe` 仓库内的默认能力。当前先把它升级为 Codex 全局默认背景能力：

- 全局 `AGENTS.md` 改为优先采用 Codex-side runtime lane，而不是手动技能搜索
- 全局 `MEMORY.md` 写入这一偏好
- 全局 `config.toml` 不再把 `skill_runtime` MCP 写死到 `D:/02-Projects/vibe` 根目录
- 改为通过全局启动脚本，优先把当前工作区识别为 runtime root；只有识别不到时才回退到 `vibe`

**Reason**

如果只是当前仓库里有一套默认接入规则，那它还不算真正的底层能力。要让用户在别的工作区也能自然触发这层，就必须把默认触发逻辑和运行根目录选择一起上收成全局行为。

**Impact**

- 新增全局启动脚本：
  - `C:\Users\Administrator\.codex\launch-skill-runtime.ps1`
- 当前已验证：
  - 在 `D:\02-Projects\vibe` 中会解析到 `D:\02-Projects\vibe`
  - 在 `D:\02-Projects\work` 中会解析到 `D:\02-Projects\work`
  - `python -m skill_runtime.cli --root D:\02-Projects\work search --query "test workflow"` 可正常返回空结果而不崩溃
- 这意味着当前已从“仓库内默认能力”升级到“Codex 全局默认背景能力雏形”
- 下一步不再是继续改全局配置，而是进入跨工作区真实使用观察

### 2026-04-30 - Codex 默认通道先进入观察期，再决定是否扩大

**Decision**

在第一处现有入口已经完成阶段性验证点收口之后，当前不继续默认扩大 Codex 默认通道。先进入观察期，并把“何时允许继续扩大到第二处现有入口”的判断标准写入仓库文档。

观察期的核心问题不是“还能不能继续迁移”，而是：

- 当前这条默认通道是否已经在正常使用里带来更顺手的体验
- 它是否会让用户更少感知到底层 runtime，而不是更多

**Reason**

如果现在继续切第二处现有入口，很容易重新回到“为了推进而推进”的节奏。当前更需要确认的是：第一处迁移后的真实使用表现到底值不值得扩大覆盖面。先进入观察期，可以把后续决定建立在真实使用证据上，而不是继续依赖推测。

**Impact**

- 新增 `docs/codex-default-lane-observation-plan.md`
- 新增 `docs/codex-default-lane-observation-log.md`
- 当前默认策略变为：
  - 先观察第一处现有入口
  - 只有在出现明确证据时，才考虑第二处入口迁移
- 后续如果继续扩默认通道，依据将来自观察期结果，而不是“还有入口没切完”

### 2026-04-30 - 第一处 Codex 默认通道先作为阶段性验证点收口

**Decision**

在第一处现有入口 `agent-plan` / `agent-plan-learning` 已经切到 Codex 默认通道，并且完成更大范围验证之后，当前不默认继续切第二处现有入口。先把这一处入口视为阶段性默认路径验证点收口。

这一轮收口覆盖了：

- 快验
- `check_mcp_architecture`
- `check_runtime_contracts`
- CLI 级 `default-in` smoke
- CLI 级 `default-out` smoke
- full slow runtime suite

**Reason**

当前最重要的问题已经不是“Codex 能不能接这层”，而是“第一处现实入口切过去后，值不值得继续扩大默认覆盖面”。既然第一处入口已经通过从快验到全量慢验的完整验证，就不该再为了推进感继续默认切第二处入口。此时更合理的是先把它作为一个稳定验证点收住。

**Impact**

- 新增 `docs/codex-default-lane-stage-closure.md` 作为这一轮正式收口文档
- 当前可明确宣称：
  - 第一处现有入口已经真实迁移到 Codex 默认通道
  - 这一处入口已通过架构、contract、CLI smoke 和 full suite 验证
- 当前不宣称：
  - 所有 Codex 默认入口都已切换
  - 已经适合继续自动扩大到第二处现有入口
- 下一步更适合等待真实使用反馈，或在出现明确价值时再决定是否扩第二处入口

### 2026-04-30 - 第一处现有入口切换后先用更大范围验证收口

**Decision**

在 `agent-plan` / `agent-plan-learning` 切到 Codex 默认通道后，先不立刻继续切第二处现有入口，而是先做一轮更大范围验证：

- `check_mcp_architecture`
- `check_runtime_contracts`
- CLI 级别的 `codex-run` smoke
- CLI 级别的 `agent-plan` default-out smoke

**Reason**

第一处现有入口刚切过去时，最重要的不是继续扩入口数量，而是确认：

- 新旧路径没有互相打架
- default-in 任务真的会进入 runtime lane
- default-out 任务真的会留在普通路径
- contract 和架构约束没有被悄悄破坏

**Impact**

- 当前已确认：
  - MCP architecture check passed
  - Runtime contract check passed
  - `codex-run` 可真实执行 default-in 文本工作流
  - `agent-plan` 可真实把开放式 review 任务留在普通路径
- 当前 `git diff --check` 仍只有既有 LF 换行提示，不是本轮新增失败
- 下一步更适合决定是继续切第二处现有入口，还是把当前入口当作阶段性默认路径验证点

### 2026-04-30 - 第一处现有入口先切换为 Codex 默认通道

**Decision**

先不去碰所有现有入口，第一处正式切换的现有入口选择为：

- `agent-plan`
- `agent-plan-learning`

它们现在默认走：

- `start_codex_task(...)`
- `finalize_codex_task(...)`

而不再直接走旧的纯 agent lifecycle helper。

**Reason**

这两条入口已经最接近“任务开始前给一份计划、任务完成后补回结果”的真实使用方式，又比直接改动更大的默认宿主路径风险低。先切它们，能最小代价证明“已有入口已经开始被 Codex 默认通道接管”。

**Impact**

- 第一处现有入口已经正式改走 Codex 默认通道
- `agent-plan` 现在会携带 `task_classification`
- `agent-plan` 在 `default-out` 任务上会留在普通路径，不再假装都能进入 runtime lane
- 当前快验已更新为 53 个测试通过
- 下一步更适合决定：
  - 是否继续切第二处现有入口
  - 或先停在这里做更大范围验证

### 2026-04-30 - Phase-one default-in 先收窄为四类白名单家族

**Decision**

Codex phase-one 的 `default-in` 不再仅靠“本地 + 低风险 + 工作流”这类宽条件判断，而是先收窄为四类明确白名单家族：

- `project-state-maintenance`
- `local-text-transformation`
- `structured-format-conversion`
- `low-risk-workspace-organization`

只有命中这四类之一的任务，才默认进入 runtime lane。

**Reason**

如果 default-in 仍然过宽，那么后面即使把现有入口正式切过去，也会在边界模糊任务上误判。把第一批任务先收成白名单家族，能让 phase one 真正保持“范围小但可信”，而不是一边接默认入口一边继续猜任务类型。

**Impact**

- `skill_runtime/api/classification.py` 现在先判断是否命中四类 phase-one family
- `default-in` 已从宽条件进一步收成小范围白名单
- 新增测试覆盖：
  - JSON -> CSV 结构化转换
  - 低风险工作区整理
  - 带本地输出路径的外部登录任务仍保持 `default-out`
- 当前快验已更新为 52 个测试通过

### 2026-04-30 - 更真实的 Codex 默认入口先落在 CLI 默认通道

**Decision**

在已有 host API 和 MCP 实验入口之外，先新增一组更接近默认使用方式的 CLI 通道：

- `codex-classify`
- `codex-run`
- `codex-finalize`

它们直接走 Codex 侧分类与默认 runtime lane，而不是继续只保留在实验型 MCP 工具里。

**Reason**

当前需要的不是更多文档，而是一个“比实验工具更真实、又不会一下子改坏所有旧路径”的默认入口。CLI 是最小、最稳、最好验证的接点：它比纯 API 更像实际使用路径，又比直接改写所有默认上层更容易回退。

**Impact**

- Codex 默认通道第一次脱离“只存在于实验型 MCP 工具”的状态
- 现在可以直接通过 CLI 验证：
  - 任务分类
  - default-in 自动进入 runtime lane
  - default-in 任务完成后继续 capture + recommendation
- 当前快验已更新为 49 个测试通过
- 下一步更适合继续收窄第一批 default-in 规则，或决定是否让某个现有入口改走这组 Codex CLI/host 通道

### 2026-04-29 - Codex 默认入口先通过任务分类器接入实验宿主路径

**Decision**

在已有 `run_agent_task_experimental` / `finalize_agent_task_experimental` 之外，新增一条更贴近 Codex 默认行为的实验入口：

- `run_codex_task_experimental`
- `finalize_codex_task_experimental`

它们先走 Codex 侧任务分类器：

- `default-in`
- `guarded-in`
- `default-out`

只有 `default-in` 才自动进入 runtime lane。

**Reason**

光有分类文档还不够，必须先让“按任务类型决定是否进入 runtime”变成真实可运行入口，才能验证 Codex 版本是不是已经开始具备默认接入的产品形态。同时又不应该直接改掉所有现有入口，所以先落在实验宿主路径最稳。

**Impact**

- 新增 `skill_runtime/api/classification.py`
- 新增 host API：
  - `classify_codex_task`
  - `start_codex_task`
  - `run_codex_task`
  - `finalize_codex_task`
- 新增 MCP 实验入口：
  - `run_codex_task_experimental`
  - `finalize_codex_task_experimental`
- 当前快验已扩大到 46 个测试通过
- 下一步应优先把第一批 `default-in` 规则收成更小的 host-side classifier 映射，或者选择是否让某个更真实的默认入口开始调用这条 Codex 路径

### 2026-04-29 - Codex 侧任务先分为 default-in guarded-in default-out 三类

**Decision**

Codex 默认接入 phase one 先采用三桶分类：

- `default-in`
  - 本地、低风险、工作流形态明确、可回退或可清楚解释失败的任务
- `guarded-in`
  - 有一定复用价值，但范围更大、分叉更多、边界更模糊的任务
- `default-out`
  - 开放式对话、高风险操作、外部系统依赖重、主要靠推理而不是靠稳定执行的任务

当前默认只让 `default-in` 自动进入 runtime lane；`guarded-in` 继续保持更高门槛；`default-out` 继续走普通 Codex 路径。

**Reason**

如果不先把任务分桶，后续默认接入会退化成“遇到任务就先试 runtime”，这会把产品形态重新拉回隐式技能搜索，而不是受控后台能力层。三桶分类能把风险控制、产品体验和后续扩张路径一次说清。

**Impact**

- `docs/codex-task-classification-boundary.md` 成为 Codex 默认接入的第一道边界说明
- 后续落代码时，应先实现一个小型 host-side classifier，而不是先改 silent reuse 规则
- 第一处默认入口应只覆盖：
  - 本地文本处理
  - 结构化转换
  - 项目状态文件维护
  - 低风险工作区整理

### 2026-04-29 - Codex 默认接入先采用受控低风险任务通道

**Decision**

当前不把 Skill Runtime 一次性挂到 Codex 的全部默认任务链上。先采用“受控默认接入”：

- 只让低风险、本地、可回退、工作流形态明确的任务默认进入 runtime lane
- 默认接入形态先停在：
  - silent reuse gate
  - 正常任务执行
  - capture + recommendation
- 继续排除：
  - 开放式对话
  - 高风险操作
  - 外部系统依赖重的任务
  - 成功标准不清晰的任务

**Reason**

当前 runtime 已经证明“先做事，再回收经验”这条主线成立，但还没有证明它适合无差别挂到所有 Codex 任务上。如果直接全量默认接入，风险会从“能力还不够成熟”迅速变成“默认产品行为越界”。受控低风险任务通道能让 Codex 版本先获得真实产品意义，同时避免过早把整条主链改得过重。

**Impact**

- Codex 版本的下一步主线正式变成“默认接入方案”，不再是继续扩通用 dogfood 或继续深挖更深自动入库
- `docs/codex-default-integration-plan.md` 成为这条新主线的正式说明
- 后续真正落代码时，应先做 Codex 侧任务分类边界，再选择低风险 default-in 任务集，而不是直接全量切换默认上层

### 2026-04-29 - 当前层先以“capture + recommendation”作为阶段性收口点

**Decision**

当前实验路径先不默认继续推进到自动 `distill/promote`。现阶段把：

- 静默自动复用
- 欠覆盖任务的 plan-only 退回
- 宿主执行后的 trajectory capture
- 明确的后续 recommendation

视为一个可用的阶段性收口点。

**Reason**

到现在为止，这一层已经通过两类验证：

- 演示型文件工作流
- 当前项目的真实维护工作流

这已经足以证明“先做事，再回收经验”这条主线成立。继续默认冲向自动 `distill/promote`，会明显增加生成、审核、入库风险，但并没有同等明确的当前产品收益。

**Impact**

- 当前层被正式视为可用阶段，而不再只是过渡实验
- 后续默认不再继续深入自动入库，除非出现明确产品需求
- 下一步更适合转向：
  - 第二类真实任务验证
  - 或回到更高优先级的主线目标
- `docs/agent-layer-stage-closure.md` 成为这次收口判断的正式说明

### 2026-04-29 - 真实任务 dogfood 先选“更新项目接力文件”

**Decision**

真实任务 dogfood 的第一条验证样本，先选当前项目里最贴近实际使用的维护任务：

- 更新 `HANDOFF.md`
- 更新 `TASKS.md`
- 更新 `DECISIONS.md`

并验证实验路径能否把这类任务在执行后重新接回学习链。

**Reason**

这比继续用纯演示型 JSON/文本转换样本更接近当前项目的真实工作模式，而且不需要开始业务功能开发。它能直接回答一个更重要的问题：当前这层“capture + recommendation”是否已经足够承接你现在最常见的项目维护工作。

**Impact**

- 当前已通过快验证明：
  - 实验路径可以承接“更新项目接力文件”这类真实维护任务
  - finalize 后会真实生成 trajectory
  - trajectory 中保留了 read / write 这类项目维护动作
- 这说明当前层不只适用于演示型文件转换，也能覆盖当前项目管理型 workflow
- 下一步若继续推进，应决定是停在 `capture + recommendation`，还是继续自动衔接到 `distill/promote`

### 2026-04-29 - 实验入口学习承接先采用“计划后收尾”的双步形态

**Decision**

`run_agent_task_experimental` 不负责替宿主发明未知任务的执行过程；当它没有自动复用时，实验路径先返回 plan。宿主完成真实执行后，再通过新增的：

- `finalize_agent_task_experimental`

把执行结果交回 runtime，由它决定是否 capture trajectory，并返回后续蒸馏建议。

**Reason**

当前阶段的关键不是让实验入口一次包办所有事情，而是把“自动复用失败后如何继续学习”这条后半段接起来，同时不破坏“宿主自己完成任务”的边界。双步形态最小、最稳，也最接近真实代理生命周期。

**Impact**

- under-covered workflow 现在可以：
  - 先返回 plan
  - 再在任务完成后交回 execution payload
  - 自动 capture trajectory
  - 返回 `distill_trajectory` 后续建议
- `AgentOrchestrationResult` 现在可携带 `learning_capture_payload`
- 当前已通过快验证明实验入口不只会停下，也会把成功执行重新接回学习链

### 2026-04-29 - 首轮实验入口边界先验证“可回退、会克制、尊重限制”

**Decision**

首轮围绕 `run_agent_task_experimental` 的边界验证，先不扩行为，优先验证三件事：

- 自动执行时是否保留 rollback 操作线索
- 欠覆盖工作流时是否干净退回 plan-only，而不是擅自执行
- 显式关闭 silent reuse 时是否严格尊重

**Reason**

当前实验入口的价值首先不在于“会做更多事”，而在于“不会乱来”。如果这三条边界没有先守住，后面即使继续扩 learning capture 或未知工作流承接，也会把风险叠上去。

**Impact**

- 当前已通过快验证明：
  - 自动执行路径保留了 `rollback_operations`
  - 欠覆盖工作流返回 plan-only
  - `allow_silent_reuse=False` 时不会偷跑
- 当前尚未证明实验入口已经具备完整 post-task learning capture 输出
- 下一步若继续推进，应聚焦 learning capture 和 under-covered workflow 的后续承接，而不是继续增加入口数量

### 2026-04-29 - 首个受控试运行入口选择独立 MCP 实验工具

**Decision**

首个受控试运行入口选择为 MCP 层中的独立实验工具：

- `run_agent_task_experimental`

它直接调用 `skill_runtime.api.host.run_agent_task(...)`，但不替换现有：

- `search_skill`
- `execute_skill`

**Reason**

当前项目已经有 CLI、service helper 和 host facade，但还缺一条“真实宿主会怎么接”的小范围试运行路径。继续扩 CLI 不够真实；直接重写现有 MCP 主流程风险太高。独立 MCP 实验工具同时满足三件事：

- 是真实宿主入口
- 范围小、可回退
- 不会破坏现有默认主线

**Impact**

- 当前已完成首个试运行入口选择，并已落成可运行代码
- MCP 现在新增一个显式实验入口，可验证 agent-first 主线在真实 host 形态下的行为
- 现有 MCP 主流程保持不变
- 下一步应围绕这个实验入口验证是否需要补 rollback / learning capture / unknown-workflow 边界

### 2026-04-29 - 当前不建议立即切换默认上层到新 host facade

**Decision**

当前不建议立刻把默认上层产品路径整体切换到 `skill_runtime.api.host` 这组 facade。它已经足够作为“首选实验路径”存在，但还不足以作为“所有默认上层入口都应改走的新主路径”。

**Reason**

当前 agent-first runtime 已经具备：

- reuse planning
- learning planning
- lifecycle helper
- minimal run-task flow
- host-facing facade

但它还缺少几件把默认路径全面切过去所需的条件：

- `run_task(...)` 仍然只有最小执行策略
- `improve_existing_skill` 还停留在决策层，不是完整 lifecycle
- 未知工作流默认生成质量还不足以支撑无条件默认承诺
- 搜索仍是可用级，不是成熟级

**Impact**

- 现在最合理的定位是“preferred experimental path”，不是“universal default path”
- 下一步应选择一个受控、低风险、可回退的真实宿主路径来试运行 `skill_runtime.api.host`
- 不应继续盲目扩底层，也不应现在就全量切默认上层

### 2026-04-29 - 新增 host-facing API facade 作为更真实宿主入口

**Decision**

新增 `skill_runtime/api/host.py`，对外提供三类更适合宿主直接调用的公开 API：

- `start_agent_task(...)`
- `finalize_agent_task(...)`
- `run_agent_task(...)`

同时把它们导出到 `skill_runtime.api` 公共导出面中。

**Reason**

到上一阶段为止，项目已经有了 service-level 的最小真实任务流，但更真实的外部宿主如果想接入，仍需要自己 import 内部类、实例化 service、决定调用哪个 helper。新增 host-facing facade 后，宿主只需要拿公开 API 即可，不必了解内部拼装方式。这比继续扩 CLI 更接近最终形态，也比直接改 MCP 主流程更稳。

**Impact**

- 现在项目已经有一个不依赖 CLI 的公开宿主入口
- 外部代理可直接调用：
  - `run_agent_task(root, request)`
  - `start_agent_task(root, request)`
  - `finalize_agent_task(root, plan, execution_payload)`
- 新增快验覆盖：host API 可直接跑通最小真实任务流
- 下一步若继续推进，应决定是否需要让某个真实上层调用默认改走这组 facade

### 2026-04-29 - 新增最小真实任务流入口 run_task

**Decision**

在 `AgentOrchestrationService` 中新增最小真实任务流入口：

- `run_task(request)`

这一版行为刻意保持保守：

- 如果 `start_task(...)` 判断为 `auto_execute`，则直接调用现有 `RuntimeService.execute(...)`
- 执行成功后再走 `finalize_task(...)`
- 如果不是 `auto_execute`，则只返回 plan，不替上层发明新的执行策略

**Reason**

到上一阶段为止，系统已经有规则、有 service、有 lifecycle helper，也有 CLI 调用点，但还缺少一个真正能在 service 层把“判断 -> 执行 -> 学习回收”串起来的最小主线。`run_task(...)` 正好补上这个缺口，同时又不会过早变成一个过度聪明的大执行器。

**Impact**

- 现在 service 层已经有比 CLI 更贴近真实代理的最小任务流入口
- 新增快验覆盖：
  - 强匹配工作流会自动执行并回收学习判断
  - 无自动复用条件时只返回 plan，不擅自执行
- 下一步若继续推进，应决定这个 `run_task(...)` 由哪个更真实的宿主入口来调用

### 2026-04-29 - 现有 agent-plan CLI 改为走 lifecycle helper

**Decision**

不再让 `agent-plan` / `agent-plan-learning` 各自直接调用底层单点判断，而是改为：

- `agent-plan` 调 `start_task(...)`
- `agent-plan-learning` 调 `finalize_task(...)`

并允许 `agent-plan-learning` 直接接收上一轮 `plan-json`，把学习判断附着回同一份上层计划对象。

**Reason**

如果 CLI 继续只调用 `plan_reuse(...)` / `plan_learning(...)`，虽然能工作，但上层仍要自己拼任务生命周期。既然 `start_task(...)` / `finalize_task(...)` 已经存在，就应该让现有上层入口真正走这条生命周期，证明它不是只给未来代码预留的空壳。

**Impact**

- CLI 现在已经开始使用更贴近真实代理的双阶段 helper
- `agent-plan` 返回完整 plan 结构，包括：
  - `selected_skill_name`
  - `selected_skill_args`
  - `execution_payload`
- `agent-plan-learning` 可基于已有 `plan-json` 做 finalize，而不是重复构造一份独立请求
- 下一步若继续推进，应考虑哪个更真实的代理入口值得接这套 lifecycle helper

### 2026-04-29 - service helper 先提供 start_task / finalize_task 双阶段接口

**Decision**

在 `AgentOrchestrationService` 里先新增两个更贴近真实代理调用方式的 helper：

- `start_task(request)`
- `finalize_task(plan, execution_payload)`

其中：

- `start_task(...)` 返回一份包含复用判断、选中技能名和已知参数的上层计划对象
- `finalize_task(...)` 在任务结束后把学习判断附着回同一份计划对象

仍然不在这一阶段直接帮上层执行技能，也不自动触发蒸馏链路。

**Reason**

CLI 入口已经证明这套判断能被真实调用，但上层如果还要分别手动拼 `plan_reuse(...)` 和 `plan_learning(...)`，离真实代理使用方式仍有一步距离。先提供双阶段 helper，可以让上层像正常任务生命周期一样接入这套能力，同时避免过早把执行动作和学习动作绑死。

**Impact**

- 上层现在可以用“开始任务 / 结束任务”的方式接入 orchestration
- 新增快验覆盖：
  - `start_task(...)` 返回组合后的上层计划
  - `finalize_task(...)` 把学习判断附着回原计划
- 下一步若继续推进，应开始考虑哪个现有上层流程最适合真正调用这两个 helper

### 2026-04-29 - 第一处真实调用点先接到 CLI，而不是 MCP 主流程

**Decision**

第一处真实调用点先通过 CLI 落地，而不是直接改 MCP 主流程。新增两个最小命令：

- `agent-plan`
- `agent-plan-learning`

它们分别调用：

- `AgentOrchestrationService.plan_reuse(...)`
- `AgentOrchestrationService.plan_learning(...)`

**Reason**

CLI 是当前最小、最安全、最好验证的真实入口。它能证明 orchestration 不只是库内 helper，而是已经有真实调用面；同时又不会过早改变 MCP host-style 主流程，避免把“新策略判断”与“现有主链重接”混在一起。

**Impact**

- 现在项目已经有一个可直接调用的 agent-facing 最小入口
- 新增 CLI 测试覆盖：
  - `agent-plan` 返回复用判断
  - `agent-plan-learning` 返回学习判断
- 下一步若继续推进，应优先考虑把这套入口接到更贴近真实代理的 service helper，而不是立刻重写 MCP 主流程

### 2026-04-29 - 第一版 orchestration service 先只做规划，不直接接管执行

**Decision**

新增 `skill_runtime/api/orchestration.py`，落地第一版 `AgentOrchestrationService`。这一版只实现：

- `plan_reuse(...)`
- `plan_learning(...)`

不在第一步就增加一个会直接执行技能、自动调用蒸馏链路、或重写现有 MCP / CLI 流程的“大一统 orchestrate”入口。

**Reason**

当前阶段的目标是先把“自动复用判断”和“自动学习判断”从文档变成可运行代码，并验证它们能和现有 runtime 共存。若第一步就把执行动作也接进来，变更面会明显扩大，很难分清是策略判断错了，还是整条执行链重构带来的问题。

**Impact**

- 现在项目已经有可运行的 agent-side planning service
- 新增测试覆盖：
  - 强匹配且参数齐全时允许 `auto_execute`
  - 参数缺失时退回 `background_hint`
  - 已有技能干净完成任务时学习决策为 `skip`
  - 具体且成功的欠覆盖工作流可标记为 `new_skill_candidate`
- 下一步不再是继续写规则文档，而是选择一个真实调用点接入 `plan_reuse(...)` / `plan_learning(...)`

### 2026-04-29 - 第一版 orchestration 接口先收口为小边界

**Decision**

第一版 agent-side orchestration 不直接接管整条任务规划链，而是先收口为一个小边界，只负责两件事：

- 任务开始前判断：`skip | background_hint | auto_execute`
- 任务成功后判断：`skip | observed_only | new_skill_candidate | improve_existing_skill`

并在 `skill_runtime/api/models.py` 中先落最小数据模型：

- `AgentTaskRequest`
- `ReuseDecision`
- `LearningDecision`
- `AgentOrchestrationResult`

**Reason**

如果第一步就让新 orchestration 接管完整任务规划，范围太大，容易把“默认复用/默认学习的规则设计”和“整个 agent 执行器重构”混在一起。先把最小边界和数据结构钉住，能更快进入可实现状态，也更不容易返工。

**Impact**

- 后续实现应优先新增一个靠近 `RuntimeService` 的小型 orchestration service
- 第一版重点是决策边界，不是全量代理管理器
- `skill_runtime/api/models.py` 现在已经为这条边界准备了最小请求/决策/结果结构
- 后续如果要接代码，优先实现 `plan_reuse(...)` 和 `plan_learning(...)`

### 2026-04-29 - 自动沉淀先采用“观测优先、蒸馏保守”策略

**Decision**

任务成功后，自动沉淀先采用四种结果分流：

- `skip`：已有技能复用已足够，不新增学习动作
- `observed_only`：只保留 observed task，不立刻蒸馏
- `new_skill_candidate`：生成新的 staging 候选技能
- `improve_existing_skill`：把这次成功任务作为优化已有技能的候选证据

第一版默认策略偏保守：

- 工作流型成功任务默认允许进入 observation
- 纯对话型任务不自动蒸馏
- 已经被强匹配已有技能干净复用的任务，不默认再蒸馏
- 只要对复用价值、稳定输入、风险边界有疑问，就优先停在 `observed_only`

**Reason**

如果“任务成功”就等于“自动新增技能”，active skill 库很快会重新被噪音污染，重复之前已经清理过的问题。当前阶段更重要的是让系统先学会“什么时候值得学”，而不是“逢成功必入库”。

**Impact**

- 后续自动沉淀实现默认会比自动复用更保守
- `observed task` 会成为自动学习的缓冲层，而不是所有成功任务都直接蒸馏
- 下一步 orchestration 接口应返回 `skip | observed_only | new_skill_candidate | improve_existing_skill`
- 后续如果要实现“优化已有技能”，需要给现有 skill lifecycle 增加对应承接路径

### 2026-04-29 - 自动复用先采用“三段式决策带”

**Decision**

自动复用先采用三段式决策带：

- `>= 0.85`：可进入静默自动复用候选，但仍必须通过参数完整性、scope compatibility、风险兼容性三道门
- `>= 0.75` 且 `< 0.85`：只保留为后台提示，不默认自动执行
- `< 0.75`：不复用，直接正常做任务

第一处代码接入点不放在 MCP，而放在 `skill_runtime/api/` 附近的新 agent-facing orchestration / policy 边界上，由它统一决定是否静默调用 `RuntimeService.search(...)` 和 `RuntimeService.execute(...)`。

**Reason**

当前 `RuntimeService.RECOMMENDED_EXECUTION_SCORE = 0.75` 已经足够支持“推荐一个可执行技能”，但还不足以作为“静默自动执行”的默认门槛。自动复用比显式推荐更敏感，必须更保守。同时，若把这套逻辑先塞进 MCP，产品心智仍会停留在工具层，而不是转向代理内部的默认能力层。

**Impact**

- 后续自动复用实现会使用比当前推荐阈值更严格的门槛
- `0.75` 继续可作为“值得提示”的下限，不等于“可以自动执行”
- 下一步应在 `skill_runtime/api/` 增加新的 agent-side policy / orchestration 层
- MCP / CLI 暂不需要先改成主承载层

### 2026-04-29 - Skill Runtime 主形态转向 agent-first 自动沉淀层

**Decision**

从当前阶段开始，不再把“继续增加通用 dogfood 技能数量”作为默认主线。Skill Runtime 的目标主形态改为 agent-first：用户正常提任务，代理优先直接完成任务；runtime 在后台自动判断何时复用已有技能、何时沉淀新技能、何时优化旧技能。MCP、CLI 和治理脚本继续保留，但退居为接口层、调试层和治理层，而不是默认产品形态。

**Reason**

当前 6 个真实 dogfood 样本已经足够证明 `search -> execute -> observed task -> distill -> audit -> promote -> reuse` 这条链路不是假的。继续机械补第 7 个、第 8 个通用样本，已经不能显著提高对核心方向的信心，反而容易把项目推向“手动技能库”心智，偏离用户要的“任务执行时自动形成和优化能力”的目标。

**Impact**

- 后续默认不再追求通用 dogfood 技能数量增长
- 下一阶段主线改为：
  - agent 侧默认复用策略
  - 任务完成后的自动沉淀策略
  - 新技能创建与旧技能优化之间的决策边界
- `docs/agent-first-runtime-architecture.md` 成为这轮架构转向的正式说明
- 后续新增样本只应来自真实任务 dogfood 或明确的回归缺口，而不是为了凑通用样本数量

### 2026-04-29 - 第六个真实 dogfood 技能选择目录文本清洗

**Decision**

新增 `directory_text_cleanup_dogfood` 作为第六个真实 active dogfood skill，并配套嵌套 demo 输入、源 trajectory、audit 记录、active metadata、索引记录、搜索质量样本和执行回归测试。

**Reason**

active 库已有单文件文本替换，但还缺少“批量清理一个目录里的文本文件”这种更接近真实资料整理的场景。目录文本清洗能复用已有 `directory_text_transform` 规则，不新增大功能，同时覆盖 clean / normalize / trailing whitespace 这类常见用户表达。

**Impact**

- active skill 数量从 5 增加到 6
- 搜索质量基线从 11 个检查扩展到 13 个检查
- 快验新增目录文本清洗 dogfood 搜索与执行覆盖
- 当前清洗语义是去掉文件末尾多余空白并统一最终换行，不是逐行格式化；后续如果要做逐行清洗，需要单独设计规则或明确作为新能力

### 2026-04-29 - 第五个真实 dogfood 技能选择单文件文本替换

**Decision**

新增 `text_replace_dogfood` 作为第五个真实 active dogfood skill，并配套 demo 输入、源 trajectory、audit 记录、active metadata、索引记录、搜索质量样本和执行回归测试。

**Reason**

active 库已有文本合并、日志归档、JSON 转 CSV 和目录 JSON 批量转 CSV，但还缺少最常见的“改一个文件里的某段文字”工作流。单文件文本替换能复用已有 `text_replace` 规则，不新增大功能，同时覆盖普通用户常说的 replace / update word 表述。

**Impact**

- active skill 数量从 4 增加到 5
- 搜索质量基线从 9 个检查扩展到 11 个检查
- 快验新增单文件文本替换 dogfood 搜索与执行覆盖
- 由于 `merge_text_files` 使用次数很高，文本类查询可能被 usage boost 干扰；本轮通过更明确的 replace / update / word 描述守住了当前查询命中

### 2026-04-29 - 第四个真实 dogfood 技能选择目录 JSON 批量转 CSV

**Decision**

新增 `directory_json_to_csv_dogfood` 作为第四个真实 active dogfood skill，并配套嵌套 demo 输入、源 trajectory、audit 记录、active metadata、索引记录、搜索质量样本和执行回归测试。

**Reason**

第三个样本已经覆盖单个 JSON 文件转 CSV，但 active 库仍缺少“批量处理整个文件夹”的真实样本。目录 JSON 批量转 CSV 能复用已有 `directory_json_to_csv` 规则，不需要新增大功能，同时可以验证嵌套目录保持相对结构这一类更接近真实工作的场景。

**Impact**

- active skill 数量从 3 增加到 4
- 搜索质量基线从 7 个检查扩展到 9 个检查
- 快验新增目录 JSON 批量转 CSV dogfood 搜索与执行覆盖
- 新增样本仍属于文件类工作流，后续还需要文本清洗、替换等不同类型 dogfood 扩大复用证明

### 2026-04-29 - 第三个真实 dogfood 技能选择 JSON 转 CSV

**Decision**

新增 `json_to_csv_dogfood` 作为第三个真实 active dogfood skill，并配套 demo 输入、源 trajectory、audit 记录、active metadata、索引记录、搜索质量样本和执行回归测试。

**Reason**

当前 active 库已有文本合并和日志归档，仍缺少结构化数据转换样本。JSON 转 CSV 属于常见文件工作流，能复用已有 `json_to_csv` 规则，不需要新增大功能或新规则。

**Impact**

- active skill 数量从 2 增加到 3
- 搜索质量基线从 5 个检查扩展到 7 个检查
- 快验新增 JSON 转 CSV dogfood 搜索与执行覆盖
- active 库仍然较小，后续还需要更多真实 dogfood 样本证明复用价值

### 2026-04-29 - 搜索分词过滤英文停用词

**Decision**

`SkillIndex` 搜索分词时过滤常见英文停用词，例如 `a`、`an`、`in`、`to`、`with`。无关查询不应因为这些低价值词返回弱相关技能。

**Reason**

搜索质量基线发现，`send an email newsletter campaign` 虽然不会产生推荐技能，但仍会因为 `an` 这类停用词返回 `merge_text_files` 的弱匹配结果。这会让用户误以为系统理解了无关需求。

**Impact**

- 无关查询更容易得到空结果
- 现有 merge/archive 正向查询仍通过
- 这是轻量修正，不替代后续更完整的搜索质量评估或语义检索

### 2026-04-29 - 搜索质量先用小型基线评估守住当前能力

**Decision**

新增 `scripts/evaluate_search_quality.py`，用少量代表性查询检查当前 active skill 能否命中预期技能，并把该基线接入 `tests.test_runtime_fast`。

**Reason**

当前搜索仍是轻量关键词评分，不适合立刻大改算法。先建立可重复评估入口，可以在后续增加 dogfood 技能或调整评分时快速发现明显退化。

**Impact**

- 快验会覆盖搜索质量基线
- 当前基线只覆盖现有两个真实 active 技能，不代表完整搜索质量评测
- 后续如果 active 技能库扩充，应同步增加评估样本

### 2026-04-29 - DeepSeek live 闭环 smoke 固化为临时沙箱脚本

**Decision**

新增 `scripts/smoke_deepseek_provider_loop.py` 作为手动 live smoke 入口。脚本要求 `DEEPSEEK_API_KEY` 从环境变量读取，自动创建临时 runtime 沙箱，配置 DeepSeek fallback 和 semantic provider，执行生成、审核、提升、复用，并验证复制文件和 metadata sidecar。

**Reason**

一次性手工命令虽然能证明 API 可用，但不适合后续重复验证。把完整闭环固化为脚本，可以让真实 provider 验收变成可复用操作，同时避免污染仓库真实 active skill 库。

**Impact**

- DeepSeek 完整 provider dogfood 现在有明确手动验证入口
- 该脚本不进 CI，因为它依赖真实 API key 和网络
- smoke 过程中发现并修正了 `write_json` 签名契约错误：真实参数是 `payload`，不是 `data`
- 最新真实 smoke 结果：生成、审核、提升、复用均通过

### 2026-04-29 - DeepSeek fallback 失败时允许一次自动返修

**Decision**

DeepSeek fallback provider 在本地质量门禁失败后，默认把具体失败原因和上一版候选 JSON 发回 DeepSeek，请模型修复一次；修复后的候选仍必须通过同一套本地门禁。`DEEPSEEK_REPAIR_ATTEMPTS=0` 可关闭返修。

**Reason**

真实 live smoke 已证明 DeepSeek 会偶发生成调用签名错误的代码。只拦截会保证安全，但用户每次都需要手工重试；允许一次受控返修，可以用本地门禁的具体错误指导模型修正，同时仍避免坏候选进入 staging / promote。

**Impact**

- 默认多一次 DeepSeek API 调用，仅在首次候选未过门禁时发生
- 修复不绕过本地门禁，失败后仍明确退出
- 快验新增一次返修成功和返修关闭两个回归测试
- 真实 API 本轮 smoke 返回了可直接通过门禁的候选，没有触发返修

### 2026-04-29 - DeepSeek fallback 输出必须先过本地质量门禁

**Decision**

DeepSeek fallback provider 在返回生成代码前，必须先通过本地质量门禁。门禁检查 Python 语法、`run(tools, **kwargs)` 入口、三段式 docstring、轨迹对应 runtime tool 调用、`input_schema` 声明的 kwargs，以及 `RuntimeTools` 常用方法的真实调用签名。

**Reason**

真实 live smoke 发现 DeepSeek 会生成看似合理但运行必失败的代码，例如 `tools.copy_file(destination_path=...)` 或 `tools.write_json(metadata_path=...)`。这些问题不能等到 promote 后复用时才发现，必须在 fallback provider 返回前就拦住。

**Impact**

- 坏输出不再进入 staging / audit / promote
- 快验新增 DeepSeek 质量门禁回归测试
- 当前门禁只负责拦截，不负责自动修复
- 下一步应增加一次修复请求，用门禁失败原因指导 DeepSeek 重新输出

### 2026-04-29 - DeepSeek live smoke 后先补本地质量门禁

**Decision**

DeepSeek provider 已经真实连通，但暂不把它标记为稳定核心闭环能力。下一步先为 DeepSeek fallback 输出增加本地质量门禁，至少检查生成代码是否包含 `run`、docstring 结构、轨迹对应 runtime tool 调用和必要 kwargs；不满足时应失败或触发一次修复请求，而不是继续盲目 promote / reuse。

**Reason**

真实 live smoke 结果显示模型输出有波动：出现过通过审核、审核挡住、以及 promote 后复用未产出目标文件的情况。继续重试只会消耗额度，不能提升稳定性。把可验证的结构要求放在本地门禁里，比完全依赖模型自觉遵守 prompt 更可靠。

**Impact**

- DeepSeek API 接入层可继续保留
- 当前不能宣称 DeepSeek provider 端到端稳定可用
- 后续工作重点从“能否调用 API”转为“模型输出能否被本地验证和修复”
- 本轮确认用户提供的 key 没有写入仓库文件

### 2026-04-29 - DeepSeek 接入采用命令型 provider 示例，不保存 API key

**Decision**

新增 `examples/providers/deepseek_fallback_provider.py` 和 `examples/providers/deepseek_semantic_review_provider.py`，通过 DeepSeek OpenAI-compatible Chat Completions API 接入 fallback 生成和 semantic review。默认模型为 `deepseek-v4-flash`，API key 只从 `DEEPSEEK_API_KEY` 环境变量读取，不写入仓库、文档示例或测试。

**Reason**

项目已有命令型 provider 契约，继续沿用这个边界能用最小改动接入真实模型，同时不把 runtime 核心绑定死到某一家 SDK 或新增依赖。用户提供的 key 已出现在聊天中，不能再沉淀到项目文件里。

**Impact**

- DeepSeek provider 可以通过 `SKILL_RUNTIME_FALLBACK_PROVIDER_CMD` 和 `SKILL_RUNTIME_SEMANTIC_PROVIDER_CMD` 启用
- 测试使用本地假 DeepSeek API 验证请求格式和响应解析，不依赖真实 key 或真实网络
- 后续 live smoke 需要用户先在本地环境设置轮换后的 `DEEPSEEK_API_KEY`
- 如果 DeepSeek 返回质量不稳定，下一步需要补 provider 输出质量约束或更严格的审核边界

### 2026-04-29 - 先用仓库内本地 demo provider 固化 provider 接口闭环

**Decision**

新增仓库内本地 demo provider：`examples/providers/copy_metadata_fallback_provider.py` 和 `examples/providers/pass_semantic_review_provider.py`。现有 provider dogfood 测试改为直接调用这些示例脚本，而不是在测试过程中临时写 provider 脚本。

**Reason**

上一阶段已经有外部命令 provider 契约，但新用户 clone 后仍看不到一个可直接运行的 provider 后端示例。把最小 provider 示例放进仓库，可以证明真实 provider hook 从配置、生成、审核、入库到复用都可运行，同时不引入云 API key、新依赖或更大的功能面。

**Impact**

- fresh clone 用户可直接按文档配置本地 demo provider
- 快验中的 provider dogfood 覆盖仓库内真实示例脚本
- 本地 demo provider 只覆盖窄场景文件复制和 metadata sidecar，不代表通用 LLM 生成能力
- 下一步仍需选择是否接 OpenAI、本地模型，或继续保持 provider 命令契约由宿主自带

### 2026-04-29 - Contract 检查沙箱默认不复制历史运行产物

**Decision**

`scripts/check_runtime_contracts.py` 的隔离沙箱默认只复制 contract 验证真正需要的 `demo`、`skill_store`、`trajectories`，并创建空的 `audits`、`observed_tasks`、`output` 目录；只有显式传入 `copy_runtime_history=True` 时才复制历史运行产物。测试沙箱复制 `skill_store` 时也跳过 `__pycache__`。

**Reason**

全量测试反复超时的最大慢点不是业务逻辑，而是 contract 检查每次都复制大量历史 observed task、output 和缓存文件。默认不复制这些历史产物，可以保持验证语义不变，同时大幅降低本地文件复制成本。

**Impact**

- `check_runtime_contracts.py` 从约 47-52 秒降到约 12 秒
- full runtime suite 从约 11 分钟降到约 9 分钟
- 新增回归测试保证默认隔离沙箱不会把历史运行产物带进验证
- 如果未来确实需要验证历史运行产物复制行为，可显式启用 `copy_runtime_history=True`

### 2026-04-29 - Runtime 验证拆分快验和全量慢验

**Decision**

新增 `tests.test_runtime_fast` 作为日常快验入口，保留 `tests.test_runtime` 作为发布级全量慢验入口；新增 `scripts/profile_runtime_tests.py` 用于定位慢测试。README、TESTS、AGENTS 和 CI 都明确区分两类验证。

**Reason**

全量 runtime suite 当前约 11 分钟，继续把它当作每次小改动的默认验证会导致本地执行反复撞短超时，也会拖慢反馈。快验保留最关键的用户闭环和安全边界，让日常迭代先得到快速结果。

**Impact**

- 日常验证可先跑 `python -m unittest tests.test_runtime_fast -v`，当前约 10 秒
- 全量验证仍跑 `python -m unittest tests.test_runtime -v`，当前约 11 分钟
- 慢测试定位可跑 `python scripts/profile_runtime_tests.py --suite tests.test_runtime --top 20`
- CI 先跑快验，再跑全量，既有快速失败信号，也保留完整保护

### 2026-04-29 - 真实 provider 路径先采用可信本地命令契约

**Decision**

fallback distillation 和 semantic audit 的真实 provider 接入先采用外部命令契约：runtime 通过 stdin 发送结构化 JSON 请求，provider 命令通过 stdout 返回结构化 JSON 响应。未配置环境变量时继续使用内置 mock provider。

**Reason**

这样可以先打通真实 provider 的工程边界，而不把核心 runtime 绑定到某一家云服务、某种 API key 或某个本地模型实现。OpenAI、本地模型、企业内部审核器都可以包装成同一类本地命令，测试也能稳定验证。

**Impact**

- 新增 `SKILL_RUNTIME_FALLBACK_PROVIDER_CMD` 和 `SKILL_RUNTIME_SEMANTIC_PROVIDER_CMD`
- 未知工作流在配置可信 provider 后可走生成、审核、入库、复用闭环
- mock provider 仍是安全默认值，不会因为这次改造自动放行模板技能
- provider 命令被视为可信本地命令，不能指向未审核脚本
- 当前还没有内置 OpenAI 或本地模型 provider，只完成了可插拔接入路径

### 2026-04-29 - mock fallback 默认不作为可自动晋级的核心能力

**Decision**

当前把 mock fallback 视为候选技能生成和提示产物，不视为可自动晋级到 active 的可靠核心能力。未知工作流如果只命中 mock fallback，必须被审核挡住，除非后续接入明确可信的真实 provider 或另行设计人工确认边界。

**Reason**

mock fallback 生成的是模板化技能，它能帮助暴露“未知工作流需要 provider”的缺口，但不能证明真实自动生成能力已经完成。如果允许这类候选直接提升，会把看似可复用但实际没有真实动作的技能放进 active 库，污染搜索和复用结果。

**Impact**

- 新增核心验收保证未知工作流进入 mock fallback 后不会自动提升
- 当前核心主线的下一步从“是否需要收紧 fallback”变为“是否接真实 provider”
- 在真实 provider 未接入前，不应宣称未知工作流自动生成已经完成

### 2026-04-28 - 核心 dogfood 验收先覆盖真实 MCP 主链路

**Decision**

第一条核心 dogfood 验收不新增业务能力，而是用 MCP host-style 调用串起现有主链路：搜索已有技能、执行、生成 observed task、从 observed task 提升为 active skill、再次复用，并检查 active 搜索结果没有 fixture-tier 污染。

**Reason**

此前已有很多单点测试，但用户关心的是核心功能本身是否建设完成。单点测试不能直接证明“从用户角度的一整条闭环能不能跑通”。先用真实 MCP 工具调用做验收，比继续补外围安装/文档更贴近核心主线。

**Impact**

- `tests.test_runtime` 会跑到新的核心 dogfood 验收
- MCP smoke 从“能构造 server”进一步扩展到“一条真实 host-style 闭环能跑通”
- 当前验收仍不证明 mock semantic audit / mock fallback provider 已经足够，下一步应补 fallback 路径验收

### 2026-04-28 - 主线从产品化收敛切回核心闭环验收

**Decision**

当前不把安装、CI、README、MCP smoke 和治理清理视为“核心功能完成”。Skill Runtime 只达到可用本地 MVP，下一步主线应回到核心闭环验收，优先证明 `search -> execute -> observed task -> distill -> audit -> promote -> reuse` 在真实 dogfood 任务上稳定成立。

**Reason**

上一阶段解决的是“别人 clone 后能装、能测、能 smoke、active skill 不被测试数据污染”的产品化基础问题，但这不能替代核心能力完成度判断。当前代码里仍存在默认 mock semantic review、默认 mock fallback distillation、轻量关键词检索、active skill 样本较少等核心缺口。

**Impact**

- 后续主线先做核心 dogfood 验收包，而不是继续扩展外围产品化事项
- 不新增大功能，先建立真实闭环的通过/失败标准
- 只有验收暴露出明确短板后，再决定升级真实 provider、搜索质量或 MCP host round-trip

### 2026-04-28 - Clone 后验证路径优先使用模块入口

**Decision**

README / README.zh-CN 中的 clone 后验证流程优先展示 `python -m skill_runtime...` 模块入口，同时保留安装后的 `skill-runtime` / `skill-runtime-mcp` 命令入口和旧脚本入口。为保证文档可执行，补齐 `skill_runtime.cli` 与 `skill_runtime.mcp_stdio` 的 `__main__` 调用，并新增回归测试。

**Reason**

安装后的 console scripts 在部分 Windows shell 中可能因为 Scripts 目录不在 `PATH` 而暂时不可见；模块入口更稳定，适合作为新用户从 clone 到验证的默认路径。但此前模块入口只可 import，直接 `python -m` 不会执行主函数，导致文档路径不可靠。

**Impact**

- 新用户可按 README 从安装一路验证到 MCP smoke 和搜索 smoke
- `python -m skill_runtime.cli search ...` 会真实输出搜索结果
- `python -m skill_runtime.mcp_stdio --help` 会真实显示帮助
- 安装后的 console scripts 和旧脚本入口继续保留

### 2026-04-28 - 提交项目规则并规范化 skill_store 文本文件

**Decision**

将 `AGENTS.md` 中已经生效的新会话接力、自动模式和 GitNexus 使用规则作为正式项目规则提交；同时按 `.gitattributes` 对 `skill_store` 下的文本文件做一次规范化，清理此前长期显示为修改状态的换行噪音。

**Reason**

工作区剩余差异里，`AGENTS.md` 是真实项目规则，不应继续悬空为本地改动；`skill_store/staging` 这批 metadata 则主要是 Windows 换行状态造成的噪音，不处理会持续干扰用户判断仓库是否真的发生了业务变化。

**Impact**

- 项目级接力和自动模式规则成为仓库内正式状态
- `skill_store` 的文本文件更符合当前 `.gitattributes` 规则
- 后续 `git status` 更容易暴露真正有意义的改动
- 没有改变 runtime 行为和业务功能

### 2026-04-28 - 治理维护动作保存索引时合并最新状态

**Decision**

对 `archive_cold`、`archive_duplicate_candidates`、`archive_fixture_skills` 以及 provenance 回填这类治理维护动作，不再在最后用一份旧的 skill 列表整包覆盖 `skill_store/index.json`。改为读取当前最新索引后按 `skill_name` 合并更新，再保存。

**Reason**

当前主线风险已经从“功能缺失”转成“维护动作之间互相覆盖”。如果一个治理动作开始后，期间又有另一项索引变化发生，最后那次整包保存就可能把中途新增或更新的索引项盖掉。

**Impact**

- 连续治理动作之间更不容易互相覆盖索引结果
- 新增了回归测试，专门覆盖“归档过程中出现晚到索引更新仍能保留”
- 现有治理 contract 不需要新增用户可见参数
- 当前完整验证已通过：
  - `python scripts/check_mcp_architecture.py`
  - `python scripts/check_runtime_contracts.py`
  - `python -m unittest tests.test_runtime -v`
  - 结果：346 tests OK

### 2026-04-28 - 将 active skill 使用统计移到本地运行状态文件

**Decision**

保留 active skill 的使用统计能力，但不再把执行产生的 `usage_count / last_used_at` 直接写回版本管理下的 `skill_store/index.json` 和 `skill_store/active/*.metadata.json`。改为把这类运行态统计写到本地 `.skill_runtime/usage.json`，并在读取 skill 索引时叠加到内存视图中。

**Reason**

当前最真实的工作区脏状态来自日常 dogfood 执行会改写版本文件，而不是代码本身真的发生了产品变更。把“技能定义”和“本地使用痕迹”拆开，既保留检索和排序需要的 usage 信号，也避免正常运行持续污染仓库状态。

**Impact**

- 正常执行 skill 后，使用统计仍会累积
- 搜索和索引读取仍能看到最新 usage 信息
- 默认不再改写版本管理下的 active metadata 和主索引文件
- 本地统计写入 `.skill_runtime/usage.json`，并通过 `.gitignore` 忽略
- 当前完整验证已通过：
  - `python scripts/check_mcp_architecture.py`
  - `python scripts/check_runtime_contracts.py`
  - `python -m unittest tests.test_runtime -v`
  - 结果：345 tests OK

### 2026-04-28 - 用仓库规则和忽略项收口本地杂项边界

**Decision**

新增仓库级 `.gitattributes`，统一 `md / py / json / toml / yml` 为 LF；同时把 `.claude/` 视为本地辅助目录加入 `.gitignore`，并将 `docs/gitnexus-local-runbook.md` 作为正式仓库文档保留，而不是继续悬空为未跟踪文件。

**Reason**

当前工作区的“脏状态”里，既有真实运行统计更新，也有 Windows 换行差异和本地辅助目录噪音。如果不先把这些边界说清楚，用户很难分辨哪些是正常运行痕迹，哪些只是本地环境噪音。

**Impact**

- 未来 clone / checkout 后，文本文件的换行规则更一致
- `.claude/` 这类本地辅助目录不再干扰仓库状态判断
- GitNexus 本机恢复说明现在正式纳入仓库，可随项目一起交接
- 当前工作区剩余差异更集中到真实运行统计和个别历史本地改动，后续更容易继续收口

### 2026-04-28 - 安装入口使用包内模块并同时保留旧脚本兼容

**Decision**

将 CLI 和 MCP stdio 启动逻辑收敛到 `skill_runtime.cli` 与 `skill_runtime.mcp_stdio` 两个包内模块里，通过 `pyproject.toml` 暴露正式命令入口 `skill-runtime` / `skill-runtime-mcp`；同时保留 `scripts/skill_cli.py` 与 `scripts/skill_mcp_server.py` 作为薄包装兼容层，不要求现有仓库内用法一次性迁移。

**Reason**

当前项目已经具备功能，但安装后仍主要依赖仓库脚本路径，产品感不完整，而且 `pyproject.toml` 只列顶层包，对安装产物也不够稳。把正式入口收回包内模块，同时保留旧脚本兼容，是收口成本最小、对现有使用者最不打扰的路径。

**Impact**

- 安装后可直接使用：
  - `skill-runtime`
  - `skill-runtime-mcp`
- 也可用更稳的模块入口：
  - `python -m skill_runtime.cli`
  - `python -m skill_runtime.mcp_stdio`
- 旧入口仍兼容：
  - `python scripts/skill_cli.py`
  - `python scripts/skill_mcp_server.py`
- `pyproject.toml` 已改为递归发现 `skill_runtime*` 包，降低安装缺子包风险
- 本轮验证已覆盖：
  - `python -m pip install -e .`
  - `python scripts/check_mcp_architecture.py`
  - `python scripts/check_runtime_contracts.py`
  - `python -m unittest tests.test_runtime -v`
  - 安装后入口 `--help`

### 2026-04-28 - runtime 测试默认使用隔离副本而不是直接写真实仓库

**Decision**

将 `RuntimeTestCase` 的默认运行根切到临时隔离副本；只有少量需要验证目录生成行为的测试模块，才把 `ROOT` 显式映射到隔离副本。与此同时，让搜索、治理和部分生命周期测试自己准备需要的样本技能，而不是继续依赖历史测试留下的 active skill 污染状态。

**Reason**

当前主线目标之一是“别人 clone 后能验证”，而不是“测试一跑就把仓库越跑越脏”。如果验证默认会改写真实 `skill_store`、`observed_tasks` 或隐式依赖旧的脏数据，那么 CI 和本地验证都不稳定，active library 清理后的产品承诺也站不住。

**Impact**

- `tests.test_runtime` 现在默认在隔离副本里运行 runtime service、CLI 和 MCP smoke
- 目录生成类测试仍能在隔离副本里按原样验证输出文件行为
- 搜索与治理测试会自己播种 `experimental / fixture` 样本，不再要求真实 active library 被测试技能污染
- `python -m unittest tests.test_runtime -v` 当前已通过 342 个测试
- 仓库里此前已经存在的历史验证产物仍需后续单独清理，但本轮修复后默认验证不应继续扩大这类污染

### 2026-04-28 - active skill 清理后立即重建索引

**Decision**

在完成 active skill 归档清理后，立即重建 active index，而不是只依赖前面的归档动作逐步更新索引状态。

**Reason**

这样可以确保治理报告和搜索结果直接对齐到文件系统里的真实 active skill 集合，避免“文件已归档，但旧索引仍把测试技能当 active”的残留污染。

**Impact**

- 当前 active library 已收敛到 2 个 stable 技能：
  - `merge_text_files`
  - `archive_log_files_dogfood`
- 当前治理报告无 duplicate candidates
- 当前搜索结果不再被 fixture / demo / alias-rule 技能污染

### 2026-04-28 - active skill 清理优先保留 dogfood 与 canonical 技能

**Decision**

执行 active skill 清理时，优先归档 fixture、demo、rule-test、alias-rule、promote-smoke 类技能，明确保留真实 dogfood 技能和 canonical 技能。

**Reason**

这样可以先解决“active skill 污染搜索结果”的产品问题，同时避免误删仍有真实使用价值的主线技能。

**Impact**

- 已保留：
  - `merge_text_files`
  - `archive_log_files_dogfood`
- 已归档大量 fixture / duplicate / experimental 噪音技能
- active skill 默认搜索面已大幅收敛

### 2026-04-28 - 本轮先做产品化收敛，不新增大功能

**Decision**

本轮继续围绕安装、CI、MCP smoke、rollback 一致性和 active skill 治理做产品化收敛，不新增新的大能力面。

**Reason**

当前项目已经具备可用主线，下一步更重要的是让别人 clone 后能装起来、CI 能验证、MCP 能最小 smoke、搜索结果不被测试技能污染。

**Impact**

- 已新增最小 `pyproject.toml`
- README 中已有本地安装与最小验证步骤
- CI 会先执行 `python -m pip install -e .`
- 当前阶段剩余的主要拍板项是 active skill 治理清理

### 2026-04-28 - copy_file 复用现有 delete_created_file 回滚策略

**Decision**

不扩展 `rollback_operations` 去新增 `delete_copied_file`，而是把 `RuntimeTools.copy_file` 在“新建复制目标”场景下的 rollback strategy 改为现有的 `delete_created_file`。

**Reason**

这是更小、更稳定、对现有 contract 破坏最少的方案，同时能让 rollback hint 与实际自动回滚能力保持一致。

**Impact**

- 新建复制目标时，自动回滚会删除复制出来的文件
- 覆盖已有目标时，仍保持 `manual_restore_required`
- MCP / CLI / service 的 rollback 承诺现在一致

### 2026-04-28 - 当前阶段先收口基础设施，后续直接使用 GitNexus

**Decision**

当前阶段不再继续深挖 GitNexus 的长期底层修复，而是先把已经可用的结果收口，后续直接在真实任务中使用当前仓库已建好的 GitNexus 能力。

**Reason**

这样可以避免继续在低价值的底层整理上投入时间，先把已经打通的能力转化为后续任务中的实际效率收益。

**Impact**

- 当前 GitNexus 基础设施阶段视为完成
- 后续如果没有新的明确需求，不继续扩展本机补丁范围
- 新会话恢复后，默认优先使用当前已建好的 GitNexus 索引辅助任务

### 2026-04-28 - 将本机 GitNexus 补丁整理为仓库内 runbook

**Decision**

把当前成功依赖的 GitNexus 本机补丁点、验证方式和恢复步骤写进仓库内文档，而不是只保留在聊天记录里。

**Reason**

这样在重装、升级、换机器或开新会话后，可以直接按文件恢复，不需要再从零回忆这次排查过程。

**Impact**

当前仓库已经有一份可直接复用的操作说明：
- `docs/gitnexus-local-runbook.md`
- 后续若 GitNexus 重装、升级或迁移机器，可先按 runbook 恢复，再判断是否需要继续做更长期修复

### 2026-04-28 - 当前仓库采用本机补丁加单线程方式完成 GitNexus 注册

**Decision**

当前仓库的 GitNexus 索引先采用“本机最小补丁 + 单线程索引”的方式完成注册，而不是继续强求默认路径一次解决所有底层问题。

**Reason**

这样可以先拿到一个可用结果，确认仓库已经能被 GitNexus 查询，再决定是否继续处理更底层、更通用的长期修复。

**Impact**

当前 `vibe` 仓库已经成功注册并处于 `up-to-date` 状态；但这次成功依赖本机 GitNexus 安装中的临时修改，包括：
- Python 重解析路径补充 tree-sitter `bufferSize`
- `runFullAnalysis` 透传 `skipWorkers`
- 暂时跳过 VECTOR 扩展加载
- 使用单线程索引路径完成注册

### 2026-04-28 - 先拆开验证“分析阶段”和“写库阶段”

**Decision**

将 GitNexus 的“代码分析”和“LadybugDB 写入”拆开分别验证，而不是继续只跑整条 `gitnexus analyze` 命令。

**Reason**

这样可以快速判断问题是在前半段代码理解，还是后半段数据库落盘。当前结果已经证明：前半段在单线程模式下可以完整跑通，真正阻塞点在 LadybugDB / lbug 的写入阶段。

**Impact**

后续排查重点从 Python 解析切换到 LadybugDB / lbug。当前最值得验证的是：是否因为 VECTOR 扩展加载副作用导致后续 `COPY` 失败。

### 2026-04-28 - 先做本机最小补丁验证 GitNexus 根因

**Decision**

在不改业务代码的前提下，先对本机 GitNexus 安装做最小补丁验证：给 Python scope capture 的重解析路径补上 tree-sitter `bufferSize`，并打通 `runFullAnalysis -> runPipelineFromRepo` 的选项透传，用于验证 `skipWorkers`。

**Reason**

当前问题首先需要确认是仓库内容问题，还是 GitNexus 自身实现问题。最小补丁可以快速证明根因，避免在业务仓库里做无价值试错。

**Impact**

已确认第一层失败并非仓库代码语法问题，而是 GitNexus 的 Python 重解析路径缺少 `bufferSize`；在单线程模式下，索引流程已能越过原来的 Python 失败点并推进到 LadybugDB / lbug 写入阶段。后续仍需继续排查写库阶段问题。

### 2026-04-28 - GitNexus 先全局接入，再按仓库逐步验证

**Decision**

先将 GitNexus 安装并接入 Codex 全局配置，让它成为默认可用能力；如果某个仓库索引失败，不阻塞其他工作，先把失败点记录到项目状态文件中，再决定是否专项排查。

**Reason**

这样可以先完成“全局可用”这个基础能力，同时避免因为单个仓库的索引异常卡住整个流程。

**Impact**

后续在支持正常索引的仓库中可以直接优先使用 GitNexus；当前 `vibe` 仓库则需要先处理 `gitnexus analyze` 的失败问题，短期内仍可能回退到普通文件检索。

### 2026-04-28 - 自动模式按阶段汇报且面向非技术用户

**Decision**

自动模式不再采用“持续执行但全程静默”的方式。改为按有意义阶段连续推进，并在每个阶段结束后输出面向非技术用户的阶段报告，同时更新 `HANDOFF.md`、`TASKS.md`、`DECISIONS.md`。

**Reason**

用户没有系统编程基础，仅靠技术术语或零散进度无法判断项目实际进展。阶段报告需要直接解释“做了什么、带来了什么能力、有什么风险、下一步怎么选”，这样用户才能拍板。

**Impact**

后续自动模式下，Codex 需要以产品和结果导向组织汇报，而不是以文件、测试或代码细节为主；同时每轮阶段结束都要同步刷新仓库内状态文件，保证新会话可接力。

### 2026-04-28 - 使用仓库内状态文件承接新会话上下文

**Decision**

将 `HANDOFF.md` 作为新会话默认入口，将 `TASKS.md` 和 `DECISIONS.md` 作为辅助状态文件，要求 Codex 在继续任务时优先读取这些文件，而不是依赖旧对话历史。

**Reason**

这样可以把长期上下文沉淀在仓库内，降低对单个聊天线程的依赖，并避免每次开新会话都重新整理长篇交接提示。

**Impact**

后续每个重要阶段、决策和阻塞都需要同步更新这些文件；新会话可以直接用简短启动语恢复上下文，但前提是状态文件保持最新。

### 2026-05-03 - 技能进化先做候选提案，不自动改全局技能

**Decision**

Skill Runtime 的技能进化第一版只生成 `improve_existing_skill_candidate` 候选。候选记录到 `.skill_runtime/evolution_candidates/*.json`，dashboard 只读展示；不会因为一次任务直接修改 `C:\Users\Administrator\.codex\skills` 下的全局技能。

**Reason**

用户明确要的是“以后少犯错、技能能吸收经验”，但之前已经出现过不断加技能、不断验证样本的低价值循环。把进化先做成候选提案，可以让系统优先改进已有技能、避免重复蒸馏，同时保留人工审核和审计边界。

**Impact**

后续学习决策分成 `skip`、`observed_only`、`new_skill_candidate` 和 `improve_existing_skill_candidate`。下一阶段应实现 `review_evolution_candidate`：把候选转成可审查 diff、拒绝原因或需要更多证据，而不是直接自动写全局技能。

### 2026-05-03 - review_evolution_candidate 只生成审核结果，不应用修改

**Decision**

`review_evolution_candidate` 第一版只做审核分流和提案产物：目标全局技能不存在则拒绝，候选缺少证据或建议修改则要求补充证据，候选完整时生成 `.review.json` 和 `.diff`。它不会自动写入全局 `SKILL.md`。

**Reason**

技能进化需要让系统少犯旧错误，但全局技能是跨项目权威来源，不能被一次任务或一次候选无确认改写。先生成可审查 diff 能让用户或后续安全流程判断是否真的要吸收，避免把噪音沉淀成全局规则。

**Impact**

后续如果要进入应用阶段，需要单独实现带确认的 apply 流程：再次读取目标文件、校验 diff 或候选仍适用、写入备份/回滚信息，并把候选状态更新为 `applied` 或 `rejected`。在该流程完成前，所有进化候选都停留在审核提案层。

### 2026-05-03 - apply_evolution_candidate 必须显式确认并可回滚

**Decision**

确认应用阶段新增 `apply_evolution_candidate`，但默认拒绝执行；只有调用方显式传 `confirm_apply=true` 或 CLI `--confirm-apply` 时才允许修改目标全局技能。应用前必须校验 review 时记录的目标文件 hash，应用时必须写备份、应用记录和 rollback hint。

**Reason**

全局技能是跨项目权威来源，不能因为候选存在就自动写入。显式确认、hash 校验和备份让“技能进化”从记录走到真实生效，同时保留撤销路径，降低把噪音或过期 diff 写入全局规则的风险。

**Impact**

候选状态现在可以推进到 `applied`。下一阶段如果继续，应实现 rollback/undo 路径：根据 `.skill_runtime/evolution_applications/*.apply.json` 里的备份记录恢复目标文件，并把候选状态更新为 `rolled_back`，而不是继续扩大自动应用范围。

### 2026-05-05 - Rollback records must link directly to review and apply

**Decision**

将 `candidate -> review -> apply -> rollback` 视为一条完整可审计生命周期。回滚记录除了指向 application 和 backup 之外，还必须直接保留 `review_path`。

**Reason**

仅靠 `application_path` 间接回跳到 review 虽然 technically 可行，但不够干净。回滚记录本身应该能直接回答“这次撤回的是哪一份已审核提案”，这样审计和人工复核时不需要再做二次推断。

**Impact**

- `rollback_evolution_candidate` 现在会把 `review_path` 写进 `.skill_runtime/evolution_rollbacks/*.rollback.json`
- 新 acceptance-style 测试会直接校验 review linkage、application linkage、backup linkage 和 restored hash
- 下一步如果继续 skill evolution 主线，应优先补 operator-facing acceptance doc / runbook 或更明确的人工审核路径，而不是再回头补 rollback 基础能力

### 2026-05-05 - Evolution lifecycle tools must return explicit host follow-up actions

**Decision**

`review_evolution_candidate`、`apply_evolution_candidate`、`rollback_evolution_candidate` 不再只返回原始 lifecycle 结果；它们还必须返回统一的 host-facing recommendation。

**Reason**

仅有 candidate/review/application/rollback 数据并不等于人工审核路径清楚。Host 还需要直接知道下一步是什么：review 后该显式 apply，apply 后该保留显式 rollback，rollback 后该刷新治理视图确认状态。如果没有这些 recommendation，流程虽然存在，但对 host 来说仍然是隐式的。

**Impact**

- review 完成后主推荐动作是 `apply_evolution_candidate`
- apply 完成后主推荐动作是 `rollback_evolution_candidate`，并附带 `governance_report`
- rollback 完成后主推荐动作是 `governance_report`
- 回归测试现在会校验 `recommended_next_action`、`recommended_host_operation` 和 `available_host_operations`

### 2026-05-05 - Evolution lifecycle is now a documented operator-facing mainline

**Decision**

将 skill evolution lifecycle 从“若干 service/CLI/MCP 能力”提升为明确的 operator-facing mainline，并补独立 acceptance doc 与 runbook。

**Reason**

在 review/apply/rollback 都具备后，缺的已经不是能力，而是主线表达。如果没有一份把 candidate、manual diff、confirmed apply、confirmed rollback、host next actions 串起来的文档，后续很容易又回到“底层存在，但人不知道该怎么用”的状态。

**Impact**

- 新增 `docs/evolution-lifecycle-acceptance.md`
- 新增 `docs/evolution-lifecycle-runbook.md`
- 这条主线现在与 handoff mainline 一样，具备 acceptance path、runbook、host follow-up 和 rollback audit chain
- 后续如果继续，应优先 dogfood 这条 operator-facing 主线，而不是继续新增 lifecycle 机制
