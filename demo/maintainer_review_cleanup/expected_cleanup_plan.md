# Review Cleanup Plan

Pull request: #42 - Add runtime dashboard export

## Required Fixes

1. Guard dashboard export paths.
   - Source comment: `RC-101`
   - File: `skill_runtime/dashboard/render.py`
   - Action: ensure the output path resolves inside the intended workspace or configured output directory before writing.
   - Verification: add or run a path traversal regression.

2. Add regression coverage for path traversal.
   - Source comment: `RC-102`
   - File: `tests/test_runtime_dashboard.py`
   - Action: test that `../` or absolute-path escape attempts are rejected.
   - Verification: run the focused dashboard test module.

## Follow-Up Documentation

1. Clarify dashboard output handling.
   - Source comment: `RC-103`
   - File: `README.md`
   - Action: mention that generated dashboard HTML is local output and should not be committed.

## Suggested Verification

```powershell
python -m unittest tests.test_runtime_dashboard -v
git diff --check
```

## Maintainer Decision

Do the required fixes before merge. The README clarification can be included in the same pull request if the code patch already touches dashboard docs; otherwise it can be a follow-up issue.
