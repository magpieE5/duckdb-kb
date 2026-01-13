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
updated: '2026-01-11T22:58:33.588835'
---

# duckdb-kb MCP Architecture

**DuckDB-powered knowledge base MCP server providing persistent AI memory and session continuity. Single-table schema with tools for CRUD, search, session logging, and markdown backup/restore**

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

### kb_access.parquet
Access logging (timestamp, session, op, id). 

### kb-mode.csv
Personal mode configuration (mode, is_auto, id). Controls what loads on `/open {mode}`.

---

## Categories

reference, pattern, table, command, issue, troubleshooting, project, decision, research, log, transcript, todo, seed, other

---

## MCP Tools (14)

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

## Workflow Commands (Skills)

| Skill | Purpose |
|-------|---------|
| `/open [mode...]` | Session open - load context, pull shared repos, supports multiple modes |
| `/close` | Session close - save log, extract transcript, export, commit main repo AND shared repos |
| `/audit [repo]` | KB health check |

---

## User Configuration

| File | Purpose |
|------|---------|
| `kb-mode.csv` | Mode configuration (mode, is_auto, id) - controls what loads per mode |

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

*KB Entry: `seed-duckdb-kb-mcp-architecture` | Category: seed | Updated: 2026-01-11*
