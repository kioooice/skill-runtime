# AGENTS.md - Workspace Guide

This workspace is `vibe`.

## Workspace Purpose

- This project is for discussing workflows, development methods, and reusable process documents.
- Do not treat this workspace as the default place to implement real product code.
- Unless the user explicitly says otherwise, keep work here at the discussion, documentation, and process-definition level.

## Default Workflow

- New projects can start light.
- Do not force Docker at the beginning of a project.
- Confirm the tech stack first, then choose the deployment pattern.
- Add Docker when the project is ready for deployment or long-term maintenance.

## Auto Mode Protocol

- When the user sends `自动模式开始`, treat that message itself as an execution command.
- Do not send any confirmation or transition message before acting.
- After `自动模式开始`, execute the most recent explicit user task already in context. If it contains multiple steps, continue them autonomously.
- If the goal is clear but implementation is not uniquely specified, choose a reasonable, minimal, verifiable path and continue without asking.
- In auto mode, do not interrupt the user for tiny changes, single passing tests, or single-file edits.
- Auto mode is not silent-only. Continue executing across related work, but after each meaningful stage you must publish a stage report.
- Stage reports must be written in non-technical language suitable for a user without programming background.
- Every stage report must include:
  - what was done in this stage
  - what new or improved capability the project gained from a user or product perspective
  - which core files changed, listing only the most important files
  - current risks, explained in plain language
  - 2 to 3 next-step options
  - one explicit recommended option
  - a decision question for the user if needed, otherwise `无`
- Do not trap the user into replying only `继续`.
- If the next step is clear, write exactly in this pattern:
  - `推荐下一步做 X。如果同意，回复：继续 X。`
- If there are multiple reasonable directions, explain the benefit and cost of each direction in plain language.
- After every stage report, update `HANDOFF.md`, `TASKS.md`, and `DECISIONS.md` as needed so the repository stays ahead of chat history.
- Do not make low-value changes just to show visible activity.
- Prioritize work that makes the project more runnable, demoable, or verifiable.
- Do not treat `自动模式开始` as a state-only message that allows waiting for more instructions.
- Only interrupt auto mode when:
  - required information is missing and execution cannot continue
  - there is an irreversible branch that must be decided by the user
  - there is a substantial blocker that cannot be recovered from autonomously
- If auto mode stops for any reason, explicitly state why it stopped. Do not leave a silent gap or an unexplained pause.
- If auto mode stops after a completed execution round, state that the round was completed and why execution is not continuing automatically.
- When auto mode is executing against a previously stated multi-stage plan, stopping messages must also include plan progress:
  - the current stage or milestone
  - what was completed in this round
  - the next likely entry point if execution resumes
- Do not stop with only a generic "this round is done" message when a longer plan is already in flight.
- When a stage is already in progress, do not stop after each small internal subtask, test addition, or narrow contract tweak.
- Prefer stage-level stop points, not micro-round stop points.
- Within an active stage, keep chaining related sub-work until one of these is true:
  - the stage reaches a meaningful closure point
  - a real decision branch appears
  - required information is missing
  - an unrecoverable blocker appears
- Do not present a sequence of tiny within-stage edits as if they were separate completed stages.
- If the active stage is itself an internal restructuring stage such as test maintenance, module splitting, architecture cleanup, or documentation consolidation, do not stop after only the first extracted file, first moved group, or first compatibility shim.
- For restructuring stages, the default stopping bar is a recognizable structural closure, for example:
  - the main source file has been reduced to a compatibility or aggregation layer
  - the targeted group of tests or modules has been fully migrated
  - the old and new structure have both been verified and stabilized
- Do not report an internal restructuring stage as complete when only one sub-group has been moved and the original file still substantially carries the old structure.
- If `自动模式开始` is received and there is no clear executable task in context, reply with exactly:
  `缺少可执行任务，请给出目标。`
- If the user asks whether execution is currently happening, answer with the factual state only.
- If the user explicitly says not to start business development yet, do not start business development before approval.

## Deployment Rule

- For deployment tasks, inspect the project files first and decide the deployment approach from the actual project structure.
- Treat user-provided labels like "static", "Next.js", or "Node" as hints only, not the final source of truth.
- Check `package.json`, `next.config.*`, `Dockerfile`, `docker-compose.yml`, build output directories such as `dist` or `build`, and the start/build scripts before choosing a deployment path.
- If the detected project structure conflicts with the user's verbal classification, follow the project files and explain the mismatch briefly.

## Docker Selection

- Static build output: use the static frontend deployment pattern.
- Projects using `next`: use the Next.js deployment pattern.
- Backend services using long-running server processes: use the Node service deployment pattern.
- If the project already contains its own Docker setup, prefer the existing structure unless there is a clear reason to change it.

## Codex Session Handoff

- Do not rely on old chat history as project memory.
- Do not ask the user to restate prior conversation context when the required state is already available in project files.
- When the user says `继续`, `继续完成任务`, `继续 HANDOFF`, or `continue`:
  1. read `HANDOFF.md` first
  2. then read `TASKS.md` and `DECISIONS.md` only as needed
  3. continue from the `Next Action` in `HANDOFF.md`
  4. do not ask for old chat content
  5. only ask the user if `HANDOFF.md` is missing, clearly stale, contradictory with other project state, or the next step contains a branch that cannot be resolved safely from local context
- After each important stage completion, design or technical decision, blocker discovery, or when context is becoming long, update the project state files:
  - `TASKS.md` records task progress
  - `DECISIONS.md` records design and technical decisions
  - `HANDOFF.md` records the next handoff point
- While the Codex default-lane observation period is active, if a real task touches the current default lane, append a short entry to `docs/codex-default-lane-observation-log.md`.
- Keep observation entries lightweight and outcome-focused. Do not turn normal task execution into heavy manual reporting.
- Do not pack long project summaries into chat context.
- Long-term context must be written into files in the repository.
- Before code changes, read only the smallest file set relevant to the current task. Do not scan the full repository without a clear reason.
- After changes, run relevant tests, type checks, or static checks when possible. If they cannot be run, state why.
- For routine local validation, prefer the fast runtime suite first: `python -m unittest tests.test_runtime_fast -v`.
- Treat `python -m unittest tests.test_runtime -v` as the full slow suite; it currently takes about 10 minutes locally, so run it only for release-level validation or when broad runtime behavior may be affected, and use a timeout of at least 900 seconds.
- To diagnose slow tests, run `python scripts/profile_runtime_tests.py --suite tests.test_runtime --top 20`.
- Do not change business code unless the current task requires it.

## GitNexus Preference

- If GitNexus MCP is available in the current environment, prefer it first for module lookup, symbol search, call-chain tracing, and impact analysis before falling back to plain file search.
- If GitNexus MCP is not available, do not block the task; use normal file inspection and repository search.
- If this repository does not yet have GitNexus configured, do not auto-install dependencies, do not auto-install from the network, and do not modify global Codex configuration during normal task execution.
- Optional future setup commands for the user:
  - `npx gitnexus analyze`
  - `codex mcp add gitnexus -- npx -y gitnexus@latest mcp`
