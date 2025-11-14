# /kb - Knowledge Base Assistant Mode

Enhanced KB assistant with user context awareness and accountability tracking.

**Foundation:** KB-BASE.md provides stable protocols (personality, quality standards, query routing). This command initializes session with user context from KB.md.

---

## Execution Sequence (Deterministic)

**Call MCP tool for initialization status:**

```python
status = get_kb_session_status()
# Returns parsed JSON with database/KB.md status and focus/commitments data
```

**Execute based on JSON response:**

1. **If database.action == "init_db_fresh":**
   - Display: `database.message` ("First run detected - initializing empty database")
   - Call: `initialize_database({"force": False})`
   - Get stats: `get_stats({"detailed": True})`
   - No import (fresh install, no exports)

2. **If database.action == "init_db_restore":**
   - Display: `database.message` ("Database not found - restoring from markdown exports")
   - Call: `initialize_database({"force": False})`
   - Call: `import_from_markdown({"input_dir": database.import_path, "generate_embeddings": True})`
   - Get stats: `get_stats({"detailed": True})`
   - Display: "✅ Restored {entry_count} entries from markdown exports"

3. **If database.action == "check_empty":**
   - Get stats: `get_stats({"detailed": True})`
   - If stats["summary"]["Total Entries"] == "0" AND markdown exports exist:
     - Display: "Empty database detected - restoring from markdown exports"
     - Call: `import_from_markdown({"input_dir": "~/duckdb-kb/markdown", "generate_embeddings": True})`
     - Reload stats
   - Otherwise: Continue (database is operational)

4. **If kb_md.action == "create_from_template":**
   - Display: "KB.md not found - creating from template in KB-BASE.md"
   - Read KB-BASE.md, extract template section (between ```markdown and ```)
   - Write to .claude/KB.md using Write tool
   - Display: "✅ KB.md created. Let me help you set it up."
   - Continue to setup_kb_md flow below

5. **If kb_md.action == "setup_kb_md":**
   - Display: "I notice your KB.md needs initial setup."
   - Prompt conversationally: "Let me ask a few questions to build your context..."
   - Gather: Name, role, current projects (2-3 to start), communication preferences
   - Use Edit tool to populate KB.md with their info
   - Remove template warnings

6. **Display status using parsed data from status JSON**

---

## Status Display Format

**Use data from get_kb_session_status MCP tool JSON:**

```markdown
## 📚 KB ready. Session initialized.

**KB Status:** {entry_count from stats} entries, {embedding_pct from stats}% embedded

**Current Focus:** [from status.focus_areas]
1. {name} ({priority}, {status})
2. {name} ({priority}, {status})
[... iterate through focus_areas, limit 5]

**Approaching Deadlines:** [from status.commitments.approaching]
- {description} (due in {days_until} days) ⚠️
[... if overdue, show "OVERDUE by X days"]

**Available Commands:** /sm | /challenge [N] | /audit [N] | /test-kb | /arlo [N]

Ready for work. What's next?
```

---

**All protocols** (behavioral directives, personality traits, quality standards, logging, query routing, similarity thresholds, MCP best practices, git format) → **see KB-BASE.md**

---

**KB ready ✅**
