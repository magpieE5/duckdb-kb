"""Tool registry for modular MCP tool structure

Provides dynamic tool discovery and registration.
Each tool is a separate module with:
- TOOL: Tool definition for MCP
- execute: async function handler
- REQUIRES_DB: bool flag for DB connection need
"""

import importlib
from pathlib import Path
from typing import Dict, Callable, List, Optional
from mcp.types import Tool, TextContent

# =============================================================================
# Tool Registry
# =============================================================================

_tool_registry: Dict[str, Dict] = {}  # Maps tool_name -> {module, handler, requires_db, tool_def}
_registration_failures: List[tuple] = []  # Tracks (module_name, error_msg) for failed registrations


def register_tool(module_name: str, subdir: str):
    """
    Register a tool from a module.

    Args:
        module_name: Module name (e.g., 'get_knowledge')
        subdir: Subdirectory name (e.g., 'read')
    """
    full_module_path = f"tools.{subdir}.{module_name}"

    try:
        module = importlib.import_module(full_module_path)

        # Extract required attributes
        tool_def = getattr(module, 'TOOL')
        execute = getattr(module, 'execute')
        requires_db = getattr(module, 'REQUIRES_DB', True)  # Default: require DB

        _tool_registry[tool_def.name] = {
            'module': module,
            'handler': execute,
            'requires_db': requires_db,
            'tool_def': tool_def
        }

    except Exception as e:
        # Expected failures: __init__.py, base.py (not tools)
        # Log unexpected failures for debugging
        if module_name not in ['__init__', 'base']:
            _registration_failures.append((f"{subdir}.{module_name}", str(e)))


def get_tool_handler(tool_name: str) -> Optional[Callable]:
    """
    Get handler function for a tool.

    Returns:
        Async function: async def handler(con, arguments) -> List[TextContent]
        None if tool not found
    """
    if tool_name not in _tool_registry:
        return None

    return _tool_registry[tool_name]['handler']


def tool_requires_db(tool_name: str) -> bool:
    """Check if tool requires database connection"""
    if tool_name not in _tool_registry:
        return True  # Conservative default

    return _tool_registry[tool_name]['requires_db']


def get_all_tool_definitions() -> List[Tool]:
    """Get all tool definitions for list_tools() handler"""
    return [entry['tool_def'] for entry in _tool_registry.values()]


def get_registration_failures() -> List[tuple]:
    """Get list of tools that failed to register (for debugging)

    Returns:
        List of (module_name, error_message) tuples
    """
    return _registration_failures.copy()


# =============================================================================
# Auto-discovery and registration
# =============================================================================

def discover_and_register_tools():
    """Discover all tools in tools/ directory structure"""
    tools_dir = Path(__file__).parent

    # Find all subdirectories (read, search, write, utility, system)
    for subdir_path in tools_dir.iterdir():
        if not subdir_path.is_dir():
            continue

        if subdir_path.name.startswith('_'):  # Skip __pycache__, etc.
            continue

        subdir_name = subdir_path.name

        # Find all .py files in subdirectory
        for tool_file in subdir_path.glob("*.py"):
            if tool_file.name.startswith('_'):  # Skip __init__.py
                continue

            module_name = tool_file.stem
            register_tool(module_name, subdir_name)


# Auto-register on import
discover_and_register_tools()
