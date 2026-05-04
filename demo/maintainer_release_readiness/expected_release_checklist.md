# Release Readiness Checklist

Release: `0.2.0`

## Ready

- License file exists.
- README has been updated.
- Fast tests are passing.
- Basic secret scan passed.
- Release notes have maintainer-facing entries.

## Must Fix Before Public Release

1. Add `CONTRIBUTING.md`.
   - Why: new contributors need the fast validation path and contribution expectations.

2. Add `SECURITY.md`.
   - Why: users need a clear private vulnerability reporting path.

3. Add `CODE_OF_CONDUCT.md`.
   - Why: public collaboration needs explicit behavior expectations.

4. Run the full test suite or record why it was skipped.
   - Current status: `not_run`

## Should Fix Soon

- Complete package metadata beyond the initial license and URL fields.
- Add a short release note that links to the maintainer workflow demos.

## Suggested Verification

```powershell
python -m unittest tests.test_runtime_fast -v
python scripts/check_runtime_contracts.py
git diff --check
```

## Maintainer Decision

Do not tag the public readiness release yet. Complete the community files and full verification record first, then re-run this checklist.
