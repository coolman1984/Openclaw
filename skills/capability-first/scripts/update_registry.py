#!/usr/bin/env python3
"""Regenerate the capability registry from current skills and the capability inventory."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SKILLS_ROOT = ROOT / "skills"
INVENTORY = ROOT / "skills" / "capability-first" / "references" / "capability-inventory.json"
OUTPUT = ROOT / "skills" / "capability-first" / "references" / "capability-registry.md"

DEFAULT_SECTIONS = [
    {
        "title": "Core runtime tools",
        "items": [
            {"name": "read", "description": "Read file contents from the workspace."},
            {"name": "write", "description": "Create or overwrite files in the workspace."},
            {"name": "edit", "description": "Make precise text replacements in existing files."},
            {"name": "exec", "description": "Run shell commands and scripts."},
            {"name": "process", "description": "Manage background exec sessions."},
            {"name": "web_search", "description": "Search the web using DuckDuckGo."},
            {"name": "web_fetch", "description": "Fetch and extract readable web content."},
            {"name": "memory_search", "description": "Search memory files and transcripts semantically."},
            {"name": "memory_get", "description": "Read targeted memory snippets safely."},
            {"name": "sessions_spawn", "description": "Spawn a sub-agent or ACP session."},
            {"name": "sessions_yield", "description": "Yield control while waiting for sub-agent results."},
            {"name": "sessions_list", "description": "List sessions and recent activity."},
            {"name": "sessions_history", "description": "Fetch session history."},
            {"name": "sessions_send", "description": "Send a message into another session."},
            {"name": "subagents", "description": "List, steer, or kill sub-agent runs."},
            {"name": "session_status", "description": "Show session status and usage card."},
        ],
    },
    {
        "title": "Orchestration helpers",
        "items": [
            {"name": "multi_tool_use.parallel", "description": "Run multiple compatible tools in parallel."},
            {"name": "skill-creator", "description": "Create, improve, audit, and package AgentSkills."},
            {"name": "orchestration-ceo", "description": "Top-level routing and control skill."},
            {"name": "task-watch", "description": "Pending-work monitoring and completion follow-up."},
            {"name": "capability-first", "description": "Pre-task capability routing to reuse existing skills and tools first."},
        ],
    },
    {
        "title": "Workspace tools",
        "items": [
            {"name": "dev-assistant.py", "description": "Python CLI productivity dashboard."},
            {"name": "multi-agent-coding.sh", "description": "Multi-agent coding workflow shell script."},
            {"name": "memory-manager.py", "description": "Original monolithic memory manager CLI."},
            {"name": "memory-v3.py", "description": "Modular memory manager v3 entry point."},
            {"name": "memory-maintenance.sh", "description": "Daily memory maintenance helper."},
            {"name": "memory-install-cron.sh", "description": "Cron installer for memory maintenance and audits."},
            {"name": "capability-first/scripts/update_registry.py", "description": "Regenerate the capability registry from the current inventory."},
            {"name": "capability-first/scripts/sync_capabilities.py", "description": "Register new skills or tools and refresh the registry."},
        ],
    },
]


def parse_skill(skill_md: Path) -> dict[str, str]:
    text = skill_md.read_text(encoding="utf-8")
    name = skill_md.parent.name
    desc = ""
    if text.startswith("---"):
        frontmatter = text.split("---", 2)[1]
        for line in frontmatter.splitlines():
            m = re.match(r"^\s*name:\s*(.+?)\s*$", line)
            if m:
                name = m.group(1)
            m = re.match(r"^\s*description:\s*(.+?)\s*$", line)
            if m:
                desc = m.group(1)
    return {"name": name, "description": desc}


def load_inventory() -> list[dict]:
    if INVENTORY.exists():
        data = json.loads(INVENTORY.read_text(encoding="utf-8"))
        return data.get("sections", [])
    return DEFAULT_SECTIONS


def build_registry() -> str:
    skills = [parse_skill(skill_md) for skill_md in sorted(SKILLS_ROOT.glob("*/SKILL.md"))]
    skills.sort(key=lambda item: item["name"].lower())

    sections = load_inventory()

    lines = [
        "# Capability Registry",
        "",
        "This registry is the first place to check before doing fresh reasoning.",
        "",
        f"_Generated: {datetime.now().isoformat(timespec='seconds')}_",
        "",
        "## Skills",
        "",
    ]

    for item in skills:
        lines.append(f"### `{item['name']}`")
        if item["description"]:
            lines.append(item["description"])
        lines.append("")

    lines.append("## Tools and workflows")
    lines.append("")
    for section in sections:
        lines.append(f"### {section['title']}")
        for item in section.get("items", []):
            lines.append(f"- `{item['name']}`")
            if item.get("description"):
                lines.append(f"  - {item['description']}")
        lines.append("")

    lines.extend([
        "## Routing rule of thumb",
        "",
        "If a skill already matches the task, use the skill before inventing a new solution.",
        "If a tool already finishes the job, use the tool before writing new code.",
        "If the workflow repeats, convert it into a skill or automation.",
        "",
        "## Maintenance rule",
        "",
        "Whenever a new skill or tool is created or discovered, rerun the sync script and refresh the registry.",
    ])

    return "\n".join(lines) + "\n"


def main() -> int:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(build_registry(), encoding="utf-8")
    print(f"Updated {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
