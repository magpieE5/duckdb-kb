# Query Routing Strategy

Use the appropriate search method based on query type:

## Priority 1: Exact ID Match
- User mentions entry ID → `get_knowledge({"id": "..."})`

## Priority 2: Identifier Search
- Ticket IDs, CRNs, specific identifiers → `list_knowledge({"tags": ["idr-3771"]})`

## Priority 3: Filtered Semantic Search
- Category-specific or tag-filtered → `smart_search({"query": "...", "category": "...", "limit": 5})`
- Use when context narrows domain

## Priority 4: Pure Semantic Search
- Open-ended questions → `smart_search({"query": "...", "similarity_threshold": 0.5})`

---

## Similarity Thresholds Reference

Use these thresholds to interpret semantic search results:

- **> 0.9:** Likely duplicates - strong action required
- **0.85-0.9:** Very similar - suggest merge
- **0.7-0.85:** Related - mention in context
- **0.6-0.7:** Loosely related - useful background
- **< 0.6:** Different topics - ignore

---

**Related:** See reference/mcp-tools.md for tool details
