"""
Data Models for Memory Management System
"""

import json
import hashlib
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field, asdict


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    @classmethod
    def disable(cls):
        """Disable all colors."""
        cls.HEADER = ''
        cls.BLUE = ''
        cls.CYAN = ''
        cls.GREEN = ''
        cls.WARNING = ''
        cls.FAIL = ''
        cls.ENDC = ''
        cls.BOLD = ''
        cls.UNDERLINE = ''


def generate_id(prefix: str = "item") -> str:
    """Generate a unique ID with prefix."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def compute_hash(text: str) -> str:
    """Compute SHA256 hash of text."""
    return f"sha256:{hashlib.sha256(text.encode()).hexdigest()[:16]}"


@dataclass
class Summary:
    """Entry summary."""
    title: str = ""
    description: str = ""
    mood: str = ""
    energy_level: int = 5
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Summary':
        return cls(**data)


@dataclass
class Task:
    """Task model."""
    id: str
    title: str
    description: str = ""
    status: str = "pending"  # pending, in_progress, completed, blocked, cancelled
    priority: str = "medium"  # low, medium, high, critical
    project_id: Optional[str] = None
    entry_date: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    progress: int = 0
    blockers: List[str] = field(default_factory=list)
    related_entries: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    @classmethod
    def create(cls, title: str, **kwargs) -> 'Task':
        """Create a new task."""
        return cls(
            id=generate_id("task"),
            title=title,
            **kwargs
        )
    
    def complete(self, hours: Optional[float] = None):
        """Mark task as completed."""
        self.status = "completed"
        self.completed_at = datetime.now().isoformat()
        self.progress = 100
        if hours:
            self.actual_hours = hours
    
    def block(self, reason: str):
        """Block task with reason."""
        self.status = "blocked"
        blocker = Blocker.create(title=reason, related_task=self.id)
        self.blockers.append(blocker.id)
        return blocker
    
    def start(self):
        """Start task."""
        if self.status == "pending":
            self.status = "in_progress"
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Task':
        return cls(**data)
    
    @staticmethod
    def print_list(tasks: List['Task'], title: str = "Tasks"):
        """Print task list in table format."""
        print(f"\n{Colors.BOLD}{title}{Colors.ENDC}")
        print("-" * 80)
        print(f"{'ID':<12} {'Status':<12} {'Priority':<10} {'Title':<46}")
        print("-" * 80)
        
        priority_colors = {
            'critical': Colors.FAIL,
            'high': Colors.WARNING,
            'medium': Colors.CYAN,
            'low': Colors.GREEN
        }
        
        status_symbols = {
            'completed': f"{Colors.GREEN}✓{Colors.ENDC}",
            'in_progress': f"{Colors.BLUE}►{Colors.ENDC}",
            'blocked': f"{Colors.FAIL}✗{Colors.ENDC}",
            'pending': f"{Colors.CYAN}○{Colors.ENDC}"
        }
        
        for task in tasks:
            p_color = priority_colors.get(task.priority, '')
            symbol = status_symbols.get(task.status, '?')
            print(f"{task.id:<12} {symbol} {task.status:<10} "
                  f"{p_color}{task.priority:<8}{Colors.ENDC} {task.title[:44]:<44}")
        print("-" * 80)


@dataclass
class Decision:
    """Decision registry entry."""
    id: str
    title: str
    context: str
    decision: str
    rationale: str = ""
    alternatives: List[Dict] = field(default_factory=list)
    consequences: Dict = field(default_factory=dict)
    reversibility: str = "medium"  # low, medium, high
    status: str = "active"  # active, superseded, reversed
    project_id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    review_date: Optional[str] = None
    superseded_by: Optional[str] = None
    linked_entries: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    @classmethod
    def create(cls, title: str, context: str, decision: str, **kwargs) -> 'Decision':
        """Create a new decision."""
        return cls(
            id=generate_id("dec"),
            title=title,
            context=context,
            decision=decision,
            **kwargs
        )
    
    def supersede(self, new_decision_id: str):
        """Mark as superseded by another decision."""
        self.status = "superseded"
        self.superseded_by = new_decision_id
    
    def reverse(self):
        """Reverse the decision."""
        self.status = "reversed"
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Decision':
        return cls(**data)
    
    @staticmethod
    def print_list(decisions: List['Decision'], title: str = "Decisions"):
        """Print decision list."""
        print(f"\n{Colors.BOLD}{title}{Colors.ENDC}")
        print("-" * 80)
        
        for d in decisions:
            status_color = Colors.GREEN if d.status == "active" else Colors.WARNING
            print(f"{d.id} {status_color}[{d.status}]{Colors.ENDC} {d.title}")
            print(f"  Context: {d.context[:60]}...")
            print(f"  Choice: {d.decision}")
            if d.reversibility:
                print(f"  Reversibility: {d.reversibility}")
            print()


@dataclass
class Blocker:
    """Blocker model with escalation tracking."""
    id: str
    title: str
    description: str = ""
    severity: str = "medium"  # low, medium, high, critical
    impact: str = "blocking"  # minor, moderate, blocking, critical
    escalation_level: int = 0
    escalation_history: List[Dict] = field(default_factory=list)
    status: str = "active"  # active, mitigated, resolved
    project_id: Optional[str] = None
    assigned_to: Optional[str] = None
    related_task: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    resolved_at: Optional[str] = None
    resolution: Optional[str] = None
    mitigation: Dict = field(default_factory=lambda: {"attempted": [], "pending": [], "workaround": None})
    tags: List[str] = field(default_factory=list)
    
    ESCALATION_LEVELS = [
        {"level": 0, "name": "Identified", "auto_escalate_after_hours": 24},
        {"level": 1, "name": "Acknowledged", "auto_escalate_after_hours": 48},
        {"level": 2, "name": "Escalated", "auto_escalate_after_hours": 72},
        {"level": 3, "name": "Critical", "auto_escalate_after_hours": None}
    ]
    
    @classmethod
    def create(cls, title: str, **kwargs) -> 'Blocker':
        """Create a new blocker."""
        blocker = cls(
            id=generate_id("blk"),
            title=title,
            **kwargs
        )
        blocker.escalation_history.append({
            "level": 0,
            "name": "Identified",
            "date": datetime.now().isoformat()
        })
        return blocker
    
    def escalate(self, level: Optional[int] = None, reason: Optional[str] = None):
        """Escalate blocker to next or specified level."""
        if level is None:
            level = self.escalation_level + 1
        
        if level > 3:
            level = 3
        
        self.escalation_level = level
        self.escalation_history.append({
            "level": level,
            "name": self.ESCALATION_LEVELS[level]["name"],
            "date": datetime.now().isoformat(),
            "reason": reason
        })
    
    def should_auto_escalate(self) -> bool:
        """Check if blocker should auto-escalate."""
        if self.status != "active":
            return False
        if self.escalation_level >= 3:
            return False
        
        level_info = self.ESCALATION_LEVELS[self.escalation_level]
        hours_threshold = level_info.get("auto_escalate_after_hours")
        
        if hours_threshold is None:
            return False
        
        last_escalation = datetime.fromisoformat(self.escalation_history[-1]["date"])
        hours_elapsed = (datetime.now() - last_escalation).total_seconds() / 3600
        
        return hours_elapsed >= hours_threshold
    
    def resolve(self, resolution: str):
        """Resolve blocker."""
        self.status = "resolved"
        self.resolution = resolution
        self.resolved_at = datetime.now().isoformat()
    
    def add_mitigation(self, action: str, pending: bool = False):
        """Add mitigation attempt or pending action."""
        if pending:
            self.mitigation["pending"].append(action)
        else:
            self.mitigation["attempted"].append(action)
    
    def set_workaround(self, workaround: str):
        """Set workaround for blocker."""
        self.mitigation["workaround"] = workaround
        self.status = "mitigated"
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Blocker':
        return cls(**data)
    
    @staticmethod
    def print_list(blockers: List['Blocker'], title: str = "Blockers"):
        """Print blocker list."""
        print(f"\n{Colors.BOLD}{title}{Colors.ENDC}")
        print("-" * 80)
        
        severity_colors = {
            'critical': Colors.FAIL,
            'high': Colors.WARNING,
            'medium': Colors.CYAN,
            'low': Colors.GREEN
        }
        
        for b in blockers:
            sev_color = severity_colors.get(b.severity, '')
            esc_indicator = f"⬆{b.escalation_level}" if b.escalation_level > 0 else ""
            print(f"{b.id} {esc_indicator} {sev_color}[{b.severity}]{Colors.ENDC} {b.title}")
            if b.description:
                print(f"  {b.description[:60]}...")
            print(f"  Impact: {b.impact} | Status: {b.status}")
            if b.assigned_to:
                print(f"  Assigned to: {b.assigned_to}")
            print()


@dataclass
class Conversation:
    """Extracted conversation record."""
    id: str
    source: str
    participants: List[str] = field(default_factory=list)
    summary: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    context_hash: str = ""
    extracted_tasks: List[str] = field(default_factory=list)
    extracted_decisions: List[str] = field(default_factory=list)
    extracted_blockers: List[str] = field(default_factory=list)
    raw_text: str = ""
    
    @classmethod
    def create(cls, source: str, summary: str, raw_text: str, **kwargs) -> 'Conversation':
        """Create a new conversation record."""
        context_hash = kwargs.pop("context_hash", compute_hash(raw_text))
        return cls(
            id=generate_id("conv"),
            source=source,
            summary=summary,
            raw_text=raw_text,
            context_hash=context_hash,
            **kwargs
        )
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Conversation':
        return cls(**data)


@dataclass
class Note:
    """Note model."""
    id: str
    content: str
    category: str = "general"
    tags: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @classmethod
    def create(cls, content: str, **kwargs) -> 'Note':
        return cls(
            id=generate_id("note"),
            content=content,
            **kwargs
        )
    
    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'Note':
        return cls(**data)


@dataclass
class Metrics:
    """Daily metrics."""
    tasks_completed: int = 0
    tasks_created: int = 0
    decisions_made: int = 0
    blockers_identified: int = 0
    blockers_resolved: int = 0
    hours_logged: float = 0.0
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Metrics':
        return cls(**data)


@dataclass
class Entry:
    """Daily entry model."""
    id: str
    date: str
    timestamp_created: str
    timestamp_updated: str
    version: str = "1.0"
    summary: Summary = field(default_factory=Summary)
    tasks: List[Task] = field(default_factory=list)
    decisions: List[Decision] = field(default_factory=list)
    blockers: List[Blocker] = field(default_factory=list)
    notes: List[Note] = field(default_factory=list)
    conversations: List[Conversation] = field(default_factory=list)
    metrics: Metrics = field(default_factory=Metrics)
    tags: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    
    @classmethod
    def create(cls, date: Optional[str] = None, title: str = "", **kwargs) -> 'Entry':
        """Create a new daily entry."""
        now = datetime.now().isoformat()
        date = date or datetime.now().strftime('%Y-%m-%d')
        
        return cls(
            id=date,
            date=date,
            timestamp_created=now,
            timestamp_updated=now,
            summary=Summary(title=title),
            **kwargs
        )
    
    def update(self, data: Dict):
        """Update entry from dictionary."""
        if 'summary' in data:
            self.summary = Summary.from_dict(data['summary'])
        if 'tasks' in data:
            self.tasks = [Task.from_dict(t) for t in data['tasks']]
        if 'decisions' in data:
            self.decisions = [Decision.from_dict(d) for d in data['decisions']]
        if 'blockers' in data:
            self.blockers = [Blocker.from_dict(b) for b in data['blockers']]
        if 'tags' in data:
            self.tags = data['tags']
        if 'references' in data:
            self.references = data['references']
        
        self.timestamp_updated = datetime.now().isoformat()
    
    def add_task(self, task: Task):
        """Add task to entry."""
        task.entry_date = self.date
        self.tasks.append(task)
        self.metrics.tasks_created += 1
    
    def add_decision(self, decision: Decision):
        """Add decision to entry."""
        self.decisions.append(decision)
        self.metrics.decisions_made += 1
    
    def add_blocker(self, blocker: Blocker):
        """Add blocker to entry."""
        self.blockers.append(blocker)
        self.metrics.blockers_identified += 1
    
    def add_conversation(self, conversation: Conversation):
        """Add conversation to entry."""
        self.conversations.append(conversation)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'date': self.date,
            'timestamp_created': self.timestamp_created,
            'timestamp_updated': self.timestamp_updated,
            'version': self.version,
            'summary': self.summary.to_dict(),
            'tasks': [t.to_dict() for t in self.tasks],
            'decisions': [d.to_dict() for d in self.decisions],
            'blockers': [b.to_dict() for b in self.blockers],
            'notes': [n.to_dict() for n in self.notes],
            'conversations': [c.to_dict() for c in self.conversations],
            'metrics': self.metrics.to_dict(),
            'tags': self.tags,
            'references': self.references
        }
    
    def to_markdown(self) -> str:
        """Convert entry to markdown format."""
        md = f"# Daily Log: {self.date}\n\n"
        md += f"**{self.summary.title}**\n\n"
        
        if self.summary.description:
            md += f"{self.summary.description}\n\n"
        
        if self.tasks:
            md += "## Tasks\n\n"
            for task in self.tasks:
                status = "[x]" if task.status == "completed" else "[ ]"
                md += f"- {status} {task.title} ({task.priority})\n"
            md += "\n"
        
        if self.decisions:
            md += "## Decisions\n\n"
            for d in self.decisions:
                md += f"- **{d.title}**: {d.decision}\n"
            md += "\n"
        
        if self.blockers:
            md += "## Blockers\n\n"
            for b in self.blockers:
                md += f"- ⚠️ **{b.title}** ({b.severity})\n"
            md += "\n"
        
        if self.notes:
            md += "## Notes\n\n"
            for note in self.notes:
                md += f"- {note.content}\n"
            md += "\n"
        
        if self.tags:
            md += f"**Tags:** {', '.join(self.tags)}\n\n"
        
        return md
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Entry':
        """Create entry from dictionary."""
        return cls(
            id=data['id'],
            date=data['date'],
            timestamp_created=data['timestamp_created'],
            timestamp_updated=data['timestamp_updated'],
            version=data.get('version', '1.0'),
            summary=Summary.from_dict(data.get('summary', {})),
            tasks=[Task.from_dict(t) for t in data.get('tasks', [])],
            decisions=[Decision.from_dict(d) for d in data.get('decisions', [])],
            blockers=[Blocker.from_dict(b) for b in data.get('blockers', [])],
            notes=[Note.from_dict(n) if isinstance(n, dict) else n for n in data.get('notes', [])],
            conversations=[Conversation.from_dict(c) for c in data.get('conversations', [])],
            metrics=Metrics.from_dict(data.get('metrics', {})),
            tags=data.get('tags', []),
            references=data.get('references', [])
        )
    
    def to_format(self, format_type: str = "table") -> str:
        """Format entry for display."""
        if format_type == "json":
            return json.dumps(self.to_dict(), indent=2)
        elif format_type == "markdown":
            return self.to_markdown()
        else:
            return self._to_table()
    
    def _to_table(self) -> str:
        """Format as text table."""
        lines = [
            f"{Colors.BOLD}Entry: {self.date}{Colors.ENDC}",
            f"Title: {self.summary.title}",
            f"Created: {self.timestamp_created}",
            f"Updated: {self.timestamp_updated}",
            "-" * 60,
            f"Tasks: {len(self.tasks)}",
            f"Decisions: {len(self.decisions)}",
            f"Blockers: {len(self.blockers)}",
            f"Tags: {', '.join(self.tags) if self.tags else 'None'}",
        ]
        return "\n".join(lines)
    
    @staticmethod
    def print_list(entries: List['Entry'], title: str = "Entries"):
        """Print entry list."""
        print(f"\n{Colors.BOLD}{title}{Colors.ENDC}")
        print("-" * 80)
        print(f"{'Date':<12} {'Title':<50} {'Tasks':<6} {'Decisions':<10}")
        print("-" * 80)
        
        for entry in entries:
            print(f"{entry.date:<12} {entry.summary.title[:48]:<48} "
                  f"{len(entry.tasks):<6} {len(entry.decisions):<10}")
        print("-" * 80)


@dataclass
class Project:
    """Project model."""
    id: str
    name: str
    description: str = ""
    status: str = "active"  # active, paused, completed, archived
    priority: str = "medium"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    target_completion: Optional[str] = None
    completed_at: Optional[str] = None
    color: str = "#4A90E2"
    tags: List[str] = field(default_factory=list)
    goals: List[str] = field(default_factory=list)
    linked_entries: List[str] = field(default_factory=list)
    
    @classmethod
    def create(cls, id: str, name: str, **kwargs) -> 'Project':
        """Create a new project."""
        now = datetime.now().isoformat()
        return cls(
            id=id,
            name=name,
            created_at=now,
            started_at=now,
            **kwargs
        )
    
    def complete(self):
        """Mark project as completed."""
        self.status = "completed"
        self.completed_at = datetime.now().isoformat()
    
    def pause(self):
        """Pause project."""
        self.status = "paused"
    
    def resume(self):
        """Resume project."""
        self.status = "active"
    
    def archive(self):
        """Archive project."""
        self.status = "archived"
    
    def add_goal(self, goal: str):
        """Add project goal."""
        self.goals.append(goal)
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Project':
        return cls(**data)
    
    @staticmethod
    def print_list(projects: List['Project'], title: str = "Projects"):
        """Print project list."""
        print(f"\n{Colors.BOLD}{title}{Colors.ENDC}")
        print("-" * 80)
        print(f"{'ID':<20} {'Status':<12} {'Priority':<10} {'Name':<38}")
        print("-" * 80)
        
        status_colors = {
            'active': Colors.GREEN,
            'paused': Colors.WARNING,
            'completed': Colors.CYAN,
            'archived': Colors.FAIL
        }
        
        for p in projects:
            s_color = status_colors.get(p.status, '')
            print(f"{p.id:<20} {s_color}{p.status:<10}{Colors.ENDC} "
                  f"{p.priority:<10} {p.name:<36}")
        print("-" * 80)
