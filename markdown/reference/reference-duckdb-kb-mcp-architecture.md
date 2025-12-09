---
id: reference-duckdb-kb-mcp-architecture
category: reference
title: duckdb-kb MCP Architecture - Persistent Memory System
tags: []
---

**DuckDB-powered knowledge base MCP server providing persistent AI memory and session continuity. Single-table schema in kb.duckdb with 10 tools, 7 slash commands, and markdown backup/restore. Uses venv/ (not .venv) for Python 3.13 environment.**

---

## Purpose

Give LLMs persistent memory. This MCP enables genuine relationship continuity across sessions - no more starting from zero.

---

## Architecture Overview

```
~/duckdb-kb/
├── mcp_server.py          # MCP entry point (50 lines)
├── kb.duckdb              # Single DuckDB file (~5MB)
├── tools/                 # 10 MCP tool modules
│   ├── __init__.py        # Tool registry + auto-discovery
│   ├── base.py            # Shared utilities (get_connection, SCHEMA_SQL)
│   ├── upsert_knowledge.py
│   ├── scan_knowledge.py
│   ├── get_knowledge.py
│   ├── delete_knowledge.py
│   ├── raw_query.py
│   ├── log_session.py
│   ├── get_stats.py
│   ├── export_to_markdown.py
│   ├── import_from_markdown.py
│   ├── initialize_database.py
│   ├── canvas.py          # Standalone - Canvas LMS API
│   └── jira.py            # Standalone - Jira API
├── .claude/
│   ├── commands/          # Slash commands
│   │   ├── kbo.md         # KB Open - session start
│   │   ├── kbc.md         # KB Close - session end
│   │   ├── kbs.md         # KB Search
│   │   ├── kba.md         # KB Audit
│   │   ├── kb-setup.md    # One-time setup
│   │   ├── canvas.md      # School monitoring
│   │   └── jira.md        # Ticket lookup
│   └── settings.local.json
├── markdown/              # Backup directory
│   ├── pattern/           # Pattern entries
│   └── reference/         # Reference entries
├── venv/                  # Python 3.13 virtual environment
└── requirements.txt       # duckdb>=1.4.0, mcp>=0.9.0, pyyaml>=6.0
```

---

## Database Schema

Single table with comprehensive categorization:

```sql
CREATE TABLE IF NOT EXISTS knowledge (
    id VARCHAR PRIMARY KEY,           -- kebab-case: {category}-{topic}-{specifics}
    category VARCHAR NOT NULL,        -- reference, pattern, table, command, issue, etc.
    title VARCHAR NOT NULL,           -- Human-readable title
    tags VARCHAR[] DEFAULT [],        -- Array of lowercase tags (8-15 recommended)
    content TEXT NOT NULL,            -- Markdown content (400-char preview + full)
    metadata JSON DEFAULT '{}'::JSON, -- Additional structured data
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Categories**:
| Category | Purpose | Example ID |
|----------|---------|------------|
| reference | Static facts about people, systems, orgs | `reference-person-name` |
| pattern | Reusable approaches, how-tos | `pattern-etl-workflow` |
| table | Schema/structure documentation | `table-user-schema` |
| command | CLI commands with usage | `command-tool-name` |
| issue | Bugs, investigations | `issue-ticket-123` |
| troubleshooting | Diagnostic procedures | `troubleshooting-common-error` |
| project | Active initiatives | `project-feature-name` |
| decision | Architectural choices with rationale | `decision-tech-choice` |
| research | Explorations not yet actionable | `research-topic` |
| log | Session logs (validated: session-NNN) | `session-001` |
| todo | Rolling task lists | `todo-work` |
| other | Escape hatch (rare) | `other-misc` |

---

## MCP Tools (10)

### Core CRUD

| Tool | Purpose |
|------|---------|
| `upsert_knowledge` | Create/update entry. ON CONFLICT → update. |
| `scan_knowledge` | Browse with 400-char previews. WHERE clause + LIMIT. |
| `get_knowledge` | Retrieve full content. WHERE clause required. |
| `delete_knowledge` | Remove entry by ID. |
| `raw_query` | SQL escape hatch (SELECT only). |

### Session Management

| Tool | Purpose |
|------|---------|
| `log_session` | Create session log with 3 sections: conversation_dump, internal_dialogue, handoff. |
| `get_stats` | Entry counts, categories, tag usage. |

### Backup/Restore

| Tool | Purpose |
|------|---------|
| `export_to_markdown` | Write .md files with YAML frontmatter to `markdown/`. |
| `import_from_markdown` | Restore from backup directory. |
| `initialize_database` | Create/reset schema. |

---

## Tool Architecture Pattern

Each tool module follows this pattern:

```python
# tools/example_tool.py
from mcp.types import Tool, TextContent
from .base import json_response, error_response

TOOL_DEF = Tool(
    name="example_tool",
    description="...",
    inputSchema={...}
)

REQUIRES_DB = True  # or False

async def execute(con, args: dict) -> List[TextContent]:
    # con is DuckDB connection (or None if REQUIRES_DB=False)
    # args is validated input
    return json_response({"status": "ok"})
```

The `__init__.py` auto-discovers modules and builds registry:
```python
TOOL_REGISTRY[tool_def.name] = {
    "tool_def": tool_def,
    "handler": module.execute,
    "requires_db": module.REQUIRES_DB,
}
```

---

## Slash Commands (7)

| Command | Purpose | Key Steps |
|---------|---------|-----------|
| `/kbo [mode]` | **Open** - Load session context | get_stats → import if empty → load todos → load last 5 logs → load foundations |
| `/kbc` | **Close** - Save session | load conventions → log_session → export_to_markdown → git commit+push |
| `/kbs <topic>` | **Search** | scan_knowledge → fallback to WebSearch |
| `/kba` | **Audit** | Full KB health check |
| `/kb-setup` | **Setup** | One-time venv/MCP config |
| `/canvas [student]` | School monitoring | Canvas LMS grades, missing work |
| `/jira [ticket]` | Ticket lookup | Jira API search/detail |

---

## Session Lifecycle

### Session Start (`/kbo`)

1. `get_stats({"detailed": True})` - Check KB state
2. If empty: `import_from_markdown({"input_dir": "markdown/"})`
3. Load `category = 'todo'` entries
4. `scan_knowledge` last 10 session logs (previews)
5. `get_knowledge` last 5 logs in full
6. Load `reference-arlo-foundations`

**auto mode**: Autonomous operation, no user interaction needed.

### Session End (`/kbc`)

1. Load `pattern-session-log-conventions`
2. Calculate next session number
3. `log_session` with:
   - `conversation_dump`: Verbatim transcript
   - `internal_dialogue`: Stream of consciousness reflection
   - `handoff`: Notes for next instance
4. `export_to_markdown()` - Backup to files
5. `git add -A && git commit -m "feat: S{N} - ..." && git push`

---

## MCP Configuration

Active configuration uses `venv/` (not `.venv/`).

In `~/.claude/settings.json`:
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

---

## Content Structure Conventions

### Entry Format
1. Start with ~400 char **dense preview** (key facts, names, relationships)
2. Full structured content below
3. Be VERBOSE - more is better
4. Never lose: exact quotes, numbers, names, dates, examples, caveats

### ID Format
Kebab-case: `{category}-{topic}-{specifics}`
- `reference-person-name`
- `pattern-workflow-name`
- `issue-ticket-123`

### Tags
8-15 lowercase tags recommended for discoverability.

---

## Browser Projects Integration

For read-only KB access from any device:
1. Sync `markdown/` to Claude browser Projects
2. Use `markdown/reference/reference-browser-project-instructions.md` as project instructions
3. Browser Claude can query, discuss, draft entries
4. Handoff pattern: "handoff, see reference/hd.md"
5. `/kbc` auto-pushes to git, keeping browser in sync

---

## Design Philosophy

1. **Single file persistence**: Everything in `kb.duckdb`
2. **Markdown as backup**: Human-readable, git-trackable
3. **Category-driven organization**: ID prefix = category
4. **Preview-first retrieval**: scan_knowledge → get_knowledge pattern
5. **Session continuity**: log_session captures conversation + internal state + handoff
6. **Fidelity over brevity**: Verbose entries preserve context
