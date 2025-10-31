# DuckDB Knowledge Base - Complete Setup Guide

**Version:** 2.0
**Updated:** 2025-10-31
**For:** New users setting up from scratch

---

## Quick Start (Recommended)

The MCP server now **auto-initializes** the database on first run! Just configure the environment variable and start using it.

### 1. Install Dependencies

```bash
cd ~/duckdb-kb
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure MCP Server

Add to your Claude Code configuration (`~/.claude.json`):

```json
{
  "projects": {
    "/your/project/path": {
      "mcpServers": {
        "duckdb-kb": {
          "type": "stdio",
          "command": "/absolute/path/to/duckdb-kb/venv/bin/python",
          "args": ["/absolute/path/to/duckdb-kb/mcp_server.py"],
          "env": {
            "KNOWLEDGE_DB_PATH": "/absolute/path/to/duckdb-kb/knowledge.duckdb"
          }
        }
      }
    }
  }
}
```

**CRITICAL:**
- Use **absolute paths** for all paths
- The `KNOWLEDGE_DB_PATH` environment variable is **required**
- Replace `/your/project/path` and `/absolute/path/to/duckdb-kb` with your actual paths

### 3. Start Using

That's it! The database will auto-initialize on first use. Restart Claude Code and start adding knowledge entries.

---

## Manual Initialization (Optional)

If you prefer to initialize the database manually or want to validate it:

### Initialize a New Database

```bash
cd ~/duckdb-kb
source venv/bin/activate
python scripts/init_db.py
```

This will:
- Create the `knowledge.duckdb` file
- Set up tables (`knowledge`, `knowledge_links`)
- Create indexes and views
- Add helper functions for search
- Install VSS extension (if available)

### Validate Existing Database

```bash
python scripts/init_db.py --validate
```

This checks:
- Tables exist
- Functions are present
- Database statistics
- VSS extension status

### Initialize Custom Database

```bash
python scripts/init_db.py --db /path/to/custom.duckdb
```

---

## What Gets Created

### Tables

1. **knowledge** - Main table for entries
   - `id` (PRIMARY KEY)
   - `category`, `title`, `tags`, `content`
   - `metadata` (JSON)
   - `embedding` (FLOAT[1536]) for semantic search
   - `created`, `updated` timestamps

2. **knowledge_links** - Relationship graph
   - `from_id`, `to_id`, `link_type`
   - Supports: 'related', 'parent', 'child', 'references'

### Functions/Macros

- `get_with_related()` - Get entry with linked entries
- `semantic_search()` - Vector similarity search
- `hybrid_search()` - Combined SQL + semantic search
- `database_summary()` - Database statistics

### Views

- `recent_knowledge` - Entries from last 30 days
- `knowledge_stats` - Statistics by category
- `tag_usage` - Tag frequency analysis

---

## Environment Variables

### Required

- **KNOWLEDGE_DB_PATH** - Path to your database file
  - Example: `/Users/you/duckdb-kb/knowledge.duckdb`
  - Must be absolute path
  - Used by MCP server to locate database

### Optional

- **OPENAI_API_KEY** - For OpenAI embeddings (recommended)
  - Get from: https://platform.openai.com/api-keys
  - Sign up, create API key, copy key (starts with `sk-proj-...`)
  - Cost: ~$0.005-0.01/month for typical usage
  - Falls back to local model if not set

- **EMBEDDING_PROVIDER** - Choose embedding provider
  - Options: `openai` (default) or `local`
  - Local uses `sentence-transformers` (free but slower, ~500MB model download on first run)

---

## Troubleshooting

### Error: "Table with name knowledge does not exist"

**Cause:** `KNOWLEDGE_DB_PATH` not set or pointing to wrong file

**Fix:**
1. Check your `~/.claude.json` has the `env.KNOWLEDGE_DB_PATH` set
2. Verify the path is absolute and points to existing database
3. Restart Claude Code after changing config

### Error: "Table Function with name database_summary does not exist"

**Cause:** Database schema initialized but functions not added

**Fix:**
```bash
cd ~/duckdb-kb
source venv/bin/activate
python scripts/init_db.py --validate  # Check status
python scripts/init_db.py --force     # Reinitialize if needed
```

### Auto-initialization Not Working

**Cause:** Schema files (`schema.sql`, `add_functions.sql`) not in same directory as `mcp_server.py`

**Fix:**
Ensure your directory structure looks like:
```
duckdb-kb/
├── mcp_server.py
├── schema.sql
├── add_functions.sql
├── scripts/
│   └── init_db.py
└── venv/
```

### VSS Extension Not Available

**Cause:** DuckDB VSS extension not installed

**Impact:** Semantic search (`find_similar`, `smart_search`) won't work

**Fix:**
```bash
# Install VSS extension
python -c "import duckdb; con = duckdb.connect(); con.execute('INSTALL vss')"
```

**Note:** VSS is optional - SQL filtering and CRUD operations work without it

---

## Configuration Examples

### Standard Configuration

```json
{
  "projects": {
    "/Users/you/myproject": {
      "mcpServers": {
        "duckdb-kb": {
          "type": "stdio",
          "command": "/Users/you/duckdb-kb/venv/bin/python",
          "args": ["/Users/you/duckdb-kb/mcp_server.py"],
          "env": {
            "KNOWLEDGE_DB_PATH": "/Users/you/duckdb-kb/knowledge.duckdb",
            "OPENAI_API_KEY": "sk-your-key-here"
          }
        }
      }
    }
  }
}
```

### Using Local Embeddings (No OpenAI)

```json
{
  "projects": {
    "/Users/you/myproject": {
      "mcpServers": {
        "duckdb-kb": {
          "type": "stdio",
          "command": "/Users/you/duckdb-kb/venv/bin/python",
          "args": ["/Users/you/duckdb-kb/mcp_server.py"],
          "env": {
            "KNOWLEDGE_DB_PATH": "/Users/you/duckdb-kb/knowledge.duckdb",
            "EMBEDDING_PROVIDER": "local"
          }
        }
      }
    }
  }
}
```

**Note:** Run only ONE knowledge base MCP at a time. If you fork this repo to create team or personal layers, configure only the layer you're currently using.

---

## Verification Checklist

After setup, verify everything works:

- [ ] Database file exists at specified path
- [ ] `python scripts/init_db.py --validate` passes
- [ ] Claude Code shows MCP server as "Connected"
- [ ] Can call `mcp__duckdb-kb__get_stats()` tool successfully
- [ ] Database summary shows expected entry count
- [ ] No "table not found" errors when using MCP tools

---

## Next Steps

1. **Add your first entry** using `upsert_knowledge` tool
2. **Generate embeddings** for semantic search with `generate_embeddings`
3. **Link related entries** using `add_link`
4. **Search your knowledge** with `find_similar` or `smart_search`

---

## Need Help?

- Run validation: `python scripts/init_db.py --validate`
- Check MCP logs: Look for connection errors in Claude Code debug logs
- Read documentation: See `README.md`, `QUICKSTART.md`, `BACKUP.md`
- File issues: Create GitHub issue with validation output

---

## Summary: What Makes This Easy for New Users

✅ **Auto-initialization**: Database sets up automatically on first use
✅ **Validation script**: Check everything is working with one command
✅ **Clear error messages**: Helpful hints when something goes wrong
✅ **Example configs**: Copy-paste configurations for common setups
✅ **Fallback options**: Works without OpenAI, VSS, or advanced features

**Bottom line:** Set the environment variable, start Claude Code, and you're ready to go!
