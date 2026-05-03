# Platform Skill Inventory Design

Date: 2026-05-03

## Goal

Add a read-only inventory layer that shows where skills are visible across the current runtime root, known platform skill folders, and selected project roots.

This is the first low-risk lesson borrowed from `iamzhihuix/skills-manage`: make skill locations and ownership visible before adding install, export, import, or edit operations.

## Product Boundary

This inventory is not a skill manager and does not write to platform folders.

It answers:

- which known platforms have skill folders
- which `SKILL.md` directories are visible there
- whether a skill appears runtime-owned, project-local, external, or symlink-exported
- where the skill was found

It does not:

- install skills
- copy skills
- create symlinks
- promote imported skills
- change active/staging/archive/rejected lifecycle state

## Known Platform Roots

The first built-in platform registry is intentionally small:

| Platform ID | Display Name | Default Skill Directory |
| --- | --- | --- |
| `codex` | Codex | `~/.codex/skills` |
| `claude-code` | Claude Code | `~/.claude/skills` |
| `cursor` | Cursor | `~/.cursor/skills` |
| `gemini-cli` | Gemini CLI | `~/.gemini/skills` |
| `agents-shared` | Shared Agents | `~/.agents/skills` |

These roots are observation targets only. Missing folders are diagnostics, not failures.

## Inventory Item Model

Each discovered skill is normalized to:

```json
{
  "platform_id": "codex",
  "display_name": "Codex",
  "skills_dir": "C:/Users/Administrator/.codex/skills",
  "skill_name": "example-skill",
  "skill_path": "C:/Users/Administrator/.codex/skills/example-skill",
  "skill_file": "C:/Users/Administrator/.codex/skills/example-skill/SKILL.md",
  "ownership": "external",
  "link_type": "read_only",
  "source_root": "C:/Users/Administrator/.codex/skills",
  "is_read_only": true
}
```

## Ownership

`ownership` is a dashboard hint, not a lifecycle state.

- `managed_by_runtime`: the skill directory is under the current runtime root
- `project_local`: the skill directory is under an explicitly provided project root
- `external`: the skill directory is outside the current runtime root and project roots

Shared `.agents/skills` folders must remain `external` unless they are explicitly inside a project root. This avoids misreading a shared global skill library as project-local.

## Link Type

`link_type` is also read-only in this phase.

- `symlink_export`: the discovered skill directory is a symlink
- `read_only`: ordinary discovered directory

Future phases can add `copied_export` only when export/write support exists and records provenance.

## Dashboard Placement

The dashboard gets a separate `平台与项目` page.

This keeps platform inventory separate from:

- `技能树`: runtime lifecycle view
- `触发日志`: runtime lane behavior
- `治理快照`: skill library health
- `全局项目`: cross-project runtime events
- `全局日志`: cross-project trigger log

## Safety Rules

- Inventory collection must not call file write APIs.
- Inventory collection must not create missing platform directories.
- Inventory collection must not recurse beyond direct `*/SKILL.md` skill folders in this phase.
- Dashboard must show diagnostics for missing or unreadable roots without failing the whole page.

## Recommended Next Step

After this read-only inventory is stable, the next safest extension is `platform-export-plan`: show what would be copied or linked, but still do not write platform directories.
