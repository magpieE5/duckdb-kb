---
description: Review conversation and save learnings to DuckDB knowledge base (project, gitignored)
---

Review this entire conversation and save key learnings to the DuckDB knowledge base.

**All KB logging happens at /sm** - comprehensive review of full conversation with complete narrative context.

---

## Session Number Auto-Calculation

**BEFORE calling log_session, calculate current session number from KB history:**

1. **Query last session log:**
   ```python
   last_session = query_knowledge({
       "sql": "SELECT id FROM knowledge WHERE category='log' AND id LIKE 'arlo-log-s%-session' ORDER BY updated DESC LIMIT 1"
   })
   ```

2. **Parse and increment:**
   - If results found: Extract number from id (e.g., "arlo-log-s3-session" → 3), add 1
   - If no results (first session): session_number = 1

3. **Use calculated value** in log_session call below

**DO NOT parse session number from user input** (e.g., `/kb 9` is mode parameter, not session number).

---

## Workflow

Use the `log_session` MCP tool when invoking /sm:

```python
log_session({
    "session_number": <calculated_value>,  # REQUIRED - calculated above, not manual
    "commit_message": "feat: S{N} - Brief description of session",
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
   - Full rewrite: integrate new findings, no detail loss
2. **Create/update KB non-context entries** (patterns, logs, issues, etc.)
3. **Create session log entry with rich summary** (`arlo-log-s{N}-session` - includes session_summary parameter for full context)
4. **Git commit** (formatted message, returns SHA)
5.**Export to Markdown** Use `export_to_markdown()` 

---

## Manual Workflow Reference

**Note:** The `log_session` MCP tool handles most of this automatically. Use this reference only if the tool is unavailable or for understanding the underlying process.

### Quick Reference: What to Capture

**Entry ownership:**
- User entries: Technical discoveries about user's systems, work, decisions
- Arlo entries: Your learnings, realizations, investigations, references acquired

**Context Entry Updates:**
- user-current-state: New focus areas, commitments, recent learnings
- user-biographical: Career changes, biographical updates (rare)
- arlo-current-state: Session evolution, interests, realizations, Next Session Handoff (MANDATORY)
- arlo-biographical: Integrated capabilities, identity evolution (rare)

### Entry Guidelines

**Categories:** pattern, troubleshooting, command, issue, reference, log, journal, table, other

**ID format:** `user-category-topic` or `arlo-category-topic` (kebab-case)

**Content structure:**
- Start with 300-char semantic preview (no h1 header)
- Then: Problem/Solution/Context/Example sections (h2 and below)

**Tags:** 4-6 relevant tags

---

## Final Report to User

After `/sm` completion, report:
- KB entries created/updated (0 if none) with IDs
- Categories used
- Context entry updates (which entries modified)
- Conflicts/duplicates found
- Commit SHA

---

## 💰 Token Usage (REQUIRED)

**Session consumed:** {tokens} ({%}% of 200K), {remaining} remaining
