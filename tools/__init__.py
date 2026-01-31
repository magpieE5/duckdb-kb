"""MCP Tools registry - auto-discovers and exports all tools (14 tools)."""
from typing import List, Optional, Callable
from mcp.types import Tool

from . import (
    upsert_knowledge,
    list_add,
    list_remove,
    raw_query,
    log_session,
    list_knowledge,
    export_to_markdown,
    import_from_markdown,
    scan_knowledge,
    get_knowledge,
    delete_knowledge,
    extract_transcript,
    set_session,
    drafts_to_pdf,
)
from .base import get_connection, persist, close_connection

# All tool modules
_TOOL_MODULES = [
    upsert_knowledge,
    list_add,
    list_remove,
    raw_query,
    log_session,
    list_knowledge,
    export_to_markdown,
    import_from_markdown,
    scan_knowledge,
    get_knowledge,
    delete_knowledge,
    extract_transcript,
    set_session,
    drafts_to_pdf,
]

# Build registry from modules
TOOL_REGISTRY = {}
for module in _TOOL_MODULES:
    tool_def = module.TOOL_DEF
    TOOL_REGISTRY[tool_def.name] = {
        "tool_def": tool_def,
        "handler": module.execute,
        "requires_db": module.REQUIRES_DB,
    }


def get_tool_handler(tool_name: str) -> Optional[Callable]:
    """Get the handler function for a tool."""
    if tool_name not in TOOL_REGISTRY:
        return None
    return TOOL_REGISTRY[tool_name]['handler']


def tool_requires_db(tool_name: str) -> bool:
    """Check if a tool requires a database connection."""
    if tool_name not in TOOL_REGISTRY:
        return True
    return TOOL_REGISTRY[tool_name]['requires_db']


def get_all_tool_definitions() -> List[Tool]:
    """Get all tool definitions for MCP registration."""
    return [entry['tool_def'] for entry in TOOL_REGISTRY.values()]


# Tools that modify the database (need persist after execution)
WRITE_TOOLS = {
    'upsert_knowledge',
    'list_add',
    'list_remove',
    'log_session',
    'import_from_markdown',
    'delete_knowledge',
    'extract_transcript',
    'scan_knowledge',  # logs access to accumulator
    'get_knowledge',   # logs access to accumulator
}


def tool_writes_db(tool_name: str) -> bool:
    """Check if a tool writes to the database (needs persist)."""
    return tool_name in WRITE_TOOLS


__all__ = [
    'TOOL_REGISTRY',
    'get_tool_handler',
    'tool_requires_db',
    'tool_writes_db',
    'get_all_tool_definitions',
    'get_connection',
    'persist',
    'close_connection',
]
