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
