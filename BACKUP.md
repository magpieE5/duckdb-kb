# Backup & Recovery Strategy

**Critical**: The `knowledge.duckdb` file contains all your knowledge base data. Corruption or loss would be catastrophic. This document outlines a multi-layered backup strategy.

## Backup Strategy Overview

We use a **3-tier backup approach**:

1. **Local Binary Backups** - Fast, complete copies including embeddings
2. **JSON Exports** - Git-friendly, human-readable, portable
3. **Cloud Sync** - Optional offsite backup (iCloud/Dropbox/etc)

---

## Tier 1: Local Binary Backups

**Purpose**: Quick disaster recovery with full data including embeddings

**Script**: `backup.sh`

### Usage

```bash
# Create a backup now
./backup.sh

# Keep backups for 60 days (default: 30)
./backup.sh --keep-days 60
```

### What It Does

- Creates timestamped copy: `backups/knowledge_20250130_152030.duckdb`
- Verifies backup integrity
- Shows database stats
- Deletes backups older than N days (prevents disk bloat)

### Backup Schedule Recommendations

**Option 1: Manual backups**
```bash
# Before making significant changes:
./backup.sh
```

**Option 2: Scheduled backups (cron)**
```bash
# Edit crontab
crontab -e

# Add this line for daily backups at 2 AM:
0 2 * * * cd /path/to/duckdb-kb && ./backup.sh >> backups/backup.log 2>&1
```

**Option 3: Pre-commit hook (backup before git commits)**
```bash
# Create .git/hooks/pre-commit in your project
#!/bin/bash
cd /path/to/duckdb-kb
./backup.sh --keep-days 7 > /dev/null 2>&1
```

### Recovery from Binary Backup

```bash
# Option 1: Use restore script
python restore.py --from-backup backups/knowledge_20250130_152030.duckdb

# Option 2: Manual copy
cp backups/knowledge_20250130_152030.duckdb knowledge.duckdb
```

**Restoration time**: ~1 second (file copy)

---

## Tier 2: JSON Exports (Git-Friendly)

**Purpose**: Version-controlled, human-readable backups

**Script**: `export.py`

### Usage

```bash
# Export to JSON (default)
python export.py

# Export to SQL
python export.py --format sql

# Export both formats
python export.py --format both

# Custom output directory
python export.py --output ~/backups/knowledge-exports
```

### What Gets Exported

**JSON format:**
- `exports/knowledge_YYYYMMDD_HHMMSS.json` - All entries (no embeddings)
- `exports/links_YYYYMMDD_HHMMSS.json` - All relationships
- `exports/stats_YYYYMMDD_HHMMSS.json` - Database statistics
- `exports/knowledge_latest.json` - Symlink to latest export
- `exports/links_latest.json` - Symlink to latest links

**SQL format:**
- `exports/knowledge_YYYYMMDD_HHMMSS.sql` - Full SQL dump

### Why JSON Instead of Git + DuckDB?

| Aspect | Binary .duckdb in Git | JSON Exports in Git |
|--------|----------------------|---------------------|
| Diff visibility | None (binary) | Full (readable) |
| Merge conflicts | Impossible | Manageable |
| File size | ~5MB + history | ~500KB text |
| Git efficiency | Poor | Excellent |
| Embeddings | Included | Excluded (regenerated) |

### Git Integration

```bash
# Initial setup
git init
echo "knowledge.duckdb" >> .gitignore
echo "backups/" >> .gitignore
echo "venv/" >> .gitignore

# Commit exports only
git add exports/knowledge_latest.json exports/links_latest.json
git commit -m "Backup knowledge base"

# Push to remote (GitHub/GitLab)
git remote add origin YOUR_REPO_URL
git push origin main
```

### Recovery from JSON Export

```bash
# Restore from latest export
python restore.py --from-json exports/knowledge_latest.json

# Restore from specific backup
python restore.py --from-json exports/knowledge_20250130_152030.json

# Regenerate embeddings (required)
python generate_embeddings.py
```

**Restoration time**: ~10 seconds + embedding generation (~30 seconds)

---

## Tier 3: Cloud Sync (Optional)

**Purpose**: Offsite backup protection

### Option A: Cloud Sync the Entire Directory

```bash
# Move duckdb-mcp to synced location
mv /path/to/duckdb-kb ~/Library/CloudStorage/Dropbox/

# Update Claude Code config to new path
```

**Pros**: Automatic, continuous sync
**Cons**: May cause conflicts if editing on multiple machines

### Option B: Sync Backups Directory Only

```bash
# Create symlink in cloud folder
ln -s /path/to/duckdb-kb/backups ~/Library/CloudStorage/Dropbox/duckdb-backups
```

**Pros**: No conflicts, backups are offsite
**Cons**: Manual backup script execution needed

### Option C: Sync Exports Directory

```bash
# Symlink exports to cloud
ln -s /path/to/duckdb-kb/exports ~/Library/CloudStorage/iCloud/duckdb-exports
```

**Pros**: Git-friendly exports are offsite, small files
**Cons**: Need to regenerate embeddings on restore

---

## Recommended Backup Workflow

### Daily Workflow
```bash
# Morning: Check system health
python -c "
import duckdb
con = duckdb.connect('knowledge.duckdb', read_only=True)
stats = con.execute('SELECT * FROM knowledge_stats').fetchone()
print(f'Entries: {stats[0]}, With embeddings: {stats[1]}')
"

# Throughout the day: Use knowledge base normally
# Claude Code auto-saves through MCP

# Evening: Export to JSON for git
python export.py
git add exports/knowledge_latest.json
git commit -m "Daily backup $(date +%Y-%m-%d)"
git push
```

### Weekly Workflow
```bash
# Weekly binary backup
./backup.sh --keep-days 30

# Verify backup integrity
ls -lh backups/ | tail -5
```

### Before Major Changes
```bash
# Create checkpoint backup
./backup.sh
echo "Checkpoint created before: [describe change]" >> backups/CHANGELOG.md
```

---

## Recovery Scenarios

### Scenario 1: Database Corruption (Today)

**Solution**: Restore from latest binary backup
```bash
python restore.py --from-backup backups/knowledge_$(date +%Y%m%d)_*.duckdb
# Loss: None or minimal (< 1 day)
```

### Scenario 2: Database Deleted (Recent Backup Available)

**Solution**: Restore from recent binary backup
```bash
# Find latest backup
ls -t backups/*.duckdb | head -1

# Restore
python restore.py --from-backup backups/knowledge_20250128_020000.duckdb
# Loss: Up to 1 day (depending on backup frequency)
```

### Scenario 3: All Local Backups Lost (Git Available)

**Solution**: Restore from git exports
```bash
# Clone from remote
git clone YOUR_REPO_URL recovered-knowledge
cd recovered-knowledge

# Restore from JSON
python restore.py --from-json exports/knowledge_latest.json

# Regenerate embeddings
python generate_embeddings.py
# Loss: Changes since last export + need to regenerate embeddings
```

### Scenario 4: Complete Disaster (Cloud Backup Available)

**Solution**: Download from cloud sync
```bash
# Download from Dropbox/iCloud
# Then restore as above
```

---

## Backup Verification

### Check Backup Integrity

```bash
# Verify binary backup
duckdb backups/knowledge_20250130_152030.duckdb <<SQL
SELECT COUNT(*) as total FROM knowledge;
SELECT COUNT(*) as with_embeddings FROM knowledge WHERE embedding IS NOT NULL;
SQL

# Verify JSON export
python -c "
import json
with open('exports/knowledge_latest.json') as f:
    data = json.load(f)
print(f'Entries in JSON: {len(data)}')
"
```

### Test Restore Process

```bash
# Test restore to temporary database
python restore.py --from-backup backups/latest.duckdb --db-path test_restore.duckdb
rm test_restore.duckdb  # Clean up after test
```

---

## Backup Best Practices

1. **3-2-1 Rule**: 3 copies, 2 different media, 1 offsite
   - ✅ Original database
   - ✅ Local binary backup (different disk location)
   - ✅ Cloud sync or git remote

2. **Test Restores**: Verify backups work before you need them
   ```bash
   # Monthly restore test
   python restore.py --from-backup backups/latest.duckdb --db-path test.duckdb
   ```

3. **Automate**: Set up cron jobs or git hooks

4. **Document Changes**: Keep CHANGELOG.md in backups directory

5. **Monitor Backup Size**: Watch for unusual growth
   ```bash
   du -sh backups/ exports/
   ```

---

## Automation Setup

### Create Backup Cron Job

```bash
# Edit crontab
crontab -e

# Add these lines:

# Daily binary backup at 2 AM
0 2 * * * cd /path/to/duckdb-kb && ./backup.sh >> backups/backup.log 2>&1

# Weekly JSON export and git commit at 3 AM on Sundays
0 3 * * 0 cd /path/to/duckdb-kb && python export.py && git add exports/*.json && git commit -m "Weekly backup $(date +%Y-%m-%d)" && git push >> exports/export.log 2>&1
```

### Create Git Hook for Auto-Export

```bash
# Create .git/hooks/pre-push
cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash
cd /path/to/duckdb-kb
python export.py
git add exports/knowledge_latest.json exports/links_latest.json
EOF

chmod +x .git/hooks/pre-push
```

---

## File Size Considerations

| File | Typical Size | Notes |
|------|--------------|-------|
| knowledge.duckdb | 5-10 MB | Includes embeddings (1536 floats × entries) |
| Binary backup | 5-10 MB | Exact copy of .duckdb |
| JSON export | 500 KB - 2 MB | No embeddings, human-readable |
| SQL export | 1-3 MB | No embeddings, includes all data |

**Storage requirements for 30 days of daily backups:**
- Binary: ~300 MB (30 × 10 MB)
- JSON: ~60 MB (30 × 2 MB)
- Git repo: ~5-10 MB (excellent compression for JSON)

---

## Quick Reference

```bash
# BACKUP
./backup.sh                    # Binary backup to backups/
python export.py              # JSON export to exports/

# RESTORE
python restore.py --from-backup backups/latest.duckdb  # From binary
python restore.py --from-json exports/knowledge_latest.json  # From JSON

# VERIFY
duckdb knowledge.duckdb "SELECT * FROM knowledge_stats"

# GIT BACKUP
git add exports/knowledge_latest.json
git commit -m "Backup $(date +%Y-%m-%d)"
git push
```

---

## Support

If you encounter issues with backups or recovery:

1. Check backup integrity (see Verification section above)
2. Review backup logs: `backups/backup.log`
3. Test with a temporary restore before overwriting main database
4. Keep multiple backup generations (recommended: 30 days)

**Remember**: The best backup strategy is one you actually use! Start simple (weekly exports to git) and automate as needed.
