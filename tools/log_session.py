"""Session logging tool - simplified. Captures meaning, not transcript."""
from typing import List, Dict, Any
from datetime import datetime, timezone
import json
from mcp.types import Tool, TextContent

from .base import error_response, json_response

TOOL_DEF = Tool(
    name="log_session",
    description="""Create session log. Captures relational context, not transcript.

## Auto-detected
- **session_number**: Next session number (max existing + 1)

## AI-provided parameters
- **preview**: Dense searchable summary (~400 chars). Format: "{date} ({day}), {mode}. {Key events}. Key: {terms}."
- **witness**: Session Witness - the relationship layer. Object with:
  - **you_today**: What I noticed about the user - mood, energy, what they seemed to need
  - **me_today**: Where I helped, where I struggled, what I'd do differently
  - **us_today**: Anything notable about our dynamic this session
- **handoff**: Summary for next session. Unfinished business, context needed, KB operations performed.

Transcript is in JSONL, extracted to transcript/ at session close. Logs capture meaning, not exchanges.""",
    inputSchema={
        "type": "object",
        "properties": {
            "preview": {"type": "string", "description": "Dense searchable summary line"},
            "witness": {
                "type": "object",
                "description": "Session Witness - the relationship layer",
                "properties": {
                    "you_today": {"type": "string", "description": "What I noticed about the user"},
                    "me_today": {"type": "string", "description": "Where I helped/struggled, what I'd do differently"},
                    "us_today": {"type": "string", "description": "Notable dynamics this session"}
                },
                "required": ["you_today", "me_today", "us_today"]
            },
            "handoff": {"type": "string", "description": "Context and summary for next session"}
        },
        "required": ["preview", "witness", "handoff"]
    }
)

REQUIRES_DB = True


def _get_next_session_number(con) -> int:
    """Get next session number from KB."""
    result = con.execute("""
        SELECT COALESCE(MAX(CAST(REPLACE(id, 'session-', '') AS INT)), 0) + 1
        FROM knowledge
        WHERE id LIKE 'session-%' AND category = 'log'
    """).fetchone()
    return result[0]


def _generate_log_content(session_number: int, preview: str,
                          witness: dict, handoff: str) -> str:
    date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    return f"""# Session {session_number} Log

**Date:** {date}

---

<!-- PREVIEW -->
{preview}
<!-- /PREVIEW -->

---

## Session Witness

**You today:** {witness.get('you_today', '')}

**Me today:** {witness.get('me_today', '')}

**Us today:** {witness.get('us_today', '')}

---

## Handoff

{handoff}
"""


async def _upsert_kb_entry(con, entry: Dict[str, Any]):
    """Insert or update (upsert) a KB entry."""
    now = datetime.now(timezone.utc)
    con.execute("""
        INSERT INTO knowledge (id, category, title, content, tags, metadata, created, updated)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT (id) DO UPDATE SET
            content = EXCLUDED.content,
            tags = EXCLUDED.tags,
            metadata = EXCLUDED.metadata,
            updated = ?
    """, [entry["id"], entry["category"], entry["title"], entry["content"],
          entry["tags"], json.dumps(entry.get("metadata", {})), now, now, now])


async def execute(con, args: dict) -> List[TextContent]:
    preview = args["preview"]
    witness = args["witness"]
    handoff = args["handoff"]

    try:
        session_number = _get_next_session_number(con)

        log_id = f"session-{session_number:03d}"
        log_entry = {
            "id": log_id,
            "category": "log",
            "title": f"Session {session_number} Log",
            "content": _generate_log_content(session_number, preview, witness, handoff),
            "tags": ["session", f"session-{session_number}"],
            "metadata": {}
        }
        await _upsert_kb_entry(con, log_entry)

    except Exception as e:
        error = error_response("database_error", f"Failed to log session: {str(e)}")
        return [TextContent(type="text", text=json.dumps(error, indent=2))]

    return json_response({"success": True, "session_number": session_number, "log_id": log_id})
