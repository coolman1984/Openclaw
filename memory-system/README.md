# Memory System v3

This is the modular v3 memory system for OpenClaw.

## What it does
- keeps structured memory for days, projects, decisions, blockers, and tasks
- generates MEMORY.md and supporting views
- supports search, reports, sync, backup, validation, and auto-extraction
- keeps Markdown human-readable while using SQLite for querying
- adds a health check and automated maintenance path

## Main entry point

Use the v3 wrapper:

```bash
python3 memory-v3.py --help
```

## Quick start

```bash
# Initialize the workspace
python3 memory-v3.py init

# Generate the dashboard
python3 memory-v3.py dashboard

# Add a daily entry
python3 memory-v3.py entry add

# Search memory
python3 memory-v3.py search "authentication" --advanced

# Validate integrity
python3 memory-v3.py validate

# Show health report
python3 memory-v3.py health

# Create a backup snapshot
python3 memory-v3.py backup create

# Run maintenance + optional git push
python3 memory-v3.py maintain --push --include-code
```

## Core commands

### Entries
- `entry add` — interactive daily log
- `entry list` — list entries with filters

### Search
- `search` — search across entries, tasks, decisions, blockers

### Reports
- `report daily`
- `report weekly`
- `report project`
- `report blockers`
- `report decisions`

### Sync and integrity
- `sync full`
- `sync verify`
- `sync fix`
- `sync escalate`
- `validate`
- `health`

### Backups
- `backup create`
- `backup list`
- `backup restore`
- `maintain --push` — backup + optional git commit/push

### Auto-extraction
- `parse --text ...`
- `parse --file ...`
- `parse --preview`
- `pending`
- `approve <parse_id>`

## V3 improvements

- schema-first workflow
- better validation
- draft/review/commit pipeline support
- backup snapshots
- integrity checks
- health reporting
- auto-extracted memory candidates with stricter approval gating
- cleaner modular layout

## Daily automation

You can run the maintenance script from cron:

```bash
# Example: every day at 9:00
0 9 * * * /root/.openclaw/workspace/memory-system/memory-maintenance.sh --push >> /root/.openclaw/workspace/memory-system/backups/maintenance.log 2>&1
```

This will:
- validate the memory system
- create a snapshot backup
- commit/push changes when there are updates

## Legacy note

The older monolithic `memory-manager.py` remains in the folder, but the v3 wrapper is the preferred path forward.
