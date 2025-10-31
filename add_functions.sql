-- Add missing macros to DuckDB knowledge base
-- These are required by the MCP server

-- =============================================================================
-- Macro: get_with_related (used by get_knowledge with include_related=true)
-- =============================================================================

CREATE OR REPLACE MACRO get_with_related(entry_id) AS TABLE
SELECT
    k.id,
    k.category,
    k.title,
    k.tags,
    k.content,
    k.metadata,
    k.created,
    k.updated,
    k.embedding,
    list(kl.to_id) FILTER (WHERE kl.to_id IS NOT NULL) as related_ids,
    list(k2.title) FILTER (WHERE k2.title IS NOT NULL) as related_titles
FROM knowledge k
LEFT JOIN knowledge_links kl ON k.id = kl.from_id
LEFT JOIN knowledge k2 ON kl.to_id = k2.id
WHERE k.id = entry_id
GROUP BY k.id, k.category, k.title, k.tags, k.content, k.metadata, k.created, k.updated, k.embedding;

-- =============================================================================
-- Macro: semantic_search (used by find_similar tool)
-- =============================================================================

CREATE OR REPLACE MACRO semantic_search(query_embedding, similarity_threshold, category_filter, result_limit) AS TABLE
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
LIMIT result_limit;

-- =============================================================================
-- Macro: hybrid_search (used by smart_search tool)
-- =============================================================================

CREATE OR REPLACE MACRO hybrid_search(query_embedding, category_filter, tag_filter, date_after, similarity_threshold, result_limit) AS TABLE
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
    similarity DESC,
    updated DESC
LIMIT result_limit;

-- =============================================================================
-- Macro: database_summary (used by get_stats tool)
-- =============================================================================

CREATE OR REPLACE MACRO database_summary() AS TABLE (
SELECT 'Total Entries' as metric, COUNT(*)::VARCHAR as value FROM knowledge
UNION ALL
SELECT 'With Embeddings', COUNT(*)::VARCHAR FROM knowledge WHERE embedding IS NOT NULL
UNION ALL
SELECT 'Categories', COUNT(DISTINCT category)::VARCHAR FROM knowledge
UNION ALL
SELECT 'Unique Tags', COUNT(DISTINCT unnest(tags))::VARCHAR FROM knowledge
UNION ALL
SELECT 'Total Links', COUNT(*)::VARCHAR FROM knowledge_links
);

-- Test the functions
SELECT 'Testing get_with_related...' as test;
SELECT * FROM get_with_related('mst-course-offering') LIMIT 1;

SELECT 'Testing database_summary...' as test;
SELECT * FROM database_summary();

SELECT 'All functions added and tested successfully!' as status;
