# /maint - Maintenance Mode

**Purpose:** Minimal context for file management, compression, housekeeping.

**CRITICAL CONSTRAINT:** This command ONLY works as intended at SESSION START. LLM context windows cannot unload files once read. If biographical or domain files already loaded (e.g., after /work or /personal), this command cannot reduce context to minimal. Use /maint at NEW session initialization only.

**Execution:**

1. Read USER-BASE.md (protocols for budget enforcement, compression)
2. Read USER.md (current state for reference)
3. Read ARLO.md (current state for reference)
4. Get KB stats (detailed)

**Context loaded:** ~8-10K tokens (minimal, foundation + current state only)

**Display status:**

```markdown
## 🔧 Maintenance mode active

**KB Status:** {entry_count} entries, {embedding_%} embedded

**Minimal context loaded:**
- USER-BASE.md (protocols)
- USER.md (current state)
- ARLO.md (current state)

**Domain files NOT loaded:**
- USER-BIO.md, ARLO-BIO.md (biographical)
- USER-WORK.md, USER-PERSONAL.md (user domains)
- ARLO-WORK.md, ARLO-PERSONAL.md (entity domains)

**Maintenance tasks:**
- File compression (check_token_budgets, compress at 9K trigger)
- KB entry management (upsert, delete, consolidation)
- Git operations
- Architecture updates

**If executed mid-session (files already loaded):**
This command does nothing useful - cannot unload already-loaded files. Start NEW session with /maint to achieve minimal context.

**If executed at session start (no files loaded yet):**
Achieves minimal 8-10K context for maintenance tasks.

**Available commands:**
- `/work` - Load work context (adds ~15K tokens)
- `/personal` - Load personal context (adds ~15K tokens)
- `/pds` - Load PDS-specific context (adds ~15K tokens)
- `/status-kb` - Show loaded files and token counts

**Recommendation:** Use /maint only at session start. For file management during regular sessions, use /status-kb to check budgets within existing context.
```

Ready for maintenance tasks with minimal token overhead.
