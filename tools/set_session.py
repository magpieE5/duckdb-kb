"""Set current session number for KB access logging."""
from typing import List
from mcp.types import Tool, TextContent

from .base import set_current_session, json_response

TOOL_DEF = Tool(
    name="set_session",
    description="Set the current session number. Call at session open to enable KB access logging.",
    inputSchema={
        "type": "object",
        "properties": {
            "session": {"type": "integer", "description": "Session number (e.g., 153)"}
        },
        "required": ["session"]
    }
)

REQUIRES_DB = False


async def execute(con, args: dict) -> List[TextContent]:
    session = args.get("session")
    if session is None:
        return json_response({"status": "error", "message": "session parameter required"})

    set_current_session(session)
    return json_response({"status": "ok", "session": session})
