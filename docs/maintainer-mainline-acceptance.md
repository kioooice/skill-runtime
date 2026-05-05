# Maintainer Mainline Acceptance

Date: 2026-05-05

## Goal

Define one core workflow that represents the real product shape of Skill Runtime.

This document is not a UI spec. It is the acceptance path for the mainline:

`direction review when needed -> runtime gate -> Codex completes task -> finalizer records learning -> evolution or promotion stays explicit`

The chosen maintainer task family is:

`handoff continuation`

This is the best first mainline because it is:

- real maintainer work
- local-first
- easy to verify without external systems
- already aligned with repository state files
- a good fit for Skill Runtime's value: durable workflow memory instead of chat-only memory

## Why This Is The Mainline

This project no longer needs more proof that isolated runtime parts exist.

The core question is now:

`When a maintainer resumes work, does the system produce a reliable continuation path and capture that workflow in a governed way?`

If the answer is yes, the mainline is real.

If the answer is no, more dashboard work does not help.

## Scope

This acceptance path covers:

1. when `pre-implementation-workflow-review` should run
2. when the Codex-facing runtime gate should run
3. what the maintainer-facing output should be
4. when the finalizer should capture learning
5. when the result should stay as observation, become an evolution candidate, or be promoted later

This acceptance path does not cover:

- dashboard expansion
- new rich UI
- silent auto-promotion
- external GitHub or API integrations

## Chosen Task Family

### Handoff continuation

Input shape:

- durable repository state such as `HANDOFF.md`, `TASKS.md`, and optional `DECISIONS.md`
- a maintainer request to continue work, resume safely, or decide the next concrete step

Expected output shape:

- a continuation brief that states current goal, current stage, completed work, next action, risks, and decision branch

The output must help a maintainer or the next Codex session continue work without relying on old chat context.

## Mainline Phases

### Phase 0 - Direction review only when the request is actually about route choice

Use `pre-implementation-workflow-review` only when the maintainer is asking things like:

- should we keep building this feature
- should we switch direction
- is this next stage worth doing

Do not force direction review on ordinary continuation requests.

For a plain "continue from handoff" task, this phase is skipped.

Acceptance check:

- ordinary continuation requests do not get blocked by unnecessary route review
- route-change requests do get a clear verdict before implementation

### Phase 1 - Runtime gate

The Codex-facing runtime gate runs before substantive work.

For handoff continuation, the runtime should usually:

- enter the lane for observation
- not silently replace the task with an unrelated generic skill
- keep visible `runtime_lane_status` and `runtime_lane_reason`

Desired behavior:

- `entered` is acceptable
- `used` is acceptable if a strong existing workflow match is truly appropriate
- `skipped` is acceptable only when the request falls outside the current runtime lane boundary

Acceptance check:

- the event is visible through runtime lane logging
- the lane does not distort the maintainer task

### Phase 2 - Codex completes the maintainer task

Codex reads durable state and produces the continuation brief.

The brief should answer:

- what is the maintainer trying to achieve
- what has already been completed
- what exact action comes next
- what remains uncertain
- whether there is a decision branch that should stop implementation

This is the user-visible value.

Acceptance check:

- the brief is usable without old chat context
- the next step is concrete
- the result is maintainer-facing, not an internal runtime dump

### Phase 3 - Finalizer

After successful completion, the Codex-facing finalizer runs when there is structured execution output worth capturing.

The finalizer should:

- record that the workflow happened
- preserve the observed task or equivalent structured artifact
- return a learning decision without silently mutating the global library

Acceptance check:

- the workflow leaves a usable runtime event or trajectory artifact
- follow-up actions are explicit
- no automatic promotion happens

### Phase 4 - Learning outcome

The finalizer result should land in one of these buckets:

- `skip`: the existing workflow already handled the task cleanly
- `observed_only`: useful sample, but not enough to propose library change
- `improve_existing_skill_candidate`: the task exposed a gap in an existing workflow skill
- `new_skill_candidate`: only when this is truly a new repeatable workflow, not a duplicate

For the chosen mainline, the preferred default is:

- `observed_only` for normal successful continuation
- `improve_existing_skill_candidate` when the continuation flow exposes a gap in `session-handoff-maintenance` or a related workflow skill

Acceptance check:

- the system prefers improving an existing workflow over creating duplicates
- learning stays governed and explicit

## Happy Path

```text
Maintainer says: continue from handoff
-> Codex reads HANDOFF.md
-> runtime gate records lane entry
-> Codex produces continuation brief
-> finalizer captures the successful workflow
-> result stays observed_only, or creates an improve_existing_skill_candidate if a real gap was exposed
-> any later promotion remains manual and reviewable
```

## Failure Boundaries

The mainline is not acceptable if any of these happen:

- Codex needs old chat history instead of repository state
- runtime gate blocks or warps ordinary continuation work
- finalizer silently promotes or rewrites a skill
- the system creates duplicate new-skill candidates when an existing workflow should be improved
- dashboard visibility becomes the primary success measure

## Acceptance Criteria

The maintainer mainline is considered proven when all of the following are true:

1. A real handoff continuation request can be completed from repository state alone.
2. The runtime gate leaves a visible lane event without hijacking the task.
3. The maintainer-facing output is a usable continuation brief.
4. The finalizer returns a governed learning outcome.
5. When the flow exposes a gap, the system can prefer evolution of an existing workflow skill.

## Stop Conditions Before Further Expansion

Do not expand dashboard or add more surface area until this mainline is clearly proven.

Stop and reevaluate if work starts drifting into:

- collecting more `used` or `entered` samples as an end in itself
- adding more generic skills without changing the mainline
- polishing observation UI before the maintainer workflow itself is clearly valuable

## Next Implementation Target

The next practical target should be one of these, in order:

1. create a runbook that exercises this exact mainline end to end using the existing handoff continuation demo
2. add one acceptance-style test that proves the mainline can produce the expected continuation brief plus governed learning outcome
3. only after that, decide whether any runtime boundary or lifecycle behavior needs code changes
