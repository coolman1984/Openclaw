"""
Sync Manager - Bidirectional sync between JSON files and SQLite database
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime

from database import Database
from config import Config
from models import Entry, Task, Decision, Blocker, Project


class SyncManager:
    """Manage bidirectional sync between JSON files and database."""
    
    def __init__(self, database: Database, config: Config):
        self.db = database
        self.config = config
    
    def full_sync(self) -> Dict[str, int]:
        """Perform full bidirectional sync."""
        stats = {
            'entries_imported': 0,
            'entries_exported': 0,
            'tasks_imported': 0,
            'decisions_imported': 0,
            'blockers_imported': 0,
            'projects_imported': 0
        }
        
        # First: JSON to DB (to pick up file changes)
        json_stats = self.json_to_db()
        stats.update(json_stats)
        
        # Then: DB to JSON (to write any DB-only changes)
        db_stats = self.db_to_json()
        stats['entries_exported'] = db_stats.get('entries', 0)
        
        return stats
    
    def json_to_db(self, force: bool = False) -> Dict[str, int]:
        """Sync JSON files to database."""
        stats = {'entries': 0, 'tasks': 0, 'decisions': 0, 'blockers': 0, 'projects': 0}
        
        # Sync entries
        entries_dir = Path(self.config.get('paths.entries', 'data/entries/'))
        if entries_dir.exists():
            for json_file in entries_dir.glob('*.json'):
                try:
                    with open(json_file) as f:
                        data = json.load(f)
                    
                    entry = Entry.from_dict(data)
                    
                    # Check if entry exists and needs updating
                    existing = self.db.get_entry(entry.date)
                    if not existing or force or entry.timestamp_updated > existing.timestamp_updated:
                        self.db.save_entry(entry)
                        stats['entries'] += 1
                        
                        # Count related items
                        stats['tasks'] += len(entry.tasks)
                        stats['decisions'] += len(entry.decisions)
                        stats['blockers'] += len(entry.blockers)
                        
                except Exception as e:
                    print(f"Warning: Failed to sync {json_file}: {e}")
        
        # Sync projects
        projects_dir = Path(self.config.get('paths.projects', 'data/projects/'))
        if projects_dir.exists():
            for json_file in projects_dir.glob('*.json'):
                try:
                    with open(json_file) as f:
                        data = json.load(f)
                    
                    project = Project.from_dict(data)
                    existing = self.db.get_project(project.id)
                    
                    if not existing or force:
                        self.db.save_project(project)
                        stats['projects'] += 1
                        
                except Exception as e:
                    print(f"Warning: Failed to sync {json_file}: {e}")
        
        return stats
    
    def db_to_json(self, force: bool = False) -> Dict[str, int]:
        """Sync database to JSON files."""
        stats = {'entries': 0, 'projects': 0}
        
        # Export entries
        entries = self.db.list_entries(limit=10000)
        entries_dir = Path(self.config.get('paths.entries', 'data/entries/'))
        entries_dir.mkdir(parents=True, exist_ok=True)
        
        for entry in entries:
            json_file = entries_dir / f"{entry.date}.json"
            
            # Check if file needs updating
            needs_write = force
            if not needs_write and json_file.exists():
                try:
                    with open(json_file) as f:
                        existing = json.load(f)
                    if existing.get('timestamp_updated') != entry.timestamp_updated:
                        needs_write = True
                except:
                    needs_write = True
            else:
                needs_write = True
            
            if needs_write:
                with open(json_file, 'w') as f:
                    json.dump(entry.to_dict(), f, indent=2)
                stats['entries'] += 1
        
        # Export projects
        projects = self.db.list_projects(limit=1000)
        projects_dir = Path(self.config.get('paths.projects', 'data/projects/'))
        projects_dir.mkdir(parents=True, exist_ok=True)
        
        for project in projects:
            json_file = projects_dir / f"{project.id}.json"
            
            with open(json_file, 'w') as f:
                json.dump(project.to_dict(), f, indent=2)
            stats['projects'] += 1
        
        # Generate markdown logs
        self._generate_markdown_logs(entries)
        
        return stats
    
    def _generate_markdown_logs(self, entries: List[Entry]) -> None:
        """Generate human-readable markdown logs from entries."""
        logs_dir = Path(self.config.get('paths.logs', 'data/logs/'))
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        for entry in entries:
            md_file = logs_dir / f"{entry.date}.md"
            
            with open(md_file, 'w') as f:
                f.write(entry.to_markdown())
    
    def verify(self) -> List[str]:
        """Verify integrity of data."""
        issues = []
        
        # Check for orphaned tasks
        tasks = self.db.list_tasks(limit=10000)
        for task in tasks:
            if task.entry_date:
                entry = self.db.get_entry(task.entry_date)
                if not entry:
                    issues.append(f"Orphaned task {task.id} references missing entry {task.entry_date}")
        
        # Check for orphaned decisions
        decisions = self.db.list_decisions(limit=1000)
        for decision in decisions:
            if decision.project_id:
                project = self.db.get_project(decision.project_id)
                if not project:
                    issues.append(f"Orphaned decision {decision.id} references missing project {decision.project_id}")
        
        # Check for orphaned blockers
        blockers = self.db.list_blockers(limit=1000)
        for blocker in blockers:
            if blocker.project_id:
                project = self.db.get_project(blocker.project_id)
                if not project:
                    issues.append(f"Orphaned blocker {blocker.id} references missing project {blocker.project_id}")
        
        # Check for missing JSON files
        entries = self.db.list_entries(limit=10000)
        entries_dir = Path(self.config.get('paths.entries', 'data/entries/'))
        
        for entry in entries:
            json_file = entries_dir / f"{entry.date}.json"
            if not json_file.exists():
                issues.append(f"Missing JSON file for entry {entry.date}")
        
        return issues
    
    def fix_issues(self, issues: List[str]) -> None:
        """Auto-fix integrity issues."""
        for issue in issues:
            if "Orphaned task" in issue:
                import re
                match = re.search(r'task_\w+', issue)
                if match:
                    self.db.delete_task(match.group())
            
            elif "Orphaned decision" in issue:
                import re
                match = re.search(r'decision_\w+', issue)
                if match:
                    self.db.delete_decision(match.group())
            
            elif "Orphaned blocker" in issue:
                import re
                match = re.search(r'blocker_\w+', issue)
                if match:
                    self.db.delete_blocker(match.group())
            
            elif "Missing JSON file" in issue:
                # Re-export entry
                match = re.search(r'entry (\d{4}-\d{2}-\d{2})', issue)
                if match:
                    entry = self.db.get_entry(match.group(1))
                    if entry:
                        entries_dir = Path(self.config.get('paths.entries', 'data/entries/'))
                        json_file = entries_dir / f"{entry.date}.json"
                        with open(json_file, 'w') as f:
                            json.dump(entry.to_dict(), f, indent=2)


class BackupManager:
    """Manage database backups."""
    
    def __init__(self, config: Config):
        self.config = config
        self.backup_dir = Path(config.get('database.backup_path', 'backups/'))
    
    def create_backup(self) -> str:
        """Create database backup."""
        import shutil
        from datetime import datetime
        
        db_path = Path(self.config.get('database.path', 'data/.memory.db'))
        if not db_path.exists():
            raise FileNotFoundError("Database not found")
        
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = self.backup_dir / f"memory_backup_{timestamp}.db"
        
        shutil.copy2(db_path, backup_file)
        
        return str(backup_file)
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List available backups."""
        if not self.backup_dir.exists():
            return []
        
        backups = []
        for backup_file in self.backup_dir.glob('memory_backup_*.db'):
            stat = backup_file.stat()
            backups.append({
                'file': str(backup_file),
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        return sorted(backups, key=lambda x: x['created'], reverse=True)
    
    def restore_backup(self, backup_file: str) -> None:
        """Restore database from backup."""
        import shutil
        
        db_path = Path(self.config.get('database.path', 'data/.memory.db'))
        backup_path = Path(backup_file)
        
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_file}")
        
        # Create safety backup of current database
        if db_path.exists():
            safety_backup = self.backup_dir / f"memory_safety_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy2(db_path, safety_backup)
        
        # Restore
        shutil.copy2(backup_path, db_path)
    
    def cleanup_old_backups(self, keep_days: int = 30) -> int:
        """Remove old backups."""
        from datetime import datetime, timedelta
        
        if not self.backup_dir.exists():
            return 0
        
        cutoff = datetime.now() - timedelta(days=keep_days)
        removed = 0
        
        for backup_file in self.backup_dir.glob('memory_backup_*.db'):
            stat = backup_file.stat()
            created = datetime.fromtimestamp(stat.st_mtime)
            
            if created < cutoff:
                backup_file.unlink()
                removed += 1
        
        return removed
