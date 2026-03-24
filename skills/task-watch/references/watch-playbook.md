# Task Watch Playbook

## Default interval
- Re-check every 2 minutes while a task is pending.

## Escalation rule
Escalate if:
- the same state repeats across multiple checks without movement,
- a blocker appears,
- or the task exceeds the expected runtime.

## Notification format
When the task finishes:
- say it finished
- say whether it passed or failed
- mention any important result or blocker
- mention the next action if one remains

## If nothing changed
Do not send a fake completion.
Reply with a brief status update and set the next check.

## If a task is blocked
Report:
- blocker
- impact
- workaround
- next check

## When to stop watching
Stop only when one of these is true:
- task finished
- task failed and is handed back
- Mohamed asks to stop
- task is cancelled
