"""Cleanup test entries from KB

Removes test entries by pattern matching:
- IDs containing 'test'
- Tags containing 'test'
- Configurable exclusions

Used for post-test cleanup and maintenance.
"""

from mcp.types import Tool, TextContent
from typing import List
import json

# =============================================================================
# Tool Definition (for registration)
# =============================================================================

TOOL = Tool(
    name="cleanup_test_entries",
    description="""Cleanup test entries from KB.

WHEN TO USE: After test runs, maintenance cleanup

Matches entries by:
- IDs containing 'test' (case-insensitive)
- Tags containing 'test'
- Custom pattern matching

Options:
- dry_run: Show what would be deleted without deleting (default: false)
- exclude_ids: List of entry IDs to never delete
- pattern: Custom pattern to match (default: 'test')

Returns:
- found: Count of entries matching pattern
- deleted: Count of entries deleted
- skipped: Count of entries skipped (due to exclusions)
- ids: List of affected entry IDs""",
    inputSchema={
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "default": "test",
                "description": "Pattern to match in IDs/tags (case-insensitive)"
            },
            "dry_run": {
                "type": "boolean",
                "default": False,
                "description": "Show what would be deleted without deleting"
            },
            "exclude_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Entry IDs to never delete",
                "default": []
            }
        }
    }
)

# =============================================================================
# Implementation
# =============================================================================

async def execute(con, args: dict) -> List[TextContent]:
    """Cleanup test entries from KB"""

    pattern = args.get("pattern", "test").lower()
    dry_run = args.get("dry_run", False)
    exclude_ids = args.get("exclude_ids", [])

    # Find entries matching pattern
    # Match on ID or tags containing pattern
    query = """
        SELECT id, category, title, tags
        FROM knowledge
        WHERE LOWER(id) LIKE ? OR list_has_any(tags, ?)
    """

    pattern_like = f"%{pattern}%"
    results = con.execute(query, [pattern_like, [pattern]]).fetchall()

    found_ids = []
    excluded_ids = []

    for row in results:
        entry_id = row[0]

        # Check if excluded
        if entry_id in exclude_ids:
            excluded_ids.append(entry_id)
            continue

        found_ids.append(entry_id)

    # Delete entries (unless dry_run)
    deleted_ids = []

    if not dry_run and found_ids:
        for entry_id in found_ids:
            try:
                con.execute("DELETE FROM knowledge WHERE id = ?", [entry_id])
                deleted_ids.append(entry_id)
            except Exception as e:
                # Failed to delete - skip
                pass

    response = {
        "pattern": pattern,
        "dry_run": dry_run,
        "found": len(found_ids) + len(excluded_ids),
        "deleted": len(deleted_ids),
        "skipped": len(excluded_ids),
        "would_delete": found_ids if dry_run else None,
        "deleted_ids": deleted_ids if not dry_run else None,
        "excluded_ids": excluded_ids if excluded_ids else None,
        "message": _build_message(dry_run, len(found_ids), len(deleted_ids), len(excluded_ids))
    }

    return [TextContent(type="text", text=json.dumps(response, indent=2))]


def _build_message(dry_run: bool, found: int, deleted: int, excluded: int) -> str:
    """Build human-readable message"""

    if dry_run:
        if found == 0:
            return "No test entries found matching pattern"
        else:
            msg = f"DRY RUN: Would delete {found} entries"
            if excluded > 0:
                msg += f" ({excluded} excluded)"
            return msg
    else:
        if deleted == 0 and found == 0:
            return "✅ No test entries found - KB clean"
        elif deleted == 0:
            return f"⚠️ Found {found + excluded} entries but none deleted (all excluded)"
        else:
            msg = f"✅ Deleted {deleted} test entries"
            if excluded > 0:
                msg += f" ({excluded} excluded from deletion)"
            return msg

# =============================================================================
# Metadata
# =============================================================================

REQUIRES_DB = True
