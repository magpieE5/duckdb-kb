# Backup & Recovery Strategy

The `knowledge.duckdb` file contains all your knowledge base data. This document outlines the recommended backup approach using **human-readable JSON exports**.

## Why JSON Backups?

✅ **Human-readable** - Review and edit before restore
✅ **Git-friendly** - Track changes, see diffs
✅ **Portable** - Works across platforms
✅ **Safe** - Can inspect/modify before applying
❌ **Embeddings not included** - Need to regenerate (small cost)

**Manual binary copies:** You can always `cp knowledge.duckdb knowledge.backup.duckdb` manually if you need a quick snapshot before major changes.

---

## Quick Reference

```bash
# BACKUP (export to JSON)
python export.py

# RESTORE (from JSON)
python restore.py --from-json exports/knowledge_latest.json
python generate_embeddings.py  # Regenerate embeddings

# VERIFY
python -c "import json; print(len(json.load(open('exports/knowledge_latest.json'))))"
```

---

## Backup Workflow

### Daily/After Changes

```bash
# Export to JSON
python export.py

# Commit to git
git add exports/knowledge_latest.json exports/links_latest.json
git commit -m "Backup: $(date +%Y-%m-%d)"
git push
```

**What this creates:**
- `exports/knowledge_YYYYMMDD_HHMMSS.json` - Timestamped export
- `exports/knowledge_latest.json` - Symlink to latest (git-tracked)
- `exports/links_YYYYMMDD_HHMMSS.json` - Relationships
- `exports/links_latest.json` - Symlink to latest

### Before Major Changes

```bash
# Quick manual copy for immediate rollback
cp knowledge.duckdb knowledge.duckdb.backup

# Make your changes...

# If something goes wrong:
cp knowledge.duckdb.backup knowledge.duckdb
```

---

## Recovery Scenarios

### Restore from Recent JSON Export

```bash
# Restore from latest
python restore.py --from-json exports/knowledge_latest.json

# Regenerate embeddings
python generate_embeddings.py
```

**Time:** ~10 seconds + ~30 seconds for embeddings (12 entries)

### Restore from Specific Export

```bash
# List available exports
ls -lt exports/knowledge_*.json

# Restore from specific date
python restore.py --from-json exports/knowledge_20250130_120000.json
python generate_embeddings.py
```

### Complete Data Loss (Git Available)

```bash
# Clone from remote
git clone YOUR_REPO_URL recovered-kb
cd recovered-kb

# Restore from git-tracked export
python restore.py --from-json exports/knowledge_latest.json
python generate_embeddings.py
```

---

## Git Integration

### Initial Setup

```bash
# Ensure exports are tracked
git add exports/knowledge_latest.json exports/links_latest.json
git commit -m "Add knowledge base exports"

# Ensure database is ignored (it's already in .gitignore)
grep "*.duckdb" .gitignore  # Should show *.duckdb
```

### Automated Git Backups

**Option 1: Pre-commit hook** (export before every commit)

```bash
# Create .git/hooks/pre-commit
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
cd /path/to/duckdb-kb
python export.py > /dev/null 2>&1
git add exports/knowledge_latest.json exports/links_latest.json
EOF

chmod +x .git/hooks/pre-commit
```

**Option 2: Cron job** (weekly exports)

```bash
crontab -e

# Add: Weekly export on Sundays at 3 AM
0 3 * * 0 cd /path/to/duckdb-kb && python export.py && git add exports/*.json && git commit -m "Weekly backup $(date +%Y-%m-%d)" && git push
```

---

## Reviewing Backups Before Restore

This is the key advantage of JSON backups - you can inspect and edit them!

### Inspect JSON Export

```bash
# View entry count
python -c "
import json
data = json.load(open('exports/knowledge_latest.json'))
print(f'Entries: {len(data)}')
"

# View specific entry
python -c "
import json
data = json.load(open('exports/knowledge_latest.json'))
entry = [e for e in data if e['id'] == 'some-entry-id'][0]
print(entry['content'])
"
```

### Edit Before Restore

```bash
# Make a copy
cp exports/knowledge_latest.json exports/knowledge_edited.json

# Edit with your favorite editor
code exports/knowledge_edited.json  # or vim, nano, etc.

# Restore the edited version
python restore.py --from-json exports/knowledge_edited.json
python generate_embeddings.py
```

**Use cases:**
- Remove sensitive entries before sharing
- Fix errors in bulk
- Merge entries manually
- Update tags across multiple entries

---

## File Sizes

| File | Typical Size | Notes |
|------|--------------|-------|
| knowledge.duckdb | 2-5 MB | Includes embeddings (1536 floats × entries) |
| JSON export | 100-500 KB | No embeddings, human-readable |
| Git repo with exports | 500 KB - 2 MB | Excellent compression |

**Storage:** Git handles JSON very efficiently. 30 days of exports might only add ~500KB to your repo.

---

## Best Practices

1. **Export regularly** - After significant changes
2. **Commit exports to git** - Free version control
3. **Use latest symlinks** - Easier to reference in scripts
4. **Test restores** - Verify your backups work
5. **Manual copies optional** - Use `cp` for quick snapshots if needed

---

## Automation Examples

### Daily Export Script

```bash
#!/bin/bash
# daily-backup.sh

cd /path/to/duckdb-kb
python export.py
git add exports/knowledge_latest.json exports/links_latest.json
git commit -m "Automated backup: $(date +%Y-%m-%d)"
git push
```

### Recovery Script

```bash
#!/bin/bash
# restore-latest.sh

cd /path/to/duckdb-kb
python restore.py --from-json exports/knowledge_latest.json
python generate_embeddings.py
echo "✅ Restored from latest export"
```

---

## Why Not Binary Backups?

| Aspect | Binary .duckdb Copy | JSON Export |
|--------|-------------------|-------------|
| Review before restore | ❌ No | ✅ Yes |
| Edit before restore | ❌ No | ✅ Yes |
| Git diffs | ❌ Binary blob | ✅ Line-by-line |
| Human readable | ❌ No | ✅ Yes |
| Embeddings included | ✅ Yes | ❌ No (regenerate) |
| Size | ~3-5 MB | ~200-500 KB |

**Bottom line:** JSON exports give you **control and visibility**. The small cost of regenerating embeddings is worth it for human-readable, editable backups.

---

## Emergency: Database Corrupted Right Now

```bash
# Quick recovery from latest export
python restore.py --from-json exports/knowledge_latest.json --force
python generate_embeddings.py

# Or from git if you don't trust local exports
git pull
python restore.py --from-json exports/knowledge_latest.json --force
python generate_embeddings.py
```

**Recovery time:** < 2 minutes

---

## Questions?

- **Q: Can I still make manual binary copies?**
  A: Yes! `cp knowledge.duckdb backup.duckdb` works fine for quick snapshots.

- **Q: Do I need both JSON and binary backups?**
  A: No. JSON exports are sufficient. Binary copies are optional for convenience.

- **Q: How much does embedding regeneration cost?**
  A: ~$0.0002 for 12 entries, ~$0.002 for 100 entries (OpenAI pricing).

- **Q: Can I backup without embeddings?**
  A: JSON exports already exclude embeddings. They're regenerated on restore.
