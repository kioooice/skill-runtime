# Import To Staging Policy

Date: 2026-05-03

## Goal

Allow local external skills to be studied inside Skill Runtime without bypassing distillation, audit, promotion, and governance.

This phase supports local directory import only. GitHub or marketplace import must wait until local import behavior is stable.

## Command

```powershell
python -m skill_runtime.cli import-skill-to-staging --source C:\path\to\skill-directory
```

The source directory must contain `SKILL.md`.

## Output Contract

The command returns JSON with:

- `skill_name`
- `status`
- `audit_status`
- `source_path`
- `staging_path`
- `metadata_path`
- `content_hash`
- `read_only_source`

## Staging Layout

Imported content is copied to:

```text
skill_store/staging/imported/<skill_name>/
```

Metadata is written to:

```text
skill_store/staging/<skill_name>.metadata.json
```

The source directory is read-only. The importer must not modify source files.

## Metadata Requirements

Imported metadata must include:

- `status: staging`
- `audit_status: requires_review`
- `import_source`
- `imported_at`
- `content_hash`
- `provenance.type: local_skill_import`
- `provenance.source`
- `provenance.content_hash`
- `tags` including `imported`, `external`, and `requires_review`

## Safety Rules

- Do not write to `skill_store/active`.
- Do not create an executable active skill.
- Do not silently reuse imported skills before promotion.
- Do not import a directory without `SKILL.md`.
- Do not fetch network sources in this phase.
- Do not treat import as audit approval.

## Lifecycle

Imported skills are candidates for human or semantic review.

Expected lifecycle:

```text
local external SKILL.md
-> import-skill-to-staging
-> staging metadata with provenance
-> audit / review
-> optional distillation or adaptation
-> promote only after approval
```

## Next Step

After local import is stable, the next safe extension is dashboard provenance display for imported candidates. GitHub import should come later and must use the same staging-only rule.
