"""Export to markdown tool."""
import shutil
from typing import List
from pathlib import Path
import yaml
import json
from mcp.types import Tool, TextContent

from .base import normalize_tags, text_response
from .session_details import MARKDOWN_DIR

TOOL_DEF = Tool(
    name="export_to_markdown",
    description="Export KB entries to markdown files with YAML frontmatter.",
    inputSchema={
        "type": "object",
        "properties": {
            "output_dir": {"type": "string", "description": "Directory to export files (default: ~/duckdb-kb/markdown). Created if doesn't exist."},
            "category": {"type": "string", "description": "Optional: Only export this category (table, command, issue, pattern, etc.)"},
            "tags": {"type": "array", "items": {"type": "string"}, "description": "Optional: Only export entries with these tags"},
            "organize_by_category": {"type": "boolean", "description": "Create subdirectories by category (default: true)", "default": True},
            "clear_existing": {"type": "boolean", "description": "Clear existing category directories before export (default: false, safer)", "default": False}
        },
        "required": []
    }
)

REQUIRES_DB = True


async def execute(con, args: dict) -> List[TextContent]:
    default_output = str(MARKDOWN_DIR)
    output_dir_str = args.get("output_dir", default_output)
    output_dir = Path(output_dir_str).expanduser()
    category_filter = args.get("category")
    tags_filter = args.get("tags")
    if tags_filter:
        tags_filter = normalize_tags(tags_filter)
    organize_by_category = args.get("organize_by_category", True)
    clear_existing = args.get("clear_existing", False)

    where_clauses = []
    params = []

    if category_filter:
        where_clauses.append("category = ?")
        params.append(category_filter)

    if tags_filter:
        tag_conditions = " OR ".join(["list_contains(tags, ?)" for _ in tags_filter])
        where_clauses.append(f"({tag_conditions})")
        params.extend(tags_filter)

    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
    query = f"SELECT id, category, title, content, tags, metadata, created, updated FROM knowledge WHERE {where_sql} ORDER BY category, id"
    entries = con.execute(query, params).fetchall()

    if not entries:
        return text_response("No entries found matching filters")

    output_dir.mkdir(parents=True, exist_ok=True)

    if organize_by_category and clear_existing:
        for cat_dir in output_dir.iterdir():
            # Skip special dirs and shared repos (dirs containing .git)
            if cat_dir.is_dir() and cat_dir.name not in ['.obsidian', '.git']:
                if (cat_dir / '.git').exists():
                    continue  # Protect shared repos
                shutil.rmtree(cat_dir)

    exported_count = 0
    for entry in entries:
        entry_id, category, title, content, tags, metadata, created, updated = entry

        if organize_by_category:
            cat_dir = output_dir / category
            cat_dir.mkdir(exist_ok=True)
            file_path = cat_dir / f"{entry_id}.md"
        else:
            file_path = output_dir / f"{entry_id}.md"

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

        md_content = "---\n"
        md_content += yaml.dump(frontmatter, sort_keys=False, allow_unicode=True)
        md_content += "---\n\n"

        if content and content.strip().startswith(f"# {title}"):
            md_content += content
        else:
            md_content += f"# {title}\n\n"
            md_content += content if content else ""

        md_content += f"\n\n---\n\n*KB Entry: `{entry_id}` | Category: {category} | Updated: {updated.date() if updated else 'N/A'}*\n"

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        exported_count += 1

    return text_response(f"Exported {exported_count} entries to {output_dir}\n\nOrganized by category: {organize_by_category}\nBackup complete! Use import_from_markdown() to restore.")
