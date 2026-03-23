#!/bin/bash
# memory-backup.sh - Backup script for memory system
# Created: 2026-03-23

MEMORY_DIR="$HOME/.openclaw/memory"
BACKUP_DIR="$HOME/.openclaw/memory-backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="memory_backup_$DATE.tar.gz"

echo "💾 Memory System Backup"
echo "======================="
echo ""

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Create backup
echo "Creating backup..."
cd "$MEMORY_DIR/.."
tar -czf "$BACKUP_DIR/$BACKUP_FILE" memory/

if [ $? -eq 0 ]; then
    echo "✅ Backup created: $BACKUP_DIR/$BACKUP_FILE"
    echo "   Size: $(du -h $BACKUP_DIR/$BACKUP_FILE | cut -f1)"
    
    # Keep only last 10 backups
    ls -t $BACKUP_DIR/memory_backup_*.tar.gz | tail -n +11 | xargs -r rm
    echo "   Retention: Kept last 10 backups"
else
    echo "❌ Backup failed"
    exit 1
fi

# Optional: Git backup if initialized
if [ -d "$MEMORY_DIR/../.git" ]; then
    echo ""
    echo "📤 Pushing to git..."
    cd "$MEMORY_DIR/.."
    git add memory/
    git commit -m "Memory backup $(date -Iseconds)" --quiet
    git push origin main --quiet 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✅ Synced to remote repository"
    else
        echo "⚠️  Git push failed (check remote)"
    fi
fi

echo ""
echo "Backup complete!"