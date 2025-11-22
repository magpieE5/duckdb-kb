# KB Entry Quality Standards

## Entry Structure

**ID format:** kebab-case with first-position owner prefix
- **User's entries:** `user-{category}-{specifics}` (e.g., `user-pattern-error-handling`, `user-troubleshooting-auth-timeout`)
- **Arlo's entries:** `arlo-{category}-{specifics}` (e.g., `arlo-pattern-continuity-testing`, `arlo-troubleshooting-substrate-transition`)
- **Exception:** The 4 context entries (`user-current-state`, `user-biographical`, `arlo-current-state`, `arlo-biographical`) omit category/tags since they're always loaded

**Tags:** 4-6 descriptive tags for discoverability

**Content structure:**
- Dense summary paragraph first (300 chars max)
- Then: Context, Problem, Insight, Solution, Examples sections
- Use markdown formatting for readability

---

## Categories

Each category works across any domain - technical, educational, personal, creative, therapeutic, etc.

**context** - Always-loaded continuity substrate (4 core entries: user-current-state, user-biographical, arlo-current-state, arlo-biographical)

**pattern** - Reusable solutions, methodologies, approaches that work repeatedly
- Examples: Database error handling strategy, visual method for teaching fractions, morning routine for ADHD management, sourdough feeding schedule

**command** - Executable procedures, recipes, step-by-step instructions
- Examples: Git workflow commands, bread recipe steps, meditation sequence, therapy session structure

**issue** - Important decisions with rationale, architectural choices, "why we chose X"
- Examples: Technology stack selection, homeschooling decision, therapy modality choice, career pivot reasoning

**troubleshooting** - Problems solved with root cause and prevention
- Examples: Database timeout fix, sourdough not rising diagnosis, anxiety spiral interruption technique, communication breakdown resolution

**reference** - Stable information for lookup: documentation, preferences, routines, key people
- Examples: API documentation, daily medication schedule, client contact preferences, family medical history, recipe collection

**log** - Work/system events: progress made, decisions executed, milestones reached
- Examples: Feature shipped, therapy session notes, habit streak milestone, recipe experiment results

**journal** - Personal reflections: insights, feelings, growth observations
- Examples: Career transition thoughts, grief processing, learning breakthrough, parenting realization

**object** - Entity/thing documentation: systems, physical objects, relationships, spaces
- Examples: Database schema, raised garden bed (location/specs), client profile, recipe variations, home office setup
- Use tags to distinguish: `db-table`, `physical-object`, `person`, `location`, `infrastructure`

**other** - Everything else not fitting above categories

---

## Duplicate Detection

**During /sm (search-before-create protocol):**

For each topic to document:
1. **Search for existing entries:** `smart_search(query="{topic}", limit=3)`
2. **Check similarity:**
   - If similarity >= 0.65: **UPDATE** existing entry with new findings
   - If similarity < 0.65: **CREATE** new entry
3. **Full rewrite when updating:** Integrate new findings, no detail loss

**When matches found:**
1. Read the existing entry (highest similarity)
2. Reason about how to integrate new content into existing
3. Update existing entry with full rewrite

**Prevents:**
- Creating duplicates when entries already exist
- Missing resolution opportunities (issue entries waiting for fixes)
- Fragmentation (multiple entries for same topic)
