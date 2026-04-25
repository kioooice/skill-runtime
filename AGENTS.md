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
- In auto mode, keep executing while remaining silent. Do not send progress updates, stage summaries, small-milestone reports, test-pass reports, or “current step” narration.
- Do not treat `自动模式开始` as a state-only message that allows waiting for more instructions.
- Only interrupt auto mode when:
  - required information is missing and execution cannot continue
  - there is an irreversible branch that must be decided by the user
  - there is a substantial blocker that cannot be recovered from autonomously
- If auto mode stops for any reason, explicitly state why it stopped. Do not leave a silent gap or an unexplained pause.
- If auto mode stops after a completed execution round, state that the round was completed and why execution is not continuing automatically.
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
