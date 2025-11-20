"""Import knowledge base from markdown backup files"""

from mcp.types import Tool, TextContent
from typing import List
import json
import os
import yaml
import re
from pathlib import Path
from tools.base import generate_embedding

# =============================================================================
# Tool Definition (for registration)
# =============================================================================

TOOL = Tool(
    name="import_from_markdown",
    description="""RESTORE: Restore KB from markdown backup. This is for DISASTER RECOVERY and MIGRATION only.

IMPORTANT: Markdown exports are BACKUPS, not a bi-directional sync. The DuckDB KB (via MCP) is the single source of truth for read/write operations. Only use this tool to restore after data loss or migrate to a new system.

WHEN TO USE: Disaster recovery (DB corrupted), migrate to new machine, testing (tear-down/restore)
DO NOT USE FOR: Importing manual edits to markdown files (markdown exports are read-only for humans)
PROCESS: Always upserts (inserts new, updates existing), recreates links, regenerates embeddings
TIP: Run get_stats() before/after to verify restore""",
    inputSchema={
        "type": "object",
        "properties": {
            "input_dir": {
                "type": "string",
                "description": "Directory with markdown backup files (e.g., '~/duckdb-kb/backup')"
            },
            "generate_embeddings": {
                "type": "boolean",
                "description": "Generate embeddings after import (default: true for disaster recovery)",
                "default": True
            },
            "category": {
                "type": "string",
                "description": "Optional: Only import files from this category subdirectory"
            }
        },
        "required": ["input_dir"]
    }
)

# =============================================================================
# Implementation
# =============================================================================

async def execute(con, args: dict) -> List[TextContent]:
    """Restore KB entries from markdown backup (disaster recovery/migration only)"""
    input_dir = Path(os.path.expanduser(args["input_dir"]))
    generate_embeddings_flag = args.get("generate_embeddings", True)
    category_filter = args.get("category")

    if not input_dir.exists():
        return [TextContent(type="text", text=f"Error: Directory not found: {input_dir}")]

    # Find all markdown files
    if category_filter:
        cat_dir = input_dir / category_filter
        if not cat_dir.exists():
            return [TextContent(type="text", text=f"Error: Category directory not found: {cat_dir}")]
        md_files = list(cat_dir.glob("*.md"))
    else:
        md_files = list(input_dir.rglob("*.md"))

    if not md_files:
        return [TextContent(type="text", text=f"No markdown files found in {input_dir}")]

    imported_count = 0  # New entries inserted
    updated_count = 0   # Existing entries updated
    skipped_count = 0   # Invalid/malformed files

    for md_file in md_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse YAML frontmatter
            if not content.startswith('---'):
                skipped_count += 1
                continue

            # Extract frontmatter
            parts = content.split('---', 2)
            if len(parts) < 3:
                skipped_count += 1
                continue

            frontmatter = yaml.safe_load(parts[1])
            body = parts[2].strip()

            # Extract content (remove title section)
            # Remove first H1 (title) - handle both \n\n and single \n
            body = re.sub(r'^#\s+.*?\n+', '', body, count=1)

            # Remove ALL metadata footers (there may be multiple from previous cycles)
            # Keep removing until no more matches found (handles interleaved footers)
            while re.search(r'\n+---\s*\n+\*KB Entry:.*?\*', body, flags=re.DOTALL):
                body = re.sub(r'\n+---\s*\n+\*KB Entry:.*?\*\s*', '', body, flags=re.DOTALL)

            # Clean up any trailing --- separators
            body = re.sub(r'\n+---\s*$', '', body)

            # Prepare data
            entry_id = frontmatter['id']
            category = frontmatter.get('category', 'other')
            title = frontmatter['title']
            tags = frontmatter.get('tags', [])
            metadata = json.dumps(frontmatter.get('metadata')) if frontmatter.get('metadata') else None
            created = frontmatter.get('created')
            updated = frontmatter.get('updated')

            # Check if entry exists (for counting purposes)
            existing = con.execute("SELECT id FROM knowledge WHERE id = ?", [entry_id]).fetchone()

            # Always UPSERT (insert if new, update if exists)
            # This is a restore operation - always overwrite
            if existing:
                con.execute("""
                    UPDATE knowledge
                    SET category = ?, title = ?, content = ?, tags = ?, metadata = ?, updated = ?
                    WHERE id = ?
                """, [category, title, body.strip(), tags, metadata, updated, entry_id])
                updated_count += 1
            else:
                con.execute("""
                    INSERT INTO knowledge (id, category, title, content, tags, metadata, created, updated, embedding)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL)
                """, [entry_id, category, title, body.strip(), tags, metadata, created, updated])
                imported_count += 1

        except Exception as e:
            return [TextContent(type="text", text=f"Error processing {md_file.name}: {str(e)}")]

    # Generate embeddings if requested
    embeddings_generated = 0
    if generate_embeddings_flag and (imported_count > 0 or updated_count > 0):
        # Get entries without embeddings
        no_embed = con.execute("SELECT id, title, tags, content FROM knowledge WHERE embedding IS NULL").fetchall()

        for entry_id, title, tags, content in no_embed:
            if content:
                try:
                    # Create rich embedding text (same as upsert_knowledge)
                    embed_text = f"Title: {title}\nTags: {', '.join(tags)}\nContent: {content}"
                    embedding = generate_embedding(embed_text)
                    # Cast to FLOAT array for DuckDB compatibility
                    embedding = [float(x) for x in embedding]
                    con.execute("UPDATE knowledge SET embedding = ? WHERE id = ?", [embedding, entry_id])
                    embeddings_generated += 1
                except Exception as e:
                    # Continue on error, don't fail entire import
                    pass  # Failed to generate embedding
                    pass

    summary = f"✓ Restore complete!\n\n"
    summary += f"New entries: {imported_count}\n"
    summary += f"Updated entries: {updated_count}\n"
    if skipped_count > 0:
        summary += f"Skipped: {skipped_count} files (invalid/malformed)\n"
    if generate_embeddings_flag:
        summary += f"Embeddings generated: {embeddings_generated}\n"
    summary += f"\nRestored from: {input_dir}"

    return [TextContent(type="text", text=summary)]

# =============================================================================
# Metadata
# =============================================================================

REQUIRES_DB = True
