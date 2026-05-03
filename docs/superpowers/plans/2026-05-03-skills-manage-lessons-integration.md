# Skills-Manage Lessons Integration Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Absorb useful control-plane ideas from `iamzhihuix/skills-manage` while keeping Skill Runtime focused on creation, distillation, evolution, audit, and governed reuse.

**Architecture:** Keep Skill Runtime as the runtime lane and learning engine. Add optional control-plane surfaces around it: platform/project inventory, export planning, import-to-staging, capability collections, and provenance-rich dashboard views. No external skill should bypass staging, audit, or promotion.

**Tech Stack:** Existing Python runtime, existing JSON/metadata skill store, existing static dashboard renderer, existing CLI/MCP entry points, no new desktop shell in this plan.

---

## Product Boundary

`skills-manage` is best understood as a cross-platform skill asset manager. Its center of gravity is: collect, browse, organize, install, uninstall, and import skills across many agent platforms.

Skill Runtime is different. Its center of gravity is: task happens, runtime gate decides, skill may be reused, task result is captured, new skill can be distilled, audited, promoted, reused, archived, and governed.

The plan is therefore:

- absorb `skills-manage` as control-plane inspiration
- do not turn Skill Runtime into a passive desktop skill manager
- keep the runtime lifecycle as the source of product differentiation

## What To Borrow

- Central skill library as a single source of truth.
- Platform directory awareness for Codex, Claude Code, Cursor, Gemini CLI, and custom tools.
- Symlink-first export planning with copy fallback for Windows or unsafe symlink cases.
- Project-level discovery, with clear separation between shared global skill folders and project-local skill folders.
- Marketplace/GitHub import ergonomics, but routed into staging.
- Collections for organizing capability areas.
- Local-first privacy and provenance wording.
- Search and navigation patterns for larger skill libraries.

## What Not To Borrow

- Full Tauri desktop app as the next default step.
- Direct marketplace install into active skills.
- Cross-platform write operations before a plan-only phase.
- Editable skill management UI before lifecycle governance is proven.
- Any path that makes asset management more important than distillation and evolution.

## Target Shape

```text
Real task
-> Codex / host adapter
-> runtime gate
-> reuse or normal execution
-> capture
-> distill
-> audit
-> staging / active / archive
-> optional control-plane surfaces:
   - dashboard
   - platform/project inventory
   - export planning
   - import-to-staging
   - capability collections
```

## Phase 1: Read-Only Platform And Project Inventory

**Goal:** Show where runtime skills and platform skills live without writing to platform directories.

**Files:**

- Create: `docs/platform-skill-inventory-design.md`
- Later create: `skill_runtime/platforms/registry.py`
- Later create: `skill_runtime/platforms/discovery.py`
- Later modify: `skill_runtime/dashboard/collector.py`
- Later modify: `skill_runtime/dashboard/templates.py`
- Later test: `tests/test_runtime_platform_inventory.py`

**Rules:**

- Platform directories are observed external surfaces, not the source of truth.
- Runtime lifecycle states remain `active`, `staging`, `archived`, and `rejected`.
- Platform inventory states should be `managed_by_runtime`, `external`, `copied_export`, `symlink_export`, or `read_only`.
- Do not scan the whole disk. Scan only configured platform roots and selected sibling project roots.
- Shared `.agents/skills` must not be falsely classified as project-local.

**Tasks:**

- [x] Write the inventory design doc with supported platform directory mappings.
- [x] Define a normalized inventory item model: `platform_id`, `display_name`, `skills_dir`, `skill_name`, `skill_path`, `ownership`, `link_type`, `source_root`, `is_read_only`.
- [x] Add tests for Windows paths, missing directories, duplicate skill names, and shared `.agents/skills`.
- [x] Add dashboard collection for inventory data.
- [x] Add a dashboard page named `平台与项目`.
- [x] Verify with `python -m unittest tests.test_runtime_fast -v`.

**Acceptance criteria:**

- Dashboard can answer: "Which projects and platforms currently expose skills?"
- Runtime-owned skills and external skills are visually separate.
- No platform directory is modified.

## Phase 2: Export Plan Before Export Write

**Goal:** Let users preview what would happen if an active runtime skill were exposed to a platform.

**Files:**

- Create: `docs/platform-export-policy.md`
- Later create: `skill_runtime/platforms/export_plan.py`
- Later modify: `skill_runtime/cli.py`
- Later test: `tests/test_runtime_platform_export.py`

**First command:**

```powershell
python -m skill_runtime.cli platform-export-plan --skill merge_text_files --platform codex
```

**Rules:**

- Only `active` skills are export-eligible.
- The command returns source path, target platform, target directory, proposed target path, link type, conflict state, and warnings.
- It refuses to overwrite real directories.
- It prefers symlink when safe.
- It recommends copy fallback on Windows or cross-volume cases.
- This phase does not write to platform directories.

**Tasks:**

- [x] Write `docs/platform-export-policy.md`.
- [x] Add export planning model with fields: `skill_name`, `platform_id`, `source_path`, `target_path`, `link_type`, `conflict`, `requires_confirmation`, `warnings`.
- [x] Add tests for no conflict, existing real directory, missing/non-active skill, and Windows copy fallback eligibility.
- [x] Add CLI command `platform-export-plan`.
- [x] Verify with focused export-plan tests.

**Acceptance criteria:**

- User can see platform exposure consequences before any write.
- Conflicts are explicit.
- Export planning remains lifecycle-aware.

## Phase 3: Import External Skills Into Staging

**Goal:** Borrow import ergonomics without letting external skills bypass runtime governance.

**Files:**

- Create: `docs/import-to-staging-policy.md`
- Later create: `skill_runtime/importers/local_skill_importer.py`
- Later create: `skill_runtime/importers/github_skill_importer.py`
- Later modify: `skill_runtime/cli.py`
- Later test: `tests/test_runtime_skill_import.py`

**First command:**

```powershell
python -m skill_runtime.cli import-skill-to-staging --source <path-or-url>
```

**Rules:**

- External skills always enter `skill_store/staging/`.
- Imported metadata must include source path or URL, import time, content hash, and audit state.
- Imported skills are visible as candidates but cannot be silently reused before promotion.
- Missing or invalid `SKILL.md` fails with a concrete reason.
- GitHub import should come after local path import is tested.

**Tasks:**

- [x] Write `docs/import-to-staging-policy.md`.
- [x] Add local directory importer for one `SKILL.md` directory.
- [ ] Add GitHub raw/repository importer only after local importer tests pass.
- [x] Add provenance fields to staging metadata without changing active metadata contract.
- [x] Add audit gate marker that marks imported skills as `requires_review`.
- [x] Add CLI command `import-skill-to-staging --source <path>`.
- [x] Add dashboard section for imported candidates and their audit state.
- [x] Verify with tests that imported skills do not enter active.

**Acceptance criteria:**

- External ecosystem skills can be studied.
- Active runtime reuse is not polluted.
- Every imported candidate has provenance and audit state.

## Phase 4: Capability Collections

**Goal:** Turn dashboard ability groups into durable collections without changing execution semantics.

**Files:**

- Create: `docs/capability-collections-design.md`
- Later create: `skill_runtime/collections/model.py`
- Later create: `skill_runtime/collections/store.py`
- Later modify: `skill_runtime/dashboard/collector.py`
- Later test: `tests/test_runtime_collections.py`

**Rules:**

- Collections are organizational overlays, not lifecycle states.
- One skill can belong to multiple collections.
- Collections can include active, staging, and archived skills, but lifecycle state must remain visible.
- Suggested initial collections: 文本处理, 格式转换, 文件整理, 项目维护, 运行时治理.

**Tasks:**

- [x] Write `docs/capability-collections-design.md`.
- [x] Add a durable `skill_store/collections.json` schema.
- [x] Add collection model and store modules.
- [x] Add dashboard collection data without changing skill lifecycle metadata.
- [x] Add a read-only dashboard page named `能力集合`.
- [x] Add tests for explicit collection membership, stale skill references, and dashboard rendering.

**Acceptance criteria:**

- Users can understand capability areas instead of reading raw skill lists.
- Collections do not alter classification, audit, promotion, or execution.

## Phase 5: Privacy And Provenance

**Goal:** Make data flow and source history explicit before import/export grows.

**Files:**

- Create: `docs/privacy-and-provenance.md`
- Modify: `README.md`
- Modify: `README.en.md`
- Later modify: dashboard provenance rendering

**Rules:**

- Clearly state what stays local: skill store, trajectories, audits, runtime lane events, usage overlays, dashboard HTML.
- Clearly state what can leave the machine: provider prompts, semantic audit requests, future GitHub/marketplace import requests.
- Provider credentials must not be stored in tracked files.
- Dashboard should distinguish distilled, imported, manually authored, and exported skills.

**Tasks:**

- [x] Create `docs/privacy-and-provenance.md`.
- [x] Document local files and directories that stay on the machine.
- [x] Document external provider and future network import data flow.
- [x] Document credential storage boundaries.
- [x] Document provenance categories and local import metadata.
- [x] Link the privacy/provenance doc from `README.md`.
- [x] Link the privacy/provenance doc from `README.en.md`.

**Acceptance criteria:**

- A non-technical user can understand local vs external data flow.
- Imported and distilled skills are visibly different.

## Phase 6: Rich UI Decision Gate

**Goal:** Avoid prematurely building a desktop app.

Only consider a richer UI if at least two become true:

- static dashboard becomes too limited for real daily work
- users need repeated filtering, comparison, or batch selection
- import/export review becomes a multi-step workflow
- cross-project inventory becomes too dense for static HTML
- non-technical users need a visual management surface

If this gate opens, prefer a local web UI first. Keep runtime logic in Python and treat UI as a client, not as owner of lifecycle rules.

## Recommended Next Step

Phase 1 through Phase 5 are now complete. The next recommended step is to pause before Phase 6:

```text
Use the current static dashboard for real work before deciding whether a richer local web UI is justified.
```

GitHub import and richer UI are now both design-gated rather than automatic next steps. Continue only if real usage shows a repeated need.

## References

- `skills-manage` repository: https://github.com/iamzhihuix/skills-manage
- v0.10.0 release notes: https://github.com/iamzhihuix/skills-manage/releases/tag/v0.10.0
- Link/export behavior: https://raw.githubusercontent.com/iamzhihuix/skills-manage/main/src-tauri/src/commands/linker.rs
- Marketplace behavior: https://raw.githubusercontent.com/iamzhihuix/skills-manage/main/src-tauri/src/commands/marketplace.rs
- Security notes: https://raw.githubusercontent.com/iamzhihuix/skills-manage/main/SECURITY.md

## Self-Review

Spec coverage:

- Similarity to `skills-manage` is covered in Product Boundary and What To Borrow.
- Skill Runtime's creation, distillation, evolution, and governance focus is preserved in every phase.
- Concrete absorbable ideas are split into inventory, export planning, import-to-staging, collections, provenance, and UI decision gate.

Placeholder scan:

- No phase depends on a broad future rewrite.
- Each phase has files, rules, and acceptance criteria.

Type consistency:

- Lifecycle states stay `active`, `staging`, `archived`, and `rejected`.
- Runtime lane states stay `entered`, `used`, and `skipped`.
- External imports consistently enter staging before audit and promotion.
