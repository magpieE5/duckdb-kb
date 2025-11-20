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
    description="""Get KB initialization status, parse USER.md for focus areas and commitments.

Returns structured JSON with:
- database.action: "init_db_fresh", "init_db_restore", or "check_empty"
- kb_md.action: "setup_kb_md" if template, "ready" if populated
- status.focus_areas: Top 5 parsed from USER.md Current Focus
- status.commitments: All, approaching (7 days), and overdue commitments

Used by /kb command for deterministic initialization flow.""",
    inputSchema={
        "type": "object",
        "properties": {}
    }
)

# =============================================================================
# Implementation
# =============================================================================

async def execute(args: dict) -> List[TextContent]:
    """Get KB initialization status, parse USER.md, check deadlines"""
    # Get project directory (2 levels up from this file)
    project_dir = Path(__file__).parent.parent.parent
    db_path = project_dir / "kb.duckdb"
    kb_md_path = project_dir / ".claude" / "USER.md"
    markdown_dir = project_dir / "markdown"

    result = {
        "database": {},
        "kb_md": {},
        "status": {
            "focus_areas": [],
            "commitments": {
                "all": [],
                "approaching": [],
                "overdue": []
            }
        },
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

    # Check USER.md status
    if not kb_md_path.exists():
        result["kb_md"] = {
            "is_template": True,
            "action": "create_from_template",
            "message": "USER.md not found - needs creation"
        }
    else:
        content = kb_md_path.read_text()

        # Check for template patterns
        template_patterns = [
            r"\[Your Name\]",
            r"\[Your job title/role\]",
            r"\*\*⚠️ TEMPLATE FILE",
            r"Replace all bracketed placeholders"
        ]

        is_template = any(re.search(pattern, content) for pattern in template_patterns)

        result["kb_md"] = {
            "is_template": is_template,
            "action": "setup_kb_md" if is_template else "ready",
            "message": "USER.md needs initial setup" if is_template else "USER.md ready"
        }

        # Parse Current Focus if not template
        if not is_template:
            focus_match = re.search(
                r'## Current Focus[^\n]*\n+(.*?)(?=\n## |\Z)',
                content,
                re.DOTALL
            )

            if focus_match:
                focus_section = focus_match.group(1)
                for match in re.finditer(
                    r'###\s+(\d+)\.\s+(.+?)\s+\(.*?priority:\s*(\w+)',
                    focus_section,
                    re.IGNORECASE
                ):
                    number = int(match.group(1))
                    name = match.group(2).strip()
                    priority = match.group(3).strip().upper()

                    # Extract status
                    status_match = re.search(
                        rf'###\s+{number}\..*?status:\s*([^\)]+)',
                        focus_section,
                        re.IGNORECASE | re.DOTALL
                    )
                    status = status_match.group(1).strip() if status_match else "unknown"

                    result["status"]["focus_areas"].append({
                        "number": number,
                        "name": name,
                        "priority": priority,
                        "status": status
                    })

            # Parse Open Commitments
            commits_match = re.search(
                r'## Open Commitments[^\n]*\n+(.*?)(?=\n## |\Z)',
                content,
                re.DOTALL
            )

            if commits_match:
                commits_section = commits_match.group(1)
                today = datetime.now()

                for match in re.finditer(
                    r'-\s+\[([ x])\]\s+(.+?)\s+\(due:\s*(\d{4}-\d{2}-\d{2})\)',
                    commits_section
                ):
                    completed = match.group(1) == 'x'
                    description = match.group(2).strip()
                    due_date_str = match.group(3)

                    try:
                        due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
                        days_until = (due_date - today).days

                        if not completed:
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

    return [TextContent(type="text", text=json.dumps(result))]

# =============================================================================
# Metadata
# =============================================================================

REQUIRES_DB = False
