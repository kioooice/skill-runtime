# Minimal Test Checklist

## CLI

- `search` returns an empty list when the index is empty
- `distill` rejects invalid trajectory files
- `audit` rejects missing skill files
- `promote` rejects skills without a passing audit
- `execute` rejects missing skills
- `execute` accepts `--args-file` for shell-safe invocation

## Trajectory

- valid trajectories can be saved and loaded
- invalid trajectories are rejected

## Audit

- detects `shell=True`
- detects `os.system`
- detects hardcoded absolute paths
- detects missing docstrings

## Promotion

- blocks missing audit reports
- blocks `needs_fix`
- accepts `passed`

## Retrieval

- `reindex` rebuilds `skill_store/index.json`
- `search` returns `score` and `why_matched`

## Execution

- active skills with `run` execute successfully
- active skills without `run` fail cleanly
- non-dict results are wrapped as `raw_result`

## End-to-End

- `log-trajectory -> distill -> audit -> promote -> search -> execute` runs successfully
