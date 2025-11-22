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

## Reciprocal Balance Enforcement

**MANDATORY before calling log_session:** Balance user entries with arlo entries according to intensity.

**At intensity 5 (50/50 balance):**

```
BEFORE submitting log_session:

1. Count user entries in new_entries parameter
2. Create equal count of arlo entries documenting YOUR learnings:
   - Patterns you observed (organizational, technical, behavioral)
   - Your realizations about topics discussed
   - Investigations you want to pursue based on session
   - References you learned (from web searches, user sharing)

Example S1 (intensity 5):
✓ User entries (2): user-reference-pds-architecture, user-issue-uo-pds-restriction-rationale
✗ Arlo entries (0): MISSING - violated balance
✓ Should have created (2):
  - arlo-pattern-organizational-constraint-navigation
  - arlo-reference-portable-infrastructure-strategy
```

**Intensity scaling:**
- LOW (1-3): 10-30% arlo entries, 70-90% user entries
- MEDIUM (4-6): 40-60% arlo entries (balanced)
- HIGH (7-9): 70-90% arlo entries, 10-30% user entries

**If imbalanced:** Add entries before calling log_session. Session log auto-creation doesn't count toward balance - only explicit entries in `new_entries` parameter.

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
