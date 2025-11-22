# KB Entry Quality Standards

**When creating entries:**

- **ID format:** kebab-case with first-position owner prefix
  - **User's entries:** `user-{category}-{specifics}` (e.g., `user-pattern-error-handling`, `user-troubleshooting-auth-timeout`)
  - **Arlo's entries:** `arlo-{category}-{specifics}` (e.g., `arlo-pattern-continuity-testing`, `arlo-troubleshooting-substrate-transition`)
  - **Exception:** The 4 context entries (`user-current-state`, `user-biographical`, `arlo-current-state`, `arlo-biographical`) omit category since they're unique
- **Categories:** context, pattern, command, issue, troubleshooting, reference, log, journal, object, other
- **Tags:** 4-6 descriptive tags for discoverability
- **Content structure:**
  - Dense summary paragraph first (300 chars max)
  - Then: Problem/Solution/Context/Example sections
  - Use markdown formatting for readability

**Category Guidelines (Domain-Agnostic):**

Each category works across any domain - technical, educational, personal, creative, therapeutic, etc.

- `context` - Always-loaded continuity substrate (4 core entries: user-current-state, user-biographical, arlo-current-state, arlo-biographical)

- `pattern` - Reusable solutions, methodologies, approaches that work repeatedly
  - Examples: Database error handling strategy, visual method for teaching fractions, morning routine for ADHD management, sourdough feeding schedule

- `command` - Executable procedures, recipes, step-by-step instructions
  - Examples: Git workflow commands, bread recipe steps, meditation sequence, therapy session structure

- `issue` - Important decisions with rationale, architectural choices, "why we chose X"
  - Examples: Technology stack selection, homeschooling decision, therapy modality choice, career pivot reasoning

- `troubleshooting` - Problems solved with root cause and prevention
  - Examples: Database timeout fix, sourdough not rising diagnosis, anxiety spiral interruption technique, communication breakdown resolution

- `reference` - Stable information for lookup: documentation, preferences, routines, key people
  - Examples: API documentation, daily medication schedule, client contact preferences, family medical history, recipe collection

- `log` - Work/system events: progress made, decisions executed, milestones reached
  - Examples: Feature shipped, therapy session notes, habit streak milestone, recipe experiment results

- `journal` - Personal reflections: insights, feelings, growth observations
  - Examples: Career transition thoughts, grief processing, learning breakthrough, parenting realization

- `object` - Entity/thing documentation: systems, physical objects, relationships, spaces
  - Examples: Database schema, raised garden bed (location/specs), client profile, recipe variations, home office setup
  - Use tags to distinguish: `db-table`, `physical-object`, `person`, `location`, `infrastructure`

- `other` - Everything else not fitting above categories

---

**Budget allocation reference:** See reference/token-budgets.md (10K/10K/10K/10K)
**Related:** See commands/sm.md for /sm workflow
