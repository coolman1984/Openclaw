#!/usr/bin/env python3
"""Memory Manager v3

A modular, v3-oriented entry point for the OpenClaw memory system.
Uses the existing database, dashboard, report, sync, backup, and auto-entry modules.
"""

from __future__ import annotations

import argparse
import os
import sys
import tarfile
from datetime import datetime
from pathlib import Path
from typing import List, Optional

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "integrations") not in sys.path:
    sys.path.insert(0, str(ROOT / "integrations"))

from config import Config
from database import Database
from models import Entry, Task, Decision, Blocker, Note, Summary
from reports import ReportGenerator
from search import SearchEngine, QueryParser
from sync import SyncManager, BackupManager
from views import DashboardUpdater
from integrations.conversation_parser import ConversationParser, ConversationValidator
from integrations.auto_entry import AutoEntryGenerator
from setup import initialize_system
from utils import (
    Colors,
    confirm,
    print_error,
    print_header,
    print_info,
    print_success,
    print_warning,
    table,
    truncate,
)

SCHEMA_VERSION = "v3"


def runtime():
    config = Config()
    config.ensure_directories()
    db = Database(config.database_path)
    return config, db


def split_csv(value: str) -> List[str]:
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]


def prompt(text: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    value = input(f"{text}{suffix}: ").strip()
    return value or default


def interactive_entry(db: Database) -> Entry:
    print_header("Create Memory Entry (v3)")

    date = prompt("Date", datetime.now().strftime("%Y-%m-%d"))
    title = prompt("Title", "Untitled session")
    description = prompt("Description", "")
    mood = prompt("Mood", "")
    energy = prompt("Energy level 0-10", "5")
    tags = split_csv(prompt("Tags (comma-separated)", ""))
    refs = split_csv(prompt("References (comma-separated)", ""))

    entry = Entry.create(date=date, title=title)
    entry.summary.description = description
    entry.summary.mood = mood
    try:
        entry.summary.energy_level = int(energy)
    except ValueError:
        entry.summary.energy_level = 5
    entry.tags = tags
    entry.references = refs

    print_info("Add tasks, decisions, blockers, and notes. Leave title blank to finish.")

    while True:
        task_title = prompt("Task title", "")
        if not task_title:
            break
        task = Task.create(
            title=task_title,
            description=prompt("Task description", ""),
            priority=prompt("Task priority (low/medium/high/critical)", "medium"),
            project_id=prompt("Project ID", ""),
            tags=split_csv(prompt("Task tags", "")),
        )
        task.start()
        entry.add_task(task)

    while True:
        decision_title = prompt("Decision title", "")
        if not decision_title:
            break
        decision = Decision.create(
            title=decision_title,
            context=prompt("Decision context", ""),
            decision=prompt("Chosen decision", ""),
            rationale=prompt("Rationale", ""),
            project_id=prompt("Project ID", ""),
            reversibility=prompt("Reversibility (low/medium/high)", "medium"),
            tags=split_csv(prompt("Decision tags", "")),
        )
        entry.add_decision(decision)

    while True:
        blocker_title = prompt("Blocker title", "")
        if not blocker_title:
            break
        blocker = Blocker.create(
            title=blocker_title,
            description=prompt("Blocker description", ""),
            severity=prompt("Severity (low/medium/high/critical)", "medium"),
            impact=prompt("Impact (minor/moderate/blocking/critical)", "blocking"),
            project_id=prompt("Project ID", ""),
            assigned_to=prompt("Assigned to", ""),
            tags=split_csv(prompt("Blocker tags", "")),
        )
        entry.add_blocker(blocker)

    while True:
        note_content = prompt("Note content", "")
        if not note_content:
            break
        entry.notes.append(Note.create(note_content, category=prompt("Note category", "general")))

    db.save_entry(entry)
    return entry


def cmd_init(args):
    initialize_system(force=args.force)


def cmd_entry_add(args):
    config, db = runtime()
    try:
        entry = interactive_entry(db)
        print_success(f"Saved entry for {entry.date} ({entry.summary.title})")
    finally:
        db.close()


def cmd_entry_list(args):
    config, db = runtime()
    try:
        entries = db.list_entries(
            from_date=args.from_date,
            to=args.to,
            project=args.project,
            tags=split_csv(args.tags) if args.tags else None,
            limit=args.limit,
        )
        if not entries:
            print_warning("No entries found.")
            return
        rows = []
        for e in entries:
            rows.append([
                e.date,
                truncate(e.summary.title, 36),
                str(len(e.tasks)),
                str(len(e.decisions)),
                str(len(e.blockers)),
                ", ".join(e.tags[:3]) if e.tags else "",
            ])
        print(table(rows, headers=["Date", "Title", "Tasks", "Decisions", "Blockers", "Tags"]))
    finally:
        db.close()


def cmd_dashboard(args):
    config, db = runtime()
    try:
        updater = DashboardUpdater(db)
        path = updater.generate_memory_md(output_path=args.output or "MEMORY.md")
        updater.update_all()
        stats = db.get_stats()
        print_success(f"Dashboard written to {path}")
        print_header("Memory v3 Dashboard")
        print(table([
            ["Schema", SCHEMA_VERSION],
            ["Entries", str(stats['total_entries'])],
            ["Active Tasks", str(stats['active_tasks'])],
            ["Completed Tasks", str(stats['completed_tasks'])],
            ["Active Decisions", str(stats['active_decisions'])],
            ["Active Blockers", str(stats['active_blockers'])],
            ["Projects", str(stats['total_projects'])],
        ], headers=["Metric", "Value"]))
    finally:
        db.close()


def cmd_search(args):
    config, db = runtime()
    try:
        engine = SearchEngine(db)
        query = args.query
        if args.advanced:
            parsed = QueryParser.parse(query)
            print_info(f"Parsed query: {parsed}")
        results = engine.search(
            query=query,
            type=args.type,
            project=args.project,
            from_date=args.from_date,
            to=args.to,
            tags=split_csv(args.tags) if args.tags else None,
            limit=args.limit,
            advanced=args.advanced,
        )
        engine.print_results(results)
    finally:
        db.close()


def _write_report(output: Optional[str], content: str) -> None:
    if output:
        out = ROOT / output
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content)
        print_success(f"Wrote report to {out}")
    else:
        print(content)


def cmd_report(args):
    config, db = runtime()
    try:
        generator = ReportGenerator(db)
        if args.kind == "daily":
            content = generator.daily_report(args.date)
        elif args.kind == "weekly":
            content = generator.weekly_report(args.week, args.year)
        elif args.kind == "project":
            if not args.project:
                raise SystemExit("--project is required for project reports")
            content = generator.project_report(args.project, args.from_date, args.to)
        elif args.kind == "blockers":
            content = generator.blockers_report(escalated_only=args.escalated)
        elif args.kind == "decisions":
            content = generator.decisions_report(review_due=args.review_due)
        else:
            raise SystemExit(f"Unknown report kind: {args.kind}")
        _write_report(args.output, content)
    finally:
        db.close()


def _create_snapshot(include_code: bool = False, name: Optional[str] = None) -> Path:
    backup_dir = ROOT / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    label = name or f"memory_v3_{timestamp}"
    archive = backup_dir / f"{label}.tar.gz"

    with tarfile.open(archive, "w:gz") as tar:
        paths = [
            "data",
            "reports",
            "templates",
            "memory-config.json",
            "MEMORY.md",
        ]
        if include_code:
            paths.extend([
                "models.py",
                "database.py",
                "config.py",
                "views.py",
                "reports.py",
                "search.py",
                "sync.py",
                "setup.py",
                "utils.py",
                "integrations",
            ])
        for rel in paths:
            p = ROOT / rel
            if p.exists():
                tar.add(p, arcname=rel)
    return archive


def cmd_backup(args):
    config, db = runtime()
    try:
        if args.action == "create":
            archive = _create_snapshot(include_code=args.include_code, name=args.name)
            print_success(f"Created backup: {archive}")
        elif args.action == "list":
            backups = sorted((ROOT / "backups").glob("*.tar.gz"), key=lambda p: p.stat().st_mtime, reverse=True)
            if not backups:
                print_warning("No backups found.")
                return
            rows = []
            for b in backups[:20]:
                stat = b.stat()
                rows.append([b.name, str(stat.st_size), datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")])
            print(table(rows, headers=["File", "Size", "Modified"]))
        else:
            raise SystemExit(f"Unknown backup action: {args.action}")
    finally:
        db.close()


def _safe_tar_extractall(archive: tarfile.TarFile, dest: Path) -> None:
    """Extract tar archive safely, rejecting path traversal attempts."""
    dest = dest.resolve()
    for member in archive.getmembers():
        member_path = (dest / member.name).resolve()
        if not str(member_path).startswith(str(dest) + os.sep) and member_path != dest:
            raise SystemExit(f"Refusing to extract {member.name}: path traversal detected")
        if member.issym() or member.islnk():
            link_target = (dest / member.linkname).resolve()
            if not str(link_target).startswith(str(dest) + os.sep):
                raise SystemExit(f"Refusing to extract symlink {member.name}: target outside dest")
    archive.extractall(dest, filter="data" if hasattr(tarfile, "data_filter") else None)


def cmd_restore(args):
    config, db = runtime()
    try:
        archive = Path(args.path)
        if not archive.is_absolute():
            archive = ROOT / archive
        if not archive.exists():
            raise SystemExit(f"Backup not found: {archive}")
        if not args.yes and not confirm(f"Restore from {archive.name}? This will overwrite files."):
            return
        with tarfile.open(archive, "r:gz") as tar:
            _safe_tar_extractall(tar, ROOT)
        print_success(f"Restored snapshot from {archive}")
    finally:
        db.close()


def cmd_validate(args):
    config, db = runtime()
    try:
        sync = SyncManager(db, config)
        issues = sync.verify()
        if not issues:
            print_success("Integrity check passed. No issues found.")
            return
        print_warning(f"Found {len(issues)} issue(s):")
        for issue in issues:
            print(f" - {issue}")
        if args.fix and confirm("Try to auto-fix issues?"):
            sync.fix_issues(issues)
            print_success("Auto-fix pass completed.")
    finally:
        db.close()


def cmd_sync(args):
    config, db = runtime()
    try:
        sync = SyncManager(db, config)
        if args.action == "full":
            stats = sync.full_sync()
            print_success(f"Sync complete: {stats}")
        elif args.action == "verify":
            issues = sync.verify()
            if issues:
                print_warning(f"{len(issues)} issue(s) found")
                for issue in issues:
                    print(f" - {issue}")
            else:
                print_success("No sync issues found.")
        elif args.action == "fix":
            issues = sync.verify()
            sync.fix_issues(issues)
            print_success(f"Attempted to fix {len(issues)} issue(s)")
        elif args.action == "escalate":
            escalated = db.check_auto_escalations()
            print_success(f"Auto-escalated {len(escalated)} blocker(s)")
        else:
            raise SystemExit(f"Unknown sync action: {args.action}")
    finally:
        db.close()


def cmd_parse(args):
    config, db = runtime()
    try:
        parser = ConversationParser(nlp_backend="regex")
        generator = AutoEntryGenerator(parser, db)
        text = args.text
        if args.file:
            text = (ROOT / args.file).read_text()
        if not text:
            raise SystemExit("Provide --text or --file")
        if args.preview:
            print(generator.preview_entry(text, source=args.source))
            return
        result = generator.generate_from_conversation(
            text,
            source=args.source,
            auto_create=args.auto_create,
            dry_run=False,
        )
        print(table([
            ["Tasks", str(result['extracted']['tasks'])],
            ["Decisions", str(result['extracted']['decisions'])],
            ["Blockers", str(result['extracted']['blockers'])],
            ["Created", str(result['created'])],
            ["Pending Approval", str(result['pending_approval'])],
            ["Parse ID", str(result['parse_id'])],
        ], headers=["Field", "Value"]))
    finally:
        db.close()


def cmd_pending(args):
    config, db = runtime()
    try:
        parser = AutoEntryGenerator(ConversationParser(), db)
        pending = parser.get_pending_parses()
        if not pending:
            print_info("No pending parses.")
            return
        rows = []
        for p in pending:
            rows.append([p['id'], p['source'], p['created_at'][:19], truncate(p.get('raw_text', ''), 40)])
        print(table(rows, headers=["ID", "Source", "Created", "Text preview"]))
    finally:
        db.close()


def cmd_approve(args):
    config, db = runtime()
    try:
        parser = AutoEntryGenerator(ConversationParser(), db)
        ok = parser.approve_pending_parse(args.parse_id)
        if ok:
            print_success(f"Approved {args.parse_id}")
        else:
            print_error(f"Parse not found: {args.parse_id}")
    finally:
        db.close()


def cmd_version(args):
    print(f"Memory System {SCHEMA_VERSION} (v3 wrapper)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Memory Manager v3 - modular operational memory system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s init
  %(prog)s dashboard
  %(prog)s entry add
  %(prog)s search "authentication" --advanced
  %(prog)s report daily
  %(prog)s backup create --include-code
  %(prog)s validate --fix
  %(prog)s parse --file chat.txt --auto-create
        """,
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    p = subparsers.add_parser("init", help="Initialize v3 memory workspace")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_init)

    p = subparsers.add_parser("dashboard", help="Generate MEMORY.md and views")
    p.add_argument("-o", "--output", default="MEMORY.md")
    p.set_defaults(func=cmd_dashboard)

    p = subparsers.add_parser("version", help="Show version")
    p.set_defaults(func=cmd_version)

    entry = subparsers.add_parser("entry", help="Entry management")
    entry_sub = entry.add_subparsers(dest="entry_command", required=True)
    p = entry_sub.add_parser("add", help="Interactively add a daily entry")
    p.set_defaults(func=cmd_entry_add)
    p = entry_sub.add_parser("list", help="List entries")
    p.add_argument("--from-date", dest="from_date")
    p.add_argument("--to")
    p.add_argument("--project")
    p.add_argument("--tags")
    p.add_argument("--limit", type=int, default=20)
    p.set_defaults(func=cmd_entry_list)

    p = subparsers.add_parser("search", help="Search entries/tasks/decisions/blockers")
    p.add_argument("query")
    p.add_argument("--type", choices=["all", "entry", "task", "decision", "blocker"], default="all")
    p.add_argument("--project")
    p.add_argument("--from-date")
    p.add_argument("--to")
    p.add_argument("--tags")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--advanced", action="store_true")
    p.set_defaults(func=cmd_search)

    p = subparsers.add_parser("report", help="Generate reports")
    p.add_argument("kind", choices=["daily", "weekly", "project", "blockers", "decisions"])
    p.add_argument("--date")
    p.add_argument("--week", type=int)
    p.add_argument("--year", type=int)
    p.add_argument("--project")
    p.add_argument("--from-date", dest="from_date")
    p.add_argument("--to")
    p.add_argument("--escalated", action="store_true")
    p.add_argument("--review-due", action="store_true")
    p.add_argument("-o", "--output")
    p.set_defaults(func=cmd_report)

    p = subparsers.add_parser("sync", help="Sync / verify / escalate memory data")
    p.add_argument("action", choices=["full", "verify", "fix", "escalate"])
    p.set_defaults(func=cmd_sync)

    p = subparsers.add_parser("validate", help="Run integrity checks")
    p.add_argument("--fix", action="store_true")
    p.set_defaults(func=cmd_validate)

    p = subparsers.add_parser("backup", help="Backup memory data")
    bp = p.add_subparsers(dest="backup_action", required=True)
    c = bp.add_parser("create", help="Create a tar.gz snapshot")
    c.add_argument("--name")
    c.add_argument("--include-code", action="store_true", help="Include code/docs in snapshot")
    c.set_defaults(func=lambda a: cmd_backup(argparse.Namespace(action="create", name=a.name, include_code=a.include_code)))
    l = bp.add_parser("list", help="List backups")
    l.set_defaults(func=lambda a: cmd_backup(argparse.Namespace(action="list", name=None, include_code=False)))
    r = bp.add_parser("restore", help="Restore from a snapshot")
    r.add_argument("path")
    r.add_argument("-y", "--yes", action="store_true")
    r.set_defaults(func=cmd_restore)

    p = subparsers.add_parser("parse", help="Parse conversations into memory candidates")
    p.add_argument("--text")
    p.add_argument("--file")
    p.add_argument("--source", default="unknown")
    p.add_argument("--preview", action="store_true")
    p.add_argument("--auto-create", action="store_true")
    p.set_defaults(func=cmd_parse)

    p = subparsers.add_parser("pending", help="List pending auto-extraction parses")
    p.set_defaults(func=cmd_pending)

    p = subparsers.add_parser("approve", help="Approve a pending parse")
    p.add_argument("parse_id")
    p.set_defaults(func=cmd_approve)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
