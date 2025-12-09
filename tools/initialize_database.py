"""Initialize database tool."""
from typing import List
from pathlib import Path
import duckdb
from mcp.types import Tool, TextContent

from .base import DB_PATH, SCHEMA_SQL, json_response

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

REQUIRES_DB = False


async def execute(con, args: dict) -> List[TextContent]:
    force = args.get("force", False)
    db_path_obj = Path(DB_PATH)

    if db_path_obj.exists() and not force:
        return json_response({"success": False, "error": "Database already exists. Use force=True to reinitialize."})

    try:
        con = duckdb.connect(str(DB_PATH))
        try:
            con.execute(SCHEMA_SQL)
        except Exception as e:
            if 'already exists' not in str(e).lower():
                con.close()
                return json_response({"success": False, "error": f"Failed to execute schema: {str(e)}"})

        tables = con.execute("SHOW TABLES").fetchall()
        table_names = [t[0] for t in tables]

        if 'knowledge' not in table_names:
            con.close()
            return json_response({"success": False, "error": "Validation failed: knowledge table not created"})

        try:
            stats_result = con.execute("SELECT * FROM database_summary()").fetchall()
            stats = {metric: value for metric, value in stats_result}
        except:
            stats = {}

        con.close()
        return json_response({"success": True, "message": "Database initialized successfully", "stats": stats})
    except Exception as e:
        return json_response({"success": False, "error": f"Initialization failed: {str(e)}"})
