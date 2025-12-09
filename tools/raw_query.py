"""Raw SQL query tool."""
from typing import List
import json
from mcp.types import Tool, TextContent

from .base import text_response

TOOL_DEF = Tool(
    name="raw_query",
    description="Raw SQL escape hatch for aggregations, stats, or complex joins. For normal retrieval use scan_knowledge -> get_knowledge. Table: knowledge (columns: id, category, title, tags, content, metadata, created, updated)",
    inputSchema={
        "type": "object",
        "properties": {
            "sql": {"type": "string", "description": "SQL query to execute (SELECT only)"}
        },
        "required": ["sql"]
    }
)

REQUIRES_DB = True


async def execute(con, args: dict) -> List[TextContent]:
    sql = args["sql"]

    if not sql.strip().upper().startswith("SELECT"):
        return text_response("Error: Only SELECT queries allowed")

    try:
        results = con.execute(sql).fetchall()
        cols = [desc[0] for desc in con.description]
        rows = [dict(zip(cols, row)) for row in results]
        return text_response(json.dumps(rows, default=str))
    except Exception as e:
        return text_response(f"SQL Error: {str(e)}")
