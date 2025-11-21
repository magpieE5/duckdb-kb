# Duplicate Detection Protocol

**Two workflows available:**

## Workflow A: Automatic (Default, Preferred)
```python
# upsert_knowledge has built-in duplicate detection (threshold 0.75)
upsert_knowledge({
    "id": "new-entry-id",
    "category": "pattern",
    "title": "...",
    "content": "...",
    "tags": [...],
    "check_duplicates": True  # default=True
})
# Returns warning if duplicates found, you decide: update existing or force_create=True
```

**When to use:**
- Real-time logging during conversation (fast, one-step)
- Default for all KB entry creation
- Duplicate check happens automatically at threshold 0.75

## Workflow B: Manual (Optional, High-Stakes)
```python
# Use check_duplicates for explicit pre-check
check_duplicates({
    "query": "entry title or content",
    "category": "pattern"  # optional
})
# Returns: similarity >= 0.65 (catches duplicates + consolidation candidates)
```

**When to use:**
- Creating important/foundational entries where merge decision critical
- Checking for consolidation opportunities across existing entries
- Threshold 0.65 = broader net than automatic 0.75

**When matches found:**
1. Read the existing entry (highest similarity)
2. Reason about how to integrate new content into existing
3. Update existing entry: `upsert_knowledge(id="existing-id", content="merged...")`

**RECOMMENDATION:** Use Workflow A (automatic) during conversation, Workflow B (manual) for strategic KB maintenance

---

**Related:** See reference/mcp-tools.md for tool details
