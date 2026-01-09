"""Scan knowledge entries tool."""
from typing import List
import json
from mcp.types import Tool, TextContent

from .base import text_response, log_kb_access

TOOL_DEF = Tool(
    name="scan_knowledge",
    description="Search KB using full-text search. Returns entries ranked by relevance with 400-char previews.",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query. Words are tokenized and matched against title and content. Pass your natural language query directly."},
            "where": {"type": "string", "description": "Optional SQL WHERE clause to filter results (e.g., \"category = 'pattern'\", \"'pds' = ANY(tags)\")."},
            "limit": {"type": "integer", "description": "Max entries to return. Default: 10.", "default": 10},
            "include_transcripts": {"type": "boolean", "description": "Include transcript entries in search. Default: false (transcripts excluded).", "default": False}
        },
        "required": ["query"]
    }
)

REQUIRES_DB = True


async def execute(con, args: dict) -> List[TextContent]:
    query = args.get("query", "").strip()
    if not query:
        return text_response("Error: query parameter required")

    where_clause = args.get("where", "").strip()
    limit = args.get("limit", 10)
    include_transcripts = args.get("include_transcripts", False)

    # Escape single quotes in query
    safe_query = query.replace("'", "''")

    # Build transcript exclusion clause
    transcript_filter = "" if include_transcripts else "AND category <> 'transcript'"

    # FTS query with optional WHERE filter
    if where_clause:
        sql = f"""
            WITH fts_results AS (
                SELECT *, fts_main_knowledge.match_bm25(id, '{safe_query}') AS score
                FROM knowledge
                WHERE score IS NOT NULL {transcript_filter}
            )
            SELECT id, title, category, tags, LEFT(content, 400) as preview, updated, score
            FROM fts_results
            WHERE {where_clause}
            ORDER BY score DESC
            LIMIT {limit}
        """
    else:
        sql = f"""
            SELECT id, title, category, tags, LEFT(content, 400) as preview, updated,
                   fts_main_knowledge.match_bm25(id, '{safe_query}') AS score
            FROM knowledge
            WHERE score IS NOT NULL {transcript_filter}
            ORDER BY score DESC
            LIMIT {limit}
        """

    try:
        results = con.execute(sql).fetchall()
        cols = ["id", "title", "category", "tags", "preview", "updated", "score"]
        rows = [dict(zip(cols, row)) for row in results]

        # Log KB access
        result_ids = [row["id"] for row in rows]
        log_kb_access(con, "scan", result_ids)

        return text_response(json.dumps(rows, default=str))
    except Exception as e:
        return text_response(f"FTS Error: {str(e)}")
