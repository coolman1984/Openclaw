#!/usr/bin/env python3
"""Synchronize the capability inventory and regenerate the registry.

Use this after creating, discovering, or updating any skill/tool.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
INVENTORY = ROOT / "skills" / "capability-first" / "references" / "capability-inventory.json"
UPDATE_REGISTRY = ROOT / "skills" / "capability-first" / "scripts" / "update_registry.py"


def load_inventory() -> dict:
    if INVENTORY.exists():
        return json.loads(INVENTORY.read_text(encoding="utf-8"))
    return {"sections": []}


def save_inventory(data: dict) -> None:
    INVENTORY.parent.mkdir(parents=True, exist_ok=True)
    INVENTORY.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def ensure_section(data: dict, title: str) -> dict:
    for section in data.setdefault("sections", []):
        if section.get("title") == title:
            return section
    section = {"title": title, "items": []}
    data["sections"].append(section)
    return section


def upsert_item(section: dict, name: str, description: str) -> None:
    for item in section.setdefault("items", []):
        if item.get("name") == name:
            item["description"] = description
            return
    section["items"].append({"name": name, "description": description})


def run_update_registry() -> None:
    subprocess.run(["python3", str(UPDATE_REGISTRY)], cwd=ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Synchronize capability inventory and regenerate registry")
    parser.add_argument("--add-tool", action="append", nargs=3, metavar=("SECTION", "NAME", "DESCRIPTION"), help="Register a tool in a section")
    parser.add_argument("--refresh", action="store_true", help="Regenerate the registry from the current inventory")
    args = parser.parse_args()

    data = load_inventory()
    changed = False

    if args.add_tool:
        for section_title, name, description in args.add_tool:
            section = ensure_section(data, section_title)
            upsert_item(section, name, description)
            changed = True

    if changed:
        save_inventory(data)

    if changed or args.refresh or not INVENTORY.exists():
        run_update_registry()
        print(f"Synchronized capability registry at {INVENTORY}")
    else:
        print("No changes; registry already current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
