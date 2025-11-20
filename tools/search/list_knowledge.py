"""List knowledge entries with optional filters"""

from mcp.types import Tool, TextContent
from typing import List, Optional
import json

# =============================================================================
# Tool Definition (for registration)
# =============================================================================

TOOL = Tool(
    name="list_knowledge",
    description="""List knowledge entries with optional filters. Good for browsing by category, tags, or date range.

WHEN TO USE: Browsing without semantic search, exact tag/category filtering, getting recent entries.
BEST FOR: "Show me all commands" or "List recent troubleshooting entries"
NOT FOR: Conceptual search (use find_similar) or complex queries (use query_knowledge)
TIP: Returns previews only - use get_knowledge() to get full content.""",
    inputSchema={
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "description": "Filter by category (table, command, issue, pattern, troubleshooting, etc.)",
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Filter by tags (matches if entry has ANY of these tags)"
            },
            "date_after": {
                "type": "string",
                "description": "ISO timestamp - only entries updated after this date"
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of results (default: 20)",
                "default": 20
            },
            "offset": {
                "type": "integer",
                "description": "Skip this many results (for pagination)",
                "default": 0
            }
        }
    }
)

# =============================================================================
# Implementation
# =============================================================================

async def execute(con, args: dict) -> List[TextContent]:
    """List knowledge entries with filters"""
    category = args.get("category")
    tags = args.get("tags")
    # Normalize tag filters to match DB normalization
    if tags:
        tags = [tag.lower().strip() for tag in tags]
    date_after = args.get("date_after")
    limit = args.get("limit", 20)
    offset = args.get("offset", 0)

    # Build query dynamically
    where_clauses = []
    params = []

    if category:
        where_clauses.append("category = ?")
        params.append(category)

    if tags:
        where_clauses.append("list_has_any(tags, ?)")
        params.append(tags)

    if date_after:
        where_clauses.append("updated > ?")
        params.append(date_after)

    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

    sql = f"""
        SELECT id, category, title, tags,
               left(content, 300) as preview,
               updated
        FROM knowledge
        WHERE {where_sql}
        ORDER BY updated DESC
        LIMIT ? OFFSET ?
    """

    params.extend([limit, offset])

    results = con.execute(sql, params).fetchall()
    cols = [desc[0] for desc in con.description]

    entries = [dict(zip(cols, row)) for row in results]

    return [TextContent(type="text", text=json.dumps(entries, default=str))]

# =============================================================================
# Metadata
# =============================================================================

REQUIRES_DB = True
