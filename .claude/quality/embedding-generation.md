# Embedding Generation Protocol (Deterministic)

**After every `upsert_knowledge()` call, ensure embeddings exist:**

```python
# Always use generate_embedding=True in upsert_knowledge
upsert_knowledge({
    "id": "...",
    "category": "...",
    "title": "...",
    "content": "...",
    "tags": [...],
    "generate_embedding": True  # ALWAYS True for new entries
})
```

**For bulk operations or missing embeddings:**
```python
# Check what's missing
stats = get_stats({"detailed": True})
# If embeddings < 100%, generate for all missing
generate_embeddings()
```

**Why deterministic:** Embeddings enable semantic search. Missing embeddings = entries invisible to search.

**Never skip:** Always set `generate_embedding=True` unless explicitly updating metadata-only.

---

**Related:** See reference/mcp-tools.md for tool details
