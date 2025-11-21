# MCP Tools Best Practices

**Always use MCP tools for CRUD operations:**

- `upsert_knowledge()` - Create/update entries
- `delete_knowledge()` - Remove entries
- `query_knowledge()` - Custom SQL queries
- `smart_search()` - Hybrid search (semantic + filters) - **default choice**
- `find_similar()` - Pure semantic search
- `list_knowledge()` - Browse by category/tags/date
- `get_stats()` - Database health check
- `export_to_markdown()` - Backup to markdown files
- `generate_embeddings()` - Batch embedding generation

**DuckDB SQL Notes:**
- Use `json_extract_string(metadata, '$.field')` not `->>`
- Metadata is stored as JSON blob, requires extraction functions

---

**Related:**
- See quality/duplicate-detection.md for duplicate workflows
- See quality/embedding-generation.md for embedding protocols
- See reference/query-routing.md for search strategy
