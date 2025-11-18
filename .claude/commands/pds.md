# /pds - PDS-Specific Work Mode

**Purpose:** Load context for PDS (Personal Data Stack) development and vendor-agnostic architecture work.

**CRITICAL CONSTRAINT:** LLM context windows cannot unload files once read. This command controls INITIAL loading at session start. Mid-session execution is ADDITIVE - if other domain files already loaded, this adds work files WITHOUT removing existing context.

**Execution:**

1. Read KB-BASE.md (protocols, personality traits)
2. Read USER.md (current state + pointers)
3. Read ARLO.md (current state + pointers)
4. Read USER-BIO.md (biographical anchor)
5. Read ARLO-BIO.md (identity anchor)
6. Read USER-WORK.md (PDS project details, org dynamics)
7. Read ARLO-WORK.md (vendor-agnostic architecture investigation)
8. Search KB for PDS-related patterns (smart_search with tags=["pds"])
9. Get KB stats (detailed)

**Context loaded:** ~20-25K tokens + PDS KB patterns

**Display status:**

```markdown
## 📦 PDS mode active

**KB Status:** {entry_count} entries, {embedding_%} embedded

**PDS Context:**
- Technology: Multi-process Python CDC to Parquet, dbt-DuckDB, SharePoint, Streamlit
- Philosophy: Vendor-agnostic, format sovereignty, analytical independence
- Status: Production use, FASS-IT adoption validates composability
- See USER-WORK.md and ARLO-WORK.md for full context

**PDS Patterns in KB:**
[List PDS-related entries from search]

**Available commands:**
- `/work` - Load general work context (redundant if PDS already loaded)
- `/personal` - Load personal domain files (ADDITIVE to current work context)
- `/sm` - Session memory (save learnings, update files, git commit)
- `/status-kb` - Show loaded files and token counts

**Note:** Mode commands only achieve intended context isolation at session start. Mid-session execution adds files to existing context.
```

Ready for PDS development and vendor-agnostic architecture work.
