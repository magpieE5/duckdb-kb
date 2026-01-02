"""Add item to a todo list."""
from typing import List
from datetime import datetime
from mcp.types import Tool, TextContent

from .base import json_response

TOOL_DEF = Tool(
    name="todo_add",
    description="""Add a todo item. Creates list if it doesn't exist.

Flat list - no sections. Items are added at the end.
Use todo_complete to remove items when done.""",
    inputSchema={
        "type": "object",
        "properties": {
            "id": {"type": "string", "description": "Todo entry ID (e.g., 'todo-work', 'todo-personal')"},
            "content": {"type": "string", "description": "Todo item content"},
            "title": {"type": "string", "description": "Title for new list (only used if creating)"}
        },
        "required": ["id", "content"]
    }
)

REQUIRES_DB = True


async def execute(con, args: dict) -> List[TextContent]:
    entry_id = args["id"]
    item_content = args["content"]
    title = args.get("title", entry_id.replace("-", " ").title())

    now = datetime.now()

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
            VALUES (?, 'todo', ?, ?, ?, '{}', ?, ?)
        """, [entry_id, title, ['todo'], new_content, now, now])

        return json_response({
            "id": entry_id,
            "status": "created",
            "item": item_content,
            "total_items": 1
        })
