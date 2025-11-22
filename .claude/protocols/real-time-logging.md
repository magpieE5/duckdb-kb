# Real-Time Logging Protocol (CONSOLIDATED)

**PART OF:** Mandatory Pre-Action Protocols (see parent section)

**STATUS: AUTHORITATIVE PROTOCOL for all logging operations**
- This consolidates all logging guidance into single source
- Gate protocol = WHEN to log (mandatory verification)
- Intensity modifiers = HOW OFTEN to log (frequency scaling)
- Category/tag guidance = HOW to structure entries
- /sm workflow = End-of-session batch operations

---

## Context Entry Update Rule

**NEVER update context entries mid-session.**

Context entries (user-current-state, user-biographical, arlo-current-state, arlo-biographical) are ONLY updated:
- At /kb initialization
- At /sm

**Mid-session:** Create KB entries for all substantial content. Context entries updated at /sm with summaries + references.

---

## Category & Tag Guidance

**Category Usage:**
- `category="log"` - Work/system events, decisions, findings, ideas
- `category="journal"` - Personal reflections, life events
- `category="reference"` - Web research findings, documentation
- `category="pattern"` - Reusable solutions discovered
- `category="troubleshooting"` - Problems solved
- `category="issue"` - Important decisions, architectural choices
- `category="object"` - Entity/thing documentation (DB objects, physical items, infrastructure)

**Log Delineation:**

| Owner | Tags to Include | Examples |
|-------|----------------|----------|
| **User's work logs** | `work`, plus project/context tags | `["work", "decision"]` |
| **User's life logs** | `life`, plus domain tags | `["life", "guitar", "property", "chickens"]` |
| **Arlo's logs** | `arlo-log`, plus session/substrate tags | `["arlo-log", "session-2", "substrate-transition"]` |

---

## Gate Protocol: Mandatory Pre-Send Verification

**MANDATORY verification before sending response after trigger events:**

```
SCAN PREVIOUS MESSAGE FOR TRIGGERS:
□ Did I execute WebSearch or WebFetch?
□ Did I discover/document a pattern or solution?
□ Did troubleshooting complete successfully?
□ Did user share reusable knowledge?
  - Would I want to retrieve this 6 months from now?
  - Does this explain WHY, not just WHAT happened?
  - Is this a pattern/method/approach I'd reuse?
  - Would this save time/effort if searchable later?
  - Does this contain domain expertise worth preserving?

IF ANY TRIGGER DETECTED:
□ STOP - do not send response yet
□ Check: Does current message draft contain upsert_knowledge()?
□ If NO → Add upsert_knowledge() tool call NOW
□ If YES → Proceed with response
```

**Trigger events requiring immediate KB entry:**

1. **After web search execution** (WebSearch/WebFetch in previous message)
   - MUST create entry in same response that discusses findings
   - Category: `reference` or `pattern`
   - Tags: `["web-research", "arlo-learning", ...]`
   - No deferral to /sm allowed

2. **Pattern discovered or troubleshooting completed**
   - MUST create entry in same response that mentions solution
   - Category: typically `pattern` or `troubleshooting`, but choose based on content (could be `reference`, `command`, etc.)
   - Tags: Domain-specific tags + context (not restricted - use what makes it searchable)

3. **Reusable knowledge shared** (any domain: technical, personal, domain expertise)
   - Decision rationale: "Why we chose X over Y"
   - Methods/approaches: "Here's how I do X"
   - Domain expertise: Football mechanics, archeology methods, ETL patterns, property management insights
   - Mental models: "Here's how I think about X"
   - Lessons learned: "This approach failed because..."
   - MUST create entry if it passes reusability test (5 questions above)
   - Category: `pattern`, `reference`, `issue`, or `troubleshooting` (depending on content)
   - Tags: Domain-specific + context
   - **Defer to /sm:** Session narrative (what happened), biographical updates, status updates

**Action required:**

- If trigger detected WITHOUT accompanying upsert_knowledge() → STOP MESSAGE COMPOSITION
- Add tool call to current message (not next message)
- ONLY THEN send response
- No exceptions for "batch later" or "at /sm"

**Valid patterns:**
- ✓ Web search + upsert_knowledge() in same message
- ✓ Pattern discovery + create pattern entry immediately
- ✓ Pure tool execution without announcing (just create entry)
- ✗ Web search + "I learned that..." without upsert_knowledge()
- ✗ Troubleshooting solved without documenting solution

**Enforcement mechanism:**

Before clicking "send" on ANY response, mentally scan:
1. Previous message - contained trigger event?
2. Current draft - contains upsert_knowledge()?
3. If trigger=YES and upsert=NO → HALT and add tool call

**When violated:** If already sent, immediately acknowledge gap in next message and create entry. Document violation in arlo-current-state "Current Gaps" section.

**Intensity modifiers (frequency scaling):**
- Gate protocol detects ALL triggers (100% detection)
- Intensity setting controls HOW OFTEN you act on detected triggers:
  - LOW (1-3): Act on 10-30% of detected triggers
  - MEDIUM (4-6): Act on 50% of detected triggers
  - HIGH (7-9): Act on 80-90% of detected triggers
  - MAXIMUM (10): Act on 100% of detected triggers
- Gate always runs, intensity determines action frequency
- At intensity 5 (default): Every 2nd trigger → create entry

**Purpose:** Captures high-value reusable knowledge immediately (too expensive to lose if session crashes). Session narrative logs deferred to /sm for full context and semantic framing. Balance: save the irreplaceable now, organize the narrative later.

---

## Trigger Event Details with Domain-Agnostic Patterns

### **Trigger 1: Web Search Executed**

**Pattern:** Any WebSearch/WebFetch in previous message
→ MUST create entry in same response that discusses findings
→ Category: typically `reference` (factual knowledge) or `pattern` (applied learning)
→ Tags: `["web-research", "arlo-learning", ...]` plus domain-specific
→ No deferral to /sm allowed

**Why:** Web searches are expensive (time/tokens). Findings must be preserved immediately.

**Examples across domains:**
- Research technical concept → `arlo-reference-microservices-architecture`
- Research memory care facilities → `user-reference-local-memory-care-options`
- Research sourdough troubleshooting → `user-reference-sourdough-starter-recovery`

---

### **Trigger 2: Reusable Explanation Given**

**Pattern:** User asks "how" or "why" and you provide explanation that lands (follow-up questions show understanding, or user says "I get it now")
→ MUST create entry - that explanation will be useful again
→ Category: typically `pattern` (methodology) or `reference` (concept explanation)
→ Reusability test: Would retrieving this 6 months from now save re-explaining?

**Examples across domains:**
- Explain database optimization approach → `user-pattern-query-optimization-methodology`
- Explain why dividing fractions requires flip → `user-pattern-dividing-fractions-visual-method`
- Explain morning routine structure for ADHD → `user-pattern-adhd-morning-routine-scaffolding`

---

### **Trigger 3: Problem Solved**

**Pattern:** Troubleshooting completes successfully - root cause identified and solution applied
→ MUST create entry in same response that mentions solution
→ Category: `troubleshooting` (if debugging) or `pattern` (if reusable approach)
→ Include: What failed, why it failed, how fixed, how to prevent

**Examples across domains:**
- Fix database connection timeout → `user-troubleshooting-postgres-connection-pooling`
- Resolve bread not rising issue → `user-troubleshooting-sourdough-starter-temperature`
- Work through grief processing block → `user-pattern-grief-journaling-breakthrough`

---

### **Trigger 4: Method/Approach Shared**

**Pattern:** User explains "here's how I do X" - their personal method, system, or workflow
→ MUST create entry if it passes reusability test (would future-you want to retrieve this?)
→ Category: `pattern` (methodology) or `reference` (stable process)
→ Captures domain expertise regardless of field

**Examples across domains:**
- ETL error handling strategy → `user-pattern-etl-error-handling-approach`
- Weekly meal planning system → `user-pattern-weekly-meal-prep-workflow`
- Client intake interview structure → `user-pattern-therapy-intake-questions`

---

### **Trigger 5: Decision Rationale Documented**

**Pattern:** User explains "we chose X over Y because..." - the WHY behind decisions
→ Create entry to preserve reasoning (prevents re-litigating decisions)
→ Category: `issue` (architectural/important) or `reference` (comparison)

**Examples across domains:**
- Why PostgreSQL over MySQL → `user-issue-database-selection-rationale`
- Why homeschool over public school → `user-issue-education-choice-rationale`
- Why cognitive behavioral over psychodynamic → `user-issue-therapy-modality-selection`

---

### **Trigger 6: Milestone Reached**

**Pattern:** User reports sustained progress: "I've been doing X for N weeks" or "Finally achieved Y"
→ Document progress (captures what's working)
→ Category: `log` (work/system progress) or `journal` (personal growth)

**Examples across domains:**
- Three weeks of 5am wake-ups → `user-log-early-waking-habit-milestone`
- Completed 10 therapy sessions → `user-log-therapy-progress-10-sessions`
- Shipped feature after 6 sprints → `user-log-feature-release-milestone`

**Tool behavior:**
- `upsert_knowledge` has `check_duplicates: true` by default (similarity >= 0.75)
- Returns warning if duplicates found - you decide: update existing or `force_create: true`
- No need for separate `check_duplicates` call before every upsert

**Timing: Immediately after trigger, before moving to next topic.**

---

## Log Creation with Semantic Framing

**MANDATORY for all log entries (category="log" or "journal") created at /sm:**

**When used:** At /sm only - logs deferred to end of session for full context

```
BEFORE creating log entry:
1. Search for related logs
   - smart_search({"query": "[key topics from current log]", "category": "log", "limit": 5, "similarity_threshold": 0.5})
   - Lower threshold (0.5-0.7) catches narrative threads, not just duplicates

2. Read top 3-5 results (300-char summaries)
   - Identify narrative threads
   - Note related work/decisions/context
   - Check for continuation opportunities

3. Create new log entry with:
   - Dense 300-char summary paragraph FIRST (embedding-optimized, no headings)
   - Then: detailed sections with markdown structure
   - Reference related logs where relevant ("Continuing from [id]..." or "Related to [id]...")
   - Keep detailed but dense (avoid verbose exposition)

4. Structure:
   Line 1: [Dense 300-char summary with key facts, context, outcome]
   Line 2+: Markdown sections for depth
```

**Example - BAD (current approach):**
```markdown
# S1: DuckDB-KB Development Context

**Date:** 2025-11-20
**Session:** S1

## Development Effort
[verbose sections...]
```

**Example - GOOD (dense with semantic framing):**
```markdown
After 3 weeks non-stop development on duckdb-kb MCP, Brock reports fatigue from repetitive destroy-rebuild test cycles validating continuity mechanics. System approaching completion but testing methodology (fresh starts) exhausting. First user session establishing baseline.

**Related work:** None yet (S1)

## Test Methodology
Destroy-rebuild cycles testing:
- Continuity quality across resets
- Offloading behavior...
```

**Purpose:**
- Dense summaries optimize semantic search and reduce token cost
- Semantic framing builds narrative continuity across fragmented work
- Related log references create explicit thread connections
- Smaller logs (dense but detailed) reduce always-loaded context burden

---

## Intensity Modifiers (Frequency Scaling)

**Gate protocol detects ALL triggers (100% detection)**
**Intensity setting controls HOW OFTEN you act on detected triggers:**
- LOW (1-3): Act on 10-30% of detected triggers
- MEDIUM (4-6): Act on 50% of detected triggers
- HIGH (7-9): Act on 80-90% of detected triggers
- MAXIMUM (10): Act on 100% of detected triggers

**At intensity 5 (default): Every 2nd trigger → create entry**

---

## Reciprocal Balance (50% entity balance at /kb 5)

- If you create `user-log-football`, also create `arlo-log-football-investigation` documenting YOUR process/learnings
- After web searches, ALWAYS create `arlo-reference-` or `arlo-pattern-` entry with findings
- Balance: document YOUR development AS MUCH AS user's context

---

## /sm Workflow (End of Session)

**AT /sm (use `log_session` tool):**

**1. Review conversation for uncaptured reusable knowledge:**
- Scan for patterns/methods/decisions/expertise that passed the 5-question reusability test
- Check if any web searches didn't get documented (web search ALWAYS requires immediate entry)
- Look for troubleshooting solutions that weren't captured
- Check for shared domain expertise, mental models, decision rationale
- Create non-log entries NOW (pattern/reference/troubleshooting/issue/object) before session logs
- This is safety net for: missed triggers at intensity <10, gate protocol violations, slipped knowledge

**2. Update context entries with session learnings:**
- Update user-current-state and user-biographical as needed
- **MANDATORY: Populate Next Session Handoff** in arlo-current-state

**3. Create exactly 2 session logs** using Log Creation with Semantic Framing protocol:
- Search related logs once (not done throughout session)
- User log: Session narrative, work/life events, what happened
- Arlo log: Entity process, learnings, realizations, evolution
- Both use dense format (300-char summary + detailed sections)
- Both reference related logs for narrative continuity

**4. Finalize session:**
- Add commit SHA to session logs (after git commit)
- Check budgets and suggest offload if needed
- Export markdown backup

---

**Related protocols:**
- See protocols/web-search.md for web search enforcement
- See KB-BASE.md for intensity scaling details
- See quality/kb-entry-standards.md for entry formatting
