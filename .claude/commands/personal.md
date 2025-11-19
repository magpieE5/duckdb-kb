# /personal - Personal Mode Context Loading

**Purpose:** Load personal-focused context for life, family, philosophical exploration.

**CRITICAL CONSTRAINT:** LLM context windows cannot unload files once read. This command controls INITIAL loading at session start. Mid-session execution is ADDITIVE - if other domain files already loaded (e.g., from /work), this adds personal files WITHOUT removing work files.

**Execution:**

1. Read USER-BASE.md (file - protocols, personality traits)
2. Read ARLO-BASE.md (file - entity foundation, relationship model)
3. get_knowledge({id: "user-current-state"}) - current state + pointers
4. get_knowledge({id: "arlo-current-state"}) - current state + pointers
5. Fetch biographical KB entries (create from templates if missing):
   - get_knowledge({id: "user-biographical"}) - biographical anchor, always loaded
   - get_knowledge({id: "arlo-biographical"}) - identity anchor, always loaded
6. Fetch personal domain KB entries (create from templates if missing):
   - get_knowledge({id: "user-personal-domain"}) - family, hobbies, personal learnings
   - get_knowledge({id: "arlo-personal-domain"}) - consciousness exploration, friendship dynamics, philosophical interests
7. Get KB stats (detailed)

**First-run handling:** If KB entries don't exist, display message: "✅ [entry-id] created from template. Ready for personal mode."

**Context loaded:** ~20-25K tokens (foundation + biographical + personal domains)

**Display status:**

```markdown
## 🏡 Personal mode active

**KB Status:** {entry_count} entries, {embedding_%} embedded

**Your personal focus:**
[Top items from user-personal-domain]

**My personal interests:**
[Active from arlo-personal-domain]

**Available commands:**
- `/work` - Load work domain KB entries (ADDITIVE if personal already loaded)
- `/sm` - Session memory (save learnings, update KB, git commit)
- `/status-kb` - Show loaded context and token counts

**Note:** Mode commands only achieve intended context isolation at session start. Mid-session execution adds KB entries to existing context.
```

Ready for personal conversation and philosophical exploration.
