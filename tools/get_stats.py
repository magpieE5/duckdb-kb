"""Get KB statistics tool."""
from typing import List
from mcp.types import Tool, TextContent

from .base import json_response

TOOL_DEF = Tool(
    name="get_stats",
    description="Get KB statistics (entry counts, categories, tag usage).",
    inputSchema={
        "type": "object",
        "properties": {
            "detailed": {"type": "boolean", "description": "Include detailed breakdown (default: false)", "default": False}
        }
    }
)

REQUIRES_DB = True


async def execute(con, args: dict) -> List[TextContent]:
    detailed = args.get("detailed", False)

    summary_data = []
    total = con.execute("SELECT COUNT(*) FROM knowledge").fetchone()[0]
    summary_data.append(('Total Entries', str(total)))

    categories_count = con.execute("SELECT COUNT(DISTINCT category) FROM knowledge").fetchone()[0]
    summary_data.append(('Categories', str(categories_count)))

    tags_count = con.execute("SELECT COUNT(DISTINCT t.tag) FROM knowledge k, UNNEST(k.tags) AS t(tag)").fetchone()[0]
    summary_data.append(('Unique Tags', str(tags_count)))

    stats = {"summary": {row[0]: row[1] for row in summary_data}}

    if detailed:
        categories = con.execute("""
            SELECT category, COUNT(*) as count, MIN(created) as oldest, MAX(updated) as newest
            FROM knowledge
            GROUP BY category
            ORDER BY count DESC
        """).fetchall()
        stats["by_category"] = [
            {"category": row[0], "count": row[1], "oldest": str(row[2]), "newest": str(row[3])}
            for row in categories
        ]

        tags = con.execute("""
            SELECT t.tag, COUNT(*) as usage, LIST(DISTINCT k.category) as categories
            FROM knowledge k, UNNEST(k.tags) AS t(tag)
            GROUP BY t.tag
            ORDER BY usage DESC
            LIMIT 20
        """).fetchall()
        stats["top_tags"] = [
            {"tag": row[0], "count": row[1], "categories": row[2]}
            for row in tags
        ]

    return json_response(stats)
