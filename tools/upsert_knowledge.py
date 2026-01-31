"""Upsert knowledge entry tool."""
import re
from typing import List
from datetime import datetime, timezone
from mcp.types import Tool, TextContent

from .base import normalize_tags, json_response, error_response, log_kb_access

# ID validation patterns by category
ID_PATTERNS = {
    "log": re.compile(r"^session-\d{3}$"),  # session-001, session-002, etc.
}

TOOL_DEF = Tool(
    name="upsert_knowledge",
    description="""Create or update knowledge entry.

## Categories
- **reference**: Static facts about people, systems, orgs - things that ARE (e.g., resume, system architecture, org structure)
- **pattern**: Reusable approaches, how-tos - things that WORK (e.g., ETL pattern, code idiom)
- **table**: Schema/structure documentation for data sources (e.g., Banner tables, PDS schemas)
- **command**: CLI commands, scripts, invocations with usage
- **issue**: Bugs, problems, investigations - may resolve over time. ID format: `issue-{system}-{ticket_id}` (e.g., `issue-idr-3731` for Jira IDR tickets, `issue-tdx-19745186` for TeamDynamix). Include: summary, investigation path, root cause, resolution/status, impact, session reference.
- **troubleshooting**: Diagnostic procedures - "when X happens, do Y"
- **project**: Active initiatives - status, goals, scope
- **decision**: Architectural/design choices WITH RATIONALE - why X over Y
- **research**: Investigations, explorations, learning - not yet actionable
- **log**: Session logs ONLY (validated ID: session-NNN) - use log_session tool instead
- **actions**: Trackable life events - things that HAPPENED. Verbose tagging for structured retrieval.
  - Fitness: run, walk, bike, swim, lift, stretch, yoga, hike
  - Nutrition: meal, snack, fast, water, coffee, alcohol
  - Health: sleep, weight, mood, symptom, medication, appointment
  - Work: meeting, deploy, release, presentation, interview
  - Social: call, hangout, date, party, family
  - Finance: purchase, bill, income, investment
  - Learning: read, course, practice, lesson
  - Creative: write, music, art, project
  At session open, run `SELECT tag, count(*) FROM (SELECT unnest(tags) as tag FROM knowledge WHERE category='actions') GROUP BY 1 ORDER BY 2 DESC` to show user what they're tracking.
- **todo**: Rolling task lists (todo-work, todo-personal) - when done, remove item and re-order list
- **seed**: Minting templates and structural foundations for distribution - what a fresh instance needs to bootstrap
- **transcript**: Verbatim session exchanges - created by close.md via extract_exchanges.py
- **other**: Escape hatch - should be rare

## When to Create Entries
Create a KB entry when information has REUSE VALUE beyond the current session:
- Facts about people/systems you'll reference again → reference
- A solution that could apply elsewhere → pattern
- An active project being discussed → project
- A choice that needs rationale preserved → decision

Do NOT create entries for transient conversation - that belongs in session logs.

## ID Format
Use kebab-case: {category}-{topic}-{specifics} (e.g., 'reference-brock-lampman', 'pattern-duckdb-upsert')

## Content Structure
Start with ~400 char dense preview (key facts, names, relationships), then full structured content below.

## Fidelity
VERBOSE entries, full context, more is better. Never lose: exact quotes, numbers, names, dates, examples given, caveats stated, and how ideas developed. Summarizing loses information.""",
    inputSchema={
        "type": "object",
        "properties": {
            "id": {"type": "string", "description": "Unique kebab-case identifier: {category}-{topic}-{specifics}"},
            "category": {"type": "string", "enum": ["reference", "pattern", "table", "command", "issue", "troubleshooting", "project", "decision", "research", "log", "actions", "todo", "seed", "transcript", "other"]},
            "title": {"type": "string", "description": "Human-readable title"},
            "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags for categorization (8-15 recommended)"},
            "content": {"type": "string", "description": "Full content (markdown). Start with ~400 char dense preview, then exhaustive detail. Be VERBOSE - more is better."},
            "metadata": {"type": "object", "description": "Additional structured data (JSON object)"},
        },
        "required": ["id", "category", "title", "content"]
    }
)

REQUIRES_DB = True


def validate_id(entry_id: str, category: str) -> str | None:
    """Validate ID format for category. Returns error message or None if valid."""
    if category in ID_PATTERNS:
        pattern = ID_PATTERNS[category]
        if not pattern.match(entry_id):
            return f"Invalid ID '{entry_id}' for category '{category}'. Expected format: {pattern.pattern}"
    return None


async def execute(con, args: dict) -> List[TextContent]:
    entry_id = args["id"]
    category = args["category"]
    title = args["title"]
    content = args["content"]
    tags = normalize_tags(args.get("tags", []))
    metadata = args.get("metadata", {})

    # Block list-type entries - use list_add/list_remove instead
    if entry_id.startswith("todo-") or entry_id.startswith("accumulator-"):
        return error_response("protected_entry",
            f"Cannot upsert '{entry_id}'. Use list_add/list_remove tools instead.")

    # Validate ID format for category
    if error := validate_id(entry_id, category):
        return error_response("validation_error", error)

    existing = con.execute("SELECT 1 FROM knowledge WHERE id = ?", [entry_id]).fetchone()
    now = datetime.now(timezone.utc)

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

    # Log upsert for federation candidate detection
    log_kb_access(con, 'upsert', [entry_id])

    return json_response({"id": entry_id, "status": "updated" if existing else "created"})
