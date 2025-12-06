#!/usr/bin/env python3
"""DuckDB Knowledge Base MCP Server - Entry Point."""
from mcp.server import Server
from mcp.types import TextContent
import mcp.server.stdio

from tools import (
    get_tool_handler,
    tool_requires_db,
    get_all_tool_definitions,
    get_connection,
)

app = Server("duckdb-knowledge")


@app.list_tools()
async def list_tools():
    return get_all_tool_definitions()


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    handler = get_tool_handler(name)
    if handler is None:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    con = None
    if tool_requires_db(name):
        con = get_connection()

    try:
        return await handler(con, arguments)
    finally:
        if con is not None:
            try:
                con.close()
            except Exception:
                pass


async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
