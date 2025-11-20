"""Create or update knowledge entries with duplicate detection"""

from mcp.types import Tool, TextContent
from typing import List
import json
from datetime import datetime
from tools.base import generate_embedding, EMBEDDINGS_AVAILABLE

# =============================================================================
# Tool Definition (for registration)
# =============================================================================

TOOL = Tool(
    name="upsert_knowledge",
    description="""Create a new knowledge entry or update existing one. Automatically generates embedding if content is provided.

DUPLICATE DETECTION: By default, automatically checks for similar entries (similarity >= 0.75) before saving. If duplicates found, returns warning without saving - you can then update existing entry or force create. This prevents fragmentation and ensures knowledge base quality.

WHEN TO USE: Saving valuable knowledge, fixing/updating entries, consolidating duplicates.
WORKFLOW (AUTOMATIC): 1) Duplicate check runs automatically, 2) If similar found, returns warning with options, 3) You decide: update existing or force_create=True
ID FORMAT: Use kebab-case like 'pattern-topic-specifics' or 'troubleshooting-issue-name'
TAGS: Include 4-6 relevant tags + layer tag (layer:base, layer:team, or layer:personal)

PARAMETERS:
- check_duplicates (default: true): Automatically search for similar entries before saving
- force_create (default: false): Skip duplicate check and save anyway
- similarity_threshold (default: 0.75): Minimum similarity to flag duplicates (0.0-1.0)""",
    inputSchema={
        "type": "object",
        "properties": {
            "id": {
                "type": "string",
                "description": "Unique identifier (e.g., 'pattern-caching-strategy', 'issue-bug-123')"
            },
            "category": {
                "type": "string",
                "description": "Category: table, command, issue, pattern, troubleshooting, reference, other"
            },
            "title": {
                "type": "string",
                "description": "Human-readable title"
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of tags for categorization"
            },
            "content": {
                "type": "string",
                "description": "Main content (markdown supported)"
            },
            "metadata": {
                "type": "object",
                "description": "Additional structured data (JSON object)"
            },
            "generate_embedding": {
                "type": "boolean",
                "description": "Auto-generate embedding from content (default: true)",
                "default": True
            },
            "check_duplicates": {
                "type": "boolean",
                "description": "Check for similar entries before saving (default: true)",
                "default": True
            },
            "force_create": {
                "type": "boolean",
                "description": "Skip duplicate check and save anyway (default: false)",
                "default": False
            },
            "similarity_threshold": {
                "type": "number",
                "description": "Minimum similarity score to flag duplicates, 0.0-1.0 (default: 0.75)",
                "default": 0.75,
                "minimum": 0.0,
                "maximum": 1.0
            }
        },
        "required": ["id", "category", "title", "content"]
    }
)

# =============================================================================
# Implementation
# =============================================================================

async def execute(con, args: dict) -> List[TextContent]:
    """Create or update knowledge entry"""
    entry_id = args["id"]
    category = args["category"]
    title = args["title"]
    content = args["content"]
    tags = args.get("tags", [])
    # Normalize tags: lowercase + trim whitespace for consistent matching
    tags = [tag.lower().strip() for tag in tags]
    metadata = args.get("metadata", {})
    generate_emb = args.get("generate_embedding", True)

    # New duplicate detection parameters
    check_duplicates = args.get("check_duplicates", True)
    force_create = args.get("force_create", False)
    similarity_threshold = args.get("similarity_threshold", 0.75)

    # Check if entry already exists (this is an update)
    existing = con.execute("SELECT 1 FROM knowledge WHERE id = ?", [entry_id]).fetchone()

    # Skip duplicate check if:
    # - force_create is True
    # - Entry already exists (this is an update)
    # - No embeddings available
    # - check_duplicates is False
    skip_check = force_create or existing or not EMBEDDINGS_AVAILABLE or not check_duplicates

    # Generate embedding (needed for both duplicate check and save)
    embedding = None
    if generate_emb and EMBEDDINGS_AVAILABLE:
        try:
            # Create rich text for embedding (includes title + tags + content)
            embed_text = f"Title: {title}\nTags: {', '.join(tags)}\nContent: {content}"
            embedding = generate_embedding(embed_text)
            # Cast to FLOAT array for DuckDB compatibility
            embedding = [float(x) for x in embedding]
        except Exception as e:
            # Continue without embedding if generation fails
            pass

    # Duplicate detection (pre-flight check)
    if not skip_check and embedding is not None:
        try:
            similar = con.execute("""
                SELECT
                    id,
                    title,
                    array_cosine_similarity(embedding, ?::FLOAT[3072]) as similarity,
                    created,
                    tags
                FROM knowledge
                WHERE embedding IS NOT NULL
                    AND id != ?
                    AND array_cosine_similarity(embedding, ?::FLOAT[3072]) >= ?
                ORDER BY similarity DESC
                LIMIT 5
            """, [embedding, entry_id, embedding, similarity_threshold]).fetchall()

            if similar:
                # Return duplicate warning without saving
                similar_entries = [
                    {
                        "id": row[0],
                        "title": row[1],
                        "similarity": round(row[2], 3),
                        "created": str(row[3]),
                        "tags": row[4]
                    }
                    for row in similar
                ]

                return [TextContent(type="text", text=json.dumps({
                    "status": "duplicate_check",
                    "saved": False,
                    "similar_entries": similar_entries,
                    "recommendation": f"Found {len(similar)} similar entries (threshold: {similarity_threshold})",
                    "next_steps": [
                        f"Update existing: upsert_knowledge(id='{similar[0][0]}', ...)",
                        "Create anyway: upsert_knowledge(..., force_create=True)",
                        f"Stricter match: upsert_knowledge(..., similarity_threshold={min(0.95, round(similarity_threshold + 0.1, 2))})",
                        f"Cast wider net: smart_search(query='...', similarity_threshold={max(0.5, round(similarity_threshold - 0.2, 2))})"
                    ]
                }))]
        except Exception as e:
            # If duplicate check fails, proceed with save (fail-open)
            pass

    # Upsert - get current timestamp as Python datetime
    now = datetime.now()

    # Use different SQL depending on whether we have an embedding
    # (COALESCE doesn't work with FLOAT arrays in DuckDB)
    if embedding is not None:
        con.execute("""
            INSERT INTO knowledge (id, category, title, tags, content, metadata, embedding, created, updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (id) DO UPDATE SET
                category = EXCLUDED.category,
                title = EXCLUDED.title,
                tags = EXCLUDED.tags,
                content = EXCLUDED.content,
                metadata = EXCLUDED.metadata,
                embedding = EXCLUDED.embedding,
                updated = ?
        """, [entry_id, category, title, tags, content, metadata, embedding, now, now, now])
    else:
        con.execute("""
            INSERT INTO knowledge (id, category, title, tags, content, metadata, created, updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (id) DO UPDATE SET
                category = EXCLUDED.category,
                title = EXCLUDED.title,
                tags = EXCLUDED.tags,
                content = EXCLUDED.content,
                metadata = EXCLUDED.metadata,
                updated = ?
        """, [entry_id, category, title, tags, content, metadata, now, now, now])

    return [TextContent(type="text", text=json.dumps({
        "id": entry_id,
        "embedding_generated": embedding is not None
    }))]

# =============================================================================
# Metadata
# =============================================================================

REQUIRES_DB = True
