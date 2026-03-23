"""
Report Generation
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path

from database import Database
from models import Entry, Task, Decision, Blocker
from utils import Colors, format_date, progress_bar, table


class ReportGenerator:
    """Generate various reports from memory data."""
    
    def __init__(self, database: Database):
        self.db = database
    
    def daily_report(self, date: Optional[str] = None) -> str:
        """Generate daily report."""
        date = date or datetime.now().strftime('%Y-%m-%d')
        entry = self.db.get_entry(date)
        
        if not entry:
            return f"# Daily Report: {date}\n\nNo entry found for this date."
        
        report = f"""# Daily Report: {date}

## Summary

**Title:** {entry.summary.title}

**Description:** {entry.summary.description or 'No description'}

**Mood:** {entry.summary.mood or 'Not recorded'}
**Energy Level:** {entry.summary.energy_level or 'N/A'}/10

---

## Tasks

### Completed ({len([t for t in entry.tasks if t.status == 'completed'])})
{self._format_task_list([t for t in entry.tasks if t.status == 'completed'])}

### In Progress ({len([t for t in entry.tasks if t.status == 'in_progress'])})
{self._format_task_list([t for t in entry.tasks if t.status == 'in_progress'])}

### Pending ({len([t for t in entry.tasks if t.status == 'pending'])})
{self._format_task_list([t for t in entry.tasks if t.status == 'pending'])}

---

## Decisions

{self._format_decision_list(entry.decisions)}

---

## Blockers

{self._format_blocker_list(entry.blockers)}

---

## Notes

{self._format_note_list(entry.notes)}

---

## Metrics

| Metric | Value |
|--------|-------|
| Tasks Created | {entry.metrics.tasks_created} |
| Tasks Completed | {entry.metrics.tasks_completed} |
| Decisions Made | {entry.metrics.decisions_made} |
| Blockers Identified | {entry.metrics.blockers_identified} |
| Hours Logged | {entry.metrics.hours_logged} |

---

## Tags

{', '.join(entry.tags) if entry.tags else 'None'}

---

*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
        
        return report
    
    def weekly_report(self, week: Optional[int] = None, year: Optional[int] = None) -> str:
        """Generate weekly report."""
        now = datetime.now()
        year = year or now.year
        
        if week is None:
            week = now.isocalendar()[1]
        
        # Calculate week dates
        jan_1 = datetime(year, 1, 1)
        start_of_week = jan_1 + timedelta(weeks=week - 1, days=-jan_1.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        start_str = start_of_week.strftime('%Y-%m-%d')
        end_str = end_of_week.strftime('%Y-%m-%d')
        
        # Get entries for the week
        entries = self.db.list_entries(from_date=start_str, to=end_str, limit=100)
        
        # Aggregate data
        all_tasks = []
        all_decisions = []
        all_blockers = []
        
        for entry in entries:
            all_tasks.extend(entry.tasks)
            all_decisions.extend(entry.decisions)
            all_blockers.extend(entry.blockers)
        
        completed_tasks = [t for t in all_tasks if t.status == 'completed']
        new_tasks = [t for t in all_tasks if t.created_at and t.created_at >= start_str]
        
        report = f"""# Weekly Report: Week {week}, {year}

**Period:** {start_str} to {end_str}

---

## Summary

| Metric | Count |
|--------|-------|
| Days Logged | {len(entries)} |
| New Tasks | {len(new_tasks)} |
| Completed Tasks | {len(completed_tasks)} |
| Decisions Made | {len(all_decisions)} |
| Blockers Identified | {len(all_blockers)} |

---

## Task Progress

{self._generate_task_progress_chart(all_tasks)}

---

## Daily Breakdown

"""
        
        for entry in entries:
            report += f"\n### {entry.date}\n\n"
            report += f"**{entry.summary.title}**\n\n"
            
            day_tasks = [t for t in entry.tasks if t.status == 'completed']
            if day_tasks:
                report += "Completed:\n"
                for t in day_tasks:
                    report += f"- ✅ {t.title}\n"
                report += "\n"
        
        report += f"""
---

## Decisions This Week

{self._format_decision_list(all_decisions)}

---

## Blockers This Week

{self._format_blocker_list(all_blockers)}

---

*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
        
        return report
    
    def project_report(self, project_id: str, 
                       from_date: Optional[str] = None,
                       to: Optional[str] = None) -> str:
        """Generate project report."""
        project = self.db.get_project(project_id)
        
        if not project:
            return f"# Project Report: {project_id}\n\nProject not found."
        
        # Get project data
        tasks = self.db.list_tasks(project=project_id, limit=1000)
        decisions = self.db.list_decisions(project=project_id, limit=100)
        blockers = self.db.list_blockers(project=project_id, limit=100)
        
        # Filter by date if specified
        if from_date:
            tasks = [t for t in tasks if t.created_at and t.created_at >= from_date]
        if to:
            tasks = [t for t in tasks if t.created_at and t.created_at <= to]
        
        completed = len([t for t in tasks if t.status == 'completed'])
        total = len(tasks)
        progress = (completed / max(total, 1)) * 100
        
        report = f"""# Project Report: {project.name}

**ID:** {project.id}
**Status:** {project.status}
**Priority:** {project.priority}
**Created:** {format_date(project.created_at[:10]) if project.created_at else 'Unknown'}

{project.description or 'No description'}

---

## Progress

{progress_bar(int(progress), 100)}

- **Total Tasks:** {total}
- **Completed:** {completed} ({progress:.1f}%)
- **Remaining:** {total - completed}

---

## Goals

{self._format_goals(project.goals)}

---

## Active Tasks

{self._format_task_list([t for t in tasks if t.status in ['pending', 'in_progress', 'blocked']])}

---

## Completed Tasks

{self._format_task_list([t for t in tasks if t.status == 'completed'])}

---

## Decisions

{self._format_decision_list(decisions)}

---

## Blockers

{self._format_blocker_list(blockers)}

---

## Timeline

"""
        
        # Add timeline
        if project.started_at:
            report += f"- **Started:** {format_date(project.started_at[:10])}\n"
        if project.target_completion:
            report += f"- **Target Completion:** {format_date(project.target_completion)}\n"
        if project.completed_at:
            report += f"- **Completed:** {format_date(project.completed_at[:10])}\n"
        
        report += f"""

---

*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
        
        return report
    
    def blockers_report(self, escalated_only: bool = False) -> str:
        """Generate blockers report."""
        if escalated_only:
            blockers = self.db.get_escalated_blockers(min_level=1)
            title = "Escalated Blockers Report"
        else:
            blockers = self.db.list_blockers(status='active', limit=100)
            title = "Blockers Report"
        
        if not blockers:
            return f"# {title}\n\nNo blockers to report."
        
        # Group by escalation level
        by_level = {}
        for b in blockers:
            level = b.escalation_level
            if level not in by_level:
                by_level[level] = []
            by_level[level].append(b)
        
        report = f"""# {title}

**Total Active Blockers:** {len(blockers)}

---

## By Escalation Level

"""
        
        level_names = {0: "Identified", 1: "Acknowledged", 2: "Escalated", 3: "Critical"}
        
        for level in sorted(by_level.keys(), reverse=True):
            name = level_names.get(level, f"Level {level}")
            report += f"\n### {name} ({len(by_level[level])})\n\n"
            
            for b in by_level[level]:
                report += f"- **{b.title}**\n"
                report += f"  - Severity: {b.severity}\n"
                report += f"  - Impact: {b.impact}\n"
                if b.description:
                    report += f"  - {b.description[:100]}...\n"
                if b.assigned_to:
                    report += f"  - Assigned to: {b.assigned_to}\n"
                report += "\n"
        
        report += f"""
---

## Summary by Severity

"""
        
        by_severity = {}
        for b in blockers:
            sev = b.severity
            if sev not in by_severity:
                by_severity[sev] = 0
            by_severity[sev] += 1
        
        for sev in ['critical', 'high', 'medium', 'low']:
            if sev in by_severity:
                emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}[sev]
                report += f"- {emoji} **{sev.title()}:** {by_severity[sev]}\n"
        
        report += f"""

---

*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
        
        return report
    
    def decisions_report(self, review_due: bool = False) -> str:
        """Generate decisions report."""
        if review_due:
            decisions = self.db.get_decisions_for_review(days=30)
            title = "Decisions Requiring Review"
        else:
            decisions = self.db.list_decisions(status='active', limit=100)
            title = "Decisions Report"
        
        if not decisions:
            return f"# {title}\n\nNo decisions to report."
        
        report = f"""# {title}

**Total Decisions:** {len(decisions)}

---

## Active Decisions

"""
        
        for d in decisions:
            rev_emoji = {'low': '🔄', 'medium': '↩️', 'high': '🔒'}.get(d.reversibility, '❓')
            report += f"\n### {rev_emoji} {d.title}\n\n"
            report += f"**ID:** {d.id}\n\n"
            report += f"**Context:** {d.context}\n\n"
            report += f"**Decision:** {d.decision}\n\n"
            report += f"**Reversibility:** {d.reversibility}\n\n"
            if d.review_date:
                report += f"**Review Date:** {format_date(d.review_date)}\n\n"
            if d.project_id:
                report += f"**Project:** {d.project_id}\n\n"
        
        report += f"""
---

*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')}*
"""
        
        return report
    
    # Helper methods
    
    def _format_task_list(self, tasks: List[Task]) -> str:
        """Format task list for report."""
        if not tasks:
            return "_None_"
        
        lines = []
        for t in tasks:
            priority = f"[{t.priority}]" if t.priority else ""
            lines.append(f"- {priority} {t.title}")
            if t.description:
                lines.append(f"  {t.description}")
        
        return "\n".join(lines)
    
    def _format_decision_list(self, decisions: List[Decision]) -> str:
        """Format decision list for report."""
        if not decisions:
            return "_None_"
        
        lines = []
        for d in decisions:
            lines.append(f"- **{d.title}**")
            lines.append(f"  Decision: {d.decision}")
        
        return "\n".join(lines)
    
    def _format_blocker_list(self, blockers: List[Blocker]) -> str:
        """Format blocker list for report."""
        if not blockers:
            return "_None_"
        
        lines = []
        for b in blockers:
            lines.append(f"- **{b.title}** ({b.severity})")
            if b.description:
                lines.append(f"  {b.description}")
        
        return "\n".join(lines)
    
    def _format_note_list(self, notes: List[Any]) -> str:
        """Format note list for report."""
        if not notes:
            return "_None_"
        
        return "\n".join([f"- {n.content if hasattr(n, 'content') else str(n)}" for n in notes])
    
    def _format_goals(self, goals: List[str]) -> str:
        """Format goals list."""
        if not goals:
            return "_No goals defined_"
        
        return "\n".join([f"{i+1}. {goal}" for i, goal in enumerate(goals)])
    
    def _generate_task_progress_chart(self, tasks: List[Task]) -> str:
        """Generate ASCII task progress chart."""
        if not tasks:
            return "No tasks"
        
        statuses = ['pending', 'in_progress', 'blocked', 'completed']
        counts = {s: len([t for t in tasks if t.status == s]) for s in statuses}
        total = len(tasks)
        
        chart = []
        for status in statuses:
            count = counts[status]
            pct = (count / total) * 100
            bar_length = int(pct / 5)  # 20 chars max
            bar = "█" * bar_length
            emoji = {'completed': '✅', 'in_progress': '▶️', 'blocked': '🚫', 'pending': '⏳'}[status]
            chart.append(f"{emoji} {status:12} {bar:20} {count:3} ({pct:5.1f}%)")
        
        return "```\n" + "\n".join(chart) + "\n```"
