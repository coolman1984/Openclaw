---
name: task-watch
description: Pending-work monitoring and completion follow-up for long-running tasks, sub-agents, reviews, tests, and background jobs. Use when you need recurring status checks, 2-minute wakeups, completion notifications, blocker tracking, or a clean handoff from waiting to done.
---

# Task Watch

## Overview
Use this skill when work is pending and the important job is not execution, but vigilant follow-up. It keeps long-running work from going silent by defining check intervals, escalation rules, and completion notifications.

## When to use it
Use this skill when any of the following is true:
- a sub-agent is running
- a review or test is still pending
- a background job may finish later
- a user explicitly asks to be notified when something completes
- a task has unclear finish timing and needs repeated checks

## Operating loop
1. Record what is pending.
2. Set the next check time.
3. Re-check at a short interval, usually every 2 minutes.
4. If still pending, keep the loop alive.
5. If finished, notify immediately and summarize the result.
6. If blocked, state the blocker, impact, and next action.

## Status states
Use these states consistently:
- **pending** — still running or waiting
- **finished** — completed successfully
- **blocked** — cannot proceed without help
- **failed** — ended with an error
- **stale** — too old without a useful update

## Check discipline
For pending work:
- check every 2 minutes by default
- do not silently wait
- do not assume completion without verification
- escalate if a task remains unchanged across multiple checks

## Notification standard
When something finishes, report:
- what finished
- whether it passed or failed
- what changed
- whether any follow-up remains

Keep the notification short and direct.

## Blocker handling
If work is blocked, always state:
- blocker
- why it matters
- best workaround
- exact next check or next action

## Good handoff pattern
Use this structure when tracking a pending item:
- **Task:** what is being watched
- **Owner:** who or what is responsible
- **State:** pending / blocked / finished
- **Next check:** timestamp or interval
- **Notify on:** completion, failure, or blocker change

## Completion rule
A task is not done until:
- it has been checked
- the outcome is known
- Mohamed has been told what happened

## Memory rule
Log meaningful pending-work transitions:
- task started
- task still pending after checks
- task completed
- blocker discovered
- blocker resolved

## Status labels
When reporting pending work, use these labels when relevant:
- PLANNING
- EXECUTING
- WAITING
- BLOCKED
- REVIEWING
- COMPLETE

If a watched task reaches COMPLETE, report:
- Result
- Why this is complete
- Best next action
