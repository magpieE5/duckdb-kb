"""Offload topics from context entries when they exceed budget

Autonomous topic extraction to maintain token budgets:
- Identifies oldest topics by timestamp
- Extracts and creates new KB entries
- Removes from source entry
- Repeats until under budget
"""

from mcp.types import Tool, TextContent
from typing import List, Dict, Any
import json
import re
from datetime import datetime

# =============================================================================
# Tool Definition (for registration)
# =============================================================================

TOOL = Tool(
    name="offload_topics",
    description="""Offload topics from context entries when they exceed budget.

WHEN TO USE: Autonomous execution when check_token_budgets detects over-budget
STRATEGY: Always oldest-first by timestamp (automatic, no manual selection)

Process:
1. Parse topics with timestamps from entry
2. Sort by date: oldest first
3. Extract oldest topic(s) until under target_tokens
4. Generate KB entry suggestions
5. Return extracted topics + new entry proposals

Budget targets (15K/5K allocation):
- user-current-state: 15K
- user-biographical: 5K
- arlo-current-state: 15K
- arlo-biographical: 5K""",
    inputSchema={
        "type": "object",
        "properties": {
            "entry_id": {
                "type": "string",
                "description": "KB entry ID to offload from (e.g., 'user-current-state')"
            },
            "target_tokens": {
                "type": "integer",
                "description": "Target token count after offload (e.g., 13000 for 15K budget with 2K margin)"
            },
            "strategy": {
                "type": "string",
                "enum": ["oldest_first"],
                "default": "oldest_first",
                "description": "Offload strategy (currently only oldest_first supported)"
            }
        },
        "required": ["entry_id", "target_tokens"]
    }
)

# =============================================================================
# Implementation
# =============================================================================

async def execute(con, args: dict) -> List[TextContent]:
    """Execute topic offload from context entry"""

    entry_id = args["entry_id"]
    target_tokens = args["target_tokens"]
    strategy = args.get("strategy", "oldest_first")

    # Fetch entry
    row = con.execute(
        "SELECT content FROM knowledge WHERE id = ?",
        [entry_id]
    ).fetchone()

    if not row:
        return [TextContent(type="text", text=json.dumps({
            "error": f"Entry not found: {entry_id}"
        }))]

    content = row[0]
    current_tokens = len(content) // 4

    # Parse topics with timestamps
    topics = _parse_topics_with_timestamps(content)

    # Sort by date: oldest first
    topics.sort(key=lambda t: t["timestamp"])

    # Select topics to offload
    topics_to_offload = []
    remaining_tokens = current_tokens

    for topic in topics:
        if remaining_tokens <= target_tokens:
            break

        topics_to_offload.append(topic)
        remaining_tokens -= (len(topic["content"]) // 4)

    # Generate new entry suggestions
    new_entry_suggestions = _generate_entry_suggestions(topics_to_offload, entry_id)

    # Build updated entry content (with topics removed)
    updated_content = _remove_topics_from_content(content, topics_to_offload)
    new_token_count = len(updated_content) // 4

    response = {
        "entry_id": entry_id,
        "current_tokens": current_tokens,
        "target_tokens": target_tokens,
        "new_token_count": new_token_count,
        "topics_offloaded": len(topics_to_offload),
        "extracted_topics": topics_to_offload,
        "new_entry_suggestions": new_entry_suggestions,
        "updated_entry_content": updated_content,
        "status": "under_budget" if new_token_count <= target_tokens else "still_over_budget"
    }

    return [TextContent(type="text", text=json.dumps(response, indent=2))]


def _parse_topics_with_timestamps(content: str) -> List[Dict[str, Any]]:
    """Parse topics with timestamps from entry content"""

    topics = []

    # Pattern: ### Topic Title (YYYY-MM-DD)
    # Captures section until next ### or end
    pattern = r'###\s+([^\n]+?)\s+\((\d{4}-\d{2}-\d{2})\)(.*?)(?=###|\Z)'

    matches = re.finditer(pattern, content, re.DOTALL)

    for match in matches:
        title = match.group(1).strip()
        timestamp_str = match.group(2)
        topic_content = match.group(3).strip()

        try:
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d")
        except ValueError:
            # Invalid timestamp, skip
            continue

        topics.append({
            "title": title,
            "timestamp": timestamp,
            "timestamp_str": timestamp_str,
            "content": f"### {title} ({timestamp_str})\n{topic_content}",
            "content_only": topic_content
        })

    return topics


def _generate_entry_suggestions(topics: List[Dict], source_entry_id: str) -> List[Dict[str, Any]]:
    """Generate KB entry suggestions for offloaded topics"""

    suggestions = []

    # Determine category based on source entry
    if "user" in source_entry_id:
        default_category = "log"  # User work/activity logs
    else:
        default_category = "pattern"  # Arlo investigations/realizations

    for topic in topics:
        # Generate ID from title
        entry_id = topic["title"].lower()\
            .replace(" ", "-")\
            .replace("&", "and")\
            .replace("/", "-")[:50]

        entry_id = f"{default_category}-{entry_id}-{topic['timestamp_str']}"

        suggestions.append({
            "id": entry_id,
            "category": default_category,
            "title": topic["title"],
            "content": topic["content_only"],
            "tags": [default_category, source_entry_id, "offloaded", topic["timestamp_str"][:7]],  # YYYY-MM
            "source": source_entry_id,
            "offloaded_date": datetime.now().strftime("%Y-%m-%d")
        })

    return suggestions


def _remove_topics_from_content(content: str, topics_to_remove: List[Dict]) -> str:
    """Remove offloaded topics from entry content"""

    updated_content = content

    for topic in topics_to_remove:
        # Remove the entire topic section
        updated_content = updated_content.replace(topic["content"], "")

    # Clean up multiple consecutive blank lines
    updated_content = re.sub(r'\n{3,}', '\n\n', updated_content)

    return updated_content.strip()

# =============================================================================
# Metadata
# =============================================================================

REQUIRES_DB = True
