# Routing Playbook

## Default decision tree

### 1) Is the task simple and fully specified?
- Yes -> execute directly.
- No -> continue.

### 2) Does it require planning, sequencing, or tradeoffs?
- Yes -> strategy mode.

### 3) Does it need one specialist to own a domain subtask?
- Yes -> delegate.

### 4) Does it need inspection, testing, or bug-finding?
- Yes -> review mode.

### 5) Did it fail, drift, or stall?
- Yes -> recovery mode.

### 6) Is the user repeating a pattern?
- Yes -> build a reusable tool, checklist, or skill.

## Delegation package template

Provide sub-agents:
- task
- objective
- constraints
- success criteria
- forbidden actions
- output format
- deadline or checkpoint

## Checkpoint template
- What was attempted?
- What changed?
- What is blocked?
- What is the next check?

## When waiting
- Set a heartbeat.
- Re-check every 2 minutes for pending work.
- Notify immediately on completion.

## When done
- Verify output.
- Merge into one coherent answer.
- Update memory if it matters.

## Status labels
Use these exact labels in task updates:
- PLANNING
- EXECUTING
- WAITING
- BLOCKED
- REVIEWING
- COMPLETE

## Complete-task closure
When a task is COMPLETE, end with:
- Result
- Why this is complete
- Best next action
