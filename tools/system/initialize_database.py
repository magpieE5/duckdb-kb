"""Initialize or reinitialize the DuckDB knowledge base"""

from mcp.types import Tool, TextContent
from typing import List
import json
from pathlib import Path
import duckdb
from tools.base import DB_PATH

# =============================================================================
# Tool Definition (for registration)
# =============================================================================

TOOL = Tool(
    name="initialize_database",
    description="""Initialize or reinitialize the DuckDB knowledge base with schema.

Creates kb.duckdb file, loads VSS extension (if available), and executes schema.sql to set up tables, indexes, views, and macros.

WHEN TO USE: First run, database recovery, or force reinitialize
Returns: Success status, VSS availability, and initial database stats""",
    inputSchema={
        "type": "object",
        "properties": {
            "force": {
                "type": "boolean",
                "description": "Force reinitialize even if database exists (default: false)",
                "default": False
            }
        }
    }
)

# =============================================================================
# Implementation
# =============================================================================

async def execute(args: dict) -> List[TextContent]:
    """Initialize or reinitialize the database with schema"""
    force = args.get("force", False)

    # Check if database already exists
    db_path_obj = Path(DB_PATH)
    if db_path_obj.exists() and not force:
        return [TextContent(type="text", text=json.dumps({
            "success": False,
            "error": "Database already exists. Use force=True to reinitialize."
        }))]

    try:
        # Create fresh connection (will create file if doesn't exist)
        con = duckdb.connect(str(DB_PATH))

        # 1. Install and load VSS extension
        has_vss = False
        try:
            con.execute("INSTALL vss")
            con.execute("LOAD vss")
            has_vss = True
        except Exception as e:
            # VSS not available, continue without it
            pass

        # 2. Execute schema.sql
        # Get schema.sql from project root (2 levels up from this file)
        schema_path = Path(__file__).parent.parent.parent / 'schema.sql'
        if not schema_path.exists():
            con.close()
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": f"schema.sql not found at {schema_path}"
            }))]

        with open(schema_path) as f:
            schema_sql = f.read()

        try:
            con.execute(schema_sql)
        except Exception as e:
            # Ignore "already exists" errors during force reinit
            if 'already exists' not in str(e).lower():
                con.close()
                return [TextContent(type="text", text=json.dumps({
                    "success": False,
                    "error": f"Failed to execute schema: {str(e)}"
                }))]

        # 3. Validate - check that knowledge table exists
        tables = con.execute("SHOW TABLES").fetchall()
        table_names = [t[0] for t in tables]

        if 'knowledge' not in table_names:
            con.close()
            return [TextContent(type="text", text=json.dumps({
                "success": False,
                "error": "Validation failed: knowledge table not created"
            }))]

        # Get stats
        try:
            stats_result = con.execute("SELECT * FROM database_summary()").fetchall()
            stats = {metric: value for metric, value in stats_result}
        except:
            stats = {}

        con.close()

        return [TextContent(type="text", text=json.dumps({
            "success": True,
            "message": "Database initialized successfully",
            "vss_available": has_vss,
            "stats": stats
        }))]

    except Exception as e:
        return [TextContent(type="text", text=json.dumps({
            "success": False,
            "error": f"Initialization failed: {str(e)}"
        }))]

# =============================================================================
# Metadata
# =============================================================================

REQUIRES_DB = False
