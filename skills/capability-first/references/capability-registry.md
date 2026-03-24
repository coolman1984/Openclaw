# Capability Registry

This registry is the first place to check before doing fresh reasoning.

_Generated: 2026-03-24T08:55:01_

## Skills

### `capability-first`
Silent pre-task routing for OpenClaw. Use when deciding how to handle any request by checking existing skills, tools, reusable workflows, or delegated execution before doing fresh reasoning. This skill prevents duplicated work, wasted tokens, and rebuilding known workflows from scratch.

### `orchestration-ceo`
Top-level orchestration for Mohamed’s AI system. Use when a request needs strategy, multi-step planning, delegation to sub-agents or tools, review/testing, long-running task control, heartbeat follow-up, or building reusable operating procedures and automation.

### `task-watch`
Pending-work monitoring and completion follow-up for long-running tasks, sub-agents, reviews, tests, and background jobs. Use when you need recurring status checks, 2-minute wakeups, completion notifications, blocker tracking, or a clean handoff from waiting to done.

## Tools and workflows

### Core runtime tools
- `read`
- `write`
- `edit`
- `exec`
- `process`
- `web_search`
- `web_fetch`
- `memory_search`
- `memory_get`
- `sessions_spawn`
- `sessions_yield`
- `sessions_list`
- `sessions_history`
- `sessions_send`
- `subagents`
- `session_status`

### Orchestration helpers
- `multi_tool_use.parallel`
- `skill-creator`
- `capability-first`
- `orchestration-ceo`
- `task-watch`

## Routing rule of thumb

If a skill already matches the task, use the skill before inventing a new solution.
If a tool already finishes the job, use the tool before writing new code.
If the workflow repeats, convert it into a skill or automation.

## Maintenance rule

Whenever a new skill or tool is created or discovered, rerun this generator and refresh the registry.
