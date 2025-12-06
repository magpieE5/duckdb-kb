"""Shared utilities for MCP tools."""
import os
import json
from typing import List
from datetime import datetime
import duckdb
from mcp.types import TextContent

DB_PATH = os.getenv('KB_DB_PATH', 'kb.duckdb')

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS knowledge (
    id VARCHAR PRIMARY KEY,
    category VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    tags VARCHAR[] DEFAULT [],
    content TEXT NOT NULL,
    metadata JSON DEFAULT '{}'::JSON,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE OR REPLACE MACRO database_summary() AS TABLE (
SELECT 'Total Entries' as metric, COUNT(*)::VARCHAR as value FROM knowledge
UNION ALL
SELECT 'Categories', COUNT(DISTINCT category)::VARCHAR FROM knowledge
UNION ALL
SELECT 'Unique Tags', (SELECT COUNT(DISTINCT t.tag) FROM knowledge k, UNNEST(k.tags) AS t(tag))::VARCHAR
);
"""


def get_connection():
    """Get a DuckDB connection."""
    return duckdb.connect(DB_PATH)


def normalize_tags(tags: List[str]) -> List[str]:
    """Normalize tags to lowercase and stripped."""
    return [tag.lower().strip() for tag in tags]


def error_response(error_type: str, message: str, details: dict = None) -> dict:
    """Create a standardized error response."""
    return {
        "status": "error",
        "error_type": error_type,
        "message": message,
        "details": details or {}
    }


def json_response(data: dict) -> List[TextContent]:
    """Create a JSON TextContent response."""
    return [TextContent(type="text", text=json.dumps(data, default=str))]


def text_response(text: str) -> List[TextContent]:
    """Create a plain text TextContent response."""
    return [TextContent(type="text", text=text)]
