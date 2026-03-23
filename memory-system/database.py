"""
SQLite Database Operations for Memory Management System
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path

from models import Entry, Task, Decision, Blocker, Project, Summary, Metrics


class Database:
    """SQLite database manager with FTS support."""
    
    SCHEMA = """
    -- Main entries table
    CREATE TABLE IF NOT EXISTS entries (
        id TEXT PRIMARY KEY,
        date TEXT NOT NULL UNIQUE,
        timestamp_created TEXT NOT NULL,
        timestamp_updated TEXT NOT NULL,
        summary_title TEXT,
        summary_description TEXT,
        mood TEXT,
        energy_level INTEGER,
        tags TEXT,
        references_json TEXT,
        raw_json TEXT NOT NULL
    );

    -- Full-text search virtual table
    CREATE VIRTUAL TABLE IF NOT EXISTS entries_fts USING fts5(
        id,
        summary_title,
        summary_description,
        content='entries',
        content_rowid='rowid'
    );

    -- Triggers to keep FTS index in sync
    CREATE TRIGGER IF NOT EXISTS entries_ai AFTER INSERT ON entries BEGIN
        INSERT INTO entries_fts(id, summary_title, summary_description)
        VALUES (new.id, new.summary_title, new.summary_description);
    END;

    CREATE TRIGGER IF NOT EXISTS entries_ad AFTER DELETE ON entries BEGIN
        INSERT INTO entries_fts(entries_fts, rowid, id, summary_title, summary_description)
        VALUES ('delete', old.rowid, old.id, old.summary_title, old.summary_description);
    END;

    CREATE TRIGGER IF NOT EXISTS entries_au AFTER UPDATE ON entries BEGIN
        INSERT INTO entries_fts(entries_fts, rowid, id, summary_title, summary_description)
        VALUES ('delete', old.rowid, old.id, old.summary_title, old.summary_description);
        INSERT INTO entries_fts(id, summary_title, summary_description)
        VALUES (new.id, new.summary_title, new.summary_description);
    END;

    -- Tasks table
    CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        status TEXT NOT NULL,
        priority TEXT NOT NULL,
        project_id TEXT,
        entry_date TEXT NOT NULL,
        created_at TEXT NOT NULL,
        completed_at TEXT,
        estimated_hours REAL,
        actual_hours REAL,
        progress INTEGER DEFAULT 0,
        tags TEXT,
        raw_json TEXT NOT NULL,
        FOREIGN KEY (entry_date) REFERENCES entries(id)
    );

    -- Decisions table
    CREATE TABLE IF NOT EXISTS decisions (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        context TEXT,
        decision TEXT NOT NULL,
        reversibility TEXT,
        status TEXT NOT NULL,
        project_id TEXT,
        created_at TEXT NOT NULL,
        review_date TEXT,
        superseded_by TEXT,
        tags TEXT,
        raw_json TEXT NOT NULL
    );

    -- Blockers table
    CREATE TABLE IF NOT EXISTS blockers (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        severity TEXT NOT NULL,
        impact TEXT NOT NULL,
        escalation_level INTEGER DEFAULT 0,
        status TEXT NOT NULL,
        project_id TEXT,
        assigned_to TEXT,
        created_at TEXT NOT NULL,
        resolved_at TEXT,
        resolution TEXT,
        tags TEXT,
        raw_json TEXT NOT NULL
    );

    -- Projects table
    CREATE TABLE IF NOT EXISTS projects (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        status TEXT NOT NULL,
        priority TEXT NOT NULL,
        created_at TEXT NOT NULL,
        started_at TEXT,
        target_completion TEXT,
        completed_at TEXT,
        color TEXT,
        tags TEXT,
        raw_json TEXT NOT NULL
    );

    -- Tags table
    CREATE TABLE IF NOT EXISTS tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        category TEXT,
        usage_count INTEGER DEFAULT 0
    );

    -- Entry-tag relationships
    CREATE TABLE IF NOT EXISTS entry_tags (
        entry_id TEXT NOT NULL,
        tag_name TEXT NOT NULL,
        PRIMARY KEY (entry_id, tag_name),
        FOREIGN KEY (entry_id) REFERENCES entries(id)
    );

    -- Conversations table
    CREATE TABLE IF NOT EXISTS conversations (
        id TEXT PRIMARY KEY,
        source TEXT NOT NULL,
        summary TEXT,
        timestamp TEXT NOT NULL,
        context_hash TEXT,
        extracted_tasks TEXT,
        extracted_decisions TEXT,
        extracted_blockers TEXT,
        raw_json TEXT NOT NULL
    );

    -- Pending parses table
    CREATE TABLE IF NOT EXISTS pending_parses (
        id TEXT PRIMARY KEY,
        source TEXT NOT NULL,
        raw_text TEXT,
        extracted_data TEXT,
        created_at TEXT NOT NULL,
        approved BOOLEAN DEFAULT 0
    );

    -- Indexes
    CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
    CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project_id);
    CREATE INDEX IF NOT EXISTS idx_decisions_status ON decisions(status);
    CREATE INDEX IF NOT EXISTS idx_blockers_status ON blockers(status);
    CREATE INDEX IF NOT EXISTS idx_blockers_escalation ON blockers(escalation_level);
    CREATE INDEX IF NOT EXISTS idx_entries_date ON entries(date);
    CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
    """
    
    def __init__(self, db_path: str = "data/.memory.db"):
        """Initialize database connection."""
        self.db_path = db_path
        self._ensure_directory()
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.execute("PRAGMA journal_mode = WAL")
        self._init_schema()
    
    def _ensure_directory(self):
        """Ensure database directory exists."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    def _init_schema(self):
        """Initialize database schema."""
        self.conn.executescript(self.SCHEMA)
        self.conn.commit()
    
    def close(self):
        """Close database connection."""
        self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    # Entry operations
    
    def save_entry(self, entry: Entry) -> None:
        """Save or update entry."""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO entries 
            (id, date, timestamp_created, timestamp_updated, summary_title, 
             summary_description, mood, energy_level, tags, references_json, raw_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entry.id,
            entry.date,
            entry.timestamp_created,
            entry.timestamp_updated,
            entry.summary.title,
            entry.summary.description,
            entry.summary.mood,
            entry.summary.energy_level,
            json.dumps(entry.tags),
            json.dumps(entry.references),
            json.dumps(entry.to_dict())
        ))
        
        # Update entry tags
        cursor.execute("DELETE FROM entry_tags WHERE entry_id = ?", (entry.id,))
        for tag in entry.tags:
            cursor.execute("""
                INSERT OR IGNORE INTO tags (name) VALUES (?)
            """, (tag,))
            cursor.execute("""
                INSERT OR REPLACE INTO entry_tags (entry_id, tag_name) VALUES (?, ?)
            """, (entry.id, tag))
        
        # Save related objects
        for task in entry.tasks:
            self.save_task(task)
        for decision in entry.decisions:
            self.save_decision(decision)
        for blocker in entry.blockers:
            self.save_blocker(blocker)
        
        self.conn.commit()
    
    def get_entry(self, date: str) -> Optional[Entry]:
        """Get entry by date."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT raw_json FROM entries WHERE id = ?", (date,))
        row = cursor.fetchone()
        
        if row:
            data = json.loads(row['raw_json'])
            return Entry.from_dict(data)
        return None
    
    def list_entries(self, from_date: Optional[str] = None, 
                     to: Optional[str] = None,
                     project: Optional[str] = None,
                     tags: Optional[List[str]] = None,
                     limit: int = 100) -> List[Entry]:
        """List entries with filters."""
        cursor = self.conn.cursor()
        
        query = "SELECT raw_json FROM entries WHERE 1=1"
        params = []
        
        if from_date:
            query += " AND date >= ?"
            params.append(from_date)
        if to:
            query += " AND date <= ?"
            params.append(to)
        if project:
            query += " AND raw_json LIKE ?"
            params.append(f'%"project_id": "{project}"%')
        
        query += " ORDER BY date DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        entries = [Entry.from_dict(json.loads(row['raw_json'])) for row in rows]
        
        # Filter by tags if specified
        if tags:
            entries = [e for e in entries if any(t in e.tags for t in tags)]
        
        return entries
    
    def delete_entry(self, date: str) -> None:
        """Delete entry and all related data."""
        cursor = self.conn.cursor()
        # Collect IDs of related items before deleting the entry
        entry = self.get_entry(date)
        if entry:
            for decision in entry.decisions:
                cursor.execute("DELETE FROM decisions WHERE id = ?", (decision.id,))
            for blocker in entry.blockers:
                cursor.execute("DELETE FROM blockers WHERE id = ?", (blocker.id,))
        cursor.execute("DELETE FROM tasks WHERE entry_date = ?", (date,))
        cursor.execute("DELETE FROM entry_tags WHERE entry_id = ?", (date,))
        cursor.execute("DELETE FROM entries WHERE id = ?", (date,))
        self.conn.commit()
    
    def link_entries(self, date1: str, date2: str) -> None:
        """Link two entries."""
        entry1 = self.get_entry(date1)
        entry2 = self.get_entry(date2)
        
        if entry1 and entry2:
            if date2 not in entry1.references:
                entry1.references.append(date2)
            if date1 not in entry2.references:
                entry2.references.append(date1)
            
            self.save_entry(entry1)
            self.save_entry(entry2)
    
    # Task operations
    
    def save_task(self, task: Task) -> None:
        """Save or update task."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO tasks 
            (id, title, description, status, priority, project_id, entry_date,
             created_at, completed_at, estimated_hours, actual_hours, progress, tags, raw_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            task.id, task.title, task.description, task.status, task.priority,
            task.project_id, task.entry_date, task.created_at, task.completed_at,
            task.estimated_hours, task.actual_hours, task.progress,
            json.dumps(task.tags), json.dumps(task.to_dict())
        ))
        self.conn.commit()
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT raw_json FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        
        if row:
            return Task.from_dict(json.loads(row['raw_json']))
        return None
    
    def list_tasks(self, status: Optional[str] = None,
                   project: Optional[str] = None,
                   priority: Optional[str] = None,
                   from_date: Optional[str] = None,
                   to: Optional[str] = None,
                   limit: int = 100) -> List[Task]:
        """List tasks with filters."""
        cursor = self.conn.cursor()
        
        query = "SELECT raw_json FROM tasks WHERE 1=1"
        params = []
        
        if status and status != 'all':
            query += " AND status = ?"
            params.append(status)
        if project:
            query += " AND project_id = ?"
            params.append(project)
        if priority:
            query += " AND priority = ?"
            params.append(priority)
        if from_date:
            query += " AND entry_date >= ?"
            params.append(from_date)
        if to:
            query += " AND entry_date <= ?"
            params.append(to)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return [Task.from_dict(json.loads(row['raw_json'])) for row in rows]
    
    def delete_task(self, task_id: str) -> None:
        """Delete task."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self.conn.commit()
    
    # Decision operations
    
    def save_decision(self, decision: Decision) -> None:
        """Save or update decision."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO decisions 
            (id, title, context, decision, reversibility, status, project_id,
             created_at, review_date, superseded_by, tags, raw_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            decision.id, decision.title, decision.context, decision.decision,
            decision.reversibility, decision.status, decision.project_id,
            decision.created_at, decision.review_date, decision.superseded_by,
            json.dumps(decision.tags), json.dumps(decision.to_dict())
        ))
        self.conn.commit()
    
    def get_decision(self, decision_id: str) -> Optional[Decision]:
        """Get decision by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT raw_json FROM decisions WHERE id = ?", (decision_id,))
        row = cursor.fetchone()
        
        if row:
            return Decision.from_dict(json.loads(row['raw_json']))
        return None
    
    def list_decisions(self, project: Optional[str] = None,
                       status: Optional[str] = None,
                       search: Optional[str] = None,
                       limit: int = 100) -> List[Decision]:
        """List decisions with filters."""
        cursor = self.conn.cursor()
        
        query = "SELECT raw_json FROM decisions WHERE 1=1"
        params = []
        
        if project:
            query += " AND project_id = ?"
            params.append(project)
        if status and status != 'all':
            query += " AND status = ?"
            params.append(status)
        if search:
            query += " AND (title LIKE ? OR context LIKE ? OR decision LIKE ?)"
            params.extend([f'%{search}%'] * 3)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return [Decision.from_dict(json.loads(row['raw_json'])) for row in rows]
    
    def supersede_decision(self, old_id: str, new_id: str, reason: str) -> None:
        """Mark decision as superseded."""
        old_decision = self.get_decision(old_id)
        if old_decision:
            old_decision.supersede(new_id)
            self.save_decision(old_decision)
    
    def get_decisions_for_review(self, days: int = 30) -> List[Decision]:
        """Get decisions due for review."""
        cursor = self.conn.cursor()
        
        from datetime import timedelta
        future_date = (datetime.now() + timedelta(days=days)).isoformat()
        
        cursor.execute("""
            SELECT raw_json FROM decisions 
            WHERE review_date <= ? AND status = 'active'
            ORDER BY review_date ASC
        """, (future_date,))
        
        rows = cursor.fetchall()
        return [Decision.from_dict(json.loads(row['raw_json'])) for row in rows]
    
    # Blocker operations
    
    def save_blocker(self, blocker: Blocker) -> None:
        """Save or update blocker."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO blockers 
            (id, title, description, severity, impact, escalation_level, status,
             project_id, assigned_to, created_at, resolved_at, resolution, tags, raw_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            blocker.id, blocker.title, blocker.description, blocker.severity,
            blocker.impact, blocker.escalation_level, blocker.status,
            blocker.project_id, blocker.assigned_to, blocker.created_at,
            blocker.resolved_at, blocker.resolution, json.dumps(blocker.tags),
            json.dumps(blocker.to_dict())
        ))
        self.conn.commit()
    
    def get_blocker(self, blocker_id: str) -> Optional[Blocker]:
        """Get blocker by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT raw_json FROM blockers WHERE id = ?", (blocker_id,))
        row = cursor.fetchone()
        
        if row:
            return Blocker.from_dict(json.loads(row['raw_json']))
        return None
    
    def list_blockers(self, status: Optional[str] = None,
                      severity: Optional[str] = None,
                      escalation_level: Optional[int] = None,
                      project: Optional[str] = None,
                      limit: int = 100) -> List[Blocker]:
        """List blockers with filters."""
        cursor = self.conn.cursor()
        
        query = "SELECT raw_json FROM blockers WHERE 1=1"
        params = []
        
        if status and status != 'all':
            query += " AND status = ?"
            params.append(status)
        if severity:
            query += " AND severity = ?"
            params.append(severity)
        if escalation_level is not None:
            query += " AND escalation_level = ?"
            params.append(escalation_level)
        if project:
            query += " AND project_id = ?"
            params.append(project)
        
        query += " ORDER BY escalation_level DESC, created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return [Blocker.from_dict(json.loads(row['raw_json'])) for row in rows]
    
    def get_escalated_blockers(self, min_level: int = 2) -> List[Blocker]:
        """Get blockers at or above escalation level."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT raw_json FROM blockers 
            WHERE escalation_level >= ? AND status = 'active'
            ORDER BY escalation_level DESC
        """, (min_level,))
        
        rows = cursor.fetchall()
        return [Blocker.from_dict(json.loads(row['raw_json'])) for row in rows]
    
    def check_auto_escalations(self) -> List[Blocker]:
        """Check and auto-escalate blockers."""
        blockers = self.list_blockers(status='active')
        escalated = []
        
        for blocker in blockers:
            if blocker.should_auto_escalate():
                blocker.escalate(reason="Auto-escalated after timeout")
                self.save_blocker(blocker)
                escalated.append(blocker)
        
        return escalated
    
    # Project operations
    
    def save_project(self, project: Project) -> None:
        """Save or update project."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO projects 
            (id, name, description, status, priority, created_at, started_at,
             target_completion, completed_at, color, tags, raw_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            project.id, project.name, project.description, project.status,
            project.priority, project.created_at, project.started_at,
            project.target_completion, project.completed_at, project.color,
            json.dumps(project.tags), json.dumps(project.to_dict())
        ))
        self.conn.commit()
    
    def get_project(self, project_id: str) -> Optional[Project]:
        """Get project by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT raw_json FROM projects WHERE id = ?", (project_id,))
        row = cursor.fetchone()
        
        if row:
            return Project.from_dict(json.loads(row['raw_json']))
        return None
    
    def list_projects(self, status: Optional[str] = None,
                      limit: int = 100) -> List[Project]:
        """List projects with filters."""
        cursor = self.conn.cursor()
        
        query = "SELECT raw_json FROM projects WHERE 1=1"
        params = []
        
        if status and status != 'all':
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return [Project.from_dict(json.loads(row['raw_json'])) for row in rows]
    
    def delete_project(self, project_id: str) -> None:
        """Delete project."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        self.conn.commit()
    
    # Search operations
    
    def search_entries_fts(self, query: str, limit: int = 20) -> List[Dict]:
        """Search entries using full-text search."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT e.raw_json, rank 
            FROM entries_fts f
            JOIN entries e ON e.id = f.id
            WHERE entries_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (query, limit))
        
        return [json.loads(row['raw_json']) for row in cursor.fetchall()]
    
    # Stats
    
    def get_stats(self) -> Dict[str, int]:
        """Get system statistics."""
        cursor = self.conn.cursor()
        
        stats = {}
        
        cursor.execute("SELECT COUNT(*) FROM entries")
        stats['total_entries'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status IN ('pending', 'in_progress')")
        stats['active_tasks'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'completed'")
        stats['completed_tasks'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM decisions WHERE status = 'active'")
        stats['active_decisions'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM blockers WHERE status = 'active'")
        stats['active_blockers'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM projects")
        stats['total_projects'] = cursor.fetchone()[0]
        
        return stats
    
    # Pending parses (for approval workflow)
    
    def save_pending_parse(self, parse_id: str, source: str, raw_text: str, 
                          extracted_data: Dict) -> None:
        """Save pending parse for approval."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO pending_parses (id, source, raw_text, extracted_data, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (parse_id, source, raw_text, json.dumps(extracted_data), 
              datetime.now().isoformat()))
        self.conn.commit()
    
    def get_pending_parses(self) -> List[Dict]:
        """Get pending parses."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM pending_parses WHERE approved = 0 ORDER BY created_at DESC
        """)
        return [dict(row) for row in cursor.fetchall()]
    
    def approve_parse(self, parse_id: str) -> None:
        """Approve a pending parse."""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE pending_parses SET approved = 1 WHERE id = ?
        """, (parse_id,))
        self.conn.commit()
