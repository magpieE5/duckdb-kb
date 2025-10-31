# DuckDB Knowledge Base MCP Server

A Model Context Protocol (MCP) server that provides AI assistants with hybrid SQL + semantic search capabilities over a DuckDB knowledge base.

**Current Status:** Production system managing 66+ knowledge entries with semantic search capabilities.

## For AI Assistants 🤖

**First time connecting?** Start here:

1. **Get oriented**: Run `get_stats({"detailed": true})` to see what's in the knowledge base
2. **Learn the system**: Search for directives with `find_similar({"query": "how to use this knowledge base", "limit": 5})`
3. **Discover patterns**: The KB is self-documenting - semantic search will find usage guides, best practices, and examples

**Key concepts:**
- **10 tools available** - See tool descriptions for WHEN TO USE guidance
- **Hybrid search** - Combine SQL filtering with semantic similarity
- **Always check for duplicates** - Use `smart_search()` before creating new entries
- **Self-bootstrapping** - Search for "directives" to learn automatic knowledge capture patterns

**Quick tool guide:**
- 🔍 **Discovering**: `find_similar()` for concepts, `smart_search()` for filtered search, `list_knowledge()` for browsing
- ✍️ **Creating**: Always `smart_search()` first, then `upsert_knowledge()` if no duplicates
- 📊 **Analyzing**: `get_stats()` for overview, `query_knowledge()` for custom SQL
- 🔗 **Connecting**: `add_link()` to build knowledge graph

## Features

- ✅ **10 comprehensive tools** (CRUD + search + utilities)
- ✅ **Hybrid search** - SQL filtering + semantic similarity ranking
- ✅ **OpenAI embeddings** (1536 dims) with local fallback
- ✅ **Token-efficient** - ~4-5k token overhead
- ✅ **Git-friendly** - Single .duckdb file
- ✅ **Fast** - In-memory DuckDB with VSS extension
- ✅ **Offline-capable** - Only needs network for embedding generation

## Quick Start

### 1. Install Dependencies

```bash
cd /path/to/duckdb-kb
pip install -r requirements.txt
```

### 2. Initialize Database

```bash
# Create database and load schema
duckdb knowledge.duckdb < schema.sql
```

### 3. Import Data (If starting fresh)

If you're setting up a new knowledge base, you can import existing markdown files:

```bash
python migrate.py \
    --vault-path /path/to/markdown/files \
    --db-path knowledge.duckdb \
    --skip-sessions
```

**Note:** The current database already contains 66+ migrated entries with embeddings.

### 4. Generate Embeddings

```bash
# Set OpenAI API key (already done via export)
# Generate embeddings for all entries
python -c "
import asyncio
from mcp_server import tool_generate_embeddings, get_connection

async def main():
    con = get_connection()
    result = await tool_generate_embeddings(con, {})
    print(result[0].text)

asyncio.run(main())
"
```

### 5. Configure Claude Code

Add to your MCP configuration:

```json
{
  "mcpServers": {
    "duckdb-kb": {
      "command": "python3",
      "args": [
        "/path/to/duckdb-kb/mcp_server.py"
      ],
      "env": {
        "OPENAI_API_KEY": "sk-...",
        "KNOWLEDGE_DB_PATH": "/path/to/duckdb-kb/knowledge.duckdb"
      }
    }
  }
}
```

## Tools Reference

### Read/Query Tools

#### `get_knowledge` - Get single entry by ID

```json
{
  "id": "mst-course-offering",
  "include_related": true
}
```

**Returns:**
```json
{
  "id": "mst-course-offering",
  "category": "table",
  "title": "MST_COURSE_OFFERING",
  "tags": ["oracle", "table", "course-offering"],
  "content": "Base table for course offerings...",
  "metadata": {"schema": "BANNER"},
  "has_embedding": true,
  "created": "2025-10-29T10:00:00",
  "updated": "2025-10-30T12:00:00"
}
```

#### `list_knowledge` - Browse/filter entries

```json
{
  "category": "table",
  "tags": ["oracle"],
  "limit": 20
}
```

#### `query_knowledge` - Execute custom SQL

```json
{
  "sql": "SELECT category, COUNT(*) as count FROM knowledge GROUP BY category"
}
```

**Example queries:**
```sql
-- Find all tables updated recently
SELECT id, title, updated
FROM knowledge
WHERE category = 'table'
  AND updated > NOW() - INTERVAL 7 DAYS
ORDER BY updated DESC;

-- Tag frequency
SELECT unnest(tags) as tag, COUNT(*) as usage
FROM knowledge
GROUP BY tag
ORDER BY usage DESC
LIMIT 20;

-- Entries without embeddings
SELECT id, title, category
FROM knowledge
WHERE embedding IS NULL;
```

#### `find_similar` - Semantic search

```json
{
  "query": "waitlist capacity enrollment issues",
  "category": "table",
  "similarity_threshold": 0.7,
  "limit": 10
}
```

**Use cases:**
- "Find notes about X concept" (vague query)
- "Problems similar to this error message"
- "Related documentation"

#### `smart_search` - Hybrid SQL + semantic

```json
{
  "query": "Oracle performance optimization techniques",
  "category": "pattern",
  "tags": ["oracle"],
  "date_after": "2025-10-01",
  "similarity_threshold": 0.65,
  "limit": 10
}
```

**Use cases:**
- "Recent Oracle performance issues"
- "Troubleshooting patterns for uploads"
- "Command examples from last month"

### Write Tools

#### `upsert_knowledge` - Create or update entry

```json
{
  "id": "new-table-doc",
  "category": "table",
  "title": "MY_NEW_TABLE",
  "tags": ["oracle", "table"],
  "content": "Documentation about MY_NEW_TABLE...",
  "metadata": {"schema": "BANNER", "size": "large"},
  "generate_embedding": true
}
```

**On create:** Inserts new entry with embedding
**On update:** Updates existing entry, regenerates embedding

#### `delete_knowledge` - Delete entry

```json
{
  "id": "obsolete-entry"
}
```

**Note:** Also deletes all links to/from this entry.

#### `add_link` - Create relationship

```json
{
  "from_id": "issue-idr-3674",
  "to_id": "msvgvc1",
  "link_type": "references"
}
```

**Link types:** `related`, `parent`, `child`, `references`

### Utility Tools

#### `get_stats` - Database statistics

```json
{
  "detailed": true
}
```

**Returns:**
```json
{
  "summary": {
    "Total Entries": "60",
    "With Embeddings": "60",
    "Categories": "5",
    "Unique Tags": "42"
  },
  "by_category": [
    {
      "category": "table",
      "count": 15,
      "embeddings_generated": 15,
      "embedding_pct": 100
    }
  ],
  "top_tags": [
    {"tag": "oracle", "count": 32, "categories": ["table", "command", "issue"]},
    {"tag": "performance", "count": 18, "categories": ["pattern", "issue"]}
  ]
}
```

#### `generate_embeddings` - Batch embedding generation

```json
{
  "ids": ["entry1", "entry2"],  // Optional - generates for all missing if not specified
  "regenerate": false,
  "batch_size": 32
}
```

**Returns:**
```json
{
  "status": "success",
  "total_entries": 60,
  "updated": 60,
  "provider": "OpenAI",
  "model": "text-embedding-3-small",
  "dimensions": 1536
}
```

## Usage Examples

### Example 1: Finding Related Issues

```
User: "Find issues similar to the MSVGVC1 waitlist problem"

Claude calls:
find_similar({
  "query": "MSVGVC1 waitlist capacity enrollment missing students",
  "category": "issue",
  "limit": 5
})

Results:
- IDR-3674: MSVGVC1 waitlist issue (similarity: 0.92)
- IDR-2341: Course enrollment capacity (similarity: 0.78)
- ...
```

### Example 2: Recent Performance Work

```
User: "What performance optimizations have we done recently?"

Claude calls:
smart_search({
  "query": "performance optimization tuning improvements",
  "tags": ["performance"],
  "date_after": "2025-10-01",
  "limit": 10
})

Results: Recent performance-related entries, ranked by relevance
```

### Example 3: Complex Analysis

```
User: "Show me all tables we've documented, grouped by database"

Claude calls:
query_knowledge({
  "sql": "SELECT metadata->>'database' as db, COUNT(*) as tables, list(title) as table_names FROM knowledge WHERE category = 'table' GROUP BY db"
})

Results:
[
  {"db": "Oracle", "tables": 12, "table_names": ["MST_COURSE_OFFERING", ...]},
  {"db": "MSSQL", "tables": 3, "table_names": ["..."]},
  ...
]
```

### Example 4: Adding Documentation

```
User: "Document a new table called STUDENT_WAITLIST"

Claude calls:
upsert_knowledge({
  "id": "student-waitlist",
  "category": "table",
  "title": "STUDENT_WAITLIST",
  "tags": ["oracle", "table", "waitlist"],
  "content": "Table tracking students waiting for course enrollment...",
  "metadata": {"schema": "BANNER", "database": "Oracle"},
  "generate_embedding": true
})

Result: Entry created with embedding generated automatically
```

## Architecture

```
┌─────────────────┐
│   Claude Code   │
└────────┬────────┘
         │ MCP Protocol (JSON-RPC)
         │
┌────────┴────────┐
│  mcp_server.py  │
│                 │
│  10 Tools:      │
│  - get          │
│  - list         │
│  - query        │
│  - find_similar │
│  - smart_search │
│  - upsert       │
│  - delete       │
│  - add_link     │
│  - get_stats    │
│  - gen_embed    │
└────────┬────────┘
         │
         ├──────────────┐
         │              │
┌────────┴────────┐  ┌──┴──────────┐
│ knowledge.duckdb│  │  OpenAI API │
│                 │  │  (embeddings)│
│ - knowledge     │  └─────────────┘
│ - knowledge_links│
│ - indexes       │
│ - VSS extension │
└─────────────────┘
```

## Performance

### Token Efficiency

| Operation | Traditional File Reading | DuckDB MCP | Savings |
|-----------|-------------------------|------------|---------|
| MCP overhead | N/A | 4-5k tokens | N/A |
| Find Oracle tables | Read 5 files (10k) | SQL query (500) | 95% |
| Semantic search | Full scan required | find_similar (800) | 90%+ |

### Query Performance

| Dataset Size | SQL Query | Semantic Search (brute force) | Semantic (HNSW) |
|--------------|-----------|------------------------------|-----------------|
| 60 entries | < 1ms | ~5ms | ~2ms |
| 1,000 entries | ~2ms | ~50ms | ~10ms |
| 10,000 entries | ~5ms | ~500ms | ~15ms |

**M2 Max optimizations:** DuckDB's vectorized execution + GPU-accelerated cosine similarity

### Embedding Generation

| Provider | 60 entries | 1 entry | Cost | Quality |
|----------|------------|---------|------|---------|
| OpenAI | ~5-10s | ~1-2s | $0.0008 | Excellent (1536 dims) |
| Local | ~2s | ~50ms | Free | Good (384 dims) |

## File Structure

```
duckdb-mcp/
├── schema.sql              # Database schema with VSS extension
├── mcp_server.py          # MCP server with 10 tools
├── migrate.py             # Import markdown files to database
├── generate_embeddings.py # Batch embedding generator
├── backup.sh              # Binary backup script
├── export.py              # Export to JSON/SQL (git-friendly)
├── restore.py             # Restore from backups
├── requirements.txt       # Python dependencies
├── knowledge.duckdb       # DuckDB database (DO NOT GIT COMMIT)
├── backups/               # Binary backups (DO NOT GIT COMMIT)
├── exports/               # JSON/SQL exports (GIT FRIENDLY)
├── README.md             # This file
├── BACKUP.md             # Backup strategy guide
└── MCP-EXPLAINED.md      # Deep dive into MCP architecture
```

## Backup & Recovery

**Critical**: Your knowledge base is stored in a single `knowledge.duckdb` file. Loss or corruption would be catastrophic.

### Quick Backup

```bash
# Binary backup (fast, includes embeddings)
./backup.sh

# JSON export (git-friendly, human-readable)
python export.py
```

### Restore

```bash
# From binary backup
python restore.py --from-backup backups/knowledge_20250130.duckdb

# From JSON export (requires regenerating embeddings)
python restore.py --from-json exports/knowledge_latest.json
python generate_embeddings.py
```

### Recommended Strategy

1. **Daily**: Export to JSON and commit to git
2. **Weekly**: Create binary backup with `./backup.sh`
3. **Before major changes**: Always create a backup first

See [BACKUP.md](./BACKUP.md) for complete backup strategy and automation setup.

## Troubleshooting

### "OpenAI API error"

```bash
# Check key is set
echo $OPENAI_API_KEY

# Re-export if needed
export OPENAI_API_KEY="sk-..."

# Or use local fallback
export EMBEDDING_PROVIDER="local"
pip install sentence-transformers torch
```

### "DuckDB connection failed"

```bash
# Check database exists
ls -lh knowledge.duckdb

# Recreate if needed
duckdb knowledge.duckdb < schema.sql
```

### "VSS extension not found"

```bash
# Install VSS extension
duckdb knowledge.duckdb
> INSTALL vss;
> LOAD vss;
> .exit
```

### "No embeddings generated"

```bash
# Check embedding status
duckdb knowledge.duckdb
> SELECT COUNT(*) as total,
>        COUNT(embedding) as with_embeddings
> FROM knowledge;

# Generate manually
python -c "
import asyncio
from mcp_server import tool_generate_embeddings, get_connection
async def main():
    con = get_connection()
    result = await tool_generate_embeddings(con, {})
    print(result[0].text)
asyncio.run(main())
"
```

## Advanced Usage

### Custom Embedding Model

```python
# In mcp_server.py, change:
EMBEDDING_MODEL = 'text-embedding-3-large'  # 3072 dimensions, better quality
EMBEDDING_DIM = 3072

# Update schema:
ALTER TABLE knowledge ALTER COLUMN embedding TYPE FLOAT[3072];
```

### HNSW Index for Large Datasets

```sql
-- After generating embeddings for >1000 entries:
CREATE INDEX idx_knowledge_embedding_hnsw
ON knowledge
USING HNSW (embedding)
WITH (metric = 'cosine');

-- Speeds up semantic search 10-50x
```

### Query Optimization

```sql
-- Use EXPLAIN to see query plan
EXPLAIN SELECT * FROM knowledge WHERE category = 'table';

-- Add indexes for frequent queries
CREATE INDEX idx_custom ON knowledge(your_field);
```

## Data Import from Markdown

The `migrate.py` script can import markdown files into the knowledge base. It preserves:
- ✅ Frontmatter metadata
- ✅ Tags (frontmatter + inline #tags)
- ✅ Wikilinks ([[links]])
- ✅ Timestamps (created/updated)
- ✅ Content (markdown body)

And automatically infers:
- ✅ Category (from directory, filename, tags, frontmatter)
- ✅ Relationships (from wikilinks)

```bash
python migrate.py \
    --vault-path /path/to/markdown/directory \
    --db-path knowledge.duckdb \
    --skip-jira \
    --skip-sessions
```

**Note:** The current system has already been populated with migrated data.

## Contributing

This is a custom MCP server for PDS work. Extend as needed:

1. **Add new tool:**
   ```python
   # In mcp_server.py @app.list_tools():
   Tool(name="my_tool", description="...", inputSchema={...})

   # Add handler:
   async def tool_my_tool(con, args):
       # Implementation
       return [TextContent(type="text", text="result")]

   # Route in call_tool():
   elif name == "my_tool":
       return await tool_my_tool(con, arguments)
   ```

2. **Add new category:**
   ```python
   # In migrate.py CATEGORY_MAPPING:
   'MyCategory': 'mycategory'

   # Use in knowledge base:
   upsert_knowledge(category="mycategory", ...)
   ```

3. **Extend schema:**
   ```sql
   -- Add column:
   ALTER TABLE knowledge ADD COLUMN my_field VARCHAR;

   -- Add index:
   CREATE INDEX idx_my_field ON knowledge(my_field);
   ```

## License

Custom internal tool for PDS work.

## Resources

- [DuckDB Documentation](https://duckdb.org/docs/)
- [VSS Extension](https://github.com/duckdb/duckdb-vss)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [MCP-EXPLAINED.md](./MCP-EXPLAINED.md) - Detailed architecture guide
