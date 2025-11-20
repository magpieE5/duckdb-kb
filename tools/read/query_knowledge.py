"""Execute custom SQL queries on the knowledge database"""

from mcp.types import Tool, TextContent
from typing import List
import json

# =============================================================================
# Tool Definition (for registration)
# =============================================================================

TOOL = Tool(
    name="query_knowledge",
    description="""Execute a custom SQL query on the knowledge database. Use for complex filtering, aggregations, or joins. The main table is 'knowledge' with columns: id, category, title, tags, content, metadata, embedding, created, updated.

WHEN TO USE: Complex analytics, aggregations, custom filtering logic not available in other tools.
BEST FOR: "Count entries by category", "Find entries with specific tag combinations", "Analyze tag usage"
NOT FOR: Semantic search (use find_similar) or simple filtering (use list_knowledge)
EXAMPLE: query_knowledge({"sql": "SELECT category, COUNT(*) FROM knowledge GROUP BY category"})""",
    inputSchema={
        "type": "object",
        "properties": {
            "sql": {
                "type": "string",
                "description": "SQL query to execute (SELECT only)"
            }
        },
        "required": ["sql"]
    }
)

# =============================================================================
# Implementation
# =============================================================================

async def execute(con, args: dict) -> List[TextContent]:
    """Execute custom SQL query (SELECT only)"""
    sql = args["sql"]

    # Security: Only allow SELECT
    if not sql.strip().upper().startswith("SELECT"):
        return [TextContent(type="text", text="Error: Only SELECT queries allowed")]

    try:
        results = con.execute(sql).fetchall()
        cols = [desc[0] for desc in con.description]

        # Format as list of dicts
        rows = [dict(zip(cols, row)) for row in results]

        return [TextContent(type="text", text=json.dumps(rows, default=str))]

    except Exception as e:
        return [TextContent(type="text", text=f"SQL Error: {str(e)}")]

# =============================================================================
# Metadata
# =============================================================================

REQUIRES_DB = True
