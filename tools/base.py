"""Shared utilities for MCP tools - Parquet-backed storage."""
import json
import os
import re
from typing import List
from datetime import datetime
from pathlib import Path
import duckdb
import yaml
from mcp.types import TextContent

try:
    from .session_details import KB_PARQUET_PATH, KB_DB_PATH, MARKDOWN_DIR
except ImportError:
    from session_details import KB_PARQUET_PATH, KB_DB_PATH, MARKDOWN_DIR

PARQUET_PATH = KB_PARQUET_PATH

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

# Singleton connection
_connection = None

# Session state for access logging
_current_session = None


def set_current_session(session_num: int):
    """Set the current session number for KB access logging."""
    global _current_session
    _current_session = session_num


def get_current_session():
    """Get the current session number, or None if not set."""
    return _current_session


def log_kb_access(con, op: str, result_ids: list):
    """Log KB access to accumulator-kb-access.

    Format: SESSION|OP|id1,id2,id3
    Example: 153|get|seed-arlo-foundations,reference-arlo-foundations
    """
    session = get_current_session()
    if session is None or not result_ids:
        return  # No logging if session not set or no results

    ids_str = ",".join(result_ids)
    log_line = f"{session}|{op}|{ids_str}"

    # Append to accumulator
    from datetime import datetime
    now = datetime.now()

    existing = con.execute(
        "SELECT content FROM knowledge WHERE id = 'accumulator-kb-access'"
    ).fetchone()

    if existing:
        combined = existing[0] + "\n" + log_line
        con.execute(
            "UPDATE knowledge SET content = ?, updated = ? WHERE id = 'accumulator-kb-access'",
            [combined, now]
        )
    else:
        con.execute("""
            INSERT INTO knowledge (id, category, title, tags, content, metadata, created, updated)
            VALUES ('accumulator-kb-access', 'reference', 'KB Access Log', ?, ?, '{}', ?, ?)
        """, [['accumulator', 'access-log'], log_line, now, now])


def _bootstrap_from_markdown(con):
    """Import all entries from markdown/ on fresh install.

    Called automatically when no parquet exists and no migration source.
    Imports from all category subdirectories (seed/, reference/, etc.).
    """
    if not MARKDOWN_DIR.exists():
        return 0

    imported = 0
    for md_file in MARKDOWN_DIR.glob('**/*.md'):
        try:
            content = md_file.read_text(encoding='utf-8')

            if not content.startswith('---'):
                continue

            parts = content.split('---', 2)
            if len(parts) < 3:
                continue

            frontmatter = yaml.safe_load(parts[1])
            body = parts[2].strip()

            # Clean up body (remove auto-generated title/footer)
            body = re.sub(r'^#\s+.*?\n+', '', body, count=1)
            body = re.sub(r'\n+---\s*\n+\*KB Entry:.*?\*\s*', '', body, flags=re.DOTALL)
            body = re.sub(r'\n+---\s*$', '', body)

            entry_id = frontmatter['id']
            category = frontmatter.get('category', 'seed')
            title = frontmatter['title']
            tags = frontmatter.get('tags', [])
            metadata = json.dumps(frontmatter.get('metadata')) if frontmatter.get('metadata') else None
            created = frontmatter.get('created') or datetime.now()
            updated = frontmatter.get('updated') or datetime.now()

            con.execute(
                "INSERT INTO knowledge (id, category, title, content, tags, metadata, created, updated) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                [entry_id, category, title, body.strip(), tags, metadata, created, updated]
            )
            imported += 1
        except Exception:
            continue  # Skip malformed files silently during bootstrap

    return imported


def get_connection():
    """Get the singleton DuckDB connection.

    On first call: loads from parquet (or creates empty table if no parquet exists).
    Subsequent calls: returns the same in-memory connection.
    """
    global _connection

    if _connection is not None:
        return _connection

    # Create in-memory connection
    _connection = duckdb.connect()

    # Load FTS extension
    _connection.execute("INSTALL fts; LOAD fts;")

    # Create schema first (ensures PRIMARY KEY constraint exists for ON CONFLICT)
    _connection.execute(SCHEMA_SQL)

    # Load data from parquet if exists, otherwise bootstrap from seeds
    if os.path.exists(PARQUET_PATH):
        _connection.execute(f"INSERT INTO knowledge SELECT * FROM read_parquet('{PARQUET_PATH}')")
    elif os.path.exists(KB_DB_PATH):
        # Migration path: load from old duckdb file if parquet doesn't exist yet
        _connection.execute(f"ATTACH '{KB_DB_PATH}' AS old_db (READ_ONLY)")
        _connection.execute("INSERT INTO knowledge SELECT * FROM old_db.knowledge")
        _connection.execute("DETACH old_db")
        # Immediately persist to create the parquet file
        persist()
    else:
        # Fresh install: bootstrap from markdown
        imported = _bootstrap_from_markdown(_connection)
        if imported > 0:
            persist()  # Save bootstrapped entries to parquet

    # Create FTS index
    try:
        _connection.execute("PRAGMA create_fts_index('knowledge', 'id', 'title', 'content', overwrite=1)")
    except Exception:
        pass  # Table might be empty

    return _connection


def persist():
    """Persist the in-memory database to parquet file.

    Called automatically after write operations.
    Uses ZSTD compression for optimal size.
    """
    global _connection

    if _connection is None:
        return

    _connection.execute(f"COPY knowledge TO '{PARQUET_PATH}' (FORMAT PARQUET, COMPRESSION ZSTD)")


def close_connection():
    """Close the singleton connection. Called at server shutdown."""
    global _connection

    if _connection is not None:
        try:
            persist()  # Final persist before close
            _connection.close()
        except Exception:
            pass
        _connection = None


def normalize_tags(tags: List[str]) -> List[str]:
    """Normalize tags to lowercase and stripped."""
    return [tag.lower().strip() for tag in tags]


def error_response(error_type: str, message: str, details: dict = None) -> List[TextContent]:
    """Create a standardized error response as TextContent."""
    return [TextContent(type="text", text=json.dumps({
        "status": "error",
        "error_type": error_type,
        "message": message,
        "details": details or {}
    }))]


def json_response(data: dict) -> List[TextContent]:
    """Create a JSON TextContent response."""
    return [TextContent(type="text", text=json.dumps(data, default=str))]


def text_response(text: str) -> List[TextContent]:
    """Create a plain text TextContent response."""
    return [TextContent(type="text", text=text)]
