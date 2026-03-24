#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
DAILY_SCHEDULE="${1:-0 9 * * *}"
WEEKLY_SCHEDULE="${2:-0 18 * * 0}"
MAINTENANCE_LOG="$ROOT_DIR/backups/maintenance.log"
AUDIT_LOG="$ROOT_DIR/backups/audit.log"
DAILY_MARKER="# openclaw-memory-maintenance"
WEEKLY_MARKER="# openclaw-memory-weekly-audit"

if ! command -v crontab >/dev/null 2>&1; then
  echo "crontab not found. Install cron/cronie first."
  exit 1
fi

TMP_CRON="$(mktemp)"
trap 'rm -f "$TMP_CRON"' EXIT

crontab -l 2>/dev/null | grep -vF "$DAILY_MARKER" | grep -vF "$WEEKLY_MARKER" > "$TMP_CRON" || true

# Daily maintenance: validate, back up, write a notification report, and optionally push.
echo "$DAILY_SCHEDULE bash -lc 'cd \"$ROOT_DIR\" && ./memory-maintenance.sh --push --notify >> \"$MAINTENANCE_LOG\" 2>&1' $DAILY_MARKER" >> "$TMP_CRON"

# Weekly audit: create a markdown audit report.
echo "$WEEKLY_SCHEDULE bash -lc 'cd \"$ROOT_DIR\" && python3 memory-v3.py audit --print-report >> \"$AUDIT_LOG\" 2>&1' $WEEKLY_MARKER" >> "$TMP_CRON"

crontab "$TMP_CRON"
echo "Installed cron jobs:"
crontab -l
