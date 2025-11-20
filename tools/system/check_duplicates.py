"""Check for duplicate KB entries using two-pass semantic search

Implements deterministic duplicate detection protocol:
- Pass 1: Strict check (similarity >= 0.75) - high confidence duplicates
- Pass 2: Fallback check (similarity >= 0.3) - conceptually related entries

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
    description="""Check for duplicate KB entries using two-pass semantic search.

WHEN TO USE: Before creating any KB entry, integrated with upsert workflows
PROTOCOL:
- Pass 1: Strict check (similarity >= 0.75) - high confidence duplicates
- Pass 2: Fallback check (similarity >= 0.3) - conceptually related entries

Returns strict_match, possible_match, recommendation, and next_steps.""",
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
            },
            "return_mode": {
                "type": "string",
                "enum": ["strict", "all"],
                "default": "all",
                "description": "strict=0.75+ only, all=both passes (default: all)"
            }
        },
        "required": ["query"]
    }
)

# =============================================================================
# Implementation
# =============================================================================

async def execute(con, args: dict) -> List[TextContent]:
    """Execute two-pass duplicate detection"""

    query = args["query"]
    category = args.get("category")
    return_mode = args.get("return_mode", "all")

    # Generate embedding for query
    query_embedding = generate_embedding(query)

    # Pass 1: Strict check (similarity >= 0.75)
    strict_matches = await _search_pass(
        con,
        query_embedding,
        category,
        similarity_threshold=0.75,
        limit=5
    )

    # Pass 2: Fallback check (similarity >= 0.3) - only if strict found nothing
    possible_matches = []
    if not strict_matches and return_mode == "all":
        possible_matches = await _search_pass(
            con,
            query_embedding,
            category,
            similarity_threshold=0.3,
            limit=10
        )

    # Build recommendation
    recommendation, next_steps = _build_recommendation(strict_matches, possible_matches)

    response = {
        "strict_match": strict_matches,
        "possible_match": possible_matches if return_mode == "all" else [],
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


def _build_recommendation(strict_matches: List, possible_matches: List) -> tuple:
    """Build recommendation and next steps based on results"""

    if strict_matches:
        recommendation = "⚠️ HIGH CONFIDENCE DUPLICATES FOUND (similarity >= 0.75)"
        next_steps = [
            "MUST show user the duplicates and get explicit approval before proceeding",
            "Display: entry IDs, titles, similarity scores",
            "Wait for user decision: update existing vs. create new",
            "DO NOT create new entry without user approval"
        ]
    elif possible_matches:
        recommendation = "ℹ️ POSSIBLE RELATED ENTRIES FOUND (similarity >= 0.3)"
        next_steps = [
            "Show user the related entries",
            "Suggest consolidation if appropriate",
            "User can proceed with creation or consolidate existing",
            "Safe to create if user confirms intent"
        ]
    else:
        recommendation = "✅ NO DUPLICATES FOUND - Safe to create"
        next_steps = [
            "No similar entries detected",
            "Proceed with KB entry creation"
        ]

    return recommendation, next_steps

# =============================================================================
# Metadata
# =============================================================================

REQUIRES_DB = True
