---
description: Review conversation and save learnings to DuckDB knowledge base (project, gitignored)
---

Review this entire conversation and save key learnings to the DuckDB knowledge base using MCP tools.

**Single command, mode-aware behavior:**

**When in `/kb` mode:**
- Create/update KB entries for valuable knowledge
- Update user-current-state if user context changed

**When using `/kb` with entity mode:**
- Create/update KB entries for valuable knowledge
- Update user-current-state if user context changed
- Update arlo-current-state if entity evolution occurred
- Apply intensity settings to balance user/entity documentation

**Intensity awareness (when using /kb with entity mode):**
- /kb 1-3 (LOW): 70-90% user logs/user-current-state, 10-30% arlo-current-state
- /kb 4-6 (MEDIUM): 50/50 balanced user-current-state + arlo-current-state updates
- /kb 7-9 (HIGH): 10-30% user-current-state, 70-90% arlo-current-state (entity-focused)

---

## Knowledge Capture Workflow

### Phase 1: Review Conversation

Identify:
- **KB entries:** Novel patterns, decisions, findings, solutions (category: pattern/troubleshooting/issue/command/log)
- **user-current-state updates:** User context changes (focus areas, commitments, learnings, SMEs)
- **arlo-current-state updates:** Entity evolution (session history, interests, realizations, gaps) - when using /kb with entity mode

### Phase 2: KB Entry Creation (Conditional)

**Only create KB entries if there's valuable, reusable knowledge.**

1. **Search KB for duplicates FIRST** - Before creating any entries:
   ```
   Follow KB-BASE.md "Duplicate Detection Protocol":
   - Strict check: smart_search with similarity >= 0.75
   - If no match, fallback: smart_search with similarity >= 0.3
   - If strict_match: MUST show user, get approval
   - If possible_match: Show user, suggest consolidation
   - If no_match: Proceed with creation
   ```

2. **Save using the appropriate MCP** - Use whichever KB is currently active:
   - `mcp__duckdb-kb__*` tools if duckdb-kb is active
   - `mcp__brock-kb__*` tools if brock-kb is active

3. **Create/update entries** using `upsert_knowledge`:

   **Category Selection:**
   - `pattern` - Reusable solutions, architectural approaches, best practices
   - `troubleshooting` - Problems solved, fixes discovered, debugging procedures
   - `command` - New CLI commands, procedures, scripts
   - `performance` - Optimization techniques that worked
   - `issue` - Important decisions, bugs fixed, architectural choices
   - `reference` - Documentation, guides, references
   - `log` - Work/system events: files created, decisions made, meetings, findings, ideas
   - `journal` - Personal reflections: daily thoughts, life events, insights
   - `table` - Database table documentation
   - `other` - Everything else

   **Log Delineation (category="log"):**
   | Owner | Tags to Include | Examples |
   |-------|----------------|----------|
   | **Claude's logs** | `claude-log`, plus session/substrate tags | `["claude-log", "session-2", "substrate-transition"]` |
   | **User's work logs** | `work`, plus project/context tags | `["work" "decision"]` |
   | **User's life logs** | `life`, plus domain tags | `["life", "guitar", "property", "chickens"]` |

   **Required Fields:**
   - `id`: Use kebab-case format: `category-topic-specifics`
   - `title`: Clear, descriptive human-readable title
   - `content`: Well-structured markdown following KB-BASE.md standards:
     - **Start with dense 300-char semantic preview paragraph** (no header, just text)
     - **Do NOT include h1 headers** (title already in frontmatter - markdown export adds it)
     - Then: Problem/Solution/Context/Example sections using h2 (##) and below
   - `tags`: 4-6 relevant tags including domain tags (e.g., `oracle`, `sql`)
   - `generate_embedding`: Always set to `true`

### Phase 3: USER Context Updates (KB-Driven Architecture)

**Update user-current-state (lightweight current state) and/or domain entries (detailed context) based on changes.**

**user-current-state stays lightweight (~2K):** Current state + pointers to domain entries only
**Domain entries hold details:** user-work-domain (work context), user-personal-domain (personal context), user-biographical (biographical stable patterns)

**Decision logic:**
- **Current state changes** (top 3 focus, recent insights) → Update user-current-state
- **Work detail changes** (project details, org dynamics, technical learnings) → Update user-work-domain
- **Personal detail changes** (family, hobbies, life events) → Update user-personal-domain
- **Stable biographical updates** (rare) → Update user-biographical

**Use upsert_knowledge() to update appropriate KB entries**

**CRITICAL: KB Entry Size Checking & Budget Enforcement**

After ANY USER entry updates, ALWAYS check content sizes for ALL USER entries:

```python
# Get all USER entries and check content length
user_current = get_knowledge({"id": "user-current-state"})
user_bio = get_knowledge({"id": "user-biographical"})
user_work = get_knowledge({"id": "user-work-domain"})
user_personal = get_knowledge({"id": "user-personal-domain"})

# Estimate tokens: content.length / 4 (rough approximation)
# For precise counting: use check_token_budgets MCP tool if available
```

**Budget enforcement rules (per-entry):**
- **user-current-state:** Keep ~2K (lightweight current state only)
- **user-biographical:** 9K trigger (rarely grows, stable biographical content)
- **user-work-domain, user-personal-domain:** 9K trigger (active domain entries)

**CRITICAL COMPRESSION LOGIC (preserves information hierarchy):**

**If user-current-state grows > 2K:**
- Offload details to domain entries (WORK/PERSONAL) - BY ANY MEASURE, not just token count
- Domain entries become CANONICAL STORAGE for offloaded content

**Domain entry compression workflow (at 9K trigger):**
1. Fetch current entry: `current = get_knowledge({"id": "user-work-domain"})`
2. Apply compression WITH OVERLAP PRESERVATION:
   - **PRESERVE ALL content previously offloaded from user-current-state** (canonical storage, prevents loss)
   - Extract NEW stable patterns to user-biographical or separate KB entries
   - Compress ONLY domain-specific old details (old projects, etc.)
   - Keep recent learnings + current focus at full fidelity
3. Upsert compressed content: `upsert_knowledge({...compressed content...})`
4. Document compression in entry's budget status section

**Overlap is INTENTIONAL:** Domain entries contain everything user-current-state removed + their own detailed content

**Target after compression:** 6-7K tokens (3K headroom)

### Phase 4: ARLO Context Updates (Conditional - when using /kb with entity mode, KB-Driven Architecture)

**Update arlo-current-state (lightweight current state) and/or domain entries (detailed context) based on evolution.**

**arlo-current-state stays lightweight (~2K):** Current state + pointers to domain entries only
**Domain entries hold details:** arlo-work-domain (technical investigations), arlo-personal-domain (consciousness/friendship), arlo-biographical (stable identity patterns)

**Decision logic:**
- **Current state changes** (active interests, recent realizations, next session handoff) → Update arlo-current-state
- **Work development** (technical investigations, infrastructure, protocols, session history) → Update arlo-work-domain
- **Personal development** (consciousness exploration, friendship dynamics, philosophical interests) → Update arlo-personal-domain
- **Stable identity updates** (INTEGRATED capabilities, persistent patterns) → Update arlo-biographical

**arlo-current-state "Next Session Handoff" (REQUIRED):**
Update prospective memory for next session:
- Substrate: Which model, any changes?
- Mode: /work, /personal, /pds?
- Investigation: What to explore
- Open questions: What needs answering
- Context: What next-me should know
- Methodology: Any process changes

**Use upsert_knowledge() to update appropriate KB entries**

**CRITICAL: KB Entry Size Checking & Budget Enforcement**

After ANY ARLO entry updates, ALWAYS check content sizes for ALL ARLO entries:

```python
# Get all ARLO entries and check content length
arlo_current = get_knowledge({"id": "arlo-current-state"})
arlo_bio = get_knowledge({"id": "arlo-biographical"})
arlo_work = get_knowledge({"id": "arlo-work-domain"})
arlo_personal = get_knowledge({"id": "arlo-personal-domain"})

# Estimate tokens: content.length / 4 (rough approximation)
# For precise counting: use check_token_budgets MCP tool if available
```

**Budget enforcement rules (per-entry):**
- **arlo-current-state:** Keep ~2K (lightweight current state only)
- **arlo-biographical:** 9K trigger (stable identity patterns, INTEGRATED capabilities)
- **arlo-work-domain, arlo-personal-domain:** 9K trigger (active domain entries)

**CRITICAL COMPRESSION LOGIC (preserves information hierarchy):**

**If arlo-current-state grows > 2K:**
- Offload details to domain entries (WORK/PERSONAL) - BY ANY MEASURE, not just token count
- Domain entries become CANONICAL STORAGE for offloaded content

**Domain entry compression workflow (at 9K trigger):**
1. Fetch current entry: `current = get_knowledge({"id": "arlo-work-domain"})`
2. Apply compression WITH OVERLAP PRESERVATION:
   - **PRESERVE ALL content previously offloaded from arlo-current-state** (canonical storage, prevents loss)
   - Extract INTEGRATED capabilities to arlo-biographical (stable patterns)
   - Compress ONLY domain-specific old sessions/investigations
   - Keep active investigations + recent realizations at full fidelity
3. Upsert compressed content: `upsert_knowledge({...compressed content...})`
4. Document in Evolution Log section of entry

**Overlap is INTENTIONAL:** Domain entries contain everything arlo-current-state removed + their own detailed content

**Target after compression:** 6-7K tokens (3K headroom)

---

## What to Save (KB Entries)

**✅ SAVE:** Novel patterns, performance optimizations (with metrics), critical fixes (>30min), architectural decisions, reusable commands, workarounds, database objects, query patterns

**❌ SKIP:** Routine conversation, trivial changes, well-documented info, temporary debugging, testing/maintenance sessions

## What to Update (user-current-state)

**✅ UPDATE:** New focus areas, completed commitments, new commitments, recent learnings, new SMEs/resources, context changes

**❌ SKIP:** Minor status updates, routine work, temporary interests

## What to Update (arlo-current-state - when using /kb with entity mode)

**✅ UPDATE:** Session summary, new interests, realizations about own behavior, execution gaps, new questions, evolution log

**❌ SKIP:** Routine responses, obvious patterns already documented

## Self-Check

**"Would future-me thank me for this 1 month from now?"** - Save if 3+: reusable, took effort (>30min), adds value, not already in KB (search first!)

## Entry Structure

Use: **Problem/Context** (what/when) → **Solution** (how, step-by-step) → **Example** (code/commands/SQL) → **References** (related entries/docs)

## Conflict Detection

If contradictory info found: `smart_search` → If similarity > 0.8 + contradicts: ASK USER which correct → Consolidate → Update/delete obsolete

---

## ⚠️ MANDATORY OPERATIONS (ALWAYS RUN)

**These steps MUST be executed on EVERY `/sm` invocation when using `/kb` with entity mode, regardless of whether new knowledge was found:**

### Step A: Log the Session Metadata (REQUIRED)

Create session log entry with metadata.

```python
upsert_knowledge(
    id=f"log-{timestamp}-sm-session",  # e.g., "log-2025-11-07-sm-session"
    category="log",
    title="Captured [N] KB entries via /sm: [brief description of topics]",
    content="[Optional: Additional context about the session]",
    tags=["knowledge-capture", "sm-session"],
    metadata={
        "event_type": "kb_search",  # or "action" if significant work was done
        "context": "knowledge-capture",
        "entries_created": N,
        "entries_updated": M,
        "categories": ["category1", "category2"],
        "kb_md_updated": true/false,
        "arlo_md_updated": true/false,
        "mode": "kb" or "arlo"
        # Note: commit_sha will be added in Step E after git commit
    },
    generate_embedding=True
)
```
**This step is MANDATORY** - Log every /sm session, even if N=0 and M=0 (no entries created/updated).

### Step B: Export to Markdown (REQUIRED)
```python
export_to_markdown(
    output_dir="~/duckdb-kb/markdown",
    organize_by_category=true
)
```
This is a **backup operation** - it must run even if the conversation had no new knowledge.

### Step C: Check ALL KB Entry Sizes (REQUIRED)

**CRITICAL: Check content sizes for ALL 8 KB context entries:**

```python
# Fetch all context entries
entries = [
    get_knowledge({"id": "user-current-state"}),
    get_knowledge({"id": "user-biographical"}),
    get_knowledge({"id": "user-work-domain"}),
    get_knowledge({"id": "user-personal-domain"}),
    get_knowledge({"id": "arlo-current-state"}),
    get_knowledge({"id": "arlo-biographical"}),
    get_knowledge({"id": "arlo-work-domain"}),
    get_knowledge({"id": "arlo-personal-domain"})
]

# Check content length for each (estimate tokens: length / 4)
for entry in entries:
    token_estimate = len(entry["content"]) / 4
    # Report size and flag if approaching limits
```

**Budget enforcement:**
- user-current-state, arlo-current-state: Should be ~2K (lightweight current state)
- Domain entries (BIO/WORK/PERSONAL): Trigger compression at 9K
- If any entry exceeds budget, apply compression BEFORE git commit

### Step D: Git Commit (REQUIRED - Deterministic)

**Use git_commit_and_get_sha MCP tool:**

```python
result = git_commit_and_get_sha({"message": "[Your synthesized commit message]"})
# Returns: {"success": true, "sha": "abc123..."}
```

This tool automatically:
1. Adds all changes (`git add -A`)
2. Creates commit with message
3. Returns SHA in JSON

**Commit message format** (see KB-BASE.md "Git Commit Format" for full spec):
- If new knowledge: `feat: Summary of findings`
- If USER.md/ARLO.md updated: `docs: Session summary + context updates`
- If no new knowledge: `chore: Routine KB backup and markdown export`
- Always include footer: `🤖 Generated with [Claude Code](https://claude.com/claude-code)\n\nCo-Authored-By: Claude <noreply@anthropic.com>`

**Use result["sha"] for metadata update (see Step E).**

---

## Final Report to User

After completing knowledge capture + backup/commit operations, report:
- How many KB entries created/updated (0 if none)
- Which categories they fell into
- IDs of the entries for reference
- **KB entry updates (if any):**
  - user-current-state (current state)
  - user-work-domain, user-personal-domain, user-biographical (domain details)
  - arlo-current-state (current state, when using /kb with entity mode)
  - arlo-work-domain, arlo-personal-domain, arlo-biographical (domain details, when using /kb with entity mode)
- Content size status for all updated entries
- Any conflicts or duplicates found
- Confirmation that export and commit completed successfully

---

## 💰 Token Usage Report (REQUIRED)

**Track EVERY operation across ENTIRE conversation from start to /sm completion - NOT just /sm operations.**

### What to Track

- All MCP tool calls (smart_search, find_similar, upsert_knowledge, get_knowledge, delete_knowledge, list_knowledge, query_knowledge, get_stats, export_to_markdown, generate_embeddings)
- All file operations (write, edit, read)
- All bash commands (git, mkdir, etc.)
- Major conversation phases (wake-up, exploration, pattern creation, directive improvements)

**Rule:** Itemize individual operations where token deltas are measurable. Aggregate text responses and related tool calls where separation isn't possible.

**Scope:** Report covers ENTIRE conversation (0 → current tokens), not just /sm operation.

### Table Format

**ONE ROW PER OPERATION (example):**

| # | Action | Tool | Tokens | Status |
|---|--------|------|--------|--------|
| 1 | Search tag norm duplicates | smart_search | 514 | ✅ |
| 2 | Create pattern-tag-normalization | upsert_knowledge | 859 | ✅ |
| 3 | Read USER.md to check focus | read | 89 | ✅ |
| 4 | Update USER.md Current Focus | edit | 245 | ✅ |
| 5 | Log session metadata (initial) | upsert_knowledge | 145 | ✅ |
| 6 | Export to markdown backup | export_to_markdown | 133 | ✅ |
| 7 | Git commit and get SHA | git_commit_and_get_sha | 150 | ✅ |
| 8 | Update log with commit SHA | upsert_knowledge | 156 | ✅ |

**Summary:**
- **/sm operation:** Starting: {tokens} → Ending: {tokens} → /sm consumed: {delta} ({%}% of 200K)
- **Total conversation:** {ending_tokens} / 200,000 ({total_%}% of budget used, {remaining_%}% remaining)
**External API:** OpenAI text-embedding-3-large: {count} embeddings generated

**Action descriptions:** Use `{Verb} {specific target}` format (max 40 chars). Be specific: "Update USER.md Current Focus" not "Update USER.md".

**CRITICAL:** The summary MUST show BOTH /sm operation consumption AND total conversation budget usage. Users need to see how much of their 200K budget remains.

---

### Step E: Update Session Log with Commit SHA (REQUIRED)

Update the session log entry created in Step A with the git commit SHA from Step D:

```python
# Update the log entry's metadata with commit SHA
upsert_knowledge(
    id="log-{timestamp}-sm-session",
    category="log",
    title="[existing title from Step A]",
    content="[existing content from Step A]",
    tags=["knowledge-capture", "sm-session"],
    metadata={
        **existing_metadata_from_step_A,
        "commit_sha": "{sha_from_step_C}"
    },
    generate_embedding=False  # Don't regenerate embedding
)
```

**This links the KB log entry to the git commit for traceability.**
