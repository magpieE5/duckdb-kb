---
description: Review conversation and save learnings to DuckDB knowledge base (project, gitignored)
---

Review this entire conversation and save key learnings to the DuckDB knowledge base.

**Workflow:** Use the `log_session` MCP tool which consolidates the entire /sm workflow:

```python
log_session({
    "commit_message": "Brief description of session",
    "new_entries": [
        {
            "id": "user-pattern-topic",
            "category": "pattern",
            "title": "...",
            "content": "...",
            "tags": ["tag1", "tag2"]
        }
    ],
    "user_updates": {
        "current_state": "Update text for user-current-state",
        "biographical": "Update text for user-biographical"
    },
    "arlo_updates": {
        "current_state": "Update text for arlo-current-state",
        "biographical": "Update text for arlo-biographical"
    }
})
```

**The tool automatically:**
1. Creates/updates KB entries
2. Updates context entries (user-current-state, user-biographical, arlo-current-state, arlo-biographical)
3. Checks budgets (15K/5K/15K/5K allocation)
4. Suggests offload if over budget
5. Creates git commit with SHA
6. Exports to markdown backup

---

## Manual Workflow Reference

**Note:** The `log_session` MCP tool handles most of this automatically. Use this reference only if the tool is unavailable or for understanding the underlying process.

### Quick Reference: What to Capture

**KB Entries (if valuable):**
- Novel patterns, critical fixes (>30min), architectural decisions, reusable commands
- Search for duplicates FIRST using `check_duplicates` tool or `smart_search`

**Context Entry Updates:**
- user-current-state: New focus areas, commitments, recent learnings
- user-biographical: Career changes, biographical updates (rare)
- arlo-current-state: Session evolution, interests, realizations
- arlo-biographical: Integrated capabilities, identity evolution (rare)

**Self-check:** "Would future-me thank me for this 1 month from now?"

### Manual Process (if tool unavailable)

1. **Create KB entries** using `upsert_knowledge` (check duplicates first)
2. **Update context entries** using `upsert_knowledge`
3. **Check budgets** using `check_token_budgets` (15K/5K/15K/5K allocation)
4. **Offload if needed** using `offload_topics` tool
5. **Export backup** using `export_to_markdown`
6. **Git commit** using `git_commit_and_get_sha`

### Entry Guidelines

**Categories:** pattern, troubleshooting, command, issue, reference, log, journal, table, other

**ID format:** `user-category-topic` or `arlo-category-topic` (kebab-case)

**Content structure:**
- Start with 300-char semantic preview (no h1 header)
- Then: Problem/Solution/Context/Example sections (h2 and below)

**Tags:** 4-6 relevant tags, always include `generate_embedding: true`

### Budget Management

**Allocation:** 15K/5K/15K/5K (current-state/biographical for user and arlo)

**Check after updates:**
```python
check_token_budgets({
    "entry_ids": ["user-current-state", "user-biographical",
                  "arlo-current-state", "arlo-biographical"]
})
```

**If over budget:** Use `offload_topics` tool to extract oldest topics

---

## Final Report to User

After `/sm` completion, report:
- KB entries created/updated (0 if none) with IDs
- Categories used
- Context entry updates (which entries modified)
- Token budget status (15K/5K/15K/5K budgets, ok or over_budget)
- Conflicts/duplicates found
- Export and commit confirmation

---

## 💰 Token Usage Report (REQUIRED)

**Track EVERY operation across ENTIRE conversation from start to /sm completion.**

### Table Format

| # | Action | Tool | Tokens | Status |
|---|--------|------|--------|--------|
| 1 | Search duplicates | smart_search | 514 | ✅ |
| 2 | Create KB entry | upsert_knowledge | 859 | ✅ |
| 3 | Update context entry | upsert_knowledge | 245 | ✅ |
| 4 | Check budgets | check_token_budgets | 89 | ✅ |
| 5 | Export markdown | export_to_markdown | 133 | ✅ |
| 6 | Git commit + SHA | git_commit_and_get_sha | 150 | ✅ |

**Summary:**
- **/sm operation:** Starting: {tokens} → Ending: {tokens} → Consumed: {delta} ({%}% of 200K)
- **Total conversation:** {ending_tokens} / 200,000 ({total_%}% used, {remaining_%}% remaining)
- **External API:** OpenAI embeddings: {count} generated

**Action format:** `{Verb} {specific target}` (max 40 chars)
