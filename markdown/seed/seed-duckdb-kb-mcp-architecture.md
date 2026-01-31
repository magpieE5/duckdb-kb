---
id: seed-duckdb-kb-mcp-architecture
category: seed
title: duckdb-kb MCP Architecture
tags:
- architecture
- mcp
- duckdb
- schema
- tools
- shared-repos
created: '2025-12-13T19:27:48.062907'
updated: '2026-01-22T07:40:05.955088'
---

# duckdb-kb MCP Architecture

**DuckDB-powered knowledge base MCP server providing persistent AI memory and session continuity. Single-table schema with tools for CRUD, search, session logging, and markdown backup/restore. Supports team sharing via nested git repos.**

---

## Location

Repository: `~/duckdb-kb/`
Database: `~/duckdb-kb/kb.parquet` (loaded into DuckDB in-memory at runtime)
Transcripts: `~/duckdb-kb/markdown/transcript/`

---

## Schema

Single table: `knowledge`

| Column | Type | Description |
|--------|------|-------------|
| id | VARCHAR PRIMARY KEY | Kebab-case identifier |
| category | VARCHAR | Entry type |
| title | VARCHAR | Human-readable title |
| tags | VARCHAR[] | Array of tags |
| content | TEXT | Full markdown content |
| metadata | JSON | Additional structured data |
| created | TIMESTAMP | Creation time |
| updated | TIMESTAMP | Last update time |

---

## Supporting Files

| File | Purpose |
|------|---------|
| `kb.parquet` | Main knowledge base (loaded into DuckDB in-memory) |
| `kb_access.parquet` | Access logging (timestamp, session, op, id) |
| `open-config.csv` | Session continuity controls (depth of transcripts/logs)|
| `kb-mode.csv` | Mode configuration (mode, is_auto, id) |

---

## /open Workflow Configuration

Two CSV files control session startup behavior.

### kb-mode.csv

Defines what KB entries load for each mode.

| Column | Purpose |
|--------|---------|
| mode | Mode name (e.g., `pds`, `cognos`, `IDR-3799 Eric Bever...`) |
| is_auto | `true` = auto-load on mode selection, `false` = offered for manual selection |
| id | KB entry ID to load |

**Special modes:**
- `seed` - Entries loaded for ALL sessions before mode selection (core orientation)
- `auto` - Autonomous mode, skips user interaction and proceeds to history loading

**Ticket-specific modes:** Create modes for active investigations (e.g., `IDR-3799 Eric Bever: COVERAGE_OPTION_DESC`). Add relevant KBs with `is_auto=true` for instant context loading when working that ticket.

### open-config.csv

Controls mode display order and session history depth.

| Column | Purpose |
|--------|---------|
| mode | Mode name (must match kb-mode.csv) |
| load_order | Display order in mode selection (lower = first) |
| transcript_depth | How many transcripts to load (0 = none) |
| log_depth | How many session logs to load (0 = none) |

Modes not in open-config.csv use defaults (no history loading, alphabetical order after explicit entries).

### /open Flow

1. Core context (date, session number, shared repos, markdown import)
2. Load all `mode=seed` entries
3. Load `reference-arlo-foundations`, `state-arlo`, `accumulator-corrections`
4. Set session number for access logging
5. **Mode selection** - user picks from available modes
6. For selected mode(s): auto-load `is_auto=true` entries, offer `is_auto=false` for selection
7. Load session history (logs, then transcripts) per open-config.csv depths

---

## Helper Scripts

| Script | Purpose |
|--------|---------|
| `tools/shared_repos.py` | Git operations for shared repos (pull/push/list) |
| `tools/session_details.py` | Session metadata and cross-OS compatability |
| `tools/extract_exchanges.py` | Transcript extraction from Claude Code CLI internals |

---

## Categories

reference, pattern, table, command, issue, troubleshooting, project, decision, research, log, actions, transcript, seed, other

---

## MCP Tools (13)

| Tool | Purpose |
|------|---------|
| `upsert_knowledge` | Create or update entry |
| `get_knowledge` | Retrieve full entries by WHERE clause |
| `scan_knowledge` | FTS search with 400-char return previews |
| `delete_knowledge` | Remove entry by ID |
| `list_knowledge` | List all non-log entry IDs/titles |
| `list_add` | Add item to any list-type entry |
| `list_remove` | Remove item from list-type entry |
| `raw_query` | Direct SQL for complex queries |
| `log_session` | Create session log (preview, witness, handoff) |
| `set_session` | Set current session number for access logging |
| `extract_transcript` | Extract and upsert transcript from session file |
| `export_to_markdown` | Backup KB to markdown files |
| `import_from_markdown` | Restore KB from markdown |

**Note:** `export_to_markdown` with `clear_existing=true` automatically skips directories containing `.git` folders, protecting shared repos.

---

## DuckDB Query Patterns

Common syntax patterns for querying DuckDB via `raw_query` or direct connections.

### Array UNNEST with Aggregation

DuckDB doesn't support UNNEST directly in SELECT with GROUP BY.

**WRONG:**
```sql
SELECT DISTINCT unnest(tags) as tag, COUNT(*) FROM knowledge GROUP BY 1
-- Binder Error: UNNEST not supported here
```

**RIGHT:**
```sql
SELECT tag, COUNT(*) 
FROM (SELECT unnest(tags) as tag FROM knowledge) 
GROUP BY tag
```

The subquery pattern is required for unnesting arrays before aggregation.

---

### Schema Introspection

Always check a table's schema before first query of the session.

```sql
-- Find table location
SELECT table_schema, table_name 
FROM information_schema.tables 
WHERE table_name LIKE '%search_pattern%';

-- Check columns and types
DESCRIBE schema.table_name;

-- List all columns with details
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'schema_name' 
  AND table_name = 'table_name';
```

---

### MCP vs Direct Access

When working with duckdb-kb MCP:
- **USE:** `mcp__duckdb-kb__raw_query` for KB queries
- **DON'T:** Shell out to `duckdb ~/duckdb-kb/kb.parquet`

The MCP abstracts storage. Direct parquet access bypasses the interface and couples to implementation details.

---

### Case Sensitivity

DuckDB stores identifiers in lowercase by default. String values may preserve original case.

```sql
-- Check actual case in data
SELECT DISTINCT column_name FROM table LIMIT 5;

-- Safe: case-insensitive match
SELECT * FROM table WHERE lower(column_name) = lower('VALUE');
```

**Note:** When joining across systems (e.g., Oracle metadata vs DuckDB data), case mismatches are common. Always use `LOWER()` for string comparisons when joining.

---

### Verify Date Ranges, Not Row Counts

High row counts don't indicate full history. Always check actual date range:

```sql
-- WRONG: Assuming 171M rows = full history
SELECT COUNT(*) FROM web_logs;  -- 171M rows

-- RIGHT: Check actual retention
SELECT MIN(log_date), MAX(log_date) FROM web_logs;
-- Result: 30 days exactly (Dec 28 - Jan 27)
```

Row volume ≠ time coverage. Verify MIN/MAX dates before making retention claims.

---

### Common Patterns

```sql
-- Count with NULL handling
SELECT COUNT(*) as total, COUNT(column) as non_null FROM table;

-- Array contains
SELECT * FROM table WHERE 'value' = ANY(array_column);

-- JSON extraction
SELECT json_extract(metadata, '$.key') as value FROM knowledge;

-- Date arithmetic
SELECT CURRENT_DATE - INTERVAL '7 days' as week_ago;

-- String aggregation
SELECT string_agg(column, ', ') FROM table;
```

---

## Workflow Commands (Skills)

Skills are markdown files in `.claude/commands/` (not `skills/`).

| Skill | Purpose |
|-------|---------|
| `/open` | Session open - load context, pull shared repos, import markdown |
| `/close` | Session close - save log, extract transcript, export, commit private + shared repos |
| `/audit` | KB health doctor |

---

## Team Sharing

Share KB entries with others via nested git repos in `markdown/`.

### How It Works

1. Clone a shared repo into `markdown/` (e.g., `markdown/dds/`)
2. Add path to `.gitignore` between markers:
   ```
   # Shared DuckDB-KB MCP repos
   markdown/dds/
   # ^ Shared DuckDB-KB MCP repos
   ```
3. `/open` pulls all shared repos, then imports via `import_from_markdown`
4. `/close` commits and pushes changes to shared repos

### Shared Entry Convention

Entries in shared repos use the repo name as category prefix:
- Category: `dds` (repo name)
- ID: `dds-{topic}` (e.g., `dds-pds-core-utils`)

### Commands

```bash
./venv/bin/python tools/shared_repos.py pull   # Pull all shared repos
./venv/bin/python tools/shared_repos.py push   # Commit and push all
./venv/bin/python tools/shared_repos.py list   # Show configured repos
```

---

## User Configuration

| File | Purpose |
|------|---------|
| `kb-mode.csv` | Mode configuration (mode, is_auto, id) - controls what loads per mode |
| `.gitignore` | Shared repo paths between marker comments |

---

## Content Structure

Entries should start with ~400 char dense preview, then full structured content. This enables `scan_knowledge` to surface relevant entries without loading full content.

---

## ID Conventions

Format: `{category}-{topic}-{specifics}`

Examples: `reference-person-john-doe`, `pattern-duckdb-upsert`, `session-047`

---

*Structural documentation for the MCP itself.*

---

*KB Entry: `seed-duckdb-kb-mcp-architecture` | Category: seed | Updated: 2026-01-22*
