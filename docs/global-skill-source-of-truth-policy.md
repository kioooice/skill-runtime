# Global Skill Source Of Truth Policy

## Decision

Reusable workflow skills should live as global Codex skills by default:

```text
C:\Users\Administrator\.codex\skills\<skill-name>\SKILL.md
```

The global Codex skill is the authoritative copy. Project files may route to it, index it, or adapt it, but should not duplicate the full workflow as another independent source of truth.

## Default Placement

- Cross-project workflow, reusable process, development method, review gate, handoff rule, deployment rule, verification rule, or reporting workflow: create a global Codex skill.
- Project-specific business knowledge, local project conventions, or temporary experiments: keep in the project.
- Skill Runtime distilled candidates: start in runtime staging; promote to a global Codex skill only when the workflow is broadly reusable.
- Runtime active skills: use for executable adapters, deterministic tools, governance experiments, and tests, not as the canonical home for general Codex workflow instructions.

## Naming

- Global Codex skills use hyphen names, for example `pre-implementation-workflow-review`.
- Skill Runtime executable skills may keep Python/runtime names with underscores, for example `pre_implementation_workflow_review`.
- `AGENTS.md` should route to the global hyphen skill name unless the task explicitly calls a Runtime active skill.

## Runtime Visibility

Skill Runtime should discover global Codex skills as read-only platform inventory. For global Codex skills under `C:\Users\Administrator\.codex\skills`, platform inventory marks them as:

```text
source_role: authoritative_global_skill
```

This lets dashboard and governance views see that the workflow exists globally without copying the full skill into `skill_store/active`.

## Promotion Path

When a staging Runtime skill represents a broadly reusable workflow, audit it first, then promote it to the global Codex skill library instead of project `skill_store/active`.

Use:

```text
python -m skill_runtime.cli promote-global-codex-skill --file <staging-skill.py>
```

For the full captured-workflow path, use:

```text
python -m skill_runtime.cli distill-and-promote --trajectory <trajectory.json> --skill-name <name> --promotion-target global-codex
```

or start from an observed task record:

```text
python -m skill_runtime.cli distill-and-promote --observed-task <observed-task.json> --skill-name <name> --promotion-target global-codex
```

The same target is available through the service API and MCP `distill_and_promote_candidate` tool as `promotion_target: "global_codex"`.

Workflow staging metadata tagged with `workflow`, `global-workflow`, or `codex-skill` should recommend `promote_global_codex_skill` after a passing audit. The resulting global skill writes:

- `<global skills dir>/<skill-name>/SKILL.md`
- `<global skills dir>/<skill-name>/agents/openai.yaml`

It does not create a project active copy and does not update the project active index.

## Avoiding Drift

Do not maintain two full copies of the same workflow. If a workflow exists globally and a project needs special behavior, prefer one of these:

- project `AGENTS.md` routes to the global skill
- project docs add only local constraints
- Runtime active skill acts as a thin executable adapter
- platform inventory indexes the global skill read-only

Update the global skill first when the general workflow changes.
