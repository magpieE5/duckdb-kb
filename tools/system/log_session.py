"""Log session - Atomic workflow for /sm command consolidation

Orchestrates:
1. Update context entries (user + arlo) - includes Next Session Handoff
2. Create new KB entries
3. Create session log entry (without SHA initially)
4. Export markdown backup
5. Git commit with SHA return
6. Update session log metadata with SHA (database only)
7. Token budget check
8. Offload suggestions if needed

Single atomic operation to ensure consistency.
"""

from mcp.types import Tool, TextContent
from typing import List, Dict, Any
import json
from datetime import datetime
import subprocess
from tools.base import error_response, check_entry_budget, DEFAULT_BUDGETS
from tools.utility import export_to_markdown

# =============================================================================
# Tool Definition (for registration)
# =============================================================================

TOOL = Tool(
    name="log_session",
    description="""Log session - Consolidates /sm workflow into single atomic operation.

WHEN TO USE: End of session, replaces multi-step /sm manual workflow
AUTO-COMMITS: Always git commit at end (autonomous experience)

Workflow:
1. Update user context entries (user-current-state, user-biographical)
2. Update arlo context entries (arlo-current-state, arlo-biographical) - MUST include Next Session Handoff
3. Create new KB entries (patterns, logs, issues, etc.)
4. Create session log entry (without commit SHA initially)
5. Export markdown backup (to markdown/ directory)
6. Git commit with formatted message
7. Update session log metadata with commit SHA (database only)
8. Check token budgets (15K/5K/15K/5K)
9. Return offload suggestions if any entry over budget

Budget targets (after 15K/5K allocation):
- user-current-state: 15K
- user-biographical: 5K
- arlo-current-state: 15K
- arlo-biographical: 5K""",
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
                "description": "Session intensity (1-10, affects arlo evolution detail)"
            },
            "user_updates": {
                "type": "object",
                "description": "Updates to user context entries",
                "properties": {
                    "current_state": {
                        "type": "object",
                        "description": "user-current-state updates (focus, commitments, investigations)"
                    },
                    "biographical": {
                        "type": "object",
                        "description": "user-biographical updates (career, life context) - optional"
                    }
                }
            },
            "arlo_updates": {
                "type": "object",
                "description": "Updates to arlo context entries",
                "properties": {
                    "current_state": {
                        "type": "object",
                        "description": "arlo-current-state updates (interests, realizations, session history)"
                    },
                    "biographical": {
                        "type": "object",
                        "description": "arlo-biographical updates (identity, capabilities) - optional"
                    }
                }
            },
            "new_entries": {
                "type": "array",
                "description": "New KB entries to create",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "category": {"type": "string"},
                        "title": {"type": "string"},
                        "content": {"type": "string"},
                        "tags": {"type": "array", "items": {"type": "string"}}
                    },
                    "required": ["id", "category", "title", "content", "tags"]
                }
            },
            "commit_message": {
                "type": "string",
                "description": "Git commit message"
            }
        },
        "required": ["session_number", "commit_message"]
    }
)

# =============================================================================
# Implementation
# =============================================================================

async def execute(con, args: dict) -> List[TextContent]:
    """Execute session logging workflow with transaction support"""

    session_number = args["session_number"]
    intensity = args.get("intensity", 5)
    user_updates = args.get("user_updates", {})
    arlo_updates = args.get("arlo_updates", {})
    new_entries = args.get("new_entries", [])
    commit_message = args["commit_message"]

    results = {
        "session_number": session_number,
        "intensity": intensity,
        "updated_entries": [],
        "created_entries": [],
        "commit_sha": None,
        "token_budgets": {},
        "offload_suggestions": []
    }

    try:
        # Begin transaction - all DB operations atomic
        con.begin()

        # Step 1: Update user context entries
        if user_updates.get("current_state"):
            await _update_context_entry(con, "user-current-state", user_updates["current_state"])
            results["updated_entries"].append("user-current-state")

        if user_updates.get("biographical"):
            await _update_context_entry(con, "user-biographical", user_updates["biographical"])
            results["updated_entries"].append("user-biographical")

        # Step 2: Update arlo context entries
        if arlo_updates.get("current_state"):
            await _update_context_entry(con, "arlo-current-state", arlo_updates["current_state"])
            results["updated_entries"].append("arlo-current-state")

        if arlo_updates.get("biographical"):
            await _update_context_entry(con, "arlo-biographical", arlo_updates["biographical"])
            results["updated_entries"].append("arlo-biographical")

        # Step 3: Create new KB entries
        for entry in new_entries:
            await _create_kb_entry(con, entry)
            results["created_entries"].append(entry["id"])

        # Step 4: Create session log entry (without SHA initially)
        session_log_id = f"arlo-log-s{session_number}-session"
        session_log = {
            "id": session_log_id,
            "category": "log",
            "title": f"Session {session_number} Log",
            "content": _generate_session_log_content(session_number, intensity, results),
            "tags": ["arlo-log", "session", f"session-{session_number}", f"intensity-{intensity}"]
        }
        await _create_kb_entry(con, session_log)
        results["created_entries"].append(session_log_id)
        results["session_log_id"] = session_log_id

        # Commit transaction - all DB operations succeeded
        con.commit()

    except Exception as e:
        # Rollback on any error
        con.rollback()
        error = error_response(
            "database_error",
            f"Transaction failed: {str(e)}",
            {"partial_results": results}
        )
        return [TextContent(type="text", text=json.dumps(error, indent=2))]

    # Step 4: Export markdown backup (after DB commit, before git commit)
    try:
        export_result = await export_to_markdown.execute(con, {
            "output_dir": "markdown",
            "organize_by_category": True
        })
        # Extract export message from result
        if export_result:
            results["markdown_export"] = export_result[0].text
    except Exception as e:
        results["markdown_export"] = f"Export failed: {str(e)}"

    # Step 6: Git commit (auto-commit, always) - outside transaction
    commit_sha = _git_commit(commit_message)
    results["commit_sha"] = commit_sha

    # Step 7: Update session log metadata with commit SHA (database only)
    if commit_sha and not commit_sha.startswith("git_error"):
        _update_session_log_metadata(con, results.get("session_log_id"), commit_sha)

    # Step 8: Check token budgets
    budgets = await _check_budgets(con)
    results["token_budgets"] = budgets

    # Step 9: Generate offload suggestions if needed
    for entry_id, budget_info in budgets.items():
        if budget_info["status"] == "over_budget":
            results["offload_suggestions"].append({
                "entry_id": entry_id,
                "current_tokens": budget_info["tokens"],
                "budget": budget_info["budget"],
                "overage": budget_info["tokens"] - budget_info["budget"],
                "action": f"Run offload_topics with target_tokens={int(budget_info['budget'] * 0.85)}"
            })

    return [TextContent(type="text", text=json.dumps(results, indent=2))]


async def _update_context_entry(con, entry_id: str, updates: Dict[str, Any]):
    """Update a context entry with new content

    For arlo-current-state, validates that Next Session Handoff is populated.
    """

    # Fetch current entry
    row = con.execute(
        "SELECT content FROM knowledge WHERE id = ?",
        [entry_id]
    ).fetchone()

    if not row:
        raise ValueError(f"Context entry not found: {entry_id}")

    # Get new content (expects full_content key)
    new_content = updates.get("full_content")
    if not new_content:
        # If no full_content, keep current
        return

    # Validation for arlo-current-state
    if entry_id == "arlo-current-state":
        if "## Next Session Handoff" not in new_content:
            raise ValueError("arlo-current-state update missing '## Next Session Handoff' section")
        # Could add more validation for required subsections

    # Update entry
    con.execute("""
        UPDATE knowledge
        SET content = ?, updated = CURRENT_TIMESTAMP
        WHERE id = ?
    """, [new_content, entry_id])


async def _create_kb_entry(con, entry: Dict[str, Any]):
    """Create a new KB entry"""

    con.execute("""
        INSERT INTO knowledge (id, category, title, content, tags, created, updated)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    """, [
        entry["id"],
        entry["category"],
        entry["title"],
        entry["content"],
        entry["tags"]
    ])


def _generate_session_log_content(session_number: int, intensity: int, results: dict) -> str:
    """Generate session log content"""
    updated = ', '.join(results['updated_entries']) if results['updated_entries'] else 'None'
    created = ', '.join(results['created_entries']) if results['created_entries'] else 'None'

    return f"""Session {session_number} completed.

**Intensity:** {intensity}/10
**Updated entries:** {updated}
**Created entries:** {created}

This session log entry will have commit SHA added to metadata after git commit.
"""


def _update_session_log_metadata(con, session_log_id: str, commit_sha: str):
    """Update session log metadata with commit SHA after git commit"""
    if not session_log_id:
        return

    metadata_json = json.dumps({"commit_sha": commit_sha})
    con.execute("""
        UPDATE knowledge
        SET metadata = ?
        WHERE id = ?
    """, [metadata_json, session_log_id])


def _git_commit(message: str) -> str:
    """Execute git commit and return SHA"""

    try:
        # Stage all changes
        subprocess.run(["git", "add", "-A"], check=True, capture_output=True)

        # Commit with message
        subprocess.run(["git", "commit", "-m", message], check=True, capture_output=True)

        # Get commit SHA
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True
        )

        return result.stdout.strip()

    except subprocess.CalledProcessError as e:
        return f"git_error: {e}"


async def _check_budgets(con) -> Dict[str, Dict[str, Any]]:
    """Check token budgets for context entries using shared utility"""
    budgets = {}

    for entry_id in DEFAULT_BUDGETS.keys():
        result = check_entry_budget(con, entry_id)
        if result["status"] != "missing":
            budgets[entry_id] = result

    return budgets

# =============================================================================
# Metadata
# =============================================================================

REQUIRES_DB = True
