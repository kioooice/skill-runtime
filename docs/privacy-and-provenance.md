# Privacy And Provenance

Date: 2026-05-03

## Summary

Skill Runtime is local-first. Its default skill store, lifecycle metadata, trajectories, audits, runtime lane events, usage overlays, and dashboard HTML are stored on the local machine.

External data flow only happens when the user configures an external provider command, runs a future network-backed import command, or deliberately connects another host or platform integration. Those external paths must remain explicit and auditable.

## What Stays Local

By default, these files and directories stay in the workspace or local runtime root:

- `skill_store/active/`
- `skill_store/staging/`
- `skill_store/archive/`
- `skill_store/rejected/`
- `skill_store/index.json`
- `skill_store/collections.json`
- `trajectories/`
- `audits/`
- `.skill_runtime/runtime_lane_events.jsonl`
- `.skill_runtime/usage.json`
- `.skill_runtime/dashboard.html`
- `.skill_runtime/global-dashboard.html`
- local demo input and output files under `demo/` or test sandboxes

The dashboard is generated as static local HTML. It reads local runtime data and does not require a web service.

## What Can Leave The Machine

Nothing leaves the machine by default because the built-in fallback and semantic providers are local mock providers.

Data can leave the machine in these cases:

- A configured fallback provider command calls a remote model or service.
- A configured semantic review provider command calls a remote model or service.
- A DeepSeek provider is enabled through `SKILL_RUNTIME_FALLBACK_PROVIDER_CMD` or `SKILL_RUNTIME_SEMANTIC_PROVIDER_CMD`.
- A future GitHub, marketplace, or URL import command fetches external skill content.
- A host application outside this repository forwards task or trajectory data to another service.

Provider commands receive structured JSON on stdin. Depending on the provider, that JSON can include task summaries, inferred schemas, candidate skill source, prompts, trajectory fragments, heuristic audit issues, or review context. Treat provider commands as trusted local programs.

## Credentials

Do not store provider credentials in tracked files.

Allowed places:

- local shell environment variables
- Codex local environment configuration
- operating system secret managers
- CI or deployment secret stores, if this project is ever used in that context

Disallowed places:

- `README.md`
- docs files
- `skill_store/`
- `trajectories/`
- `audits/`
- committed `.env` files
- provider example scripts

Examples:

- `DEEPSEEK_API_KEY` must stay local.
- Future GitHub tokens for import must stay local.
- Future marketplace credentials must stay local.

## Provenance Types

Skill Runtime should keep source history visible because different skill origins carry different risk.

Current and expected provenance categories:

- `distilled`: generated from a local successful task trajectory.
- `imported`: copied from an external skill directory into staging.
- `manual`: authored directly by a developer or maintainer.
- `exported`: exposed to another platform by copy or symlink after explicit planning.
- `legacy`: older skill metadata that was created before full provenance fields existed.

Current local import metadata uses:

```json
{
  "audit_status": "requires_review",
  "import_source": "C:\\path\\to\\external\\skill",
  "content_hash": "<sha256>",
  "provenance": {
    "type": "local_skill_import",
    "source": "C:\\path\\to\\external\\skill",
    "content_hash": "<sha256>"
  },
  "tags": ["imported", "external", "requires_review"]
}
```

Imported skills must stay in staging until audited and promoted. They must not become active just because they were copied into the runtime.

## Dashboard Signals

Dashboard should make provenance and lifecycle visible without adding write controls.

Current dashboard behavior:

- lifecycle branches remain `active`, `staging`, `archived`, and `rejected`
- imported staging candidates display source path, content hash, and `requires_review`
- capability collections organize skills without changing execution semantics
- platform inventory is read-only
- export planning remains preview-only

Future dashboard provenance improvements should distinguish:

- distilled skills
- imported skills
- manually authored skills
- exported skills
- legacy skills with backfilled provenance

## Import And Export Boundaries

Local import:

- reads a local source directory
- requires `SKILL.md`
- copies content into `skill_store/staging/imported/<skill_name>/`
- writes staging metadata with provenance
- does not write active skills

GitHub or marketplace import:

- is not enabled in the current phase
- must enter staging only when added
- must record URL, commit or release reference when available, fetch time, content hash, and audit state
- must never bypass audit or promotion

Platform export:

- currently supports preview through `platform-export-plan`
- does not copy, symlink, or write platform directories in the preview phase
- must remain explicit when write support is added

## Operator Checklist

Before enabling any external provider or network import:

1. Confirm what data the command receives.
2. Confirm where credentials are stored.
3. Confirm the command writes only expected local outputs.
4. Confirm imported skill content enters staging, not active.
5. Confirm dashboard shows provenance and audit state.

## Non-Goals

This document does not make claims about third-party provider retention policies. Read the provider's own terms and privacy documentation before sending task or code context to that provider.

This document also does not turn Skill Runtime into a security sandbox. Provider commands are trusted local commands, and imported skills still require review before promotion.
