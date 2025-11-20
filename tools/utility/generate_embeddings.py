"""Generate embeddings for knowledge entries"""

from mcp.types import Tool, TextContent
from typing import List
import json
from datetime import datetime
from tools.base import EMBEDDINGS_AVAILABLE, generate_embeddings_batch, EMBEDDING_MODEL

# =============================================================================
# Tool Definition (for registration)
# =============================================================================

TOOL = Tool(
    name="generate_embeddings",
    description="""Generate embeddings for entries that don't have them yet. Uses OpenAI text-embedding-3-large (3072 dimensions) by default. Falls back to local model if OpenAI unavailable. Requires network connectivity.

WHEN TO USE: After bulk imports, when entries missing embeddings, after restoring from backup.
COST: ~$0.00002 per 1K tokens (~$0.001 for 100 entries)
TIP: Set regenerate=false (default) to only generate missing embeddings, not replace existing. Returns count of entries processed, no pre-check needed.""",
    inputSchema={
        "type": "object",
        "properties": {
            "ids": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Specific entry IDs to generate embeddings for (optional - generates for all missing if not specified)"
            },
            "regenerate": {
                "type": "boolean",
                "description": "Regenerate embeddings even if they already exist (default: false)",
                "default": False
            },
            "batch_size": {
                "type": "integer",
                "description": "Number of entries to process at once (default: 32)",
                "default": 32
            }
        }
    }
)

# =============================================================================
# Implementation
# =============================================================================

async def execute(con, args: dict) -> List[TextContent]:
    """Generate embeddings for entries"""
    ids = args.get("ids")
    regenerate = args.get("regenerate", False)
    batch_size = args.get("batch_size", 32)

    if not EMBEDDINGS_AVAILABLE:
        return [TextContent(type="text", text="Error: OPENAI_API_KEY not set.\nRun: export OPENAI_API_KEY='sk-...'")]

    # Find entries needing embeddings
    if ids:
        where = f"id IN ({','.join(['?'] * len(ids))})"
        params = ids
    elif regenerate:
        where = "1=1"
        params = []
    else:
        where = "embedding IS NULL"
        params = []

    sql = f"""
        SELECT id, title, tags, content
        FROM knowledge
        WHERE {where}
    """

    entries = con.execute(sql, params).fetchall()

    if not entries:
        return [TextContent(type="text", text="No entries need embeddings")]

    # Generate embeddings in batches
    total = len(entries)
    updated = 0

    for i in range(0, total, batch_size):
        batch = entries[i:i+batch_size]

        # Create rich embedding text for each entry
        texts = [
            f"Title: {row[1]}\nTags: {', '.join(row[2])}\nContent: {row[3]}"
            for row in batch
        ]

        # Generate batch embeddings (uses GPU on M2 Max!)
        embeddings = generate_embeddings_batch(texts)

        # Update database
        now = datetime.now()
        for (entry_id, _, _, _), embedding in zip(batch, embeddings):
            # Cast to FLOAT array for DuckDB compatibility
            embedding = [float(x) for x in embedding]
            con.execute(
                "UPDATE knowledge SET embedding = ?, updated = ? WHERE id = ?",
                [embedding, now, entry_id]
            )
            updated += 1

    # Note: EMBEDDING_PROVIDER and LOCAL_MODEL/LOCAL_DIM are not in base.py
    # Using OpenAI values directly since that's what we're using
    provider = "OpenAI"
    model = EMBEDDING_MODEL
    dims = 3072  # EMBEDDING_DIM from base.py

    return [TextContent(type="text", text=json.dumps({
        "status": "success",
        "total_entries": total,
        "updated": updated,
        "provider": provider,
        "model": model,
        "dimensions": dims
    }))]

# =============================================================================
# Metadata
# =============================================================================

REQUIRES_DB = True
