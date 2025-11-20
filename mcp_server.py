#!/usr/bin/env python3
"""
DuckDB Knowledge Base MCP Server (Modular Switchboard)

Provides 15 tools for Claude Code to interact with knowledge base.
All tool implementations are in the tools/ directory.
This file serves as a minimal switchboard that delegates to tool handlers.
"""

from mcp.server import Server
from mcp.types import TextContent
import mcp.server.stdio

# Import tool registry
from tools import (
    get_all_tool_definitions,
    get_tool_handler,
    tool_requires_db
)
from tools.base import get_connection

# =============================================================================
# MCP Server
# =============================================================================

app = Server("duckdb-knowledge")


@app.list_tools()
async def list_tools():
    """Return all registered tool definitions"""
    return get_all_tool_definitions()


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """
    Handle tool calls by delegating to registered handlers.

    This is the minimal switchboard pattern:
    1. Check if tool exists
    2. Get database connection if tool needs it
    3. Execute tool handler
    4. Close connection if opened
    """

    # Get tool handler
    handler = get_tool_handler(name)

    if handler is None:
        return [TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]

    # Get database connection if tool needs it
    con = None
    if tool_requires_db(name):
        con = get_connection()

    try:
        # Execute tool handler
        return await handler(con, arguments)

    finally:
        # Clean up database connection if opened
        if con is not None:
            try:
                con.close()
            except Exception:
                pass  # Already closed or connection invalid


# =============================================================================
# Server Entry Point
# =============================================================================

async def main():
    """Run MCP server"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
