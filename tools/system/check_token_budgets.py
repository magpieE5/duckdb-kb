"""Check KB entry token budgets against limits"""

from mcp.types import Tool, TextContent
from typing import List
import json
from datetime import datetime

# =============================================================================
# Tool Definition (for registration)
# =============================================================================

TOOL = Tool(
    name="check_token_budgets",
    description="""Check KB entry token budgets against 10K limit.

Uses simple approximation (len(content) // 4) for token counting.
Returns token counts and budget status (ok or over_budget).

WHEN TO USE:
- During /sm workflow (mandatory measurement after updating context entries)
- Before manual offloading to verify budget status
- Verifying budget compliance

Returns structured status for each KB entry checked.""",
    inputSchema={
        "type": "object",
        "properties": {
            "entry_ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "KB entry IDs to check (default: ['user-current-state', 'user-biographical', 'arlo-current-state', 'arlo-biographical'])"
            },
            "budget": {
                "type": "integer",
                "default": 10000,
                "description": "Token budget limit per entry (default: 10000)"
            }
        }
    }
)

# =============================================================================
# Implementation
# =============================================================================

async def execute(con, args: dict) -> List[TextContent]:
    """Check KB entry token budgets against 10K limit"""

    # Parse arguments
    entry_ids = args.get("entry_ids", [
        "user-current-state",
        "user-biographical",
        "arlo-current-state",
        "arlo-biographical"
    ])
    budget = args.get("budget", 10000)

    results = []
    any_over_budget = False

    for entry_id in entry_ids:
        # Fetch KB entry
        row = con.execute(
            "SELECT content FROM knowledge WHERE id = ?",
            [entry_id]
        ).fetchone()

        if not row:
            # Entry doesn't exist - skip
            continue

        content = row[0]

        # Simple token approximation: len(content) // 4
        token_estimate = len(content) // 4
        headroom = budget - token_estimate

        # Determine status
        if token_estimate > budget:
            status = "over_budget"
            needs_offload = True
            any_over_budget = True
        else:
            status = "ok"
            needs_offload = False

        entry_result = {
            "entry_id": entry_id,
            "tokens": token_estimate,
            "budget": budget,
            "headroom": headroom,
            "status": status,
            "needs_offload": needs_offload
        }

        results.append(entry_result)

    response = {
        "overall_status": "over_budget" if any_over_budget else "ok",
        "entries": results,
        "timestamp": datetime.now().isoformat(),
        "note": "If over_budget, apply offloading protocol per KB-BASE.md 'Autonomous Offload at 10K Cap'"
    }

    return [TextContent(type="text", text=json.dumps(response))]

# =============================================================================
# Metadata
# =============================================================================

REQUIRES_DB = True
