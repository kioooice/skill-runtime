# AGENTS.md - Workspace Guide

This workspace is `vibe`.

## Workspace Purpose

- This project is for discussing workflows, development methods, and reusable process documents.
- Do not treat this workspace as the default place to implement real product code.
- Unless the user explicitly says otherwise, keep work here at the discussion, documentation, and process-definition level.

## Standing Rules

- New development directions must pass the development direction value gate before implementation; only a `build_now` verdict permits same-flow implementation.
- Do not send clear small execution tasks through direction review; reserve `pre-implementation-workflow-review` for real new directions, route changes, MVP framing, or should-we-build-this decisions.
- Keep `AGENTS.md` lightweight; record recurring workflow mistakes through `workflow-error-correction` instead of adding case-specific history here.
- Concrete project development tasks must call the Codex-facing Skill Runtime gate before substantive reads or edits.
- Resume commands such as `继续`, `继续完成任务`, `继续 HANDOFF`, or `continue` must start from `HANDOFF.md`.
- Do not default to `python -m unittest tests.test_runtime_fast -v` for every small change; use `runtime-verification-selector` and choose the smallest useful verification for the current blast radius.
- Do not update `HANDOFF.md`, `TASKS.md`, and `DECISIONS.md` after every small change; use `session-handoff-maintenance` only when the next-session entry point, durable decision, blocker, plan coordinate, or long-context risk actually changed.
- Do not default to commit and push after every small change; publish at meaningful stage completions, batching points, or when the user explicitly wants the changes published.
- Deployment decisions must be based on inspected project files, not labels alone.
- Do not change business code unless the current task requires it.

## Workflow Skill Routing

- Use `pre-implementation-workflow-review` as the main process for new development directions, product ideas, route changes, and value checks before coding.
- Use `workflow-error-correction` when a repeated process mistake or route drift should be recorded without bloating `AGENTS.md`.
- Use `runtime-gate-workflow` for Skill Runtime gate/finalizer setup, fallback, and event visibility.
- Use `auto-mode-stage-runner` for `自动模式开始`, autonomous stage execution, stage reports, auto-mode stopping rules, and explicit full-auto finite-plan requests such as “列个长计划，然后自动推进，中间不要汇报，不要停下来，直到计划全部完成”.
- Use `plan-progress-tracker` for multi-stage plans so progress always shows the current stage, completed stages, next action, and drift risk.
- Use `nontechnical-stage-report` when a stage report must be understandable to a non-technical user.
- Use `session-handoff-maintenance` for resume flow and updates to `HANDOFF.md`, `TASKS.md`, and `DECISIONS.md`.
- Use `context-compaction-audit` after context compaction or summary-based resume; when it recommends checkpointing or reopening, pair it with `session-handoff-maintenance`.
- Use `deployment-strategy-review` for deployment planning, Docker selection, and static/Next.js/Node service decisions.
- Use `runtime-verification-selector` for choosing fast, full, profiling, syntax, or static validation commands.
- Use `repo-impact-analysis` for repository structure lookup, symbol search, call-chain tracing, and GitNexus fallback decisions.
- Use `parallel-subagent-orchestration` when complex work can be split across authorized subagents while Codex remains the main reviewer and integrator.
- When calling Skill Runtime active skills directly, use the underscore runtime skill names from `skill_store/active`.
- New reusable workflow skills belong in the global Codex skills directory, not in this project as a second full copy. See `docs/global-skill-source-of-truth-policy.md`.

## Minimal Handoff Rule

- Keep long-term context in repository state files, not chat.
- After important stage completions, design decisions, blockers, or long context growth, update `HANDOFF.md`, `TASKS.md`, and `DECISIONS.md` as needed.
- While the Codex default-lane observation period is active, append lightweight real-task entries to `docs/codex-default-lane-observation-log.md`.
