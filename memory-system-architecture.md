# Operational Memory Management System - Architecture Design

**Version:** 1.0  
**Date:** 2026-03-23  
**Status:** Architecture Complete - Ready for Implementation

---

## 1. Executive Summary

This document defines a comprehensive operational memory management system for an AI assistant. The system evolves from basic daily logs to a fully automated, searchable, and interconnected memory infrastructure that maintains context, tracks progress, and proactively surfaces relevant information.

### Key Improvements Over Current State
- **Automated daily log creation** with template generation
- **Structured YAML frontmatter** for machine-readable metadata
- **Multiple dashboard views** (daily, project, task, blocker, timeline)
- **Full-text search with indexing** via ripgrep/embedded search
- **Automated cross-referencing** between related entries
- **Reminder system** for blockers and overdue items
- **Timeline visualization** with history tracking
- **Task management integration** with status synchronization

---

## 2. File Structure & Organization

```
memory/
├── MEMORY.md                    # Main dashboard (auto-generated)
├── index/                       # Index files for fast lookups
│   ├── projects.json           # Project registry with metadata
│   ├── tasks.json              # Task index with status tracking
│   ├── blockers.json           # Active blockers with reminders
│   ├── tags.json               # Tag cloud and usage stats
│   └── references.json         # Cross-reference map
├── daily/                       # Daily log entries
│   ├── 2026-03-23.md
│   ├── 2026-03-24.md
│   └── ...
├── projects/                    # Project-specific memory
│   ├── opencode-setup/
│   │   ├── index.md            # Project overview
│   │   ├── decisions.md        # Decision log
│   │   └── timeline.md         # Project timeline
│   └── ...
├── templates/                   # Entry templates
│   ├── daily.md.tpl            # Daily log template
│   ├── entry.md.tpl            # Standard entry template
│   ├── blocker.md.tpl          # Blocker entry template
│   └── decision.md.tpl         # Decision record template
├── search/                      # Search index (auto-generated)
│   ├── inverted-index.json     # Word → entry mapping
│   └── entries-meta.json       # Entry metadata cache
└── reminders/                   # Reminder tracking
    ├── pending.json            # Pending reminders
    └── completed.json          # Completed reminders archive
```

### Naming Conventions

| Component | Format | Example |
|-----------|--------|---------|
| Daily logs | `YYYY-MM-DD.md` | `2026-03-23.md` |
| Project directories | `kebab-case/` | `opencode-setup/` |
| Entry IDs | `entry-YYYYMMDD-NNN` | `entry-20260323-001` |
| Task IDs | `task-YYYYMMDD-NNN` | `task-20260323-005` |
| Blocker IDs | `blocker-YYYYMMDD-NNN` | `blocker-20260323-002` |
| Decision IDs | `dec-YYYYMMDD-NNN` | `dec-20260323-001` |

---

## 3. Data Schemas

### 3.1 Entry Schema (YAML Frontmatter)

Every entry in the system uses YAML frontmatter for structured metadata:

```yaml
---
id: "entry-20260323-001"
type: "entry"              # entry, task, blocker, decision, note
date: "2026-03-23"
time: "15:30:00"
timestamp: "2026-03-23T15:30:00+02:00"
project: "OpenCode Setup"
project_id: "proj-opencode-setup"
title: "Initial Installation"
summary: "Installed OpenCode CLI from official repository"
status: "complete"         # active, complete, blocked, cancelled
priority: "high"           # critical, high, medium, low
tags:
  - "installation"
  - "cli-tools"
  - "opencode"
references:
  - id: "entry-20260323-002"
    type: "related"
    title: "Dependency Installation"
  - id: "dec-20260323-001"
    type: "decision"
    title: "Choose OpenCode over Crush"
  - id: "blocker-20260323-001"
    type: "blocks"
    title: "ripgrep Installation Blocked"
tasks:
  - id: "task-20260323-001"
    description: "Download install script"
    status: "complete"
  - id: "task-20260323-002"
    description: "Configure API keys"
    status: "pending"
blockers: []
reminders:
  - date: "2026-03-24T10:00:00"
    message: "Follow up on API key configuration"
    priority: "medium"
---
```

### 3.2 Task Schema

```yaml
---
id: "task-20260323-005"
type: "task"
created: "2026-03-23T15:30:00+02:00"
updated: "2026-03-23T16:00:00+02:00"
project: "OpenCode Setup"
project_id: "proj-opencode-setup"
title: "Configure OpenCode with API keys"
description: "Set up OpenCode CLI with OpenCode Go API credentials"
status: "pending"          # pending, in-progress, complete, blocked
priority: "high"
due_date: "2026-03-24"
assignee: "self"
tags:
  - "configuration"
  - "api-keys"
parent: "entry-20260323-001"
subtasks:
  - id: "subtask-001"
    description: "Create ~/.opencode.json"
    status: "complete"
  - id: "subtask-002"
    description: "Add Go provider configuration"
    status: "pending"
history:
  - timestamp: "2026-03-23T15:30:00+02:00"
    action: "created"
    note: "Identified as next step"
  - timestamp: "2026-03-23T16:00:00+02:00"
    action: "updated"
    note: "Subtask 1 completed"
---
```

### 3.3 Blocker Schema

```yaml
---
id: "blocker-20260323-001"
type: "blocker"
created: "2026-03-23T15:45:00+02:00"
updated: "2026-03-23T15:45:00+02:00"
project: "OpenCode Setup"
project_id: "proj-opencode-setup"
title: "ripgrep Installation Failed"
description: "Unable to install ripgrep due to SSL certificate and architecture issues in Termux proot environment"
severity: "medium"         # critical, high, medium, low
impact: "OpenCode will use slower grep for searches"
workaround: "Use built-in grep or install via pkg in non-root Termux shell"
status: "active"           # active, resolved, mitigated, escalated
due_date: null
assigned_to: null
related_entries:
  - "entry-20260323-003"
  - "entry-20260323-002"
reminders:
  - date: "2026-03-30"
    message: "Revisit ripgrep installation after 1 week"
    type: "follow-up"
resolution:
  date: null
  solution: null
  verified_by: null
---
```

### 3.4 Decision Record Schema

```yaml
---
id: "dec-20260323-001"
type: "decision"
date: "2026-03-23T15:20:00+02:00"
project: "OpenCode Setup"
project_id: "proj-opencode-setup"
title: "Choose OpenCode over Crush"
context: "Need AI coding assistant CLI tool. Discovered OpenCode was renamed to Crush by Charm team."
decision: "Install original OpenCode (v0.0.55) instead of Crush"
status: "accepted"          # proposed, accepted, rejected, superseded
consequences:
  positive:
    - "Familiar interface and documentation"
    - "Proven stability"
  negative:
    - "Archived project - no future updates"
    - "May need migration to Crush later"
  neutral:
    - "Current functionality meets needs"
alternatives_considered:
  - option: "Crush (renamed OpenCode)"
    outcome: "rejected"
    reason: "Newer but less documented, potential breaking changes"
  - option: "Continue with manual tools"
    outcome: "rejected"
    reason: "Would lose AI assistance benefits"
supersedes: null
superseded_by: null
stakeholders:
  - "Mohamed Fawzy"
  - "OpenClaw (AI Assistant)"
---
```

### 3.5 Project Registry Schema (index/projects.json)

```json
{
  "version": "1.0",
  "last_updated": "2026-03-23T17:00:00+02:00",
  "projects": {
    "proj-opencode-setup": {
      "id": "proj-opencode-setup",
      "name": "OpenCode Setup",
      "display_name": "OpenCode CLI Setup",
      "description": "Installation and configuration of OpenCode AI coding assistant",
      "status": "in-progress",
      "priority": "high",
      "created": "2026-03-23T15:00:00+02:00",
      "updated": "2026-03-23T17:00:00+02:00",
      "path": "projects/opencode-setup/",
      "tags": ["cli-tools", "ai", "development"],
      "active_blockers": 1,
      "pending_tasks": 3,
      "completed_tasks": 2,
      "total_entries": 6,
      "first_entry": "entry-20260323-001",
      "last_entry": "entry-20260323-006"
    }
  },
  "stats": {
    "total_projects": 1,
    "active_projects": 1,
    "completed_projects": 0,
    "total_entries": 6
  }
}
```

### 3.6 Task Index Schema (index/tasks.json)

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
    "pending": ["task-20260323-001", "task-20260323-002"],
    "in-progress": [],
    "complete": ["task-20260323-003"],
    "blocked": ["task-20260323-004"]
  },
  "by_project": {
    "proj-opencode-setup": ["task-20260323-001", "task-20260323-002", "task-20260323-003"]
  },
  "overdue": [],
  "due_today": ["task-20260323-001"]
}
```

---

## 4. Automation Scripts

### 4.1 Daily Log Initialization (`scripts/init-daily.sh`)

**Trigger:** Daily at 00:01 via cron or manual invocation  
**Purpose:** Create new daily log with template and carry forward active items

```bash
#!/bin/bash
# init-daily.sh - Initialize daily log for current date

MEMORY_DIR="${MEMORY_DIR:-/root/.openclaw/workspace/memory}"
DATE=$(date +%Y-%m-%d)
TEMPLATE="$MEMORY_DIR/templates/daily.md.tpl"
OUTPUT="$MEMORY_DIR/daily/$DATE.md"
INDEX="$MEMORY_DIR/index"

# Check if already exists
if [ -f "$OUTPUT" ]; then
    echo "Daily log for $DATE already exists"
    exit 0
fi

# Get active items from index
ACTIVE_BLOCKERS=$(jq -r '.blockers | to_entries[] | select(.value.status == "active") | "- \\(.value.title) (ID: \\(.key))"' "$INDEX/blockers.json" 2>/dev/null || echo "")
PENDING_TASKS=$(jq -r '.tasks | to_entries[] | select(.value.status == "pending" or .value.status == "in-progress") | "- \\(.value.title) (ID: \\(.key))"' "$INDEX/tasks.json" 2>/dev/null || echo "")

# Generate daily log
cat > "$OUTPUT" << EOF
---
date: "$DATE"
type: "daily-log"
generated: "$(date -Iseconds)"
active_blockers: $(jq '[.blockers | to_entries[] | select(.value.status == "active") | .key]' "$INDEX/blockers.json" 2>/dev/null || echo "[]")
pending_tasks: $(jq '[.tasks | to_entries[] | select(.value.status == "pending" or .value.status == "in-progress") | .key]' "$INDEX/tasks.json" 2>/dev/null || echo "[]")
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

### Entry 1: [Title]
- **Project:** [Project Name]
- **Summary:** [Brief description]
- **Decisions:**
  - [Decision 1]
- **Tasks:**
  - [ ] Task 1
  - [ ] Task 2
- **Blockers:** None
- **Next Steps:** [What's next]

---

## Summary
<!-- End-of-day summary -->

**Key Artifacts:**
- 

**Environment Notes:**
- 
EOF

echo "Created daily log: $OUTPUT"
```

### 4.2 Entry Creation Helper (`scripts/create-entry.sh`)

**Trigger:** Manual or automated during interactions  
**Purpose:** Create standardized entries with proper ID generation

```bash
#!/bin/bash
# create-entry.sh - Create a new memory entry

MEMORY_DIR="${MEMORY_DIR:-/root/.openclaw/workspace/memory}"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M:%S)
DATETIME=$(date -Iseconds)

# Parse arguments
PROJECT=""
TITLE=""
TYPE="entry"
PRIORITY="medium"

while [[ $# -gt 0 ]]; do
    case $1 in
        --project) PROJECT="$2"; shift 2 ;;
        --title) TITLE="$2"; shift 2 ;;
        --type) TYPE="$2"; shift 2 ;;
        --priority) PRIORITY="$2"; shift 2 ;;
        *) shift ;;
    esac
done

# Generate ID
SEQ=$(ls "$MEMORY_DIR/daily/$DATE.md" 2>/dev/null | xargs grep -c "^### Entry" 2>/dev/null || echo "0")
SEQ=$(printf "%03d" $((SEQ + 1)))
ID="${TYPE:0:3}-${DATE//-}-$SEQ"
ENTRY_ID="entry-${DATE//-}-$SEQ"

# Output template
cat << EOF

### Entry $SEQ: $TITLE

---
id: "$ENTRY_ID"
type: "$type"
date: "$DATE"
time: "$TIME"
timestamp: "$DATETIME"
project: "$PROJECT"
title: "$TITLE"
status: "active"
priority: "$PRIORITY"
tags: []
references: []
tasks: []
blockers: []
---

**Summary:** 
<!-- Describe what happened -->

**Decisions:**
<!-- Record any decisions made -->

**Tasks:**
- [ ] 

**Blockers:**
<!-- None or list blockers -->

**Next Steps:**

**References:**

EOF
```

### 4.3 Index Updater (`scripts/update-index.sh`)

**Trigger:** After each entry creation/modification  
**Purpose:** Update all index files based on current memory state

```bash
#!/bin/bash
# update-index.sh - Update all memory indexes

MEMORY_DIR="${MEMORY_DIR:-/root/.openclaw/workspace/memory}"
INDEX_DIR="$MEMORY_DIR/index"

# Ensure index directory exists
mkdir -p "$INDEX_DIR"

# Update projects index
echo "Updating projects index..."
python3 "$MEMORY_DIR/scripts/indexer.py" --update-projects

# Update tasks index  
echo "Updating tasks index..."
python3 "$MEMORY_DIR/scripts/indexer.py" --update-tasks

# Update blockers index
echo "Updating blockers index..."
python3 "$MEMORY_DIR/scripts/indexer.py" --update-blockers

# Update tags index
echo "Updating tags index..."
python3 "$MEMORY_DIR/scripts/indexer.py" --update-tags

# Update references index
echo "Updating references index..."
python3 "$MEMORY_DIR/scripts/indexer.py" --update-references

# Rebuild search index
echo "Rebuilding search index..."
python3 "$MEMORY_DIR/scripts/search-indexer.py" --rebuild

echo "All indexes updated!"
```

### 4.4 Reminder Checker (`scripts/check-reminders.sh`)

**Trigger:** Every 15 minutes via cron  
**Purpose:** Check for due reminders and notify

```bash
#!/bin/bash
# check-reminders.sh - Check and process reminders

MEMORY_DIR="${MEMORY_DIR:-/root/.openclaw/workspace/memory}"
NOW=$(date -Iseconds)
TODAY=$(date +%Y-%m-%d)

# Check pending reminders
jq -r --arg now "$NOW" '
    .reminders | to_entries[] | 
    select(.value.date <= $now and .value.status == "pending") |
    "\(.key)|\(.value.message)|\(.value.type)|\(.value.priority)"
' "$MEMORY_DIR/reminders/pending.json" 2>/dev/null | while IFS='|' read -r ID MESSAGE TYPE PRIORITY; do
    
    echo "REMINDER: $MESSAGE (Priority: $PRIORITY)"
    
    # Update reminder status
    jq --arg id "$ID" --arg now "$NOW" '
        .reminders[$id].status = "triggered" |
        .reminders[$id].triggered_at = $now
    ' "$MEMORY_DIR/reminders/pending.json" > "$MEMORY_DIR/reminders/pending.json.tmp"
    mv "$MEMORY_DIR/reminders/pending.json.tmp" "$MEMORY_DIR/reminders/pending.json"
    
    # Archive if one-time reminder
    if [ "$TYPE" == "one-time" ]; then
        jq --arg id "$ID" '.reminders[$id]' "$MEMORY_DIR/reminders/pending.json" >> "$MEMORY_DIR/reminders/completed.json"
    fi
done

# Check overdue tasks
jq -r --arg today "$TODAY" '
    .tasks | to_entries[] |
    select(.value.due_date < $today and .value.status != "complete") |
    "OVERDUE: \(.value.title) (Due: \(.value.due_date))"
' "$MEMORY_DIR/index/tasks.json" 2>/dev/null | while read -r LINE; do
    echo "$LINE"
done
```

### 4.5 Dashboard Generator (`scripts/generate-dashboard.sh`)

**Trigger:** After index updates or on-demand  
**Purpose:** Generate MEMORY.md with current state

```bash
#!/bin/bash
# generate-dashboard.sh - Generate MEMORY.md dashboard

MEMORY_DIR="${MEMORY_DIR:-/root/.openclaw/workspace/memory}"
INDEX="$MEMORY_DIR/index"
OUTPUT="$MEMORY_DIR/MEMORY.md"
DATE=$(date +%Y-%m-%d)
DATETIME=$(date -Iseconds)

# Read indices
PROJECTS=$(cat "$INDEX/projects.json")
TASKS=$(cat "$INDEX/tasks.json")
BLOCKERS=$(cat "$INDEX/blockers.json")

# Generate dashboard
cat > "$OUTPUT" << 'HEADER'
# MEMORY.md - Operational Memory Dashboard

**Last Updated:** TIMESTAMP_PLACEHOLDER

---

HEADER

# Update timestamp
sed -i "s/TIMESTAMP_PLACEHOLDER/$DATETIME/" "$OUTPUT"

# Add Today's Summary section
cat >> "$OUTPUT" << 'SECTION'

## Today's Summary (DATE_PLACEHOLDER)

SECTION

# Get today's entries if daily log exists
if [ -f "$MEMORY_DIR/daily/DATE_PLACEHOLDER.md" ]; then
    grep -A 2 "^### Entry" "$MEMORY_DIR/daily/DATE_PLACEHOLDER.md" | head -20 >> "$OUTPUT"
fi

sed -i "s/DATE_PLACEHOLDER/$DATE/" "$OUTPUT"

# Add Active Projects section
cat >> "$OUTPUT" << 'SECTION'

## Active Projects

| Project | Status | Priority | Tasks (Done/Total) | Blockers | Last Updated |
|---------|--------|----------|-------------------|----------|--------------|
SECTION

jq -r '.projects | to_entries[] | 
    select(.value.status == "in-progress" or .value.status == "active") |
    "| \(.value.display_name) | \(.value.status) | \(.value.priority) | \(.value.completed_tasks)/\(.value.total_tasks) | \(.value.active_blockers) | \(.value.updated[:10]) |"
' "$INDEX/projects.json" >> "$OUTPUT"

# Add Pending Tasks section
cat >> "$OUTPUT" << 'SECTION'

## Pending Tasks

| Task | Project | Priority | Due Date | Status |
|------|---------|----------|----------|--------|
SECTION

jq -r '.tasks | to_entries[] | 
    select(.value.status == "pending" or .value.status == "in-progress") |
    "| \(.value.title) | \(.value.project) | \(.value.priority) | \(.value.due_date // "-") | \(.value.status) |"
' "$INDEX/tasks.json" | head -20 >> "$OUTPUT"

# Add Blockers section
cat >> "$OUTPUT" << 'SECTION'

## Current Blockers

| Blocker | Project | Severity | Workaround | Age |
|---------|---------|----------|------------|-----|
SECTION

jq -r '.blockers | to_entries[] | 
    select(.value.status == "active") |
    "| \(.value.title) | \(.value.project) | \(.value.severity) | \(.value.workaround // "None") | \((now - (.value.created | fromdateiso8601)) / 86400 | floor)d |"
' "$INDEX/blockers.json" >> "$OUTPUT"

# Add Quick Stats
cat >> "$OUTPUT" << 'SECTION'

## Quick Stats

SECTION

jq -r '"- **Active Projects:** \(.stats.active_projects)"' "$INDEX/projects.json" >> "$OUTPUT"
jq -r '"- **Pending Tasks:** \(.by_status.pending | length)"' "$INDEX/tasks.json" >> "$OUTPUT"
jq -r '"- **Active Blockers:** \([.blockers | to_entries[] | select(.value.status == "active")] | length)"' "$INDEX/blockers.json" >> "$OUTPUT"

echo "" >> "$OUTPUT"
echo "---" >> "$OUTPUT"
echo "" >> "$OUTPUT"
echo "_Use \`memory search <query>\` to find entries, \`memory log\` to add entries, \`memory dashboard\` to refresh this view._" >> "$OUTPUT"

echo "Dashboard regenerated: $OUTPUT"
```

---

## 5. Dashboard Generation System

### 5.1 Dashboard Views

The system generates multiple dashboard views:

#### Main Dashboard (MEMORY.md)
- Today's summary
- Active projects overview
- Pending tasks list
- Current blockers
- Quick statistics
- Quick actions

#### Project View (projects/{project}/index.md)
```markdown
# Project: {Project Name}

## Overview
[Description, goals, current status]

## Timeline
[Chronological list of entries]

## Active Tasks
[Task list with status]

## Decisions
[Decision log]

## Blockers
[Current and resolved blockers]
```

#### Task Board View (dashboards/task-board.md)
```markdown
# Task Board

## To Do
- [ ] Task 1
- [ ] Task 2

## In Progress
- [ ] Task 3

## Blocked
- [ ] Task 4 (blocked by #blocker-001)

## Complete
- [x] Task 5
```

#### Blocker Tracker (dashboards/blockers.md)
```markdown
# Blocker Tracker

## Critical (> 7 days)
[List old critical blockers]

## Recent (≤ 7 days)
[List newer blockers]

## Recently Resolved
[List resolved blockers from last 7 days]
```

#### Timeline View (dashboards/timeline.md)
```markdown
# Timeline

## 2026-03-23
- 15:30: Entry created (OpenCode Setup)
- 16:00: Decision recorded

## 2026-03-22
- ...
```

### 5.2 Dashboard Generation Flow

```
┌─────────────────┐
│  Index Update   │
│    Trigger      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Parse Daily    │
│     Logs        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Update JSON    │
│    Indexes      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│ Generate Main   │────▶│   MEMORY.md     │
│    Dashboard    │     │  (Primary View) │
└─────────────────┘     └─────────────────┘
         │
         ├─────────────────┬─────────────────┐
         ▼                 ▼                 ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  Project Views  │ │  Task Board     │ │ Blocker Tracker │
│  (Per Project)  │ │   (Kanban)      │ │  (Aging Report) │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

---

## 6. Search & Indexing Architecture

### 6.1 Search Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Search Query Input                        │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│  Full-Text      │    │  Structured     │
│  Search         │    │  Query (JSON)   │
│  (Keywords)     │    │  (Filters)      │
└────────┬────────┘    └────────┬────────┘
         │                       │
         └───────────┬───────────┘
                     ▼
┌─────────────────────────────────────┐
│       Search Processor              │
│  ┌─────────────────────────────┐    │
│  │  Inverted Index Lookup      │    │
│  │  (word → entry mappings)    │    │
│  └─────────────────────────────┘    │
│  ┌─────────────────────────────┐    │
│  │  Metadata Filtering         │    │
│  │  (date, project, status)    │    │
│  └─────────────────────────────┘    │
│  ┌─────────────────────────────┐    │
│  │  Relevance Scoring          │    │
│  │  (TF-IDF, recency, etc.)    │    │
│  └─────────────────────────────┘    │
└────────────────┬────────────────────┘
                 ▼
┌─────────────────────────────────────┐
│       Search Results                │
│  [Ranked list with snippets]        │
└─────────────────────────────────────┘
```

### 6.2 Inverted Index Structure

```json
{
  "version": "1.0",
  "last_updated": "2026-03-23T17:00:00+02:00",
  "index": {
    "opencode": {
      "df": 15,
      "entries": {
        "entry-20260323-001": {
          "tf": 5,
          "positions": [12, 45, 89, 134, 201],
          "fields": ["title", "content", "tags"]
        },
        "entry-20260323-002": {
          "tf": 3,
          "positions": [23, 67, 156],
          "fields": ["content"]
        }
      }
    },
    "installation": {
      "df": 8,
      "entries": {
        "entry-20260323-001": {
          "tf": 2,
          "positions": [34, 78],
          "fields": ["title", "content"]
        }
      }
    }
  },
  "metadata": {
    "total_entries": 50,
    "total_terms": 1200,
    "avg_entry_length": 350
  }
}
```

### 6.3 Search Implementation Approaches

#### Approach A: ripgrep-based (Simple, Fast)

```bash
# Search by keyword
rg -i "opencode" memory/daily/ --type md -C 2

# Search with context
rg -i "opencode" memory/daily/ -B 2 -A 5

# Search in specific date range
rg -i "opencode" memory/daily/2026-03-*.md
```

**Pros:** Fast, no additional dependencies, works with existing tools  
**Cons:** Limited ranking, no semantic search, basic filtering

#### Approach B: Python Indexer (Recommended)

```python
# search-indexer.py - Core search functionality

import json
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import math

class MemorySearch:
    def __init__(self, memory_dir):
        self.memory_dir = Path(memory_dir)
        self.index_path = self.memory_dir / "search" / "inverted-index.json"
        self.index = self._load_index()
    
    def _load_index(self):
        if self.index_path.exists():
            with open(self.index_path) as f:
                return json.load(f)
        return {"index": {}, "metadata": {}}
    
    def tokenize(self, text):
        """Simple tokenization - can be enhanced with stemming"""
        return re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    
    def build_index(self):
        """Rebuild inverted index from all entries"""
        index = defaultdict(lambda: {"df": 0, "entries": {}})
        
        for entry_file in (self.memory_dir / "daily").glob("*.md"):
            entry_id = entry_file.stem
            content = entry_file.read_text()
            
            # Extract frontmatter and body
            tokens = self.tokenize(content)
            token_counts = defaultdict(int)
            
            for token in tokens:
                token_counts[token] += 1
            
            for token, count in token_counts.items():
                index[token]["df"] += 1
                index[token]["entries"][entry_id] = {
                    "tf": count,
                    "positions": []  # Could track positions for phrase search
                }
        
        self.index = {
            "index": dict(index),
            "metadata": {
                "last_updated": datetime.now().isoformat(),
                "total_entries": len(list((self.memory_dir / "daily").glob("*.md")))
            }
        }
        
        self.index_path.parent.mkdir(exist_ok=True)
        with open(self.index_path, 'w') as f:
            json.dump(self.index, f, indent=2)
    
    def search(self, query, filters=None, limit=10):
        """Search with BM25-like scoring"""
        query_tokens = self.tokenize(query)
        scores = defaultdict(float)
        
        N = self.index["metadata"].get("total_entries", 1)
        avg_dl = 300  # Average document length (configurable)
        k1 = 1.5
        b = 0.75
        
        for token in query_tokens:
            if token not in self.index["index"]:
                continue
            
            posting = self.index["index"][token]
            df = posting["df"]
            idf = math.log((N - df + 0.5) / (df + 0.5) + 1)
            
            for entry_id, data in posting["entries"].items():
                tf = data["tf"]
                dl = 300  # Could track actual doc lengths
                
                # BM25 scoring
                score = idf * (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * (dl / avg_dl)))
                scores[entry_id] += score
        
        # Sort by score
        results = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:limit]
        return results
```

### 6.4 Search Query Syntax

```bash
# Basic keyword search
memory search "opencode installation"

# Search with filters
memory search "api keys" --project "OpenCode Setup"
memory search "blocker" --status active
memory search "decision" --date-after 2026-03-20

# Search in specific fields
memory search "title:opencode"
memory search "tag:cli-tools"

# Fuzzy search
memory search "opencode~"  # Matches opencode, opencode, etc.

# Boolean queries
memory search "opencode AND (installation OR setup)"
```

---

## 7. Tool Specifications for Developer

### 7.1 CLI Tool: `memory`

**Location:** `/root/.openclaw/workspace/scripts/memory.py`  
**Entry Point:** CLI wrapper script at `/usr/local/bin/memory`

#### Commands

```bash
# Daily operations
memory init-day                    # Create today's daily log
memory log                         # Add entry to today's log (interactive)
memory log --quick "Summary"       # Quick entry with minimal fields

# Entry management
memory entry create --project "X" --title "Y" --type decision
memory entry list --project "X" --status active
memory entry show <entry-id>
memory entry edit <entry-id>

# Task management
memory task add "Description" --project "X" --due 2026-03-25
memory task list --status pending
memory task complete <task-id>
memory task block <task-id> --blocker-id <blocker-id>

# Blocker tracking
memory blocker add "Description" --severity high --project "X"
memory blocker list --status active
memory blocker resolve <blocker-id> --solution "Fixed by..."

# Search
memory search "query"
memory search --project "X" --date-after 2026-03-20
memory search --tags "cli-tools,installation"

# Dashboards
memory dashboard                   # Regenerate all dashboards
memory dashboard --view projects   # Project overview only
memory dashboard --view tasks      # Task board only
memory dashboard --view blockers   # Blocker tracker only

# Reminders
memory reminder add "Message" --date 2026-03-25T10:00
memory reminder list
memory reminder check              # Check and display due reminders

# Index management
memory index rebuild               # Full index rebuild
memory index update                # Incremental update

# Utilities
memory timeline                    # Show chronological timeline
memory stats                       # Show memory statistics
memory export --format json        # Export to JSON
memory import --file backup.json   # Import from backup
```

### 7.2 Python Module Structure

```
scripts/
├── memory/
│   ├── __init__.py
│   ├── cli.py              # Click/Typer CLI interface
│   ├── models.py           # Pydantic models for entries
│   ├── storage.py          # File I/O operations
│   ├── indexer.py          # Index management
│   ├── search.py           # Search engine
│   ├── dashboards.py       # Dashboard generation
│   ├── reminders.py        # Reminder system
│   └── templates.py        # Template management
├── memory.py               # Main entry point
└── tests/                  # Unit tests
```

### 7.3 Core Models (Pydantic)

```python
# models.py

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict, Literal
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
    id: str = Field(..., description="Unique entry ID")
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
    
    def to_frontmatter(self) -> str:
        """Convert to YAML frontmatter"""
        import yaml
        data = self.model_dump(exclude_none=True)
        data['timestamp'] = data['timestamp'].isoformat()
        return f"---\n{yaml.dump(data, default_flow_style=False)}---\n"
    
    @classmethod
    def from_frontmatter(cls, text: str) -> "Entry":
        """Parse from YAML frontmatter"""
        import yaml
        if text.startswith("---"):
            _, frontmatter, content = text.split("---", 2)
            data = yaml.safe_load(frontmatter)
            return cls(**data)
        raise ValueError("No frontmatter found")
```

### 7.4 Configuration File

```yaml
# memory/config.yaml

paths:
  memory_dir: /root/.openclaw/workspace/memory
  daily_dir: daily
  projects_dir: projects
  index_dir: index
  templates_dir: templates
  search_dir: search

defaults:
  entry_priority: medium
  reminder_check_interval: 15  # minutes
  auto_create_daily: true
  auto_update_index: true

search:
  algorithm: bm25  # or simple, tfidf
  index_on_startup: true
  min_term_length: 3
  stopwords: ["the", "and", "or", "but", "in", "on", "at", "to", "for"]

dashboard:
  auto_generate: true
  sections:
    - today
    - active_projects
    - pending_tasks
    - current_blockers
    - quick_stats
  
reminders:
  enabled: true
  notification_command: null  # Custom command to run on reminder
  
templates:
  daily: templates/daily.md.tpl
  entry: templates/entry.md.tpl
  blocker: templates/blocker.md.tpl
  decision: templates/decision.md.tpl
```

---

## 8. Automation Triggers & Scheduling

### 8.1 Cron Schedule

```bash
# Memory System Automation Schedule

# Daily log creation at 00:01
1 0 * * * /root/.openclaw/workspace/memory/scripts/init-daily.sh

# Reminder check every 15 minutes
*/15 * * * * /root/.openclaw/workspace/memory/scripts/check-reminders.sh

# Dashboard regeneration every hour
0 * * * * /root/.openclaw/workspace/memory/scripts/generate-dashboard.sh

# Full index rebuild daily at 02:00
0 2 * * * /root/.openclaw/workspace/memory/scripts/update-index.sh

# Weekly cleanup/archival (Sundays at 03:00)
0 3 * * 0 /root/.openclaw/workspace/memory/scripts/weekly-cleanup.sh
```

### 8.2 Event-Based Triggers

| Event | Trigger | Action |
|-------|---------|--------|
| Entry created | `memory log` command | Update indexes, update dashboard |
| Task completed | `memory task complete` | Move to completed list, update stats |
| Blocker resolved | `memory blocker resolve` | Archive blocker, notify watchers |
| New project started | `memory project create` | Create project directory structure |
| Daily log accessed | File open | Check if exists, create if missing |

---

## 9. Integration Points

### 9.1 Task Management Integration

```python
# Integration with external task managers

class TaskManagerIntegration:
    """Sync with external task management systems"""
    
    def sync_to_todoist(self, task):
        """Push task to Todoist"""
        pass
    
    def sync_from_todoist(self):
        """Pull tasks from Todoist"""
        pass
    
    def sync_to_notion(self, entry):
        """Push entry to Notion database"""
        pass
```

### 9.2 Notification Integration

```python
# Notification system

class NotificationManager:
    def send_reminder(self, reminder):
        """Send reminder via available channels"""
        # Could integrate with:
        # - System notifications (notify-send)
        # - Telegram bot
        # - Email
        # - Slack
        pass
```

---

## 10. Migration Plan

### Phase 1: Foundation (Week 1)
1. Create new directory structure
2. Implement entry models and YAML frontmatter
3. Create basic CLI (`memory log`, `memory search`)
4. Set up daily log templates

### Phase 2: Indexing (Week 2)
1. Implement indexer.py
2. Build inverted index
3. Create index update automation
4. Migrate existing entries to new format

### Phase 3: Dashboards (Week 3)
1. Implement dashboard generators
2. Create multiple views (projects, tasks, blockers)
3. Auto-regeneration on changes
4. Migrate MEMORY.md to new format

### Phase 4: Reminders & Automation (Week 4)
1. Implement reminder system
2. Set up cron jobs
3. Create automation triggers
4. Test full workflow

---

## 11. Future Enhancements

1. **Semantic Search:** Use embeddings for concept-based search
2. **Graph View:** Visualize relationships between entries
3. **AI Summary:** Auto-generate daily/weekly summaries
4. **Voice Entry:** Speech-to-text for quick logging
5. **Mobile App:** Companion mobile interface
6. **Collaboration:** Multi-user memory sharing
7. **Analytics:** Productivity metrics and trends
8. **Backup/Restore:** Cloud sync capabilities

---

## Appendix A: File Templates

### A.1 Daily Log Template

```markdown
---
date: "{{DATE}}"
type: "daily-log"
generated: "{{TIMESTAMP}}"
active_blockers: {{BLOCKERS}}
pending_tasks: {{TASKS}}
---

# Daily Log - {{DATE}}

## Today's Focus
<!-- Main goals for today -->

## Active Context

### Carried Forward Blockers
{{BLOCKER_LIST}}

### Pending Tasks
{{TASK_LIST}}

## Entries

{{ENTRIES}}

---

## Summary

**Key Artifacts:**
- 

**Environment Notes:**
- 

**Mood/Energy:**
<!-- How did today feel? -->
```

### A.2 Entry Template

```markdown
---
id: "{{ENTRY_ID}}"
type: "entry"
date: "{{DATE}}"
time: "{{TIME}}"
timestamp: "{{TIMESTAMP}}"
project: "{{PROJECT}}"
title: "{{TITLE}}"
status: "active"
priority: "{{PRIORITY}}"
tags: []
references: []
tasks: []
blockers: []
---

**Summary:** 
<!-- What happened? -->

**Decisions:**
<!-- What was decided? -->

**Tasks:**
- [ ] 

**Blockers:**
<!-- None or list blockers -->

**Next Steps:**

**References:**
```

---

**End of Architecture Document**
