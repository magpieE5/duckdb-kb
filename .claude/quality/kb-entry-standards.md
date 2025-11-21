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

**Category Guidelines:**
- `context` - Always-loaded continuity substrate (4 core entries: user-current-state, user-biographical, arlo-current-state, arlo-biographical)
- `pattern` - Reusable solutions, architectural approaches, best practices
- `command` - CLI commands, procedures, scripts
- `issue` - Important decisions, bugs fixed, architectural choices
- `troubleshooting` - Problems solved, fixes discovered, debugging procedures
- `reference` - Documentation, guides, references
- `log` - Work/system events: files created, decisions made, findings, ideas
- `journal` - Personal reflections: daily thoughts, life events, insights
- `object` - Entity/thing documentation: DB tables/views/procedures, physical objects (raised garden, equipment), infrastructure, code modules (use tags to distinguish: `db-table`, `db-view`, `physical`, `infrastructure`, etc.)
- `other` - Everything else

---

**Budget allocation reference:** See KB-BASE.md Architecture & Scoping (15K/5K/15K/5K)
**Related:** See protocols/real-time-logging.md for category/tag guidance
