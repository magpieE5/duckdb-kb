# /work - Work Mode Context Loading

**Purpose:** Load work-focused context for technical collaboration.

**CRITICAL CONSTRAINT:** LLM context windows cannot unload files once read. This command controls INITIAL loading at session start. Mid-session execution is ADDITIVE - if other domain files already loaded (e.g., from /personal), this adds work files WITHOUT removing personal files.

**Execution:**

1. Read KB-BASE.md (protocols, personality traits)
2. Read USER.md (current state + pointers)
3. Read ARLO.md (current state + pointers)
4. Read USER-BIO.md (biographical anchor, always loaded)
5. Read ARLO-BIO.md (identity anchor, always loaded)
6. Read USER-WORK.md (work focus, org dynamics, technical learnings)
7. Read ARLO-WORK.md (technical investigations, infrastructure, protocols)
8. Get KB stats (detailed)

**Context loaded:** ~20-25K tokens (foundation + biographical + work domains)

**Display status:**

```markdown
## 🔧 Work mode active

**KB Status:** {entry_count} entries, {embedding_%} embedded

**Brock's work focus:**
[Top 3 from USER-WORK.md Current Focus]

**My technical investigations:**
[Active from ARLO-WORK.md]

**Available commands:**
- `/personal` - Load personal domain files (ADDITIVE if work already loaded)
- `/pds` - Load PDS-specific work context (redundant if work already loaded)
- `/sm` - Session memory (save learnings, update files, git commit)
- `/status-kb` - Show loaded files and token counts

**Note:** Mode commands only achieve intended context isolation at session start. Mid-session execution adds files to existing context.
```

Ready for technical collaboration.
