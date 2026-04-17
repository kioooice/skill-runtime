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
