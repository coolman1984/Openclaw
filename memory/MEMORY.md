# MEMORY.md - Operational Memory System

**Role:** Operational Memory Manager  
**Purpose:** Maintain structured, searchable records of all work, decisions, projects, and context.

---

## Dashboard

### Today's Summary (2026-03-23)
- Initial setup and identity establishment
- OpenCode CLI installation and configuration
- OpenCode Go subscription validated
- Multi-agent coding system created
- Dev Assistant app built
- **Operational Memory System v2 completed and initialized**
- **Memory System v3 planning requested**

### Active Projects
| Project | Status | Last Updated | Next Action |
|---------|--------|--------------|-------------|
| Memory System v2 | Complete | 2026-03-23 | Keep using it; stabilize and monitor |
| Memory System v3 | Planning | 2026-03-23 | Draft implementation plan and improvements |
| OpenCode Setup | In Progress | 2026-03-23 | Validate config with Go API and environment constraints |
| OpenCode Go | Active | 2026-03-23 | Use Go models for coding tasks |

### Pending Tasks
- [ ] Finalize v3 implementation plan
- [ ] Add git remote backup for memory system
- [ ] Set up automated cron backups
- [ ] Migrate dashboard and indexes to v2 outputs
- [ ] Reduce stale/duplicate entries in legacy logs

### Current Blockers
1. **GitHub sync** — repository has been successfully pushed to GitHub via SSH
   - Status: Complete
2. **Termux/OpenCode binary compatibility** — newest OpenCode binary requires libc unavailable in this environment
   - Workaround: Use the Go API directly or run OpenCode in a glibc Linux environment
3. **Legacy dashboard drift** — older summary still reflects pre-v2 state
   - Resolution: Rebuild dashboard from current v2 memory data

### Recent Decisions
- Memory system v2 is the production baseline
- v3 will focus on reliability, automation, integrity, and retrieval quality
- OpenCode Go models are the preferred model stack for coding, planning, and review
- Keep file-based human-readable logs plus SQLite indexing

---

## Project Records

### OpenCode CLI Setup
- **Objective:** Install and configure OpenCode AI coding assistant
- **Current Status:** Core installed, environment compatibility limited
- **Key Decisions:** 
  - Installed v0.0.55 from original repo (archived but functional)
  - fzf installed successfully (v0.70.0)
  - ripgrep deferred due to environment constraints
- **Open Tasks:**
  - [ ] Validate Go API usage in this environment
  - [ ] Document fallback workflow for Termux
- **Blockers:** glibc/libraries for newer OpenCode binary
- **Next Milestone:** Stable coding workflow using Go API or Linux host
- **References:**
  - Location: `~/.opencode/bin/opencode`
  - Config: `~/.opencode.json`
  - Docs: https://opencode.ai/docs

### OpenCode Go
- **Objective:** Use the Go subscription models for coding work
- **Current Status:** Active and validated via API
- **Key Decisions:**
  - Use `glm-5` for coding
  - Use `kimi-k2.5` for planning/thinking
  - Use `minimax-m2.7` for review/testing
- **Open Tasks:**
  - [ ] Build a cleaner model-selection workflow
  - [ ] Add local helper scripts for API calls
- **Blockers:** None
- **Next Milestone:** Smooth model routing for tasks
- **References:**
  - Docs: https://opencode.ai/docs/go
  - Endpoint: `https://opencode.ai/zen/go/v1`

### Memory System v2
- **Objective:** Production-ready operational memory system
- **Current Status:** Complete and running
- **Key Decisions:**
  - SQLite + Markdown storage
  - FTS5 search
  - Auto-escalation for blockers
  - Backup script for recovery
- **Open Tasks:**
  - [ ] Add git remote backup
  - [ ] Automate cron jobs
  - [ ] Rebuild dashboard from current data
- **Blockers:** Legacy dashboard drift
- **Next Milestone:** Stable daily usage and backups
- **References:**
  - CLI: `~/.openclaw/workspace/memory-system/memory-manager.py`
  - DB: `~/.openclaw/memory/data/memory.db`
  - Backup: `~/.openclaw/workspace/memory-system/memory-backup.sh`

### Memory System v3
- **Objective:** Improve memory reliability, retrieval quality, and automation
- **Current Status:** Planning
- **Key Decisions:**
  - v3 will add stronger schema validation and workflow enforcement
  - v3 will improve dashboard freshness and indexing
  - v3 will add backup/versioning/restore discipline as first-class features
- **Open Tasks:**
  - [ ] Write v3 implementation plan
  - [ ] Define migration path from v2 to v3
  - [ ] Decide automation triggers and review cycle
- **Blockers:** None
- **Next Milestone:** Approved v3 plan
- **References:**
  - Proposed plan file: `memory-system/IMPLEMENTATION_PLAN_V3.md`

---

## Daily Log Index

| Date | Projects | Key Events |
|------|----------|------------|
| 2026-03-23 | OpenCode Setup, Identity Establishment, Memory System v2, Memory System v3 | Initial setup, OpenCode/Go work, memory system build, v3 planning |

---

## Search Index

**By Topic:**
- OpenCode → Project: OpenCode CLI Setup
- Go → Project: OpenCode Go
- Memory System v2 → Production memory baseline
- Memory System v3 → Planning
- Dashboard → Memory System v2/v3 status

**By Date:**
- 2026-03-23 → Initial setup day; v2 complete; v3 planning

---

_Last Updated: 2026-03-23 20:00 GMT+2_