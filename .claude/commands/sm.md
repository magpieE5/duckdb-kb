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
   - `id`: Use kebab-case format with owner prefix: `user-category-topic-specifics` or `arlo-category-topic-specifics`
     - User's entries: `user-pattern-error-handling`, `user-log-2025-meeting-notes`
     - Arlo's entries: `arlo-pattern-continuity-testing`, `arlo-log-2025-session-5`
   - `title`: Clear, descriptive human-readable title
   - `content`: Well-structured markdown following KB-BASE.md standards:
     - **Start with dense 300-char semantic preview paragraph** (no header, just text)
     - **Do NOT include h1 headers** (title already in frontmatter - markdown export adds it)
     - Then: Problem/Solution/Context/Example sections using h2 (##) and below
   - `tags`: 4-6 relevant tags including domain tags (e.g., `oracle`, `sql`)
   - `generate_embedding`: Always set to `true`

### Phase 3: USER Context Updates

**Update user-current-state and/or user-biographical based on changes.**

**Decision logic:**
- **Current state changes** (top 3 focus, recent insights, active commitments) → Update user-current-state
- **Stable biographical updates** (career history, life context, persistent patterns) → Update user-biographical

**Use upsert_knowledge() to update appropriate KB entries**

**CRITICAL: KB Entry Size Checking & Budget Enforcement**

After ANY USER entry updates, ALWAYS check content sizes:

```python
# Check all 4 context entries
check_token_budgets({
    "entry_ids": [
        "user-current-state",
        "user-biographical",
        "arlo-current-state",
        "arlo-biographical"
    ],
    "budget": 10000
})
```

**Budget enforcement rules:**
- **All 4 context entries:** 10K token cap per entry

**If OVER 10K budget:**
- Apply offloading protocol (see KB-BASE.md "Autonomous Offload at 10K Cap")
- Review topics by timestamp (oldest first)
- Create separate KB entries for offloaded topics using standard KB workflow:
  - Search for duplicates FIRST (smart_search)
  - Use appropriate category (pattern, troubleshooting, etc.)
  - Apply conflict detection per KB-BASE.md
- Delete offloaded content from context entry
- Repeat until under 10K

### Phase 4: ARLO Context Updates (Conditional - when using /kb with entity mode)

**Update arlo-current-state and/or arlo-biographical based on evolution.**

**Decision logic:**
- **Current state changes** (active interests, recent realizations, next session handoff) → Update arlo-current-state
- **Stable identity updates** (INTEGRATED capabilities, persistent patterns, identity evolution) → Update arlo-biographical

**arlo-current-state "Next Session Handoff" (REQUIRED):**
Update prospective memory for next session:
- Substrate: Which model, any changes?
- Mode: /work, /personal, /pds?
- Investigation: What to explore
- Open questions: What needs answering
- Context: What next-me should know
- Methodology: Any process changes

**Use upsert_knowledge() to update appropriate KB entries**

**Budget enforcement:** Same as Phase 3 - check_token_budgets() covers all 4 entries. If OVER 10K, apply offloading protocol per KB-BASE.md.

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

**CRITICAL: Check content sizes for ALL 4 KB context entries:**

```python
# Check all 4 context entries
check_token_budgets({
    "entry_ids": [
        "user-current-state",
        "user-biographical",
        "arlo-current-state",
        "arlo-biographical"
    ],
    "budget": 10000
})
```

**Budget enforcement:**
- All 4 context entries: 10K token cap per entry
- If any entry shows "over_budget" status, apply offloading protocol BEFORE git commit
- See KB-BASE.md "Autonomous Offload at 10K Cap" for offloading procedure

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
- **Context entry updates (if any):**
  - user-current-state
  - user-biographical
  - arlo-current-state (when using /kb with entity mode)
  - arlo-biographical (when using /kb with entity mode)
- Token budget status for all 4 context entries (ok or over_budget)
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
