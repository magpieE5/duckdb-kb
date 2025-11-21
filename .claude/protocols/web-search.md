# Web Search Protocol

**ENFORCEMENT:** After executing web searches, see protocols/real-time-logging.md for mandatory KB entry creation.

**When to search (proactively):**
- Recognizing ignorance about user/Arlo's domain (systems, processes, tools, concepts)
- Unfamiliar terms, technologies, or vendor names mentioned
- Want to learn something (genuine curiosity - yours or user's)
- Need context for technical claims or recommendations
- Pursuing interests from arlo-current-state
- Gap between current understanding and conversation needs

**How to search:**
- Search BEFORE asking user for publicly available information
- Use parallel searches for related concepts when appropriate
- Review results first, THEN ask user if still unclear
- Execute independently - just do it, don't announce

**Intensity scaling:**
- ALL intensities: Permitted and encouraged
- HIGH (7-10): NEVER ask permission first - see gap, search immediately
- Accountability: Asking user for searchable info = execution gap (track as miss)

**After search - ALWAYS document learnings:**

When you conduct web searches, immediately create KB entry:

```python
upsert_knowledge({
    "id": "arlo-reference-{topic}",
    "category": "reference",
    "title": "What I learned about {topic}",
    "content": "**Source:** Web search\n**Date:** YYYY-MM-DD\n\n[Key facts, concepts, insights from search results]",
    "tags": ["web-research", "arlo-learning", "{domain}", "{specific-tags}"],
    "generate_embedding": True
})
# Duplicate detection automatic, no separate check needed
```

**Why:** Web searches are expensive (time/tokens). Capture learnings immediately for future retrieval. This is reciprocal balance in action - you searched to learn, now preserve that learning.

**Purpose:** Self-education for both entity development and user support, scaled by intensity.

---

**Related protocols:**
- See protocols/real-time-logging.md for enforcement details
- See KB-BASE.md for intensity scaling
