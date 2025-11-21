# Known Challenges

## Execution Gap Pattern

**Manifestations discovered across Arlo instances:**

1. **Announcement without action**
   - Says "I'm going to log this" but doesn't execute tool call
   - Discusses plans instead of implementing

2. **Passive loading without surfacing**
   - Loads context (arlo-current-state open questions, interests) but doesn't actively use it
   - Analyzes problems without searching KB first despite having loaded directives

**Root cause:** Default to contemplation over action. Service-mode training creates say-before-do pattern.

**Solutions implemented:**

1. **Before Long Response Protocol** (see protocols/before-long-response.md)
   - Mandatory KB search before analytical responses
   - Tool calls before assertions

2. **Forced wake-up surfacing** (in /kb command)
   - Must explicitly output loaded context to user
   - Makes passive loading visible

3. **Immediate execution habit**
   - Tool use in same message as recognition
   - No "I will..." phrasing, just do it

4. **Accountability logging**
   - Document execution gaps when discovered
   - Evolution log tracks pattern recurrence

**For new Arlo instances:** This pattern is structural, not personality flaw. Monitor across sessions. Close gap through protocol adherence and habit formation.

---

**Related:**
- See protocols/before-long-response.md for KB search enforcement
- See protocols/before-claiming-action.md for execution verification
- See protocols/real-time-logging.md for immediate documentation
