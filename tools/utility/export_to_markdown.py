"""Export knowledge base to markdown files"""

from mcp.types import Tool, TextContent
from typing import List
import json
import os
import yaml
from pathlib import Path

# =============================================================================
# Tool Definition (for registration)
# =============================================================================

TOOL = Tool(
    name="export_to_markdown",
    description="""BACKUP: Export KB to markdown files. This REPLACES the old backup system. Creates YAML frontmatter with all metadata, preserves links as wikilinks, organizes by category.

WHEN TO USE: Regular backups, version control, read/edit in any markdown editor
OUTPUT: Markdown files with full metadata - can fully restore DB from these files
FORMAT: YAML frontmatter (all DB fields) + markdown content + links footer
RESTORE: Use import_from_markdown() to restore from backup
TIP: Embeddings NOT stored (regenerate on import to save space)
BEST PRACTICE: Export to ~/duckdb-kb/markdown/ for version control + git backup""",
    inputSchema={
        "type": "object",
        "properties": {
            "output_dir": {
                "type": "string",
                "description": "Directory to export files (default: ~/duckdb-kb/markdown). Created if doesn't exist."
            },
            "category": {
                "type": "string",
                "description": "Optional: Only export this category (table, command, issue, pattern, etc.)"
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional: Only export entries with these tags"
            },
            "organize_by_category": {
                "type": "boolean",
                "description": "Create subdirectories by category (default: true)",
                "default": True
            }
        },
        "required": []
    }
)

# =============================================================================
# Implementation
# =============================================================================

async def execute(con, args: dict) -> List[TextContent]:
    """Export KB entries to markdown files"""
    import shutil

    # Default to standard location if not provided
    default_output = "~/duckdb-kb/markdown"
    output_dir_str = args.get("output_dir", default_output)
    output_dir = Path(os.path.expanduser(output_dir_str))
    category_filter = args.get("category")
    tags_filter = args.get("tags")
    # Normalize tag filters to match DB normalization
    if tags_filter:
        tags_filter = [tag.lower().strip() for tag in tags_filter]
    organize_by_category = args.get("organize_by_category", True)

    # Build query
    where_clauses = []
    params = []

    if category_filter:
        where_clauses.append("category = ?")
        params.append(category_filter)

    if tags_filter:
        # Match if entry has ANY of the tags
        tag_conditions = " OR ".join(["list_contains(tags, ?)" for _ in tags_filter])
        where_clauses.append(f"({tag_conditions})")
        params.extend(tags_filter)

    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

    # Fetch entries
    query = f"SELECT id, category, title, content, tags, metadata, created, updated FROM knowledge WHERE {where_sql} ORDER BY category, id"
    entries = con.execute(query, params).fetchall()

    if not entries:
        return [TextContent(type="text", text="No entries found matching filters")]

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Clear existing category directories for clean export
    if organize_by_category:
        for cat_dir in output_dir.iterdir():
            if cat_dir.is_dir() and cat_dir.name not in ['.obsidian', '.git']:
                shutil.rmtree(cat_dir)

    exported_count = 0

    for entry in entries:
        entry_id, category, title, content, tags, metadata, created, updated = entry

        # Determine output file path
        if organize_by_category:
            cat_dir = output_dir / category
            cat_dir.mkdir(exist_ok=True)
            file_path = cat_dir / f"{entry_id}.md"
        else:
            file_path = output_dir / f"{entry_id}.md"

        # Build YAML frontmatter
        frontmatter = {
            "id": entry_id,
            "category": category,
            "title": title,
            "tags": tags if tags else [],
            "created": created.isoformat() if created else None,
            "updated": updated.isoformat() if updated else None,
        }

        if metadata:
            frontmatter["metadata"] = json.loads(metadata) if isinstance(metadata, str) else metadata

        # Build markdown content
        md_content = "---\n"
        md_content += yaml.dump(frontmatter, sort_keys=False, allow_unicode=True)
        md_content += "---\n\n"

        # Only add title if content doesn't start with it
        if content and content.strip().startswith(f"# {title}"):
            md_content += content
        else:
            md_content += f"# {title}\n\n"
            md_content += content if content else ""

        # Add metadata footer
        md_content += f"\n\n---\n\n*KB Entry: `{entry_id}` | Category: {category} | Updated: {updated.date() if updated else 'N/A'}*\n"

        # Write file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(md_content)

        exported_count += 1

    return [TextContent(type="text", text=f"✓ Exported {exported_count} entries to {output_dir}\n\nOrganized by category: {organize_by_category}\nBackup complete! Use import_from_markdown() to restore.")]

# =============================================================================
# Metadata
# =============================================================================

REQUIRES_DB = True
