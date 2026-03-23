# Memory System v3 - Implementation Plan

## Goal
Build a more reliable, more automated, and more searchable memory system than v2, while keeping the good parts:
- Human-readable Markdown logs
- Fast structured querying
- Strong project continuity
- Low-friction updates

## v3 Principles
1. **Trust but verify** — every auto-generated entry must be reviewable.
2. **Single source of truth** — database and files must stay synchronized.
3. **Schema-first** — all memory objects should validate before write.
4. **Retrieval-first** — search and dashboards should be faster than manual browsing.
5. **Recovery-first** — backups and restore flow are mandatory, not optional.
6. **Low-noise** — capture meaningful work only.

## Problems v3 Must Solve
- Legacy dashboard drift
- Manual log inconsistency
- Missing entry triggers / workflow rules
- Weak schema enforcement
- Poor stale-item surfacing
- Backup/recovery not integrated enough
- Search quality limited to exact/FTS-style queries
- No easy migration/versioning path

## Proposed v3 Improvements

### 1) Memory Schema v3
Add required fields and stronger validation:
- `id`
- `date`
- `project`
- `topic`
- `context`
- `summary`
- `decisions[]`
- `tasks[]`
- `blockers[]`
- `next_steps`
- `owner`
- `priority`
- `status`
- `participants[]`
- `tags[]`
- `references[]`
- `source`
- `confidence`
- `created_at`
- `updated_at`
- `schema_version`

Validation rules:
- Required fields cannot be blank
- Priority/status values must come from allowed enums
- References must be resolvable or explicitly marked external
- Confidence is mandatory for auto-extracted entries

### 2) Entry Workflow Rules
Create entries when:
- A task starts and is likely to take > 15 minutes
- A decision is made
- A blocker appears or changes
- A task completes
- A project changes status
- A significant plan is approved

Add a review state:
- `draft` → `reviewed` → `committed`

### 3) Better Search
v3 search should support:
- Exact keyword search
- Filters: project, status, date range, priority, owner, tags
- Recent-first and relevance ranking
- Similarity search for near-duplicate entries
- “Open blockers” and “overdue tasks” prebuilt queries

### 4) Dashboard v3
Dashboard should include:
- Today summary
- Active projects
- Open tasks
- Blockers by severity and age
- Recent decisions
- Overdue follow-ups
- Stale items
- Timeline of important events
- Search shortcuts

### 5) Backup and Recovery
Add first-class backup lifecycle:
- Daily automatic backup
- Git commits for memory files
- Restore command
- Integrity check command
- Snapshot tags by date

### 6) Automated Sync
- File changes update DB
- DB changes regenerate Markdown
- Integrity checker compares both sides
- Conflicts require explicit resolution

### 7) Agent-Generated Memory
Improve the assistant workflow:
- Parse conversations into candidates
- Classify items as task/decision/blocker/note
- Assign confidence score
- Require approval before commit for low-confidence extraction

### 8) Versioning / Migration
- Introduce `schema_version`
- Provide migration scripts from v2 → v3
- Keep export path to JSON and Markdown
- Preserve old logs in archive mode

## Proposed File Structure
```text
memory-v3/
├── cli/
│   ├── memory.py
│   └── commands/
├── core/
│   ├── models.py
│   ├── validation.py
│   ├── sync.py
│   ├── search.py
│   └── backups.py
├── integrations/
│   ├── conversation_parser.py
│   ├── approval_queue.py
│   └── agent_extractor.py
├── dashboards/
│   ├── generate.py
│   ├── templates/
│   └── views/
├── migrations/
│   ├── v2_to_v3.py
│   └── schema.sql
├── tests/
└── docs/
```

## Proposed v3 Phases

### Phase 0 - Stabilize v2
- Update dashboard to current state
- Enable backups and restore
- Add git remote sync

### Phase 1 - Schema and Validation
- Implement v3 models
- Add validators
- Add confidence scoring for auto-entry
- Add approval workflow

### Phase 2 - Search and Dashboard
- Improve search filters/ranking
- Add stale-item detection
- Generate richer dashboards

### Phase 3 - Sync and Recovery
- File/DB bidirectional sync
- Conflict detection
- Restore and integrity commands

### Phase 4 - Automation
- Cron-based backup/checks
- Auto reminder surfacing
- Conversation parsing pipeline

## Success Criteria
- No stale dashboard entries for active projects
- Every entry has required fields
- Search finds items by project/date/status/tags
- Backups restore cleanly
- Auto-extracted items can be reviewed before commit
- The system stays reliable over long usage

## Immediate Next Steps
1. Approve this plan
2. Decide v3 directory/location
3. Implement validation + schema versioning first
4. Add restore/backup integration
5. Upgrade dashboard generation

## Notes
- v3 should evolve from v2, not replace it abruptly.
- Keep human-readable files as the primary interface.
- Use SQLite as the query engine and Markdown as the audit trail.
