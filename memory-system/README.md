# 🧠 Memory Manager - Operational Memory System

A comprehensive CLI tool for tracking daily work, projects, decisions, and maintaining continuity across sessions.

## 🎯 Mission

Built as the **operational memory engine** for OpenClaw to:
- Preserve what happened and why it mattered
- Track tasks, decisions, and blockers
- Enable fast search and retrieval
- Maintain continuity across days and projects
- Surface overdue items and escalations

## ✨ Features

### Core Capabilities
- ✅ **Daily Entry Creation** - Structured logs with YAML frontmatter
- ✅ **Task Management** - Track tasks with priorities and owners
- ✅ **Decision Registry** - Document context and rationale
- ✅ **Blocker Tracking** - Auto-escalation after 24h/48h/72h
- ✅ **Full-Text Search** - SQLite FTS5 for fast queries
- ✅ **Dashboard Views** - Multiple perspectives on your work
- ✅ **Markdown Export** - Human-readable daily logs
- ✅ **Backup System** - Automated backup script

### Data Models
| Model | Fields |
|-------|--------|
| **Entry** | date, project, summary, context, tasks, decisions, blockers, next_steps, priority, status, participants, tags |
| **Task** | title, project, priority, status, owner, notes, created, completed_date |
| **Blocker** | title, description, severity, status, escalation_level, next_review |
| **Decision** | title, context, choice, rationale, impact, reversible |

## 🚀 Quick Start

### 1. Initialize System
```bash
cd ~/.openclaw/workspace/memory-system
python3 memory-manager.py init
```

This creates:
- `~/.openclaw/memory/` - Main directory
- `~/.openclaw/memory/data/memory.db` - SQLite database
- `~/.openclaw/memory/daily/` - Markdown daily logs
- `~/.openclaw/memory/projects/` - Project-specific memory

### 2. Add Your First Entry
```bash
python3 memory-manager.py entry add
```

Interactive prompts for:
- Summary and context
- Tasks (with priorities)
- Blockers (with severity)
- Decisions (with rationale)
- Next steps

### 3. View Dashboard
```bash
python3 memory-manager.py dashboard
```

Shows:
- Active projects count
- Pending tasks
- Active blockers (with escalation alerts)
- Recent decisions
- Completion stats

### 4. Search Everything
```bash
python3 memory-manager.py search "authentication"
python3 memory-manager.py search "blocker" --limit 10
```

## 📋 Commands

### Entry Management
```bash
# Add new entry (interactive)
python3 memory-manager.py entry add

# Search entries
python3 memory-manager.py search "query" [--limit N]
```

### Task Management
```bash
# List active tasks
python3 memory-manager.py task list [--project NAME]

# Mark task complete
python3 memory-manager.py task complete ID
```

### Blocker Management
```bash
# List active blockers
python3 memory-manager.py blocker list [--project NAME]

# Resolve blocker
python3 memory-manager.py blocker resolve ID
```

### Dashboard & Reports
```bash
# Show dashboard
python3 memory-manager.py dashboard

# Generate daily report
python3 memory-manager.py report daily

# Generate project report
python3 memory-manager.py report project --name myproject
```

### Backup
```bash
# Create backup
./memory-backup.sh

# Or manually
cd ~/.openclaw
tar -czf memory_backup_$(date +%Y%m%d).tar.gz memory/
```

## 🏗️ System Architecture

### Storage Layer
- **SQLite** (`memory.db`) - Fast queries, FTS5 search
- **Markdown** (`daily/*.md`) - Human-readable, versionable
- **JSON Indexes** - Cross-references, tags

### Directory Structure
```
~/.openclaw/memory/
├── data/
│   └── memory.db              # SQLite with FTS5
├── daily/
│   ├── 2026-03-23.md         # Daily log
│   └── 2026-03-24.md
├── projects/
│   ├── memory-system.md
│   └── opencode-go.md
├── index/
│   ├── projects.json
│   └── tags.json
└── reminders/
    └── overdue.json
```

### Database Schema

#### entries
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| date | TEXT | Entry date (YYYY-MM-DD) |
| project | TEXT | Project name |
| summary | TEXT | Brief description |
| context | TEXT | Why this matters |
| next_steps | TEXT | What comes next |
| status | TEXT | active/completed/archived |
| priority | TEXT | low/medium/high |
| participants | TEXT | JSON array |
| tags | TEXT | JSON array |
| refs | TEXT | JSON array |
| created | TEXT | ISO timestamp |
| modified | TEXT | ISO timestamp |

#### tasks, blockers, decisions
Linked to entries via `entry_id` foreign key.

### FTS5 Full-Text Search
Virtual table `entries_fts` indexes:
- summary
- context
- next_steps

Triggers keep index synchronized with entries table.

## 🔒 Data Integrity

### Validation
- Required fields: date, project, summary, status
- Priority levels: low, medium, high
- Status values: pending, in_progress, completed, blocked

### Backup Strategy
1. **Local backups** - Daily tar.gz archives
2. **Git sync** - Version controlled Markdown
3. **Auto-cleanup** - Keep last 10 backups only

### Recovery
```bash
# Restore from backup
cd ~/.openclaw
tar -xzf memory-backups/memory_backup_YYYYMMDD.tar.gz
```

## 🔄 Workflow

### Daily Workflow
1. **Morning**: Check dashboard for overdue items
2. **During work**: Add entries as needed
3. **Evening**: Run backup, review next steps

### Entry Triggers
Create an entry when:
- Starting a new task (>15 min)
- Making a decision
- Encountering a blocker
- Completing significant work
- Switching contexts

### Weekly Review
```bash
# Generate weekly report
python3 memory-manager.py report weekly

# Check for stale blockers
python3 memory-manager.py blocker list

# Review completed tasks
python3 memory-manager.py task list --status completed
```

## 🎨 Entry Format

### Markdown Daily Log
```markdown
---
id: 42
date: 2026-03-23
project: memory-system
status: active
priority: high
participants: ["Mohamed", "OpenClaw"]
tags: ["infrastructure", "cli"]
created: 2026-03-23T10:00:00
modified: 2026-03-23T10:00:00
---

# Built comprehensive memory system

## Context
User requested detailed memory tracking across sessions

## Tasks
- [✓] **HIGH** Design architecture
- [✓] **HIGH** Implement CLI
- [○] **MEDIUM** Write tests

## Decisions
- **Storage format** (Reversible)
  - Choice: SQLite + Markdown
  - Rationale: Fast queries + human readable

## Blockers
- None

## Next Steps
Initialize git backup, create cron reminders

## References
- memory-system-architecture.md
```

## 🚨 Blocker Escalation

Blockers auto-escalate based on age:
- **Level 0**: New blocker
- **Level 1**: > 24 hours (first escalation)
- **Level 2**: > 48 hours (second escalation)
- **Level 3**: > 72 hours (critical - requires immediate action)

Dashboard shows ⚠️ ESCALATED for blockers level > 0.

## 📊 Dashboard Views

### Overview
- Active projects
- Active/completed tasks
- Active blockers (with escalation count)
- Recent decisions (7 days)

### Task View
Grouped by status, sorted by priority:
```
[○] [H] High priority task
    Project: myproject
[○] [M] Medium priority task
    Project: other
```

### Blocker View
Sorted by severity and escalation:
```
#5 [H] Critical dependency issue ⚠️ ESCALATED
   Project: infrastructure
   
#3 [M] Waiting for API keys
   Project: integration
```

## 🔍 Search Syntax

SQLite FTS5 supports:
- **Simple**: `authentication`
- **AND**: `auth AND jwt`
- **OR**: `auth OR oauth`
- **NOT**: `auth NOT basic`
- **Phrase**: `"json web token"`
- **Prefix**: `auth*`

## 🛠️ Development

### Adding New Features
1. Update `models.py` with new data class
2. Add database migration in `init_tables()`
3. Create CLI command handler
4. Update dashboard/report generators

### Testing
```bash
# Run demo data
python3 demo-data.py

# Test search
python3 memory-manager.py search "test"

# Verify database
sqlite3 ~/.openclaw/memory/data/memory.db ".schema"
```

## 📝 Best Practices

### Entry Quality
- ✅ Clear, specific summaries
- ✅ Context explaining "why"
- ✅ Actionable next steps
- ✅ Relevant references
- ✅ Appropriate priority

### Task Management
- One owner per task
- Clear completion criteria
- Regular status updates
- Archive completed items

### Decision Documentation
- Always include context
- Document alternatives considered
- Note if reversible
- Explain expected impact

### Blocker Resolution
- Clear description of issue
- Severity assessment
- Next review date
- Escalation path

## 🎓 Example Session

```bash
# Initialize
python3 memory-manager.py init

# Add entry about current work
python3 memory-manager.py entry add
# Summary: Implementing user authentication
# Project: webapp
# Context: Security requirement for production
# Tasks: Setup JWT library, Create auth middleware, Write tests
# Priority: high

# Check dashboard
python3 memory-manager.py dashboard

# Search for auth-related entries
python3 memory-manager.py search "authentication"

# Complete a task
python3 memory-manager.py task complete 1

# Add a blocker
python3 memory-manager.py entry add
# Summary: Blocked on API rate limits
# Blocker: Need enterprise API key | high

# Check blockers
python3 memory-manager.py blocker list

# Resolve when unblocked
python3 memory-manager.py blocker resolve 1

# Backup
./memory-backup.sh
```

## 🔮 Future Enhancements

### Planned
- [ ] Web dashboard (Flask/FastAPI)
- [ ] Telegram bot integration
- [ ] Time tracking integration
- [ ] Automated report generation
- [ ] GitHub Issues sync

### Ideas
- [ ] Voice entry creation
- [ ] Screenshot attachments
- [ ] Calendar integration
- [ ] Team collaboration features
- [ ] AI-powered summarization

## 📞 Support

For issues or questions:
1. Check `memory-manager.py --help`
2. Review this README
3. Search existing entries: `python3 memory-manager.py search "issue"`

## 📄 License

Created by OpenClaw for Mohamed Fawzy
Part of the OpenClaw operational memory system

---

**Version**: 1.0.0  
**Created**: 2026-03-23  
**Last Updated**: 2026-03-23