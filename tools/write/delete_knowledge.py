"""Delete knowledge entries by ID"""

from mcp.types import Tool, TextContent
from typing import List
import json

# =============================================================================
# Tool Definition (for registration)
# =============================================================================

TOOL = Tool(
    name="delete_knowledge",
    description="""Delete a knowledge entry by ID. This also removes all links to/from this entry. Use for: obsolete entries, duplicates after consolidation, one-off solutions that didn't generalize, or entries superseded by better versions. Consider consolidating multiple related entries instead of just deleting.

WHEN TO USE: Removing obsolete/duplicate entries AFTER consolidating their useful content elsewhere.
CAUTION: Deletion is permanent! Consider updating with deprecation notice instead.
WORKFLOW: 1) Review entry, 2) Extract any valuable content, 3) Consolidate into other entries, 4) Then delete
CAUTION: Deletion is permanent!""",
    inputSchema={
        "type": "object",
        "properties": {
            "id": {
                "type": "string",
                "description": "ID of entry to delete"
            }
        },
        "required": ["id"]
    }
)

# =============================================================================
# Implementation
# =============================================================================

async def execute(con, args: dict) -> List[TextContent]:
    """Delete a knowledge entry by ID"""
    entry_id = args["id"]

    # Check if exists
    exists = con.execute("SELECT 1 FROM knowledge WHERE id = ?", [entry_id]).fetchone()
    if not exists:
        return [TextContent(type="text", text=f"Entry not found: {entry_id}")]

    # Delete entry
    con.execute("DELETE FROM knowledge WHERE id = ?", [entry_id])

    return [TextContent(type="text", text=json.dumps({
        "id": entry_id
    }))]

# =============================================================================
# Metadata
# =============================================================================

REQUIRES_DB = True
