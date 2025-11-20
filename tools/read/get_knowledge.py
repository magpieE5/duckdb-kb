"""Get a single knowledge entry by ID"""

from mcp.types import Tool, TextContent
from typing import List
import json

# =============================================================================
# Tool Definition (for registration)
# =============================================================================

TOOL = Tool(
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
)

# =============================================================================
# Implementation
# =============================================================================

async def execute(con, args: dict) -> List[TextContent]:
    """Get a single knowledge entry by ID"""
    entry_id = args["id"]

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

    return [TextContent(type="text", text=json.dumps(entry, default=str))]

# =============================================================================
# Metadata
# =============================================================================

REQUIRES_DB = True
