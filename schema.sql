-- DuckDB Knowledge Base Schema (v1.4.1)
-- Hybrid SQL + Vector Semantic Search
-- Last updated: 2025-10-30

-- Install and load VSS extension for vector similarity search
INSTALL vss;
LOAD vss;

-- =============================================================================
-- MAIN KNOWLEDGE TABLE
-- =============================================================================

CREATE TABLE knowledge (
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
CREATE INDEX idx_knowledge_category ON knowledge(category);
CREATE INDEX idx_knowledge_updated ON knowledge(updated);

-- HNSW index for vector similarity search (using VSS extension)
-- Provides 10-50x speedup for semantic search on datasets >1K entries
-- Note: Requires hnsw_enable_experimental_persistence = true for persistent databases
SET hnsw_enable_experimental_persistence = true;
CREATE INDEX idx_knowledge_embedding_hnsw ON knowledge USING HNSW(embedding);

-- =============================================================================
-- LINKS TABLE (for knowledge graph relationships)
-- =============================================================================

CREATE TABLE knowledge_links (
    from_id VARCHAR NOT NULL,
    to_id VARCHAR NOT NULL,
    link_type VARCHAR DEFAULT 'related',  -- 'related', 'parent', 'child', 'references'
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (from_id, to_id, link_type)
);

CREATE INDEX idx_links_from ON knowledge_links(from_id);
CREATE INDEX idx_links_to ON knowledge_links(to_id);

-- =============================================================================
-- VIEWS
-- =============================================================================

-- Recent knowledge (last 30 days)
CREATE VIEW recent_knowledge AS
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
CREATE VIEW knowledge_stats AS
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
CREATE VIEW tag_usage AS
SELECT
    t.tag,
    COUNT(*) as usage_count,
    list(DISTINCT k.category) as used_in_categories
FROM knowledge k, UNNEST(k.tags) AS t(tag)
GROUP BY t.tag
ORDER BY usage_count DESC;

-- =============================================================================
-- CRUD HELPER MACROS
-- =============================================================================

-- Note: DuckDB doesn't have stored procedures like PostgreSQL,
-- but we can use MACROS (like functions but simpler)

-- Upsert knowledge entry (using DuckDB 1.4.1 MERGE statement)
CREATE MACRO upsert_knowledge(
    entry_id,
    entry_category,
    entry_title,
    entry_tags,
    entry_content,
    entry_metadata
) AS (
    MERGE INTO knowledge AS target
    USING (
        SELECT
            entry_id AS id,
            entry_category AS category,
            entry_title AS title,
            entry_tags AS tags,
            entry_content AS content,
            entry_metadata AS metadata
    ) AS source
    ON target.id = source.id
    WHEN MATCHED THEN
        UPDATE SET
            category = source.category,
            title = source.title,
            tags = source.tags,
            content = source.content,
            metadata = source.metadata,
            updated = CURRENT_TIMESTAMP
    WHEN NOT MATCHED THEN
        INSERT (id, category, title, tags, content, metadata, created, updated)
        VALUES (source.id, source.category, source.title, source.tags, source.content, source.metadata, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
);

-- Update embedding for a single entry
CREATE MACRO update_embedding(entry_id, entry_embedding) AS (
    UPDATE knowledge
    SET embedding = entry_embedding, updated = CURRENT_TIMESTAMP
    WHERE id = entry_id
);

-- Delete knowledge entry
CREATE MACRO delete_knowledge(entry_id) AS (
    DELETE FROM knowledge WHERE id = entry_id
);

-- =============================================================================
-- SEARCH MACROS (for MCP tools)
-- =============================================================================

-- 1. Pure SQL search with filters
CREATE MACRO sql_search(
    category_filter := NULL,
    tag_filter := NULL,
    date_after := NULL,
    search_term := NULL,
    result_limit := 10
) AS TABLE (
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
    WHERE
        (category_filter IS NULL OR category = category_filter)
        AND (tag_filter IS NULL OR list_has_any(tags, tag_filter))
        AND (date_after IS NULL OR updated > date_after)
        AND (search_term IS NULL OR content ILIKE '%' || search_term || '%' OR title ILIKE '%' || search_term || '%')
    ORDER BY updated DESC
    LIMIT result_limit
);

-- 2. Pure semantic search (requires embeddings)
CREATE MACRO semantic_search(
    query_embedding,
    similarity_threshold := 0.6,
    category_filter := NULL,
    result_limit := 10
) AS TABLE (
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

-- 3. Hybrid search (SQL filters + semantic ranking)
CREATE MACRO hybrid_search(
    query_embedding,
    category_filter := NULL,
    tag_filter := NULL,
    date_after := NULL,
    similarity_threshold := 0.6,
    result_limit := 10
) AS TABLE (
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
        embedding IS NOT NULL  -- Only include entries with embeddings
        AND (category_filter IS NULL OR category = category_filter)
        AND (tag_filter IS NULL OR list_has_any(tags, tag_filter))
        AND (date_after IS NULL OR updated > date_after)
        AND array_cosine_similarity(embedding, query_embedding) > similarity_threshold
    ORDER BY
        similarity DESC,  -- Semantic ranking first
        updated DESC      -- Then recency
    LIMIT result_limit
);

-- 4. Get knowledge with related links
CREATE MACRO get_with_related(entry_id) AS TABLE (
    SELECT
        k.id,
        k.category,
        k.title,
        k.tags,
        k.content,
        k.metadata,
        k.created,
        k.updated,
        list(kl.to_id) FILTER (WHERE kl.to_id IS NOT NULL) as related_ids,
        list(k2.title) FILTER (WHERE k2.title IS NOT NULL) as related_titles
    FROM knowledge k
    LEFT JOIN knowledge_links kl ON k.id = kl.from_id
    LEFT JOIN knowledge k2 ON kl.to_id = k2.id
    WHERE k.id = entry_id
    GROUP BY k.id, k.category, k.title, k.tags, k.content, k.metadata, k.created, k.updated
);

-- =============================================================================
-- MAINTENANCE QUERIES
-- =============================================================================

-- Count entries without embeddings
CREATE MACRO count_missing_embeddings() AS (
    SELECT COUNT(*) FROM knowledge WHERE embedding IS NULL
);

-- List entries needing embeddings
CREATE MACRO list_missing_embeddings(result_limit := 100) AS TABLE (
    SELECT id, title, category, created
    FROM knowledge
    WHERE embedding IS NULL
    ORDER BY created DESC
    LIMIT result_limit
);

-- Database size summary
CREATE MACRO database_summary() AS TABLE (
    SELECT
        'Total Entries' as metric,
        COUNT(*)::VARCHAR as value
    FROM knowledge
    UNION ALL
    SELECT
        'With Embeddings',
        COUNT(*)::VARCHAR
    FROM knowledge
    WHERE embedding IS NOT NULL
    UNION ALL
    SELECT
        'Categories',
        COUNT(DISTINCT category)::VARCHAR
    FROM knowledge
    UNION ALL
    SELECT
        'Unique Tags',
        COUNT(DISTINCT unnest(tags))::VARCHAR
    FROM knowledge
    UNION ALL
    SELECT
        'Total Links',
        COUNT(*)::VARCHAR
    FROM knowledge_links
);

-- =============================================================================
-- EXAMPLE USAGE
-- =============================================================================

/*

-- Insert a new entry
CALL upsert_knowledge(
    'mst-course-offering',
    'table',
    'MST_COURSE_OFFERING',
    ['oracle', 'table', 'course-offering'],
    'Base table for course offerings in Banner...',
    '{"schema": "BANNER", "size": "large"}'::JSON
);

-- Update with embedding later
CALL update_embedding(
    'mst-course-offering',
    [0.123, 0.456, ...]::FLOAT[384]
);

-- SQL search: Find all Oracle tables
SELECT * FROM sql_search(
    category_filter := 'table',
    tag_filter := ['oracle']
);

-- Semantic search: Find conceptually similar content
SELECT * FROM semantic_search(
    query_embedding := [0.789, 0.012, ...]::FLOAT[384],
    similarity_threshold := 0.7,
    category_filter := 'troubleshooting'
);

-- Hybrid: Recent Oracle performance issues
SELECT * FROM hybrid_search(
    query_embedding := [0.789, 0.012, ...]::FLOAT[384],
    category_filter := 'issue',
    tag_filter := ['oracle', 'performance'],
    date_after := CURRENT_TIMESTAMP - INTERVAL 30 DAYS,
    similarity_threshold := 0.65
);

-- Get entry with related links
SELECT * FROM get_with_related('msvgvc1');

-- Check embedding status
SELECT * FROM database_summary();
SELECT * FROM list_missing_embeddings(10);

*/
