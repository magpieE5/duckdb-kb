"""Track user commitments in user-current-state

Proactive commitment checking:
- At session start: Surface approaching deadlines (within 7 days)
- During conversation: Add new commitments
- At session end: Review commitment status
"""

from mcp.types import Tool, TextContent
from typing import List, Dict, Any
import json
from datetime import datetime, timedelta
import re

# =============================================================================
# Tool Definition (for registration)
# =============================================================================

TOOL = Tool(
    name="track_commitments",
    description="""Track user commitments in user-current-state.

WHEN TO USE:
- Session start: check() to surface approaching/overdue commitments
- During conversation: add() when user mentions committing to something
- Session end: check() to review status

Actions:
- add: Add new commitment to user-current-state
- check: Parse commitments and return approaching/overdue
- complete: Mark commitment as completed (remove from list)

Commitment format:
- [ ] **[Task description] (YYYY-MM-DD)** - due: YYYY-MM-DD, [priority]""",
    inputSchema={
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["add", "check", "complete"],
                "description": "Action to perform"
            },
            "commitment": {
                "type": "object",
                "description": "Commitment details (for add action)",
                "properties": {
                    "description": {"type": "string"},
                    "due_date": {"type": "string", "description": "YYYY-MM-DD format"},
                    "priority": {"type": "string", "enum": ["high", "medium", "low"], "default": "medium"}
                }
            },
            "days_ahead": {
                "type": "integer",
                "default": 7,
                "description": "Days ahead to check for approaching deadlines (default: 7)"
            },
            "commitment_id": {
                "type": "string",
                "description": "Commitment description (for complete action)"
            }
        },
        "required": ["action"]
    }
)

# =============================================================================
# Implementation
# =============================================================================

async def execute(con, args: dict) -> List[TextContent]:
    """Execute commitment tracking action"""

    action = args["action"]

    if action == "add":
        return await _add_commitment(con, args)
    elif action == "check":
        return await _check_commitments(con, args)
    elif action == "complete":
        return await _complete_commitment(con, args)
    else:
        return [TextContent(type="text", text=json.dumps({
            "error": f"Unknown action: {action}"
        }))]


async def _add_commitment(con, args: dict) -> List[TextContent]:
    """Add new commitment to user-current-state"""

    commitment = args.get("commitment")
    if not commitment:
        return [TextContent(type="text", text=json.dumps({
            "error": "commitment object required for add action"
        }))]

    # Fetch user-current-state
    row = con.execute(
        "SELECT content FROM knowledge WHERE id = ?",
        ["user-current-state"]
    ).fetchone()

    if not row:
        return [TextContent(type="text", text=json.dumps({
            "error": "user-current-state not found"
        }))]

    content = row[0]
    today = datetime.now().strftime("%Y-%m-%d")

    # Build commitment line
    description = commitment["description"]
    due_date = commitment.get("due_date", "TBD")
    priority = commitment.get("priority", "medium")

    commitment_line = f"- [ ] **{description} ({today})** - due: {due_date}, {priority}"

    # Insert into Immediate Commitments section
    pattern = r'(## Immediate Commitments\s*\n\s*\n)(.*?)(?=\n##|\Z)'

    def replace_commitments(match):
        header = match.group(1)
        existing = match.group(2).strip()

        if existing:
            return f"{header}{commitment_line}\n{existing}"
        else:
            return f"{header}{commitment_line}"

    updated_content = re.sub(pattern, replace_commitments, content, flags=re.DOTALL)

    response = {
        "action": "add",
        "commitment_added": commitment_line,
        "updated_content": updated_content,
        "status": "commitment_added"
    }

    return [TextContent(type="text", text=json.dumps(response, indent=2))]


async def _check_commitments(con, args: dict) -> List[TextContent]:
    """Check commitments for approaching/overdue deadlines"""

    days_ahead = args.get("days_ahead", 7)

    # Fetch user-current-state
    row = con.execute(
        "SELECT content FROM knowledge WHERE id = ?",
        ["user-current-state"]
    ).fetchone()

    if not row:
        return [TextContent(type="text", text=json.dumps({
            "error": "user-current-state not found"
        }))]

    content = row[0]

    # Parse commitments
    commitments = _parse_commitments(content)

    # Categorize by deadline
    now = datetime.now()
    approaching_threshold = now + timedelta(days=days_ahead)

    approaching = []
    overdue = []
    all_active = []

    for commitment in commitments:
        if not commitment["completed"] and commitment["due_date_obj"]:
            all_active.append(commitment)

            if commitment["due_date_obj"] < now:
                days_overdue = (now - commitment["due_date_obj"]).days
                commitment["days_overdue"] = days_overdue
                overdue.append(commitment)
            elif commitment["due_date_obj"] <= approaching_threshold:
                days_until = (commitment["due_date_obj"] - now).days
                commitment["days_until"] = days_until
                approaching.append(commitment)

    response = {
        "action": "check",
        "days_ahead": days_ahead,
        "approaching": approaching,
        "overdue": overdue,
        "all_active": all_active,
        "summary": {
            "total_active": len(all_active),
            "approaching_count": len(approaching),
            "overdue_count": len(overdue)
        }
    }

    return [TextContent(type="text", text=json.dumps(response, indent=2))]


async def _complete_commitment(con, args: dict) -> List[TextContent]:
    """Mark commitment as completed (remove from list)"""

    commitment_id = args.get("commitment_id")
    if not commitment_id:
        return [TextContent(type="text", text=json.dumps({
            "error": "commitment_id required for complete action"
        }))]

    # Fetch user-current-state
    row = con.execute(
        "SELECT content FROM knowledge WHERE id = ?",
        ["user-current-state"]
    ).fetchone()

    if not row:
        return [TextContent(type="text", text=json.dumps({
            "error": "user-current-state not found"
        }))]

    content = row[0]

    # Find and remove commitment line containing the description
    lines = content.split("\n")
    updated_lines = []
    removed = False

    for line in lines:
        if commitment_id.lower() in line.lower() and "- [ ]" in line:
            removed = True
            continue  # Skip this line (remove it)
        updated_lines.append(line)

    updated_content = "\n".join(updated_lines)

    response = {
        "action": "complete",
        "commitment_id": commitment_id,
        "removed": removed,
        "updated_content": updated_content if removed else None,
        "status": "commitment_completed" if removed else "commitment_not_found"
    }

    return [TextContent(type="text", text=json.dumps(response, indent=2))]


def _parse_commitments(content: str) -> List[Dict[str, Any]]:
    """Parse commitments from Immediate Commitments section"""

    commitments = []

    # Pattern: - [ ] or - [x] **description (YYYY-MM-DD)** - due: YYYY-MM-DD, priority
    pattern = r'- \[([ x])\] \*\*(.+?) \((\d{4}-\d{2}-\d{2})\)\*\* - due: (\d{4}-\d{2}-\d{2}|TBD),\s*(\w+)'

    matches = re.finditer(pattern, content)

    for match in matches:
        completed = match.group(1) == 'x'
        description = match.group(2)
        created_date = match.group(3)
        due_date_str = match.group(4)
        priority = match.group(5)

        # Parse due date
        due_date_obj = None
        if due_date_str != "TBD":
            try:
                due_date_obj = datetime.strptime(due_date_str, "%Y-%m-%d")
            except ValueError:
                pass

        commitments.append({
            "description": description,
            "created_date": created_date,
            "due_date": due_date_str,
            "due_date_obj": due_date_obj,
            "priority": priority,
            "completed": completed
        })

    return commitments

# =============================================================================
# Metadata
# =============================================================================

REQUIRES_DB = True
