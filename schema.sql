-- DuckDB Knowledge Base Schema (v1.5.0)
-- Hybrid SQL + Vector Semantic Search
-- Last updated: 2025-11-08
-- Consolidated: All macros now included in this file

-- Install and load VSS extension for vector similarity search
INSTALL vss;
LOAD vss;

-- =============================================================================
-- MAIN KNOWLEDGE TABLE
-- =============================================================================

-- NOTE: Using CREATE IF NOT EXISTS to preserve existing data
-- If you need to modify the schema, use ALTER TABLE or migrate data first

CREATE TABLE IF NOT EXISTS knowledge (
    -- Identity
    id VARCHAR PRIMARY KEY,  -- Creates automatic ART index

    -- Metadata
    category VARCHAR NOT NULL,  -- 'table', 'command', 'issue', 'pattern', 'troubleshooting'
    title VARCHAR NOT NULL,
    tags VARCHAR[] DEFAULT [],

    -- Content
    content TEXT NOT NULL,

    -- Flexible structured data
    metadata JSON DEFAULT '{}'::JSON,

    -- Vector embedding for semantic search (nullable for lazy generation)
    embedding FLOAT[3072] DEFAULT NULL,  -- Using OpenAI text-embedding-3-large (3072 dimensions)

    -- Timestamps
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- INDEXES
-- =============================================================================

-- ART indexes for fast SQL filtering
-- Note: DuckDB uses columnar storage, so indexes are optional for small datasets
CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge(category);
CREATE INDEX IF NOT EXISTS idx_knowledge_updated ON knowledge(updated);

-- HNSW index for vector similarity search (using VSS extension)
-- Provides 10-50x speedup for semantic search on datasets >1K entries
-- Note: Requires hnsw_enable_experimental_persistence = true for persistent databases
SET hnsw_enable_experimental_persistence = true;
CREATE INDEX IF NOT EXISTS idx_knowledge_embedding_hnsw ON knowledge USING HNSW(embedding);

-- =============================================================================
-- VIEWS
-- =============================================================================

-- Recent knowledge (last 30 days)
CREATE OR REPLACE VIEW recent_knowledge AS
SELECT
    id,
    category,
    title,
    tags,
    content,
    metadata,
    created,
    updated
FROM knowledge
WHERE updated > CURRENT_TIMESTAMP - INTERVAL 30 DAYS
ORDER BY updated DESC;

-- Knowledge statistics by category
CREATE OR REPLACE VIEW knowledge_stats AS
SELECT
    category,
    COUNT(*) as count,
    COUNT(embedding) as embeddings_generated,
    (COUNT(embedding)::FLOAT / COUNT(*)::FLOAT * 100)::INTEGER as embedding_pct,
    MIN(created) as oldest,
    MAX(updated) as newest
FROM knowledge
GROUP BY category
ORDER BY count DESC;

-- Tag frequency analysis
CREATE OR REPLACE VIEW tag_usage AS
SELECT
    t.tag,
    COUNT(*) as usage_count,
    list(DISTINCT k.category) as used_in_categories
FROM knowledge k, UNNEST(k.tags) AS t(tag)
GROUP BY t.tag
ORDER BY usage_count DESC;

-- =============================================================================
-- MACROS (Functions used by MCP tools)
-- =============================================================================

-- Macro: semantic_search (used by find_similar tool)
CREATE OR REPLACE MACRO semantic_search(query_embedding, similarity_threshold, category_filter, result_limit) AS TABLE (
SELECT
    id,
    category,
    title,
    tags,
    content,
    metadata,
    array_cosine_similarity(embedding, query_embedding) as similarity,
    created,
    updated
FROM knowledge
WHERE
    embedding IS NOT NULL
    AND (category_filter IS NULL OR category = category_filter)
    AND array_cosine_similarity(embedding, query_embedding) > similarity_threshold
ORDER BY similarity DESC
LIMIT result_limit
);

-- Macro: hybrid_search (used by smart_search tool)
-- Full-spectrum search: exact matches + semantic matches
CREATE OR REPLACE MACRO hybrid_search(query_text, query_embedding, category_filter, tag_filter, date_after, similarity_threshold, result_limit) AS TABLE (
WITH exact_matches AS (
    -- Exact/LIKE matches get perfect score (1.0)
    SELECT
        id,
        category,
        title,
        tags,
        content,
        metadata,
        1.0 AS similarity,
        'exact' AS match_type,
        created,
        updated
    FROM knowledge
    WHERE
        (LOWER(id) LIKE LOWER('%' || query_text || '%')
         OR LOWER(content) LIKE LOWER('%' || query_text || '%')
         OR LOWER(title) LIKE LOWER('%' || query_text || '%')
         OR ARRAY_TO_STRING(tags, ',') LIKE LOWER('%' || query_text || '%'))
        AND (category_filter IS NULL OR category = category_filter)
        AND (tag_filter IS NULL OR list_has_any(tags, tag_filter))
        AND (date_after IS NULL OR updated > date_after)
),
semantic_matches AS (
    -- Semantic matches scored by embedding similarity
    SELECT
        id,
        category,
        title,
        tags,
        content,
        metadata,
        array_cosine_similarity(embedding, query_embedding) AS similarity,
        'semantic' AS match_type,
        created,
        updated
    FROM knowledge
    WHERE
        embedding IS NOT NULL
        AND (category_filter IS NULL OR category = category_filter)
        AND (tag_filter IS NULL OR list_has_any(tags, tag_filter))
        AND (date_after IS NULL OR updated > date_after)
        AND array_cosine_similarity(embedding, query_embedding) > similarity_threshold
)
-- Combine and deduplicate (keep highest score per ID)
SELECT DISTINCT ON (id)
    id,
    category,
    title,
    tags,
    content,
    metadata,
    similarity,
    match_type,
    created,
    updated
FROM (
    SELECT * FROM exact_matches
    UNION ALL
    SELECT * FROM semantic_matches
) combined
ORDER BY
    id,
    similarity DESC,
    updated DESC
LIMIT result_limit
);

-- Macro: database_summary (used by get_stats tool)
CREATE OR REPLACE MACRO database_summary() AS TABLE (
SELECT 'Total Entries' as metric, COUNT(*)::VARCHAR as value FROM knowledge
UNION ALL
SELECT 'With Embeddings', COUNT(*)::VARCHAR FROM knowledge WHERE embedding IS NOT NULL
UNION ALL
SELECT 'Categories', COUNT(DISTINCT category)::VARCHAR FROM knowledge
UNION ALL
SELECT 'Unique Tags', (SELECT COUNT(DISTINCT t.tag) FROM knowledge k, UNNEST(k.tags) AS t(tag))::VARCHAR
);
