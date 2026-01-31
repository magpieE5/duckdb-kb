"""Extract and upsert transcript from session file.

Combines session detection, exchange extraction, and KB upsert into one atomic operation.
Eliminates the model-in-the-loop failure point from the old close.md workflow.
"""
from typing import List
from datetime import datetime, timezone
from pathlib import Path
from mcp.types import Tool, TextContent

from .base import json_response, error_response
from .session_details import get_session_details
from .extract_exchanges import (
    extract_exchanges,
    format_exchanges,
    detect_format,
)

TOOL_DEF = Tool(
    name="extract_transcript",
    description="""Extract transcript from session file and upsert to KB.

Automatically finds the latest session file (Claude JSONL or Gemini JSON),
extracts User/Thinking/Said exchanges, and upserts as transcript-{NNN}.

Use this at session close instead of manually running extract_exchanges.py + upsert_knowledge.

Parameters:
- session_number: Required. The session number (e.g., 153)
- session_path: Optional. Override auto-detection with specific file path
- suppress: Optional. Apply structured content suppression (default: true)
- max_exchanges: Optional. Limit number of exchanges extracted""",
    inputSchema={
        "type": "object",
        "properties": {
            "session_number": {
                "type": "integer",
                "description": "Session number for the transcript ID (e.g., 153 -> transcript-153)"
            },
            "session_path": {
                "type": "string",
                "description": "Optional: specific session file path (auto-detects if not provided)"
            },
            "suppress": {
                "type": "boolean",
                "description": "Suppress structured content like code blocks, JSON, XML (default: true)"
            },
            "max_exchanges": {
                "type": "integer",
                "description": "Optional: limit number of exchanges to extract"
            }
        },
        "required": ["session_number"]
    }
)

REQUIRES_DB = True


async def execute(con, args: dict) -> List[TextContent]:
    session_number = args["session_number"]
    session_path = args.get("session_path")
    suppress = args.get("suppress", True)
    max_exchanges = args.get("max_exchanges")

    # Find session file
    if session_path:
        file_path = Path(session_path)
        if not file_path.exists():
            return error_response("file_not_found", f"Session file not found: {session_path}")
    else:
        details = get_session_details()
        if not details.get("latest_session"):
            return error_response("no_session", "No session file found. Provide session_path manually.")
        file_path = Path(details["latest_session"])

    # Extract exchanges
    try:
        fmt = detect_format(file_path)
        exchanges = extract_exchanges(file_path)
        content = format_exchanges(exchanges, max_exchanges, suppress=suppress)
    except Exception as e:
        return error_response("extraction_error", f"Failed to extract exchanges: {str(e)}")

    # Build transcript entry
    entry_id = f"transcript-{session_number:03d}"
    title = f"Session {session_number} Transcript"
    tags = ["transcript", f"session-{session_number}"]
    now = datetime.now(timezone.utc)

    # Check if exists
    existing = con.execute("SELECT 1 FROM knowledge WHERE id = ?", [entry_id]).fetchone()

    # Upsert
    con.execute("""
        INSERT INTO knowledge (id, category, title, tags, content, metadata, created, updated)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT (id) DO UPDATE SET
            category = EXCLUDED.category,
            title = EXCLUDED.title,
            tags = EXCLUDED.tags,
            content = EXCLUDED.content,
            metadata = EXCLUDED.metadata,
            updated = ?
    """, [entry_id, "transcript", title, tags, content, "{}", now, now, now])

    return json_response({
        "id": entry_id,
        "status": "updated" if existing else "created",
        "format": fmt,
        "exchanges": len(exchanges),
        "content_length": len(content),
        "suppressed": suppress,
        "source": str(file_path)
    })
