# Security Policy

## Supported Versions

This repository is in early local-MVP development. Security fixes should target the current `main` branch unless a release branch is introduced later.

## Reporting A Vulnerability

Please report security issues privately through the repository maintainer contact path on GitHub. Do not open a public issue for secrets, credential exposure, code execution bugs, path traversal, or provider-command vulnerabilities.

When reporting, include:

- the affected command, API, MCP tool, or workflow
- steps to reproduce
- expected impact
- whether credentials, private files, or external commands are involved

## Security Boundaries

Skill Runtime is local-first and file-based, but it can run provider commands, inspect workspace files, and generate executable skills. Treat these surfaces as sensitive:

- external fallback and semantic provider commands
- generated staging skills
- promoted active skills
- MCP tool calls
- local `.skill_runtime` data
- demo or observed-task records that may contain project context

Do not commit API keys, `.env` files, private provider configs, or captured private workspace content.

## Maintainer Response

For credible reports, maintainers should:

1. acknowledge the report
2. reproduce or scope the issue
3. prepare a fix or mitigation
4. document any required user action
5. publish the fix after sensitive details are safe to disclose
