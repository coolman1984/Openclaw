#!/usr/bin/env python3
"""Demo script to populate memory system with sample data"""

import sys
sys.path.insert(0, '/root/.openclaw/workspace/memory-system')

import importlib.util
spec = importlib.util.spec_from_file_location("memory_manager", "/root/.openclaw/workspace/memory-system/memory-manager.py")
memory_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(memory_module)

MemoryDatabase = memory_module.MemoryDatabase
Entry = memory_module.Entry
Colors = memory_module.Colors
c = memory_module.c
from datetime import datetime

# Initialize and add sample data
db = MemoryDatabase()

print(c("\n📝 Adding Sample Entries", Colors.HEADER))
print("=" * 60)

# Entry 1: Initial Setup
entry1 = Entry(
    id=0,
    date="2026-03-23",
    project="memory-system",
    summary="Built comprehensive operational memory management system",
    context="User requested a detailed memory system to track all work, decisions, and continuity across sessions",
    tasks=[
        {"title": "Review existing memory files", "priority": "high", "status": "completed", "owner": "reviewer"},
        {"title": "Design system architecture", "priority": "high", "status": "completed", "owner": "architect"},
        {"title": "Create implementation plan", "priority": "high", "status": "completed", "owner": "developer"},
        {"title": "Build CLI tool", "priority": "high", "status": "completed", "owner": "developer"},
        {"title": "Test system", "priority": "medium", "status": "completed", "owner": "reviewer"}
    ],
    decisions=[
        {"title": "Storage format", "choice": "SQLite + Markdown", "context": "Need both fast queries and human-readable logs", "rationale": "SQLite for search/retrieval, Markdown for version control and readability", "impact": "high", "reversible": True}
    ],
    blockers=[
        {"title": "Reserved keyword conflict", "description": "SQLite 'references' keyword caused syntax error", "severity": "medium", "status": "resolved"}
    ],
    next_steps="Initialize git backup, create cron reminders, train user on workflow",
    references=["memory-system-architecture.md", "memory-implementation-guide.md"],
    status="completed",
    priority="high",
    participants=["Mohamed", "OpenClaw", "Architect", "Developer", "Reviewer"],
    tags=["infrastructure", "memory", "cli"],
    created=datetime.now().isoformat(),
    modified=datetime.now().isoformat()
)

id1 = db.add_entry(entry1)
print(c(f"✅ Entry #{id1}: System implementation complete", Colors.GREEN))

# Entry 2: Multi-agent workflow
entry2 = Entry(
    id=0,
    date="2026-03-23",
    project="opencode-go",
    summary="Configured specialized coding agents with OpenCode Go subscription",
    context="User has OpenCode Go subscription with access to GLM-5, Kimi K2.5, and MiniMax models",
    tasks=[
        {"title": "Research OpenCode Go models", "priority": "high", "status": "completed"},
        {"title": "Create agent personalities", "priority": "high", "status": "completed"},
        {"title": "Build multi-agent orchestration", "priority": "medium", "status": "completed"}
    ],
    decisions=[
        {"title": "Agent model assignments", "choice": "GLM-5 for coding, Kimi K2.5 for planning, MiniMax M2.7 for review", "context": "Each model has different strengths", "rationale": "Optimal cost/performance balance", "impact": "medium", "reversible": True}
    ],
    blockers=[],
    next_steps="Use agents for actual coding tasks",
    references=["AGENTS.md", "multi-agent-coding.sh"],
    status="active",
    priority="medium",
    participants=["Mohamed", "OpenClaw"],
    tags=["agents", "opencode", "ai"],
    created=datetime.now().isoformat(),
    modified=datetime.now().isoformat()
)

id2 = db.add_entry(entry2)
print(c(f"✅ Entry #{id2}: Multi-agent system configured", Colors.GREEN))

# Entry 3: Dev Assistant app
entry3 = Entry(
    id=0,
    date="2026-03-23",
    project="productivity-tools",
    summary="Built Dev Assistant Dashboard CLI application",
    context="Demonstrated app development capabilities in Termux environment",
    tasks=[
        {"title": "Design app architecture", "priority": "medium", "status": "completed"},
        {"title": "Implement task manager", "priority": "medium", "status": "completed"},
        {"title": "Implement notes system", "priority": "medium", "status": "completed"},
        {"title": "Add time tracking", "priority": "low", "status": "completed"}
    ],
    decisions=[
        {"title": "Language choice", "choice": "Python 3", "context": "Available in Termux environment", "rationale": "Cross-platform, rich ecosystem, easy to extend", "impact": "low", "reversible": True}
    ],
    blockers=[],
    next_steps="Extend with more features as needed",
    references=["dev-assistant.py"],
    status="completed",
    priority="low",
    participants=["OpenClaw"],
    tags=["python", "cli", "productivity"],
    created=datetime.now().isoformat(),
    modified=datetime.now().isoformat()
)

id3 = db.add_entry(entry3)
print(c(f"✅ Entry #{id3}: Dev Assistant app created", Colors.GREEN))

print(c("\n✅ Demo data loaded successfully!", Colors.GREEN))
print(f"\nRun these commands to explore:")
print(f"  python3 memory-manager.py dashboard")
print(f"  python3 memory-manager.py task list")
print(f"  python3 memory-manager.py blocker list")
print(f"  python3 memory-manager.py search 'memory'")

db.close()