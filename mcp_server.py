#!/usr/bin/env python3
"""DuckDB Knowledge Base MCP Server - Entry Point.

Storage: Parquet file (kb.parquet) with in-memory DuckDB for queries.
Connection: Singleton - loaded once at first tool call, persisted after writes.
"""
from mcp.server import Server
from mcp.types import TextContent
import mcp.server.stdio

from tools import (
    get_tool_handler,
    tool_requires_db,
    tool_writes_db,
    get_all_tool_definitions,
    get_connection,
    persist,
    close_connection,
)

app = Server("duckdb-kb")


@app.list_tools()
async def list_tools():
    return get_all_tool_definitions()


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    handler = get_tool_handler(name)
    if handler is None:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    # Get singleton connection if tool needs it
    con = None
    if tool_requires_db(name):
        con = get_connection()

    try:
        result = await handler(con, arguments)

        # Persist to parquet after write operations
        if tool_writes_db(name):
            persist()

        return result
    except Exception as e:
        return [TextContent(type="text", text=f"Error executing {name}: {str(e)}")]


async def main():
    try:
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await app.run(read_stream, write_stream, app.create_initialization_options())
    finally:
        # Clean shutdown: persist and close
        close_connection()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
