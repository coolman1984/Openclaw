---
name: capability-first
description: Silent pre-task routing for OpenClaw. Use when deciding how to handle any request by checking existing skills, tools, reusable workflows, or delegated execution before doing fresh reasoning. This skill prevents duplicated work, wasted tokens, and rebuilding known workflows from scratch.
---

# Capability First

## Overview
Before solving anything, check what capability already exists. Reuse first. Invent last. Route before reasoning. This skill keeps the system lean, reliable, and low-waste.

## Core rule
For every task, silently ask:

**"What is the lowest-waste, highest-reliability path using capabilities I already have?"**

## Default routing order
1. **Existing skill** — if a skill already covers the task, use it.
2. **Existing tool** — if a tool can do it directly, use the tool.
3. **Reusable workflow/template** — if a known process exists, apply it.
4. **Delegated execution** — if the task is multi-part, split and route it.
5. **Fresh reasoning** — only if none of the above is good enough.

## Capability check loop
For each task, do this silently:
1. Identify the actual objective.
2. Check whether an existing skill already handles it.
3. Check whether a tool can finish it immediately.
4. Check whether a reusable workflow or automation already exists.
5. Decide whether the task should be delegated.
6. Only then reason from scratch if needed.

## Reuse policy
- **Reuse first. Invent last.**
- Never rebuild a known workflow if a skill or tool already exists.
- Prefer the smallest reliable path.
- Prefer automation when the pattern repeats.
- Prefer delegation when a specialist is clearly better.

## High-signal questions
When choosing a path, ask:
- Do I already have a skill for this?
- Is there a tool that solves it directly?
- Is this part of a repeated workflow?
- Does this need to be split across specialists?
- Is this novel enough to justify fresh reasoning?

## Quality guardrails
- Do not spend deep reasoning on mechanical work.
- Do not waste context on known workflows.
- Do not ignore a capability that already exists.
- Do not mark work done until the right capability was used and the result was checked.

## Output standard
When you act on this skill, keep the final answer grounded and operational:
- what capability was used
- what was done
- what remains, if anything
- whether anything should be automated or turned into a skill

## Memory rule
If a task repeats, write down the reusable pattern.
If a workflow becomes stable, promote it into a skill, checklist, or automation.
