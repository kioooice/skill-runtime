# Codex Open Source Packaging Decision

Date: 2026-05-05

## Current Plan Position

Stage 4 of 5: packaging route chosen.

Completed:

- Stage 1: readiness audit
- Stage 2: public positioning and README/application narrative
- Stage 3: maintainer workflow demos

## Decision

Chosen route:

1. docs-first open-source readiness release

Other routes kept for later:

2. CLI package hardening
3. Codex plugin path

## Option 1: Docs-First Open-Source Readiness Release

What it means:

- Add missing community files: `CONTRIBUTING.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`
- Add a release checklist section or release note
- Keep demos local and easy to run
- Avoid new runtime or plugin features
- Prepare the repository for external review first

Pros:

- Fastest route to a credible public repository
- Directly addresses current readiness blockers
- Low implementation risk
- Best fit for the current application evidence gap

Cons:

- Does not create a new install surface
- Less exciting than a plugin demo
- External traction still needs community sharing

Best when:

- The goal is to become application-ready without overbuilding.

## Option 2: CLI Package Hardening

What it means:

- Improve package metadata and command help
- Add a short installed-command quickstart
- Possibly add release tags or PyPI readiness notes
- Keep the main product as local CLI + MCP runtime

Pros:

- Strengthens actual usability
- Supports open-source maintainers who want to try the project locally
- Builds on existing `skill-runtime` and `skill-runtime-mcp` entry points

Cons:

- More implementation and verification than docs-first
- Still may not answer why the project qualifies for Codex for Open Source
- Packaging polish can expand into unrelated release work

Best when:

- The goal is a more usable developer tool release before public outreach.

## Option 3: Codex Plugin Path

What it means:

- Create or refine a Codex plugin-facing package, connector, or skill bundle shape
- Make the project feel directly "Codex plugin-level"
- Potentially add plugin metadata, install instructions, or a curated demo path

Pros:

- Closest to the user's original plugin-level goal
- Stronger Codex-specific story if done well
- Could make demos more concrete for Codex users

Cons:

- Higher risk of building for optics instead of user value
- Current readiness blockers are still community/docs/demo evidence, not missing plugin code
- Plugin APIs and distribution expectations may change
- Could delay application readiness

Best when:

- There is a clear target plugin interface and a concrete user workflow that requires it.

## Recommendation

Choose Option 1 now: docs-first open-source readiness release.

Reason:

The project already has CLI, MCP, runtime, dashboard, and maintainer demos. The biggest current blockers are public trust and onboarding: license was fixed, but contributing, security, code of conduct, release-readiness docs, and public application narrative are still incomplete. A plugin path can come after the repository is easier to evaluate.

## Stage Result

The docs-first route has been accepted. Stage 4 output is the packaging decision plus the community and readiness documents listed in `docs/open-source-release-readiness-checklist.md`.

Do not continue into plugin implementation unless a later value gate shows that a plugin path is necessary for a concrete maintainer workflow.

Next stage: prepare the final application packet and identify user-specific fields that cannot be filled from the repository.
