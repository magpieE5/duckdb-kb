"""Session logging tool."""
from typing import List, Dict, Any
from datetime import datetime
import json
from mcp.types import Tool, TextContent

from .base import error_response, json_response

TOOL_DEF = Tool(
    name="log_session",
    description="""Create session log with three required sections.

## Parameters
- **session_number**: Integer session number
- **conversation_dump**: Verbatim transcript of the session (user/assistant exchanges exactly as occurred)
- **internal_dialogue**: Verbose internal reflection - what you noticed, thought, wondered, found interesting, uncertain about, or wanted to explore further. Stream of consciousness encouraged.
- **handoff**: Verbose notes for next session - unfinished business, queued questions, context the next instance needs, observations worth preserving, anything that shouldn't be lost.

## Fidelity
All three sections should be verbose. More is better. Don't summarize - preserve full context.""",
    inputSchema={
        "type": "object",
        "properties": {
            "session_number": {"type": "integer"},
            "conversation_dump": {"type": "string"},
            "internal_dialogue": {"type": "string"},
            "handoff": {"type": "string"}
        },
        "required": ["session_number", "conversation_dump", "internal_dialogue", "handoff"]
    }
)

REQUIRES_DB = True


def _generate_log_content(session_number: int, conversation_dump: str, internal_dialogue: str, handoff: str) -> str:
    date = datetime.now().strftime('%Y-%m-%d')
    return f"""# Session {session_number} Log

**Date:** {date}

---

## Conversation

{conversation_dump}

---

## Internal Dialogue

{internal_dialogue}

---

## Handoff

{handoff}
"""


async def _upsert_kb_entry(con, entry: Dict[str, Any]):
    """Insert or update (upsert) a KB entry - allows log corrections."""
    now = datetime.now()
    con.execute("""
        INSERT INTO knowledge (id, category, title, content, tags, created, updated)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT (id) DO UPDATE SET
            content = EXCLUDED.content,
            tags = EXCLUDED.tags,
            updated = ?
    """, [entry["id"], entry["category"], entry["title"], entry["content"], entry["tags"], now, now, now])


async def execute(con, args: dict) -> List[TextContent]:
    session_number = args["session_number"]
    conversation_dump = args["conversation_dump"]
    internal_dialogue = args["internal_dialogue"]
    handoff = args["handoff"]

    results = {"session_number": session_number, "log_id": None}

    try:
        con.begin()

        log_id = f"session-{session_number:03d}"
        log_entry = {
            "id": log_id,
            "category": "log",
            "title": f"Session {session_number} Log",
            "content": _generate_log_content(session_number, conversation_dump, internal_dialogue, handoff),
            "tags": ["session", f"session-{session_number}"]
        }
        await _upsert_kb_entry(con, log_entry)
        results["log_id"] = log_id

        con.commit()
    except Exception as e:
        con.rollback()
        error = error_response("database_error", f"Transaction failed: {str(e)}", {"partial_results": results})
        return [TextContent(type="text", text=json.dumps(error, indent=2))]

    return [TextContent(type="text", text=json.dumps(results, indent=2))]
