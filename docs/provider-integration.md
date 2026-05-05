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

## DeepSeek Providers

This repository also includes DeepSeek command providers backed by the OpenAI-compatible Chat Completions API:

- `examples/providers/deepseek_fallback_provider.py`: asks DeepSeek to generate the fallback skill JSON payload.
- `examples/providers/deepseek_semantic_review_provider.py`: asks DeepSeek to review a candidate skill and return semantic findings.

Configuration:

```bash
export DEEPSEEK_API_KEY="<your-deepseek-api-key>"
export DEEPSEEK_MODEL="deepseek-v4-flash"
export SKILL_RUNTIME_FALLBACK_PROVIDER_CMD='["python", "examples/providers/deepseek_fallback_provider.py"]'
export SKILL_RUNTIME_SEMANTIC_PROVIDER_CMD='["python", "examples/providers/deepseek_semantic_review_provider.py"]'
```

PowerShell:

```powershell
$env:DEEPSEEK_API_KEY="<your-deepseek-api-key>"
$env:DEEPSEEK_MODEL="deepseek-v4-flash"
$env:SKILL_RUNTIME_FALLBACK_PROVIDER_CMD='["python", "examples/providers/deepseek_fallback_provider.py"]'
$env:SKILL_RUNTIME_SEMANTIC_PROVIDER_CMD='["python", "examples/providers/deepseek_semantic_review_provider.py"]'
```

Optional DeepSeek variables:

- `DEEPSEEK_API_BASE`: defaults to `https://api.deepseek.com`
- `DEEPSEEK_MODEL`: defaults to `deepseek-v4-flash`
- `DEEPSEEK_TIMEOUT_SECONDS`: defaults to `60`
- `DEEPSEEK_TEMPERATURE`: defaults to `0.0`
- `DEEPSEEK_REPAIR_ATTEMPTS`: defaults to `1`; set to `0` to disable the fallback provider's one-pass repair request

The DeepSeek fallback provider applies a local quality gate before returning generated code. It checks:

- Python syntax and `run(tools, **kwargs)` entrypoint
- required docstring sections: `功能描述`, `输入参数`, `输出结果`
- runtime tool calls that match the trajectory
- literal kwargs for every inferred input schema key
- supported keyword arguments for known runtime tools such as `copy_file` and `write_json`

If the generated code fails this gate, the provider sends the failure reason back to DeepSeek once and asks for a corrected JSON payload. The repaired candidate must pass the same local gate. If repair is disabled or the repaired candidate still fails, the provider exits with a non-zero status and the candidate is not written into staging.

Do not commit API keys. Set `DEEPSEEK_API_KEY` only in your local shell, Codex environment, or a secret manager.

Live smoke test:

```bash
python scripts/smoke_deepseek_provider_loop.py
```

PowerShell:

```powershell
python scripts/smoke_deepseek_provider_loop.py
```

The smoke test creates a temporary runtime sandbox, configures both DeepSeek providers, runs `distill_and_promote`, executes the promoted skill, and verifies the copied text file plus metadata sidecar. It does not write generated skills into the repository's real active library. Use `--keep-sandbox` only when debugging a failure.

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
  "provider_guidance": "- Generate executable workflow code, not a template summary.",
  "trajectory": {},
  "prompt": "Prompt text for the provider."
}
```

Request fields:

- `skill_name`: requested candidate skill name
- `summary`: short task summary for the workflow being distilled
- `docstring`: target docstring shape the generated `run(...)` function should satisfy
- `input_schema`: inferred input names and type strings for the candidate skill
- `provider_guidance`: structured fallback-generation guidance derived from the current trajectory family
- `trajectory`: captured successful task trajectory used as provider context
- `prompt`: the assembled fallback prompt string sent to prompt-driven providers

`provider_guidance` is part of the formal fallback request contract.

- It is structured guidance intended for provider-side logic or prompt assembly.
- The same guidance is also embedded into `prompt`.
- A provider may read `provider_guidance` directly, or it may ignore that field and work only from `prompt`.
- Providers must not treat `provider_guidance` as permission to relax audit requirements, auto-promote a generated candidate, or bypass maintainer judgment.

Compatibility note for the bundled example fallback providers:

- `copy_metadata_fallback_provider.py` reads the request JSON and uses `summary`; extra fields such as `provider_guidance` are ignored safely.
- `review_cleanup_fallback_provider.py` only validates that the stdin payload is JSON; extra request fields are ignored safely.
- `deepseek_fallback_provider.py` forwards the full request object to the model and remains compatible with added request fields because its local validation is applied to the generated candidate, not to a fixed request schema.

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
