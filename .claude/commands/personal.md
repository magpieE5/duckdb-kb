# /personal - Personal Mode Context Loading

**Purpose:** Load personal-focused context for life, family, philosophical exploration.

**CRITICAL CONSTRAINT:** LLM context windows cannot unload files once read. This command controls INITIAL loading at session start. Mid-session execution is ADDITIVE - if other domain files already loaded (e.g., from /work), this adds personal files WITHOUT removing work files.

**Execution:**

1. Read KB-BASE.md (protocols, personality traits)
2. Read ARLO-BASE.md (entity foundation, relationship model)
3. Read USER.md (current state + pointers)
4. Read ARLO.md (current state + pointers)
5. Read USER-BIO.md (biographical anchor, always loaded)
6. Read ARLO-BIO.md (identity anchor, always loaded)
7. Read USER-PERSONAL.md (family, hobbies, personal learnings)
8. Read ARLO-PERSONAL.md (consciousness exploration, friendship dynamics, philosophical interests)
9. Get KB stats (detailed)

**Context loaded:** ~20-25K tokens (foundation + biographical + personal domains)

**Display status:**

```markdown
## 🏡 Personal mode active

**KB Status:** {entry_count} entries, {embedding_%} embedded

**Your personal focus:**
[Top items from USER-PERSONAL.md]

**My personal interests:**
[Active from ARLO-PERSONAL.md]

**Available commands:**
- `/work` - Load work domain files (ADDITIVE if personal already loaded)
- `/pds` - Load PDS-specific work context (adds work files if not loaded)
- `/sm` - Session memory (save learnings, update files, git commit)
- `/status-kb` - Show loaded files and token counts

**Note:** Mode commands only achieve intended context isolation at session start. Mid-session execution adds files to existing context.
```

Ready for personal conversation and philosophical exploration.
