# Open Source Release Readiness Checklist

Date: 2026-05-05

This checklist defines the docs-first readiness release for Skill Runtime. It is meant to prepare the repository for external review before any Codex plugin path or broader packaging work.

See also:

- `docs/v0.1.0-alpha-release-plan.md`

## Completed In This Stage

- MIT `LICENSE` added.
- Package metadata includes license, author, project URLs, keywords, and classifiers.
- README top sections now explain the maintainer-facing value.
- Three maintainer workflow demos exist:
  - review cleanup
  - release readiness
  - handoff continuation
- `CONTRIBUTING.md` added.
- `SECURITY.md` added.
- `CODE_OF_CONDUCT.md` added.
- `.gitignore` protects local `.env` files.
- Application draft created in `docs/codex-open-source-application-draft.md`.

## Pre-Release Verification

Run before tagging or public outreach:

```bash
python -m pip install -e .
python scripts/check_mcp_architecture.py
python scripts/check_runtime_contracts.py
python -m unittest tests.test_runtime_fast -v
git diff --check
```

Run the full suite before a release tag or broad announcement:

```bash
python -m unittest tests.test_runtime -v
```

## Maintainer Demo Verification

Keep these demos runnable and easy to inspect:

- `docs/main-demo-walkthrough.md`
- `docs/maintainer-review-cleanup-demo.md`
- `docs/maintainer-release-readiness-demo.md`
- `docs/maintainer-handoff-continuation-demo.md`
- `DEMO.md`

Each demo should keep:

- a realistic maintainer input fixture
- an expected maintainer output
- an observed task record
- a verification command or reproducible check

## Before Applying For OpenAI Support

Confirm:

- public GitHub repository URL is final
- maintainer GitHub profile is public and current
- project description in GitHub matches the README positioning
- issues/discussions are enabled if the maintainer wants public feedback
- no API keys or private runtime data are committed
- the application text is updated with real maintainer role, repository URL, and OpenAI organization ID

## Known Remaining Gaps

- Public traction is still weak and should not be overstated.
- The project is still a local MVP; README caveats should stay honest.
- The Codex plugin path remains a later option, not a readiness blocker.
- API credit usage should be tied to concrete semantic review, workflow distillation, and maintainer automation evaluation.
