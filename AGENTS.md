# AGENTS.md - Workspace Guide

This workspace is `vibe`.

## Workspace Purpose

- This project is for discussing workflows, development methods, and reusable process documents.
- Do not treat this workspace as the default place to implement real product code.
- Unless the user explicitly says otherwise, keep work here at the discussion, documentation, and process-definition level.

## Standing Rules

- New development directions must pass the development direction value gate before implementation; only a `build_now` verdict permits same-flow implementation.
- Do not treat Skill Runtime, local skills, `entered / used` samples, dashboard events, or trigger validation as the product goal. If work starts drifting into "prove the runtime works" loops, stop and return to the development-direction value gate.
- Do not continue adding or validating skills just because auto mode can keep going. Runtime work is only justified when it directly supports valuable development decisions, especially preventing low-value implementation.
- Concrete project development tasks must call the Codex-facing Skill Runtime gate before substantive reads or edits.
- Resume commands such as `继续`, `继续完成任务`, `继续 HANDOFF`, or `continue` must start from `HANDOFF.md`.
- Prefer the fast runtime suite for routine validation: `python -m unittest tests.test_runtime_fast -v`.
- Deployment decisions must be based on inspected project files, not labels alone.
- Do not change business code unless the current task requires it.

## Workflow Skill Routing

- Use `pre-implementation-workflow-review` as the main process for new development directions, product ideas, route changes, and value checks before coding.
- Use `runtime-gate-workflow` for Skill Runtime gate/finalizer setup, fallback, and event visibility.
- Use `auto-mode-stage-runner` for `自动模式开始`, autonomous stage execution, stage reports, and auto-mode stopping rules.
- Use `nontechnical-stage-report` when a stage report must be understandable to a non-technical user.
- Use `session-handoff-maintenance` for resume flow and updates to `HANDOFF.md`, `TASKS.md`, and `DECISIONS.md`.
- Use `deployment-strategy-review` for deployment planning, Docker selection, and static/Next.js/Node service decisions.
- Use `runtime-verification-selector` for choosing fast, full, profiling, syntax, or static validation commands.
- Use `repo-impact-analysis` for repository structure lookup, symbol search, call-chain tracing, and GitNexus fallback decisions.
- When calling Skill Runtime active skills directly, use the underscore runtime skill names from `skill_store/active`.
- New reusable workflow skills belong in the global Codex skills directory, not in this project as a second full copy. See `docs/global-skill-source-of-truth-policy.md`.

## Minimal Handoff Rule

- Keep long-term context in repository state files, not chat.
- After important stage completions, design decisions, blockers, or long context growth, update `HANDOFF.md`, `TASKS.md`, and `DECISIONS.md` as needed.
- While the Codex default-lane observation period is active, append lightweight real-task entries to `docs/codex-default-lane-observation-log.md`.
