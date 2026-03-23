# Memory System Implementation - Quick Reference

**For:** Developer Agent (GLM-5)  
**From:** Architect Agent (Kimi K2.5)  
**Date:** 2026-03-23

---

## Priority 1: Core File Structure

Create these directories in `/root/.openclaw/workspace/memory/`:

```
memory/
├── daily/              # Daily log files (YYYY-MM-DD.md)
├── projects/           # Project-specific folders
│   └── {project-name}/
│       ├── index.md
│       ├── decisions.md
│       └── timeline.md
├── index/              # JSON index files
│   ├── projects.json
│   ├── tasks.json
│   ├── blockers.json
│   ├── tags.json
│   └── references.json
├── templates/          # Markdown templates
│   ├── daily.md.tpl
│   ├── entry.md.tpl
│   ├── blocker.md.tpl
│   └── decision.md.tpl
├── search/             # Search indexes
│   ├── inverted-index.json
│   └── entries-meta.json
└── reminders/          # Reminder tracking
    ├── pending.json
    └── completed.json
```

---

## Priority 2: Entry Format (YAML Frontmatter)

Every entry MUST have this format:

```markdown
---
id: "entry-YYYYMMDD-NNN"      # Auto-generated
type: "entry"                  # entry, task, blocker, decision, note
date: "2026-03-23"
time: "15:30:00"
timestamp: "2026-03-23T15:30:00+02:00"
project: "Project Name"
project_id: "proj-kebab-case"  # Normalized project ID
title: "Entry Title"
summary: "Brief description"
status: "active"               # active, complete, blocked, cancelled
priority: "medium"             # critical, high, medium, low
tags:
  - "tag1"
  - "tag2"
references:
  - id: "entry-YYYYMMDD-NNN"
    type: "related"            # related, blocks, blocked-by, decision
    title: "Reference Title"
tasks:
  - id: "task-YYYYMMDD-NNN"
    description: "Task desc"
    status: "pending"          # pending, in-progress, complete
blockers:
  - "blocker-YYYYMMDD-NNN"
---

**Summary:** 
[Content]

**Decisions:**
- 

**Tasks:**
- [ ] 

**Blockers:**

**Next Steps:**

**References:**
```

---

## Priority 3: CLI Commands to Implement

Create `memory` CLI tool with these commands:

### Essential (MVP)

```bash
# Daily operations
memory init-day                    # Create today's log from template
memory log                         # Interactive entry creation
memory log --quick "Summary"       # Quick entry mode

# Entry management
memory entry create --project "X" --title "Y"
memory entry show <entry-id>

# Task management
memory task add "Description" --project "X" --due 2026-03-25
memory task list --status pending
memory task complete <task-id>

# Blocker tracking
memory blocker add "Description" --severity high --project "X"
memory blocker resolve <blocker-id>

# Search
memory search "query"

# Dashboard
memory dashboard                   # Regenerate MEMORY.md
```

### Secondary (Post-MVP)

```bash
memory entry edit <entry-id>
memory entry list --project "X"
memory task block <task-id> --blocker-id <id>
memory reminder add "Message" --date "2026-03-25T10:00"
memory reminder check
memory timeline
memory stats
```

---

## Priority 4: Index Files (JSON Structure)

### projects.json
```json
{
  "version": "1.0",
  "last_updated": "2026-03-23T17:00:00+02:00",
  "projects": {
    "proj-opencode-setup": {
      "id": "proj-opencode-setup",
      "name": "OpenCode Setup",
      "display_name": "OpenCode CLI Setup",
      "status": "in-progress",
      "priority": "high",
      "created": "2026-03-23T15:00:00+02:00",
      "updated": "2026-03-23T17:00:00+02:00",
      "path": "projects/opencode-setup/",
      "tags": ["cli-tools"],
      "active_blockers": 1,
      "pending_tasks": 3,
      "completed_tasks": 2
    }
  },
  "stats": {
    "total_projects": 1,
    "active_projects": 1
  }
}
```

### tasks.json
```json
{
  "version": "1.0",
  "last_updated": "2026-03-23T17:00:00+02:00",
  "tasks": {
    "task-20260323-001": {
      "id": "task-20260323-001",
      "title": "Configure API keys",
      "status": "pending",
      "priority": "high",
      "project": "OpenCode Setup",
      "project_id": "proj-opencode-setup",
      "due_date": "2026-03-24",
      "entry_id": "entry-20260323-001",
      "created": "2026-03-23T15:30:00+02:00",
      "updated": "2026-03-23T15:30:00+02:00"
    }
  },
  "by_status": {
    "pending": ["task-20260323-001"],
    "in-progress": [],
    "complete": [],
    "blocked": []
  },
  "by_project": {
    "proj-opencode-setup": ["task-20260323-001"]
  },
  "overdue": [],
  "due_today": []
}
```

### blockers.json
```json
{
  "version": "1.0",
  "last_updated": "2026-03-23T17:00:00+02:00",
  "blockers": {
    "blocker-20260323-001": {
      "id": "blocker-20260323-001",
      "title": "ripgrep Installation Failed",
      "project": "OpenCode Setup",
      "project_id": "proj-opencode-setup",
      "severity": "medium",
      "impact": "OpenCode will use slower grep",
      "workaround": "Use built-in grep",
      "status": "active",
      "created": "2026-03-23T15:45:00+02:00",
      "updated": "2026-03-23T15:45:00+02:00",
      "related_entries": ["entry-20260323-003"]
    }
  }
}
```

---

## Priority 5: Automation Scripts

### init-daily.sh
```bash
#!/bin/bash
MEMORY_DIR="${MEMORY_DIR:-/root/.openclaw/workspace/memory}"
DATE=$(date +%Y-%m-%d)
OUTPUT="$MEMORY_DIR/daily/$DATE.md"

if [ -f "$OUTPUT" ]; then exit 0; fi

# Get active items from index
ACTIVE_BLOCKERS=$(jq -r '.blockers | to_entries[] | select(.value.status == "active") | "- \(.value.title) (\(.key))"' "$MEMORY_DIR/index/blockers.json" 2>/dev/null || echo "None")
PENDING_TASKS=$(jq -r '.tasks | to_entries[] | select(.value.status == "pending" or .value.status == "in-progress") | "- \(.value.title) (\(.key))"' "$MEMORY_DIR/index/tasks.json" 2>/dev/null || echo "None")

# Generate daily log from template
cat > "$OUTPUT" << EOF
---
date: "$DATE"
type: "daily-log"
generated: "$(date -Iseconds)"
---

# Daily Log - $DATE

## Today's Focus
<!-- What are the main goals for today? -->

## Active Context

### Carried Forward Blockers
$ACTIVE_BLOCKERS

### Pending Tasks
$PENDING_TASKS

## Entries

<!-- Entries will be added here -->

---

## Summary

**Key Artifacts:**
- 

**Environment Notes:**
- 
EOF

echo "Created daily log: $OUTPUT"
```

### update-index.sh
```bash
#!/bin/bash
MEMORY_DIR="${MEMORY_DIR:-/root/.openclaw/workspace/memory}"
python3 "$MEMORY_DIR/scripts/indexer.py" --update-all
```

### generate-dashboard.sh
```bash
#!/bin/bash
MEMORY_DIR="${MEMORY_DIR:-/root/.openclaw/workspace/memory}"
python3 "$MEMORY_DIR/scripts/dashboard.py" --generate
```

### check-reminders.sh
```bash
#!/bin/bash
MEMORY_DIR="${MEMORY_DIR:-/root/.openclaw/workspace/memory}"
NOW=$(date -Iseconds)
jq -r --arg now "$NOW" '.reminders | to_entries[] | select(.value.date <= $now and .value.status == "pending") | "REMINDER: \(.value.message)"' "$MEMORY_DIR/reminders/pending.json" 2>/dev/null
```

---

## Priority 6: Cron Setup

Add to crontab:

```bash
# Daily log creation at 00:01
1 0 * * * /root/.openclaw/workspace/memory/scripts/init-daily.sh

# Reminder check every 15 minutes
*/15 * * * * /root/.openclaw/workspace/memory/scripts/check-reminders.sh

# Dashboard regeneration every hour
0 * * * * /root/.openclaw/workspace/memory/scripts/generate-dashboard.sh

# Index update daily at 02:00
0 2 * * * /root/.openclaw/workspace/memory/scripts/update-index.sh
```

---

## Priority 7: Python Module Structure

```
/root/.openclaw/workspace/memory/scripts/
├── memory/
│   ├── __init__.py
│   ├── cli.py              # Click/Typer interface
│   ├── models.py           # Pydantic models
│   ├── storage.py          # File I/O
│   ├── indexer.py          # Index management
│   ├── search.py           # Search engine
│   ├── dashboards.py       # Dashboard generation
│   ├── reminders.py        # Reminder system
│   └── config.py           # Configuration
├── memory-cli.py           # Entry point: memory
└── indexer.py              # Standalone indexer
```

---

## Priority 8: Core Pydantic Models

```python
# models.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Literal
from enum import Enum

class EntryStatus(str, Enum):
    ACTIVE = "active"
    COMPLETE = "complete"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"

class Priority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Reference(BaseModel):
    id: str
    type: Literal["related", "blocks", "blocked-by", "decision", "supersedes"]
    title: str

class Task(BaseModel):
    id: str
    description: str
    status: Literal["pending", "in-progress", "complete"]

class Reminder(BaseModel):
    date: datetime
    message: str
    priority: Priority = Priority.MEDIUM
    type: Literal["one-time", "recurring", "follow-up"] = "one-time"

class Entry(BaseModel):
    id: str
    type: Literal["entry", "task", "blocker", "decision", "note"] = "entry"
    date: str
    time: str
    timestamp: datetime
    project: Optional[str] = None
    project_id: Optional[str] = None
    title: str
    summary: Optional[str] = None
    status: EntryStatus = EntryStatus.ACTIVE
    priority: Priority = Priority.MEDIUM
    tags: List[str] = []
    references: List[Reference] = []
    tasks: List[Task] = []
    blockers: List[str] = []
    reminders: List[Reminder] = []
```

---

## Implementation Order

1. **Phase 1 - Foundation:**
   - Create directory structure
   - Implement Entry model with YAML frontmatter
   - Create `memory log` command
   - Create daily log template

2. **Phase 2 - Storage:**
   - Implement storage.py for file I/O
   - Create `memory init-day` command
   - Migrate existing entries to new format

3. **Phase 3 - Indexing:**
   - Create index JSON structures
   - Implement indexer.py
   - Create `memory entry show` command

4. **Phase 4 - Tasks & Blockers:**
   - Implement `memory task` commands
   - Implement `memory blocker` commands
   - Update index on changes

5. **Phase 5 - Search:**
   - Implement basic search with ripgrep
   - Create `memory search` command
   - Build inverted index

6. **Phase 6 - Dashboard:**
   - Implement dashboard.py
   - Generate MEMORY.md
   - Create multiple views

7. **Phase 7 - Reminders:**
   - Implement reminder system
   - Add cron jobs
   - Test automation

---

## Testing Checklist

- [ ] `memory init-day` creates daily log with correct format
- [ ] `memory log` creates entry with valid YAML frontmatter
- [ ] `memory task add` adds task to index and daily log
- [ ] `memory blocker add` adds blocker to index
- [ ] `memory dashboard` regenerates MEMORY.md with current data
- [ ] `memory search` finds entries by keyword
- [ ] Indexes update after each entry creation
- [ ] Daily logs are created automatically via cron
- [ ] Reminders trigger at scheduled times

---

**Refer to the full architecture document for detailed specifications:**
`/root/.openclaw/workspace/memory-system-architecture.md`
