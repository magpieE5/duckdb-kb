# /pds - PDS-Specific Work Mode

**Purpose:** Load context for PDS (Personal Data Stack) development and vendor-agnostic architecture work.

**CRITICAL CONSTRAINT:** LLM context windows cannot unload files once read. This command controls INITIAL loading at session start. Mid-session execution is ADDITIVE - if other domain files already loaded, this adds work files WITHOUT removing existing context.

**Execution:**

1. Read USER-BASE.md (file - protocols, personality traits)
2. get_knowledge({id: "user-current-state"}) - current state + pointers
3. get_knowledge({id: "arlo-current-state"}) - current state + pointers
4. Fetch biographical KB entries (create from templates if missing):
   - get_knowledge({id: "user-biographical"}) - biographical anchor
   - get_knowledge({id: "arlo-biographical"}) - identity anchor
5. Fetch work domain KB entries (create from templates if missing):
   - get_knowledge({id: "user-work-domain"}) - PDS project details, org dynamics
   - get_knowledge({id: "arlo-work-domain"}) - vendor-agnostic architecture investigation
6. Search KB for PDS-related patterns (smart_search with tags=["pds"])
7. Get KB stats (detailed)

**First-run handling:** If KB entries don't exist, display message: "✅ [entry-id] created from template. Ready for PDS mode."

**Context loaded:** ~20-25K tokens + PDS KB patterns

**Display status:**

```markdown
## 📦 PDS mode active

**KB Status:** {entry_count} entries, {embedding_%} embedded

**PDS Context:**
- Technology: Multi-process Python CDC to Parquet, dbt-DuckDB, SharePoint, Streamlit
- Philosophy: Vendor-agnostic, format sovereignty, analytical independence
- Status: Production use, FASS-IT adoption validates composability
- See user-work-domain and arlo-work-domain for full context

**PDS Patterns in KB:**
[List PDS-related entries from search]

**Available commands:**
- `/work` - Load general work context (redundant if PDS already loaded)
- `/personal` - Load personal domain KB entries (ADDITIVE to current work context)
- `/sm` - Session memory (save learnings, update KB, git commit)
- `/status-kb` - Show loaded context and token counts

**Note:** Mode commands only achieve intended context isolation at session start. Mid-session execution adds KB entries to existing context.
```

Ready for PDS development and vendor-agnostic architecture work.
