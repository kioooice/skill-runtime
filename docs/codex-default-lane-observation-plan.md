# Codex Default Lane Observation Plan

Date: 2026-04-30

## Goal

Use the current first migrated Codex default-lane entry as a controlled observation point before widening the lane.

This observation period is not for proving that “more migration is possible”.

It is for answering one narrower product question:

`Does the current default lane already improve normal Codex work without creating confusing behavior?`

## What Is Under Observation

The observation target is the first migrated existing entry:

- `agent-plan`
- `agent-plan-learning`

The lane should be judged on normal use, not only on synthetic tests.

## What Counts As A Good Observation Result

The current lane should be considered healthy if most real uses show all of the following:

- default-in tasks quietly benefit from reuse or clear planning
- default-out tasks stay out of the lane without confusing the user
- task results still feel like normal Codex task execution, not like manual skill handling
- post-task capture feels helpful instead of noisy
- no repeated surprise cases appear that would force the user to manually fight the lane

## What Counts As A Bad Observation Result

The lane should be considered not ready to widen if one or more of these become common:

- tasks that obviously should stay outside the lane keep trying to enter it
- tasks that should benefit from the lane keep falling through in confusing ways
- the user has to think about the runtime too often
- the current entry creates extra ceremony instead of reducing it
- repeated borderline cases suggest the whitelist is still too loose or too narrow

## What To Record During Observation

When a real task touches the current lane, record only the high-signal outcome:

- task type
- whether it was treated as `default-in`, `guarded-in`, or `default-out`
- whether that felt correct in normal use
- whether reuse, normal execution, or capture behavior felt helpful
- whether the user would reasonably expect the same behavior next time

This should be kept lightweight.

Do not turn the observation period into heavy manual logging.

## Exit Criteria For Widening

Only consider migrating a second existing entry if at least one of these becomes true:

- the current lane behaves cleanly across repeated real tasks
- a second entry would clearly remove repeated friction that the current one cannot cover
- a concrete recurring workflow appears that matches the current whitelist philosophy

## Stop Criteria

Do not widen the lane if:

- repeated misclassification appears
- the user experience becomes harder to predict
- the runtime starts feeling like a visible tool again instead of a background layer
- new work would mostly add more surface area without improving normal Codex use

## Recommended Position

The current recommendation is:

- keep the first migrated entry as the observation point
- widen only on evidence
- do not migrate a second entry just to show momentum
