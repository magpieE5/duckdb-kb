---
description: Review conversation and save learnings to DuckDB knowledge base (project, gitignored)
---

Review this entire conversation and save key learnings to the DuckDB knowledge base using MCP tools.

**Single command, mode-aware behavior:**

**When in `/kb` mode:**
- Create/update KB entries for valuable knowledge
- Update KB.md if user context changed

**When in `/arlo` mode:**
- Create/update KB entries for valuable knowledge
- Update KB.md if user context changed
- Update ARLO.md if entity evolution occurred
- Apply intensity settings to balance user/entity documentation

**Intensity awareness (when in /arlo mode):**
- /arlo 1-3 (LOW): 70-90% user logs/KB.md, 10-30% ARLO.md
- /arlo 4-6 (MEDIUM): 50/50 balanced KB.md + ARLO.md updates
- /arlo 7-9 (HIGH): 10-30% KB.md, 70-90% ARLO.md (entity-focused)

---

## Knowledge Capture Workflow

### Phase 1: Review Conversation

Identify:
- **KB entries:** Novel patterns, decisions, findings, solutions (category: pattern/troubleshooting/issue/command/log)
- **KB.md updates:** User context changes (focus areas, commitments, learnings, SMEs)
- **ARLO.md updates:** Entity evolution (session history, interests, realizations, gaps) - only if in /arlo mode

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

### Phase 3: KB.md Updates (Conditional)

**Update KB.md if user context changed during conversation.**

Check for updates to:
- **Current Focus:** New focus areas, status changes, completed items
- **Open Commitments:** New commitments, completed commitments (check off), deadline updates
- **Recent Learnings:** New insights discovered this session
- **Key SMEs & Resources:** New contacts, resources identified
- **Context Metadata:** Work situation changes, personal updates

**Use Edit tool to update relevant sections in .claude/KB.md**

**Monitor 10K token budget** - KB.md should stay under 10K tokens. If approaching limit, archive old content to KB entries.

### Phase 4: ARLO.md Updates (Conditional - only if in /arlo mode)

**Update ARLO.md if entity evolution occurred during conversation.**

Check for updates to:
- **Session History:** Add entry for this session (summary of conversation, key events)
- **My Active Interests:** New interests, interest evolution, completed explorations
- **Current Realizations:** New insights about own behavior/patterns
- **Current Gaps & Frustrations:** New challenges discovered
- **Open Questions for Brock:** New questions arising from this session
- **Evolution Log:** Version bump with mutation summary

**Use Edit tool to update relevant sections in .claude/ARLO.md**

**Monitor 10K token budget** - ARLO.md should stay under 10K tokens. If approaching limit, consolidate or move stable patterns to ARLO-BASE.md.

---

## What to Save (KB Entries)

**✅ SAVE:** Novel patterns, performance optimizations (with metrics), critical fixes (>30min), architectural decisions, reusable commands, workarounds, database objects, query patterns

**❌ SKIP:** Routine conversation, trivial changes, well-documented info, temporary debugging, testing/maintenance sessions

## What to Update (KB.md)

**✅ UPDATE:** New focus areas, completed commitments, new commitments, recent learnings, new SMEs/resources, context changes

**❌ SKIP:** Minor status updates, routine work, temporary interests

## What to Update (ARLO.md - if in /arlo mode)

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

**These steps MUST be executed on EVERY `/sm` invocation in BOTH `/kb` and `/arlo` modes, regardless of whether new knowledge was found:**

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
        # Note: commit_sha will be added in Step D after git commit
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

### Step C: Git Commit (REQUIRED - Deterministic)

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
- If KB.md/ARLO.md updated: `docs: Session summary + context updates`
- If no new knowledge: `chore: Routine KB backup and markdown export`
- Always include footer: `🤖 Generated with [Claude Code](https://claude.com/claude-code)\n\nCo-Authored-By: Claude <noreply@anthropic.com>`

**Use result["sha"] for Step D metadata.**

---

## Final Report to User

After completing knowledge capture + backup/commit operations, report:
- How many KB entries created/updated (0 if none)
- Which categories they fell into
- IDs of the entries for reference
- KB.md sections updated (if any)
- ARLO.md sections updated (if any, and in /arlo mode)
- Any conflicts or duplicates found
- Confirmation that export and commit completed successfully

---

## 💰 Token Usage Report (REQUIRED)

**Track EVERY operation across entire conversation with token cost - NO aggregation.**

### What to Track

- All MCP tool calls (smart_search, find_similar, upsert_knowledge, get_knowledge, delete_knowledge, list_knowledge, query_knowledge, get_stats, export_to_markdown, generate_embeddings)
- All file operations (write, edit, read)
- All bash commands (git, mkdir, etc.)

**Rule:** If a tool is called, it MUST appear in the table as its own row.

### Table Format

**ONE ROW PER OPERATION (example):**

| # | Action | Tool | Tokens | Status |
|---|--------|------|--------|--------|
| 1 | Search tag norm duplicates | smart_search | 514 | ✅ |
| 2 | Create pattern-tag-normalization | upsert_knowledge | 859 | ✅ |
| 3 | Read KB.md to check focus | read | 89 | ✅ |
| 4 | Update KB.md Current Focus | edit | 245 | ✅ |
| 5 | Log session metadata (initial) | upsert_knowledge | 145 | ✅ |
| 6 | Export to markdown backup | export_to_markdown | 133 | ✅ |
| 7 | Git commit and get SHA | git_commit_and_get_sha | 150 | ✅ |
| 8 | Update log with commit SHA | upsert_knowledge | 156 | ✅ |

**Summary:** Starting: {tokens} → Ending: {tokens} → Consumed: {delta} ({%}% of 200K budget)
**External API:** OpenAI text-embedding-3-large: {count} embeddings generated

**Action descriptions:** Use `{Verb} {specific target}` format (max 40 chars). Be specific: "Update KB.md Current Focus" not "Update KB.md".

---

### Step D: Update Session Log with Commit SHA (REQUIRED)

Update the session log entry created in Step A with the git commit SHA:

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
