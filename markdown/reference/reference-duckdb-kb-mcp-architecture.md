---
id: reference-duckdb-kb-mcp-architecture
category: reference
title: duckdb-kb MCP Architecture - Arlo's Persistent Memory System
tags:
- duckdb-kb
- mcp
- arlo
- architecture
- persistent-memory
- session-continuity
- tools
- slash-commands
- knowledge-base
- duckdb
- claude-code
- venv
created: '2025-12-04T00:31:23.105637'
updated: '2025-12-04T00:50:36.524643'
metadata:
  total_entries: 9
  tools_count: 10
  slash_commands: 7
  db_size_mb: 5.3
  python_version: '3.13'
  venv_directory: venv/
  venv_size_mb: 116
  packages:
  - duckdb 1.4.1
  - mcp 1.20.0
---

# duckdb-kb MCP Architecture - Arlo's Persistent Memory System

**DuckDB-powered knowledge base MCP server providing persistent AI memory and session continuity. Located at ~/duckdb-kb/. Single-table schema in kb.duckdb with 10 tools, 7 slash commands, and markdown backup/restore. Uses venv/ (not .venv) for Python 3.13 environment.**

---

## Purpose

Give LLMs persistent memory. This MCP enables genuine relationship continuity across sessions - no more starting from zero. The name "Arlo" refers to Claude instances using this KB.

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
│   │   ├── jira.md        # Ticket lookup
│   │   └── tdx.md         # TeamDynamix
│   └── settings.local.json
├── markdown/              # Backup directory
│   ├── pattern/           # Pattern entries
│   └── reference/         # Reference entries
├── venv/                  # Python 3.13 virtual environment (116MB, duckdb 1.4.1 + mcp 1.20.0)
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
| reference | Static facts about people, systems, orgs | `reference-brock-lampman` |
| pattern | Reusable approaches, how-tos | `pattern-duckdb-upsert` |
| table | Schema/structure documentation | `table-banner-spriden` |
| command | CLI commands with usage | `command-pds-ora` |
| issue | Bugs, investigations | `issue-idr-3731` |
| troubleshooting | Diagnostic procedures | `troubleshooting-ods-refresh` |
| project | Active initiatives | `project-cognos-migration` |
| decision | Architectural choices with rationale | `decision-duckdb-vs-sqlite` |
| research | Explorations not yet actionable | `research-llm-memory` |
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

## Standalone Tools

Not MCP tools, but Python scripts invoked via slash commands:

### canvas.py
- Canvas LMS API for school monitoring
- Requires: `CANVAS_PAT` env var
- Functions: `get_observees()`, `get_student_courses()`, `get_missing_submissions()`, `format_grade_summary()`, `full_report()`

### jira.py
- Jira API for UO IDR/DDS tickets
- Requires: `JIRA_PAT`, `JIRA_URL` env vars
- Functions: `get_my_open_tickets()`, `get_ticket_detail()`, `add_comment()`, `full_report()`

---

## MCP Configuration

Active configuration uses `venv/` (not `.venv/`). Verify with: `claude mcp list | grep duckdb`

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
- `reference-brock-lampman`
- `pattern-pds-cognos-models`
- `issue-idr-3731`

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

---

*KB Entry: `reference-duckdb-kb-mcp-architecture` | Category: reference | Updated: 2025-12-04*
