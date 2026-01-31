"""Import from markdown tool."""
import os
import re
from typing import List
from pathlib import Path
import yaml
import json
from mcp.types import Tool, TextContent

from .base import text_response

TOOL_DEF = Tool(
    name="import_from_markdown",
    description="Restore KB from markdown backup files.",
    inputSchema={
        "type": "object",
        "properties": {
            "input_dir": {"type": "string", "description": "Directory with markdown backup files (e.g., '~/duckdb-kb/backup')"},
            "category": {"type": "string", "description": "Optional: Only import files from this category subdirectory"},
            "clear_first": {"type": "boolean", "default": False, "description": "Delete all KB entries before import (rebuilds KB from markdown)"}
        },
        "required": ["input_dir"]
    }
)

REQUIRES_DB = True


async def execute(con, args: dict) -> List[TextContent]:
    input_dir = Path(os.path.expanduser(args["input_dir"]))
    category_filter = args.get("category")
    clear_first = args.get("clear_first", False)

    if not input_dir.exists():
        return text_response(f"Error: Directory not found: {input_dir}")

    # Clear all entries before import if requested
    if clear_first:
        con.execute("DELETE FROM knowledge")

    if category_filter:
        cat_dir = input_dir / category_filter
        if not cat_dir.exists():
            return text_response(f"Error: Category directory not found: {cat_dir}")
        md_files = list(cat_dir.glob("*.md"))
    else:
        md_files = list(input_dir.rglob("*.md"))

    if not md_files:
        return text_response(f"No markdown files found in {input_dir}")

    imported_count = 0
    updated_count = 0
    skipped_count = 0

    for md_file in md_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            if not content.startswith('---'):
                skipped_count += 1
                continue

            parts = content.split('---', 2)
            if len(parts) < 3:
                skipped_count += 1
                continue

            frontmatter = yaml.safe_load(parts[1])
            body = parts[2].strip()

            # Clean up body
            body = re.sub(r'^#\s+.*?\n+', '', body, count=1)
            while re.search(r'\n+---\s*\n+\*KB Entry:.*?\*', body, flags=re.DOTALL):
                body = re.sub(r'\n+---\s*\n+\*KB Entry:.*?\*\s*', '', body, flags=re.DOTALL)
            body = re.sub(r'\n+---\s*$', '', body)

            entry_id = frontmatter['id']
            category = frontmatter.get('category', 'other')
            title = frontmatter['title']
            tags = frontmatter.get('tags', [])
            metadata = json.dumps(frontmatter.get('metadata')) if frontmatter.get('metadata') else None
            created = frontmatter.get('created')
            updated = frontmatter.get('updated')

            existing = con.execute("SELECT id FROM knowledge WHERE id = ?", [entry_id]).fetchone()

            if existing:
                con.execute(
                    "UPDATE knowledge SET category = ?, title = ?, content = ?, tags = ?, metadata = ?, updated = ? WHERE id = ?",
                    [category, title, body.strip(), tags, metadata, updated, entry_id]
                )
                updated_count += 1
            else:
                con.execute(
                    "INSERT INTO knowledge (id, category, title, content, tags, metadata, created, updated) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    [entry_id, category, title, body.strip(), tags, metadata, created, updated]
                )
                imported_count += 1
        except Exception as e:
            return text_response(f"Error processing {md_file.name}: {str(e)}")

    summary = f"Restore complete!\n\n"
    if clear_first:
        summary += "KB cleared before import.\n\n"
    summary += f"New entries: {imported_count}\nUpdated entries: {updated_count}\n"
    if skipped_count > 0:
        summary += f"Skipped: {skipped_count} files (invalid/malformed)\n"
    summary += f"\nRestored from: {input_dir}"

    return text_response(summary)
