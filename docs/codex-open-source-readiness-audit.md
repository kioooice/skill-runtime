# Codex Open Source Readiness Audit

Date: 2026-05-05

## Progress Updates

- 2026-05-05: Added `LICENSE` with MIT License text.
- 2026-05-05: Added package metadata for license, author, project URLs, keywords, and classifiers in `pyproject.toml`.
- 2026-05-05: Added license notes to `README.md`, `README.zh-CN.md`, and `README.en.md`.
- 2026-05-05: Added `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `.env` ignore rules, release readiness checklist, and Codex Open Source application draft.

## Verdict

Current status: nearly ready for a draft application, but not ready for final submission without maintainer-specific details.

Recommended route: prepare first, then apply.

The project has a credible technical base, a public GitHub repository, installable Python package metadata, CI, tests, docs, community onboarding files, maintainer workflow demos, and a clear Codex-adjacent direction. The main remaining gap is final application evidence: real maintainer identity fields, OpenAI organization ID, and any external validation or traction.

## Target Programs

- Codex for Open Source: https://openai.com/form/codex-for-oss
- Codex open source fund: https://openai.com/form/codex-open-source-fund/

Codex for Open Source asks for a public GitHub user, public repository URL, maintainer role, why the repository qualifies, interest in Codex Security or API credits, OpenAI organization ID, and how API credits would be used.

The open source fund is broader and asks how API credits would support the project.

## Current Strengths

- Repository is public at `https://github.com/kioooice/skill-runtime`.
- The project already has a coherent technical thesis: a local governed skill runtime under Codex-like host agents.
- `pyproject.toml` defines an installable package named `skill-runtime`.
- Console entry points exist: `skill-runtime` and `skill-runtime-mcp`.
- README files exist in Chinese and English.
- CI exists at `.github/workflows/runtime-contracts.yml`.
- Fast and full test suites are documented in `TESTS.md`.
- Privacy and provenance boundaries are documented in `docs/privacy-and-provenance.md`.
- There is a local demo in `DEMO.md`.
- The repo has meaningful runtime, audit, governance, dashboard, Codex integration, and provider integration docs.

## Current Gaps

### Blocking Before Application

- `LICENSE` file has now been added with MIT License text.
- `CONTRIBUTING.md` has now been added.
- `SECURITY.md` has now been added.
- `CODE_OF_CONDUCT.md` has now been added.
- `pyproject.toml` now declares license, author, project URLs, keywords, and classifiers.
- The public GitHub repository currently shows very low external traction: 0 stars, 0 forks, 0 issues, 0 pull requests, and 18 commits at the time checked.
- The README top section has been rewritten around maintainer value, but should still be checked on GitHub after rendering.
- A short application-ready positioning statement now exists in `docs/codex-open-source-application-draft.md`.
- The project now has three maintainer workflow demos tied to review cleanup, release readiness, and handoff continuation.
- Final submission still needs user-specific fields: public GitHub profile, OpenAI organization ID, request scope, and any real external validation.

### Important But Not Blocking

- The repo contains a large amount of historical runtime data: `observed_tasks`, `trajectories`, `audits`, and `skill_store` account for thousands of tracked files. This may be acceptable for a research/runtime project, but it makes the repo harder to evaluate quickly.
- The README still contains internal-stage language such as local MVP and mock provider caveats. That honesty is good, but the top-level narrative should distinguish "usable now" from "future work" more cleanly.
- There are many internal process documents under `docs/`. Useful for handoff, but public users need a shorter entry path.
- The project name `Skill Runtime` is descriptive, but the ecosystem already has other skill runtime / skill registry projects. The differentiation should be explicit: governed lifecycle, audit, provenance, local-first Codex integration, and maintainer workflow capture.
- The current demo proves the self-evolving skill loop, but not yet an open-source maintainer workflow.

## Sensitive Information Check

No obvious committed real API key was found in the audit scan.

Observed matches were expected references to environment variables such as `DEEPSEEK_API_KEY`, example placeholders, and documentation saying credentials must stay local.

Before public promotion, run a deeper secret scan. Basic `.env` patterns have now been added to `.gitignore`.

Recommended `.gitignore` additions:

```text
.env
.env.*
!.env.example
```

## Recommended Positioning

Use this as the working one-liner:

```text
Skill Runtime is a local, governed workflow layer for Codex-style coding agents that helps open-source maintainers capture, audit, reuse, and improve repeatable maintenance workflows.
```

Avoid positioning it as:

- a second chat agent
- a generic skill collection
- a dashboard project
- a way to get free membership

## Application Narrative Draft

Why the repository qualifies:

```text
Skill Runtime helps open-source maintainers turn repeated Codex workflows such as review cleanup, release checks, handoff updates, and maintenance automation into governed reusable skills. It emphasizes audit, provenance, local-first execution, and explicit promotion instead of unreviewed agent-generated scripts.
```

How API credits would be used:

```text
API credits would support provider-backed semantic review, workflow distillation tests, maintainer automation demos, release-prep validation, and evaluation of Codex-assisted review and triage workflows across realistic open-source maintenance tasks.
```

Both drafts fit the 500-character constraint, but they should be tightened after demos are chosen.

## Recommended Next Stage

Prepare the final application packet from `docs/codex-open-source-application-draft.md`.

Minimum remaining inputs:

- public GitHub profile URL
- OpenAI organization ID
- request scope: Codex Security, API credits, or both
- any current users, stars, forks, issues, posts, demos, or external validation

Do not build new plugin features only for application optics.
