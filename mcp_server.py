#!/usr/bin/env python3
"""
DuckDB Knowledge Base MCP Server

Provides 15 tools for Claude Code to interact with knowledge base:
- CRUD: upsert_knowledge, delete_knowledge
- Read: get_knowledge, list_knowledge, query_knowledge
- Search: find_similar, smart_search
- Utility: get_stats, generate_embeddings, export_to_markdown, import_from_markdown
- System: initialize_database, git_commit_and_get_sha, get_kb_session_status, check_token_budgets
"""

import json
import os
from pathlib import Path
from typing import Any, Optional, List, Dict, Tuple
from datetime import datetime

import duckdb
from mcp.server import Server
from mcp.types import Tool, TextContent, EmbeddedResource
import mcp.server.stdio

# Embedding generation
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None

# Fallback: Local embeddings
try:
    from sentence_transformers import SentenceTransformer
    LOCAL_EMBEDDINGS_AVAILABLE = True
except ImportError:
    LOCAL_EMBEDDINGS_AVAILABLE = False
    SentenceTransformer = None

# Check if any embedding provider is available
EMBEDDINGS_AVAILABLE = OPENAI_AVAILABLE or LOCAL_EMBEDDINGS_AVAILABLE


# =============================================================================
# Configuration
# =============================================================================

DB_PATH = os.getenv('KB_DB_PATH', 'kb.duckdb')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
EMBEDDING_PROVIDER = os.getenv('EMBEDDING_PROVIDER', 'openai')  # 'openai' or 'local'
EMBEDDING_MODEL = 'text-embedding-3-large'  # OpenAI model (best quality)
EMBEDDING_DIM = 3072  # OpenAI text-embedding-3-large dimensions

# Semantic search default threshold
DEFAULT_SIMILARITY_THRESHOLD = 0.5  # Conservative threshold for high-quality matches (lower for broader results)

# Local model fallback
LOCAL_MODEL = 'all-MiniLM-L6-v2'
LOCAL_DIM = 384

# Lazy-load embedding models (only when needed)
_embedding_model = None
_openai_client = None


def get_openai_client():
    """Lazy load OpenAI client"""
    global _openai_client

    if not OPENAI_AVAILABLE:
        raise RuntimeError("openai package not installed. Run: pip install openai")

    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not set. Run: export OPENAI_API_KEY='sk-...'")

    if _openai_client is None:
        _openai_client = OpenAI(api_key=OPENAI_API_KEY)

    return _openai_client


def get_local_embedding_model():
    """Lazy load local embedding model"""
    global _embedding_model

    if not LOCAL_EMBEDDINGS_AVAILABLE:
        raise RuntimeError("sentence-transformers not installed. Run: pip install sentence-transformers")

    if _embedding_model is None:
        _embedding_model = SentenceTransformer(LOCAL_MODEL)

    return _embedding_model


def generate_embedding_openai(text: str) -> List[float]:
    """Generate embedding using OpenAI API"""
    client = get_openai_client()

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    return response.data[0].embedding


def generate_embedding_local(text: str) -> List[float]:
    """Generate embedding using local model"""
    model = get_local_embedding_model()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()


def generate_embedding(text: str) -> List[float]:
    """Generate embedding (tries OpenAI first, falls back to local)"""
    if EMBEDDING_PROVIDER == 'openai' and OPENAI_API_KEY:
        try:
            return generate_embedding_openai(text)
        except Exception as e:
            pass  # Fallback to local embeddings
            if LOCAL_EMBEDDINGS_AVAILABLE:
                return generate_embedding_local(text)
            raise
    elif LOCAL_EMBEDDINGS_AVAILABLE:
        return generate_embedding_local(text)
    else:
        raise RuntimeError("No embedding provider available. Install openai or sentence-transformers")


def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for multiple texts (efficient batching)"""
    if EMBEDDING_PROVIDER == 'openai' and OPENAI_API_KEY:
        # OpenAI supports batch in single API call (up to ~2048 inputs)
        try:
            client = get_openai_client()
            response = client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            pass  # Fallback to local embeddings
            if LOCAL_EMBEDDINGS_AVAILABLE:
                model = get_local_embedding_model()
                embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
                return [emb.tolist() for emb in embeddings]
            raise
    elif LOCAL_EMBEDDINGS_AVAILABLE:
        model = get_local_embedding_model()
        embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        return [emb.tolist() for emb in embeddings]
    else:
        raise RuntimeError("No embedding provider available")


# =============================================================================
# MCP Server
# =============================================================================

app = Server("duckdb-knowledge")


def get_connection():
    """Get DuckDB connection with VSS extension loaded

    Note: Database schema must be initialized first via initialize_database MCP tool.
    This is handled by /kb command initialization flow.
    """
    con = duckdb.connect(DB_PATH)

    # Load VSS extension (if available)
    try:
        con.execute("INSTALL vss")  # Idempotent - safe to run every time
        con.execute("LOAD vss")
    except:
        # VSS might not be installed yet, that's ok for non-semantic operations
        pass

    return con


# =============================================================================
# Tool 1: Get Knowledge (Read single entry)
# =============================================================================

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_knowledge",
            description="""Get a single knowledge entry by ID. Returns full details including content, metadata, tags, and related entries.

WHEN TO USE: When you know the exact entry ID you want.
EXAMPLE: get_knowledge({"id": "pattern-caching-strategy"})
TIP: If you don't know the ID, use find_similar() or smart_search() first.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "Unique identifier for the knowledge entry"
                    },
                    "include_related": {
                        "type": "boolean",
                        "description": "Include related entries via links (default: false)",
                        "default": False
                    }
                },
                "required": ["id"]
            }
        ),

        # =============================================================================
        # Tool 2: List Knowledge (Browse/filter)
        # =============================================================================

        Tool(
            name="list_knowledge",
            description="""List knowledge entries with optional filters. Good for browsing by category, tags, or date range.

WHEN TO USE: Browsing without semantic search, exact tag/category filtering, getting recent entries.
BEST FOR: "Show me all commands" or "List recent troubleshooting entries"
NOT FOR: Conceptual search (use find_similar) or complex queries (use query_knowledge)
TIP: Returns previews only - use get_knowledge() to get full content.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Filter by category (table, command, issue, pattern, troubleshooting, etc.)",
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by tags (matches if entry has ANY of these tags)"
                    },
                    "date_after": {
                        "type": "string",
                        "description": "ISO timestamp - only entries updated after this date"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 20)",
                        "default": 20
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Skip this many results (for pagination)",
                        "default": 0
                    }
                }
            }
        ),

        # =============================================================================
        # Tool 3: Query Knowledge (Raw SQL access)
        # =============================================================================

        Tool(
            name="query_knowledge",
            description="""Execute a custom SQL query on the knowledge database. Use for complex filtering, aggregations, or joins. The main table is 'knowledge' with columns: id, category, title, tags, content, metadata, embedding, created, updated.

WHEN TO USE: Complex analytics, aggregations, custom filtering logic not available in other tools.
BEST FOR: "Count entries by category", "Find entries with specific tag combinations", "Analyze tag usage"
NOT FOR: Semantic search (use find_similar) or simple filtering (use list_knowledge)
EXAMPLE: query_knowledge({"sql": "SELECT category, COUNT(*) FROM knowledge GROUP BY category"})""",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "SQL query to execute (SELECT only)"
                    }
                },
                "required": ["sql"]
            }
        ),

        # =============================================================================
        # Tool 4: Find Similar (Semantic search)
        # =============================================================================

        Tool(
            name="find_similar",
            description="""Find knowledge entries semantically similar to a query using embeddings. Searches by meaning/concept, not just keywords. Use to identify duplicate or related entries (set similarity_threshold=0.8+ for near-duplicates). Helpful for consolidation efforts.

WHEN TO USE: Conceptual/semantic search, finding related content, checking for duplicates.
BEST FOR: "Find entries about error handling" or "What's similar to this concept?"
NOT FOR: Exact keyword matching (use query_knowledge with LIKE) or browsing (use list_knowledge)
THRESHOLDS: 0.9+=duplicates, 0.7-0.9=related, 0.5-0.7=loosely related, <0.5=unrelated
TIP: Start with threshold=0.5, adjust based on results. Lower=more results, higher=more precise.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language query describing what to find"
                    },
                    "category": {
                        "type": "string",
                        "description": "Optional: limit search to this category"
                    },
                    "similarity_threshold": {
                        "type": "number",
                        "description": f"Minimum cosine similarity (0-1, default: {DEFAULT_SIMILARITY_THRESHOLD})",
                        "default": DEFAULT_SIMILARITY_THRESHOLD
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results (default: 10)",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ),

        # =============================================================================
        # Tool 5: Smart Search (Hybrid SQL + semantic)
        # =============================================================================

        Tool(
            name="smart_search",
            description="""Hybrid search combining SQL filters (category, tags, dates) with semantic similarity ranking. Best for 'recent performance issues' or 'patterns about caching' type queries. Use BEFORE creating new entries to check for duplicates or related content. Returns similarity scores to help identify fragmentation.

WHEN TO USE: Filtered semantic search - combine category/tags/date filters with conceptual search.
BEST FOR: "Recent entries about X", "Patterns related to Y", "Troubleshooting Z from last month"
NOT FOR: Browse all (use list_knowledge) or pure semantic (use find_similar)
**IMPORTANT**: ALWAYS use this before creating new entries to avoid duplicates!
TIP: More filters = faster, more focused results.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language query for semantic matching"
                    },
                    "category": {
                        "type": "string",
                        "description": "Filter by category"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Filter by tags (entry must have at least one)"
                    },
                    "date_after": {
                        "type": "string",
                        "description": "ISO timestamp - only entries updated after this"
                    },
                    "similarity_threshold": {
                        "type": "number",
                        "description": f"Minimum similarity score (default: {DEFAULT_SIMILARITY_THRESHOLD})",
                        "default": DEFAULT_SIMILARITY_THRESHOLD
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results (default: 10)",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ),

        # =============================================================================
        # Tool 6: Upsert Knowledge (Create or update)
        # =============================================================================

        Tool(
            name="upsert_knowledge",
            description="""Create a new knowledge entry or update existing one. Automatically generates embedding if content is provided.

DUPLICATE DETECTION: By default, automatically checks for similar entries (similarity >= 0.75) before saving. If duplicates found, returns warning without saving - you can then update existing entry or force create. This prevents fragmentation and ensures knowledge base quality.

WHEN TO USE: Saving valuable knowledge, fixing/updating entries, consolidating duplicates.
WORKFLOW (AUTOMATIC): 1) Duplicate check runs automatically, 2) If similar found, returns warning with options, 3) You decide: update existing or force_create=True
ID FORMAT: Use kebab-case like 'pattern-topic-specifics' or 'troubleshooting-issue-name'
TAGS: Include 4-6 relevant tags + layer tag (layer:base, layer:team, or layer:personal)

PARAMETERS:
- check_duplicates (default: true): Automatically search for similar entries before saving
- force_create (default: false): Skip duplicate check and save anyway
- similarity_threshold (default: 0.75): Minimum similarity to flag duplicates (0.0-1.0)""",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "Unique identifier (e.g., 'pattern-caching-strategy', 'issue-bug-123')"
                    },
                    "category": {
                        "type": "string",
                        "description": "Category: table, command, issue, pattern, troubleshooting, reference, other"
                    },
                    "title": {
                        "type": "string",
                        "description": "Human-readable title"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of tags for categorization"
                    },
                    "content": {
                        "type": "string",
                        "description": "Main content (markdown supported)"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Additional structured data (JSON object)"
                    },
                    "generate_embedding": {
                        "type": "boolean",
                        "description": "Auto-generate embedding from content (default: true)",
                        "default": True
                    },
                    "check_duplicates": {
                        "type": "boolean",
                        "description": "Check for similar entries before saving (default: true)",
                        "default": True
                    },
                    "force_create": {
                        "type": "boolean",
                        "description": "Skip duplicate check and save anyway (default: false)",
                        "default": False
                    },
                    "similarity_threshold": {
                        "type": "number",
                        "description": "Minimum similarity score to flag duplicates, 0.0-1.0 (default: 0.75)",
                        "default": 0.75,
                        "minimum": 0.0,
                        "maximum": 1.0
                    }
                },
                "required": ["id", "category", "title", "content"]
            }
        ),

        # =============================================================================
        # Tool 7: Delete Knowledge
        # =============================================================================

        Tool(
            name="delete_knowledge",
            description="""Delete a knowledge entry by ID. This also removes all links to/from this entry. Use for: obsolete entries, duplicates after consolidation, one-off solutions that didn't generalize, or entries superseded by better versions. Consider consolidating multiple related entries instead of just deleting.

WHEN TO USE: Removing obsolete/duplicate entries AFTER consolidating their useful content elsewhere.
CAUTION: Deletion is permanent! Consider updating with deprecation notice instead.
WORKFLOW: 1) Review entry, 2) Extract any valuable content, 3) Consolidate into other entries, 4) Then delete
CAUTION: Deletion is permanent!""",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "ID of entry to delete"
                    }
                },
                "required": ["id"]
            }
        ),

        # =============================================================================
        # Tool 8: Get Stats
        # =============================================================================

        Tool(
            name="get_stats",
            description="""Get database statistics including entry counts by category, embedding status, tag usage, etc.

WHEN TO USE: First time connecting, health checks, understanding KB contents, planning maintenance.
RETURNS: Entry counts, categories, embedding coverage, top tags
**RECOMMENDED**: Run this first when connecting to understand what's in the knowledge base!
TIP: Use detailed=true for category breakdowns and tag analysis.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "detailed": {
                        "type": "boolean",
                        "description": "Include detailed breakdown (default: false)",
                        "default": False
                    }
                }
            }
        ),

        # =============================================================================
        # Tool 9: Generate Embeddings (Batch utility)
        # =============================================================================

        Tool(
            name="generate_embeddings",
            description="""Generate embeddings for entries that don't have them yet. Uses OpenAI text-embedding-3-large (3072 dimensions) by default. Falls back to local model if OpenAI unavailable. Requires network connectivity.

WHEN TO USE: After bulk imports, when entries missing embeddings, after restoring from backup.
COST: ~$0.00002 per 1K tokens (~$0.001 for 100 entries)
TIP: Set regenerate=false (default) to only generate missing embeddings, not replace existing. Returns count of entries processed, no pre-check needed.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific entry IDs to generate embeddings for (optional - generates for all missing if not specified)"
                    },
                    "regenerate": {
                        "type": "boolean",
                        "description": "Regenerate embeddings even if they already exist (default: false)",
                        "default": False
                    },
                    "batch_size": {
                        "type": "integer",
                        "description": "Number of entries to process at once (default: 32)",
                        "default": 32
                    }
                }
            }
        ),

        # =============================================================================
        # Tool 10: Export to Markdown (BACKUP - replaces old backup system)
        # =============================================================================

        Tool(
            name="export_to_markdown",
            description="""BACKUP: Export KB to markdown files. This REPLACES the old backup system. Creates YAML frontmatter with all metadata, preserves links as wikilinks, organizes by category.

WHEN TO USE: Regular backups, version control, read/edit in any markdown editor
OUTPUT: Markdown files with full metadata - can fully restore DB from these files
FORMAT: YAML frontmatter (all DB fields) + markdown content + links footer
RESTORE: Use import_from_markdown() to restore from backup
TIP: Embeddings NOT stored (regenerate on import to save space)
BEST PRACTICE: Export to ~/duckdb-kb/markdown/ for version control + git backup""",
            inputSchema={
                "type": "object",
                "properties": {
                    "output_dir": {
                        "type": "string",
                        "description": "Directory to export files (default: ~/duckdb-kb/markdown). Created if doesn't exist."
                    },
                    "category": {
                        "type": "string",
                        "description": "Optional: Only export this category (table, command, issue, pattern, etc.)"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional: Only export entries with these tags"
                    },
                    "organize_by_category": {
                        "type": "boolean",
                        "description": "Create subdirectories by category (default: true)",
                        "default": True
                    }
                },
                "required": []
            }
        ),

        # =============================================================================
        # Tool 11: Import from Markdown (RESTORE - replaces old restore system)
        # =============================================================================

        Tool(
            name="import_from_markdown",
            description="""RESTORE: Restore KB from markdown backup. This is for DISASTER RECOVERY and MIGRATION only.

IMPORTANT: Markdown exports are BACKUPS, not a bi-directional sync. The DuckDB KB (via MCP) is the single source of truth for read/write operations. Only use this tool to restore after data loss or migrate to a new system.

WHEN TO USE: Disaster recovery (DB corrupted), migrate to new machine, testing (tear-down/restore)
DO NOT USE FOR: Importing manual edits to markdown files (markdown exports are read-only for humans)
PROCESS: Always upserts (inserts new, updates existing), recreates links, regenerates embeddings
TIP: Run get_stats() before/after to verify restore""",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_dir": {
                        "type": "string",
                        "description": "Directory with markdown backup files (e.g., '~/duckdb-kb/backup')"
                    },
                    "generate_embeddings": {
                        "type": "boolean",
                        "description": "Generate embeddings after import (default: true for disaster recovery)",
                        "default": True
                    },
                    "category": {
                        "type": "string",
                        "description": "Optional: Only import files from this category subdirectory"
                    }
                },
                "required": ["input_dir"]
            }
        ),

        # =============================================================================
        # Tool 12: Initialize Database
        # =============================================================================

        Tool(
            name="initialize_database",
            description="""Initialize or reinitialize the DuckDB knowledge base with schema.

Creates kb.duckdb file, loads VSS extension (if available), and executes schema.sql to set up tables, indexes, views, and macros.

WHEN TO USE: First run, database recovery, or force reinitialize
Returns: Success status, VSS availability, and initial database stats""",
            inputSchema={
                "type": "object",
                "properties": {
                    "force": {
                        "type": "boolean",
                        "description": "Force reinitialize even if database exists (default: false)",
                        "default": False
                    }
                }
            }
        ),

        # =============================================================================
        # Tool 13: Git Commit and Get SHA
        # =============================================================================

        Tool(
            name="git_commit_and_get_sha",
            description="""Perform git add -A, commit with message, and return commit SHA.

Deterministic git workflow for /sm command. Automatically stages all changes, creates commit, and returns SHA for KB log entry metadata.

Returns: {"success": true, "sha": "abc123..."} or error""",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "Git commit message (must follow KB-BASE.md format)"
                    }
                },
                "required": ["message"]
            }
        ),

        # =============================================================================
        # Tool 14: Get KB Session Status
        # =============================================================================

        Tool(
            name="get_kb_session_status",
            description="""Get KB initialization status, parse USER.md for focus areas and commitments.

Returns structured JSON with:
- database.action: "init_db_fresh", "init_db_restore", or "check_empty"
- kb_md.action: "setup_kb_md" if template, "ready" if populated
- status.focus_areas: Top 5 parsed from USER.md Current Focus
- status.commitments: All, approaching (7 days), and overdue commitments

Used by /kb command for deterministic initialization flow.""",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="check_token_budgets",
            description="""Check USER.md and ARLO.md token budgets against 10K limit.

Uses tiktoken if available, falls back to word-count approximation (words × 1.3).
Returns token counts, budget status, and compression triggers.

WHEN TO USE:
- During /sm workflow (mandatory measurement)
- Before manual compression
- Verifying budget compliance

Returns structured status for each file checked.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "files": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "File paths to check (default: ['.claude/USER.md', '.claude/ARLO.md'])"
                    },
                    "budget": {
                        "type": "integer",
                        "default": 10000,
                        "description": "Token budget limit (default: 10000)"
                    },
                    "warning_threshold": {
                        "type": "integer",
                        "default": 9000,
                        "description": "Warning threshold for compression trigger (default: 9000)"
                    }
                }
            }
        ),
    ]


# =============================================================================
# Tool Implementations
# =============================================================================

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""

    # Tools that don't need a database connection
    NO_DB_TOOLS = {"initialize_database", "git_commit_and_get_sha", "get_kb_session_status", "check_token_budgets"}

    # Only get connection for tools that need it
    con = None
    if name not in NO_DB_TOOLS:
        con = get_connection()

    try:
        if name == "get_knowledge":
            return await tool_get_knowledge(con, arguments)
        elif name == "list_knowledge":
            return await tool_list_knowledge(con, arguments)
        elif name == "query_knowledge":
            return await tool_query_knowledge(con, arguments)
        elif name == "find_similar":
            return await tool_find_similar(con, arguments)
        elif name == "smart_search":
            return await tool_smart_search(con, arguments)
        elif name == "upsert_knowledge":
            return await tool_upsert_knowledge(con, arguments)
        elif name == "delete_knowledge":
            return await tool_delete_knowledge(con, arguments)
        elif name == "get_stats":
            return await tool_get_stats(con, arguments)
        elif name == "generate_embeddings":
            return await tool_generate_embeddings(con, arguments)
        elif name == "export_to_markdown":
            return await tool_export_to_markdown(con, arguments)
        elif name == "import_from_markdown":
            return await tool_import_from_markdown(con, arguments)
        elif name == "initialize_database":
            return await tool_initialize_database(arguments)
        elif name == "git_commit_and_get_sha":
            return await tool_git_commit_and_get_sha(arguments)
        elif name == "get_kb_session_status":
            return await tool_get_kb_session_status(arguments)
        elif name == "check_token_budgets":
            return await tool_check_token_budgets(arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    finally:
        if con is not None:
            try:
                con.close()
            except Exception:
                pass  # Already closed or connection invalid


# Tool: Get Knowledge
async def tool_get_knowledge(con: duckdb.DuckDBPyConnection, args: dict) -> list[TextContent]:
    entry_id = args["id"]

    result = con.execute("SELECT * FROM knowledge WHERE id = ?", [entry_id]).fetchone()

    if not result:
        return [TextContent(type="text", text=f"Entry not found: {entry_id}")]

    # Format response
    cols = [desc[0] for desc in con.description]
    entry = dict(zip(cols, result))

    # Remove embedding from output (too large)
    if 'embedding' in entry:
        entry['has_embedding'] = entry['embedding'] is not None
        del entry['embedding']

    return [TextContent(type="text", text=json.dumps(entry, default=str))]


# Tool: List Knowledge
async def tool_list_knowledge(con: duckdb.DuckDBPyConnection, args: dict) -> list[TextContent]:
    category = args.get("category")
    tags = args.get("tags")
    # Normalize tag filters to match DB normalization
    if tags:
        tags = [tag.lower().strip() for tag in tags]
    date_after = args.get("date_after")
    limit = args.get("limit", 20)
    offset = args.get("offset", 0)

    # Build query dynamically
    where_clauses = []
    params = []

    if category:
        where_clauses.append("category = ?")
        params.append(category)

    if tags:
        where_clauses.append("list_has_any(tags, ?)")
        params.append(tags)

    if date_after:
        where_clauses.append("updated > ?")
        params.append(date_after)

    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

    sql = f"""
        SELECT id, category, title, tags,
               left(content, 300) as preview,
               updated
        FROM knowledge
        WHERE {where_sql}
        ORDER BY updated DESC
        LIMIT ? OFFSET ?
    """

    params.extend([limit, offset])

    results = con.execute(sql, params).fetchall()
    cols = [desc[0] for desc in con.description]

    entries = [dict(zip(cols, row)) for row in results]

    return [TextContent(type="text", text=json.dumps(entries, default=str))]


# Tool: Query Knowledge (Raw SQL)
async def tool_query_knowledge(con: duckdb.DuckDBPyConnection, args: dict) -> list[TextContent]:
    sql = args["sql"]

    # Security: Only allow SELECT
    if not sql.strip().upper().startswith("SELECT"):
        return [TextContent(type="text", text="Error: Only SELECT queries allowed")]

    try:
        results = con.execute(sql).fetchall()
        cols = [desc[0] for desc in con.description]

        # Format as list of dicts
        rows = [dict(zip(cols, row)) for row in results]

        return [TextContent(type="text", text=json.dumps(rows, default=str))]

    except Exception as e:
        return [TextContent(type="text", text=f"SQL Error: {str(e)}")]


# Tool: Find Similar (Semantic search)
async def tool_find_similar(con: duckdb.DuckDBPyConnection, args: dict) -> list[TextContent]:
    query = args["query"]
    category = args.get("category")
    threshold = args.get("similarity_threshold", DEFAULT_SIMILARITY_THRESHOLD)
    limit = args.get("limit", 10)

    # Generate query embedding
    try:
        query_embedding = generate_embedding(query)
        # Cast to FLOAT array for DuckDB compatibility
        query_embedding = [float(x) for x in query_embedding]
    except Exception as e:
        return [TextContent(type="text", text=f"Error generating embedding: {str(e)}\nInstall: pip install sentence-transformers")]

    # Execute semantic search (Python implementation - no macro dependency)
    if category:
        sql = """
            SELECT
                id,
                category,
                title,
                tags,
                content,
                metadata,
                array_cosine_similarity(embedding, CAST(? AS FLOAT[3072])) as similarity,
                updated
            FROM knowledge
            WHERE
                embedding IS NOT NULL
                AND category = ?
                AND array_cosine_similarity(embedding, CAST(? AS FLOAT[3072])) > ?
            ORDER BY similarity DESC
            LIMIT ?
        """
        params = [query_embedding, category, query_embedding, threshold, limit]
    else:
        sql = """
            SELECT
                id,
                category,
                title,
                tags,
                content,
                metadata,
                array_cosine_similarity(embedding, CAST(? AS FLOAT[3072])) as similarity,
                updated
            FROM knowledge
            WHERE
                embedding IS NOT NULL
                AND array_cosine_similarity(embedding, CAST(? AS FLOAT[3072])) > ?
            ORDER BY similarity DESC
            LIMIT ?
        """
        params = [query_embedding, query_embedding, threshold, limit]

    results = con.execute(sql, params).fetchall()
    cols = [desc[0] for desc in con.description]

    entries = []
    for row in results:
        entry = dict(zip(cols, row))
        # Truncate content for readability
        if 'content' in entry and len(entry['content']) > 300:
            entry['preview'] = entry['content'][:300] + "..."
            del entry['content']
        if 'embedding' in entry:
            del entry['embedding']
        entries.append(entry)

    # Detect pattern emergence - find clusters of highly similar entries
    clusters = []
    if len(entries) >= 3:  # Only look for clusters if we have enough results
        # Group entries by high similarity (>0.8)
        high_similarity_threshold = 0.8
        for i, entry in enumerate(entries):
            if 'similarity' in entry and entry['similarity'] > high_similarity_threshold:
                # Find all entries with similarity above threshold
                cluster_entries = [e for e in entries if 'similarity' in e and e['similarity'] > high_similarity_threshold]
                if len(cluster_entries) >= 3:
                    clusters.append({
                        "count": len(cluster_entries),
                        "avg_similarity": round(sum(e['similarity'] for e in cluster_entries) / len(cluster_entries), 3),
                        "ids": [e['id'] for e in cluster_entries],
                        "signal": "consolidation_candidate" if len(cluster_entries) >= 4 else "emerging_pattern"
                    })
                    break  # Only report the first cluster found

    # Build response with optional clustering info
    response = {"results": entries}
    if clusters:
        response["clusters"] = clusters
        response["recommendation"] = f"Found {clusters[0]['count']} highly similar entries (similarity>{high_similarity_threshold}). Consider consolidating into a meta-pattern."

    return [TextContent(type="text", text=json.dumps(response, default=str))]


# =============================================================================
# Helper functions for smart_search (Python implementation)
# =============================================================================

def search_logs_python(con: duckdb.DuckDBPyConnection, query_embedding: list[float], threshold: float) -> list[dict]:
    """Search log entries with semantic ranking, sorted by time."""
    sql = """
        SELECT id, category, title, tags, content, metadata, created, updated,
               array_cosine_similarity(embedding, CAST(? AS FLOAT[3072])) AS similarity
        FROM knowledge
        WHERE category = 'log'
          AND embedding IS NOT NULL
          AND array_cosine_similarity(embedding, CAST(? AS FLOAT[3072])) > ?
        ORDER BY created DESC
        LIMIT 20
    """
    params = [query_embedding, query_embedding, threshold]

    result = con.execute(sql, params).fetchall()
    cols = [desc[0] for desc in con.description]

    logs = []
    for row in result:
        entry = dict(zip(cols, row))
        logs.append(entry)

    return logs


def search_exact_python(con: duckdb.DuckDBPyConnection, query_text: str,
                       category: Optional[str], tags: Optional[list],
                       date_after: Optional[str]) -> list[dict]:
    """Search knowledge table for exact text matches (LIKE)."""
    sql = """
        SELECT id, category, title, tags, content, metadata, created, updated,
               1.0 AS similarity,
               'exact' AS match_type
        FROM knowledge
        WHERE (LOWER(id) LIKE LOWER(?)
           OR LOWER(content) LIKE LOWER(?)
           OR LOWER(title) LIKE LOWER(?)
           OR ARRAY_TO_STRING(tags, ',') LIKE LOWER(?))
    """
    params = [f'%{query_text}%'] * 4

    # Add filters
    if category:
        sql += " AND category = ?"
        params.append(category)

    if tags:
        sql += " AND list_has_any(tags, ?)"
        params.append(tags)

    if date_after:
        sql += " AND updated > ?"
        params.append(date_after)

    results = con.execute(sql, params).fetchall()
    cols = [desc[0] for desc in con.description]

    return [dict(zip(cols, row)) for row in results]


def search_semantic_python(con: duckdb.DuckDBPyConnection, query_embedding: list[float],
                          category: Optional[str], tags: Optional[list],
                          date_after: Optional[str], threshold: float) -> list[dict]:
    """Search knowledge table for semantic matches (cosine similarity)."""
    sql = """
        SELECT id, category, title, tags, content, metadata, created, updated,
               array_cosine_similarity(embedding, CAST(? AS FLOAT[3072])) AS similarity,
               'semantic' AS match_type
        FROM knowledge
        WHERE embedding IS NOT NULL
          AND array_cosine_similarity(embedding, CAST(? AS FLOAT[3072])) > ?
    """
    params = [query_embedding, query_embedding, threshold]

    # Add filters
    if category:
        sql += " AND category = ?"
        params.append(category)

    if tags:
        sql += " AND list_has_any(tags, ?)"
        params.append(tags)

    if date_after:
        sql += " AND updated > ?"
        params.append(date_after)

    sql += " ORDER BY similarity DESC"

    results = con.execute(sql, params).fetchall()
    cols = [desc[0] for desc in con.description]

    return [dict(zip(cols, row)) for row in results]


def merge_results(exact_matches: list[dict], semantic_matches: list[dict], limit: int) -> list[dict]:
    """Merge and deduplicate exact + semantic matches, keeping highest similarity per ID."""
    # Index by ID, keeping highest similarity
    merged = {}

    for entry in exact_matches + semantic_matches:
        entry_id = entry['id']
        if entry_id not in merged or entry['similarity'] > merged[entry_id]['similarity']:
            merged[entry_id] = entry

    # Sort by similarity DESC, then updated DESC
    results = sorted(merged.values(),
                    key=lambda x: (x['similarity'], x['updated']),
                    reverse=True)

    return results[:limit]


# Tool: Smart Search (Hybrid - Python implementation)
async def tool_smart_search(con: duckdb.DuckDBPyConnection, args: dict) -> list[TextContent]:
    """
    Multi-prong search:
    1. Search logs (text matching, temporal)
    2. Search knowledge table (exact + semantic)
    """
    query = args["query"]
    category = args.get("category")
    tags = args.get("tags")
    # Normalize tag filters to match DB normalization
    if tags:
        tags = [tag.lower().strip() for tag in tags]
    date_after = args.get("date_after")
    threshold = args.get("similarity_threshold", DEFAULT_SIMILARITY_THRESHOLD)
    limit = args.get("limit", 10)

    # Generate query embedding
    try:
        query_embedding = generate_embedding(query)
        query_embedding = [float(x) for x in query_embedding]
    except Exception as e:
        return [TextContent(type="text", text=f"Error generating embedding: {str(e)}")]

    # 1. Search logs (semantic matching, temporal)
    log_entries = search_logs_python(con, query_embedding, threshold)

    # 2. Multi-prong knowledge search
    # 2a. Exact text matches
    exact_matches = search_exact_python(con, query, category, tags, date_after)

    # 2b. Semantic matches
    semantic_matches = search_semantic_python(con, query_embedding, category, tags, date_after, threshold)

    # 2c. Merge and deduplicate
    kb_entries = merge_results(exact_matches, semantic_matches, limit)

    # Truncate content and remove embeddings from KB entries
    for entry in kb_entries:
        if 'content' in entry and len(entry['content']) > 300:
            entry['content_preview'] = entry['content'][:300] + "..."
            del entry['content']
        if 'embedding' in entry:
            del entry['embedding']

    # Truncate content and remove embeddings from log entries
    for entry in log_entries:
        if 'content' in entry and len(entry['content']) > 300:
            entry['content_preview'] = entry['content'][:300] + "..."
            del entry['content']
        if 'embedding' in entry:
            del entry['embedding']

    return [TextContent(type="text", text=json.dumps({
        "kb_entries": kb_entries,
        "log_timeline": log_entries
    }, default=str))]


# Tool: Upsert Knowledge
async def tool_upsert_knowledge(con: duckdb.DuckDBPyConnection, args: dict) -> list[TextContent]:
    entry_id = args["id"]
    category = args["category"]
    title = args["title"]
    content = args["content"]
    tags = args.get("tags", [])
    # Normalize tags: lowercase + trim whitespace for consistent matching
    tags = [tag.lower().strip() for tag in tags]
    metadata = args.get("metadata", {})
    generate_emb = args.get("generate_embedding", True)

    # New duplicate detection parameters
    check_duplicates = args.get("check_duplicates", True)
    force_create = args.get("force_create", False)
    similarity_threshold = args.get("similarity_threshold", 0.75)

    # Check if entry already exists (this is an update)
    existing = con.execute("SELECT 1 FROM knowledge WHERE id = ?", [entry_id]).fetchone()

    # Skip duplicate check if:
    # - force_create is True
    # - Entry already exists (this is an update)
    # - No embeddings available
    # - check_duplicates is False
    skip_check = force_create or existing or not EMBEDDINGS_AVAILABLE or not check_duplicates

    # Generate embedding (needed for both duplicate check and save)
    embedding = None
    if generate_emb and EMBEDDINGS_AVAILABLE:
        try:
            # Create rich text for embedding (includes title + tags + content)
            embed_text = f"Title: {title}\nTags: {', '.join(tags)}\nContent: {content}"
            embedding = generate_embedding(embed_text)
            # Cast to FLOAT array for DuckDB compatibility
            embedding = [float(x) for x in embedding]
        except Exception as e:
            # Continue without embedding if generation fails
            pass

    # Duplicate detection (pre-flight check)
    if not skip_check and embedding is not None:
        try:
            similar = con.execute("""
                SELECT
                    id,
                    title,
                    array_cosine_similarity(embedding, ?::FLOAT[3072]) as similarity,
                    created,
                    tags
                FROM knowledge
                WHERE embedding IS NOT NULL
                    AND id != ?
                    AND array_cosine_similarity(embedding, ?::FLOAT[3072]) >= ?
                ORDER BY similarity DESC
                LIMIT 5
            """, [embedding, entry_id, embedding, similarity_threshold]).fetchall()

            if similar:
                # Return duplicate warning without saving
                similar_entries = [
                    {
                        "id": row[0],
                        "title": row[1],
                        "similarity": round(row[2], 3),
                        "created": str(row[3]),
                        "tags": row[4]
                    }
                    for row in similar
                ]

                return [TextContent(type="text", text=json.dumps({
                    "status": "duplicate_check",
                    "saved": False,
                    "similar_entries": similar_entries,
                    "recommendation": f"Found {len(similar)} similar entries (threshold: {similarity_threshold})",
                    "next_steps": [
                        f"Update existing: upsert_knowledge(id='{similar[0][0]}', ...)",
                        "Create anyway: upsert_knowledge(..., force_create=True)",
                        f"Stricter match: upsert_knowledge(..., similarity_threshold={min(0.95, round(similarity_threshold + 0.1, 2))})",
                        f"Cast wider net: smart_search(query='...', similarity_threshold={max(0.5, round(similarity_threshold - 0.2, 2))})"
                    ]
                }))]
        except Exception as e:
            # If duplicate check fails, proceed with save (fail-open)
            pass

    # Upsert - get current timestamp as Python datetime
    now = datetime.now()

    # Use different SQL depending on whether we have an embedding
    # (COALESCE doesn't work with FLOAT arrays in DuckDB)
    if embedding is not None:
        con.execute("""
            INSERT INTO knowledge (id, category, title, tags, content, metadata, embedding, created, updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (id) DO UPDATE SET
                category = EXCLUDED.category,
                title = EXCLUDED.title,
                tags = EXCLUDED.tags,
                content = EXCLUDED.content,
                metadata = EXCLUDED.metadata,
                embedding = EXCLUDED.embedding,
                updated = ?
        """, [entry_id, category, title, tags, content, metadata, embedding, now, now, now])
    else:
        con.execute("""
            INSERT INTO knowledge (id, category, title, tags, content, metadata, created, updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (id) DO UPDATE SET
                category = EXCLUDED.category,
                title = EXCLUDED.title,
                tags = EXCLUDED.tags,
                content = EXCLUDED.content,
                metadata = EXCLUDED.metadata,
                updated = ?
        """, [entry_id, category, title, tags, content, metadata, now, now, now])

    return [TextContent(type="text", text=json.dumps({
        "id": entry_id,
        "embedding_generated": embedding is not None
    }))]


# Tool: Delete Knowledge
async def tool_delete_knowledge(con: duckdb.DuckDBPyConnection, args: dict) -> list[TextContent]:
    entry_id = args["id"]

    # Check if exists
    exists = con.execute("SELECT 1 FROM knowledge WHERE id = ?", [entry_id]).fetchone()
    if not exists:
        return [TextContent(type="text", text=f"Entry not found: {entry_id}")]

    # Delete entry
    con.execute("DELETE FROM knowledge WHERE id = ?", [entry_id])

    return [TextContent(type="text", text=json.dumps({
        "id": entry_id
    }))]


# Tool: Get Stats
async def tool_get_stats(con: duckdb.DuckDBPyConnection, args: dict) -> list[TextContent]:
    detailed = args.get("detailed", False)

    # Basic summary (Python implementation - no macro dependency)
    summary_data = []

    # Total entries
    total = con.execute("SELECT COUNT(*) FROM knowledge").fetchone()[0]
    summary_data.append(('Total Entries', str(total)))

    # With embeddings
    with_emb = con.execute("SELECT COUNT(*) FROM knowledge WHERE embedding IS NOT NULL").fetchone()[0]
    summary_data.append(('With Embeddings', str(with_emb)))

    # Categories
    categories_count = con.execute("SELECT COUNT(DISTINCT category) FROM knowledge").fetchone()[0]
    summary_data.append(('Categories', str(categories_count)))

    # Unique tags
    tags_count = con.execute("""
        SELECT COUNT(DISTINCT t.tag)
        FROM knowledge k, UNNEST(k.tags) AS t(tag)
    """).fetchone()[0]
    summary_data.append(('Unique Tags', str(tags_count)))

    stats = {
        "summary": {row[0]: row[1] for row in summary_data}
    }

    if detailed:
        # Category breakdown (Python implementation)
        categories = con.execute("""
            SELECT
                category,
                COUNT(*) as count,
                COUNT(embedding) as embeddings_generated,
                ROUND(100.0 * COUNT(embedding) / COUNT(*), 1) as embedding_pct,
                MIN(created) as oldest,
                MAX(updated) as newest
            FROM knowledge
            GROUP BY category
            ORDER BY count DESC
        """).fetchall()

        stats["by_category"] = [
            {
                "category": row[0],
                "count": row[1],
                "embeddings_generated": row[2],
                "embedding_pct": row[3],
                "oldest": str(row[4]),
                "newest": str(row[5])
            }
            for row in categories
        ]

        # Tag usage (Python implementation)
        tags = con.execute("""
            SELECT
                t.tag,
                COUNT(*) as usage,
                LIST(DISTINCT k.category) as categories
            FROM knowledge k, UNNEST(k.tags) AS t(tag)
            GROUP BY t.tag
            ORDER BY usage DESC
            LIMIT 20
        """).fetchall()

        stats["top_tags"] = [
            {"tag": row[0], "count": row[1], "categories": row[2]}
            for row in tags
        ]

    return [TextContent(type="text", text=json.dumps(stats, default=str))]


# Tool: Generate Embeddings
async def tool_generate_embeddings(con: duckdb.DuckDBPyConnection, args: dict) -> list[TextContent]:
    ids = args.get("ids")
    regenerate = args.get("regenerate", False)
    batch_size = args.get("batch_size", 32)

    if not EMBEDDINGS_AVAILABLE:
        return [TextContent(type="text", text="Error: sentence-transformers not installed.\nRun: pip install sentence-transformers")]

    # Find entries needing embeddings
    if ids:
        where = f"id IN ({','.join(['?'] * len(ids))})"
        params = ids
    elif regenerate:
        where = "1=1"
        params = []
    else:
        where = "embedding IS NULL"
        params = []

    sql = f"""
        SELECT id, title, tags, content
        FROM knowledge
        WHERE {where}
    """

    entries = con.execute(sql, params).fetchall()

    if not entries:
        return [TextContent(type="text", text="No entries need embeddings")]

    # Generate embeddings in batches
    total = len(entries)
    updated = 0

    for i in range(0, total, batch_size):
        batch = entries[i:i+batch_size]

        # Create rich embedding text for each entry
        texts = [
            f"Title: {row[1]}\nTags: {', '.join(row[2])}\nContent: {row[3]}"
            for row in batch
        ]

        # Generate batch embeddings (uses GPU on M2 Max!)
        embeddings = generate_embeddings_batch(texts)

        # Update database
        now = datetime.now()
        for (entry_id, _, _, _), embedding in zip(batch, embeddings):
            # Cast to FLOAT array for DuckDB compatibility
            embedding = [float(x) for x in embedding]
            con.execute(
                "UPDATE knowledge SET embedding = ?, updated = ? WHERE id = ?",
                [embedding, now, entry_id]
            )
            updated += 1

    provider = "OpenAI" if (EMBEDDING_PROVIDER == 'openai' and OPENAI_API_KEY) else "Local"
    model = EMBEDDING_MODEL if provider == "OpenAI" else LOCAL_MODEL
    dims = EMBEDDING_DIM if provider == "OpenAI" else LOCAL_DIM

    return [TextContent(type="text", text=json.dumps({
        "status": "success",
        "total_entries": total,
        "updated": updated,
        "provider": provider,
        "model": model,
        "dimensions": dims
    }))]


# Tool: Export to Markdown (Backup)
async def tool_export_to_markdown(con: duckdb.DuckDBPyConnection, args: dict) -> list[TextContent]:
    """Export KB entries to markdown files"""
    import os
    import yaml
    from pathlib import Path

    # Default to standard location if not provided
    default_output = "~/duckdb-kb/markdown"
    output_dir_str = args.get("output_dir", default_output)
    output_dir = Path(os.path.expanduser(output_dir_str))
    category_filter = args.get("category")
    tags_filter = args.get("tags")
    # Normalize tag filters to match DB normalization
    if tags_filter:
        tags_filter = [tag.lower().strip() for tag in tags_filter]
    organize_by_category = args.get("organize_by_category", True)

    # Build query
    where_clauses = []
    params = []

    if category_filter:
        where_clauses.append("category = ?")
        params.append(category_filter)

    if tags_filter:
        # Match if entry has ANY of the tags
        tag_conditions = " OR ".join(["list_contains(tags, ?)" for _ in tags_filter])
        where_clauses.append(f"({tag_conditions})")
        params.extend(tags_filter)

    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

    # Fetch entries
    query = f"SELECT id, category, title, content, tags, metadata, created, updated FROM knowledge WHERE {where_sql} ORDER BY category, id"
    entries = con.execute(query, params).fetchall()

    if not entries:
        return [TextContent(type="text", text="No entries found matching filters")]

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Clear existing category directories for clean export
    if organize_by_category:
        import shutil
        for cat_dir in output_dir.iterdir():
            if cat_dir.is_dir() and cat_dir.name not in ['.obsidian', '.git']:
                shutil.rmtree(cat_dir)

    exported_count = 0

    for entry in entries:
        entry_id, category, title, content, tags, metadata, created, updated = entry

        # Determine output file path
        if organize_by_category:
            cat_dir = output_dir / category
            cat_dir.mkdir(exist_ok=True)
            file_path = cat_dir / f"{entry_id}.md"
        else:
            file_path = output_dir / f"{entry_id}.md"

        # Build YAML frontmatter
        frontmatter = {
            "id": entry_id,
            "category": category,
            "title": title,
            "tags": tags if tags else [],
            "created": created.isoformat() if created else None,
            "updated": updated.isoformat() if updated else None,
        }

        if metadata:
            frontmatter["metadata"] = json.loads(metadata) if isinstance(metadata, str) else metadata

        # Build markdown content
        md_content = "---\n"
        md_content += yaml.dump(frontmatter, sort_keys=False, allow_unicode=True)
        md_content += "---\n\n"

        # Only add title if content doesn't start with it
        if content and content.strip().startswith(f"# {title}"):
            md_content += content
        else:
            md_content += f"# {title}\n\n"
            md_content += content if content else ""

        # Add metadata footer
        md_content += f"\n\n---\n\n*KB Entry: `{entry_id}` | Category: {category} | Updated: {updated.date() if updated else 'N/A'}*\n"

        # Write file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(md_content)

        exported_count += 1

    return [TextContent(type="text", text=f"✓ Exported {exported_count} entries to {output_dir}\n\nOrganized by category: {organize_by_category}\nBackup complete! Use import_from_markdown() to restore.")]


# Tool: Import from Markdown (Restore)
async def tool_import_from_markdown(con: duckdb.DuckDBPyConnection, args: dict) -> list[TextContent]:
    """Restore KB entries from markdown backup (disaster recovery/migration only)"""
    import os
    import yaml
    import re
    from pathlib import Path

    input_dir = Path(os.path.expanduser(args["input_dir"]))
    generate_embeddings_flag = args.get("generate_embeddings", True)
    category_filter = args.get("category")

    if not input_dir.exists():
        return [TextContent(type="text", text=f"Error: Directory not found: {input_dir}")]

    # Find all markdown files
    if category_filter:
        cat_dir = input_dir / category_filter
        if not cat_dir.exists():
            return [TextContent(type="text", text=f"Error: Category directory not found: {cat_dir}")]
        md_files = list(cat_dir.glob("*.md"))
    else:
        md_files = list(input_dir.rglob("*.md"))

    if not md_files:
        return [TextContent(type="text", text=f"No markdown files found in {input_dir}")]

    imported_count = 0  # New entries inserted
    updated_count = 0   # Existing entries updated
    skipped_count = 0   # Invalid/malformed files

    for md_file in md_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse YAML frontmatter
            if not content.startswith('---'):
                skipped_count += 1
                continue

            # Extract frontmatter
            parts = content.split('---', 2)
            if len(parts) < 3:
                skipped_count += 1
                continue

            frontmatter = yaml.safe_load(parts[1])
            body = parts[2].strip()

            # Extract content (remove title section)
            # Remove first H1 (title) - handle both \n\n and single \n
            body = re.sub(r'^#\s+.*?\n+', '', body, count=1)

            # Remove ALL metadata footers (there may be multiple from previous cycles)
            # Keep removing until no more matches found (handles interleaved footers)
            while re.search(r'\n+---\s*\n+\*KB Entry:.*?\*', body, flags=re.DOTALL):
                body = re.sub(r'\n+---\s*\n+\*KB Entry:.*?\*\s*', '', body, flags=re.DOTALL)

            # Clean up any trailing --- separators
            body = re.sub(r'\n+---\s*$', '', body)

            # Prepare data
            entry_id = frontmatter['id']
            category = frontmatter.get('category', 'other')
            title = frontmatter['title']
            tags = frontmatter.get('tags', [])
            metadata = json.dumps(frontmatter.get('metadata')) if frontmatter.get('metadata') else None
            created = frontmatter.get('created')
            updated = frontmatter.get('updated')

            # Check if entry exists (for counting purposes)
            existing = con.execute("SELECT id FROM knowledge WHERE id = ?", [entry_id]).fetchone()

            # Always UPSERT (insert if new, update if exists)
            # This is a restore operation - always overwrite
            if existing:
                con.execute("""
                    UPDATE knowledge
                    SET category = ?, title = ?, content = ?, tags = ?, metadata = ?, updated = ?
                    WHERE id = ?
                """, [category, title, body.strip(), tags, metadata, updated, entry_id])
                updated_count += 1
            else:
                con.execute("""
                    INSERT INTO knowledge (id, category, title, content, tags, metadata, created, updated, embedding)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL)
                """, [entry_id, category, title, body.strip(), tags, metadata, created, updated])
                imported_count += 1

        except Exception as e:
            return [TextContent(type="text", text=f"Error processing {md_file.name}: {str(e)}")]

    # Generate embeddings if requested
    embeddings_generated = 0
    if generate_embeddings_flag and (imported_count > 0 or updated_count > 0):
        # Get entries without embeddings
        no_embed = con.execute("SELECT id, title, tags, content FROM knowledge WHERE embedding IS NULL").fetchall()

        for entry_id, title, tags, content in no_embed:
            if content:
                try:
                    # Create rich embedding text (same as upsert_knowledge)
                    embed_text = f"Title: {title}\nTags: {', '.join(tags)}\nContent: {content}"
                    embedding = generate_embedding(embed_text)
                    # Cast to FLOAT array for DuckDB compatibility
                    embedding = [float(x) for x in embedding]
                    con.execute("UPDATE knowledge SET embedding = ? WHERE id = ?", [embedding, entry_id])
                    embeddings_generated += 1
                except Exception as e:
                    # Continue on error, don't fail entire import
                    pass  # Failed to generate embedding
                    pass

    summary = f"✓ Restore complete!\n\n"
    summary += f"New entries: {imported_count}\n"
    summary += f"Updated entries: {updated_count}\n"
    if skipped_count > 0:
        summary += f"Skipped: {skipped_count} files (invalid/malformed)\n"
    if generate_embeddings_flag:
        summary += f"Embeddings generated: {embeddings_generated}\n"
    summary += f"\nRestored from: {input_dir}"

    return [TextContent(type="text", text=summary)]


# =============================================================================
# Tool 12: Initialize Database
# =============================================================================

async def tool_initialize_database(arguments: dict) -> list[TextContent]:
    """Initialize or reinitialize the database with schema"""
    force = arguments.get("force", False)

    # Check if database already exists
    db_path_obj = Path(DB_PATH)
    if db_path_obj.exists() and not force:
        return [TextContent(type="text", text=json.dumps({
            "success": False,
            "error": "Database already exists. Use force=True to reinitialize."
        }))]

    try:
        # Create fresh connection (will create file if doesn't exist)
        con = duckdb.connect(str(DB_PATH))

        # 1. Install and load VSS extension
        has_vss = False
        try:
            con.execute("INSTALL vss")
            con.execute("LOAD vss")
            has_vss = True
        except Exception as e:
            # VSS not available, continue without it
            pass

        # 2. Execute schema.sql
        schema_path = Path(__file__).parent / 'schema.sql'
        if not schema_path.exists():
            con.close()
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": f"schema.sql not found at {schema_path}"
            }))]

        with open(schema_path) as f:
            schema_sql = f.read()

        try:
            con.execute(schema_sql)
        except Exception as e:
            # Ignore "already exists" errors during force reinit
            if 'already exists' not in str(e).lower():
                con.close()
                return [TextContent(type="text", text=json.dumps({
                    "success": False,
                    "error": f"Failed to execute schema: {str(e)}"
                }))]

        # 3. Validate - check that knowledge table exists
        tables = con.execute("SHOW TABLES").fetchall()
        table_names = [t[0] for t in tables]

        if 'knowledge' not in table_names:
            con.close()
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "Validation failed: knowledge table not created"
            }))]

        # Get stats
        try:
            stats_result = con.execute("SELECT * FROM database_summary()").fetchall()
            stats = {metric: value for metric, value in stats_result}
        except:
            stats = {}

        con.close()

        return [TextContent(type="text", text=json.dumps({
            "success": True,
            "message": "Database initialized successfully",
            "vss_available": has_vss,
            "stats": stats
        }))]

    except Exception as e:
        return [TextContent(type="text", text=json.dumps({
            "success": False,
            "error": f"Initialization failed: {str(e)}"
        }))]


# =============================================================================
# Tool 13: Git Commit and Get SHA
# =============================================================================

async def tool_git_commit_and_get_sha(arguments: dict) -> list[TextContent]:
    """Perform git add, commit, and return SHA"""
    import subprocess

    message = arguments.get("message")
    if not message:
        return [TextContent(type="text", text=json.dumps({
            "success": False,
            "error": "message parameter is required"
        }))]

    repo_path = Path(__file__).parent

    try:
        # Git add all changes
        subprocess.run(
            ["git", "add", "-A"],
            cwd=repo_path,
            check=True,
            capture_output=True,
            text=True
        )

        # Git commit with message
        subprocess.run(
            ["git", "commit", "-m", message],
            cwd=repo_path,
            check=True,
            capture_output=True,
            text=True
        )

        # Get commit SHA
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_path,
            check=True,
            capture_output=True,
            text=True
        )

        sha = result.stdout.strip()

        return [TextContent(type="text", text=json.dumps({
            "success": True,
            "sha": sha
        }))]

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else str(e)
        return [TextContent(type="text", text=json.dumps({
            "success": False,
            "error": error_msg
        }))]


# =============================================================================
# Tool 14: Get KB Session Status
# =============================================================================

async def tool_get_kb_session_status(arguments: dict) -> list[TextContent]:
    """Get KB initialization status, parse USER.md, check deadlines"""
    import re
    from datetime import datetime, timedelta

    project_dir = Path(__file__).parent
    db_path = project_dir / "kb.duckdb"
    kb_md_path = project_dir / ".claude" / "USER.md"
    markdown_dir = project_dir / "markdown"

    result = {
        "database": {},
        "kb_md": {},
        "status": {
            "focus_areas": [],
            "commitments": {
                "all": [],
                "approaching": [],
                "overdue": []
            }
        },
        "timestamp": datetime.now().isoformat()
    }

    # Check database status
    if not db_path.exists():
        # Check if markdown exports exist for recovery
        has_markdown = False
        if markdown_dir.exists():
            for item in markdown_dir.iterdir():
                if item.is_dir() and list(item.glob("*.md")):
                    has_markdown = True
                    break

        if has_markdown:
            result["database"] = {
                "exists": False,
                "action": "init_db_restore",
                "needs_import": True,
                "import_path": str(markdown_dir),
                "message": "Database not found - restoring from markdown exports"
            }
        else:
            result["database"] = {
                "exists": False,
                "action": "init_db_fresh",
                "needs_import": False,
                "message": "First run detected - initializing empty database"
            }
    else:
        # Database file exists - verify schema is initialized
        schema_valid = False
        try:
            test_con = duckdb.connect(str(db_path), read_only=True)
            # Check if knowledge table exists
            test_con.execute("SELECT COUNT(*) FROM knowledge LIMIT 1")
            schema_valid = True
            test_con.close()
        except Exception:
            # Schema doesn't exist or is corrupted
            schema_valid = False

        if schema_valid:
            result["database"] = {
                "exists": True,
                "action": "check_empty",
                "message": "Database found - checking contents"
            }
        else:
            # Database file exists but schema invalid - treat as fresh install
            result["database"] = {
                "exists": True,
                "action": "init_db_fresh",
                "needs_import": False,
                "message": "Database file found but schema invalid - reinitializing"
            }

    # Check USER.md status
    if not kb_md_path.exists():
        result["kb_md"] = {
            "is_template": True,
            "action": "create_from_template",
            "message": "USER.md not found - needs creation"
        }
    else:
        content = kb_md_path.read_text()

        # Check for template patterns
        template_patterns = [
            r"\[Your Name\]",
            r"\[Your job title/role\]",
            r"\*\*⚠️ TEMPLATE FILE",
            r"Replace all bracketed placeholders"
        ]

        is_template = any(re.search(pattern, content) for pattern in template_patterns)

        result["kb_md"] = {
            "is_template": is_template,
            "action": "setup_kb_md" if is_template else "ready",
            "message": "USER.md needs initial setup" if is_template else "USER.md ready"
        }

        # Parse Current Focus if not template
        if not is_template:
            focus_match = re.search(
                r'## Current Focus[^\n]*\n+(.*?)(?=\n## |\Z)',
                content,
                re.DOTALL
            )

            if focus_match:
                focus_section = focus_match.group(1)
                for match in re.finditer(
                    r'###\s+(\d+)\.\s+(.+?)\s+\(.*?priority:\s*(\w+)',
                    focus_section,
                    re.IGNORECASE
                ):
                    number = int(match.group(1))
                    name = match.group(2).strip()
                    priority = match.group(3).strip().upper()

                    # Extract status
                    status_match = re.search(
                        rf'###\s+{number}\..*?status:\s*([^\)]+)',
                        focus_section,
                        re.IGNORECASE | re.DOTALL
                    )
                    status = status_match.group(1).strip() if status_match else "unknown"

                    result["status"]["focus_areas"].append({
                        "number": number,
                        "name": name,
                        "priority": priority,
                        "status": status
                    })

            # Parse Open Commitments
            commits_match = re.search(
                r'## Open Commitments[^\n]*\n+(.*?)(?=\n## |\Z)',
                content,
                re.DOTALL
            )

            if commits_match:
                commits_section = commits_match.group(1)
                today = datetime.now()

                for match in re.finditer(
                    r'-\s+\[([ x])\]\s+(.+?)\s+\(due:\s*(\d{4}-\d{2}-\d{2})\)',
                    commits_section
                ):
                    completed = match.group(1) == 'x'
                    description = match.group(2).strip()
                    due_date_str = match.group(3)

                    try:
                        due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
                        days_until = (due_date - today).days

                        if not completed:
                            commitment = {
                                "description": description,
                                "due_date": due_date_str,
                                "days_until": days_until,
                                "approaching": days_until <= 7 and days_until >= 0,
                                "overdue": days_until < 0
                            }

                            result["status"]["commitments"]["all"].append(commitment)

                            if commitment["approaching"]:
                                result["status"]["commitments"]["approaching"].append(commitment)
                            if commitment["overdue"]:
                                result["status"]["commitments"]["overdue"].append(commitment)
                    except ValueError:
                        continue

    return [TextContent(type="text", text=json.dumps(result, indent=2))]


# =============================================================================
# Tool 15: Check Token Budgets
# =============================================================================

async def tool_check_token_budgets(arguments: dict) -> list[TextContent]:
    """Check USER.md and ARLO.md token budgets against 10K limit"""

    # Try to import tiktoken, fall back to word-count approximation
    try:
        import tiktoken
        enc = tiktoken.encoding_for_model("gpt-4")
        has_tiktoken = True
    except ImportError:
        has_tiktoken = False

    def count_tokens(filepath: Path) -> tuple[int, str]:
        """Count tokens in file using tiktoken or word-count fallback"""
        with open(filepath, "r") as f:
            content = f.read()

        if has_tiktoken:
            tokens = len(enc.encode(content))
            method = "tiktoken"
        else:
            # Fallback: tokens ≈ words × 1.3 (empirically validated for English)
            words = len(content.split())
            tokens = int(words * 1.3)
            method = "word-count approximation"

        return tokens, method

    # Parse arguments
    files_arg = arguments.get("files")
    budget = arguments.get("budget", 10000)
    warning_threshold = arguments.get("warning_threshold", 9000)

    # Default files if none specified
    if not files_arg:
        project_dir = Path(__file__).parent
        files_arg = [
            str(project_dir / ".claude" / "USER.md"),
            str(project_dir / ".claude" / "ARLO.md")
        ]

    results = []
    all_ok = True

    for filepath_str in files_arg:
        filepath = Path(filepath_str)

        # Skip if file doesn't exist
        if not filepath.exists():
            continue

        tokens, method = count_tokens(filepath)
        filename = filepath.name

        file_result = {
            "file": filename,
            "path": str(filepath),
            "tokens": tokens,
            "method": method,
            "budget": budget,
            "warning_threshold": warning_threshold,
            "headroom": budget - tokens
        }

        if tokens >= budget:
            file_result["status"] = "exceeded"
            file_result["severity"] = "error"
            if filename == "ARLO.md":
                file_result["action"] = "Apply compression immediately (see ARLO-BASE.md)"
            else:
                file_result["action"] = "Archive content to KB immediately"
            all_ok = False

        elif tokens >= warning_threshold:
            file_result["status"] = "warning"
            file_result["severity"] = "warning"
            if filename == "ARLO.md":
                file_result["action"] = "Compression required (see ARLO-BASE.md Compression Strategies)"
            else:
                file_result["action"] = "Archive old learnings/commitments to KB entries"

        else:
            file_result["status"] = "ok"
            file_result["severity"] = "info"
            file_result["action"] = None

        results.append(file_result)

    response = {
        "overall_status": "ok" if all_ok else "action_required",
        "files": results,
        "timestamp": datetime.now().isoformat()
    }

    return [TextContent(type="text", text=json.dumps(response, indent=2))]


# =============================================================================
# Main
# =============================================================================

async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
