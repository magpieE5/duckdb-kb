# DuckDB Knowledge Base - System Guide

## Current System Status

- ✅ **66+ knowledge entries** with semantic search
- ✅ **100% embedding coverage** using OpenAI
- ✅ **DuckDB database** with full schema and indexes
- ✅ **MCP server** with 10 tools integrated with Claude Code
- ✅ **~5k token overhead** for efficient queries

## Configure Claude Code

### Step 1: Locate Claude Code MCP Config

The config file is at:
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

### Step 2: Verify DuckDB Knowledge MCP Configuration

Add this to your `mcpServers` object:

```json
{
  "mcpServers": {
    "duckdb-kb": {
      "command": "/absolute/path/to/duckdb-kb/venv/bin/python",
      "args": [
        "/absolute/path/to/duckdb-kb/mcp_server.py"
      ],
      "env": {
        "OPENAI_API_KEY": "your-openai-api-key-here",
        "KNOWLEDGE_DB_PATH": "/absolute/path/to/duckdb-kb/knowledge.duckdb",
        "EMBEDDING_PROVIDER": "openai"
      }
    }
  }
}
```

**Important:** Replace the paths and API key with your actual values!

### Getting an OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Create a new API key
4. Copy the key (starts with `sk-proj-...`)
5. Add it to your MCP config above

**Cost:** ~$0.01-0.02/month for personal use

### Alternative: Use Local Embeddings (Free)

If you prefer not to use OpenAI, you can use local embeddings:

```json
{
  "mcpServers": {
    "duckdb-kb": {
      "command": "/absolute/path/to/duckdb-kb/venv/bin/python",
      "args": [
        "/absolute/path/to/duckdb-kb/mcp_server.py"
      ],
      "env": {
        "KNOWLEDGE_DB_PATH": "/absolute/path/to/duckdb-kb/knowledge.duckdb",
        "EMBEDDING_PROVIDER": "local"
      }
    }
  }
}
```

Then install local model support:
```bash
pip install sentence-transformers torch
```

### Step 3: Restart Claude Code (if configuration changed)

1. Quit Claude Code completely
2. Reopen Claude Code
3. The MCP server will start automatically

## Verify System is Working

Try asking Claude:

```
"Show me database statistics from the knowledge base"
```

Claude should call `get_stats()` and show you:
- 66 total entries
- 66 with embeddings (100%)
- Breakdown by category

Or try:

```
"Find notes similar to waitlist issues"
```

Claude should use semantic search (`find_similar`) to find related content.

## Available Tools

Once configured, Claude Code can use these 10 tools:

### Read/Query
1. **get_knowledge** - Get single entry by ID
2. **list_knowledge** - Browse/filter entries
3. **query_knowledge** - Execute custom SQL
4. **find_similar** - Semantic search (conceptual)
5. **smart_search** - Hybrid SQL + semantic

### Write
6. **upsert_knowledge** - Create/update entry
7. **delete_knowledge** - Delete entry
8. **add_link** - Create relationships

### Utility
9. **get_stats** - Database statistics
10. **generate_embeddings** - Batch generate embeddings

## Example Queries

**Browse tables:**
```
"List all table documentation we have"
```

**Semantic search:**
```
"Find notes about Oracle performance optimization"
```

**Recent work:**
```
"What have we documented in the last 2 weeks?"
```

**Add new documentation:**
```
"Document a new table called STUDENT_ENROLLMENT with these details..."
```

## Maintenance

### Update Embeddings

When you add new entries, embeddings are generated automatically during `upsert_knowledge`.

To manually regenerate:
```bash
export OPENAI_API_KEY="sk-..."
venv/bin/python generate_embeddings.py
```

### Database Backup

```bash
# Backup
cp knowledge.duckdb knowledge.duckdb.backup

# Restore
cp knowledge.duckdb.backup knowledge.duckdb
```

### View Database

```bash
duckdb knowledge.duckdb

# Run queries:
SELECT * FROM knowledge_stats;
SELECT category, COUNT(*) FROM knowledge GROUP BY category;
SELECT * FROM recent_knowledge;
```

## System Performance

| Operation | Traditional File Reading | DuckDB MCP | Efficiency |
|-----------|-------------------------|------------|------------|
| MCP overhead | N/A | ~5k tokens | Minimal |
| List Oracle tables | Read 5 files (10k) | SQL query (500) | **95% reduction** |
| Semantic search | Full file scan | find_similar (800) | **Instant, ranked results** |

## File Structure

```
duckdb-mcp/
├── knowledge.duckdb          ← Your knowledge base (66 entries)
├── mcp_server.py            ← MCP server (10 tools)
├── generate_embeddings.py   ← Embedding generator
├── migrate.py               ← Obsidian → DuckDB migration
├── schema_simple.sql        ← Database schema
├── requirements.txt         ← Python dependencies
├── venv/                    ← Virtual environment
├── README.md                ← Full documentation
├── MCP-EXPLAINED.md         ← MCP architecture guide
└── SETUP.md                 ← This file
```

## Troubleshooting

### "Tool not found" when calling tools

1. Check Claude Code restarted after config change
2. Verify MCP config path is correct
3. Check server logs in Claude Code settings

### "OpenAI API error"

1. Verify API key in config is correct
2. Check OpenAI account has credits
3. Test with: `echo $OPENAI_API_KEY`

### "Database not found"

1. Check `KNOWLEDGE_DB_PATH` in config
2. Verify file exists: `ls -lh knowledge.duckdb`
3. Should be ~2-5 MB with 66 entries

### Regenerate embeddings

**With OpenAI:**
```bash
export OPENAI_API_KEY="your-openai-api-key"
venv/bin/python generate_embeddings.py
```

**With local embeddings (free):**
```bash
export EMBEDDING_PROVIDER="local"
pip install sentence-transformers torch
venv/bin/python generate_embeddings.py
```

## Next Steps

1. ✅ Configure Claude Code with new MCP
2. ✅ Remove old Obsidian MCP
3. ✅ Test with simple query
4. ✅ Start using hybrid search capabilities!

## Cost Tracking

**Current usage:**
- Initial embeddings: 66 entries ≈ $0.002
- Monthly additions: ~50 entries ≈ $0.001/month
- **Total: ~$0.01-0.02/month**

Set usage limit in OpenAI dashboard: https://platform.openai.com/usage

---

**You're all set! 🎉**

Your knowledge base is now:
- ✅ Token-efficient (~35% less overhead)
- ✅ Semantically searchable
- ✅ SQL-queryable
- ✅ Fast (DuckDB + indexes)
- ✅ Hybrid search capable

Try asking Claude about your PDS documentation!
