"""Add item to a list entry (todo, accumulator, any list)."""
from typing import List
from datetime import datetime, timezone
from mcp.types import Tool, TextContent

from .base import json_response

TOOL_DEF = Tool(
    name="list_add",
    description="""Add an item to any list-type entry. Creates list if it doesn't exist.

Works for accumulators or any entry using `- item` format.
Use list_remove to remove items.""",
    inputSchema={
        "type": "object",
        "properties": {
            "id": {"type": "string", "description": "Entry ID (e.g., 'accumulator-corrections')"},
            "content": {"type": "string", "description": "Item content (will be prefixed with '- ')"},
            "title": {"type": "string", "description": "Title for new list (only used if creating)"},
            "category": {"type": "string", "description": "Category for new list (required if creating new entry)"}
        },
        "required": ["id", "content"]
    }
)

REQUIRES_DB = True


async def execute(con, args: dict) -> List[TextContent]:
    entry_id = args["id"]
    item_content = args["content"]
    title = args.get("title", entry_id.replace("-", " ").title())
    category = args.get("category", "other")

    now = datetime.now(timezone.utc)

    # Check if exists
    existing = con.execute(
        "SELECT content FROM knowledge WHERE id = ?",
        [entry_id]
    ).fetchone()

    if existing:
        # Add to existing list
        old_content = existing[0]
        new_item = f"- {item_content}"

        # Add item at end, before any trailing whitespace
        content_stripped = old_content.rstrip()
        new_content = content_stripped + "\n" + new_item + "\n"

        con.execute("""
            UPDATE knowledge SET content = ?, updated = ? WHERE id = ?
        """, [new_content, now, entry_id])

        # Count items
        item_count = new_content.count("\n- ") + (1 if new_content.lstrip().startswith("- ") else 0)

        return json_response({
            "id": entry_id,
            "status": "added",
            "item": item_content,
            "total_items": item_count
        })
    else:
        # Create new list
        new_content = f"- {item_content}\n"

        con.execute("""
            INSERT INTO knowledge (id, category, title, tags, content, metadata, created, updated)
            VALUES (?, ?, ?, ?, ?, '{}', ?, ?)
        """, [entry_id, category, title, [category], new_content, now, now])

        return json_response({
            "id": entry_id,
            "status": "created",
            "item": item_content,
            "total_items": 1
        })
