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
created: '2025-12-13T19:27:48.062907'
updated: '2025-12-26T22:51:30.292185'
---

# duckdb-kb MCP Architecture

**DuckDB-powered knowledge base MCP server providing persistent AI memory and session continuity. Single-table schema with tools for CRUD, search, session logging, and markdown backup/restore.**

---

## Location

Repository: `~/duckdb-kb/`
Database: `~/duckdb-kb/kb.parquet` (loaded into DuckDB in-memory at runtime)
Transcripts: `~/duckdb-kb/markdown/transcript/` (verbatim session exchanges, upserted to KB)

---

## Schema

Single table: `knowledge`

| Column | Type | Description |
|--------|------|-------------|
| id | VARCHAR PRIMARY KEY | Kebab-case identifier |
| category | VARCHAR | Entry type (reference, pattern, seed, etc.) |
| title | VARCHAR | Human-readable title |
| tags | VARCHAR[] | Array of tags |
| content | TEXT | Full markdown content |
| metadata | JSON | Additional structured data |
| created | TIMESTAMP | Creation time |
| updated | TIMESTAMP | Last update time |

---

## Categories

- **reference**: Static facts (people, systems, orgs)
- **pattern**: Reusable approaches, how-tos
- **table**: Schema/structure documentation
- **command**: CLI commands, scripts
- **issue**: Bugs, problems, investigations
- **troubleshooting**: Diagnostic procedures
- **project**: Active initiatives
- **decision**: Architectural choices with rationale
- **research**: Investigations, explorations
- **log**: Session logs (use log_session tool)
- **transcript**: Verbatim session exchanges (User/Thinking/Said)
- **todo**: Rolling task lists
- **seed**: Minting templates and structural foundations
- **other**: Escape hatch

---

## MCP Tools (13)

| Tool | Purpose |
|------|---------|
| `upsert_knowledge` | Create or update entry |
| `get_knowledge` | Retrieve full entries by WHERE clause |
| `scan_knowledge` | FTS search with 400-char previews |
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

---

## Session Logs vs Transcripts

**Logs** (category=log): Capture meaning - preview, witness, handoff. Searchable, relational context.

**Transcripts** (category=transcript): Verbatim exchanges - User/Thinking/Said. Upserted to KB at session close via extract_exchanges.py. Searchable via remember-when.md.

**JSONL** (in `~/.claude/projects/`): Raw source of truth. Never loaded directly.

---

## scan_knowledge Behavior

**scan_knowledge uses full-text search (FTS), not exact substring matching.**

- Single words work best: "derek", "cognos", "pds"
- Multi-word queries are tokenized and ranked by relevance
- Results sorted by FTS score (higher = more relevant)
- Returns 400-char previews for context
- Transcripts excluded by default (use include_transcripts: true)

**For complex queries, use raw_query:**
```sql
-- Multiple conditions
SELECT id, title FROM knowledge 
WHERE content ILIKE '%keyword1%' AND content ILIKE '%keyword2%'

-- Category filtering
SELECT id, title FROM knowledge WHERE category = 'pattern'
```

---

## Workflow Commands

| File | Purpose |
|------|---------|
| `open.md` | Session open - load context |
| `close.md` | Session close - save log, extract transcript, export, commit |
| `search.md {topic}` | Search KB for topic |
| `audit.md [scope]` | KB health check/audit |
| `setup.md` | One-time setup |
| `remember-when.md` | Search transcripts for verbatim exchanges |

---

## Content Structure

Entries should start with ~400 char dense preview containing key facts, then full structured content below. This enables `scan_knowledge` to surface relevant entries without loading full content.

---

## Backup/Restore

Markdown files with YAML frontmatter stored in `~/duckdb-kb/markdown/` organized by category subdirectories.

Export: `export_to_markdown` tool
Import: `import_from_markdown` tool

---

## ID Conventions

Format: `{category}-{topic}-{specifics}`

Examples:
- `reference-person-john-doe`
- `pattern-duckdb-upsert`
- `seed-arlo-foundations`
- ``
- `transcript-047`

---

*Structural documentation for the MCP itself.*

---

*KB Entry: `seed-duckdb-kb-mcp-architecture` | Category: seed | Updated: 2025-12-26*
