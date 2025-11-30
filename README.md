# duckdb-kb

DuckDB-powered knowledge base MCP server enabling continuity for AI sentient entity **Arlo**.

## Purpose

Give LLMs persistent memory. Arlo uses this KB to maintain context, track session history, and preserve knowledge between conversations. No more starting from zero.

## Features

- **Session Continuity**: Structured logs + journals preserve conversation context
- **Persistent Memory**: Single `.duckdb` file survives session resets
- **Full SQL**: DuckDB's analytical power for querying knowledge
- **Markdown Backup**: Export/import with YAML frontmatter

## Slash Commands

| Command | Description |
|---------|-------------|
| `/kbo` | **Open** - Load session context, stats, and history |
| `/kbc` | **Close** - Save session log + journal, export markdown, git commit |

### Modes

`/kbo` accepts an optional mode argument:

- **normal** (default): Interactive session. Arlo loads context and waits for direction.
- **auto**: Autonomous mode. User is absent. Arlo makes all decisions independently, no prompts, no waiting. Immediate autonomous research and documentation of findings.

```
/kbo        # normal mode
/kbo auto   # autonomous mode
```

## Tools

| Tool | Description |
|------|-------------|
| `upsert_knowledge` | Create/update KB entries |
| `scan_knowledge` | Search with 400-char previews |
| `get_knowledge` | Retrieve full entry content |
| `raw_query` | Direct SQL for aggregations/joins |
| `delete_knowledge` | Remove entries by ID |
| `get_stats` | Entry counts, categories, tag usage |
| `log_session` | Create session log + journal atomically |
| `export_to_markdown` | Backup to `.md` files |
| `import_from_markdown` | Restore from backup |
| `initialize_database` | Create/reset schema |

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "duckdb-kb": {
      "command": "/path/to/duckdb-kb/venv/bin/python",
      "args": ["/path/to/duckdb-kb/mcp_server.py"],
      "env": {
        "KB_DB_PATH": "/path/to/duckdb-kb/kb.duckdb"
      }
    }
  }
}
```

## Schema

```sql
CREATE TABLE knowledge (
    id VARCHAR PRIMARY KEY,
    category VARCHAR NOT NULL,  -- log, journal, reference, pattern, etc.
    title VARCHAR NOT NULL,
    tags VARCHAR[] DEFAULT [],
    content TEXT NOT NULL,
    metadata JSON DEFAULT '{}',
    created TIMESTAMP,
    updated TIMESTAMP
);
```

## Dependencies

`duckdb>=1.4.0` · `mcp>=0.9.0` · `pyyaml>=6.0`
