#!/usr/bin/env python3
"""
DuckDB Knowledge Base MCP Server

Provides 10 tools for Claude Code to interact with knowledge base:
- CRUD: upsert_knowledge, delete_knowledge, add_link
- Read: get_knowledge, list_knowledge, query_knowledge
- Search: find_similar, smart_search
- Utility: get_stats, generate_embeddings
"""

import json
import os
from pathlib import Path
from typing import Any, Optional, List, Dict
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

DB_PATH = os.getenv('KNOWLEDGE_DB_PATH', 'knowledge.duckdb')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
EMBEDDING_PROVIDER = os.getenv('EMBEDDING_PROVIDER', 'openai')  # 'openai' or 'local'
EMBEDDING_MODEL = 'text-embedding-3-large'  # OpenAI model (best quality)
EMBEDDING_DIM = 3072  # OpenAI text-embedding-3-large dimensions

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
            print(f"OpenAI embedding failed: {e}, falling back to local")
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
            print(f"OpenAI batch embedding failed: {e}, falling back to local")
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


def ensure_schema_initialized(con):
    """
    Auto-initialize database schema if it doesn't exist.
    This ensures new users don't have to manually run setup scripts.
    """
    try:
        # Quick check: does knowledge table exist?
        con.execute("SELECT 1 FROM knowledge LIMIT 1")
        # Schema exists, we're good
        return
    except:
        # Schema doesn't exist, need to initialize
        pass

    print("⚙️  Initializing database schema (first-time setup)...", flush=True)

    try:
        # Get paths to SQL files
        script_dir = Path(__file__).parent
        schema_path = script_dir / 'schema.sql'
        functions_path = script_dir / 'add_functions.sql'

        if not schema_path.exists() or not functions_path.exists():
            print(f"❌ Error: Schema files not found in {script_dir}", flush=True)
            print("   Please run: python scripts/init_db.py", flush=True)
            return

        # Install VSS extension first
        try:
            con.execute("INSTALL vss")
            con.execute("LOAD vss")
        except:
            pass  # VSS optional

        # Read schema and skip problematic MACRO definitions
        with open(schema_path) as f:
            schema_sql = f.read()

        # Execute schema line by line, skipping MACRO definitions
        lines = []
        in_macro = False
        paren_depth = 0

        for line in schema_sql.split('\n'):
            stripped = line.strip()

            if stripped.startswith('--') or not stripped:
                continue

            # Skip upsert_knowledge MACRO (has MERGE issues)
            if 'CREATE MACRO' in line and 'upsert_knowledge' in line:
                in_macro = True
                continue

            if in_macro:
                if '(' in line:
                    paren_depth += line.count('(')
                if ')' in line:
                    paren_depth -= line.count(')')
                if paren_depth == 0 and ');' in line:
                    in_macro = False
                continue

            lines.append(line)

        # Execute schema statements
        statements = '\n'.join(lines).split(';')
        for stmt in statements:
            stmt = stmt.strip()
            if stmt and not stmt.startswith('--'):
                try:
                    con.execute(stmt + ';')
                except Exception as e:
                    if 'already exists' not in str(e):
                        # Ignore "already exists" errors
                        pass

        # Execute functions SQL
        with open(functions_path) as f:
            functions_sql = f.read()

        # Execute function statements
        for stmt in functions_sql.split(';'):
            stmt = stmt.strip()
            if stmt and not stmt.startswith('--') and not stmt.upper().startswith('SELECT'):
                try:
                    con.execute(stmt + ';')
                except Exception as e:
                    if 'already exists' not in str(e):
                        pass

        print("✅ Database schema initialized successfully!", flush=True)

    except Exception as e:
        print(f"⚠️  Warning: Could not auto-initialize schema: {e}", flush=True)
        print("   Please run manually: python scripts/init_db.py", flush=True)


def get_connection():
    """Get DuckDB connection with VSS extension loaded"""
    con = duckdb.connect(DB_PATH)

    # Auto-initialize schema if needed (first-time setup)
    ensure_schema_initialized(con)

    # Load VSS extension
    try:
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
            description="""Find knowledge entries semantically similar to a query using embeddings. Searches by meaning/concept, not just keywords. Use to identify duplicate or related entries (set similarity_threshold=0.8+ for near-duplicates). Helpful for defragmentation and consolidation efforts.

WHEN TO USE: Conceptual/semantic search, finding related content, checking for duplicates.
BEST FOR: "Find entries about error handling" or "What's similar to this concept?"
NOT FOR: Exact keyword matching (use query_knowledge with LIKE) or browsing (use list_knowledge)
THRESHOLDS: 0.9+=duplicates, 0.7-0.9=related, 0.6-0.7=loosely related, <0.6=unrelated
TIP: Start with threshold=0.7, adjust based on results. Lower=more results, higher=more precise.""",
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
                        "description": "Minimum cosine similarity (0-1, default: 0.6)",
                        "default": 0.6
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
                        "description": "Minimum similarity score (default: 0.6)",
                        "default": 0.6
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
            description="""Create a new knowledge entry or update existing one. Automatically generates embedding if content is provided. BEFORE creating: search for similar content to avoid duplicates - consider updating existing entries instead. Use descriptive IDs (e.g., 'pattern-error-handling'), consistent tags, and clear markdown structure (Problem/Solution/Context/Example) for maintainability.

WHEN TO USE: Saving valuable knowledge, fixing/updating entries, consolidating duplicates.
WORKFLOW: 1) smart_search() for duplicates, 2) if none found, create new entry, 3) if found, update existing
ID FORMAT: Use kebab-case like 'pattern-topic-specifics' or 'troubleshooting-issue-name'
TAGS: Include 4-6 relevant tags + layer tag (layer:base, layer:team, or layer:personal)
**CRITICAL**: Always check for duplicates first to avoid fragmentation!""",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "Unique identifier (e.g., 'pattern-caching', 'troubleshooting-performance')"
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
TIP: Use add_link() to mark entries as "superseded_by" before deleting.""",
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
        # Tool 8: Add Link
        # =============================================================================

        Tool(
            name="add_link",
            description="""Create a relationship link between two knowledge entries (e.g., 'issue references table').

WHEN TO USE: Connecting related entries to build knowledge graph, showing relationships.
LINK TYPES: 'related' (general), 'references' (points to), 'parent' (broader topic), 'child' (subtopic)
EXAMPLE: add_link({"from_id": "issue-123", "to_id": "pattern-fix", "link_type": "references"})
TIP: Use get_knowledge() with include_related=true to see all links.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_id": {
                        "type": "string",
                        "description": "Source entry ID"
                    },
                    "to_id": {
                        "type": "string",
                        "description": "Target entry ID"
                    },
                    "link_type": {
                        "type": "string",
                        "description": "Type of relationship: related, parent, child, references (default: related)",
                        "default": "related"
                    }
                },
                "required": ["from_id", "to_id"]
            }
        ),

        # =============================================================================
        # Tool 9: Get Stats
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
        # Tool 10: Generate Embeddings (Batch utility)
        # =============================================================================

        Tool(
            name="generate_embeddings",
            description="""Generate embeddings for entries that don't have them yet. Uses OpenAI text-embedding-3-small (1536 dimensions) by default. Falls back to local model if OpenAI unavailable. Requires network connectivity.

WHEN TO USE: After bulk imports, when entries missing embeddings, after restoring from backup.
COST: ~$0.00002 per 1K tokens (~$0.001 for 100 entries)
CHECK FIRST: Use get_stats() to see how many entries need embeddings
TIP: Set regenerate=false (default) to only generate missing embeddings, not replace existing.""",
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
    ]


# =============================================================================
# Tool Implementations
# =============================================================================

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""

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
        elif name == "add_link":
            return await tool_add_link(con, arguments)
        elif name == "get_stats":
            return await tool_get_stats(con, arguments)
        elif name == "generate_embeddings":
            return await tool_generate_embeddings(con, arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    finally:
        con.close()


# Tool: Get Knowledge
async def tool_get_knowledge(con: duckdb.DuckDBPyConnection, args: dict) -> list[TextContent]:
    entry_id = args["id"]
    include_related = args.get("include_related", False)

    if include_related:
        result = con.execute("SELECT * FROM get_with_related(?)", [entry_id]).fetchone()
    else:
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

    return [TextContent(type="text", text=json.dumps(entry, indent=2, default=str))]


# Tool: List Knowledge
async def tool_list_knowledge(con: duckdb.DuckDBPyConnection, args: dict) -> list[TextContent]:
    category = args.get("category")
    tags = args.get("tags")
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
               left(content, 200) as content_preview,
               metadata, created, updated
        FROM knowledge
        WHERE {where_sql}
        ORDER BY updated DESC
        LIMIT ? OFFSET ?
    """

    params.extend([limit, offset])

    results = con.execute(sql, params).fetchall()
    cols = [desc[0] for desc in con.description]

    entries = [dict(zip(cols, row)) for row in results]

    return [TextContent(type="text", text=json.dumps({
        "count": len(entries),
        "entries": entries
    }, indent=2, default=str))]


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

        return [TextContent(type="text", text=json.dumps({
            "count": len(rows),
            "results": rows
        }, indent=2, default=str))]

    except Exception as e:
        return [TextContent(type="text", text=f"SQL Error: {str(e)}")]


# Tool: Find Similar (Semantic search)
async def tool_find_similar(con: duckdb.DuckDBPyConnection, args: dict) -> list[TextContent]:
    query = args["query"]
    category = args.get("category")
    threshold = args.get("similarity_threshold", 0.6)
    limit = args.get("limit", 10)

    # Generate query embedding
    try:
        query_embedding = generate_embedding(query)
        # Cast to FLOAT array for DuckDB compatibility
        query_embedding = [float(x) for x in query_embedding]
    except Exception as e:
        return [TextContent(type="text", text=f"Error generating embedding: {str(e)}\nInstall: pip install sentence-transformers")]

    # Search - use CAST to ensure type compatibility
    if category:
        sql = "SELECT * FROM semantic_search(CAST(? AS FLOAT[1536]), ?, ?, ?)"
        params = [query_embedding, threshold, category, limit]
    else:
        sql = "SELECT * FROM semantic_search(CAST(? AS FLOAT[1536]), ?, NULL, ?)"
        params = [query_embedding, threshold, limit]

    results = con.execute(sql, params).fetchall()
    cols = [desc[0] for desc in con.description]

    entries = []
    for row in results:
        entry = dict(zip(cols, row))
        # Truncate content for readability
        if 'content' in entry and len(entry['content']) > 300:
            entry['content_preview'] = entry['content'][:300] + "..."
            del entry['content']
        if 'embedding' in entry:
            del entry['embedding']
        entries.append(entry)

    return [TextContent(type="text", text=json.dumps({
        "query": query,
        "count": len(entries),
        "results": entries
    }, indent=2, default=str))]


# Tool: Smart Search (Hybrid)
async def tool_smart_search(con: duckdb.DuckDBPyConnection, args: dict) -> list[TextContent]:
    query = args["query"]
    category = args.get("category")
    tags = args.get("tags")
    date_after = args.get("date_after")
    threshold = args.get("similarity_threshold", 0.6)
    limit = args.get("limit", 10)

    # Generate query embedding
    try:
        query_embedding = generate_embedding(query)
        # Cast to FLOAT array for DuckDB compatibility
        query_embedding = [float(x) for x in query_embedding]
    except Exception as e:
        return [TextContent(type="text", text=f"Error generating embedding: {str(e)}")]

    # Call hybrid search macro - use CAST to ensure type compatibility
    sql = "SELECT * FROM hybrid_search(CAST(? AS FLOAT[1536]), ?, ?, ?, ?, ?)"
    params = [query_embedding, category, tags, date_after, threshold, limit]

    results = con.execute(sql, params).fetchall()
    cols = [desc[0] for desc in con.description]

    entries = []
    for row in results:
        entry = dict(zip(cols, row))
        if 'content' in entry and len(entry['content']) > 300:
            entry['content_preview'] = entry['content'][:300] + "..."
            del entry['content']
        if 'embedding' in entry:
            del entry['embedding']
        entries.append(entry)

    return [TextContent(type="text", text=json.dumps({
        "query": query,
        "filters": {
            "category": category,
            "tags": tags,
            "date_after": date_after
        },
        "count": len(entries),
        "results": entries
    }, indent=2, default=str))]


# Tool: Upsert Knowledge
async def tool_upsert_knowledge(con: duckdb.DuckDBPyConnection, args: dict) -> list[TextContent]:
    entry_id = args["id"]
    category = args["category"]
    title = args["title"]
    content = args["content"]
    tags = args.get("tags", [])
    metadata = args.get("metadata", {})
    generate_emb = args.get("generate_embedding", True)

    # Generate embedding if requested
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
        "status": "success",
        "id": entry_id,
        "operation": "upsert",
        "embedding_generated": embedding is not None
    }, indent=2))]


# Tool: Delete Knowledge
async def tool_delete_knowledge(con: duckdb.DuckDBPyConnection, args: dict) -> list[TextContent]:
    entry_id = args["id"]

    # Check if exists
    exists = con.execute("SELECT 1 FROM knowledge WHERE id = ?", [entry_id]).fetchone()
    if not exists:
        return [TextContent(type="text", text=f"Entry not found: {entry_id}")]

    # Delete (cascades to links)
    con.execute("DELETE FROM knowledge WHERE id = ?", [entry_id])
    con.execute("DELETE FROM knowledge_links WHERE from_id = ? OR to_id = ?", [entry_id, entry_id])

    return [TextContent(type="text", text=json.dumps({
        "status": "success",
        "id": entry_id,
        "operation": "delete"
    }, indent=2))]


# Tool: Add Link
async def tool_add_link(con: duckdb.DuckDBPyConnection, args: dict) -> list[TextContent]:
    from_id = args["from_id"]
    to_id = args["to_id"]
    link_type = args.get("link_type", "related")

    # Verify both entries exist
    from_exists = con.execute("SELECT 1 FROM knowledge WHERE id = ?", [from_id]).fetchone()
    to_exists = con.execute("SELECT 1 FROM knowledge WHERE id = ?", [to_id]).fetchone()

    if not from_exists:
        return [TextContent(type="text", text=f"Source entry not found: {from_id}")]
    if not to_exists:
        return [TextContent(type="text", text=f"Target entry not found: {to_id}")]

    # Insert link
    con.execute("""
        INSERT INTO knowledge_links (from_id, to_id, link_type)
        VALUES (?, ?, ?)
        ON CONFLICT DO NOTHING
    """, [from_id, to_id, link_type])

    return [TextContent(type="text", text=json.dumps({
        "status": "success",
        "from": from_id,
        "to": to_id,
        "link_type": link_type
    }, indent=2))]


# Tool: Get Stats
async def tool_get_stats(con: duckdb.DuckDBPyConnection, args: dict) -> list[TextContent]:
    detailed = args.get("detailed", False)

    # Basic summary
    summary = con.execute("SELECT * FROM database_summary()").fetchall()

    stats = {
        "summary": {row[0]: row[1] for row in summary}
    }

    if detailed:
        # Category breakdown
        categories = con.execute("SELECT * FROM knowledge_stats").fetchall()
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

        # Tag usage
        tags = con.execute("SELECT * FROM tag_usage LIMIT 20").fetchall()
        stats["top_tags"] = [
            {"tag": row[0], "count": row[1], "categories": row[2]}
            for row in tags
        ]

    return [TextContent(type="text", text=json.dumps(stats, indent=2, default=str))]


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
    }, indent=2))]


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
