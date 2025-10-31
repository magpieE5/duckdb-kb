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

The seed.json contains 12 platform-focused entries:

- **5 Reference entries** - KB maintenance, directives, MCP architecture
- **4 Pattern entries** - Embedding best practices, semantic search, organization, layer tagging
- **2 Troubleshooting entries** - Missing embeddings, slow search
- **1 Command entry** - Backup and restore procedures

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
SELECT COUNT(*) FROM knowledge;  -- Should be 12

# Check entries imported
SELECT id, category FROM knowledge WHERE list_contains(tags, 'layer:base');

# Check embedding status
SELECT COUNT(*) as total, COUNT(embedding) as with_embeddings FROM knowledge;
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

1. **Keep seed minimal** - 12-15 entries for Layer 1
2. **Test imports** - Verify on fresh database periodically
3. **Version control** - Commit seed.json changes with clear messages

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

## Advanced: Fork-Based Layer Strategy

**IMPORTANT**: Layers are forks, not separate databases. Each layer contains all previous layers.

### Layer 1: Base (duckdb-kb)
```bash
# This repo - 12 base entries
seed/seed.json  # Contains layer:base entries for public distribution
```

### Layer 2: Team Fork
```bash
# Fork the entire repo
cp -r duckdb-kb team-kb
cd team-kb

# Database now has 12 base entries
# Add team-specific entries with layer:team tag
# Result: ONE database with base + team knowledge

# Export for team distribution
python export.py --filter-tags layer:base,layer:team
```

### Layer 3: Personal Fork
```bash
# Fork the team repo
cp -r team-kb personal-kb
cd personal-kb

# Database has: base + team entries
# Add personal entries with layer:personal tag
# Result: ONE database with ALL layers

# Keep private (don't distribute)
```

**Key Concept**: You run only ONE MCP server at your current layer. It contains everything you need from all previous layers.

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
