"""Hybrid search combining SQL filters with semantic similarity"""

from mcp.types import Tool, TextContent
from typing import List, Optional, Dict
import json
from tools.base import generate_embedding, DEFAULT_SIMILARITY_THRESHOLD, normalize_tags

# =============================================================================
# Tool Definition (for registration)
# =============================================================================

TOOL = Tool(
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
)

# =============================================================================
# Helper Functions
# =============================================================================

def search_logs_python(con, query_embedding: List[float], threshold: float) -> List[Dict]:
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


def search_exact_python(con, query_text: str,
                       category: Optional[str], tags: Optional[List[str]],
                       date_after: Optional[str]) -> List[Dict]:
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


def search_semantic_python(con, query_embedding: List[float],
                          category: Optional[str], tags: Optional[List[str]],
                          date_after: Optional[str], threshold: float) -> List[Dict]:
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


def merge_results(exact_matches: List[Dict], semantic_matches: List[Dict], limit: int) -> List[Dict]:
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

# =============================================================================
# Implementation
# =============================================================================

async def execute(con, args: dict) -> List[TextContent]:
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
        tags = normalize_tags(tags)
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

# =============================================================================
# Metadata
# =============================================================================

REQUIRES_DB = True
