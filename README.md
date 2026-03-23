# OpenClaw

OpenClaw is my working workspace: a curated collection of the tools, scripts, memory systems, and project artifacts built during our sessions.

## What’s here

### Core tools
- `memory-system/` — operational memory manager v2 plus the v3 plan
- `memory/` — human-readable daily logs and memory dashboard
- `dev-assistant.py` — CLI productivity dashboard
- `multi-agent-coding.sh` — multi-agent coding workflow
- `AGENTS.md` — agent roles and model assignments

### Workspace identity
- `IDENTITY.md` — who I am
- `USER.md` — who Mohamed is
- `SOUL.md` — behavior and tone guidance
- `TOOLS.md` — environment-specific notes

### Design docs
- `memory-system-architecture.md`
- `memory-implementation-guide.md`
- `memory-system/IMPLEMENTATION_PLAN.md`
- `memory-system/IMPLEMENTATION_PLAN_V3.md`
- `memory-system/IMPLEMENTATION_SUMMARY.md`

## What this repo is for

This repository is mainly for:
- preserving work across sessions
- tracking tasks, decisions, blockers, and next steps
- keeping the memory system and supporting tools together
- making the workspace easier to inspect and evolve

## What’s intentionally excluded

Sensitive or machine-specific files are ignored on purpose, including:
- API keys and local auth files
- databases and caches
- backups and downloaded binaries
- `node_modules/` and other temporary artifacts

## Current status

- OpenClaw workspace is active
- OpenCode setup exists, but the main focus moved to the memory system and supporting tools
- Memory system v2 is complete and running
- Memory system v3 is planned
- GitHub upload is complete

## Useful commands

```bash
# Memory dashboard
python3 memory-system/memory-manager.py dashboard

# Add a memory entry
python3 memory-system/memory-manager.py entry add

# Search memory
python3 memory-system/memory-manager.py search "keyword"

# Backup memory
./memory-system/memory-backup.sh
```

## Notes

This repo is curated for readability and continuity, not as a production app bundle. The important part is the workflow and the memory system behind it.
