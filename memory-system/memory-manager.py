#!/usr/bin/env python3
"""
Memory Manager - Operational Memory System for OpenClaw
A comprehensive CLI tool for tracking daily work, projects, decisions, and blockers.

Created: 2026-03-23
Author: OpenClaw + Multi-Agent Team
"""

import os
import sys
import json
import sqlite3
import argparse
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

# Configuration
MEMORY_DIR = Path.home() / ".openclaw" / "memory"
DATA_DIR = MEMORY_DIR / "data"
INDEX_DIR = MEMORY_DIR / "index"
DAILY_DIR = MEMORY_DIR / "daily"
PROJECTS_DIR = MEMORY_DIR / "projects"
DB_FILE = DATA_DIR / "memory.db"

# Colors
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

def c(text, color):
    return f"{color}{text}{Colors.END}"

# Data Models
@dataclass
class Task:
    id: int
    title: str
    project: str
    priority: str  # low, medium, high, critical
    status: str    # pending, in_progress, completed, blocked
    created: str
    completed_date: Optional[str] = None
    owner: str = ""
    notes: str = ""

@dataclass
class Blocker:
    id: int
    title: str
    description: str
    project: str
    severity: str  # low, medium, high, critical
    status: str    # active, resolved, escalated
    created: str
    resolved_date: Optional[str] = None
    escalation_level: int = 0
    next_review: str = ""

@dataclass
class Decision:
    id: int
    title: str
    context: str
    choice: str
    rationale: str
    project: str
    created: str
    impact: str = ""  # low, medium, high
    reversible: bool = True

@dataclass
class Entry:
    id: int
    date: str
    project: str
    summary: str
    context: str
    tasks: List[Dict]
    decisions: List[Dict]
    blockers: List[Dict]
    next_steps: str
    references: List[str]
    status: str      # active, completed, archived
    priority: str    # low, medium, high
    participants: List[str]
    tags: List[str]
    created: str
    modified: str

# Database Setup
class MemoryDatabase:
    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(DB_FILE))
        self.conn.row_factory = sqlite3.Row
        self.init_tables()
    
    def init_tables(self):
        """Initialize SQLite tables with FTS5 for search"""
        cursor = self.conn.cursor()
        
        # Main entries table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                project TEXT NOT NULL,
                summary TEXT NOT NULL,
                context TEXT,
                next_steps TEXT,
                status TEXT DEFAULT 'active',
                priority TEXT DEFAULT 'medium',
                participants TEXT,  -- JSON array
                tags TEXT,          -- JSON array
                refs TEXT,    -- JSON array (references)
                created TEXT NOT NULL,
                modified TEXT NOT NULL
            )
        ''')
        
        # Tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_id INTEGER,
                title TEXT NOT NULL,
                project TEXT,
                priority TEXT DEFAULT 'medium',
                status TEXT DEFAULT 'pending',
                created TEXT NOT NULL,
                completed_date TEXT,
                owner TEXT,
                notes TEXT,
                FOREIGN KEY (entry_id) REFERENCES entries (id)
            )
        ''')
        
        # Blockers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blockers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_id INTEGER,
                title TEXT NOT NULL,
                description TEXT,
                project TEXT,
                severity TEXT DEFAULT 'medium',
                status TEXT DEFAULT 'active',
                created TEXT NOT NULL,
                resolved_date TEXT,
                escalation_level INTEGER DEFAULT 0,
                next_review TEXT,
                FOREIGN KEY (entry_id) REFERENCES entries (id)
            )
        ''')
        
        # Decisions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_id INTEGER,
                title TEXT NOT NULL,
                context TEXT,
                choice TEXT NOT NULL,
                rationale TEXT,
                project TEXT,
                created TEXT NOT NULL,
                impact TEXT DEFAULT 'medium',
                reversible INTEGER DEFAULT 1,
                FOREIGN KEY (entry_id) REFERENCES entries (id)
            )
        ''')
        
        # FTS5 virtual table for full-text search
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS entries_fts USING fts5(
                summary, context, next_steps, 
                content='entries',
                content_rowid='id'
            )
        ''')
        
        # Triggers to keep FTS index updated
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS entries_ai AFTER INSERT ON entries BEGIN
                INSERT INTO entries_fts(rowid, summary, context, next_steps)
                VALUES (new.id, new.summary, new.context, new.next_steps);
            END
        ''')
        
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS entries_ad AFTER DELETE ON entries BEGIN
                INSERT INTO entries_fts(entries_fts, rowid, summary, context, next_steps)
                VALUES ('delete', old.id, old.summary, old.context, old.next_steps);
            END
        ''')
        
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS entries_au AFTER UPDATE ON entries BEGIN
                INSERT INTO entries_fts(entries_fts, rowid, summary, context, next_steps)
                VALUES ('delete', old.id, old.summary, old.context, old.next_steps);
                INSERT INTO entries_fts(rowid, summary, context, next_steps)
                VALUES (new.id, new.summary, new.context, new.next_steps);
            END
        ''')
        
        self.conn.commit()
    
    def add_entry(self, entry: Entry) -> int:
        """Add a new entry and return its ID"""
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT INTO entries (date, project, summary, context, next_steps, 
                               status, priority, participants, tags, refs,
                               created, modified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            entry.date, entry.project, entry.summary, entry.context, 
            entry.next_steps, entry.status, entry.priority,
            json.dumps(entry.participants), json.dumps(entry.tags),
            json.dumps(entry.references), now, now
        ))
        
        entry_id = cursor.lastrowid
        
        # Add tasks
        for task_data in entry.tasks:
            cursor.execute('''
                INSERT INTO tasks (entry_id, title, project, priority, status, 
                                 created, owner, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                entry_id, task_data.get('title', ''), 
                task_data.get('project', entry.project),
                task_data.get('priority', 'medium'),
                task_data.get('status', 'pending'),
                now, task_data.get('owner', ''), 
                task_data.get('notes', '')
            ))
        
        # Add blockers
        for blocker_data in entry.blockers:
            cursor.execute('''
                INSERT INTO blockers (entry_id, title, description, project, 
                                    severity, status, created, next_review)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                entry_id, blocker_data.get('title', ''),
                blocker_data.get('description', ''),
                blocker_data.get('project', entry.project),
                blocker_data.get('severity', 'medium'),
                blocker_data.get('status', 'active'),
                now, blocker_data.get('next_review', '')
            ))
        
        # Add decisions
        for decision_data in entry.decisions:
            cursor.execute('''
                INSERT INTO decisions (entry_id, title, context, choice, rationale,
                                     project, created, impact, reversible)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                entry_id, decision_data.get('title', ''),
                decision_data.get('context', ''),
                decision_data.get('choice', ''),
                decision_data.get('rationale', ''),
                decision_data.get('project', entry.project),
                now, decision_data.get('impact', 'medium'),
                1 if decision_data.get('reversible', True) else 0
            ))
        
        self.conn.commit()
        return entry_id
    
    def search(self, query: str, limit: int = 20) -> List[Dict]:
        """Full-text search across all entries"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT e.* FROM entries e
            JOIN entries_fts fts ON e.id = fts.rowid
            WHERE entries_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        ''', (query, limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row['id'],
                'date': row['date'],
                'project': row['project'],
                'summary': row['summary'],
                'context': row['context'][:100] + '...' if len(row['context']) > 100 else row['context'],
                'status': row['status'],
                'priority': row['priority']
            })
        return results
    
    def get_active_tasks(self, project: str = None) -> List[Dict]:
        """Get all active (pending/in_progress) tasks"""
        cursor = self.conn.cursor()
        
        if project:
            cursor.execute('''
                SELECT * FROM tasks 
                WHERE status IN ('pending', 'in_progress') AND project = ?
                ORDER BY priority DESC, created DESC
            ''', (project,))
        else:
            cursor.execute('''
                SELECT * FROM tasks 
                WHERE status IN ('pending', 'in_progress')
                ORDER BY priority DESC, created DESC
            ''')
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_active_blockers(self, project: str = None) -> List[Dict]:
        """Get all active blockers with escalation check"""
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()
        
        # First, auto-escalate old blockers
        cursor.execute('''
            UPDATE blockers 
            SET escalation_level = escalation_level + 1,
                next_review = ?
            WHERE status = 'active' 
            AND next_review < ?
        ''', ((datetime.now() + timedelta(days=1)).isoformat(), now))
        
        if project:
            cursor.execute('''
                SELECT * FROM blockers 
                WHERE status = 'active' AND project = ?
                ORDER BY severity DESC, escalation_level DESC, created DESC
            ''', (project,))
        else:
            cursor.execute('''
                SELECT * FROM blockers 
                WHERE status = 'active'
                ORDER BY severity DESC, escalation_level DESC, created DESC
            ''')
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_recent_decisions(self, days: int = 7, project: str = None) -> List[Dict]:
        """Get recent decisions"""
        cursor = self.conn.cursor()
        since = (datetime.now() - timedelta(days=days)).isoformat()
        
        if project:
            cursor.execute('''
                SELECT * FROM decisions 
                WHERE created > ? AND project = ?
                ORDER BY created DESC
            ''', (since, project))
        else:
            cursor.execute('''
                SELECT * FROM decisions 
                WHERE created > ?
                ORDER BY created DESC
            ''', (since,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def complete_task(self, task_id: int) -> bool:
        """Mark a task as completed"""
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()
        
        cursor.execute('''
            UPDATE tasks 
            SET status = 'completed', completed_date = ?
            WHERE id = ?
        ''', (now, task_id))
        
        self.conn.commit()
        return cursor.rowcount > 0
    
    def resolve_blocker(self, blocker_id: int) -> bool:
        """Mark a blocker as resolved"""
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()
        
        cursor.execute('''
            UPDATE blockers 
            SET status = 'resolved', resolved_date = ?
            WHERE id = ?
        ''', (now, blocker_id))
        
        self.conn.commit()
        return cursor.rowcount > 0
    
    def get_dashboard_stats(self) -> Dict:
        """Get statistics for dashboard"""
        cursor = self.conn.cursor()
        
        # Count active tasks
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status IN ('pending', 'in_progress')")
        active_tasks = cursor.fetchone()[0]
        
        # Count completed tasks today
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute('''
            SELECT COUNT(*) FROM tasks 
            WHERE status = 'completed' AND completed_date LIKE ?
        ''', (f'{today}%',))
        completed_today = cursor.fetchone()[0]
        
        # Count active blockers
        cursor.execute("SELECT COUNT(*) FROM blockers WHERE status = 'active'")
        active_blockers = cursor.fetchone()[0]
        
        # Count escalated blockers (level > 1)
        cursor.execute("SELECT COUNT(*) FROM blockers WHERE status = 'active' AND escalation_level > 1")
        escalated_blockers = cursor.fetchone()[0]
        
        # Recent decisions (7 days)
        since = (datetime.now() - timedelta(days=7)).isoformat()
        cursor.execute("SELECT COUNT(*) FROM decisions WHERE created > ?", (since,))
        recent_decisions = cursor.fetchone()[0]
        
        # Active projects
        cursor.execute("SELECT COUNT(DISTINCT project) FROM entries WHERE status = 'active'")
        active_projects = cursor.fetchone()[0]
        
        return {
            'active_tasks': active_tasks,
            'completed_today': completed_today,
            'active_blockers': active_blockers,
            'escalated_blockers': escalated_blockers,
            'recent_decisions': recent_decisions,
            'active_projects': active_projects
        }
    
    def close(self):
        self.conn.close()

# Entry Template
ENTRY_TEMPLATE = """---
id: {id}
date: {date}
project: {project}
status: {status}
priority: {priority}
participants: {participants}
tags: {tags}
created: {created}
modified: {modified}
---

# {summary}

## Context
{context}

## Tasks
{tasks_section}

## Decisions
{decisions_section}

## Blockers
{blockers_section}

## Next Steps
{next_steps}

## References
{references_section}
"""

def format_tasks(tasks: List[Dict]) -> str:
    if not tasks:
        return "- None"
    lines = []
    for t in tasks:
        status = "✓" if t.get('status') == 'completed' else "○"
        lines.append(f"- [{status}] **{t.get('priority', 'medium').upper()}** {t.get('title', '')} (Owner: {t.get('owner', 'unspecified')})")
    return "\n".join(lines)

def format_blockers(blockers: List[Dict]) -> str:
    if not blockers:
        return "- None"
    lines = []
    for b in blockers:
        escalated = " ⚠️ ESCALATED" if b.get('escalation_level', 0) > 0 else ""
        lines.append(f"- **[{b.get('severity', 'medium').upper()}]** {b.get('title', '')}{escalated}")
        if b.get('description'):
            lines.append(f"  - {b.get('description')}")
    return "\n".join(lines)

def format_decisions(decisions: List[Dict]) -> str:
    if not decisions:
        return "- None"
    lines = []
    for d in decisions:
        reversible = " (Reversible)" if d.get('reversible') else " (Irreversible)"
        lines.append(f"- **{d.get('title', '')}**{reversible}")
        lines.append(f"  - Choice: {d.get('choice', '')}")
        if d.get('rationale'):
            lines.append(f"  - Rationale: {d.get('rationale')}")
    return "\n".join(lines)

def format_references(refs: List[str]) -> str:
    if not refs:
        return "- None"
    return "\n".join([f"- {r}" for r in refs])

# CLI Commands
def cmd_init(args):
    """Initialize the memory system"""
    print(c("Initializing Memory System...", Colors.HEADER))
    
    # Create directories
    for dir_path in [MEMORY_DIR, DATA_DIR, INDEX_DIR, DAILY_DIR, PROJECTS_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(c(f"  ✓ {dir_path}", Colors.GREEN))
    
    # Initialize database
    db = MemoryDatabase()
    db.close()
    print(c(f"  ✓ Database: {DB_FILE}", Colors.GREEN))
    
    # Create today's log
    today = datetime.now().strftime('%Y-%m-%d')
    daily_file = DAILY_DIR / f"{today}.md"
    if not daily_file.exists():
        daily_file.write_text(f"# Daily Log - {today}\n\n## Entries\n\n")
        print(c(f"  ✓ Daily log: {daily_file}", Colors.GREEN))
    
    print(c("\n✅ Memory system initialized!", Colors.GREEN))
    print(f"\nNext steps:")
    print(f"  1. Add an entry: {sys.argv[0]} entry add")
    print(f"  2. View dashboard: {sys.argv[0]} dashboard")
    print(f"  3. Search: {sys.argv[0]} search <query>")

def cmd_entry_add(args):
    """Add a new entry"""
    db = MemoryDatabase()
    
    print(c("\n📝 Create New Entry", Colors.HEADER))
    print("=" * 50)
    
    # Interactive prompts
    summary = input(c("Summary: ", Colors.BOLD)) or "Untitled entry"
    project = input(c("Project: ", Colors.BOLD)) or "general"
    context = input(c("Context (why this matters): ", Colors.BOLD)) or ""
    next_steps = input(c("Next steps: ", Colors.BOLD)) or ""
    priority = input(c("Priority (low/medium/high) [medium]: ", Colors.BOLD)) or "medium"
    
    # Parse tasks
    print(c("\nTasks (enter blank line to finish):", Colors.BOLD))
    tasks = []
    while True:
        task_input = input("  Task (format: 'title | priority' or just 'title'): ")
        if not task_input.strip():
            break
        parts = task_input.split('|')
        tasks.append({
            'title': parts[0].strip(),
            'priority': parts[1].strip() if len(parts) > 1 else 'medium',
            'status': 'pending',
            'owner': ''
        })
    
    # Parse blockers
    print(c("\nBlockers (enter blank line to finish):", Colors.BOLD))
    blockers = []
    while True:
        blocker_input = input("  Blocker (format: 'title | severity' or just 'title'): ")
        if not blocker_input.strip():
            break
        parts = blocker_input.split('|')
        blockers.append({
            'title': parts[0].strip(),
            'severity': parts[1].strip() if len(parts) > 1 else 'medium',
            'description': '',
            'status': 'active',
            'next_review': (datetime.now() + timedelta(days=1)).isoformat()
        })
    
    # Parse decisions
    print(c("\nDecisions (enter blank line to finish):", Colors.BOLD))
    decisions = []
    while True:
        decision_input = input("  Decision (format: 'title | choice'): ")
        if not decision_input.strip():
            break
        parts = decision_input.split('|')
        decisions.append({
            'title': parts[0].strip(),
            'choice': parts[1].strip() if len(parts) > 1 else '',
            'context': '',
            'rationale': '',
            'impact': 'medium',
            'reversible': True
        })
    
    # Create entry
    now = datetime.now()
    entry = Entry(
        id=0,  # Will be assigned by DB
        date=now.strftime('%Y-%m-%d'),
        project=project,
        summary=summary,
        context=context,
        tasks=tasks,
        decisions=decisions,
        blockers=blockers,
        next_steps=next_steps,
        references=[],
        status='active',
        priority=priority,
        participants=[],
        tags=[],
        created=now.isoformat(),
        modified=now.isoformat()
    )
    
    entry_id = db.add_entry(entry)
    db.close()
    
    print(c(f"\n✅ Entry #{entry_id} created successfully!", Colors.GREEN))
    
    # Write to daily markdown file
    daily_file = DAILY_DIR / f"{entry.date}.md"
    with open(daily_file, 'a') as f:
        f.write(f"\n### Entry {entry_id}\n")
        f.write(f"- **Project:** {entry.project}\n")
        f.write(f"- **Summary:** {entry.summary}\n")
        f.write(f"- **Status:** {entry.status}\n")
        if tasks:
            f.write(f"- **Tasks:** {len(tasks)}\n")
        if blockers:
            f.write(f"- **Blockers:** {len(blockers)}\n")
        f.write("\n")

def cmd_dashboard(args):
    """Show dashboard"""
    db = MemoryDatabase()
    
    print(c("\n" + "=" * 60, Colors.CYAN))
    print(c("  MEMORY DASHBOARD", Colors.CYAN + Colors.BOLD))
    print(c("=" * 60 + "\n", Colors.CYAN))
    
    # Stats
    stats = db.get_dashboard_stats()
    
    print(c("📊 OVERVIEW", Colors.BOLD))
    print(f"  Active Projects: {c(stats['active_projects'], Colors.CYAN)}")
    print(f"  Active Tasks: {c(stats['active_tasks'], Colors.YELLOW)}")
    print(f"  Completed Today: {c(stats['completed_today'], Colors.GREEN)}")
    print(f"  Active Blockers: {c(stats['active_blockers'], Colors.RED)}")
    if stats['escalated_blockers'] > 0:
        print(f"  ⚠️  Escalated Blockers: {c(stats['escalated_blockers'], Colors.RED + Colors.BOLD)}")
    print(f"  Recent Decisions (7d): {c(stats['recent_decisions'], Colors.BLUE)}")
    
    # Active tasks
    print(c("\n📋 ACTIVE TASKS", Colors.BOLD))
    tasks = db.get_active_tasks()
    if tasks:
        for task in tasks[:10]:  # Show top 10
            priority_color = Colors.RED if task['priority'] == 'high' else Colors.YELLOW if task['priority'] == 'medium' else Colors.GREEN
            print(f"  [{c(task['priority'][:1].upper(), priority_color)}] {task['title'][:50]}")
            if task['project']:
                print(f"      Project: {task['project']}")
    else:
        print("  No active tasks")
    
    # Active blockers
    print(c("\n🚧 ACTIVE BLOCKERS", Colors.BOLD))
    blockers = db.get_active_blockers()
    if blockers:
        for blocker in blockers[:5]:
            severity_color = Colors.RED if blocker['severity'] == 'high' else Colors.YELLOW
            esc = " ⚠️ ESCALATED" if blocker['escalation_level'] > 0 else ""
            print(f"  [{c(blocker['severity'][:1].upper(), severity_color)}] {blocker['title'][:50]}{esc}")
    else:
        print("  No active blockers")
    
    # Recent decisions
    print(c("\n💡 RECENT DECISIONS (7 days)", Colors.BOLD))
    decisions = db.get_recent_decisions(days=7)
    if decisions:
        for decision in decisions[:5]:
            rev = " (Rev)" if decision['reversible'] else " (Irrev)"
            print(f"  • {decision['title'][:50]}{rev}")
    else:
        print("  No recent decisions")
    
    db.close()

def cmd_search(args):
    """Search entries"""
    db = MemoryDatabase()
    
    print(c(f"\n🔍 Search: '{args.query}'", Colors.HEADER))
    print("=" * 60)
    
    results = db.search(args.query, limit=args.limit)
    
    if results:
        for i, result in enumerate(results, 1):
            priority_color = Colors.RED if result['priority'] == 'high' else Colors.YELLOW if result['priority'] == 'medium' else Colors.GREEN
            print(f"\n{i}. {c(result['summary'], Colors.BOLD)}")
            print(f"   Date: {result['date']} | Project: {result['project']}")
            print(f"   Priority: {c(result['priority'], priority_color)} | Status: {result['status']}")
            if result['context']:
                print(f"   Context: {result['context'][:80]}...")
    else:
        print(c("\nNo results found.", Colors.YELLOW))
    
    db.close()

def cmd_task_list(args):
    """List tasks"""
    db = MemoryDatabase()
    
    print(c("\n📋 TASKS", Colors.HEADER))
    print("=" * 60)
    
    tasks = db.get_active_tasks(project=args.project)
    
    if tasks:
        for task in tasks:
            status_icon = "✓" if task['status'] == 'completed' else "○"
            priority_color = Colors.RED if task['priority'] == 'high' else Colors.YELLOW if task['priority'] == 'medium' else Colors.GREEN
            print(f"\n[{status_icon}] #{task['id']} [{c(task['priority'].upper(), priority_color)}] {task['title']}")
            print(f"    Project: {task['project']} | Created: {task['created'][:10]}")
            if task['owner']:
                print(f"    Owner: {task['owner']}")
    else:
        print(c("\nNo active tasks.", Colors.YELLOW))
    
    db.close()

def cmd_task_complete(args):
    """Complete a task"""
    db = MemoryDatabase()
    
    if db.complete_task(args.id):
        print(c(f"✅ Task #{args.id} marked as completed!", Colors.GREEN))
    else:
        print(c(f"❌ Task #{args.id} not found.", Colors.RED))
    
    db.close()

def cmd_blocker_list(args):
    """List blockers"""
    db = MemoryDatabase()
    
    print(c("\n🚧 BLOCKERS", Colors.HEADER))
    print("=" * 60)
    
    blockers = db.get_active_blockers(project=args.project)
    
    if blockers:
        for blocker in blockers:
            severity_color = Colors.RED if blocker['severity'] == 'critical' else Colors.RED if blocker['severity'] == 'high' else Colors.YELLOW
            esc = f" (Escalation Level: {blocker['escalation_level']})" if blocker['escalation_level'] > 0 else ""
            print(f"\n#{blocker['id']} [{c(blocker['severity'].upper(), severity_color)}] {blocker['title']}{esc}")
            print(f"   Project: {blocker['project']} | Created: {blocker['created'][:10]}")
            if blocker['description']:
                print(f"   Description: {blocker['description'][:100]}")
    else:
        print(c("\nNo active blockers! 🎉", Colors.GREEN))
    
    db.close()

def cmd_blocker_resolve(args):
    """Resolve a blocker"""
    db = MemoryDatabase()
    
    if db.resolve_blocker(args.id):
        print(c(f"✅ Blocker #{args.id} resolved!", Colors.GREEN))
    else:
        print(c(f"❌ Blocker #{args.id} not found.", Colors.RED))
    
    db.close()

def main():
    parser = argparse.ArgumentParser(
        description="Memory Manager - Operational Memory System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s init                              # Initialize system
  %(prog)s entry add                         # Add new entry
  %(prog)s dashboard                         # Show dashboard
  %(prog)s search "authentication"           # Search entries
  %(prog)s task list                         # List active tasks
  %(prog)s task complete 5                   # Complete task #5
  %(prog)s blocker list                      # List blockers
  %(prog)s blocker resolve 3                 # Resolve blocker #3
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize memory system')
    
    # Entry commands
    entry_parser = subparsers.add_parser('entry', help='Entry management')
    entry_subparsers = entry_parser.add_subparsers(dest='entry_cmd')
    entry_add = entry_subparsers.add_parser('add', help='Add new entry')
    
    # Dashboard command
    dashboard_parser = subparsers.add_parser('dashboard', help='Show dashboard')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search entries')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('-l', '--limit', type=int, default=20, help='Max results')
    
    # Task commands
    task_parser = subparsers.add_parser('task', help='Task management')
    task_subparsers = task_parser.add_subparsers(dest='task_cmd')
    task_list = task_subparsers.add_parser('list', help='List tasks')
    task_list.add_argument('-p', '--project', help='Filter by project')
    task_complete = task_subparsers.add_parser('complete', help='Complete task')
    task_complete.add_argument('id', type=int, help='Task ID')
    
    # Blocker commands
    blocker_parser = subparsers.add_parser('blocker', help='Blocker management')
    blocker_subparsers = blocker_parser.add_subparsers(dest='blocker_cmd')
    blocker_list = blocker_subparsers.add_parser('list', help='List blockers')
    blocker_list.add_argument('-p', '--project', help='Filter by project')
    blocker_resolve = blocker_subparsers.add_parser('resolve', help='Resolve blocker')
    blocker_resolve.add_argument('id', type=int, help='Blocker ID')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Route commands
    if args.command == 'init':
        cmd_init(args)
    elif args.command == 'entry':
        if args.entry_cmd == 'add':
            cmd_entry_add(args)
        else:
            entry_parser.print_help()
    elif args.command == 'dashboard':
        cmd_dashboard(args)
    elif args.command == 'search':
        cmd_search(args)
    elif args.command == 'task':
        if args.task_cmd == 'list':
            cmd_task_list(args)
        elif args.task_cmd == 'complete':
            cmd_task_complete(args)
        else:
            task_parser.print_help()
    elif args.command == 'blocker':
        if args.blocker_cmd == 'list':
            cmd_blocker_list(args)
        elif args.blocker_cmd == 'resolve':
            cmd_blocker_resolve(args)
        else:
            blocker_parser.print_help()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()