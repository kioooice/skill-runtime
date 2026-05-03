# Codex Task Classification Boundary

Date: 2026-04-29

## Purpose

This document defines which Codex task classes should enter the runtime lane by default in phase one, which ones should stay out, and which ones require an explicit higher bar before entering.

The goal is not to classify every task perfectly.

The goal is to keep Codex default integration safe, useful, and product-consistent.

## Three Buckets

Codex tasks should be divided into three buckets:

1. default-in
2. guarded-in
3. default-out

## 1. Default-In

These tasks should enter the runtime lane by default in phase one.

### Required traits

All of the following should be true:

- the task is local to the workspace
- the task has a clear execution target
- the task has a workflow shape, not only a thinking shape
- the side effects are bounded
- failure can be explained clearly
- reuse would plausibly help on similar future tasks

### Typical task classes

- local file transformation
- local file cleanup or normalization
- local file organization
- structured format conversion
- project maintenance with named files
- repetitive workspace operations with predictable inputs and outputs
- development workflow observation with an explicit workspace and artifacts

### Examples

- merge several text files into one output file
- clean trailing whitespace in a folder of text files
- convert JSON records into CSV
- update `HANDOFF.md`, `TASKS.md`, and `DECISIONS.md`
- archive local files by a clear pattern
- implement a dashboard/test/docs change with explicit output files, while silent reuse is disabled

## 2. Guarded-In

These tasks may enter the runtime lane, but only after a stronger gate.

They are not safe enough for broad default-in, but they are also not broad enough to ban outright.

### Typical risk signals

- partial external dependency
- wider file scope
- more ambiguous success condition
- rollback is possible but not trivial
- useful workflow shape exists, but the task may branch

### Typical task classes

- medium-scope repository refactors without stable output artifacts
- local code generation tasks with clear output paths
- multi-step content reshaping with human-readable success criteria
- local tasks that touch many files but still stay within one workspace

### Phase-one rule

For now, these tasks should not auto-enter the runtime lane silently.

They should require one of:

- an explicit host-side allowlist
- a narrow trigger rule
- a later phase after default-in evidence is strong

## 3. Default-Out

These tasks should stay outside the runtime lane by default.

### Typical task classes

- open-ended conversation
- strategy, planning, or product judgment without direct execution
- broad code review
- high-risk destructive operations
- tasks with unclear files or unclear outputs
- tasks dominated by browser, remote service, or external system state
- tasks whose main value is reasoning rather than repeatable execution

### Examples

- “review this architecture”
- “design the roadmap”
- “figure out why users dislike the product”
- “log into a third-party console and repair the account”
- “investigate an unknown production issue across many systems”

## Decision Order

Codex-side classification should happen before silent skill reuse.

The order should be:

1. classify the task bucket
2. if `default-out`, skip runtime lane
3. if `guarded-in`, require stronger host-side rule
4. if `default-in`, allow runtime gate evaluation
5. only then evaluate silent reuse rules

This avoids a bad product shape where every task first behaves like a hidden skill search.

## Phase-One Working Rule

For the first real Codex default integration:

- only `default-in` tasks should enter automatically
- `guarded-in` tasks stay manual or experimental
- `default-out` tasks stay on the normal Codex path

## First Recommended Default-In Set

For the first production-like Codex lane, the recommended starting set is:

- local text transformation tasks
- local structured conversion tasks
- project state-file maintenance tasks
- low-risk workspace organization tasks
- development workflow observation tasks with explicit workspace and artifacts

This starting set is still narrow on purpose.

It is broad enough to create real product value, including normal Codex development work, but narrow enough to avoid pretending Codex is already runtime-ready for everything. For broad development workflows, hosts should normally pass `allow_silent_reuse=false`, so the runtime observes and learns without silently executing unknown code changes.

## What Counts As Success

This boundary is working if:

- Codex does not try to runtime-wrap obviously conversational work
- Codex does not runtime-wrap high-risk or external tasks
- local workflow tasks enter the lane consistently
- the user feels less skill ceremony, not more

## Current Recommendation

The next implementation step should be:

1. express this bucket model in a small host-side classifier
2. map only the first recommended default-in set
3. keep all other classes outside the lane until evidence justifies expansion
