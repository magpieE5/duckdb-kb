"""Remove item from a list entry (todo, accumulator, any list)."""
from typing import List
from datetime import datetime, timezone
from mcp.types import Tool, TextContent

from .base import json_response, error_response

TOOL_DEF = Tool(
    name="list_remove",
    description="""Remove an item from any list-type entry by matching text.

Works for accumulators or any entry using `- item` format.
Matches items containing the search string (case-insensitive).
Removes the first match found.""",
    inputSchema={
        "type": "object",
        "properties": {
            "id": {"type": "string", "description": "Entry ID (e.g., 'accumulator-corrections')"},
            "match": {"type": "string", "description": "Text to match in the item (case-insensitive substring)"}
        },
        "required": ["id", "match"]
    }
)

REQUIRES_DB = True


async def execute(con, args: dict) -> List[TextContent]:
    entry_id = args["id"]
    match_text = args["match"].lower()

    # Read existing entry
    existing = con.execute(
        "SELECT content FROM knowledge WHERE id = ?",
        [entry_id]
    ).fetchone()

    if not existing:
        return error_response("not_found", f"Entry '{entry_id}' not found.")

    content = existing[0]
    lines = content.split('\n')

    # Find and remove matching line
    removed_line = None
    new_lines = []
    for line in lines:
        if removed_line is None and line.strip().startswith('- ') and match_text in line.lower():
            removed_line = line.strip()
            # Skip this line (don't add to new_lines)
        else:
            new_lines.append(line)

    if removed_line is None:
        items = [line.strip() for line in lines if line.strip().startswith('- ')][:5]
        return error_response(
            "item_not_found",
            f"No item matching '{args['match']}'. Items: {items}"
        )

    # Write back
    new_content = '\n'.join(new_lines)
    now = datetime.now(timezone.utc)
    con.execute("""
        UPDATE knowledge SET content = ?, updated = ? WHERE id = ?
    """, [new_content, now, entry_id])

    # Count remaining items
    remaining = sum(1 for line in new_lines if line.strip().startswith('- '))

    return json_response({
        "id": entry_id,
        "status": "removed",
        "removed": removed_line,
        "remaining_items": remaining
    })
