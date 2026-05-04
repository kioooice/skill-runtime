# Codex Open Source Positioning

Date: 2026-05-05

## One-Line Positioning

Skill Runtime helps Codex-style agents capture, audit, reuse, and improve repeatable maintainer workflows.

## Public Project Narrative

Skill Runtime is a local workflow governance layer for Codex-style coding agents. It helps open-source maintainers turn repeated review, triage, release, handoff, and maintenance automation workflows into auditable, reusable, improvable skills. The project focuses on lifecycle control: search before rebuilding, execute through a stable contract, capture successful work, distill candidate skills, audit them, promote only reviewed skills, and preserve provenance.

## Differentiation

Skill Runtime should be positioned as:

- local-first workflow governance for coding agents
- audit and provenance for agent-generated or imported skills
- a lifecycle layer under Codex, MCP, CLI, or future hosts
- a maintainer automation memory that can improve over time

It should not be positioned as:

- a generic skill registry
- a second chat agent
- a dashboard-first product
- an MCP-only tool collection
- an application built only to qualify for a grant

## README Top-Section Plan

The README first screen should answer these questions in order:

1. Who is this for?
2. What repeated maintainer workflows does it help with?
3. Why is governance necessary before reuse?
4. What loop does it implement?
5. How does it relate to Codex, MCP, and CLI?

Current update status:

- Chinese README top section rewritten around open-source maintainer workflows.
- English README top section rewritten around the same positioning.
- The detailed runtime architecture remains below the public-facing intro.

## Community File Checklist

Recommended next public-readiness files:

- `CONTRIBUTING.md`: explain how to run fast tests, when to run full tests, and how to propose workflow/demo changes.
- `SECURITY.md`: explain supported versions, vulnerability reporting, and secret-handling expectations.
- `CODE_OF_CONDUCT.md`: use a standard contributor covenant style unless the maintainer prefers a shorter custom policy.
- `.env.example`: optional; only add if provider setup becomes part of a standard demo path.

## Maintainer Workflow Demo Candidates

### 1. Review Cleanup Workflow

Goal: show how a maintainer can capture repeated PR review cleanup steps.

Status: first demo created.

Files:

- `docs/maintainer-review-cleanup-demo.md`
- `demo/maintainer_review_cleanup/review_comments.json`
- `demo/maintainer_review_cleanup/expected_cleanup_plan.md`
- `demo/maintainer_review_cleanup/observed_task.json`

Success criteria:

- input includes a small review/comment fixture: done
- output includes a normalized action plan or patch checklist: done
- runtime records provenance and avoids auto-promoting unreviewed skills: done through `capture-trajectory` into a temporary runtime root
- README or demo index can link to the demo in one sentence: done through `DEMO.md`

### 2. Release Readiness Workflow

Goal: show how a maintainer can run a repeatable release-prep checklist.

Status: demo created.

Files:

- `docs/maintainer-release-readiness-demo.md`
- `demo/maintainer_release_readiness/release_inputs.json`
- `demo/maintainer_release_readiness/expected_release_checklist.md`
- `demo/maintainer_release_readiness/observed_task.json`

Success criteria:

- input includes repository metadata and test checklist: done
- output flags missing license/community/docs/test requirements: done
- demo uses local-only data and does not require API keys: done
- result maps to a clear maintainer decision: done

### 3. Handoff And Continuation Workflow

Goal: show how Codex can preserve project state across long maintenance work.

Status: demo created.

Files:

- `docs/maintainer-handoff-continuation-demo.md`
- `demo/maintainer_handoff_continuation/handoff_inputs.json`
- `demo/maintainer_handoff_continuation/expected_continuation_brief.md`
- `demo/maintainer_handoff_continuation/observed_task.json`

Success criteria:

- input includes `HANDOFF.md`, `TASKS.md`, and `DECISIONS.md`: done through summarized fixture
- output updates or summarizes the next-session state: done
- workflow demonstrates why durable state beats chat-only memory: done
- demo stays understandable to non-expert maintainers: done

## Application Drafts

Why this repository qualifies:

```text
Skill Runtime helps open-source maintainers turn repeated Codex workflows such as review cleanup, release checks, handoff updates, and maintenance automation into governed reusable skills. It emphasizes audit, provenance, local-first execution, and explicit promotion instead of unreviewed agent-generated scripts.
```

How API credits would be used:

```text
API credits would support provider-backed semantic review, workflow distillation tests, maintainer automation demos, release-prep validation, and evaluation of Codex-assisted review and triage workflows across realistic open-source maintenance tasks.
```

## Stage 2 Result

Stage 2 is complete when:

- README top sections explain maintainer value before runtime internals
- this positioning document exists
- license recommendation is settled
- community file gaps are named
- maintainer workflow demo candidates have success criteria

## Stage 3 Result

Stage 3 demo set is complete:

- review cleanup demo
- release readiness demo
- handoff continuation demo

Each demo has a local fixture, expected maintainer-facing output, an observed task record, documentation, and a verified `capture-trajectory` path using a temporary runtime root.
