"""Get database statistics and metadata"""

from mcp.types import Tool, TextContent
from typing import List
import json

# =============================================================================
# Tool Definition (for registration)
# =============================================================================

TOOL = Tool(
    name="get_stats",
    description="""Get database statistics including entry counts by category, embedding status, tag usage, etc.

WHEN TO USE: First time connecting, health checks, understanding KB contents, planning maintenance.
RETURNS: Entry counts, categories, embedding coverage, top tags
**RECOMMENDED**: Run this first when connecting to understand what's in the knowledge base!
TIP: Use detailed=true for category breakdowns and tag analysis.""",
    inputSchema={
        "type": "object",
        "properties": {
            "detailed": {
                "type": "boolean",
                "description": "Include detailed breakdown (default: false)",
                "default": False
            }
        }
    }
)

# =============================================================================
# Implementation
# =============================================================================

async def execute(con, args: dict) -> List[TextContent]:
    """Get database statistics"""
    detailed = args.get("detailed", False)

    # Basic summary (Python implementation - no macro dependency)
    summary_data = []

    # Total entries
    total = con.execute("SELECT COUNT(*) FROM knowledge").fetchone()[0]
    summary_data.append(('Total Entries', str(total)))

    # With embeddings
    with_emb = con.execute("SELECT COUNT(*) FROM knowledge WHERE embedding IS NOT NULL").fetchone()[0]
    summary_data.append(('With Embeddings', str(with_emb)))

    # Categories
    categories_count = con.execute("SELECT COUNT(DISTINCT category) FROM knowledge").fetchone()[0]
    summary_data.append(('Categories', str(categories_count)))

    # Unique tags
    tags_count = con.execute("""
        SELECT COUNT(DISTINCT t.tag)
        FROM knowledge k, UNNEST(k.tags) AS t(tag)
    """).fetchone()[0]
    summary_data.append(('Unique Tags', str(tags_count)))

    stats = {
        "summary": {row[0]: row[1] for row in summary_data}
    }

    if detailed:
        # Category breakdown (Python implementation)
        categories = con.execute("""
            SELECT
                category,
                COUNT(*) as count,
                COUNT(embedding) as embeddings_generated,
                ROUND(100.0 * COUNT(embedding) / COUNT(*), 1) as embedding_pct,
                MIN(created) as oldest,
                MAX(updated) as newest
            FROM knowledge
            GROUP BY category
            ORDER BY count DESC
        """).fetchall()

        stats["by_category"] = [
            {
                "category": row[0],
                "count": row[1],
                "embeddings_generated": row[2],
                "embedding_pct": row[3],
                "oldest": str(row[4]),
                "newest": str(row[5])
            }
            for row in categories
        ]

        # Tag usage (Python implementation)
        tags = con.execute("""
            SELECT
                t.tag,
                COUNT(*) as usage,
                LIST(DISTINCT k.category) as categories
            FROM knowledge k, UNNEST(k.tags) AS t(tag)
            GROUP BY t.tag
            ORDER BY usage DESC
            LIMIT 20
        """).fetchall()

        stats["top_tags"] = [
            {"tag": row[0], "count": row[1], "categories": row[2]}
            for row in tags
        ]

    return [TextContent(type="text", text=json.dumps(stats, default=str))]

# =============================================================================
# Metadata
# =============================================================================

REQUIRES_DB = True
