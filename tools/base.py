"""Shared utilities for MCP tools

Provides common functionality:
- Database connection management
- OpenAI client access
- Embedding generation
- Configuration
"""

import os
from typing import List
import duckdb
from openai import OpenAI

# =============================================================================
# Configuration
# =============================================================================

DB_PATH = os.getenv('KB_DB_PATH', 'kb.duckdb')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
EMBEDDINGS_AVAILABLE = OPENAI_API_KEY is not None
EMBEDDING_MODEL = 'text-embedding-3-large'
EMBEDDING_DIM = 3072
DEFAULT_SIMILARITY_THRESHOLD = 0.5

# Lazy-load OpenAI client
_openai_client = None


# =============================================================================
# Database Connection
# =============================================================================

def get_connection():
    """Get DuckDB connection with VSS extension loaded

    Note: Database schema must be initialized first via initialize_database MCP tool.
    This is handled by /kb command initialization flow.

    Connection Lifecycle:
    - Connections are managed by mcp_server.py
    - Automatically closed after tool execution in finally block
    - Do not close connections manually in tools
    """
    con = duckdb.connect(DB_PATH)

    # Load VSS extension (if available)
    try:
        con.execute("INSTALL vss")  # Idempotent - safe to run every time
        con.execute("LOAD vss")
    except Exception:
        # VSS not available - embeddings won't work but other features will
        pass

    return con


# =============================================================================
# OpenAI Client
# =============================================================================

def get_openai_client():
    """Lazy load OpenAI client"""
    global _openai_client

    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not set. Run: export OPENAI_API_KEY='sk-...'")

    if _openai_client is None:
        _openai_client = OpenAI(api_key=OPENAI_API_KEY)

    return _openai_client


# =============================================================================
# Tag Normalization
# =============================================================================

def normalize_tags(tags: List[str]) -> List[str]:
    """Normalize tags for consistent matching

    Tags are stored in lowercase with trimmed whitespace.
    Apply this to both storage and query operations for consistent matching.

    Args:
        tags: List of tag strings

    Returns:
        List of normalized tags (lowercase, trimmed)
    """
    return [tag.lower().strip() for tag in tags]


# =============================================================================
# Embedding Generation
# =============================================================================

def generate_embedding(text: str) -> List[float]:
    """Generate embedding using OpenAI API"""
    client = get_openai_client()
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    return response.data[0].embedding


def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for multiple texts using OpenAI API (efficient batching)"""
    client = get_openai_client()
    # OpenAI supports batch in single API call (up to ~2048 inputs)
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts
    )
    return [item.embedding for item in response.data]


# =============================================================================
# Budget Management
# =============================================================================

DEFAULT_BUDGETS = {
    "user-current-state": 15000,
    "user-biographical": 5000,
    "arlo-current-state": 15000,
    "arlo-biographical": 5000
}


# =============================================================================
# Error Handling
# =============================================================================

def error_response(error_type: str, message: str, details: dict = None) -> dict:
    """Standard error response format for all tools

    Args:
        error_type: Type of error (validation_error, database_error, api_error, etc.)
        message: Human-readable error message
        details: Optional additional error details

    Returns:
        Dict with standard error format
    """
    return {
        "status": "error",
        "error_type": error_type,
        "message": message,
        "details": details or {}
    }


def check_entry_budget(con, entry_id: str, budget: int = None) -> dict:
    """Check token budget for a single context entry

    Args:
        con: Database connection
        entry_id: KB entry ID to check
        budget: Budget limit (uses DEFAULT_BUDGETS if not specified)

    Returns:
        Dict with tokens, budget, headroom, status
    """
    if budget is None:
        budget = DEFAULT_BUDGETS.get(entry_id, 10000)

    row = con.execute(
        "SELECT content FROM knowledge WHERE id = ?",
        [entry_id]
    ).fetchone()

    if not row:
        return {
            "entry_id": entry_id,
            "tokens": 0,
            "budget": budget,
            "headroom": budget,
            "status": "missing"
        }

    content = row[0]
    tokens = len(content) // 4  # Simple approximation
    headroom = budget - tokens

    return {
        "entry_id": entry_id,
        "tokens": tokens,
        "budget": budget,
        "headroom": headroom,
        "status": "over_budget" if tokens > budget else "ok",
        "needs_offload": tokens > budget
    }
