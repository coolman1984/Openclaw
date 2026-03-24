# Capability Registry

This registry is the first place to check before doing fresh reasoning.

## Existing skills

### `orchestration-ceo`
Top-level routing and control. Use for:
- strategy
- task decomposition
- delegation
- review and recovery
- multi-step orchestration
- building reusable operating procedures

### `task-watch`
Pending-work monitoring and follow-up. Use for:
- sub-agent waits
- tests still running
- reviews pending completion
- recurring checks every 2 minutes
- completion notifications

### `skill-creator`
Skill creation and improvement. Use for:
- creating new skills
- improving existing skills
- auditing skill folders
- restructuring skill resources

### `healthcheck`
Host security hardening and exposure review. Use for:
- security audits
- version status checks
- firewall/SSH/update hardening
- exposure review

### `node-connect`
Node pairing and connection troubleshooting. Use for:
- pairing failures
- bootstrap token issues
- unauthorized/invalid token errors
- tailscale or remote URL problems

### `weather`
Weather lookup. Use for:
- weather
- temperature
- forecast

## Existing workflows and tools

### Memory system
Use for:
- daily logs
- project continuity
- blockers and tasks
- search and retrieval
- health and maintenance

### Multi-agent coding system
Use for:
- planning with Kimi K2.5
- coding with GLM-5
- review/testing with MiniMax M2.7

### Direct tools
Use directly when the task is mechanical:
- read
- write
- edit
- exec
- web_search
- web_fetch
- memory_search
- memory_get

## Routing rule of thumb
If a skill already matches the task, use the skill before inventing a new solution.
If a tool already finishes the job, use the tool before writing new code.
If the workflow repeats, convert it into a skill or automation.
