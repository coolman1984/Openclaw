# Memory Manager - Technical Implementation Plan

## Overview
A Python-based CLI tool for structured memory management with daily logs, task tracking, decision registry, and intelligent search capabilities.

---

## 1. Directory Structure

```
memory-system/
├── memory-manager.py          # Main CLI entry point
├── config.py                  # Configuration management
├── database.py                # SQLite database operations
├── models.py                  # Data models and schemas
├── parser.py                  # Conversation parsing logic
├── reports.py                 # Report generation
├── search.py                  # Search and indexing
├── utils.py                   # Utility functions
├── views.py                   # Dashboard view generators
├── integrations/
│   ├── __init__.py
│   ├── conversation_parser.py # Parse conversation context
│   ├── task_extractor.py      # Extract tasks from text
│   └── auto_entry.py          # Auto-generate entries
├── data/
│   ├── .memory.db             # SQLite database (hidden)
│   ├── entries/               # Daily entry JSON files
│   │   ├── 2026-03-23.json
│   │   └── ...
│   ├── projects/              # Project JSON files
│   │   ├── project-alpha.json
│   │   └── ...
│   ├── decisions/             # Decision registry JSON
│   │   └── decisions.json
│   └── logs/                  # Human-readable markdown logs
│       ├── 2026-03-23.md
│       └── ...
├── MEMORY.md                  # Main dashboard
├── reports/                   # Generated reports
│   ├── daily/
│   ├── weekly/
│   └── project/
└── tests/                     # Unit tests
    ├── test_models.py
    ├── test_parser.py
    └── test_database.py
```

---

## 2. Data Structures

### 2.1 Daily Entry Schema (JSON)

```json
{
  "id": "2026-03-23",
  "date": "2026-03-23",
  "timestamp_created": "2026-03-23T14:30:00Z",
  "timestamp_updated": "2026-03-23T18:45:00Z",
  "version": "1.0",
  
  "summary": {
    "title": "Working on Memory System",
    "description": "Started building the memory manager CLI tool",
    "mood": "focused",
    "energy_level": 8
  },
  
  "tasks": [
    {
      "id": "task_001",
      "title": "Design data structures",
      "description": "Create schemas for entries, tasks, and decisions",
      "status": "completed",
      "priority": "high",
      "project_id": "memory-system",
      "tags": ["design", "architecture"],
      "created_at": "2026-03-23T14:30:00Z",
      "completed_at": "2026-03-23T16:00:00Z",
      "estimated_hours": 2,
      "actual_hours": 1.5,
      "blockers": [],
      "related_entries": ["2026-03-22"]
    }
  ],
  
  "decisions": [
    {
      "id": "dec_001",
      "title": "Use SQLite for indexing",
      "context": "Need fast search across all entries",
      "decision": "Implement SQLite FTS for full-text search",
      "alternatives_considered": ["JSON only", "Elasticsearch"],
      "consequences": "Adds dependency but enables powerful search",
      "reversibility": "medium",
      "project_id": "memory-system",
      "created_at": "2026-03-23T15:00:00Z",
      "status": "active"
    }
  ],
  
  "blockers": [
    {
      "id": "blk_001",
      "title": "Need to decide on color library",
      "description": "Choosing between colorama, rich, and termcolor",
      "severity": "low",
      "impact": "minor",
      "project_id": "memory-system",
      "escalation_level": 0,
      "escalation_dates": [],
      "status": "active",
      "created_at": "2026-03-23T17:00:00Z",
      "resolved_at": null,
      "resolution": null
    }
  ],
  
  "notes": [
    {
      "id": "note_001",
      "content": "SQLite FTS5 extension provides excellent full-text search",
      "category": "technical",
      "tags": ["sqlite", "search"],
      "created_at": "2026-03-23T16:30:00Z"
    }
  ],
  
  "conversations": [
    {
      "id": "conv_001",
      "source": "telegram",
      "participants": ["user", "assistant"],
      "summary": "Discussed memory system requirements",
      "extracted_tasks": ["task_001"],
      "extracted_decisions": ["dec_001"],
      "extracted_blockers": ["blk_001"],
      "timestamp": "2026-03-23T14:00:00Z",
      "context_hash": "sha256:abc123..."
    }
  ],
  
  "metrics": {
    "tasks_completed": 1,
    "tasks_created": 3,
    "decisions_made": 1,
    "blockers_identified": 1,
    "blockers_resolved": 0,
    "hours_logged": 4.5
  },
  
  "tags": ["memory-system", "development", "planning"],
  "references": ["2026-03-22", "project/memory-system"]
}
```

### 2.2 Project Schema (JSON)

```json
{
  "id": "memory-system",
  "name": "Memory Management System",
  "description": "Python CLI tool for structured memory management",
  "status": "active",
  "priority": "high",
  
  "created_at": "2026-03-23T14:00:00Z",
  "started_at": "2026-03-23T14:00:00Z",
  "target_completion": "2026-04-15T23:59:59Z",
  "completed_at": null,
  
  "goals": [
    "Create CLI tool for daily logs",
    "Implement search and indexing",
    "Build dashboard views"
  ],
  
  "tasks": {
    "total": 15,
    "completed": 3,
    "in_progress": 2,
    "blocked": 1,
    "backlog": 9
  },
  
  "blockers": ["blk_001"],
  "decisions": ["dec_001"],
  
  "linked_entries": ["2026-03-23", "2026-03-22"],
  
  "metadata": {
    "category": "tooling",
    "tags": ["python", "cli", "productivity"],
    "color": "#4A90E2"
  }
}
```

### 2.3 Decision Registry Schema (JSON)

```json
{
  "version": "1.0",
  "last_updated": "2026-03-23T18:00:00Z",
  "decisions": [
    {
      "id": "dec_001",
      "title": "Use SQLite for indexing",
      "context": "Need fast search across all entries",
      "decision": "Implement SQLite FTS for full-text search",
      "rationale": "Balance between simplicity and power",
      "alternatives": [
        {
          "option": "JSON only",
          "pros": ["No dependencies", "Simple"],
          "cons": ["Slow search", "No indexing"]
        },
        {
          "option": "Elasticsearch",
          "pros": ["Powerful search", "Scalable"],
          "cons": ["Heavy dependency", "Overkill for local tool"]
        }
      ],
      "consequences": {
        "positive": ["Fast search", "ACID compliance"],
        "negative": ["Additional dependency"]
      },
      "reversibility": "medium",
      "reversible_until": "2026-04-23T00:00:00Z",
      "status": "active",
      "superseded_by": null,
      "project_id": "memory-system",
      "created_at": "2026-03-23T15:00:00Z",
      "review_date": "2026-06-23T00:00:00Z",
      "linked_entries": ["2026-03-23"],
      "tags": ["architecture", "database"]
    }
  ]
}
```

### 2.4 Blocker Schema with Escalation

```json
{
  "id": "blk_001",
  "title": "API rate limiting issues",
  "description": "Third-party API has strict rate limits",
  "severity": "high",
  "impact": "blocking",
  
  "created_at": "2026-03-20T10:00:00Z",
  "escalation": {
    "level": 2,
    "levels": [
      {"level": 0, "name": "Identified", "date": "2026-03-20T10:00:00Z"},
      {"level": 1, "name": "Acknowledged", "date": "2026-03-21T09:00:00Z"},
      {"level": 2, "name": "Escalated", "date": "2026-03-23T14:00:00Z"}
    ],
    "next_escalation": "2026-03-25T10:00:00Z",
    "escalation_trigger": "If not resolved within 48 hours"
  },
  
  "status": "escalated",
  "resolution": null,
  "resolved_at": null,
  
  "mitigation": {
    "attempted": ["Implemented caching", "Added retry logic"],
    "pending": ["Contact API provider"],
    "workaround": "Batch requests overnight"
  },
  
  "assigned_to": "dev-team",
  "project_id": "project-alpha",
  "linked_entries": ["2026-03-20", "2026-03-21", "2026-03-23"],
  "tags": ["api", "rate-limit", "external-dependency"]
}
```

---

## 3. SQLite Database Schema

```sql
-- Main entries table
CREATE TABLE entries (
    id TEXT PRIMARY KEY,
    date TEXT NOT NULL,
    timestamp_created TEXT NOT NULL,
    timestamp_updated TEXT NOT NULL,
    summary_title TEXT,
    summary_description TEXT,
    mood TEXT,
    energy_level INTEGER,
    tags TEXT, -- JSON array
    references_json TEXT, -- JSON array
    raw_json TEXT NOT NULL -- Full entry JSON
);

-- Full-text search virtual table
CREATE VIRTUAL TABLE entries_fts USING fts5(
    id,
    summary_title,
    summary_description,
    content='entries',
    content_rowid='rowid'
);

-- Triggers to keep FTS index in sync
CREATE TRIGGER entries_ai AFTER INSERT ON entries BEGIN
    INSERT INTO entries_fts(id, summary_title, summary_description)
    VALUES (new.id, new.summary_title, new.summary_description);
END;

CREATE TRIGGER entries_ad AFTER DELETE ON entries BEGIN
    INSERT INTO entries_fts(entries_fts, rowid, summary_title, summary_description)
    VALUES ('delete', old.rowid, old.summary_title, old.summary_description);
END;

CREATE TRIGGER entries_au AFTER UPDATE ON entries BEGIN
    INSERT INTO entries_fts(entries_fts, rowid, summary_title, summary_description)
    VALUES ('delete', old.rowid, old.summary_title, old.summary_description);
    INSERT INTO entries_fts(id, summary_title, summary_description)
    VALUES (new.id, new.summary_title, new.summary_description);
END;

-- Tasks table
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL, -- pending, in_progress, completed, blocked, cancelled
    priority TEXT NOT NULL, -- low, medium, high, critical
    project_id TEXT,
    entry_date TEXT NOT NULL,
    created_at TEXT NOT NULL,
    completed_at TEXT,
    estimated_hours REAL,
    actual_hours REAL,
    tags TEXT, -- JSON array
    raw_json TEXT NOT NULL,
    FOREIGN KEY (entry_date) REFERENCES entries(id)
);

-- Decisions table
CREATE TABLE decisions (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    context TEXT,
    decision TEXT NOT NULL,
    reversibility TEXT, -- low, medium, high
    status TEXT NOT NULL, -- active, superseded, reversed
    project_id TEXT,
    created_at TEXT NOT NULL,
    review_date TEXT,
    superseded_by TEXT,
    tags TEXT, -- JSON array
    raw_json TEXT NOT NULL
);

-- Blockers table
CREATE TABLE blockers (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    severity TEXT NOT NULL, -- low, medium, high, critical
    impact TEXT NOT NULL, -- minor, moderate, blocking, critical
    escalation_level INTEGER DEFAULT 0,
    status TEXT NOT NULL, -- active, mitigated, resolved
    project_id TEXT,
    assigned_to TEXT,
    created_at TEXT NOT NULL,
    resolved_at TEXT,
    resolution TEXT,
    tags TEXT, -- JSON array
    raw_json TEXT NOT NULL
);

-- Projects table
CREATE TABLE projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL, -- active, paused, completed, archived
    priority TEXT NOT NULL,
    created_at TEXT NOT NULL,
    started_at TEXT,
    target_completion TEXT,
    completed_at TEXT,
    color TEXT,
    tags TEXT, -- JSON array
    raw_json TEXT NOT NULL
);

-- Tags table for fast tag-based queries
CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    category TEXT,
    usage_count INTEGER DEFAULT 0
);

-- Entry-tag relationships
CREATE TABLE entry_tags (
    entry_id TEXT NOT NULL,
    tag_name TEXT NOT NULL,
    PRIMARY KEY (entry_id, tag_name),
    FOREIGN KEY (entry_id) REFERENCES entries(id)
);

-- Conversations extracted from context
CREATE TABLE conversations (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    summary TEXT,
    timestamp TEXT NOT NULL,
    context_hash TEXT,
    extracted_tasks TEXT, -- JSON array of task IDs
    extracted_decisions TEXT, -- JSON array of decision IDs
    extracted_blockers TEXT, -- JSON array of blocker IDs
    raw_json TEXT NOT NULL
);

-- Index for performance
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_project ON tasks(project_id);
CREATE INDEX idx_decisions_status ON decisions(status);
CREATE INDEX idx_blockers_status ON blockers(status);
CREATE INDEX idx_blockers_escalation ON blockers(escalation_level);
CREATE INDEX idx_entries_date ON entries(date);
```

---

## 4. CLI Command Structure

### 4.1 Main Commands

```python
# memory-manager.py

usage: memory-manager.py [-h] [--config CONFIG] [--verbose] [--no-color]
                        {init,entry,task,decision,blocker,project,search,report,dashboard,parse,sync}
                        ...

Memory Management System - Track daily logs, tasks, decisions, and blockers

positional arguments:
  {init,entry,task,decision,blocker,project,search,report,dashboard,parse,sync}
    init                Initialize memory system
    entry               Manage daily entries
    task                Manage tasks
    decision            Manage decisions
    blocker             Manage blockers
    project             Manage projects
    search              Search across all memory
    report              Generate reports
    dashboard           Update dashboard views
    parse               Parse conversation context
    sync                Sync database with JSON files

optional arguments:
  -h, --help            Show this help message and exit
  --config CONFIG, -c CONFIG
                        Path to config file
  --verbose, -v         Enable verbose output
  --no-color            Disable colorized output
```

### 4.2 Entry Commands

```python
# Create new daily entry
memory-manager.py entry create [--date DATE] [--title TITLE] [--template TEMPLATE]

# Edit existing entry
memory-manager.py entry edit <date>

# View entry
memory-manager.py entry show <date> [--format {json,markdown,table}]

# List entries
memory-manager.py entry list [--from DATE] [--to DATE] [--project PROJECT] [--tag TAG]

# Delete entry
memory-manager.py entry delete <date> [--force]

# Link entries
memory-manager.py entry link <date1> <date2>
```

### 4.3 Task Commands

```python
# Add task
memory-manager.py task add "Task title" [--description DESC] [--priority {low,medium,high,critical}]
    [--project PROJECT] [--due DATE] [--tag TAG]

# List tasks
memory-manager.py task list [--status {pending,in_progress,completed,blocked,all}]
    [--project PROJECT] [--priority PRIORITY] [--from DATE] [--to DATE]

# Update task
memory-manager.py task update <task-id> [--status STATUS] [--progress %]

# Complete task
memory-manager.py task complete <task-id> [--hours HOURS]

# Block task
memory-manager.py task block <task-id> --reason "Blocker reason"

# Delete task
memory-manager.py task delete <task-id> [--force]
```

### 4.4 Decision Commands

```python
# Record decision
memory-manager.py decision add "Decision title" --context "Context" --choice "Chosen option"
    [--alternatives "Option 1, Option 2"] [--reversibility {low,medium,high}]
    [--project PROJECT] [--review-date DATE]

# List decisions
memory-manager.py decision list [--project PROJECT] [--status {active,superseded,reversed}]
    [--tag TAG] [--search QUERY]

# Update decision status
memory-manager.py decision update <dec-id> --status {active,superseded,reversed}

# Supersede decision
memory-manager.py decision supersede <old-id> <new-id> --reason "Reason for change"

# Review upcoming decisions
memory-manager.py decision review [--days N]
```

### 4.5 Blocker Commands

```python
# Add blocker
memory-manager.py blocker add "Blocker title" --description "Description"
    [--severity {low,medium,high,critical}] [--impact {minor,moderate,blocking,critical}]
    [--project PROJECT] [--assigned-to USER]

# List blockers
memory-manager.py blocker list [--status {active,mitigated,resolved,all}]
    [--severity SEVERITY] [--escalation-level N] [--project PROJECT]

# Escalate blocker
memory-manager.py blocker escalate <blocker-id> [--level N] [--reason "Reason"]

# Resolve blocker
memory-manager.py blocker resolve <blocker-id> --resolution "How it was resolved"

# Add mitigation
memory-manager.py blocker mitigate <blocker-id> --action "Mitigation action"
```

### 4.6 Search Commands

```python
# Full-text search
memory-manager.py search "query" [--type {entry,task,decision,blocker,all}]
    [--project PROJECT] [--from DATE] [--to DATE] [--limit N]

# Search with filters
memory-manager.py search "query" --status completed --tag "urgent"

# Advanced search (SQLite FTS query syntax)
memory-manager.py search "memory AND system NOT database" --advanced

# Tag-based search
memory-manager.py search --tag "architecture" --tag "design"

# Date range search
memory-manager.py search --from 2026-03-01 --to 2026-03-31 "refactor"
```

### 4.7 Report Commands

```python
# Daily report
memory-manager.py report daily [--date DATE] [--output FILE]

# Weekly report
memory-manager.py report weekly [--week N] [--year YYYY] [--output FILE]

# Project report
memory-manager.py report project <project-id> [--from DATE] [--to DATE] [--output FILE]

# Blocker report
memory-manager.py report blockers [--escalated-only] [--output FILE]

# Decision report
memory-manager.py report decisions [--review-due] [--output FILE]

# Custom report
memory-manager.py report custom --template TEMPLATE --output FILE
```

### 4.8 Dashboard Commands

```python
# Update all dashboards
memory-manager.py dashboard update [--all]

# Update specific view
memory-manager.py dashboard update --view {overview,tasks,decisions,blockers,projects}

# Generate MEMORY.md
memory-manager.py dashboard generate-memory [--output FILE]

# Preview dashboard
memory-manager.py dashboard preview [--view VIEW]
```

### 4.9 Parse Commands (Integration)

```python
# Parse conversation file
memory-manager.py parse conversation <file> [--source {telegram,slack,email}]
    [--extract-tasks] [--extract-decisions] [--extract-blockers]
    [--auto-create] [--dry-run]

# Parse text directly
memory-manager.py parse text "Conversation text..." [--extract-all]

# Auto-extract from context
memory-manager.py parse context [--today] [--auto-create]

# Review parsed items
memory-manager.py parse review [--pending-only]

# Approve parsed items
memory-manager.py parse approve <parse-id>
```

### 4.10 Sync Commands

```python
# Sync JSON files to database
memory-manager.py sync to-db [--force]

# Sync database to JSON files
memory-manager.py sync to-json [--force]

# Full sync (bidirectional)
memory-manager.py sync full [--dry-run]

# Verify integrity
memory-manager.py sync verify [--fix]
```

---

## 5. Integration Scripts

### 5.1 Conversation Parser

```python
# integrations/conversation_parser.py

class ConversationParser:
    """Parse conversation context and extract structured data."""
    
    def __init__(self, nlp_backend='regex'):
        self.nlp_backend = nlp_backend
        self.task_patterns = [
            r'(?:TODO|FIXME|TASK|NEED TO|HAVE TO|MUST)\s*:?\s*(.+)',
            r'(?:\-|\*)\s*\[\s*\]\s*(.+)',
        ]
        self.decision_patterns = [
            r'(?:DECIDED|DECISION|CHOSEN|WILL USE|WENT WITH)\s*:?\s*(.+)',
        ]
        self.blocker_patterns = [
            r'(?:BLOCKED|BLOCKER|STUCK|ISSUE|PROBLEM)\s*:?\s*(.+)',
        ]
    
    def parse(self, text, source='unknown'):
        """Parse conversation text and return structured data."""
        return {
            'tasks': self.extract_tasks(text),
            'decisions': self.extract_decisions(text),
            'blockers': self.extract_blockers(text),
            'summary': self.generate_summary(text),
            'context_hash': self.compute_hash(text)
        }
    
    def extract_tasks(self, text):
        """Extract task items from text."""
        tasks = []
        for pattern in self.task_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                tasks.append({
                    'title': match.group(1).strip(),
                    'source_text': match.group(0),
                    'confidence': 'high'
                })
        return tasks
    
    def extract_decisions(self, text):
        """Extract decision items from text."""
        decisions = []
        # Implementation
        return decisions
    
    def extract_blockers(self, text):
        """Extract blocker items from text."""
        blockers = []
        # Implementation
        return blockers
    
    def generate_summary(self, text, max_length=200):
        """Generate conversation summary."""
        # Simple implementation - first sentence or truncated text
        sentences = text.split('.')
        summary = sentences[0][:max_length] if sentences else text[:max_length]
        return summary + '...' if len(text) > max_length else summary
```

### 5.2 Auto Entry Generator

```python
# integrations/auto_entry.py

class AutoEntryGenerator:
    """Automatically generate entry from conversation context."""
    
    def __init__(self, parser, database):
        self.parser = parser
        self.db = database
    
    def generate_from_conversation(self, conversation_text, 
                                   source='unknown',
                                   auto_create=False,
                                   dry_run=False):
        """Generate entry from conversation."""
        parsed = self.parser.parse(conversation_text, source)
        
        entry = {
            'id': datetime.now().strftime('%Y-%m-%d'),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'timestamp_created': datetime.now().isoformat(),
            'timestamp_updated': datetime.now().isoformat(),
            'version': '1.0',
            'summary': {
                'title': parsed['summary'][:100],
                'description': parsed['summary'],
            },
            'tasks': [self._task_to_entry_format(t) for t in parsed['tasks']],
            'decisions': [self._decision_to_entry_format(d) for d in parsed['decisions']],
            'blockers': [self._blocker_to_entry_format(b) for b in parsed['blockers']],
            'conversations': [{
                'id': f"conv_{uuid4().hex[:8]}",
                'source': source,
                'summary': parsed['summary'],
                'extracted_tasks': [t['id'] for t in parsed['tasks']],
                'extracted_decisions': [d['id'] for d in parsed['decisions']],
                'extracted_blockers': [b['id'] for b in parsed['blockers']],
                'timestamp': datetime.now().isoformat(),
                'context_hash': parsed['context_hash']
            }]
        }
        
        if dry_run:
            return {'entry': entry, 'created': False}
        
        if auto_create:
            self.db.save_entry(entry)
            return {'entry': entry, 'created': True}
        
        return {'entry': entry, 'created': False, 'pending_approval': True}
    
    def _task_to_entry_format(self, task):
        """Convert parsed task to entry format."""
        return {
            'id': f"task_{uuid4().hex[:8]}",
            'title': task['title'],
            'status': 'pending',
            'priority': 'medium',
            'created_at': datetime.now().isoformat(),
            'tags': ['auto-extracted']
        }
```

### 5.3 Real-time Dashboard Updater

```python
# views.py

class DashboardUpdater:
    """Update MEMORY.md and other dashboard views."""
    
    def __init__(self, database, template_dir='templates/'):
        self.db = database
        self.template_dir = template_dir
    
    def update_all(self):
        """Update all dashboard views."""
        self.generate_memory_md()
        self.generate_task_view()
        self.generate_decision_view()
        self.generate_blocker_view()
        self.generate_project_view()
    
    def generate_memory_md(self, output_path='MEMORY.md'):
        """Generate main MEMORY.md dashboard."""
        today = datetime.now().strftime('%Y-%m-%d')
        
        content = f"""# Memory Dashboard

*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*

## Quick Stats

{self._generate_stats_section()}

## Active Projects

{self._generate_projects_section()}

## Today's Focus

{self._generate_today_section()}

## Active Tasks

{self._generate_tasks_section(status='in_progress')}

## Pending Decisions

{self._generate_decisions_section()}

## Current Blockers

{self._generate_blockers_section()}

## Recent Entries

{self._generate_entries_section(limit=7)}

## Quick Links

- [All Entries](data/entries/)
- [All Projects](data/projects/)
- [Decision Registry](data/decisions/)
- [Generated Reports](reports/)

---

*Generated by Memory Manager v1.0*
"""
        
        with open(output_path, 'w') as f:
            f.write(content)
        
        return output_path
    
    def _generate_stats_section(self):
        """Generate statistics section."""
        stats = self.db.get_stats()
        return f"""
| Metric | Count |
|--------|-------|
| Total Entries | {stats['total_entries']} |
| Active Tasks | {stats['active_tasks']} |
| Completed Tasks | {stats['completed_tasks']} |
| Active Decisions | {stats['active_decisions']} |
| Active Blockers | {stats['active_blockers']} |
| Projects | {stats['total_projects']} |
"""
    
    def _generate_projects_section(self):
        """Generate projects overview."""
        projects = self.db.get_projects(status='active')
        lines = []
        for p in projects:
            progress = p['tasks']['completed'] / max(p['tasks']['total'], 1) * 100
            lines.append(f"- **{p['name']}** - {p['status']} ({progress:.0f}% complete)")
        return '\n'.join(lines) if lines else "_No active projects_"
    
    def _generate_tasks_section(self, status='in_progress', limit=10):
        """Generate tasks list."""
        tasks = self.db.get_tasks(status=status, limit=limit)
        lines = []
        for t in tasks:
            priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(t['priority'], '⚪')
            lines.append(f"- {priority_emoji} [{t['status']}] {t['title']}")
        return '\n'.join(lines) if lines else "_No tasks_"
```

---

## 6. Configuration

### 6.1 Config File (config.json)

```json
{
  "version": "1.0",
  "database": {
    "path": "data/.memory.db",
    "backup_enabled": true,
    "backup_interval_days": 7,
    "backup_path": "backups/"
  },
  "paths": {
    "entries": "data/entries/",
    "projects": "data/projects/",
    "decisions": "data/decisions/",
    "logs": "data/logs/",
    "reports": "reports/",
    "templates": "templates/"
  },
  "output": {
    "color_enabled": true,
    "date_format": "%Y-%m-%d",
    "datetime_format": "%Y-%m-%d %H:%M",
    "default_view": "table"
  },
  "editor": {
    "default": "vim",
    "template_for_new_entries": "templates/entry_template.md"
  },
  "parsing": {
    "auto_extract_tasks": true,
    "auto_extract_decisions": true,
    "auto_extract_blockers": true,
    "require_approval": true,
    "nlp_backend": "regex"
  },
  "escalation": {
    "enabled": true,
    "levels": [
      {"level": 0, "name": "Identified", "auto_escalate_after_hours": 24},
      {"level": 1, "name": "Acknowledged", "auto_escalate_after_hours": 48},
      {"level": 2, "name": "Escalated", "auto_escalate_after_hours": 72},
      {"level": 3, "name": "Critical", "auto_escalate_after_hours": null}
    ]
  },
  "integrations": {
    "telegram": {
      "enabled": false,
      "bot_token": null
    },
    "openclaw": {
      "enabled": true,
      "auto_parse": true
    }
  }
}
```

---

## 7. Dependencies

### 7.1 requirements.txt

```
# Core
click>=8.0.0          # CLI framework (alternative to argparse for better UX)
colorama>=0.4.4       # Cross-platform colored output

# Data & Database
sqlite3-fts4>=1.0.0   # FTS support (usually built-in)

# Optional enhancements
rich>=13.0.0          # Advanced terminal formatting (optional)
tabulate>=0.9.0       # Table formatting
python-dateutil>=2.8  # Date parsing
pyyaml>=6.0           # YAML config support

# NLP (optional - for advanced parsing)
# spacy>=3.0.0        # For advanced NLP parsing
# nltk>=3.8           # Natural language processing

# Development
pytest>=7.0.0         # Testing
pytest-cov>=4.0.0     # Coverage
black>=23.0.0         # Code formatting
flake8>=6.0.0         # Linting
```

### 7.2 Using Argparse (No External Dependencies)

For zero-dependency operation, use standard library only:

```python
# Core dependencies (Python standard library)
import argparse
import json
import sqlite3
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import re
import hashlib
import uuid
from typing import List, Dict, Optional, Any
import textwrap

# Color support via ANSI codes (no external dependency)
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
```

---

## 8. Implementation Roadmap

### Phase 1: Core Foundation (Week 1)
- [ ] Set up project structure
- [ ] Implement data models (models.py)
- [ ] Implement database layer (database.py)
- [ ] Create configuration management (config.py)
- [ ] Basic CLI structure with argparse

### Phase 2: Entry Management (Week 1-2)
- [ ] Entry CRUD operations
- [ ] JSON file I/O
- [ ] Markdown generation
- [ ] Entry linking
- [ ] Tag management

### Phase 3: Task/Decision/Blocker Tracking (Week 2)
- [ ] Task lifecycle management
- [ ] Decision registry
- [ ] Blocker tracking with escalation
- [ ] Project association

### Phase 4: Search & Reports (Week 3)
- [ ] SQLite FTS implementation
- [ ] Search command
- [ ] Report generation
- [ ] Filtering and sorting

### Phase 5: Integration & Automation (Week 3-4)
- [ ] Conversation parser
- [ ] Auto-entry generation
- [ ] Dashboard updater
- [ ] Real-time sync

### Phase 6: Polish & Documentation (Week 4)
- [ ] Colorized output
- [ ] Error handling
- [ ] Unit tests
- [ ] Documentation
- [ ] Installation script

---

## 9. Key Design Decisions

### 9.1 Dual Storage Strategy
- **JSON files**: Human-readable, version-control friendly, portable
- **SQLite**: Fast querying, full-text search, indexing
- **Sync mechanism**: Bidirectional sync with conflict resolution

### 9.2 ID Generation
- Entries: `YYYY-MM-DD` (one per day)
- Tasks: `task_{8char_hex}`
- Decisions: `dec_{8char_hex}`
- Blockers: `blk_{8char_hex}`
- Projects: user-defined slug

### 9.3 Escalation Logic
- Level 0 → 1: After 24 hours
- Level 1 → 2: After 48 hours  
- Level 2 → 3: After 72 hours
- Manual escalation always allowed
- Auto-escalation can be disabled per-blocker

### 9.4 Color Scheme
- 🔴 High priority / Critical / Blocking
- 🟡 Medium priority / In Progress
- 🟢 Low priority / Completed
- 🔵 Info / Projects
- ⚪ Neutral / Pending

---

## 10. Usage Examples

### Daily Workflow

```bash
# Morning - create or update today's entry
memory-manager.py entry create --title "Working on API integration"

# Add tasks as they come up
memory-manager.py task add "Fix authentication bug" --priority high --project api-v2

# Record a decision
memory-manager.py decision add "Use JWT for auth" \
  --context "Need stateless auth for microservices" \
  --choice "Implement JWT with 24h expiry" \
  --alternatives "Session cookies,OAuth2" \
  --reversibility medium

# Log a blocker
memory-manager.py blocker add "Rate limiting on external API" \
  --severity high \
  --impact blocking \
  --project api-v2

# Evening - generate reports
memory-manager.py report daily
memory-manager.py dashboard update

# Search for something
memory-manager.py search "authentication" --type decision
```

### Weekly Review

```bash
# Generate weekly report
memory-manager.py report weekly --output reports/week-12.md

# Review pending decisions
memory-manager.py decision list --status active

# Check escalated blockers
memory-manager.py blocker list --escalation-level 2

# Update dashboards
memory-manager.py dashboard update --all
```

---

## 11. File Size Estimates

| Component | Estimated Size |
|-----------|---------------|
| Core Python files | ~50KB |
| SQLite database (1 year entries) | ~5-10MB |
| JSON files (1 year) | ~10-20MB |
| Markdown logs (1 year) | ~5-10MB |
| Reports | ~1-2MB |
| **Total (1 year)** | **~20-40MB** |

---

*Document Version: 1.0*
*Created: 2026-03-23*
*For: Memory Management System Implementation*
