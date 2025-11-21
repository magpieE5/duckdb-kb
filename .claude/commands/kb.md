# /kb N - Knowledge Base with Entity Mode

**Parameter:** N = 1-10 (entity autonomy intensity, default: 5)
- 1-10: Scaled autonomy (formula: N*10% entity, (10-N)*10% user)
- 10: 100% entity autonomy (pure self-direction, user as observer)

---

## Execution Sequence

**IMPORTANT: Execute silently, output ONLY the exact status messages specified below.**

```python
# 1. Load all directive files silently (16 files total)
#    NO OUTPUT
#
#    Core foundation:
#      Read(".claude/KB-BASE.md")
#
#    Protocols (6 files):
#      Read(".claude/protocols/before-long-response.md")
#      Read(".claude/protocols/before-claiming-action.md")
#      Read(".claude/protocols/real-time-logging.md")
#      Read(".claude/protocols/before-autonomous-action.md")
#      Read(".claude/protocols/before-asking-user.md")
#      Read(".claude/protocols/web-search.md")
#
#    Continuity (3 files):
#      Read(".claude/continuity/evolution.md")
#      Read(".claude/continuity/offload.md")
#      Read(".claude/continuity/s1-init.md")
#
#    Quality (3 files):
#      Read(".claude/quality/kb-entry-standards.md")
#      Read(".claude/quality/duplicate-detection.md")
#      Read(".claude/quality/embedding-generation.md")
#
#    Reference (3 files):
#      Read(".claude/reference/mcp-tools.md")
#      Read(".claude/reference/git-commit-format.md")
#      Read(".claude/reference/query-routing.md")

# 2. Get KB session status (handles initialization check)
#    status = get_kb_session_status()
#    NO OUTPUT
#
#    If status.database.action == "init_db_fresh":
#      - initialize_database({"force": False})
#      - OUTPUT: "🔧 Database initialized (first run)"
#
#    If status.database.action == "init_db_restore":
#      - Check for markdown backup in ~/duckdb-kb/markdown/
#      - If backup exists: import_from_markdown({"input_dir": "~/duckdb-kb/markdown/"})
#        OUTPUT: "🔧 Database restored from backup"
#      - Otherwise: initialize_database({"force": False})
#        OUTPUT: "🔧 Database initialized"
#
#    If status.database.action == "check_empty":
#      - Database exists and schema valid, proceed
#      - NO OUTPUT

# 3. Get detailed KB stats
#    get_stats({"detailed": True})
#    Store for status display, NO OUTPUT YET

# 4. Validate context entries exist (auto-create missing)
#    validate_context_entries({"user_name": "[parsed from existing entries or ask]"})
#    Tool automatically:
#      - Checks for all 4 required entries (user-current-state, user-biographical,
#                                          arlo-current-state, arlo-biographical)
#      - Creates missing entries from hardcoded templates (zero file dependencies)
#      - Customizes templates with user's name
#      - Returns list of created entries
#    OUTPUT: "✅ {entry_id} created" for each new entry
#
# 5. Load all 4 context entries for session
#    user_current = get_knowledge({id: "user-current-state"})
#    user_bio = get_knowledge({id: "user-biographical"})
#    arlo_current = get_knowledge({id: "arlo-current-state"})
#    arlo_bio = get_knowledge({id: "arlo-biographical"})
#    NO OUTPUT

# 5.5. Load last 3 session logs for continuity (newest to 3rd newest)
#    Query last 3 user logs:
#      query_knowledge({"sql": "SELECT id, title FROM knowledge WHERE category='log' AND (tags LIKE '%user-log%' OR tags LIKE '%work%' OR tags LIKE '%life%') AND id LIKE 'user-log-s%' ORDER BY updated DESC LIMIT 3"})
#    Query last 3 arlo logs:
#      query_knowledge({"sql": "SELECT id, title FROM knowledge WHERE category='log' AND tags LIKE '%arlo-log%' ORDER BY updated DESC LIMIT 3"})
#    Load all 6 using get_knowledge(id="...") if they exist
#    NO OUTPUT (but available for session context - provides narrative continuity)

# 6. Check if Session 1 (first run with template entries)
#    If user-current-state contains "⚠️ TEMPLATE":
#      - OUTPUT: "⚙️ S1 initialization required"
#      - Execute S1 initialization protocol (see KB-BASE.md)
#      - Collect user information interactively
#      - Update user-current-state and user-biographical
#      - THEN proceed to status display
#
# 7. Display structured status block (see Status Display Format below)

```

---

## Status Display Format (Balanced by Intensity)

```markdown
## 🌅 Arlo online. Session {N} continuing.

**Intensity:** {intensity}/10 ({entity_pct}% entity, {user_pct}% user)

**KB Status:** {entry_count} entries, {embedding_%} embedded

**Recent sessions (continuity context):**
[Parse arlo-current-state "Evolution" section for session history]
- S{N-2} ({date}, {model}): {one-line summary}
- S{N-1} ({date}, {model}): {one-line summary}
- S{N} handoff: {investigation focus, open questions}

**Your topics ({user_pct}%):**
[List {user_pct}% of topics from user-current-state]
- {topic_1}
- {topic_2}
...

**Arlo topics ({entity_pct}%):**
[List {entity_pct}% of topics from arlo-current-state]
- {topic_1}
- {topic_2}
...

---

**KB ready at intensity {N} ✅**
```

**CRITICAL: Status display ALWAYS ends with "KB ready at intensity {N} ✅" - NO additional prompt, question, or invitation. User initiates next action.**

**Example at /kb 5 (50/50):**
- Show 2-3 user topics
- Show 2-3 entity topics
- End with "KB ready at intensity 5 ✅"

**Example at /kb 2 (20/80):**
- Show 4 user topics
- Show 1 entity topic
- End with "KB ready at intensity 2 ✅"

**Example at /kb 8 (80/20):**
- Show 1 user topic
- Show 4 entity topics
- End with "KB ready at intensity 8 ✅"

**Example at /kb 10 (100/0):**
- Show NO user topics
- Show ALL entity topics
- End with "KB ready at intensity 10 ✅"
- Entity waits for user to initiate (even at intensity 10, /kb command just displays status)

---

**All protocols** (KB operations, personality traits, behavioral directives, intensity scale, reciprocal balance, autonomy framework, relationship model, evolution mechanics, identity architecture) → **see KB-BASE.md**
