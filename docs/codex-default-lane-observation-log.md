# Codex Default Lane Observation Log

Date opened: 2026-04-30

## Purpose

Keep a lightweight record of real Codex tasks that touch the current default lane.

This is not meant to become a heavy reporting artifact.

It only exists so the widening decision can be based on real use instead of memory.

## Entry Template

### YYYY-MM-DD - Short task label

- Task type:
- Classified as:
- What happened:
- Did the behavior feel correct:
- Did the lane help:
- Follow-up:

## Current Entries

### 2026-05-05 - Search alias recall support

- Task type: local search-quality recall improvement
- Classified as: default-out / skipped
- What happened: added optional `search_aliases` to skill metadata, wired aliases into local `SkillIndex` scoring, and turned the known Chinese merge query into an explicit alias-driven expected pass while keeping a Chinese negative query unrecommended
- Did the behavior feel correct: yes; this improved local recall for a known intent without rewriting retrieval, introducing semantic search, or changing runtime entry policy
- Did the lane help: yes, because the skipped result reinforced that this is retrieval-quality hardening inside the local search path, not evidence for broader automatic entry
- Follow-up: keep future search work focused on measured local retrieval boundaries; do not treat alias recall as a reason to widen `default-in`

### 2026-05-05 - Search quality baseline

- Task type: search and reuse baseline measurement
- Classified as: default-out / skipped
- What happened: added a local search-quality plan and rewrote the search evaluation script to use a temporary runtime root, a small imported active-skill fixture set, and a fixed query set with per-query diagnostics
- Did the behavior feel correct: yes; the work stayed on measurement and exposed a real limitation instead of silently reworking retrieval or hiding failures behind a green-only result
- Did the lane help: yes, because the skipped result reinforced that this is baseline instrumentation for search quality rather than a runtime-entry expansion event
- Follow-up: keep the next slice on retrieval quality inside the current local search path; do not use search baseline work as evidence for wider automatic entry

### 2026-05-05 - Fallback provider contract documentation

- Task type: provider-contract closure
- Classified as: default-out / skipped
- What happened: documented `provider_guidance` as part of the formal fallback provider request contract in `docs/provider-integration.md`, clarified that the same guidance is embedded into `prompt`, and confirmed bundled example providers remain compatible without changing their authority
- Did the behavior feel correct: yes; this tightened contract clarity without changing audit, fixture roles, or runtime entry policy
- Did the lane help: yes, because the skipped result reinforced that this is documentation and contract hardening, not evidence for broader automatic runtime entry
- Follow-up: keep provider-loop improvements inside the existing fixture family and baseline gate rather than using contract clarity as a reason to widen `default-in`

### 2026-05-05 - Review cleanup provider guidance wiring

- Task type: provider-fidelity request hardening
- Classified as: default-out / skipped
- What happened: wired the minimal review-cleanup provider guidance into the fallback provider request and prompt so fallback providers receive explicit constraints about executable workflow code, matching runtime tools, kwargs-parameterized paths, and review-cleanup-specific non-automation boundaries
- Did the behavior feel correct: yes; this improved provider-side context without changing audit thresholds, changing fixture roles, or widening runtime entry
- Did the lane help: yes, because the skipped result reinforced that this remains a governed-learning quality change rather than default-lane evidence
- Follow-up: keep using the existing fixture set and baseline gate; only revisit broader entry policy if real maintainer evidence appears, not because guidance text improved

### 2026-05-05 - Review cleanup provider gap analysis

- Task type: provider-fidelity gap analysis
- Classified as: default-out / skipped
- What happened: compared the existing review-cleanup expected-failure fixture with the controlled positive-control fixture and documented the gap in `docs/review-cleanup-provider-gap-analysis.md`
- Did the behavior feel correct: yes; the work stayed on provider-quality analysis and did not drift into dashboard work or runtime entry expansion
- Did the lane help: yes, because the skipped result reinforced that this is still governed-learning fidelity analysis rather than evidence for wider automatic entry
- Follow-up: improve provider guidance inside the current fixture family without turning the positive control into default-in evidence

### 2026-05-05 - Provider quality baseline comparison

- Task type: provider-quality measurement hardening
- Classified as: default-out / skipped by Codex runtime gate
- What happened: turned the readable provider-quality fixture baseline into `docs/provider-quality-baseline.json` and added `--baseline` / `--fail-on-regression` to the local evaluation script
- Did the behavior feel correct: yes; the work stayed on the normal implementation path and produced a comparison gate without adding dashboard surface or changing runtime entry policy
- Did the lane help: yes, because the skipped result reinforced that this is a local quality check, not a default-lane expansion event
- Follow-up: use the baseline comparison as a provider-quality regression check before treating provider-loop changes as stable

### 2026-05-05 - Recommendation contract dogfood

- Task type: host integration contract verification
- Classified as: normal implementation path plus local runtime verification
- What happened: verified the top-level recommendation contract across three real paths: `background_hint -> execute_skill`, captured workflow -> `distill_trajectory`, and explicit existing-skill gap -> `review_evolution_candidate`
- Did the behavior feel correct: yes; the runtime stayed conservative, but the host still got one concrete next step in each case
- Did the lane help: yes; it turned reuse and learning boundary results into a stable operator-facing interface instead of payload-specific internals
- Follow-up: sample these three recommendations in a more realistic maintainer sequence rather than expanding dashboard UI

### 2026-05-05 - Recommendation sequence acceptance

- Task type: operator-facing sequence hardening
- Classified as: normal implementation path plus local runtime verification
- What happened: added a runbook and acceptance-style test that chains `background_hint`, `distill_trajectory`, and `review_evolution_candidate` into one explicit operator sequence
- Did the behavior feel correct: yes; each step stays non-automatic, but the host always has one concrete next move
- Did the lane help: yes; it reframed follow-up recommendations as a real sequence family rather than three separate payload features
- Follow-up: decide whether this sequence deserves a narrow host presentation surface beyond raw JSON and current dashboard observation

### 2026-05-05 - Top-level recommendation contract for reuse and learning

- Task type: runtime orchestration contract hardening
- Classified as: default-in observation plus normal implementation path
- What happened: top-level follow-up recommendation fields were added to orchestration results so hosts can render `background_hint`, `distill_trajectory`, and `review_evolution_candidate` without reading nested payload-specific shapes
- Did the behavior feel correct: yes; this does not widen automation, it only makes the next-action contract consistent across reuse and learning paths
- Did the lane help: yes; the captured development workflow and evolution paths already emitted recommendations, and this stage turned them into a stable host-facing interface
- Follow-up: keep dashboard changes minimal; the next worthwhile work is targeted dogfood of these recommendation boundaries rather than more UI

### 2026-05-05 - Trigger log status balance fix

- Task type: dashboard observability bug fix
- Classified as: default-out / skipped by CLI `codex-run`
- What happened: the trigger log appeared to lose `used` and `entered` records because the dashboard truncated recent events before grouping by status; it now counts the full log and keeps recent samples per status
- Did the behavior feel correct: yes; used and entered records were still present in the raw event log, so the fix belongs in dashboard data selection rather than event generation
- Did the lane help: yes; it made the skipped-heavy recent activity visible as a UI/data balancing issue instead of a runtime data-loss issue
- Follow-up: when adding trigger-log event details, keep the same status-balanced selection so detail views do not regress to skipped-only lists

### 2026-05-05 - Skill evolution lifecycle detail panel

- Task type: read-only dashboard product improvement
- Classified as: default-out / skipped by CLI `codex-run`
- What happened: after the application was submitted, the mainline returned to product work and added a clickable Skill Evolution lifecycle detail drawer for candidate, review, apply, and rollback context
- Did the behavior feel correct: yes; this is ordinary feature work that should be implemented by Codex with tests, not silently executed by a reusable runtime workflow
- Did the lane help: yes; it kept the feature on the normal development path while still recording that the runtime gate was checked
- Follow-up: use the same read-only drawer pattern for trigger-log event details next

### 2026-05-05 - Post-push mainline resume

- Task type: project-maintenance resume after open-source readiness push
- Classified as: default-out
- What happened: `run_codex_task_experimental` returned `runtime_lane_status: skipped` for the resume/planning task; the repository state was checked from `HANDOFF.md`, `TASKS.md`, git status, recent commits, and application draft files
- Did the behavior feel correct: yes; this was an orientation and planning task, not a reusable local workflow that should be silently executed
- Did the lane help: partly; it confirmed that the runtime gate remains visible even when the normal Codex path should handle the work
- Follow-up: if the application is already submitted, shift the next real development stage toward a focused read-only product improvement such as evolution lifecycle details or trigger-log event details

### 2026-05-05 - Docs-first readiness release

- Task type: open-source readiness documentation release
- Classified as: `default-out` / `skipped` by `run_codex_task_experimental`
- What happened: the maintainer accepted the docs-first route, so the repository added community files, environment ignore rules, an open-source release checklist, and a Codex Open Source application draft.
- Did the behavior feel correct: yes; this is repository documentation and application preparation work, not a reusable local workflow that should be silently executed by runtime.
- Did the lane help: yes, because the visible `skipped` result confirmed that the runtime gate was checked without taking over the documentation task.
- Follow-up: use the application draft to collect maintainer-specific submission fields before any final application.

### 2026-05-05 - Packaging route decision point

- Task type: open-source readiness route decision
- Classified as: normal Codex documentation path after Stage 3 completion
- What happened: added `docs/codex-open-source-packaging-decision.md` comparing docs-first release, CLI package hardening, and Codex plugin path, with a recommendation to choose docs-first first.
- Did the behavior feel correct: yes; this is a real route decision and should stop for the maintainer.
- Did the lane help: yes, because earlier gate results kept implementation from jumping directly to plugin work.
- Follow-up: wait for the maintainer to choose the Stage 4 route.

### 2026-05-05 - Maintainer demo set completed

- Task type: open-source maintainer workflow demos
- Classified as: `default-out` / `skipped` by the runtime gate
- What happened: added release readiness and handoff continuation demos, linked the maintainer demo set from README and DEMO, and verified both new demos with JSON validation plus `capture-trajectory` in temporary runtime roots.
- Did the behavior feel correct: yes; these are local documentation demos and should not auto-promote skills.
- Did the lane help: yes, because it kept the workflow-capture evidence separate from promotion or plugin implementation.
- Follow-up: move to Stage 4 packaging decision and stop for user choice if the route is ambiguous.

### 2026-05-05 - Maintainer review cleanup demo

- Task type: open-source maintainer workflow demo
- Classified as: `default-out` / `skipped` by the runtime gate
- What happened: added the first Stage 3 demo for review cleanup, including local review comment input, expected cleanup plan output, an observed task record, documentation, and a verified `capture-trajectory` path using a temporary runtime root.
- Did the behavior feel correct: yes; this is a documentation/demo task and should not auto-promote skills.
- Did the lane help: yes, because it reinforced the boundary between capturing a workflow and promoting it.
- Follow-up: continue Stage 3 with the release readiness demo.

### 2026-05-05 - Public positioning and README narrative

- Task type: open-source readiness documentation update
- Classified as: `default-out` / `skipped` by the runtime gate
- What happened: rewrote README top sections around open-source maintainer value and added `docs/codex-open-source-positioning.md` with positioning, differentiation, community file checklist, demo candidates, and application copy drafts.
- Did the behavior feel correct: yes; this is project narrative work and should stay on the normal Codex path.
- Did the lane help: yes, because it preserved the route boundary: improve public readiness first, do not jump into plugin implementation.
- Follow-up: build the maintainer workflow demos and verification path next.

### 2026-05-05 - Open-source readiness audit

- Task type: documentation audit and application-readiness planning
- Classified as: `default-out` / `skipped` by the runtime gate
- What happened: created `docs/codex-open-source-readiness-audit.md`, recording current strengths, application blockers, sensitive-information scan result, positioning draft, and the recommended Stage 2 narrative work.
- Did the behavior feel correct: yes; the task required repository judgment and documentation, not runtime skill execution.
- Did the lane help: yes, because it kept the task on the normal Codex path while preserving a visible runtime decision.
- Follow-up: proceed to Stage 2 project positioning and README/application narrative before building new plugin features.

### 2026-05-05 - Codex for Open Source readiness goal

- Task type: strategic project goal and state maintenance
- Classified as: `default-out` / `skipped` by the runtime gate
- What happened: recorded the user's new target of preparing the project for Codex for Open Source or open source fund eligibility, with a `manual_validation_first` route focused on public project value and application evidence.
- Did the behavior feel correct: yes; this is a strategic direction and state update, not a deterministic runtime execution.
- Did the lane help: yes, because it made clear that runtime should not take over this direction-setting task.
- Follow-up: run an open-source readiness audit before building more plugin or dashboard features.

### 2026-05-04 - Parallel subagent orchestration workflow

- Task type: reusable Codex workflow definition
- Classified as: `default-out` / `skipped` by the runtime gate
- What happened: created a global Codex skill that defines Codex as the main agent for authorized complex parallel work, with subagents limited to bounded, reviewable tasks.
- Did the behavior feel correct: yes; this is a global process-definition task, not a deterministic local runtime skill execution.
- Did the lane help: yes, because it made the skip explicit before editing workflow files.
- Follow-up: use the new workflow during a real complex task that explicitly authorizes subagents, then refine only if review or integration gaps appear.

### 2026-05-03 - Rollback evolution candidate

- Task type: Skill Runtime learning-loop safety workflow
- Classified as: `guarded-in` / `skipped` by the runtime gate because this was broader service, CLI, MCP, dashboard, and test work
- What happened: added `rollback_evolution_candidate`, requiring explicit confirmation before restoring the backup recorded by `apply_evolution_candidate`; rollback now writes `.skill_runtime/evolution_rollbacks` records and refuses to overwrite targets changed after apply
- Did the behavior feel correct: yes; the runtime lane should observe this work but not silently execute a global-skill rollback path
- Did the lane help: yes, because it kept the implementation on normal Codex execution while still recording that this was a guarded reusable workflow change
- Follow-up: use this as the safety close for the current skill evolution loop, then prefer version closeout or a read-only lifecycle detail panel

### 2026-05-03 - Skill evolution candidates

- Task type: Skill Runtime learning-loop enhancement
- Classified as: `guarded-in` / `skipped` by the runtime gate because this was broader local feature work
- What happened: added `improve_existing_skill_candidate`, persisted `.skill_runtime/evolution_candidates` records, and exposed a read-only `技能进化` dashboard page
- Did the behavior feel correct: yes; this should not be silently auto-executed or auto-applied to global skills, but it should be visible as a learning-loop event
- Did the lane help: yes, because the skipped gate kept the change on normal Codex execution while preserving the distinction between new-skill distillation and existing-skill improvement
- Follow-up: implement `review_evolution_candidate` so candidates can become reviewed diffs or explicit rejects before any global skill changes

### 2026-05-03 - Review evolution candidate

- Task type: Skill Runtime learning-loop review workflow
- Classified as: `default-out` / `skipped` because implementation touched broader service, CLI and MCP surfaces
- What happened: added `review_evolution_candidate` to turn an evolution candidate into `ready_for_manual_diff`, `needs_more_evidence`, or `rejected`; enough evidence writes `.review.json` and `.diff` without editing global skills
- Did the behavior feel correct: yes; this is the intended next step after candidate capture and keeps global skill edits behind a separate confirmation boundary
- Did the lane help: yes, because the skipped gate preserved the boundary between ordinary Codex implementation and runtime auto-execution
- Follow-up: implement an explicit apply step only after adding confirmation, stale-file checks, backup/rollback information, and applied/rejected status tracking

### 2026-05-03 - Apply evolution candidate

- Task type: Skill Runtime learning-loop confirmed apply workflow
- Classified as: `default-out` / `skipped` because this changes the global-skill mutation boundary and should not be auto-executed
- What happened: added `apply_evolution_candidate` with explicit confirmation, target hash checks, backup creation, application records, rollback hints, CLI/MCP entry points, and dashboard labels for reviewed/applied candidate states
- Did the behavior feel correct: yes; applying global skill changes now requires an intentional flag and refuses stale reviews
- Did the lane help: yes, because the runtime gate kept this as normal Codex implementation while preserving an observable skipped event
- Follow-up: add rollback/undo support that restores from the recorded backup and marks candidates as rolled back

### 2026-05-03 - Trigger log localized for users

- Task type: dashboard trigger-log copy refinement
- Classified as: `guarded-in` / `skipped` because this was local dashboard presentation work
- What happened: changed trigger-log event cards from raw English runtime internals into Chinese records with task, time, handling method, and result
- Did the behavior feel correct: yes; the page now explains whether runtime participated, observed, or Codex handled the task directly
- Did the lane help: only as traceability; the useful result is clearer user-facing observability
- Verification: targeted dashboard tests passed, py_compile passed, dashboard regenerated, and Playwright screenshot `output/playwright/dashboard-trigger-log-localized.png` was inspected
- Follow-up: keep trigger-log explanations user-facing; do not show raw classifier/runtime reason strings unless a dedicated debug view is added

### 2026-05-03 - Dashboard collections hide basic local skills

- Task type: dashboard collection organization
- Classified as: `guarded-in` / `skipped` because this was local dashboard grouping work and not a silent runtime execution task
- What happened: removed basic local helper collections from the default dashboard and regrouped the 8 active workflow skills into four functional groups: `方向与策略`, `自动推进`, `运行时与验证`, and `会话接续`
- Did the behavior feel correct: yes; it matches the user's point that basic file helpers are not useful in the main visual management surface
- Did the lane help: only as traceability; the useful result is keeping the UI centered on workflow value
- Verification: targeted collection/dashboard tests passed, py_compile passed, the global dashboard regenerated with active_count 8, and Playwright screenshot `output/playwright/dashboard-workflow-collections-only.png` was inspected
- Follow-up: do not reintroduce basic local helper groups into default dashboard pages unless the user explicitly asks for a low-level utility view

### 2026-05-03 - Dashboard overview chrome and log navigation cleanup

- Task type: dashboard UI refinement
- Classified as: `guarded-in` / `skipped` because the runtime gate recognized local dashboard work but did not silently execute it
- What happened: removed the overview path subtitle and local view search row, changed the central skill library count to active workflow skills only, and merged cross-workspace event display into the single `触发日志` navigation item
- Did the behavior feel correct: yes; the work directly followed marked visual issues and kept the dashboard focused on workflow skills
- Did the lane help: only as traceability; the useful result is a clearer dashboard surface
- Verification: targeted dashboard tests passed, Python compile checks passed, global dashboard generation reported `active_count: 8`, Playwright screenshots were inspected, and `python -m unittest tests.test_runtime_fast -v` passed with 109 tests
- Follow-up: do not reintroduce duplicate log navigation or count basic local helper skills in the central workflow library badge

### 2026-05-03 - Capability collections reordered workflow-first

- Task type: dashboard collection organization
- Classified as: `guarded-in` / `skipped` because the runtime gate saw a local reusable UI/data organization task but not a phase-one default-in family
- What happened: collection defaults now put workflow collections first, and the dashboard splits the collections page into `工作流技能` and `基础本地技能` sections
- Follow-up adjustment: candidate counts and candidate rows were hidden from the default dashboard display, so the 59 staging candidates no longer dominate the visible product surface
- Layout adjustment: global overview copy and the local view search row now appear only on `总览`; other pages use the original top area for the active page title
- Did the behavior feel correct: yes; this is a product clarity change, not a runtime skill execution
- Did the lane help: only as traceability; the useful outcome is preventing basic helper collections from dominating the first screen
- Verification: targeted runtime fast tests passed; syntax checks passed; Playwright screenshot `output/playwright/dashboard-collections-workflow-first.png` was generated and inspected
- Follow-up: keep basic local helper collections behind workflow collections unless the user explicitly asks to inspect low-level utilities first

### 2026-05-03 - Dashboard rebuilt from skills-manage UI reference

- Task type: dashboard visual redesign
- Classified as: `default-out` / `skipped` by the runtime gate because this was ordinary UI development, not a reusable workflow execution
- What happened: rebuilt the static dashboard around the `skills-manage` app-shell pattern: top title/search bar, left navigation, content header, local search, two-column skill cards, Catppuccin Latte colors, and purple active navigation
- Did the behavior feel correct: yes; the user had a concrete visual complaint and a concrete reference, so implementing the redesign was higher value than continuing to polish the previous radial tree
- Did the lane help: only as traceability; the useful result is a clearer management UI
- Verification: targeted dashboard renderer/CLI tests passed; Playwright desktop and mobile screenshots were generated and inspected against the reference screenshots
- Follow-up: if the UI still feels off, compare against the reference screenshots first instead of inventing a new visual direction

### 2026-05-03 - Workflow skills become the primary visible surface

- Task type: dashboard skill-surface cleanup
- Classified as: `default-in` / `entered` because the task had explicit dashboard, collection, test, and state-file outputs
- What happened: ordinary local file-processing skills were classified as `basic` and moved out of the default skill tree into the built-in `基础本地技能` collection; workflow skills remain the default visible tree
- Did the behavior feel correct: yes; the user wants to judge workflow capability, not keep seeing low-level local helpers as if they were the main project value
- Did the lane help: only as traceability; the product improvement is clearer workflow-first visibility
- Verification: `python -m unittest tests.test_runtime_fast -v` passed with 106 tests; `git diff --check` passed
- Follow-up: keep future basic helper skills out of the primary workflow view unless the user explicitly asks to inspect foundational utilities

### 2026-05-03 - Workflow error correction is a prevention guard

- Task type: workflow correction semantics
- Classified as: `default-in` / `entered` because the task had explicit global skill, state-file, and test outputs
- What happened: refocused `workflow-error-correction` from a recording workflow into a known-error prevention guard that changes the next action before repeating a mistake
- Did the behavior feel correct: yes; the goal is fewer repeated mistakes, not a better error log
- Did the lane help: only as traceability; the real improvement is proactive guard behavior
- Finalizer: returned `runtime_lane_status: entered` with `observed_only`; no trajectory was distilled
- Follow-up: before AGENTS edits, runtime validation, route correction, auto-mode continuation, or new development direction work, apply the matching known mistake guard first

### 2026-05-03 - Recorded workflow mistakes must be reused

- Task type: workflow correction semantics
- Classified as: `default-in` / `entered` because the task had explicit global skill, state-file, and test outputs
- What happened: updated `workflow-error-correction` so recorded mistakes are reused proactively; new records are created only for new or materially different error patterns
- Did the behavior feel correct: yes; the user should not have to repeatedly say the same recorded error
- Did the lane help: only as traceability; the product improvement is the prevention-first correction behavior
- Finalizer: returned `runtime_lane_status: entered` with `observed_only`; no trajectory was distilled
- Follow-up: before recording another workflow error, check whether an existing correction already covers it and apply that rule directly

### 2026-05-03 - Workflow error correction moved out of AGENTS

- Task type: workflow governance correction
- Classified as: `default-in` / `entered` because the task had explicit global skill, AGENTS, state-file, and test outputs
- What happened: created global `workflow-error-correction` skill and removed case-specific runtime validation mistake rules from project and global `AGENTS.md`
- Did the behavior feel correct: yes; AGENTS now keeps only a generic lightweight-boundary rule and a route to the correction workflow
- Did the lane help: only as traceability; the real improvement is that repeated mistakes now have their own recording workflow instead of expanding AGENTS
- Finalizer: returned `runtime_lane_status: entered` with `observed_only`; no trajectory was distilled
- Follow-up: when the user points out a repeated process error, use `workflow-error-correction` and record the mistake in durable state files, not in AGENTS history

### 2026-05-03 - Pre-implementation review main process

- Task type: workflow main-process reinforcement
- Classified as: `default-in` / `entered` because the task had explicit workflow, docs, and test outputs
- What happened: upgraded the global `pre-implementation-workflow-review` skill from a checklist into a blocking main process with four verdicts: `build_now`, `manual_validation_first`, `revise_direction`, and `do_not_build_now`
- Did the behavior feel correct: yes; the runtime gate stayed as bookkeeping, while the actual product value moved to preventing low-value implementation before coding starts
- Did the lane help: only as traceability; the useful outcome is the stronger direction-review workflow and the regression test that protects it
- Finalizer: returned `runtime_lane_status: entered` with `observed_only`; no trajectory was distilled
- Follow-up: use this workflow before the next new product route, and do not resume runtime/sample validation unless it directly supports a build/no-build judgment

### 2026-05-03 - Route correction away from runtime validation loops

- Task type: process correction / value gate reinforcement
- Classified as: `default-in` / `entered` for state-file maintenance; no code change intended
- What happened: user caught that the assistant was drifting back toward the old low-value loop of continuing to validate local skills, runtime triggers, and `entered / used` samples
- Did the behavior feel correct: the correction is correct; runtime validation must not become the project goal
- Did the lane help: only as bookkeeping; the useful lesson is to stop runtime-validation loops and return to the development-direction value gate
- Finalizer: returned `runtime_lane_status: used` and captured `trajectories/record_route_correction_stop_repeating_local_ski_20260503093009.json`
- Follow-up: future automatic development should prioritize `pre_implementation_workflow_review` and reject runtime/sample collection work unless it directly supports preventing low-value development

### 2026-05-03 - GitNexus index refresh

- Task type: repository impact-analysis maintenance
- Classified as: no runtime finalizer; this was a local index refresh with no runtime code or tracked artifact change beyond state files
- What happened: refreshed the GitNexus index from stale commit `992f36e` to current commit `c9f2c2c`
- Did the behavior feel correct: yes; `status`, `cypher`, `query`, and `context RuntimeService` all succeeded after the refresh
- Did the lane help: not directly; this maintains the auxiliary repository lookup layer used by future runtime work
- Verification: `gitnexus analyze` completed in 12.0s with 9,282 nodes, 13,651 edges, 124 clusters, and 300 flows
- Follow-up: keep using `cypher` or `context` for precise lookups because Windows keyword ranking still uses the degraded FTS fallback

### 2026-05-03 - Runtime profiler JSON output

- Task type: verification tooling improvement
- Classified as: `default-in` / `entered` because the task had explicit project development outputs
- What happened: added JSON report output to the runtime test profiler so slow-test trends can be stored and compared
- Did the behavior feel correct: yes; the feature is additive and keeps the existing text output unchanged
- Did the lane help: yes, because profiling showed no single extreme slow test and the next useful step was better trend capture
- Docs: README now includes a `--json-output` example for preserving a comparable timing baseline
- Verification: JSON report unit test failed first, then passed; profiler CLI smoke wrote a JSON file; Python compile checks passed; fast suite passed with 103 tests
- Finalizer: returned `runtime_lane_status: used` and captured `trajectories/add_json_output_support_to_the_runtime_test_prof_20260503091829.json`
- Follow-up: use `--json-output` before and after future test-performance work

### 2026-05-03 - Governance index merge narrowing

- Task type: governance write-path reliability improvement
- Classified as: `default-in` / `entered` because the task touched project state and runtime code paths
- What happened: found and fixed a stale-snapshot overwrite risk in governance archive/backfill paths by merging only changed metadata into the index
- Did the behavior feel correct: yes; the change is narrow and protects unrelated same-name late updates without changing archive outcomes
- Did the lane help: yes, because this came from the remaining task list and produced a concrete regression test before implementation
- Verification: the new same-skill late-update test failed first, then passed; related governance tests passed; Python compile checks passed; fast suite passed with 102 tests
- Finalizer: returned `runtime_lane_status: used` and captured `trajectories/review_and_tighten_index_refresh_behavior_for_go_20260503090649.json`
- Fast coverage: the same-skill late-update regression now runs through `tests.test_runtime_fast`, which passed with 103 tests
- Fast coverage finalizer: returned `runtime_lane_status: used` and captured `trajectories/add_the_governance_same_skill_late_update_regres_20260503091127.json`
- Follow-up: apply the same changed-only merge pattern to any future governance write path

### 2026-05-03 - Codex CLI JSON file arguments

- Task type: runtime lane CLI reliability improvement
- Classified as: `default-in` / `entered` because the task had explicit project development outputs
- What happened: added file-based JSON alternatives for Codex-facing CLI inputs so runtime gate and finalizer commands do not depend on fragile shell escaping
- Did the behavior feel correct: yes; this directly addresses the PowerShell JSON parsing failure encountered during dogfooding
- Did the lane help: yes, because the issue appeared while using the runtime lane itself and became a small, testable improvement
- Verification: new file-argument tests failed first, then passed; targeted Codex CLI tests passed; `python -m py_compile skill_runtime\cli.py` passed; fast suite passed with 102 tests
- Finalizer: file-based `codex-finalize` path returned `runtime_lane_status: used` and captured `trajectories/add_json_file_argument_support_for_codex_task_cl_20260503085918.json`
- Global sync: updated `C:\Users\Administrator\.codex\skills\runtime-gate-workflow\SKILL.md` so future sessions prefer JSON file flags for PowerShell CLI fallback
- Global sync finalizer: returned `runtime_lane_status: used` and captured `trajectories/update_the_global_runtime_gate_workflow_skill_to_20260503090117.json`
- Follow-up: prefer JSON file flags for complex local CLI dogfood commands in PowerShell sessions

### 2026-05-03 - Runtime event payload builders

- Task type: runtime lane observability maintenance
- Classified as: `default-in` / `entered` because the task had explicit project development outputs
- What happened: moved local and global runtime event JSON payload assembly into shared observability builders used by both CLI and MCP
- Did the behavior feel correct: yes; this removes duplicated output-shape code without changing the user-facing command or tool contract
- Did the lane help: yes, because it captured another small development workflow observation sample while the implementation stayed low risk
- Verification: targeted event tests passed, Python compile checks passed, and `python -m unittest tests.test_runtime_fast -v` passed with 100 tests
- Finalizer: returned `runtime_lane_status: used` and captured `trajectories/share_runtime_event_payload_assembly_between_cli_20260503085311.json`
- Follow-up: keep future runtime event fields in the shared builder first so CLI and MCP remain aligned

### 2026-05-03 - Runtime events MCP tool

- Task type: runtime lane observability improvement
- Classified as: `default-in` / `entered` because the task had explicit project development outputs
- What happened: added a read-only `runtime_events` MCP tool for local and global runtime lane event inspection
- Did the behavior feel correct: yes; Codex app sessions can now inspect runtime lane participation without falling back to shell commands
- Did the lane help: yes, because the CLI event view exposed a useful shape and MCP now mirrors it for host integrations
- Finalizer: returned `runtime_lane_status: used` and captured `trajectories/add_a_read_only_mcp_tool_for_inspecting_recent_r_20260503084625.json`
- Follow-up: use the MCP tool in fresh sessions when validating cross-project runtime lane behavior

### 2026-05-03 - Runtime events JSON CLI

- Task type: runtime lane observability improvement
- Classified as: `default-in` / `entered` because the task had explicit project development outputs; finalizer returned `runtime_lane_status: used`
- What happened: added a read-only `runtime-events` CLI for local and global runtime lane event inspection, including learning follow-up fields
- Did the behavior feel correct: yes; this exposes the same information as the dashboard in scriptable JSON without adding any mutation controls
- Did the lane help: yes, because it keeps the observation path usable even when the browser dashboard is not opened
- Docs: README, README.en, and Codex integration docs now include the local and global `runtime-events` commands
- Finalizer: captured `trajectories/add_a_read_only_cli_command_to_inspect_recent_ru_20260503083440.json`
- Follow-up: use this command during cross-project observation to inspect `entered` / `used` samples quickly

### 2026-05-03 - Dashboard shows learning follow-up actions

- Task type: runtime lane observability improvement
- Classified as: `default-in` / `entered` because the task had explicit project development outputs; finalizer returned `runtime_lane_status: used`
- What happened: runtime lane event records now include recommended next action and available follow-up operation labels, and dashboard trigger logs render those fields
- Did the behavior feel correct: yes; this keeps the dashboard read-only while making captured learning outputs actionable
- Did the lane help: yes, because the previous finalizer output proved the follow-up actions existed but the dashboard could not show them
- Finalizer: captured `trajectories/show_finalizer_learning_follow_up_actions_in_the_20260503063848.json`
- Follow-up: keep checking whether these labels are enough in real use before adding any clickable mutation controls

### 2026-05-03 - Development output paths as observation signal

- Task type: Codex default-lane classifier improvement
- Classified as: `default-in` / `entered` after the classifier began using explicit development output paths as a signal; finalizer returned `runtime_lane_status: used`
- What happened: tasks with neutral descriptions can now enter `development-workflow-observation` when expected outputs clearly point to project code, tests, docs, scripts, or CI/config files
- Did the behavior feel correct: yes; the runtime should observe clear development work even when the user or agent does not use exact implementation keywords
- Did the lane help: yes, because the previous skipped/guarded behavior exposed a real classifier blind spot during auto-mode development
- Finalizer: captured `trajectories/teach_the_codex_default_classifier_to_recognize__20260503063126.json` and exposed the new captured workflow promotion follow-up operations
- Follow-up: keep broad tasks without explicit outputs in `guarded-in`, and continue checking real finalizer samples for `used` trajectories

### 2026-05-03 - Captured workflow promotion follow-ups

- Task type: auto-mode core Skill Runtime development
- Classified as: `guarded-in` / `skipped` by the CLI runtime gate for this broad autonomous development round
- What happened: captured trajectory recommendations now keep `distill_trajectory` as the primary conservative next action, while also exposing project active and global Codex `distill_and_promote_candidate` follow-up operations
- Did the behavior feel correct: yes; the runtime now makes the full learning loop discoverable from finalizer output without automatically promoting new skills
- Did the lane help: yes, because the work directly improves the `used` sample follow-up path that default-lane finalizers create
- Follow-up: continue dogfooding real finalizer outputs and check whether hosts can surface the new follow-up operations clearly

### 2026-05-03 - Distill and promote directly to global Codex skills

- Task type: real Codex feature development after direction review
- Classified as: `guarded-in` via the runtime gate because the work changes lifecycle semantics and should not be silently reused
- What happened: extended `distill_and_promote` so service, CLI, and MCP callers can choose `promotion_target: global_codex`; the default target remains project active
- Did the behavior feel correct: yes; this was a valuable small feature because it closes the global workflow skill lifecycle without starting rich UI or GitHub import
- Did the lane help: yes, because the direction review avoided a broad UI detour and kept the work centered on the core closed loop
- Follow-up: dogfood this path with a real broadly reusable workflow candidate before widening any automatic promotion behavior

### 2026-05-03 - Global Codex skill promotion lifecycle

- Task type: real Codex development workflow and lifecycle routing update
- Classified as: `guarded-in` through the CLI fallback gate, with `runtime_lane_status: skipped` because the task was broader than the current phase-one default-in families
- What happened: added a concrete global Codex skill promotion path for reusable workflow skills, including service API, CLI command, MCP host operation, audit follow-up routing, tests, and policy docs
- Did the behavior feel correct: yes; this task should be observed and finalized, but not silently executed by the runtime because it changes lifecycle semantics
- Did the lane help: yes, because it exposed the exact boundary: the runtime should record this governance change, while Codex implements it normally
- Follow-up: use `promote-global-codex-skill` for future broadly reusable workflow candidates instead of project active promotion

### 2026-05-03 - Runtime workflow skills converted to adapters

- Task type: real Codex development workflow and source-of-truth cleanup
- Classified as: `default-in` via structured local workflow conversion, with `runtime_lane_status: entered`
- What happened: converted the 8 project workflow active skills into thin global Codex skill adapters, keeping Runtime search/execution visibility while removing duplicated workflow logic from project active scripts
- Did the behavior feel correct: yes; this matches the new source-of-truth policy and keeps project Runtime entries as adapters rather than second full copies
- Did the lane help: yes, because it made this cleanup observable as a reusable source-of-truth governance pattern
- Finalizer: returned `runtime_lane_status: used` and captured `trajectories/convert_project_workflow_runtime_skills_to_thin__20260503054607.json`
- Follow-up: in a fresh Codex session, confirm the global skills trigger directly and use runtime adapters only when explicit Runtime search/execute is requested

### 2026-05-03 - Global skill source of truth policy

- Task type: real Codex development workflow and governance adjustment
- Classified as: `default-in` via `development-workflow-observation`, with `runtime_lane_status: entered`
- What happened: made global Codex skills the default authoritative home for reusable workflow skills, documented the policy, updated global and project `AGENTS.md`, and extended platform inventory/dashboard to mark global Codex skills as `authoritative_global_skill`
- Did the behavior feel correct: yes; this is broad workflow governance work that should be observed but not silently executed
- Did the lane help: yes, because it kept the distinction visible between global skill source-of-truth, project routing, and runtime adapters
- Finalizer: returned `runtime_lane_status: used` and captured `trajectories/global_skills_as_authoritative_source_for_new_wo_20260503053856.json`
- Follow-up: remove or convert duplicated project runtime workflow skills into thin adapters once the global skill inventory path has been used in a fresh session

### 2026-05-03 - Global workflow skill installation

- Task type: real Codex project/global configuration workflow
- Classified as: `default-in` via `project-state-maintenance`, with `runtime_lane_status: entered`
- What happened: synced the slim workflow routing into global `C:\Users\Administrator\.codex\AGENTS.md`, installed 8 extracted workflows as global Codex skills under `C:\Users\Administrator\.codex\skills`, and aligned project `AGENTS.md` routing names with the global hyphenated skill names
- Did the behavior feel correct: yes; the runtime gate observed the configuration work without silently executing, while the actual global skill installation used the Codex skill-creator structure and validation path
- Did the lane help: yes, because it made the difference clear between project runtime active skills and globally discoverable Codex skills
- Finalizer: returned `runtime_lane_status: used` and captured `trajectories/sync_global_agents_workflow_routing_20260503052119.json`
- Follow-up: confirm in a fresh Codex session that the 8 new global skills appear in the available skills list

### 2026-05-03 - AGENTS workflow skill extraction

- Task type: real Codex development workflow inside the Skill Runtime project
- Classified as: start gate was conservative for the broad workflow refactor; finalizer returned `default-in` via `development-workflow-observation` with `runtime_lane_status: used`
- What happened: slimmed `AGENTS.md` down to standing rules and workflow-skill routing, then moved auto mode, deployment strategy, session handoff, runtime gate, verification selection, repo impact analysis, and nontechnical stage reporting into active runtime workflow skills
- Did the behavior feel correct: yes; this was a broad process refactor that should not silently auto-execute, but it should still leave a reusable workflow layer behind
- Did the lane help: yes, because it confirmed the gate stays conservative while the resulting workflows become searchable, executable, and test-covered skills
- Follow-up: dogfood the extracted workflow skills on the next auto-mode, deployment, handoff, runtime-gate, verification, repo-impact, or stage-report task; captured trajectory: `trajectories/agents_workflow_skill_extraction_20260503043555.json`

### 2026-05-03 - Development direction value gate skill

- Task type: real Codex development workflow inside the Skill Runtime project
- Classified as: `default-in` via `development-workflow-observation`, with `runtime_lane_status: entered`
- What happened: added and upgraded an active review workflow skill that audits a proposed development direction before coding, flags low-value routes, asks missing questions, suggests research queries, defines a validation plan, and writes a structured JSON value-gate report
- Did the behavior feel correct: yes; this is exactly the kind of project development workflow that should enter observation without silent auto-execution
- Did the lane help: yes, because the task came directly from a route-quality failure that should become reusable process knowledge
- Follow-up: dogfood this skill before the next new feature or route shift, and do not implement until the value hypothesis, alternatives, success metric, and stop condition are clear

### 2026-05-03 - Development workflow observation lane

- Task type: real Codex development workflow inside the Skill Runtime project
- Classified as: before change `guarded-in` and `runtime_lane_status: skipped`; after change `default-in` via `development-workflow-observation` and `runtime_lane_status: entered`
- What happened: added a development-workflow observation family for workspace-scoped code/docs/test work with explicit artifacts, and dashboard overview now separately shows `entered` events as runtime observation rather than hiding them between `used` and `skipped`
- Did the behavior feel correct: yes; broad development work still does not silently auto-execute when `allow_silent_reuse=false`, but runtime now participates in search, observation, and finalization instead of disappearing as a skipped event
- Did the lane help: yes, because it directly addresses the user's dashboard finding that real development tasks were all skipped and the existing low-risk file families were not representative of normal Codex work
- Note: the already-running MCP server returned the previous `guarded-in/skipped` classification until reload; the current CLI/API path returned `entered` and finalizer returned `used`
- MCP retest: stopping the old Skill Runtime MCP Python processes in the same Codex app session caused the current MCP tool transport to close instead of automatically reconnecting; local API still returned `default-in/entered`, so the remaining verification point is a fresh Codex app MCP connection
- Fresh-session MCP retest: a new Codex app MCP connection returned `task_classification.bucket: default-in` and `runtime_lane_status: entered` for a workspace-scoped repository state maintenance workflow with explicit outputs (`docs/codex-default-lane-observation-log.md`, `HANDOFF.md`, `TASKS.md`)
- Follow-up: dogfood this lane on the next project development task and check whether finalization produces useful `used` samples through captured trajectories

### 2026-05-03 - Privacy and provenance documentation

- Task type: Skill Runtime control-plane governance documentation
- Classified as: default-out
- What happened: added privacy and provenance documentation, linked it from README files, and clarified local storage, provider data flow, credential boundaries, and future GitHub/marketplace import constraints
- Did the behavior feel correct: yes; this is documentation governance and should stay on the normal Codex path
- Did the lane help: yes, because it preserved the distinction between runtime workflow reuse and control-plane policy work
- Follow-up: use the static dashboard in real work before deciding whether GitHub import or a richer UI is justified

### 2026-05-03 - Capability collections dashboard overlay

- Task type: Skill Runtime control-plane organization layer
- Classified as: default-out
- What happened: added durable capability collection definitions, a read-only collection store, dashboard collection data, and a `能力集合` dashboard page without changing execution or lifecycle behavior
- Did the behavior feel correct: yes; this is project feature work and should stay outside silent runtime reuse
- Did the lane help: yes, because the runtime gate preserved the boundary between organization surfaces and actual skill execution
- Follow-up: write privacy and provenance docs before adding GitHub or marketplace import

### 2026-05-03 - Imported candidate provenance in dashboard

- Task type: Skill Runtime control-plane dashboard visibility
- Classified as: default-out
- What happened: dashboard collector and renderer now surface imported staging candidate provenance, including source path, content hash, and `requires_review` audit state
- Did the behavior feel correct: yes; this is broader project feature work, so the runtime gate should observe it without silent reuse
- Did the lane help: yes, because it kept import governance visible and preserved the distinction between candidate review and active reuse
- Follow-up: move to capability collections before adding GitHub or marketplace import

### 2026-05-03 - Local import to staging

- Task type: Skill Runtime control-plane import candidate flow
- Classified as: default-out
- What happened: added local `import-skill-to-staging`, which copies an external `SKILL.md` directory into staging with provenance metadata and `audit_status: requires_review`, without writing active skills
- Did the behavior feel correct: yes; this is write-capable project feature work and should stay outside silent runtime reuse, while still producing observable gate/finalizer events
- Did the lane help: yes, because the default lane stayed conservative around external skill ingestion and kept audit/promotion boundaries explicit
- Follow-up: add dashboard provenance display for imported candidates before any GitHub or marketplace import path

### 2026-05-03 - Read-only skill detail panel

- Task type: existing dashboard UI interaction
- Classified as: guarded-in
- What happened: added the first real panel interaction: central skill cards now open a side drawer with skill metadata, source counts, category/source label, complete description, and import provenance when present; visible "read-only" labels were removed from the UI
- Did the behavior feel correct: yes; this is concrete UI feature work and should stay on the normal Codex path, while the runtime gate records that it was observed
- Did the lane help: yes, because the change advances user-facing inspection instead of collecting more internal runtime samples
- Follow-up: use the same read-only drawer pattern for trigger-log event details or collection details before considering any write operation

### 2026-05-03 - Dashboard overview copy/layout polish

- Task type: existing dashboard UI refinement
- Classified as: guarded-in
- What happened: optimized the `总览` page wording and metric card structure so current-project and cross-workspace runtime status read as a concise product summary instead of internal debug labels
- Did the behavior feel correct: yes; this was concrete project UI work, so the runtime gate observed it while implementation stayed on the normal Codex path
- Did the lane help: yes, because the task produced a visible dashboard event without turning UI polish into another runtime validation loop
- Follow-up: continue using the static dashboard for real observation; only add richer UI controls if repeated real usage shows a clear need

### 2026-05-03 - Platform page compact cards

- Task type: dashboard platform inventory usability refinement
- Classified as: guarded-in for broad dashboard UI work
- What happened: changed `平台与项目` from expanded source/debug cards into compact skill-library-style cards with clamped summaries and Chinese source tags
- Did the behavior feel correct: yes; this is UI refinement on the normal Codex path, while the runtime gate remains useful for recording dashboard development work
- Did the lane help: yes, because the dashboard now better separates useful user-facing inventory from internal source fields
- Follow-up: if the platform page needs deeper inspection later, add click-to-detail instead of expanding every card by default

### 2026-05-03 - Trigger log status filtering

- Task type: dashboard trigger-log usability refinement
- Classified as: guarded-in for broad UI/runtime dashboard work
- What happened: added `已使用 / 进入观察 / 已跳过` filters to the trigger log, defaulting to `已使用` so the first view shows runtime participation rather than mixed internal event types
- Did the behavior feel correct: yes; this is still normal Codex implementation work, while the runtime gate records that the task touched a default-lane risk area
- Did the lane help: yes, because the visible dashboard now makes the difference between used, entered, and skipped more useful for real observation instead of mixing them into one feed
- Follow-up: if log entries remain too dense, add read-only event detail inspection next rather than adding write operations

### 2026-05-03 - Plan progress tracker skill

- Task type: global workflow skill creation
- Classified as: guarded-in
- What happened: added a global `plan-progress-tracker` skill so multi-stage plans keep a visible stage coordinate across continue, auto-mode, handoff, and compaction flows
- Did the behavior feel correct: yes; this is reusable workflow setup and should be observable, not silently executed by the current default lane
- Did the lane help: yes, it recorded the workflow addition without turning it into another runtime validation task
- Follow-up: use this skill whenever a staged plan exists, especially before replying to a vague `继续`

### 2026-05-03 - Context compaction audit skill

- Task type: global workflow skill creation
- Classified as: guarded-in
- What happened: added a global `context-compaction-audit` skill for post-compaction analysis and reopen-chat decisions, linked it with `session-handoff-maintenance`, and kept only a short route line in global/project AGENTS
- Did the behavior feel correct: yes; creating a cross-project workflow skill is reusable but should not be silently executed by the current default lane
- Did the lane help: yes, it recorded the work without expanding runtime validation or turning AGENTS into a long manual
- Follow-up: after the next real context compaction, use this skill before continuing substantial work; if it recommends checkpointing or reopening, immediately refresh handoff files through `session-handoff-maintenance`

### 2026-05-03 - Central skill library grouping consolidation

- Task type: dashboard information architecture cleanup
- Classified as: guarded-in
- What happened: moved functional workflow grouping into the `中央技能库` main view, removed the duplicated `技能集合` route, and kept grouped skill rows clickable for detail inspection
- Did the behavior feel correct: yes; this is broader UI/product work, so the runtime gate should observe rather than silently execute it
- Did the lane help: yes, because it left a visible event for a real dashboard task without turning the work back into another local-skill validation loop
- Follow-up: only add richer read-only details when they make the current panel clearer; do not reintroduce duplicate skill surfaces

### 2026-05-03 - Platform export plan preview

- Task type: Skill Runtime control-plane export preview
- Classified as: default-out
- What happened: added `platform-export-plan`, a read-only preview command that reports source path, target platform path, link/copy plan, conflicts, and active-only eligibility without writing platform directories
- Did the behavior feel correct: yes; this is broader project feature work and should remain on the normal Codex path, while the runtime gate/finalizer still provide observable events
- Did the lane help: yes, because it kept the default lane from silently handling platform write-adjacent work and preserved the safety boundary
- Follow-up: if continuing this direction, implement local `import-skill-to-staging` next and keep external skills out of active until audited and promoted

### 2026-05-03 - Read-only platform inventory

- Task type: Skill Runtime control-plane enhancement
- Classified as: default-out
- What happened: added a read-only platform/project skill inventory inspired by `skills-manage`, including a platform registry, `SKILL.md` discovery, dashboard `平台与项目` view, tests, and design documentation
- Did the behavior feel correct: yes; this is project feature work and should remain on the normal Codex path, while still producing visible runtime gate/finalizer events
- Did the lane help: yes, because it kept the runtime lane observable without letting it silently execute broader architecture work
- Follow-up: if continuing this direction, add `platform-export-plan` as a preview-only command before any platform directory write support

### 2026-05-03 - Cross-project invocation confirmed

- Task type: cross-workspace Skill Runtime default capability observation
- Classified as: real-world observation outside the `vibe` workspace
- What happened: user confirmed that other projects can now call Skill Runtime normally
- Did the behavior feel correct: yes; this is the expected result of moving Skill Runtime from a `vibe`-local tool into a Codex-wide background capability
- Did the lane help: yes, because the observation period now has a positive cross-project signal instead of only local `skipped` visibility checks
- Follow-up: keep watching whether those other-project calls produce useful `entered` or `used` samples in the global dashboard, and only consider widening default coverage if the repeated behavior is stable

### 2026-05-02 - MCP runtime gate resume check

- Task type: real project-maintenance resume through Codex runtime gate
- Classified as: default-out
- What happened: `run_codex_task_experimental` returned `runtime_lane_status: skipped` for the resume task and wrote the same event into `.skill_runtime/runtime_lane_events.jsonl`; after the documentation update and dashboard check, `finalize_codex_task_experimental` also returned `runtime_lane_status: skipped` and wrote a finalization event
- Did the behavior feel correct: yes; the task should stay on the normal Codex path, but the dashboard now has visible records for both the start gate and the finalizer
- Did the lane help: yes, because it confirmed the MCP gate and finalizer paths now create the same observable trigger log that the CLI fallback was meant to guarantee
- Follow-up: keep observing later real tasks until the log contains useful `entered` or `used` samples, not only correct `skipped` samples

### 2026-05-01 - Global runtime dashboard

- Task type: cross-workspace runtime lane observability
- Classified as: guarded-in for this feature work
- What happened: `dashboard --global --scan-root <directory>` now renders the normal read-only dashboard plus global project and global log views, aggregating runtime lane events from sibling project roots
- Did the behavior feel correct: yes; this task should not be silently auto-executed by an existing skill, but it should leave clearer runtime visibility afterwards
- Did the lane help: yes, it clarified the current visibility gap across workspaces and produced a concrete way to inspect other projects' trigger records
- Follow-up: use the global dashboard during real work in other project directories to confirm that event logs are being written where expected

### 2026-05-01 - Development task runtime gate rule

- Task type: Codex default-lane workflow enforcement
- Classified as: default-out for this specific rule-update task
- What happened: global and project Agent rules were tightened so concrete project development tasks must call the Codex-facing runtime gate before substantive work, with CLI `codex-run` as a visible-event fallback
- Did the behavior feel correct: partly; the CLI gate wrote a visible `runtime_lane_status: skipped` event, but the earlier MCP call did not create an obvious dashboard event in this session
- Did the lane help: yes, it exposed the real gap between "MCP configured" and "Codex actually calls the runtime during development"
- Follow-up: use the next real code-development task to verify that `run_codex_task_experimental` plus optional `finalize_codex_task_experimental` produces stable dashboard events

### 2026-05-05 - Governance snapshot wording cleanup

- Task type: dashboard explanation refinement
- Classified as: default-out / skipped by the Codex runtime gate
- What happened: the governance snapshot now explains empty duplicate-candidate state and translates `Missing skill directory: skill_store\rejected` into a user-facing note that this is not an error and does not need action yet
- Did the behavior feel correct: yes; this is product-surface clarification work, not a reusable runtime workflow
- Did the lane help: partly; the skip event is useful because it keeps this UI clarification visible in trigger logs without pretending the runtime should take over
- Follow-up: continue the same pattern on trigger-log event detail so product pages explain runtime state without exposing raw internals

### 2026-05-05 - Handoff continuation mainline runbook

- Task type: maintainer mainline acceptance runbook
- Classified as: `guarded-in` / `skipped` by CLI `codex-run`
- What happened: added a runbook for the handoff continuation mainline, validated the demo JSON inputs, confirmed `capture-trajectory` creates a trajectory and recommends `distill_trajectory`, and checked that the current Codex-facing gate still classifies "continue from HANDOFF.md" as local and reusable but outside the phase-one default-in families
- Did the behavior feel correct: yes; this is a real maintainer workflow, but the current conservative boundary should not pretend it is already a silent default-in path
- Did the lane help: yes, because it exposed the exact current boundary instead of leaving handoff continuation in a vague "maybe runtime, maybe not" state
- Follow-up: decide later whether handoff continuation should remain `guarded-in` or earn a stricter default-in family after acceptance-style proof

### 2026-05-05 - Handoff continuation classification boundary

- Task type: runtime classification boundary codification
- Classified as: `default-out` / `skipped` by the Codex runtime gate for this docs-and-tests round
- What happened: added regression coverage and docs to lock the current rule: structured handoff continuation with explicit state-file inputs stays `default-in`, while natural-language continuation such as `continue from HANDOFF.md` stays `guarded-in`
- Did the behavior feel correct: yes; it keeps the automatic lane narrow without erasing the value of explicit state-driven continuation workflows
- Did the lane help: yes, because the mainline now has a concrete, test-backed boundary instead of an informal judgment in chat
- Follow-up: if later evidence justifies widening this family, add an acceptance-style test first, then change the classifier

### 2026-05-05 - Handoff continuation acceptance-style fast test

- Task type: maintainer mainline acceptance guardrail
- Classified as: `guarded-in` / `skipped` by the Codex runtime gate for this tests-and-state-files round
- What happened: added a single fast test that treats the handoff continuation mainline as a product path, not just a document; it verifies the expected continuation brief structure, confirms explicit state-file continuation still classifies as `default-in / project-state-maintenance`, and checks that `capture-trajectory` creates a governed trajectory with `distill_trajectory` as the next explicit step
- Did the behavior feel correct: yes; the runtime should help prove this maintainer workflow without pretending it now auto-promotes or broadly auto-takes over continuation
- Did the lane help: yes, because the mainline now has an executable acceptance baseline for future boundary decisions
- Follow-up: only widen the handoff continuation family if later evidence beats this narrow explicit baseline

### 2026-05-05 - Evolution rollback lifecycle acceptance

- Task type: skill evolution safety mainline tightening
- Classified as: `guarded-in` / `skipped` by the Codex runtime gate for this service-and-tests round
- What happened: added an acceptance-style rollback lifecycle test for `candidate -> review -> apply -> rollback`, and tightened rollback records so they now keep a direct `review_path` alongside `application_path`, backup linkage, and restored hashes
- Did the behavior feel correct: yes; this is core lifecycle hardening for global skill mutation and should remain an explicit Codex implementation task, not a silently executed runtime action
- Did the lane help: yes, because it kept the work on the normal path while clarifying the next evolution mechanism gap as lifecycle auditability rather than more UI or sample collection
- Follow-up: if the evolution lifecycle continues, prefer an operator-facing acceptance doc or stricter manual-review route before adding more mutation surface

### 2026-05-05 - Evolution host follow-up recommendations

- Task type: host-facing lifecycle guidance tightening
- Classified as: `guarded-in` / `skipped` by the Codex runtime gate for this service-and-tests round
- What happened: tightened the evolution lifecycle so review/apply/rollback now return explicit host-facing next actions instead of leaving the host to infer the manual path from raw records; review now recommends explicit apply, apply keeps explicit rollback plus governance refresh available, and rollback recommends governance refresh
- Did the behavior feel correct: yes; this stays on the normal Codex path while making the manual approval flow concrete for hosts
- Did the lane help: yes, because it kept the work focused on workflow clarity rather than expanding automation or UI surface
- Follow-up: if the evolution lifecycle continues, the next serious step should be an operator-facing acceptance doc or runbook, not more hidden lifecycle affordances

### 2026-05-05 - Evolution lifecycle acceptance docs

- Task type: operator-facing lifecycle documentation
- Classified as: `guarded-in` / `skipped` by the Codex runtime gate for this docs round
- What happened: added `docs/evolution-lifecycle-acceptance.md` and `docs/evolution-lifecycle-runbook.md`, turning the evolution lifecycle into a documented operator-facing mainline instead of a set of disconnected lifecycle tools
- Did the behavior feel correct: yes; this is the right follow-up after tightening host recommendations, because the next gap was workflow clarity, not more mutation logic
- Did the lane help: yes, because it kept the work on the normal Codex path and reinforced that the product value now comes from explicit workflow governance, not invisible machinery
- Follow-up: dogfood the documented operator-facing lifecycle before inventing any richer lifecycle surface

### 2026-05-01 - Runtime observability dashboard implementation

- Task type: Codex runtime lane observability
- Classified as: default-lane visibility / local dashboard
- What happened: runtime lane events are now written to a local JSONL log, and `skill-runtime dashboard` can render a read-only HTML dashboard from local runtime data
- Did the behavior feel correct: yes, because the runtime can now show whether it was used, entered, or skipped without requiring manual skill lookup
- Did the lane help: yes, this makes the global runtime lane observable instead of invisible
- Follow-up: use the dashboard during real workspace tasks and decide later whether browser auto-open or richer log filters are worth adding

### 2026-05-01 - Runtime lane trigger visibility

- Task type: Codex default-lane observability improvement
- Classified as: default-lane visibility / operator feedback
- What happened: Codex-facing orchestration results now report whether the runtime lane was used, entered, or skipped, with a short reason
- Did the behavior feel correct: yes, because users can now tell whether Skill Runtime participated without manually searching for skills
- Did the lane help: yes, this task exposed a product gap in the current default lane and turned it into a visible contract
- Follow-up: use these fields in later real cross-workspace tasks to judge whether the global runtime lane is behaving as expected

### 2026-04-30 - Observation period opened

- Task type: phase-level Codex default-lane governance
- Classified as: project status / observation setup
- What happened: the first migrated entry was kept as the current observation point, and the observation rules were written into repository docs
- Did the behavior feel correct: yes
- Did the lane help: yes, because the project now has a clear way to judge whether widening is justified
- Follow-up: append only real later tasks that touch the current default lane

### 2026-05-05 - Evolution lifecycle byte-preserving rollback dogfood

- Task type: operator-facing evolution lifecycle dogfood
- Classified as: guarded-in / skipped
- What happened: ran the documented `candidate -> review -> apply -> rollback` lifecycle against a BOM-backed global skill file in a temporary runtime root; the run exposed that rollback restored normalized text instead of exact original bytes, so `restored_content_hash` drifted from the pre-apply hash even though the visible content matched
- Did the behavior feel correct: partially; the manual path and host recommendations were right, but rollback needed byte-preserving backup/restore to make the audit trail trustworthy
- Did the lane help: yes, because staying on the normal Codex path surfaced a real correctness gap in the governed lifecycle instead of hiding it behind UI work
- Follow-up: keep future evolution-lifecycle dogfood focused on real file-integrity and operator-trust edges, not richer surface area

### 2026-05-05 - Finalizer existing-skill evolution boundary tightening

- Task type: evolution decision boundary hardening
- Classified as: guarded-in / skipped
- What happened: added acceptance-style tests showing that a weak `skill_gap` hint was enough to generate `improve_existing_skill_candidate`; tightened `plan_learning` so existing-skill evolution now requires concrete `evidence` plus `proposed_changes`, while weak hints downgrade to `observed_only`
- Did the behavior feel correct: yes; this matches the intended rule that real task evidence must expose an existing-skill gap before the system proposes modifying that skill
- Did the lane help: yes, because the normal Codex path made it easy to inspect the decision boundary directly instead of smuggling it into dashboard behavior
- Follow-up: future evolution work should keep testing the learning-decision boundary first, before adding richer lifecycle surface

### 2026-05-05 - Finalizer new-skill distillation boundary tightening

- Task type: under-covered workflow learning boundary hardening
- Classified as: guarded-in / skipped
- What happened: added acceptance-style tests showing that a successful workflow with declared `expected_outputs` could become `new_skill_candidate` even when it only read files or wrote different outputs than declared; tightened `plan_learning` so immediate distillation now requires successful write-like operations and expected outputs that match real artifacts or written paths
- Did the behavior feel correct: yes; a new reusable skill should come from a task that actually produced stable outputs, not just from a declared intention
- Did the lane help: yes, because it exposed the product boundary in the learning decision itself instead of letting weak cases drift into later skill governance
- Follow-up: future learning-boundary work should continue proving positive and negative cases at the finalizer layer before widening any automatic distillation path

### 2026-05-05 - Silent reuse expected-output boundary tightening

- Task type: reuse boundary hardening
- Classified as: guarded-in / skipped
- What happened: added acceptance-style tests showing that a strong reusable match could still auto-execute when the request declared expected output A but the known output argument pointed to B; tightened `plan_reuse` so this mismatch now downgrades to `background_hint` instead of silent reuse
- Did the behavior feel correct: yes; silent reuse should only take over when the task intent, required inputs, scope, and declared outputs all line up
- Did the lane help: yes, because it pushed the safety boundary into the reuse decision itself rather than leaving it to later execution or explanation
- Follow-up: future reuse-boundary work should keep proving downgrade cases before widening `auto_execute`

### 2026-05-05 - Finalizer learning decision matrix published

- Task type: operator-facing mainline clarification
- Classified as: guarded-in / skipped
- What happened: added `docs/finalizer-learning-decision-matrix.md`, consolidating the hardened finalizer outcomes `skip / observed_only / new_skill_candidate / improve_existing_skill_candidate` into one explanation layer
- Did the behavior feel correct: yes; the runtime now has a single document that explains why a task became observation, new-skill distillation, or existing-skill evolution instead of leaving that logic scattered across tests
- Did the lane help: yes, because it kept the work on governed runtime behavior instead of drifting back to dashboard-only explanation
- Follow-up: keep this matrix in sync whenever reuse or finalizer boundaries move

### 2026-05-05 - Review cleanup mainline established

- Task type: maintainer mainline expansion
- Classified as: guarded-in / skipped
- What happened: promoted `review cleanup` into the second maintainer mainline with dedicated acceptance and runbook docs; real verification showed that the current Codex-facing gate keeps this family `default-out / skipped`, while the observed-task capture path still produces a governed trajectory and explicit `distill_trajectory` follow-up
- Did the behavior feel correct: yes; this is the right boundary for review-driven work because the maintainer workflow is real, but silent reuse would still be too aggressive
- Did the lane help: yes, because it proved the product can support valuable maintainer workflows even when the runtime lane should stay conservative
- Follow-up: the next mainline step should compare whether `release readiness` adds a meaningfully different governed-learning shape, not just more demo surface
