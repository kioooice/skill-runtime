# Provider Integration

Skill Runtime keeps mock providers as the safe default. Real generation or review can be connected through trusted local commands.

## Included Local Demo Providers

This repository includes two minimal command providers that exercise the real provider path without cloud credentials:

- `examples/providers/copy_metadata_fallback_provider.py`: generates an executable skill for copying one file and writing a JSON metadata sidecar.
- `examples/providers/pass_semantic_review_provider.py`: adds no extra semantic findings and lets the built-in heuristic findings decide the audit result.

Example configuration:

```bash
export SKILL_RUNTIME_FALLBACK_PROVIDER_CMD='["python", "examples/providers/copy_metadata_fallback_provider.py"]'
export SKILL_RUNTIME_SEMANTIC_PROVIDER_CMD='["python", "examples/providers/pass_semantic_review_provider.py"]'
```

PowerShell:

```powershell
$env:SKILL_RUNTIME_FALLBACK_PROVIDER_CMD='["python", "examples/providers/copy_metadata_fallback_provider.py"]'
$env:SKILL_RUNTIME_SEMANTIC_PROVIDER_CMD='["python", "examples/providers/pass_semantic_review_provider.py"]'
```

These demo providers are intentionally narrow. They prove the provider contract and host loop are runnable from a fresh clone, but they are not a general LLM backend.

## Environment Variables

- `SKILL_RUNTIME_FALLBACK_PROVIDER_CMD`: command used when no deterministic distillation rule matches a successful trajectory.
- `SKILL_RUNTIME_SEMANTIC_PROVIDER_CMD`: command used for provider-backed semantic review during audit.

Each variable can be either:

- a JSON array of command arguments, recommended for Windows-safe paths
- a shell-style command string for simple local commands

Example JSON-array value:

```json
["python", "providers/fallback_provider.py"]
```

## Fallback Provider Contract

The command receives a JSON object on stdin:

```json
{
  "skill_name": "generated_skill",
  "summary": "Task summary.",
  "docstring": "Skill docstring.",
  "input_schema": {"input_path": "str"},
  "trajectory": {},
  "prompt": "Prompt text for the provider."
}
```

It must return:

```json
{
  "code": "def run(tools, **kwargs):\n    return {\"status\": \"completed\"}\n",
  "provider_name": "my_fallback_provider",
  "reason": "Why this candidate was generated."
}
```

## Semantic Review Provider Contract

The command receives:

```json
{
  "file_path": "skill_store/staging/example.py",
  "source": "def run(...): ...",
  "trajectory": {},
  "heuristic_issues": [],
  "prompt": "Prompt text for the provider."
}
```

It must return:

```json
{
  "provider_name": "my_semantic_provider",
  "summary": "Review summary.",
  "issues": [
    {
      "rule_id": "provider-rule",
      "severity": "high",
      "message": "Human-readable issue."
    }
  ]
}
```

Use `severity: "high"` to block promotion. Return an empty `issues` list to add no provider findings.

## Safety Boundary

Provider commands are treated as trusted local commands. Do not point these variables at unreviewed scripts. If the variables are not set, Skill Runtime falls back to the built-in mock providers.
