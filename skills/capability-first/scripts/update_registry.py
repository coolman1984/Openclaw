#!/usr/bin/env python3
"""Regenerate the capability registry from current skills and curated tools/workflows."""

from __future__ import annotations

from pathlib import Path
from datetime import datetime
import re

ROOT = Path(__file__).resolve().parents[3]
SKILLS_ROOT = ROOT / "skills"
OUTPUT = ROOT / "skills" / "capability-first" / "references" / "capability-registry.md"

# Curated tools/workflows are kept here so new tools can be appended in one place.
TOOL_SECTIONS = [
    ("Core runtime tools", [
        "read", "write", "edit", "exec", "process",
        "web_search", "web_fetch",
        "memory_search", "memory_get",
        "sessions_spawn", "sessions_yield", "sessions_list", "sessions_history", "sessions_send",
        "subagents", "session_status",
    ]),
    ("Orchestration helpers", [
        "multi_tool_use.parallel",
        "skill-creator",
        "capability-first",
        "orchestration-ceo",
        "task-watch",
    ]),
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


def build_registry() -> str:
    skills = []
    for skill_md in sorted(SKILLS_ROOT.glob("*/SKILL.md")):
        if skill_md.parent.name == "capability-first":
            # include the skill itself, but keep ordering deterministic
            pass
        skills.append(parse_skill(skill_md))

    skills.sort(key=lambda item: item["name"].lower())

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
    for title, entries in TOOL_SECTIONS:
        lines.append(f"### {title}")
        for entry in entries:
            lines.append(f"- `{entry}`")
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
        "Whenever a new skill or tool is created or discovered, rerun this generator and refresh the registry.",
    ])

    return "\n".join(lines) + "\n"


def main() -> int:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(build_registry(), encoding="utf-8")
    print(f"Updated {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
