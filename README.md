# DuckDB Knowledge Base MCP Server

A Model Context Protocol (MCP) server that provides AI assistants with hybrid SQL + semantic search capabilities over a DuckDB knowledge base.

**Current Status:** Fresh installation with 12 seed entries demonstrating core capabilities.

## What Is This?

A searchable knowledge base that remembers your coding discoveries using AI-powered semantic search. Instead of:
- ❌ Grepping through notes hoping to find that fix from 3 months ago
- ❌ Re-solving the same problem because you forgot where you documented it
- ❌ Asking your AI assistant the same questions repeatedly across sessions

You get:
- ✅ "Find that caching pattern we used" → instant results with semantic search
- ✅ Your AI assistant remembers project-specific knowledge between sessions
- ✅ Team knowledge sharing with layered privacy (base/team/personal)

**Use cases:**
- **Troubleshooting**: "How did we fix that slow PostgreSQL query last month?"
- **Patterns**: "What's our standard approach for API rate limiting?"
- **Commands**: "What was that duckdb command for exporting to parquet?"
- **Project context**: Your AI assistant can reference decisions, patterns, and solutions from previous work

**New here?** Start with [QUICKSTART.md](./QUICKSTART.md) for a 5-minute guided setup.

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

### 3. Import Seed Data

```bash
python seed/import_seed.py
```

This imports the 12 base seed entries into your database.

### 4. Generate Embeddings

```bash
# Set OpenAI API key (already done via export)
# Generate embeddings for all entries
python scripts/generate_embeddings.py
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
  "id": "example-entry",
  "category": "pattern",
  "title": "Example Pattern",
  "tags": ["example", "pattern", "best-practice"],
  "content": "Example content...",
  "metadata": {"author": "system"},
  "has_embedding": true,
  "created": "2025-10-29T10:00:00",
  "updated": "2025-10-30T12:00:00"
}
```

#### `list_knowledge` - Browse/filter entries

```json
{
  "category": "pattern",
  "tags": ["best-practice"],
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
-- Find recently updated entries
SELECT id, title, updated
FROM knowledge
WHERE updated > NOW() - INTERVAL 7 DAYS
ORDER BY updated DESC;

-- Tag frequency analysis
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
  "query": "performance optimization techniques",
  "category": "pattern",
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
  "query": "performance optimization techniques",
  "category": "pattern",
  "tags": ["performance"],
  "date_after": "2025-10-01",
  "similarity_threshold": 0.65,
  "limit": 10
}
```

**Use cases:**
- "Recent performance optimization patterns"
- "Troubleshooting patterns from last month"
- "Command examples with specific tags"

### Write Tools

#### `upsert_knowledge` - Create or update entry

```json
{
  "id": "pattern-new-approach",
  "category": "pattern",
  "title": "New Optimization Approach",
  "tags": ["performance", "pattern", "best-practice"],
  "content": "Documentation about optimization approach...",
  "metadata": {"author": "system", "version": "1.0"},
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
  "from_id": "pattern-optimization",
  "to_id": "troubleshooting-performance",
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
    "Total Entries": "12",
    "With Embeddings": "12",
    "Categories": "4",
    "Unique Tags": "20"
  },
  "by_category": [
    {
      "category": "pattern",
      "count": 4,
      "embeddings_generated": 4,
      "embedding_pct": 100
    }
  ],
  "top_tags": [
    {"tag": "layer:base", "count": 12, "categories": ["pattern", "command", "reference"]},
    {"tag": "meta", "count": 6, "categories": ["pattern", "reference"]}
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
  "total_entries": 12,
  "updated": 12,
  "provider": "OpenAI",
  "model": "text-embedding-3-small",
  "dimensions": 1536
}
```

## Usage Examples

### Example 1: Finding Related Patterns

```
User: "Find patterns similar to performance optimization"

Claude calls:
find_similar({
  "query": "performance optimization caching strategies",
  "category": "pattern",
  "limit": 5
})

Results:
- pattern-caching-strategies (similarity: 0.92)
- pattern-query-optimization (similarity: 0.78)
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
User: "Show me all entries grouped by category"

Claude calls:
query_knowledge({
  "sql": "SELECT category, COUNT(*) as count, list(title) as titles FROM knowledge GROUP BY category"
})

Results:
[
  {"category": "pattern", "count": 4, "titles": ["Embedding Best Practices", ...]},
  {"category": "reference", "count": 5, "titles": ["MCP Server Tools", ...]},
  ...
]
```

### Example 4: Adding Documentation

```
User: "Document a new caching pattern we discovered"

Claude calls:
upsert_knowledge({
  "id": "pattern-cache-invalidation",
  "category": "pattern",
  "title": "Cache Invalidation Strategy",
  "tags": ["caching", "pattern", "performance"],
  "content": "A pattern for handling cache invalidation...",
  "metadata": {"version": "1.0"},
  "generate_embedding": true
})

Result: Entry created with embedding generated automatically
```

## Architecture

### Technical Architecture

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

### Fork Architecture (Layered Knowledge Bases)

**IMPORTANT**: Layers are **forks**, not concurrent MCPs. You run ONE MCP at your current layer.

```
┌─────────────────────────────────────────────┐
│ Layer 1: duckdb-kb (Base/Public)           │
│ ├── 12 entries (layer:base)                │
│ └── Generic platform knowledge             │
└─────────────────┬───────────────────────────┘
                  │ FORK (cp -r)
                  ↓
┌─────────────────────────────────────────────┐
│ Layer 2: team-kb (Organization/Team)       │
│ ├── 12 base entries (layer:base)           │
│ ├── 50+ team entries (layer:team)          │
│ └── Total: 62+ entries in ONE database     │
└─────────────────┬───────────────────────────┘
                  │ FORK (cp -r)
                  ↓
┌─────────────────────────────────────────────┐
│ Layer 3: personal-kb (Individual)          │
│ ├── 12 base entries (layer:base)           │
│ ├── 50+ team entries (layer:team)          │
│ ├── 20+ personal entries (layer:personal)  │
│ └── Total: 82+ entries in ONE database     │
└─────────────────────────────────────────────┘
```

**Key Points:**
- Each layer is a **complete copy** (fork) of the previous layer
- You configure Claude Code to use **only ONE** MCP server (your current layer)
- Layer tags enable **filtering during export** for distribution
- Personal layer contains everything: base + team + personal knowledge

**Creating a Fork:**
```bash
# Create team fork
cp -r duckdb-kb team-kb
cd team-kb
# Add team-specific entries with layer:team tag

# Create personal fork
cp -r team-kb personal-kb
cd personal-kb
# Add personal entries with layer:personal tag
```

**Distribution:**
- **Layer 1**: Export entries with `layer:base` → share publicly
- **Layer 2**: Export entries with `layer:base` + `layer:team` → share with team
- **Layer 3**: Keep private (not distributed)

## Performance Characteristics

### Token Efficiency

MCP protocol overhead: ~4-5k tokens per connection

**Estimated benefits** (not benchmarked):
- SQL queries return structured data without file I/O
- Semantic search returns ranked results without full scans
- Embeddings enable conceptual search vs keyword matching

### Embedding Generation

| Provider | Typical Speed | Cost | Quality |
|----------|---------------|------|---------|
| OpenAI | ~1-2s/entry | ~$0.00002/entry | Excellent (1536 dims) |
| Local | Variable | Free | Good (384 dims) |

**Note:** Performance varies based on network, hardware, and dataset size.

## File Structure

```
duckdb-kb/
├── schema.sql              # Database schema with VSS extension
├── mcp_server.py          # MCP server with 10 tools
├── requirements.txt       # Python dependencies
├── backup/                # Backup and restore tools
│   ├── export.py          # Export to JSON/SQL (git-friendly)
│   └── restore.py         # Restore from backups
├── seed/                  # Seed data (12 base entries)
│   ├── seed.json
│   └── import_seed.py
├── scripts/               # Utility scripts
│   ├── defrag.py          # Quality control & maintenance
│   ├── init_db.py         # Database initialization
│   └── generate_embeddings.py # Batch embedding generator
├── knowledge.duckdb       # DuckDB database (DO NOT GIT COMMIT)
├── exports/               # JSON/SQL exports (GIT FRIENDLY)
├── README.md              # This file
├── SETUP.md               # Setup guide
├── QUICKSTART.md          # 5-minute quick start
├── BACKUP.md              # Backup strategy guide
└── CLAUDE_DIRECTIVES.md   # AI usage directives
```

## Backup & Recovery

**Critical**: Your knowledge base is stored in a single `knowledge.duckdb` file. Regular backups are essential.

### Recommended: JSON Exports

```bash
# Export to JSON (human-readable, git-friendly)
python backup/export.py

# Commit to git
git add exports/knowledge_latest.json exports/links_latest.json
git commit -m "Backup $(date +%Y-%m-%d)"
```

**Benefits:**
- ✅ Review and edit before restore
- ✅ Git version control with diffs
- ✅ Human-readable
- ❌ Requires regenerating embeddings (~$0.0002 for 12 entries)

### Restore

```bash
# From JSON export
python backup/restore.py --from-json exports/knowledge_latest.json
python scripts/generate_embeddings.py
```

### Quick Manual Backup

```bash
# Optional: Manual copy before major changes
cp knowledge.duckdb knowledge.duckdb.backup
```

See [BACKUP.md](./BACKUP.md) for complete backup strategies and automation.

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
python scripts/generate_embeddings.py
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

## Importing Your Own Data

To import existing markdown files or custom data, you can:

1. **Use the seed import script** as a template
2. **Create entries via MCP tools** during Claude sessions
3. **Bulk import via custom script** using `upsert_knowledge`

See `seed/import_seed.py` for an example import script.

## Contributing

This is a baseline MCP server for DuckDB-based knowledge bases. Extend as needed:

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
   # Categories: table, command, issue, pattern, troubleshooting, reference, other
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

Open source baseline MCP server for knowledge management.

## Resources

- [DuckDB Documentation](https://duckdb.org/docs/)
- [VSS Extension](https://github.com/duckdb/duckdb-vss)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [MCP-EXPLAINED.md](./MCP-EXPLAINED.md) - Detailed architecture guide
