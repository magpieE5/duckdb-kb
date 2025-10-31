# Seed Data

This directory contains seed data for bootstrapping the DuckDB knowledge base.

## What is Seed Data?

Seed data provides:
1. **Example entries** demonstrating the knowledge base structure
2. **Platform documentation** about the knowledge base itself
3. **Claude directives** for automatic knowledge capture and conflict detection
4. **Best practices** for organization, tagging, and maintenance

## Files

- `seed.json` - 10 core entries for Layer 1 (base/public layer)
- `import_seed.py` - Script to import seed data into database
- `README.md` - This file

## Seed Entries (Layer 1 - Base)

The seed.json contains 10 platform-focused entries:

### 1. Reference Entries (4)
- **kb-maintenance-comprehensive-guide** - How to maintain and defragment the KB
- **directive-auto-knowledge-capture** - Claude directive on when to save knowledge
- **directive-conflict-detection** - Claude directive on detecting/resolving conflicts
- **duckdb-mcp-architecture** - MCP server architecture overview
- **reference-mcp-server-tools** - Complete tool reference

### 2. Pattern Entries (4)
- **pattern-embedding-best-practices** - Embedding generation guidelines
- **pattern-semantic-search-tips** - How to use semantic search effectively
- **pattern-knowledge-organization** - ID naming, tagging, content structure
- **pattern-layer-tagging** - Three-layer architecture explained

### 3. Command Entry (1)
- **command-backup-restore** - Backup and restore procedures

### 4. Troubleshooting Entries (2)
- **troubleshooting-missing-embeddings** - Fix missing embeddings
- **troubleshooting-slow-semantic-search** - Performance optimization

## Importing Seed Data

### Prerequisites

1. Database created with schema:
   ```bash
   duckdb knowledge.duckdb < schema.sql
   ```

2. Python environment with duckdb installed:
   ```bash
   pip install duckdb
   ```

### Basic Import

```bash
# From seed directory
python import_seed.py

# Or specify paths
python import_seed.py \
    --seed-file seed.json \
    --db-path ../knowledge.duckdb
```

### What Happens During Import

1. Loads seed.json
2. Connects to DuckDB database
3. For each entry:
   - Checks if entry already exists
   - If new: Inserts entry
   - If exists: Asks whether to update
4. Reports summary (imported, updated, skipped)
5. Checks embedding status and reminds to generate if needed

### After Import

Generate embeddings for semantic search:

```bash
# Option 1: Via script
python generate_embeddings.py

# Option 2: Via MCP tool (if server running)
mcp__duckdb-kb__generate_embeddings({})
```

## Customizing Seed Data

### Adding New Entries

Edit `seed.json` and add entries following this schema:

```json
{
  "id": "unique-kebab-case-id",
  "category": "pattern|command|troubleshooting|reference|issue|other",
  "title": "Human Readable Title",
  "tags": ["relevant", "tags", "layer:base"],
  "content": "# Markdown Content\n\nFull entry content here...",
  "metadata": {}
}
```

### Guidelines for Seed Entries

**Layer 1 (base) seed entries should:**
- ✅ Be platform/KB-focused (not domain-specific)
- ✅ Demonstrate the system capabilities
- ✅ Include Claude directives for auto-capture
- ✅ Show best practices for organization
- ✅ Be tagged with `layer:base`
- ✅ Have good markdown structure
- ✅ Include examples where helpful

**Avoid in Layer 1:**
- ❌ Organization-specific content
- ❌ Domain knowledge (SQL, Oracle, etc.)
- ❌ Personal notes or tickets
- ❌ Private/sensitive information

### Creating Layer 2/3 Seed Files

For organization or personal layers:

```bash
# Create layer-specific seed
cp seed.json ../pds-kb/seed/pds_seed.json

# Edit to add organization-specific entries
# Tag with layer:pds or layer:team

# Import to layer-specific database
python import_seed.py \
    --seed-file ../pds-kb/seed/pds_seed.json \
    --db-path ../pds-kb/knowledge.duckdb
```

## Seed Entry Design Principles

### 1. Self-Documenting

Seed entries document the system itself. Claude can discover functionality by searching the knowledge base.

**Example:**
- User: "How do I use this knowledge base?"
- Claude: *Searches KB, finds directive-auto-knowledge-capture*
- Claude: Returns guidelines automatically

### 2. Bootstrap Problem Solution

The system must teach itself how to grow. Seed entries provide:
- When to save knowledge
- How to detect conflicts
- How to organize entries
- How to defragment

### 3. Demonstrative

Each entry demonstrates:
- Proper ID naming (kebab-case)
- Good tagging (4-6 relevant tags)
- Clear structure (Problem → Solution → Example)
- Layer tagging for distribution

### 4. Actionable

Entries include:
- Concrete examples
- Code snippets
- Commands to run
- Decision-making guidelines

## Verifying Seed Import

After importing, verify:

```bash
# Connect to database
duckdb knowledge.duckdb

# Check entry count
SELECT COUNT(*) FROM knowledge;
-- Should show 10 entries (or more if you had existing)

# Check entries imported
SELECT id, title, category FROM knowledge WHERE list_contains(tags, 'layer:base');

# Check embedding status
SELECT COUNT(*) as total,
       COUNT(embedding) as with_embeddings
FROM knowledge;
```

## Updating Seed Data

To update seed entries after changes:

```bash
# Option 1: Re-import (will ask to update each existing entry)
python import_seed.py

# Option 2: Export current KB as new seed
python ../export.py --output seed_updated.json --filter "layer:base"

# Option 3: Manually edit seed.json and re-import
```

## Exporting Layer 1 for Distribution

To create a clean Layer 1 distribution:

```bash
# Export only layer:base tagged entries
python ../export.py \
    --output layer1_distribution.json \
    --filter-tags layer:base

# This becomes your distributable seed.json for open source
```

## Best Practices

1. **Keep seed minimal** - 10-15 entries max for Layer 1
2. **Update regularly** - As platform evolves, update seed docs
3. **Test imports** - Periodically test seed import on fresh database
4. **Document changes** - Note what changed when updating seed
5. **Version control** - Commit seed.json changes with clear messages

## Troubleshooting

### "Entry already exists"

This is normal. The script asks whether to update each existing entry. This prevents accidental overwrites.

To force update all:
```bash
# TODO: Add --force flag to import_seed.py
```

### "No embeddings generated"

Seed import doesn't generate embeddings automatically (for speed). Generate after import:

```bash
python generate_embeddings.py
```

### "Database not found"

Create database first:
```bash
duckdb knowledge.duckdb < schema.sql
```

### Import fails with "knowledge table not found"

Run schema.sql to create tables:
```bash
duckdb knowledge.duckdb < schema.sql
```

## Advanced: Layered Seed Strategy

For three-layer architecture:

```
duckdb-kb/seed/
  └── seed.json                 # 10 base entries (layer:base)

pds-kb/seed/
  └── pds_seed.json            # 20-30 PDS-specific entries (layer:pds)
      (imports layer:base automatically)

brock-kb/seed/
  └── personal_seed.json       # Personal entries (layer:personal)
      (imports layer:base + layer:pds automatically)
```

Each layer imports previous layers' seed data plus its own additions.

## Related Documentation

- `../README.md` - Full MCP server documentation
- `../SETUP.md` - Setup and configuration guide
- `../scripts/defrag.py` - Defragmentation tool
- `../schema.sql` - Database schema

## Questions?

The seed entries themselves contain detailed documentation:
- Search for "directive" entries for Claude guidelines
- Search for "pattern" entries for best practices
- Search for "troubleshooting" for common issues
