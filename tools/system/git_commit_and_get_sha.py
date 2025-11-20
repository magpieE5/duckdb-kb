"""Perform git commit and return SHA"""

from mcp.types import Tool, TextContent
from typing import List
import json
import subprocess
from pathlib import Path

# =============================================================================
# Tool Definition (for registration)
# =============================================================================

TOOL = Tool(
    name="git_commit_and_get_sha",
    description="""Perform git add -A, commit with message, and return commit SHA.

Deterministic git workflow for /sm command. Automatically stages all changes, creates commit, and returns SHA for KB log entry metadata.

Returns: {"success": true, "sha": "abc123..."} or error""",
    inputSchema={
        "type": "object",
        "properties": {
            "message": {
                "type": "string",
                "description": "Git commit message (must follow KB-BASE.md format)"
            }
        },
        "required": ["message"]
    }
)

# =============================================================================
# Implementation
# =============================================================================

async def execute(con, args: dict) -> List[TextContent]:
    """Perform git add, commit, and return SHA"""
    message = args.get("message")
    if not message:
        return [TextContent(type="text", text=json.dumps({
            "success": False,
            "error": "message parameter is required"
        }))]

    # Get repo path (project root - 2 levels up from this file)
    repo_path = Path(__file__).parent.parent.parent

    try:
        # Git add all changes
        subprocess.run(
            ["git", "add", "-A"],
            cwd=repo_path,
            check=True,
            capture_output=True,
            text=True
        )

        # Git commit with message
        subprocess.run(
            ["git", "commit", "-m", message],
            cwd=repo_path,
            check=True,
            capture_output=True,
            text=True
        )

        # Get commit SHA
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_path,
            check=True,
            capture_output=True,
            text=True
        )

        sha = result.stdout.strip()

        return [TextContent(type="text", text=json.dumps({
            "success": True,
            "sha": sha
        }))]

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else str(e)
        return [TextContent(type="text", text=json.dumps({
            "success": False,
            "error": error_msg
        }))]

# =============================================================================
# Metadata
# =============================================================================

REQUIRES_DB = False
