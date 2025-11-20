"""Check for duplicate KB entries using single-pass semantic search

Implements deterministic duplicate detection protocol:
- Single pass: similarity >= 0.65 (catches duplicates and consolidation candidates)

Always run before creating new KB entries to avoid fragmentation.
"""

from mcp.types import Tool, TextContent
from typing import List, Dict, Any
import json
from tools.base import generate_embedding, DEFAULT_SIMILARITY_THRESHOLD

# =============================================================================
# Tool Definition (for registration)
# =============================================================================

TOOL = Tool(
    name="check_duplicates",
    description="""Check for duplicate KB entries using single-pass semantic search.

WHEN TO USE: Before creating any KB entry, integrated with upsert workflows
PROTOCOL:
- Single pass: similarity >= 0.65 (catches duplicates and consolidation candidates)

Returns matches, recommendation, and next_steps.""",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Entry title or content to check for duplicates"
            },
            "category": {
                "type": "string",
                "description": "Optional: limit search to this category"
            }
        },
        "required": ["query"]
    }
)

# =============================================================================
# Implementation
# =============================================================================

async def execute(con, args: dict) -> List[TextContent]:
    """Execute single-pass duplicate detection"""

    query = args["query"]
    category = args.get("category")

    # Generate embedding for query
    query_embedding = generate_embedding(query)

    # Single pass: similarity >= 0.65
    matches = await _search_pass(
        con,
        query_embedding,
        category,
        similarity_threshold=0.65,
        limit=10
    )

    # Build recommendation
    recommendation, next_steps = _build_recommendation(matches)

    response = {
        "matches": matches,
        "recommendation": recommendation,
        "next_steps": next_steps,
        "query": query,
        "category": category
    }

    return [TextContent(type="text", text=json.dumps(response, indent=2))]


async def _search_pass(con, query_embedding: List[float], category: str, similarity_threshold: float, limit: int) -> List[Dict[str, Any]]:
    """Execute a single search pass"""

    # Build SQL query
    sql = """
        SELECT
            id,
            title,
            category,
            array_cosine_similarity(embedding, ?::FLOAT[3072]) as similarity
        FROM knowledge
        WHERE embedding IS NOT NULL
    """

    params = [query_embedding]

    if category:
        sql += " AND category = ?"
        params.append(category)

    sql += """
        AND array_cosine_similarity(embedding, ?::FLOAT[3072]) >= ?
        ORDER BY similarity DESC
        LIMIT ?
    """
    params.extend([query_embedding, similarity_threshold, limit])

    try:
        results = con.execute(sql, params).fetchall()
    except Exception as e:
        # VSS not available or embedding error
        return []

    matches = []
    for row in results:
        matches.append({
            "id": row[0],
            "title": row[1],
            "category": row[2],
            "similarity": round(row[3], 3)
        })

    return matches


def _build_recommendation(matches: List) -> tuple:
    """Build recommendation and next steps based on results"""

    if matches:
        recommendation = "⚠️ SIMILAR ENTRIES FOUND (similarity >= 0.65)"
        next_steps = [
            "Show user the similar entries with IDs, titles, and similarity scores",
            "User decides: update existing entry OR create new entry",
            "High similarity (0.85+): Strong duplicate candidate - recommend updating existing",
            "Medium similarity (0.65-0.84): Related content - user discretion"
        ]
    else:
        recommendation = "✅ NO DUPLICATES FOUND - Safe to create"
        next_steps = [
            "No similar entries detected (similarity < 0.65)",
            "Proceed with KB entry creation"
        ]

    return recommendation, next_steps

# =============================================================================
# Metadata
# =============================================================================

REQUIRES_DB = True
