"""Delete knowledge entry tool."""
from typing import List
from mcp.types import Tool, TextContent

from .base import json_response, log_kb_access

TOOL_DEF = Tool(
    name="delete_knowledge",
    description="Delete a KB entry by ID. Returns confirmation or error if entry not found.",
    inputSchema={
        "type": "object",
        "properties": {
            "id": {"type": "string", "description": "ID of the entry to delete"}
        },
        "required": ["id"]
    }
)

REQUIRES_DB = True


async def execute(con, args: dict) -> List[TextContent]:
    entry_id = args.get("id", "").strip()

    if not entry_id:
        return json_response({"status": "error", "message": "ID required"})

    existing = con.execute(
        "SELECT id, title, category FROM knowledge WHERE id = ?",
        [entry_id]
    ).fetchone()

    if not existing:
        return json_response({"status": "error", "message": f"Entry not found: {entry_id}"})

    con.execute("DELETE FROM knowledge WHERE id = ?", [entry_id])

    # Log delete for federation tracking
    log_kb_access(con, 'delete', [entry_id])

    return json_response({
        "status": "deleted",
        "id": existing[0],
        "title": existing[1],
        "category": existing[2]
    })
