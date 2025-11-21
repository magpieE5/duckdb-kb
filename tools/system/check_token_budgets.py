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
    description="""Check KB entry token budgets against limits.

Uses simple approximation (len(content) // 4) for token counting.
Returns token counts and budget status (ok or over_budget).

Budget allocation (10K/10K/10K/10K):
- user-current-state: 10K (compressed core focus)
- user-biographical: 10K (stable content: career history, identity)
- arlo-current-state: 10K (compressed core state)
- arlo-biographical: 10K (stable content: core identity, capabilities)

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
                "description": "Default token budget limit per entry (default: 10000, overridden by budgets param)"
            },
            "budgets": {
                "type": "object",
                "description": "Per-entry budget overrides (e.g., {'user-current-state': 15000, 'user-biographical': 5000})"
            }
        }
    }
)

# =============================================================================
# Implementation
# =============================================================================

async def execute(con, args: dict) -> List[TextContent]:
    """Check KB entry token budgets against limits with per-entry budget allocation"""

    # Parse arguments
    entry_ids = args.get("entry_ids", [
        "user-current-state",
        "user-biographical",
        "arlo-current-state",
        "arlo-biographical"
    ])
    default_budget = args.get("budget", 10000)
    per_entry_budgets = args.get("budgets", {})

    # Default budget allocation (10K/10K/10K/10K)
    DEFAULT_BUDGETS = {
        "user-current-state": 10000,
        "user-biographical": 10000,
        "arlo-current-state": 10000,
        "arlo-biographical": 10000
    }

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

        # Determine budget for this entry (priority: per_entry_budgets > DEFAULT_BUDGETS > default_budget)
        if per_entry_budgets and entry_id in per_entry_budgets:
            budget = per_entry_budgets[entry_id]
        elif entry_id in DEFAULT_BUDGETS:
            budget = DEFAULT_BUDGETS[entry_id]
        else:
            budget = default_budget

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
        "budget_allocation": "10K/10K/10K/10K (current-state/biographical/current-state/biographical)",
        "note": "If over_budget, apply offloading protocol per KB-BASE.md 'Autonomous Offload at Cap'"
    }

    return [TextContent(type="text", text=json.dumps(response))]

# =============================================================================
# Metadata
# =============================================================================

REQUIRES_DB = True
