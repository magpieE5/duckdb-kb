"""Initialize database tool."""
from typing import List
from mcp.types import Tool, TextContent

from .base import SCHEMA_SQL, json_response, PARQUET_PATH
import os

TOOL_DEF = Tool(
    name="initialize_database",
    description="Initialize or reinitialize database with schema.",
    inputSchema={
        "type": "object",
        "properties": {
            "force": {"type": "boolean", "description": "Force reinitialize even if database exists (default: false)", "default": False}
        }
    }
)

REQUIRES_DB = True


async def execute(con, args: dict) -> List[TextContent]:
    force = args.get("force", False)

    if os.path.exists(PARQUET_PATH) and not force:
        # Just return current stats
        try:
            stats_result = con.execute("SELECT * FROM database_summary()").fetchall()
            stats = {metric: value for metric, value in stats_result}
        except:
            stats = {}
        return json_response({"success": True, "message": "Database already initialized", "stats": stats})

    if force:
        # Drop and recreate table
        try:
            con.execute("DROP TABLE IF EXISTS knowledge")
            con.execute(SCHEMA_SQL)
        except Exception as e:
            return json_response({"success": False, "error": f"Failed to reinitialize: {str(e)}"})

    # Validate
    tables = con.execute("SHOW TABLES").fetchall()
    table_names = [t[0] for t in tables]

    if 'knowledge' not in table_names:
        return json_response({"success": False, "error": "Validation failed: knowledge table not found"})

    try:
        stats_result = con.execute("SELECT * FROM database_summary()").fetchall()
        stats = {metric: value for metric, value in stats_result}
    except:
        stats = {}

    return json_response({"success": True, "message": "Database initialized successfully", "stats": stats})
