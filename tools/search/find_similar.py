"""Find semantically similar knowledge entries"""

from mcp.types import Tool, TextContent
from typing import List, Optional
import json
from tools.base import generate_embedding, DEFAULT_SIMILARITY_THRESHOLD

# =============================================================================
# Tool Definition (for registration)
# =============================================================================

TOOL = Tool(
    name="find_similar",
    description="""Find knowledge entries semantically similar to a query using embeddings. Searches by meaning/concept, not just keywords. Use to identify duplicate or related entries (set similarity_threshold=0.8+ for near-duplicates). Helpful for consolidation efforts.

WHEN TO USE: Conceptual/semantic search, finding related content, checking for duplicates.
BEST FOR: "Find entries about error handling" or "What's similar to this concept?"
NOT FOR: Exact keyword matching (use query_knowledge with LIKE) or browsing (use list_knowledge)
THRESHOLDS: 0.9+=duplicates, 0.7-0.9=related, 0.5-0.7=loosely related, <0.5=unrelated
TIP: Start with threshold=0.5, adjust based on results. Lower=more results, higher=more precise.""",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Natural language query describing what to find"
            },
            "category": {
                "type": "string",
                "description": "Optional: limit search to this category"
            },
            "similarity_threshold": {
                "type": "number",
                "description": f"Minimum cosine similarity (0-1, default: {DEFAULT_SIMILARITY_THRESHOLD})",
                "default": DEFAULT_SIMILARITY_THRESHOLD
            },
            "limit": {
                "type": "integer",
                "description": "Maximum results (default: 10)",
                "default": 10
            }
        },
        "required": ["query"]
    }
)

# =============================================================================
# Implementation
# =============================================================================

async def execute(con, args: dict) -> List[TextContent]:
    """Find semantically similar entries"""
    query = args["query"]
    category = args.get("category")
    threshold = args.get("similarity_threshold", DEFAULT_SIMILARITY_THRESHOLD)
    limit = args.get("limit", 10)

    # Generate query embedding
    try:
        query_embedding = generate_embedding(query)
        # Cast to FLOAT array for DuckDB compatibility
        query_embedding = [float(x) for x in query_embedding]
    except Exception as e:
        return [TextContent(type="text", text=f"Error generating embedding: {str(e)}\nInstall: pip install sentence-transformers")]

    # Execute semantic search (Python implementation - no macro dependency)
    if category:
        sql = """
            SELECT
                id,
                category,
                title,
                tags,
                content,
                metadata,
                array_cosine_similarity(embedding, CAST(? AS FLOAT[3072])) as similarity,
                updated
            FROM knowledge
            WHERE
                embedding IS NOT NULL
                AND category = ?
                AND array_cosine_similarity(embedding, CAST(? AS FLOAT[3072])) > ?
            ORDER BY similarity DESC
            LIMIT ?
        """
        params = [query_embedding, category, query_embedding, threshold, limit]
    else:
        sql = """
            SELECT
                id,
                category,
                title,
                tags,
                content,
                metadata,
                array_cosine_similarity(embedding, CAST(? AS FLOAT[3072])) as similarity,
                updated
            FROM knowledge
            WHERE
                embedding IS NOT NULL
                AND array_cosine_similarity(embedding, CAST(? AS FLOAT[3072])) > ?
            ORDER BY similarity DESC
            LIMIT ?
        """
        params = [query_embedding, query_embedding, threshold, limit]

    results = con.execute(sql, params).fetchall()
    cols = [desc[0] for desc in con.description]

    entries = []
    for row in results:
        entry = dict(zip(cols, row))
        # Truncate content for readability
        if 'content' in entry and len(entry['content']) > 300:
            entry['preview'] = entry['content'][:300] + "..."
            del entry['content']
        if 'embedding' in entry:
            del entry['embedding']
        entries.append(entry)

    # Detect pattern emergence - find clusters of highly similar entries
    clusters = []
    if len(entries) >= 3:  # Only look for clusters if we have enough results
        # Group entries by high similarity (>0.8)
        high_similarity_threshold = 0.8
        for i, entry in enumerate(entries):
            if 'similarity' in entry and entry['similarity'] > high_similarity_threshold:
                # Find all entries with similarity above threshold
                cluster_entries = [e for e in entries if 'similarity' in e and e['similarity'] > high_similarity_threshold]
                if len(cluster_entries) >= 3:
                    clusters.append({
                        "count": len(cluster_entries),
                        "avg_similarity": round(sum(e['similarity'] for e in cluster_entries) / len(cluster_entries), 3),
                        "ids": [e['id'] for e in cluster_entries],
                        "signal": "consolidation_candidate" if len(cluster_entries) >= 4 else "emerging_pattern"
                    })
                    break  # Only report the first cluster found

    # Build response with optional clustering info
    response = {"results": entries}
    if clusters:
        response["clusters"] = clusters
        response["recommendation"] = f"Found {clusters[0]['count']} highly similar entries (similarity>{high_similarity_threshold}). Consider consolidating into a meta-pattern."

    return [TextContent(type="text", text=json.dumps(response, default=str))]

# =============================================================================
# Metadata
# =============================================================================

REQUIRES_DB = True
