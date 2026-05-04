# Contributing

Thanks for considering a contribution to Skill Runtime.

This project is a local workflow governance layer for Codex-style agents. The most valuable contributions are changes that make repeated maintainer workflows easier to capture, audit, reuse, or explain.

## Before You Start

- Read `README.md` or `README.en.md` for the current project shape.
- Check `DEMO.md` and the maintainer workflow demos before proposing a new feature.
- Keep changes focused. Small, reviewable pull requests are preferred.
- Do not commit API keys, local credentials, `.env` files, or private runtime output.

## Good First Contribution Areas

- Documentation improvements that make setup, demos, or governance easier to understand.
- Small bug fixes with a clear reproduction path.
- Tests for existing runtime, audit, retrieval, or governance behavior.
- Maintainer workflow demos that use realistic inputs and expected outputs.

## Development Setup

From the repository root:

```bash
python -m pip install --upgrade pip
python -m pip install -e .
python scripts/check_mcp_architecture.py
python scripts/check_runtime_contracts.py
python -m unittest tests.test_runtime_fast -v
```

The full suite is broader and slower:

```bash
python -m unittest tests.test_runtime -v
```

Use the fast suite for routine changes. Use the full suite before release-level changes or broad runtime behavior changes.

## Pull Request Checklist

- Explain the user-facing problem or maintainer workflow the change improves.
- Include focused tests or explain why the change is documentation-only.
- Keep generated local files out of the commit.
- Update README, docs, or demos when behavior changes.
- Run `git diff --check` before submitting.

## Scope Guard

Avoid adding new automation just because it is possible. This project favors governed lifecycle, auditability, provenance, and practical maintainer workflows over a large collection of unrelated skills.
