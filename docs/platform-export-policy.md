# Platform Export Policy

Date: 2026-05-03

## Goal

Provide a safe preview of how an active Skill Runtime skill would be exposed to a known agent platform skill directory.

This phase is plan-only. It does not write platform directories.

## Command

```powershell
python -m skill_runtime.cli platform-export-plan --skill merge_text_files --platform codex
```

For tests, custom setups, or manual dry checks:

```powershell
python -m skill_runtime.cli platform-export-plan --skill merge_text_files --platform codex --target-dir C:\path\to\skills
```

## Output Contract

The command returns JSON with:

- `skill_name`
- `platform_id`
- `display_name`
- `source_path`
- `target_root`
- `target_path`
- `link_type`
- `conflict`
- `requires_confirmation`
- `eligible`
- `read_only`
- `warnings`

## Eligibility

Only `active` skills are eligible.

Staging, archived, rejected, unknown, or unreadable skills return a preview payload with:

```json
{
  "eligible": false,
  "conflict": "skill_not_active"
}
```

This keeps external platform exposure behind the existing distill, audit, and promotion lifecycle.

## Link Type

The planner chooses:

- `symlink_export` on platforms where symlink export is the default plan
- `copied_export` when `--copy` is passed or Windows copy fallback is safer

The command never creates the link or copy. It only reports the proposed link type.

## Conflict Policy

The planner reports:

- `none`: target path does not exist
- `existing_symlink`: target path already exists as a symlink
- `existing_directory`: target path exists as a real directory
- `existing_file`: target path exists as a real file
- `skill_not_active`: source skill is not active
- `platform_not_found`: requested platform is not registered

Real directory and file conflicts are ineligible. The runtime must not overwrite them.

## Safety Rules

- Do not create missing platform directories.
- Do not copy skill files.
- Do not create symlinks.
- Do not overwrite real directories or files.
- Do not export non-active skills.
- Always mark the preview as `read_only: true`.
- Always require later explicit confirmation before any future write command.

## Next Step

If export planning proves useful, a later phase may add an explicit write command. That command must be separate from `platform-export-plan`, must require confirmation, and must preserve rollback or manual recovery guidance.
