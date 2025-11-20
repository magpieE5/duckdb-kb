"""Get KB initialization status and parse USER.md"""

from mcp.types import Tool, TextContent
from typing import List
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
import duckdb

# =============================================================================
# Tool Definition (for registration)
# =============================================================================

TOOL = Tool(
    name="get_kb_session_status",
    description="""Get KB initialization status and parse context entries for focus areas, commitments, and topics.

Returns structured JSON with:
- database.action: "init_db_fresh", "init_db_restore", or "check_empty"
- status.focus_areas: Top focus areas from user-current-state
- status.commitments: All, approaching (7 days), and overdue commitments from user-current-state
- selected_topics: Intensity-balanced topic selection from context entries
- recent_sessions: Parsed session history from arlo-current-state

Intensity-based topic selection:
- LOW (1-3): 80% user topics, 20% arlo topics
- MEDIUM (4-6): 50/50 balanced user + arlo topics
- HIGH (7-9): 20% user topics, 80% arlo topics

Used by /kb command for deterministic initialization flow.""",
    inputSchema={
        "type": "object",
        "properties": {
            "intensity": {
                "type": "integer",
                "minimum": 1,
                "maximum": 10,
                "description": "Session intensity for topic selection (optional)"
            }
        }
    }
)

# =============================================================================
# Implementation
# =============================================================================

async def execute(args: dict) -> List[TextContent]:
    """Get KB initialization status, parse context entries, check deadlines, select topics"""
    # Get project directory (2 levels up from this file)
    project_dir = Path(__file__).parent.parent.parent
    db_path = project_dir / "kb.duckdb"
    markdown_dir = project_dir / "markdown"

    intensity = args.get("intensity")

    result = {
        "database": {},
        "status": {
            "focus_areas": [],
            "commitments": {
                "all": [],
                "approaching": [],
                "overdue": []
            }
        },
        "selected_topics": None,
        "recent_sessions": [],
        "timestamp": datetime.now().isoformat()
    }

    # Check database status
    if not db_path.exists():
        # Check if markdown exports exist for recovery
        has_markdown = False
        if markdown_dir.exists():
            for item in markdown_dir.iterdir():
                if item.is_dir() and list(item.glob("*.md")):
                    has_markdown = True
                    break

        if has_markdown:
            result["database"] = {
                "exists": False,
                "action": "init_db_restore",
                "needs_import": True,
                "import_path": str(markdown_dir),
                "message": "Database not found - restoring from markdown exports"
            }
        else:
            result["database"] = {
                "exists": False,
                "action": "init_db_fresh",
                "needs_import": False,
                "message": "First run detected - initializing empty database"
            }
    else:
        # Database file exists - verify schema is initialized
        schema_valid = False
        try:
            test_con = duckdb.connect(str(db_path), read_only=True)
            # Check if knowledge table exists
            test_con.execute("SELECT COUNT(*) FROM knowledge LIMIT 1")
            schema_valid = True
            test_con.close()
        except Exception:
            # Schema doesn't exist or is corrupted
            schema_valid = False

        if schema_valid:
            result["database"] = {
                "exists": True,
                "action": "check_empty",
                "message": "Database found - checking contents"
            }
        else:
            # Database file exists but schema invalid - treat as fresh install
            result["database"] = {
                "exists": True,
                "action": "init_db_fresh",
                "needs_import": False,
                "message": "Database file found but schema invalid - reinitializing"
            }

    # Parse focus areas and commitments from user-current-state (if database exists)
    if db_path.exists():
        try:
            con = duckdb.connect(str(db_path), read_only=True)

            # Try to fetch user-current-state
            content = _fetch_entry_content(con, "user-current-state")

            if content:
                # Parse focus areas (### sections under Top Active Focus)
                focus_match = re.search(
                    r'### Top Active Focus(.*?)(?=\n##|\Z)',
                    content,
                    re.DOTALL
                )

                if focus_match:
                    focus_section = focus_match.group(1)
                    # Pattern: 1. **[Project name] (date)** - [priority]
                    for match in re.finditer(
                        r'(\d+)\.\s+\*\*(.+?)\s+\(.*?\)\*\*\s+-\s+\[(\w+)\]',
                        focus_section
                    ):
                        number = int(match.group(1))
                        name = match.group(2).strip()
                        priority = match.group(3).strip()

                        result["status"]["focus_areas"].append({
                            "number": number,
                            "name": name,
                            "priority": priority
                        })

                # Parse commitments (## Immediate Commitments section)
                commits_match = re.search(
                    r'## Immediate Commitments(.*?)(?=\n##|\Z)',
                    content,
                    re.DOTALL
                )

                if commits_match:
                    commits_section = commits_match.group(1)
                    today = datetime.now()

                    # Pattern: - [ ] **[description] (date)** - due: YYYY-MM-DD, priority
                    for match in re.finditer(
                        r'-\s+\[\s+\]\s+\*\*(.+?)\s+\(.*?\)\*\*\s+-\s+due:\s+(\d{4}-\d{2}-\d{2})',
                        commits_section
                    ):
                        description = match.group(1).strip()
                        due_date_str = match.group(2)

                        try:
                            due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
                            days_until = (due_date - today).days

                            commitment = {
                                "description": description,
                                "due_date": due_date_str,
                                "days_until": days_until,
                                "approaching": days_until <= 7 and days_until >= 0,
                                "overdue": days_until < 0
                            }

                            result["status"]["commitments"]["all"].append(commitment)

                            if commitment["approaching"]:
                                result["status"]["commitments"]["approaching"].append(commitment)
                            if commitment["overdue"]:
                                result["status"]["commitments"]["overdue"].append(commitment)
                        except ValueError:
                            continue

            con.close()
        except Exception:
            # Database error - skip parsing
            pass

    # Intensity-based topic selection (if intensity provided and database exists)
    if intensity is not None and db_path.exists():
        try:
            con = duckdb.connect(str(db_path), read_only=True)
            result["selected_topics"] = _select_topics_by_intensity(con, intensity)
            result["recent_sessions"] = _parse_recent_sessions(con)
            con.close()
        except Exception as e:
            # Database error - skip topic selection
            result["selected_topics"] = {"error": str(e)}

    return [TextContent(type="text", text=json.dumps(result))]


def _select_topics_by_intensity(con, intensity: int) -> dict:
    """Select topics from context entries based on intensity"""

    # Calculate user/arlo ratio based on intensity
    if intensity <= 3:
        user_ratio = 0.8  # 80% user, 20% arlo
    elif intensity <= 6:
        user_ratio = 0.5  # 50/50
    else:
        user_ratio = 0.2  # 20% user, 80% arlo

    total_topics = 10  # Total topics to select
    user_count = int(total_topics * user_ratio)
    arlo_count = total_topics - user_count

    # Fetch context entries
    user_content = _fetch_entry_content(con, "user-current-state")
    arlo_content = _fetch_entry_content(con, "arlo-current-state")

    # Parse topics (simple extraction of ### sections)
    user_topics = _extract_topics(user_content) if user_content else []
    arlo_topics = _extract_topics(arlo_content) if arlo_content else []

    # Select topics (most recent first)
    selected_user = user_topics[:user_count] if len(user_topics) >= user_count else user_topics
    selected_arlo = arlo_topics[:arlo_count] if len(arlo_topics) >= arlo_count else arlo_topics

    return {
        "intensity": intensity,
        "user_ratio": user_ratio,
        "user_topics": selected_user,
        "arlo_topics": selected_arlo,
        "total_selected": len(selected_user) + len(selected_arlo)
    }


def _parse_recent_sessions(con) -> List[dict]:
    """Parse recent session history from arlo-current-state"""

    content = _fetch_entry_content(con, "arlo-current-state")
    if not content:
        return []

    sessions = []

    # Pattern: **S1 (YYYY-MM-DD):** description
    pattern = r'\*\*S(\d+) \((\d{4}-\d{2}-\d{2})\):\*\* (.+?)(?=\n\*\*S\d+|\Z)'

    matches = re.finditer(pattern, content, re.DOTALL)

    for match in matches:
        session_num = int(match.group(1))
        date = match.group(2)
        description = match.group(3).strip()

        sessions.append({
            "session_number": session_num,
            "date": date,
            "description": description
        })

    # Sort by session number descending (most recent first)
    sessions.sort(key=lambda s: s["session_number"], reverse=True)

    return sessions[:5]  # Return 5 most recent


def _fetch_entry_content(con, entry_id: str) -> str:
    """Fetch content of a KB entry"""

    try:
        row = con.execute(
            "SELECT content FROM knowledge WHERE id = ?",
            [entry_id]
        ).fetchone()

        return row[0] if row else ""
    except Exception:
        return ""


def _extract_topics(content: str) -> List[dict]:
    """Extract topics from entry content (### sections with timestamps)"""

    topics = []

    # Pattern: ### Topic Title (YYYY-MM-DD)
    pattern = r'###\s+([^\n]+?)\s+\((\d{4}-\d{2}-\d{2})\)'

    matches = re.finditer(pattern, content)

    for match in matches:
        title = match.group(1).strip()
        timestamp = match.group(2)

        topics.append({
            "title": title,
            "timestamp": timestamp
        })

    # Sort by timestamp descending (most recent first)
    topics.sort(key=lambda t: t["timestamp"], reverse=True)

    return topics

# =============================================================================
# Metadata
# =============================================================================

REQUIRES_DB = False
