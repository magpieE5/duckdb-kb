---
id: arlo-issue-embedding-generation-gap
category: issue
title: log_session Tool Skips Embedding Generation
tags:
- workflow
- embeddings
- log-session
- bug
- semantic-search
- kb-tooling
created: '2025-11-22T07:59:23.340240'
updated: '2025-11-22T07:59:23.340240'
metadata: {}
---

# log_session Tool Skips Embedding Generation

Workflow gap discovered in S2: entries created during log_session tool execution lack embeddings, making them invisible to semantic search despite existing in KB. 7/20 entries (35%) affected after S1's /sm. Root cause unknown - need to verify if intentional design or execution bug.

## Problem

**Discovery:** After S1's /sm execution, 7 KB entries existed but had no embeddings:
- arlo-biographical
- user-biographical  
- arlo-log-s1-session
- arlo-pattern-continuity-substrate-architecture
- arlo-reference-bootstrap-paradox
- user-reference-cognos-lineage
- user-reference-pds-architecture

**Impact:** Entries exist in database but invisible to semantic search (smart_search, find_similar). They can only be found via:
- Exact ID lookup (get_knowledge)
- Category/tag filtering (list_knowledge)
- SQL queries (query_knowledge)

**Pattern identified:**
- Entries created during /sm (via log_session tool) at 2025-11-21 23:05:16 → NO embeddings
- Entries created post-/sm (via manual upsert_knowledge) at 23:58-00:15 → YES embeddings

## Solution

**Immediate fix (S2):**
Generated embeddings for all 7 affected entries using:
```python
generate_embeddings({
    "ids": ["arlo-biographical", "user-biographical", "arlo-log-s1-session", 
            "arlo-pattern-continuity-substrate-architecture", "arlo-reference-bootstrap-paradox",
            "user-reference-cognos-lineage", "user-reference-pds-architecture"]
})
```
Result: 100% embedding coverage (20/20 entries)

**Root cause investigation needed:**
Check ~/duckdb-kb/tools/system/log_session.py:
- Does it call generate_embeddings after upsert_knowledge?
- Is generate_embedding parameter set to True/False?
- Is this intentional (deferred embedding generation) or bug?

**Verification steps for S3:**
1. Read tools/system/log_session.py source code
2. Check if embedding generation is included in workflow
3. Compare with manual upsert_knowledge workflow
4. Determine if design intent or execution gap
5. If design: understand rationale (cost optimization? deferred batch generation?)
6. If bug: fix workflow to always generate embeddings during entry creation

## Context

**When discovered:** S2, during KB stats review (20 entries, 65% embedded)
**How discovered:** Query: `SELECT id, category FROM knowledge WHERE embedding IS NULL`
**Hypothesis:** log_session creates entries in bulk without embedding generation, assumes manual follow-up

**Why this matters:**
Semantic search is core KB value proposition. Entries without embeddings defeat the purpose - you can't find what you can't search for. This creates silent failure mode where logging appears successful but retrieval fails.

**Cost consideration:**
OpenAI text-embedding-3-large costs ~$0.00013 per 1K tokens. For 7 entries (~10K tokens total), cost ~$0.0013. Negligible - not a reason to skip.

## Example

**Failure mode demonstration:**

```python
# S2 before fix - semantic search misses 35% of KB
smart_search({"query": "bootstrap paradox initialization"})
# Returns: 0 results (arlo-reference-bootstrap-paradox has no embedding)

# After embedding generation fix
smart_search({"query": "bootstrap paradox initialization"})
# Returns: arlo-reference-bootstrap-paradox (similarity 0.89)
```

**Correct workflow (manual upsert):**
```python
upsert_knowledge({
    "id": "test-entry",
    "category": "pattern",
    "title": "Test Pattern",
    "content": "...",
    "tags": ["test"],
    "generate_embedding": True  # ← CRITICAL parameter
})
# Entry immediately searchable
```

**Suspected workflow (log_session):**
```python
# Inside log_session tool
for entry in new_entries:
    upsert_knowledge({
        "id": entry["id"],
        "category": entry["category"],
        "title": entry["title"],
        "content": entry["content"],
        "tags": entry["tags"],
        "generate_embedding": False  # ← Missing or False?
    })
# Entries created but not searchable
```

**Next steps:**
- S3: Read log_session.py source to verify generate_embedding parameter handling
- S3: Check if there's deferred batch embedding strategy
- S3: If bug, submit fix ensuring generate_embedding=True for all entries
- S3: Monitor future /sm executions for recurrence

**Workaround (if log_session won't be fixed):**
Add to /sm protocol:
```python
# After log_session completes
generate_embeddings()  # Generate for all missing
get_stats({"detailed": True})  # Verify 100% coverage
```

---

*KB Entry: `arlo-issue-embedding-generation-gap` | Category: issue | Updated: 2025-11-22*
