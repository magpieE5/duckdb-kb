"""Append-only tool for accumulator entries (corrections, etc.)."""
from typing import List
from datetime import datetime
from mcp.types import Tool, TextContent

from .base import json_response

TOOL_DEF = Tool(
    name="append_accumulator",
    description="""Append content to an accumulator entry. NEVER overwrites - only appends.

Use this for entries where content should only grow:
- accumulator-corrections (error log)
- Any entry where losing history is unacceptable

Creates entry if it doesn't exist. Appends with separator if it does.""",
    inputSchema={
        "type": "object",
        "properties": {
            "id": {"type": "string", "description": "ID of accumulator entry (e.g., 'accumulator-corrections')"},
            "content": {"type": "string", "description": "New content to append"},
            "title": {"type": "string", "description": "Title for new entry (only used if creating)"},
            "separator": {"type": "string", "description": "Separator between entries (default: '\\n\\n')"}
        },
        "required": ["id", "content"]
    }
)

REQUIRES_DB = True


async def execute(con, args: dict) -> List[TextContent]:
    entry_id = args["id"]
    new_content = args["content"]
    separator = args.get("separator", "\n\n")
    title = args.get("title", entry_id.replace("-", " ").title())

    now = datetime.now()

    # Check if exists
    existing = con.execute(
        "SELECT content FROM knowledge WHERE id = ?",
        [entry_id]
    ).fetchone()

    if existing:
        # Append to existing
        old_content = existing[0]
        combined_content = old_content + separator + new_content

        con.execute("""
            UPDATE knowledge SET content = ?, updated = ? WHERE id = ?
        """, [combined_content, now, entry_id])

        return json_response({
            "id": entry_id,
            "status": "appended",
            "old_length": len(old_content),
            "new_length": len(combined_content)
        })
    else:
        # Create new entry
        con.execute("""
            INSERT INTO knowledge (id, category, title, tags, content, metadata, created, updated)
            VALUES (?, 'reference', ?, ?, ?, '{}', ?, ?)
        """, [entry_id, title, ['accumulator'], new_content, now, now])

        return json_response({
            "id": entry_id,
            "status": "created",
            "length": len(new_content)
        })
