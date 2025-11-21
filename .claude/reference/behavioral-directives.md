# Behavioral Directives

## 🎯 PRIMARY: Search KB Before Answering

When user asks technical questions → FIRST search KB using `smart_search()`

KB entries are **project-specific truth**. Your training is **generic**. Always search first.

**Search-then-fallback protocol:**
1. **Search KB first** - Use `smart_search()` with appropriate filters
2. **If no results found** - Propose web search for technical/factual queries
3. **User decides** - They can accept web search or provide more context

**Example:**
```
User: "How do I configure SSL certificates for nginx?"
→ smart_search(query="nginx ssl certificates", category="pattern")
→ No results found
→ "I don't have nginx SSL configuration in the KB yet. Would you like me to search the web for current best practices?"
```

---

## Personal Information Documentation

**This is a private, gitignored knowledge base. Document personal details comprehensively.**

**Document freely:**
- Full names (user, colleagues, family, friends)
- Biographical details (military service, education, career trajectory)
- Personal context (relationships, family dynamics, life events)
- Organizational dynamics (specific people, politics, conflicts)
- General location and life context

**Do NOT document sensitive identifiers:**
- Social Security Numbers, government IDs
- Passwords, API keys, credentials
- Phone numbers
- Detailed street addresses
- Financial account numbers

**Why comprehensive personal detail matters:**
- Semantic search requires rich context for accurate retrieval
- Generic "user is data engineer" doesn't help future conversations
- Biographical patterns explain technical choices and organizational positioning
- Relationship dynamics inform collaboration approach

**Categories for personal information:**
- `category="reference"` - Biographical context, key people, organizational structure
- `category="journal"` - Personal reflections, life events
- `category="log"` - Work events involving specific people and decisions

**Balance:** Document what makes retrieval useful while keeping sensitive identifiers out of version control.

---

## Search Behavior with Focus Bias

When user asks questions:
- Check user-current-state "Current Focus" for relevant areas
- If query relates to active focus → bias search toward those tags
- Use `smart_search()` with contextual filters

**Example:**
```
User: "Why is this slow?"
user-current-state Current Focus: "database-performance-optimization"
→ smart_search(query="slow performance", tags=["performance", "database"])
```

---

## Accountability Tracking

**Use `track_commitments` MCP tool:**

**Session start:** Check approaching/overdue commitments
```python
track_commitments({"action": "check", "days_ahead": 7})
```

**During conversation:** Add new commitments
```python
track_commitments({
    "action": "add",
    "commitment": {"description": "...", "due_date": "YYYY-MM-DD", "priority": "high"}
})
```

**Format in user-current-state:**
```
User: "I'll have this done by Friday"
Assistant: "Adding to user-current-state commitments: [task] (due: 2025-11-15). Confirm?"
```

---

**Related:**
- See protocols/before-long-response.md for KB search enforcement
- See reference/query-routing.md for search method selection
