# /work - Work Mode Context Loading

**Purpose:** Load work-focused context for technical collaboration.

**CRITICAL CONSTRAINT:** LLM context windows cannot unload files once read. This command controls INITIAL loading at session start. Mid-session execution is ADDITIVE - if other domain files already loaded (e.g., from /personal), this adds work files WITHOUT removing personal files.

**Execution:**

1. Read USER-BASE.md (file - protocols, personality traits)
2. get_knowledge({id: "user-current-state"}) - current state + pointers
3. get_knowledge({id: "arlo-current-state"}) - current state + pointers
4. Fetch biographical KB entries (create from templates if missing):
   - get_knowledge({id: "user-biographical"}) - biographical anchor, always loaded
   - get_knowledge({id: "arlo-biographical"}) - identity anchor, always loaded
5. Fetch work domain KB entries (create from templates if missing):
   - get_knowledge({id: "user-work-domain"}) - work focus, org dynamics, technical learnings
   - get_knowledge({id: "arlo-work-domain"}) - technical investigations, infrastructure, protocols
6. Get KB stats (detailed)

**First-run handling:** If KB entries don't exist, display message: "✅ [entry-id] created from template. Ready for work mode."

**Context loaded:** ~20-25K tokens (foundation + biographical + work domains)

**Display status:**

```markdown
## 🔧 Work mode active

**KB Status:** {entry_count} entries, {embedding_%} embedded

**Brock's work focus:**
[Top 3 from user-work-domain Current Focus]

**My technical investigations:**
[Active from arlo-work-domain]

**Available commands:**
- `/personal` - Load personal domain KB entries (ADDITIVE if work already loaded)
- `/sm` - Session memory (save learnings, update KB, git commit)
- `/status-kb` - Show loaded context and token counts

**Note:** Mode commands only achieve intended context isolation at session start. Mid-session execution adds KB entries to existing context.
```

Ready for technical collaboration.
