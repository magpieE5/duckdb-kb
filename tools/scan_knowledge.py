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
            "limit": {"type": "integer", "description": "Max entries to return. Omit for all."}
        },
        "required": []
    }
)

REQUIRES_DB = True


async def execute(con, args: dict) -> List[TextContent]:
    where_clause = args.get("where", "1=1").strip()
    if not where_clause:
        where_clause = "1=1"

    limit = args.get("limit")
    limit_clause = f"LIMIT {limit}" if limit else ""

    sql = f"""
        SELECT id, title, category, tags, LEFT(content, 400) as preview, updated
        FROM knowledge
        WHERE {where_clause}
        ORDER BY updated DESC
        {limit_clause}
    """

    try:
        results = con.execute(sql).fetchall()
        cols = ["id", "title", "category", "tags", "preview", "updated"]
        rows = [dict(zip(cols, row)) for row in results]
        return text_response(json.dumps(rows, default=str))
    except Exception as e:
        return text_response(f"SQL Error: {str(e)}")
