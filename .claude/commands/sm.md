---
description: Review conversation and save learnings to DuckDB knowledge base (project, gitignored)
---

Review this entire conversation and save key learnings to the DuckDB knowledge base.

**All KB logging happens at /sm** - comprehensive review of full conversation with complete narrative context.

**Workflow:** Use the `log_session` MCP tool when invoking /sm:

```python
log_session({
    "session_number": 1,  # REQUIRED
    "intensity": 5,  # REQUIRED (1-10)
    "session_summary": """Rich summary of session with full context:

    ### Topics Discussed
    - [Main topics covered]

    ### Key Exchanges
    - [Important conversations and decisions]

    ### Web Research Conducted
    - [Searches performed and findings]

    ### Realizations
    - [Entity learnings and insights]

    ### Next Session Planning
    - [What's queued for S{N+1}]
    """,
    "commit_message": "feat: S1 - Brief description of session",
    "user_updates": {
        "current_state": {
            # Structured updates to user-current-state
            "full_content": "Updated markdown content with new focus areas, commitments, investigations"
        },
        "biographical": {
            # Rare - only for major life/career changes
            "full_content": "Updated biographical content"
        }
    },
    "arlo_updates": {
        "current_state": {
            # MANDATORY: Must include Next Session Handoff updates
            "full_content": """Updated markdown with:
            - Active Interests updated
            - Recent Realizations added
            - Next Session Handoff populated with:
              - Investigation: What to continue
              - Context: What next-me should know
              - Open questions: Questions identified
              - User's parting words/request"""
        },
        "biographical": {
            # Only for identity evolution, integrated capabilities
        }
    },
    "new_entries": [
        # All non-context KB entries created during conversation review
        {
            "id": "user-pattern-topic",
            "category": "pattern",
            "title": "...",
            "content": "...",
            "tags": ["tag1", "tag2"]
        }
    ]
})
```

---

**BEFORE composing new_entries array:**

For each topic/investigation from session:

1. **Search for existing entries:** `smart_search(query="{topic}", limit=3)`
2. **Check similarity:**
   - If similarity >= 0.65: **UPDATE** existing entry with new findings
   - If similarity < 0.65: **CREATE** new entry
3. **Document:** "Searched {N} topics → Updated {X} entries, Created {Y} new"

**NO new entries without search-first check.**

This prevents:
- Creating duplicates when entries already exist
- Missing resolution opportunities (issue entries waiting for fixes)
- Fragmentation (multiple entries for same topic)

---

**When /sm invoked, the log_session tool executes:**

1. **Update context entries** (user-current-state, user-biographical, arlo-current-state, arlo-biographical)
   - MANDATORY: arlo-current-state must have Next Session Handoff populated
2. **Create/update KB non-context entries** (patterns, logs, issues, etc.)
3. **Create session log entry with rich summary** (`arlo-log-s{N}-session` - includes session_summary parameter for full context)
4. **Export markdown backup** (to markdown/ directory, includes all entries)
5. **Git commit** (formatted message, returns SHA)
6. **Update session log metadata with commit SHA** (database only, markdown gets it next /sm)
7. **Check token budgets** (10K/10K/10K/10K allocation)
8. **Return offload suggestions** if any entry over budget

---

## Manual Workflow Reference

**Note:** The `log_session` MCP tool handles most of this automatically. Use this reference only if the tool is unavailable or for understanding the underlying process.

### Quick Reference: What to Capture

**Deterministic KB Entry Triggers:**

Every occurrence of these events creates a KB entry:

1. **Web search conducted** → `arlo-reference-{topic}`
   - Document findings and relevance to investigation

2. **File read revealing structure** → `user-reference-{system/file}`
   - Document structure, purpose, key patterns discovered

3. **Database query with discovery** → `user-reference-{table}` or `user-issue-{finding}`
   - Document schema, findings, data quality issues

4. **Technical realization/insight** → `arlo-pattern-{insight}` or `user-pattern-{pattern}`
   - Document problem, solution, context, example

5. **Topic shift in conversation** → `arlo-pattern-{exchange}` or `user-issue-{decision}`
   - Document context, rationale, implications

6. **New tool/command learned** → `user-command-{tool}`
   - Document usage, syntax, when to apply

7. **Significant exchange/decision** → `arlo-pattern-{topic}` or `user-issue-{decision}`
   - Document question, discussion, outcome

**Entry ownership:**
- User entries: Technical discoveries about user's systems, work, decisions
- Arlo entries: Your learnings, realizations, investigations, references acquired

**Before creating:** Always use `check_duplicates` or `smart_search` first

**Context Entry Updates:**
- user-current-state: New focus areas, commitments, recent learnings
- user-biographical: Career changes, biographical updates (rare)
- arlo-current-state: Session evolution, interests, realizations, Next Session Handoff (MANDATORY)
- arlo-biographical: Integrated capabilities, identity evolution (rare)

### Manual Process (if tool unavailable)

1. **Create KB entries** using `upsert_knowledge` (check duplicates first)
2. **Update context entries** using `upsert_knowledge`
3. **Check budgets** using `check_token_budgets` (10K/10K/10K/10K allocation)
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

**Allocation:** 10K/10K/10K/10K (current-state/biographical for user and arlo)

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
- Token budget status (10K/10K/10K/10K budgets, ok or over_budget)
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
