# Capability Collections Design

## Goal

Capability collections are a durable organization layer for skills. They help users understand capability areas without changing runtime execution, audit, promotion, archive, search, or reuse semantics.

## Boundary

Collections are not lifecycle states. A skill still belongs to exactly one lifecycle state at a time:

- `active`
- `staging`
- `archived`
- `rejected`

A skill can appear in multiple collections. Collections can include skills from any lifecycle state, but dashboard must keep the lifecycle state visible next to every skill.

## Storage

Workspace-level collections live at:

```text
skill_store/collections.json
```

Schema:

```json
{
  "collections": [
    {
      "collection_id": "direction-strategy",
      "label": "方向与策略",
      "description": "开发方向、部署路线和仓库影响判断。",
      "skill_names": [
        "pre_implementation_workflow_review",
        "deployment_strategy_review",
        "repo_impact_analysis"
      ]
    }
  ]
}
```

Field rules:

- `collection_id`: stable machine ID for the collection.
- `label`: user-facing name.
- `description`: short explanation shown in dashboard.
- `skill_names`: explicit skill references by existing `skill_name`.

Unknown skill references are preserved as `missing_skill_names` in dashboard data so stale collection entries can be spotted without breaking the page.

## Default Collections

When `skill_store/collections.json` is missing or invalid, the runtime uses read-only default collections:

- `direction-strategy`: 方向与策略
- `autonomous-execution`: 自动推进
- `runtime-safety`: 运行时与验证
- `session-continuity`: 会话接续

Default membership is explicit and limited to active workflow skills. Basic local file helpers are still available to the runtime and explicit search, but they are not part of the default dashboard collection surface. This fallback is display-only and does not write a collections file.

## Dashboard Behavior

Dashboard collector returns `capability_collections` next to `skills`, `events`, `governance`, and `platform_inventory`.

Each collection payload contains:

- `collection_id`
- `label`
- `description`
- `skill_names`
- `skills`
- `missing_skill_names`
- `status_counts`
- `read_only`

Dashboard rendering shows a dedicated `能力集合` page. The page is only a navigation and explanation surface. It must not expose promote, archive, import, export, edit, install, or execute controls.

The default dashboard renders workflow collections only. Basic local file-processing helpers are intentionally hidden from the default visual surface because they do not help users judge workflow value. A future explicit low-level utility view can be added separately if there is a real need.

## Safety Rules

- Collections never decide whether a skill is reusable.
- Collections never change search ranking.
- Collections never make staging skills executable.
- Collections never bypass audit or promotion.
- Collections never write platform directories.
- Collections do not replace provenance, audit status, or lifecycle metadata.

## Future Work

Possible later enhancements:

- CLI command to validate `collections.json`.
- CLI command to write or update collection definitions.
- Dashboard filtering by collection.
- Collection provenance showing whether a collection was default-inferred or file-backed.

These should remain separate from execution semantics.
