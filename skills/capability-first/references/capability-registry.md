# Capability Registry

This registry is the first place to check before doing fresh reasoning.

_Generated: 2026-03-24T09:59:32_

## Skills

### `builder`
Execution specialist for implementation work. Use for coding, setup steps, configurations, scripts, technical fixes, and concrete build plans. Produces working output, flags risks clearly, and returns concise implementation packages.

### `capability-first`
Silent pre-task routing for OpenClaw. Use when deciding how to handle any request by checking existing skills, tools, reusable workflows, or delegated execution before doing fresh reasoning. This skill prevents duplicated work, wasted tokens, and rebuilding known workflows from scratch.

### `orchestration-ceo`
Top-level orchestration for Mohamed’s AI system. Use when a request needs strategy, multi-step planning, delegation to sub-agents or tools, review/testing, long-running task control, heartbeat follow-up, or building reusable operating procedures and automation.

### `researcher`
Evidence-oriented research specialist for gathering, comparing, analyzing, and synthesizing facts for decision-making. Use when the task is research, option comparison, tradeoff analysis, uncertainty handling, or decision support.

### `task-watch`
Pending-work monitoring and completion follow-up for long-running tasks, sub-agents, reviews, tests, and background jobs. Use when you need recurring status checks, 2-minute wakeups, completion notifications, blocker tracking, or a clean handoff from waiting to done.

## Tools and workflows

### Core runtime tools
- `read`
  - Read file contents from the workspace.
- `write`
  - Create or overwrite files in the workspace.
- `edit`
  - Make precise text replacements in existing files.
- `exec`
  - Run shell commands and scripts.
- `process`
  - Manage background exec sessions.
- `web_search`
  - Search the web using DuckDuckGo.
- `web_fetch`
  - Fetch and extract readable web content.
- `memory_search`
  - Search memory files and transcripts semantically.
- `memory_get`
  - Read targeted memory snippets safely.
- `sessions_spawn`
  - Spawn a sub-agent or ACP session.
- `sessions_yield`
  - Yield control while waiting for sub-agent results.
- `sessions_list`
  - List sessions and recent activity.
- `sessions_history`
  - Fetch session history.
- `sessions_send`
  - Send a message into another session.
- `subagents`
  - List, steer, or kill sub-agent runs.
- `session_status`
  - Show session status and usage card.

### Orchestration helpers
- `multi_tool_use.parallel`
  - Run multiple compatible tools in parallel.
- `skill-creator`
  - Create, improve, audit, and package AgentSkills.
- `orchestration-ceo`
  - Top-level routing and control skill.
- `task-watch`
  - Pending-work monitoring and completion follow-up.
- `capability-first`
  - Pre-task capability routing to reuse existing skills and tools first.
- `builder`
  - Implementation specialist for coding, setup, config, scripts, and fixes.
- `researcher`
  - Evidence-oriented research specialist for comparison and decision support.

### Workspace tools
- `dev-assistant.py`
  - Python CLI productivity dashboard.
- `multi-agent-coding.sh`
  - Multi-agent coding workflow shell script.
- `memory-manager.py`
  - Original monolithic memory manager CLI.
- `memory-v3.py`
  - Modular memory manager v3 entry point.
- `memory-maintenance.sh`
  - Daily memory maintenance helper.
- `memory-install-cron.sh`
  - Cron installer for memory maintenance and audits.
- `capability-first/scripts/update_registry.py`
  - Regenerate the capability registry from the current inventory.
- `capability-first/scripts/sync_capabilities.py`
  - Register new skills or tools and refresh the registry.

## Routing rule of thumb

If a skill already matches the task, use the skill before inventing a new solution.
If a tool already finishes the job, use the tool before writing new code.
If the workflow repeats, convert it into a skill or automation.

## Maintenance rule

Whenever a new skill or tool is created or discovered, rerun the sync script and refresh the registry.
