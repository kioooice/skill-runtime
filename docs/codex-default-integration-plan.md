# Codex Default Integration Plan

Date: 2026-04-29

## Goal

Turn the current agent-first runtime from an optional capability into a controlled default path for Codex.

This does not mean every Codex task should enter the runtime.

It means Codex should quietly use the runtime by default only where the task is:

- local
- workflow-like
- low-risk, or a medium-risk development workflow that is observation-only
- reversible enough
- likely to benefit from reuse

## Product Intent

The user should not need to think:

- which skill should I search for
- should I manually promote this as a skill
- should I tell Codex to learn from this

Instead, the intended Codex behavior is:

1. receive a normal task
2. decide whether this task belongs to the runtime lane
3. if yes, try silent reuse conservatively
4. if reuse does not fit, do the task normally
5. after success, recover reusable experience when worth keeping

## Integration Position

The runtime should be attached to the Codex task lifecycle, not to random tool calls.

The default shape should be:

`user task -> Codex task intake -> runtime gate -> normal execution -> runtime finalize`

That means the runtime sits:

- before the main execution path, as a reuse gate
- after the main execution path, as a learning gate

It should not sit:

- as a mandatory wrapper around every MCP call
- as a required user-visible skill search step
- as a forced replacement for conversational or high-risk work

## Controlled Default Entry

### Default-in tasks for phase one

These are the first tasks that should enter the runtime lane by default:

- local file transformation tasks
- local file organization tasks
- project maintenance tasks with explicit file targets
- structured export or format conversion tasks
- repetitive workspace workflows with predictable inputs and outputs
- development workflow observation tasks with an explicit workspace and output artifacts

Examples:

- merge or clean local text files
- update project state files
- convert JSON records into CSV
- copy, rename, normalize, or archive workspace files
- implement a code/test/dashboard/docs change while disabling silent reuse

### Default-out tasks for phase one

These tasks should stay outside the runtime lane by default:

- open-ended conversation
- architecture discussion without execution
- broad code review
- high-risk destructive operations
- tasks with unclear target files or unclear success conditions
- tasks that mainly depend on external services, browsers, or remote systems
- one-off reasoning tasks with no stable workflow shape

Examples:

- “review this whole architecture”
- “decide the roadmap”
- “investigate why production users are angry”
- “log into a third-party site and fix the account state”

## Runtime Gate Rules

For Codex default integration, the runtime gate should answer one question first:

`Should this task even enter the runtime lane?`

The answer should be `yes` only if all of the following are true:

- the task is executable, not only conversational
- the task has a local-workflow shape
- the likely side effects are bounded
- rollback or failure explanation is realistic
- reuse could plausibly save future work
- broad development work can enter for observation, but should normally disable silent reuse

If any of those fail, Codex should skip the runtime lane and continue normally.

## Silent Reuse Rules

Even inside the runtime lane, silent reuse must stay conservative.

Keep the current policy:

- score `>= 0.85`
- arguments sufficiently complete
- scope compatible
- risk compatible

If those checks fail:

- do not auto-execute
- return to normal Codex execution

This keeps default integration from becoming overreach.

## Post-Task Learning Rules

Phase one default integration should stop at:

`capture + recommendation`

That means:

- Codex may recover the successful workflow as a trajectory
- Codex may receive a recommendation such as `distill_trajectory`
- Codex should not silently continue into automatic `distill/promote` by default

This keeps learning visible enough for governance while still removing most manual ceremony.

## Rollout Shape

### Phase 1 - Controlled default lane

Codex defaults into the runtime lane only for the low-risk local workflow class.

Behavior:

- try silent reuse
- if not suitable, execute normally
- after success, capture trajectory and return recommendation

### Phase 2 - Expand task coverage

Only after phase-one evidence is good:

- add more local workflow classes
- improve host-side task classification
- refine failure and opt-out handling

### Phase 3 - Reconsider deeper automation

Only after the default lane feels trustworthy:

- consider selective automatic distillation
- consider improvement of existing skills as a normal path

## First Code Target

The first real default integration target should not be the whole MCP surface.

It should be the Codex-side task intake path for:

- explicit local workflow tasks
- explicit workspace maintenance tasks

The existing experimental MCP tools remain useful as:

- proof path
- smoke path
- fallback path

But they should not be the final default product shape.

## Success Criteria

Codex default integration is working when all of the following become true:

- the user can give a normal local workflow task without naming a skill
- Codex quietly reuses an existing skill when appropriate
- Codex does not silently overreach on weak matches
- successful under-covered tasks are captured without extra ceremony
- the user experience feels like “Codex got smarter”, not like “I used a skill tool”

## Current Recommendation

Do not fully switch Codex default behavior yet.

The next safe step is:

1. define the Codex-side task classification boundary
2. define the low-risk default-in task set
3. attach the runtime gate only to that controlled class first

This keeps the product moving toward real default integration without pretending all Codex work is already runtime-ready.
