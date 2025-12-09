"""Scan knowledge entries tool."""
from typing import List
import json
from mcp.types import Tool, TextContent

from .base import text_response

TOOL_DEF = Tool(
    name="scan_knowledge",
    description="Browse KB entries with 400-char previews. Use to find entries, then get_knowledge for full content.",
    inputSchema={
        "type": "object",
        "properties": {
            "where": {"type": "string", "description": "SQL WHERE clause (e.g., \"category = 'pattern'\", \"'pds' = ANY(tags)\", \"title ILIKE '%banner%'\"). Omit for all entries."},
            "search": {"type": "string", "description": "Text search term. Searches preview (first 400 chars) and title. More precise than full content search."},
            "limit": {"type": "integer", "description": "Max entries to return. Omit for all."},
            "order": {"type": "string", "description": "Sort order: 'asc' or 'desc' by updated timestamp. Default: desc."}
        },
        "required": []
    }
)

REQUIRES_DB = True


async def execute(con, args: dict) -> List[TextContent]:
    where_clause = args.get("where", "1=1").strip()
    if not where_clause:
        where_clause = "1=1"

    # Handle search parameter - searches preview (first 400 chars) and title
    search = args.get("search", "").strip()
    if search:
        # Escape single quotes in search term
        safe_search = search.replace("'", "''")
        search_clause = f"(LEFT(content, 400) ILIKE '%{safe_search}%' OR title ILIKE '%{safe_search}%')"
        if where_clause == "1=1":
            where_clause = search_clause
        else:
            where_clause = f"({where_clause}) AND {search_clause}"

    limit = args.get("limit")
    limit_clause = f"LIMIT {limit}" if limit else ""

    order = args.get("order", "desc").lower()
    order_dir = "ASC" if order == "asc" else "DESC"

    sql = f"""
        SELECT id, title, category, tags, LEFT(content, 400) as preview, updated
        FROM knowledge
        WHERE {where_clause}
        ORDER BY updated {order_dir}
        {limit_clause}
    """

    try:
        results = con.execute(sql).fetchall()
        cols = ["id", "title", "category", "tags", "preview", "updated"]
        rows = [dict(zip(cols, row)) for row in results]
        return text_response(json.dumps(rows, default=str))
    except Exception as e:
        return text_response(f"SQL Error: {str(e)}")
