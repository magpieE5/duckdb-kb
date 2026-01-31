"""Get full knowledge entries tool."""
from typing import List
import json
from mcp.types import Tool, TextContent

from .base import text_response, log_kb_access

TOOL_DEF = Tool(
    name="get_knowledge",
    description="Retrieve full KB entries. Use after scan_knowledge, or directly when you know the entry ID/category.",
    inputSchema={
        "type": "object",
        "properties": {
            "where": {"type": "string", "description": "SQL WHERE clause (e.g., \"id = 'pattern-pds-architecture'\", \"category = 'reference' AND 'brock' = ANY(tags)\")"}
        },
        "required": ["where"]
    }
)

REQUIRES_DB = True


async def execute(con, args: dict) -> List[TextContent]:
    where_clause = args.get("where", "").strip()
    if not where_clause:
        return text_response("Error: WHERE clause required for get_knowledge")

    sql = f"""
        SELECT id, title, category, tags, content, metadata, created, updated
        FROM knowledge
        WHERE {where_clause}
        ORDER BY updated DESC
    """

    try:
        results = con.execute(sql).fetchall()
        cols = ["id", "title", "category", "tags", "content", "metadata", "created", "updated"]
        rows = [dict(zip(cols, row)) for row in results]

        # Log KB access
        result_ids = [row["id"] for row in rows]
        log_kb_access(con, "get", result_ids)

        return text_response(json.dumps(rows, default=str))
    except Exception as e:
        return text_response(f"SQL Error: {str(e)}")
