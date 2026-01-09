"""List KB entries."""
from typing import List
from mcp.types import Tool, TextContent

from .base import json_response

TOOL_DEF = Tool(
    name="list_knowledge",
    description="List all non-log KB entries (id and title).",
    inputSchema={
        "type": "object",
        "properties": {}
    }
)

REQUIRES_DB = True


async def execute(con, args: dict) -> List[TextContent]:
    entries = con.execute("""
        SELECT id, title
        FROM knowledge
        WHERE category != 'log'
        ORDER BY id
    """).fetchall()

    return json_response([{"id": row[0], "title": row[1]} for row in entries])
