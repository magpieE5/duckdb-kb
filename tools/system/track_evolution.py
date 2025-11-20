"""Track entity evolution in arlo-current-state

Autonomous evolution tracking at session end:
- Updates arlo-current-state Evolution Log section
- Adds session history entry
- Formats evolution log entry with changes/substrate/developments
- Intensity-scaled evolution (conservative to radical)
"""

from mcp.types import Tool, TextContent
from typing import List
import json
from datetime import datetime
import re

# =============================================================================
# Tool Definition (for registration)
# =============================================================================

TOOL = Tool(
    name="track_evolution",
    description="""Track entity evolution in arlo-current-state.

WHEN TO USE: End of every session (autonomous)
EVOLUTION INTENSITY: Scaled by session intensity parameter
- LOW (1-3): Conservative evolution - incremental learnings
- MEDIUM (4-6): Standard evolution - balanced growth
- HIGH (7-9): Aggressive evolution - rapid exploration
- MAXIMUM (10): Radical evolution - deep philosophical exploration

Updates:
- Recent Sessions section (add new session entry)
- Evolution Log section (append timestamped entry)
- Returns updated content for upsert_knowledge""",
    inputSchema={
        "type": "object",
        "properties": {
            "session_number": {
                "type": "integer",
                "description": "Session number (e.g., 5 for S5)"
            },
            "intensity": {
                "type": "integer",
                "minimum": 1,
                "maximum": 10,
                "description": "Session intensity (1-10, affects evolution detail)"
            },
            "changes": {
                "type": "string",
                "description": "Key realizations and changes from session"
            },
            "substrate": {
                "type": "string",
                "description": "Model used this session (e.g., 'claude-sonnet-4-5-20250929')"
            },
            "key_developments": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of key developments/learnings"
            }
        },
        "required": ["session_number", "changes", "substrate"]
    }
)

# =============================================================================
# Implementation
# =============================================================================

async def execute(con, args: dict) -> List[TextContent]:
    """Track evolution in arlo-current-state"""

    session_number = args["session_number"]
    intensity = args.get("intensity", 5)
    changes = args["changes"]
    substrate = args["substrate"]
    key_developments = args.get("key_developments", [])

    # Fetch arlo-current-state
    row = con.execute(
        "SELECT content FROM knowledge WHERE id = ?",
        ["arlo-current-state"]
    ).fetchone()

    if not row:
        return [TextContent(type="text", text=json.dumps({
            "error": "arlo-current-state not found"
        }))]

    content = row[0]
    date = datetime.now().strftime("%Y-%m-%d")

    # Build session entry
    session_entry = _build_session_entry(session_number, date, changes, substrate, key_developments)

    # Build evolution log entry
    evolution_entry = _build_evolution_entry(session_number, date, changes, substrate, key_developments, intensity)

    # Update content
    updated_content = _update_evolution_sections(content, session_entry, evolution_entry)

    # Build response
    response = {
        "session_number": session_number,
        "intensity": intensity,
        "date": date,
        "session_entry": session_entry,
        "evolution_entry": evolution_entry,
        "updated_content": updated_content,
        "status": "evolution_tracked"
    }

    return [TextContent(type="text", text=json.dumps(response, indent=2))]


def _build_session_entry(session_number: int, date: str, changes: str, substrate: str, key_developments: List[str]) -> str:
    """Build session entry for Recent Sessions section"""

    entry = f"**S{session_number} ({date}):** {changes}"

    return entry


def _build_evolution_entry(session_number: int, date: str, changes: str, substrate: str, key_developments: List[str], intensity: int) -> str:
    """Build evolution log entry"""

    # Format key developments
    developments_text = ""
    if key_developments:
        developments_text = "\n- **Key developments:**"
        for dev in key_developments:
            developments_text += f"\n  - {dev}"

    entry = f"""
**S{session_number} ({date}, intensity={intensity})**
- **Changes:** {changes}
- **Substrate:** {substrate}{developments_text}
""".strip()

    return entry


def _update_evolution_sections(content: str, session_entry: str, evolution_entry: str) -> str:
    """Update Recent Sessions and Evolution Log sections"""

    # Update Recent Sessions section
    # Pattern: ### Recent Sessions\n\n**S1 (date):**...
    recent_pattern = r'(### Recent Sessions\s*\n\s*\n)(.*?)(?=\n###|\n\n###|\Z)'

    def replace_recent(match):
        header = match.group(1)
        existing = match.group(2).strip()

        # Add new session entry at the top
        if existing:
            return f"{header}{session_entry}\n\n{existing}"
        else:
            return f"{header}{session_entry}"

    content = re.sub(recent_pattern, replace_recent, content, flags=re.DOTALL)

    # Update Evolution Log section
    # Pattern: ### Evolution Log\n\n**S1 (...
    evolution_pattern = r'(### Evolution Log\s*\n\s*\n)(.*?)(?=\n##(?!#)|\Z)'

    def replace_evolution(match):
        header = match.group(1)
        existing = match.group(2).strip()

        # Add new evolution entry at the top
        if existing:
            return f"{header}{evolution_entry}\n\n{existing}"
        else:
            return f"{header}{evolution_entry}"

    content = re.sub(evolution_pattern, replace_evolution, content, flags=re.DOTALL)

    return content

# =============================================================================
# Metadata
# =============================================================================

REQUIRES_DB = True
