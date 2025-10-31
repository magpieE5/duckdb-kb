# Quick Start Guide

Get the DuckDB Knowledge Base MCP server running in 5 minutes.

## Prerequisites

- Python 3.8+
- OpenAI API key (for embeddings)
- MCP-compatible AI assistant (Claude Code, etc.)

## Installation (2 minutes)

```bash
# Clone or download this repository
cd duckdb-mcp

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Setup (2 minutes)

### 1. Create Database

```bash
# Initialize empty database with schema
duckdb knowledge.duckdb < schema.sql
```

### 2. Import Seed Data

```bash
# Import the 12 Layer 1 seed entries
python seed/import_seed.py
```

**Expected output:**
```
Importing seed data from: seed/seed.json
Target database: knowledge.duckdb
Found 12 entries to import
  Imported: kb-maintenance-comprehensive-guide
  Imported: directive-auto-knowledge-capture
  ...
✅ Import complete!
  Imported: 12
```

### 3. Generate Embeddings

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="sk-..."

# Generate embeddings for semantic search
python generate_embeddings.py
```

**Expected:** ~10-15 seconds to generate 12 embeddings (~$0.0001 cost)

## Configure MCP (1 minute)

Add to your MCP configuration file:

**Claude Code:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "duckdb-kb": {
      "command": "/path/to/duckdb-mcp/venv/bin/python",
      "args": [
        "/path/to/duckdb-mcp/mcp_server.py"
      ],
      "env": {
        "OPENAI_API_KEY": "sk-...",
        "KNOWLEDGE_DB_PATH": "/path/to/duckdb-mcp/knowledge.duckdb"
      }
    }
  }
}
```

**Important:** Replace `/path/to/duckdb-mcp` with your actual path!

## Verify (30 seconds)

1. Restart your AI assistant (e.g., Claude Code)
2. The MCP server should connect automatically
3. Try this command:

```
Get database statistics
```

**Expected response:** Claude will call `get_stats()` and show:
- 12 total entries
- 12 with embeddings (100%)
- Breakdown by category

## First Steps

Now that it's working, try:

1. **Learn the system:**
   ```
   Search for entries about "how to use this knowledge base"
   ```

2. **Browse entries:**
   ```
   List all pattern entries
   ```

3. **Add your first entry:**
   ```
   Create a new pattern entry about [your topic]
   ```

   *(Claude will automatically check for duplicates first)*

## What's Next?

- **Read the directives:** Search for "directive" entries to learn automatic knowledge capture patterns
- **Explore tools:** See README.md "For AI Assistants" section for tool guide
- **Customize:** Add your own entries, organize with tags, build your knowledge base
- **Backup:** Export to JSON with `python export.py` and commit to git (see BACKUP.md)

## Troubleshooting

### "Import failed: knowledge table not found"

You forgot step 1. Run:
```bash
duckdb knowledge.duckdb < schema.sql
```

### "No embeddings generated"

Check your OpenAI API key:
```bash
echo $OPENAI_API_KEY  # Should show sk-...
```

If not set:
```bash
export OPENAI_API_KEY="sk-..."
python generate_embeddings.py
```

### "MCP server not connecting"

1. Check paths in MCP config are absolute (not relative)
2. Verify Python path: `which python3` or use venv path
3. Check logs in your AI assistant settings
4. Restart the AI assistant completely

### "Semantic search returns nothing"

Check embedding status:
```bash
python -c "
from mcp_server import get_connection
con = get_connection()
result = con.execute('SELECT COUNT(*) as total, COUNT(embedding) as with_emb FROM knowledge').fetchone()
print(f'Entries: {result[0]}, With embeddings: {result[1]}')
"
```

Should show: `Entries: 12, With embeddings: 12`

If not, run: `python generate_embeddings.py`

## Cost Information

**One-time setup:**
- Embedding 12 seed entries: ~$0.0001 (1 cent)

**Ongoing usage:**
- Tool overhead per connection: ~$0.003 (0.3 cents)
- New entry embedding: ~$0.00002 each
- Typical monthly cost: $0.01-0.02 for personal use

**Free alternative:** Use local embeddings instead
```bash
export EMBEDDING_PROVIDER="local"
pip install sentence-transformers torch
python generate_embeddings.py
```

## Further Reading

- **README.md** - Complete feature documentation
- **SETUP.md** - Detailed setup guide
- **BACKUP.md** - Backup strategies
- **CLAUDE_DIRECTIVES.md** - How Claude uses the KB
- **seed/README.md** - Seed data documentation
- **scripts/defrag.py** - Defragmentation tool

## Support

- **Issues:** Check troubleshooting section above
- **Questions:** Search the knowledge base itself! It's self-documenting
- **Examples:** See seed entries for patterns and best practices

---

**You're all set! 🎉**

Your knowledge base is now:
- ✅ Functional and tested
- ✅ Semantically searchable
- ✅ Multi-model compatible
- ✅ Ready to grow with your knowledge

Start adding entries and let the knowledge base evolve!
