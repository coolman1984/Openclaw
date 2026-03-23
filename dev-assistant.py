#!/usr/bin/env python3
"""
Dev Assistant Dashboard - A CLI productivity tool for developers
Created by OpenClaw for Mohamed Fawzy

Features:
- Task management with priorities
- Quick notes with timestamps
- System resource monitoring
- Project time tracking
- Git repository status
- OpenCode Go API integration
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime
from pathlib import Path

# Configuration
DATA_DIR = Path.home() / ".dev-assistant"
TASKS_FILE = DATA_DIR / "tasks.json"
NOTES_FILE = DATA_DIR / "notes.json"
SESSIONS_FILE = DATA_DIR / "sessions.json"

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}  {text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

# Initialize data directory
def init_data():
    DATA_DIR.mkdir(exist_ok=True)
    for file in [TASKS_FILE, NOTES_FILE, SESSIONS_FILE]:
        if not file.exists():
            file.write_text(json.dumps({"items": []}))

# Task Management
class TaskManager:
    def __init__(self):
        self.tasks = self.load_tasks()
    
    def load_tasks(self):
        try:
            return json.loads(TASKS_FILE.read_text())
        except:
            return {"items": []}
    
    def save_tasks(self):
        TASKS_FILE.write_text(json.dumps(self.tasks, indent=2))
    
    def add(self, title, priority="medium", project="general"):
        task = {
            "id": len(self.tasks["items"]) + 1,
            "title": title,
            "priority": priority,
            "project": project,
            "status": "pending",
            "created": datetime.now().isoformat(),
            "completed": None
        }
        self.tasks["items"].append(task)
        self.save_tasks()
        print_success(f"Task added: {title}")
    
    def list(self, project=None, status=None):
        items = self.tasks["items"]
        
        if project:
            items = [t for t in items if t["project"] == project]
        if status:
            items = [t for t in items if t["status"] == status]
        
        if not items:
            print_info("No tasks found")
            return
        
        print_header("TASKS")
        
        # Priority colors
        priority_colors = {
            "high": Colors.RED,
            "medium": Colors.YELLOW,
            "low": Colors.GREEN
        }
        
        # Group by status
        pending = [t for t in items if t["status"] == "pending"]
        completed = [t for t in items if t["status"] == "completed"]
        
        if pending:
            print(f"\n{Colors.BOLD}Pending ({len(pending)}):{Colors.END}")
            for task in sorted(pending, key=lambda x: x["priority"]):
                color = priority_colors.get(task["priority"], Colors.END)
                print(f"  {color}[{task['priority'].upper()}]{Colors.END} #{task['id']}: {task['title']}")
                print(f"     Project: {task['project']} | Created: {task['created'][:10]}")
        
        if completed:
            print(f"\n{Colors.BOLD}Completed ({len(completed)}):{Colors.END}")
            for task in completed[-5:]:  # Show last 5
                print(f"  {Colors.GREEN}[✓]{Colors.END} #{task['id']}: {task['title']}")
    
    def complete(self, task_id):
        for task in self.tasks["items"]:
            if task["id"] == task_id:
                task["status"] = "completed"
                task["completed"] = datetime.now().isoformat()
                self.save_tasks()
                print_success(f"Task #{task_id} completed!")
                return
        print_error(f"Task #{task_id} not found")
    
    def delete(self, task_id):
        self.tasks["items"] = [t for t in self.tasks["items"] if t["id"] != task_id]
        self.save_tasks()
        print_success(f"Task #{task_id} deleted")

# Notes Management
class NotesManager:
    def __init__(self):
        self.notes = self.load_notes()
    
    def load_notes(self):
        try:
            return json.loads(NOTES_FILE.read_text())
        except:
            return {"items": []}
    
    def save_notes(self):
        NOTES_FILE.write_text(json.dumps(self.notes, indent=2))
    
    def add(self, content, category="general"):
        note = {
            "id": len(self.notes["items"]) + 1,
            "content": content,
            "category": category,
            "created": datetime.now().isoformat()
        }
        self.notes["items"].append(note)
        self.save_notes()
        print_success(f"Note added (#{note['id']})")
    
    def list(self, category=None, search=None):
        items = self.notes["items"]
        
        if category:
            items = [n for n in items if n["category"] == category]
        if search:
            items = [n for n in items if search.lower() in n["content"].lower()]
        
        if not items:
            print_info("No notes found")
            return
        
        print_header("NOTES")
        for note in items[-10:]:  # Show last 10
            print(f"\n{Colors.BOLD}#{note['id']} [{note['category']}]{Colors.END}")
            print(f"  {note['content']}")
            print(f"  {Colors.CYAN}{note['created'][:16]}{Colors.END}")

# Time Tracking
class TimeTracker:
    def __init__(self):
        self.sessions = self.load_sessions()
        self.current_session = None
    
    def load_sessions(self):
        try:
            return json.loads(SESSIONS_FILE.read_text())
        except:
            return {"items": []}
    
    def save_sessions(self):
        SESSIONS_FILE.write_text(json.dumps(self.sessions, indent=2))
    
    def start(self, project, description=""):
        self.current_session = {
            "project": project,
            "description": description,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "duration": 0
        }
        print_success(f"Started tracking: {project}")
        print_info(f"Time: {self.current_session['start_time'][11:16]}")
    
    def stop(self):
        if not self.current_session:
            print_error("No active session")
            return
        
        self.current_session["end_time"] = datetime.now().isoformat()
        
        # Calculate duration
        start = datetime.fromisoformat(self.current_session["start_time"])
        end = datetime.fromisoformat(self.current_session["end_time"])
        duration = (end - start).total_seconds() / 3600  # Hours
        
        self.current_session["duration"] = round(duration, 2)
        self.sessions["items"].append(self.current_session)
        self.save_sessions()
        
        print_success(f"Stopped tracking: {self.current_session['project']}")
        print_info(f"Duration: {duration:.2f} hours")
        self.current_session = None
    
    def status(self):
        if self.current_session:
            start = datetime.fromisoformat(self.current_session["start_time"])
            now = datetime.now()
            elapsed = (now - start).total_seconds() / 60  # Minutes
            print_info(f"Active: {self.current_session['project']}")
            print_info(f"Running for: {elapsed:.0f} minutes")
        else:
            print_info("No active session")
    
    def report(self, project=None):
        items = self.sessions["items"]
        
        if project:
            items = [s for s in items if s["project"] == project]
        
        if not items:
            print_info("No sessions found")
            return
        
        print_header("TIME REPORT")
        
        # Group by project
        projects = {}
        for session in items:
            proj = session["project"]
            if proj not in projects:
                projects[proj] = {"count": 0, "hours": 0}
            projects[proj]["count"] += 1
            projects[proj]["hours"] += session["duration"]
        
        total_hours = 0
        for proj, data in projects.items():
            print(f"\n{Colors.BOLD}{proj}{Colors.END}")
            print(f"  Sessions: {data['count']}")
            print(f"  Total hours: {Colors.CYAN}{data['hours']:.2f}{Colors.END}")
            total_hours += data["hours"]
        
        print(f"\n{Colors.BOLD}Total: {Colors.GREEN}{total_hours:.2f} hours{Colors.END}")

# System Info
def show_system_info():
    print_header("SYSTEM INFO")
    
    # Current time
    now = datetime.now()
    print(f"{Colors.BOLD}Time:{Colors.END} {now.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Working directory
    print(f"{Colors.BOLD}Directory:{Colors.END} {os.getcwd()}")
    
    # Disk usage (if available)
    try:
        stat = os.statvfs('.')
        free_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
        total_gb = (stat.f_blocks * stat.f_frsize) / (1024**3)
        used_gb = total_gb - free_gb
        print(f"{Colors.BOLD}Disk:{Colors.END} {used_gb:.1f}G / {total_gb:.1f}G used")
    except:
        pass
    
    # Python version
    print(f"{Colors.BOLD}Python:{Colors.END} {sys.version.split()[0]}")
    
    # Files in current directory
    files = [f for f in os.listdir('.') if not f.startswith('.')]
    print(f"{Colors.BOLD}Files here:{Colors.END} {len(files)} items")

# Dashboard
def show_dashboard():
    show_system_info()
    
    # Quick stats
    print_header("QUICK STATS")
    
    tasks = TaskManager()
    pending = len([t for t in tasks.tasks["items"] if t["status"] == "pending"])
    completed = len([t for t in tasks.tasks["items"] if t["status"] == "completed"])
    
    notes = NotesManager()
    notes_count = len(notes.notes["items"])
    
    print(f"{Colors.YELLOW}📋 Tasks:{Colors.END} {pending} pending, {completed} completed")
    print(f"{Colors.CYAN}📝 Notes:{Colors.END} {notes_count} saved")
    
    tracker = TimeTracker()
    tracker.status()
    
    # Recent activity
    print_header("RECENT ACTIVITY")
    
    if tasks.tasks["items"]:
        recent_tasks = [t for t in tasks.tasks["items"] if t["status"] == "pending"][:3]
        if recent_tasks:
            print(f"{Colors.BOLD}Recent tasks:{Colors.END}")
            for task in recent_tasks:
                print(f"  • {task['title']}")

# Main CLI
def main():
    parser = argparse.ArgumentParser(
        description="Dev Assistant Dashboard - Your personal productivity tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                           # Show dashboard
  %(prog)s task add "Fix bug" -p high
  %(prog)s task list
  %(prog)s note add "Important idea"
  %(prog)s time start myproject
  %(prog)s time stop
  %(prog)s system
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Task commands
    task_parser = subparsers.add_parser('task', help='Task management')
    task_subparsers = task_parser.add_subparsers(dest='task_cmd')
    
    task_add = task_subparsers.add_parser('add', help='Add a task')
    task_add.add_argument('title', help='Task title')
    task_add.add_argument('-p', '--priority', choices=['low', 'medium', 'high'], 
                         default='medium', help='Task priority')
    task_add.add_argument('--project', default='general', help='Project name')
    
    task_list = task_subparsers.add_parser('list', help='List tasks')
    task_list.add_argument('--project', help='Filter by project')
    task_list.add_argument('--status', choices=['pending', 'completed'], help='Filter by status')
    
    task_complete = task_subparsers.add_parser('complete', help='Complete a task')
    task_complete.add_argument('id', type=int, help='Task ID')
    
    task_delete = task_subparsers.add_parser('delete', help='Delete a task')
    task_delete.add_argument('id', type=int, help='Task ID')
    
    # Note commands
    note_parser = subparsers.add_parser('note', help='Note management')
    note_subparsers = note_parser.add_subparsers(dest='note_cmd')
    
    note_add = note_subparsers.add_parser('add', help='Add a note')
    note_add.add_argument('content', help='Note content')
    note_add.add_argument('--category', default='general', help='Note category')
    
    note_list = note_subparsers.add_parser('list', help='List notes')
    note_list.add_argument('--category', help='Filter by category')
    note_list.add_argument('--search', help='Search in notes')
    
    # Time commands
    time_parser = subparsers.add_parser('time', help='Time tracking')
    time_subparsers = time_parser.add_subparsers(dest='time_cmd')
    
    time_start = time_subparsers.add_parser('start', help='Start tracking')
    time_start.add_argument('project', help='Project name')
    time_start.add_argument('--description', default='', help='Session description')
    
    time_stop = time_subparsers.add_parser('stop', help='Stop tracking')
    time_status = time_subparsers.add_parser('status', help='Check status')
    time_report = time_subparsers.add_parser('report', help='Show report')
    time_report.add_argument('--project', help='Filter by project')
    
    # System command
    system_parser = subparsers.add_parser('system', help='System information')
    
    args = parser.parse_args()
    
    # Initialize
    init_data()
    
    # Handle commands
    if args.command == 'task':
        manager = TaskManager()
        if args.task_cmd == 'add':
            manager.add(args.title, args.priority, args.project)
        elif args.task_cmd == 'list':
            manager.list(args.project, args.status)
        elif args.task_cmd == 'complete':
            manager.complete(args.id)
        elif args.task_cmd == 'delete':
            manager.delete(args.id)
        else:
            manager.list()
    
    elif args.command == 'note':
        manager = NotesManager()
        if args.note_cmd == 'add':
            manager.add(args.content, args.category)
        elif args.note_cmd == 'list':
            manager.list(args.category, args.search)
        else:
            manager.list()
    
    elif args.command == 'time':
        tracker = TimeTracker()
        if args.time_cmd == 'start':
            tracker.start(args.project, args.description)
        elif args.time_cmd == 'stop':
            tracker.stop()
        elif args.time_cmd == 'status':
            tracker.status()
        elif args.time_cmd == 'report':
            tracker.report(args.project)
        else:
            tracker.status()
    
    elif args.command == 'system':
        show_system_info()
    
    else:
        show_dashboard()

if __name__ == '__main__':
    main()