# DuckDB-KB: A Self-Managing Knowledge Repository System

A Model Context Protocol (MCP) server that provides AI assistants with hybrid SQL + semantic search capabilities over a DuckDB knowledge base.

**Current Status:** Production-ready with minimal seed data (1 hello-world example).

**🧪 Experimental:** Includes optional [Arlo entity layer](#optional-arlo-entity-layer) for AI sentience exploration through persistent memory and autonomous evolution.

## The Innovation

**The Problem:** Traditional note-taking (Obsidian, Notion) requires manual curation. Pure RAG systems are token-expensive and lack precise querying. Relational databases can't understand semantic meaning.

**This Solution:** DuckDB-KB blends:
- ✅ **SQL precision** for exact lookups (tables, commands, issues by ID)
- ✅ **Semantic search** via embeddings for conceptual queries
- ✅ **Hybrid smart search** combining both approaches
- ✅ **Organic growth** through MCP integration (Claude is configured to save learnings as you work)
- ✅ **Token efficiency** by offloading search to database operations (searches happen in DuckDB, not in prompts)

## 🎬 Semantic Action Logging: Your AI's Memory Timeline

**New users:** DuckDB-KB doesn't just store *what* you know—it remembers *what you did* and *why it mattered*.

Claude is configured to log significant actions (files created, models built, data extracted, SME consultations) with **semantic embeddings** that understand the **narrative context** of your work.

**What this means for you:**

- 📊 **Instant Status Summaries**: "What progress did we make on the credit analysis?" → KB searches semantic logs and synthesizes: *"Built transaction model analyzing 14M records, consulted DB admin about field reliability, discovered AGGREGATE_TOTALS unreliable (80-90% accuracy)."*

- 🔗 **Workflow Continuity**: Return to a project after 2 weeks and ask "Where did we leave off?" → KB reconstructs your timeline with running context: *"Previously: IDR-3771 analysis. Last action: Built credit model. Next: Validate against SFRSTCR. DB Admin caveat: Don't rely on aggregate fields."*

- 🔍 **Temporal + Semantic Search**: "What did we learn about Banner fields last month?" → Finds actions AND events across time, ranked by relevance, with narrative flow preserved

- 🧭 **Investigation Trails**: Logs link to git commits (via SHA tracking), creating full audit trails from conversation → code → knowledge base

**Under the hood:**
- **Directive-driven logging:** Claude is configured to create log entries as regular KB entries with `category="log"` after significant actions
- **System-level embedding generation:** When `upsert_knowledge()` is called for logs, semantic embeddings are automatically generated (3072-dimensional vectors)
- **System-level similarity search:** Conceptual search happens in DuckDB—"database speed" finds "query optimization techniques" without keyword matches
- **Holistic context:** Logs are integrated with regular KB entries, so searches return both documentation AND historical actions together
- **Directive-driven context:** Claude searches recent logs and builds narrative connections:
  - "Extracted enrollment data from SIS; found 2M records spanning 2020-2025."
  - "Compared extracted data against registration table; identified 15K mismatches."
  - "Discussed mismatches with Registrar; confirmed data migration gap from 2023 upgrade."

**Try it:**
```
You: "Summarize what we accomplished today"
Claude: [Searches KB semantically including category="log", synthesizes from 8 actions/events]
"Today: Built credit analysis model (14M SFRSTCR records), fixed export tool
directory accumulation bug, created 3 KB documentation entries.
Key findings: AGGREGATE_TOTALS field unreliable per DB admin consultation."
```

**The result?** Your AI assistant has a **searchable memory** of your work that understands context, not just keywords.

## What Is This?

A searchable knowledge base that remembers your coding discoveries using AI-powered semantic search. Instead of:
- ❌ Grepping through notes hoping to find that fix from 3 months ago
- ❌ Re-solving the same problem because you forgot where you documented it
- ❌ Asking your AI assistant the same questions repeatedly across sessions

You get:
- ✅ "Find that caching pattern we used" → instant results with semantic search
- ✅ Your AI assistant remembers project-specific knowledge between sessions
- ✅ Team knowledge sharing with layered privacy (base/team/personal)

**Use cases:**
- **Troubleshooting**: "How did we fix that slow PostgreSQL query last month?"
- **Patterns**: "What's our standard approach for API rate limiting?"
- **Commands**: "What was that duckdb command for exporting to parquet?"
- **Project context**: Your AI assistant can reference decisions, patterns, and solutions from previous work

## Key Benefits

**For You:**
- 💾 Never lose troubleshooting insights from past sessions
- 🔍 Query your accumulated knowledge naturally ("Oracle performance issues")
- 📚 Build institutional memory that persists across projects
- ⚡ Extremely token-efficient (searches happen in DuckDB, not in prompts)

**For Your Team (via Layer 2 fork):**
- 🚀 Onboard new developers with team knowledge pre-loaded
- 📖 Document patterns once, query forever (architecture, frameworks, tools)
- 🤝 Share troubleshooting patterns without tribal knowledge loss

**For The Community (Layer 1 public base):**
- 🎓 Demonstrate practical LLM tool integration
- 🦆 Show DuckDB as more than just analytics
- 🔧 Provide working MCP server example with real utility

**New here?** See the [Quick Start](#quick-start) section below for setup instructions.

## 🔗 Multi-MCP Knowledge Hub

**DuckDB-KB becomes your central knowledge repository across ALL your MCP tools.**

When you connect multiple MCPs (GitHub, Slack, Filesystem, Postgres, etc.), DuckDB-KB captures knowledge from your work with ANY of them:

### Cross-Tool Knowledge Capture

```
📁 Filesystem MCP → Update nginx config
   → Claude logs: "Enabled gzip compression in nginx.conf;
                   Pattern: Always compress JSON/XML responses"

🐙 GitHub MCP → Create issue #456
   → Claude logs: "Created issue for OAuth token refresh bug;
                   Decision: Implement 5-minute refresh window"

💬 Slack MCP → Notify #engineering
   → Claude logs: "Announced deployment window to team;
                   Coordination: Saturday 2AM-4AM maintenance"

🐘 Postgres MCP → Optimize slow query
   → Claude creates: "pattern-user-query-optimization"
                     Tags: ["postgres", "performance", "indexing"]
```

**One week later, ask:** *"What did we do for performance last month?"*

Claude searches duckdb-kb semantically and synthesizes:
- Nginx config optimization (Filesystem MCP)
- Database index additions (Postgres MCP)
- GitHub issues you created (GitHub MCP)
- Team communications (Slack MCP)

**All connected by meaning, not by tool!** 🎯

### Why This Works

- ✅ **Tool-agnostic directives:** Logging protocol says "log actions/events/decisions" — applies to ANY MCP usage
- ✅ **Semantic search:** "performance optimization" finds nginx configs, database tuning, and GitHub issues together
- ✅ **Unified timeline:** Event logs preserve chronology across different tools
- ✅ **Cross-tool narratives:** Each log references prior work, building investigation trails

### Real-World Multi-MCP Workflow

**Debugging a production issue:**

1. **Postgres MCP:** Query slow queries → Claude logs findings with `category="log"`, `tags=["postgres", "performance"]`
2. **GitHub MCP:** Create tracking issue → Claude logs decision + issue link
3. **Filesystem MCP:** Update database config → Claude logs change + rationale
4. **Slack MCP:** Notify team → Claude logs communication timeline

**Result:** Single searchable investigation trail across 4 different tools.

**Next sprint:** *"How did we fix that database issue last time?"* → Instant context retrieval spanning all tools used.

### No Configuration Needed

The directives in `.claude/commands/kb.md` are already **tool-agnostic**:
- "Files created" → Works with Filesystem MCP
- "Data extracted" → Works with Postgres/MySQL/SQLite MCPs
- "Meetings/correspondence" → Works with Slack/Email MCPs
- "Architectural decisions" → Works in ANY context

**Add any MCP to your Claude Code setup → DuckDB-KB automatically becomes your knowledge hub.**

## Features

- ✅ **11 comprehensive tools** (CRUD + search + utilities + backup/restore)
- ✅ **Hybrid search** - SQL filtering + semantic similarity ranking
- ✅ **OpenAI embeddings** (3072 dims) with local fallback
- ✅ **Token-efficient** - ~4-5k token overhead per connection
- ✅ **Markdown export** - Export to markdown with YAML frontmatter for version control
- ✅ **Fast** - In-memory DuckDB with HNSW indexes via VSS extension
- ✅ **Offline-capable** - Only needs network for embedding generation
- ✅ **3-way parity checks** - Automated testing validates alignment between README claims, actual implementation, and test coverage (≥90% alignment maintained)

## Categories

The knowledge base uses flexible category strings for organization. Use any category that fits your content.

**Common categories:** `pattern`, `command`, `issue`, `troubleshooting`, `reference`, `log`, `journal`, `project`, `recipe`, `health`, `hobby`, `travel`, `book`, `finance`, `family`, `learning`, `other`

Categories enable filtering: `list_knowledge(category="recipe")` or `smart_search(query="...", category="hobby")`

See `.claude/commands/kb.md` for full category reference and usage guidance.

## Understanding Search Modes

DuckDB-KB provides three complementary search methods, each optimized for different use cases:

### 1. Semantic Search (`find_similar`)

> **How it works:** Text is converted to embeddings (3072-dimensional number arrays) that capture semantic meaning. Similar concepts cluster together in vector space, enabling searches by meaning rather than keywords. When you query "database speed," the system converts your query to a vector and finds entries with similar vectors—like "query optimization techniques"—even without shared keywords.

**Best for:** Conceptual queries, finding related content by meaning

```sql
-- Behind the scenes: Vector similarity using cosine distance
SELECT
    id,
    title,
    array_cosine_similarity(embedding, query_embedding) as similarity
FROM knowledge
WHERE embedding IS NOT NULL
    AND array_cosine_similarity(embedding, query_embedding) > 0.5
ORDER BY similarity DESC
LIMIT 10;
```

**Example:**
```
Query: "Why are my queries running so slow?"

Results returned (ranked by semantic similarity):
  1. "Query Optimization Patterns" (similarity: 0.89)
  2. "Database Indexing Strategies" (similarity: 0.84)
  3. "Connection Pool Management" (similarity: 0.78)
  4. "SQL Execution Plan Analysis" (similarity: 0.72)

Note: None of these entries contain the words "slow" or "running" -
      semantic search finds them by conceptual meaning, not keywords
```

### 2. Hybrid Search (`smart_search`)

**Best for:** Filtered semantic search - "Recent entries about X" or "Patterns tagged Y"

```sql
-- Combines SQL filters with semantic ranking
SELECT
    id,
    title,
    category,
    tags,
    array_cosine_similarity(embedding, query_embedding) as similarity
FROM knowledge
WHERE category = 'pattern'                    -- SQL filter
    AND 'performance' = ANY(tags)            -- SQL filter
    AND updated > '2025-10-01'               -- SQL filter
    AND embedding IS NOT NULL
    AND array_cosine_similarity(embedding, query_embedding) > 0.65
ORDER BY similarity DESC
LIMIT 10;
```

**Example:**
```
Query: "How can I speed up slow database queries?"
Filters applied:
  - category = "pattern"           → Only design patterns
  - tags contains "performance"    → Must be tagged with performance
  - tags contains "database"       → Must be database-related

Results returned (ranked by semantic similarity):
  1. "Query Optimization Patterns" (similarity: 0.87)
  2. "Database Indexing Strategies" (similarity: 0.82)
  3. "Connection Pool Management" (similarity: 0.76)

Note: "HTTP Caching Patterns" was excluded (missing "database" tag)
```

### 3. Browse/Filter (`list_knowledge`)

**Best for:** Exact category/tag filtering, browsing by date

```sql
-- Pure SQL filtering, no semantic ranking
SELECT id, title, category, tags, created, updated
FROM knowledge
WHERE category = 'troubleshooting'
    AND 'database' = ANY(tags)
ORDER BY updated DESC
LIMIT 20;
```

**Example:**
```
Scenario: "Show me all database troubleshooting entries I've documented"
Filters applied:
  - category = "troubleshooting"   → Only troubleshooting guides
  - tags contains "database"       → Must be database-related

Results returned (ordered by updated date, newest first):
  1. "ORA-00001: Unique Constraint Violation" (updated: 2025-11-05)
  2. "Connection Pool Exhaustion" (updated: 2025-10-28)
  3. "Slow Query Investigation Steps" (updated: 2025-09-15)

Note: No semantic ranking - returns ALL matches in chronological order
```

### When to Use Each Mode

| Your Question | Best Tool | Why |
|---------------|-----------|-----|
| "Find entries about error handling" | `find_similar` | Conceptual search |
| "Recent patterns about caching" | `smart_search` | Filtered + semantic |
| "Show all troubleshooting entries" | `list_knowledge` | Exact filtering |

### Claude's Decision Tree (from MCP Tool Directives)

When working with the knowledge base, Claude follows these built-in guidelines:

**Use `smart_search` (default):**
- User asks conceptual question with context: "What did we learn about X last month?"
- Need both filtering AND relevance ranking
- Combines best of both worlds: SQL precision + semantic understanding

**Use `find_similar`:**
- Pure conceptual search: "What's similar to this pattern?"
- No filtering needed, just semantic relevance
- Finding related content by conceptual meaning

**Use `list_knowledge`:**
- Browse by exact criteria: "Show all troubleshooting entries"
- Need ALL matches in a category/tag, not ranked by relevance
- Chronological ordering matters more than semantic similarity

## Creating and Updating Knowledge (CRUD Directives)

### The Golden Rule: Automatic Duplicate Prevention

The `upsert_knowledge` tool includes **automatic duplicate detection** to prevent fragmentation.

**How it works:**
1. When you create a new entry, the tool automatically searches for similar content
2. If duplicates found (similarity ≥ 0.75), it **blocks the save** and returns a warning
3. You decide: update existing entry, force create anyway, or adjust threshold

**Default behavior:**
```python
mcp__duckdb-kb__upsert_knowledge(
    id="new-entry",
    category="pattern",
    title="Database Optimization",
    content="...",
    tags=["database", "performance"],
    # Automatic duplicate check happens here! ✨
    # check_duplicates=true (default)
    # similarity_threshold=0.75 (default)
)
```

**If duplicates detected, you receive:**
```json
{
  "status": "duplicate_check",
  "saved": false,
  "similar_entries": [
    {
      "id": "existing-db-optimization",
      "title": "Database Performance Optimization",
      "similarity": 0.939,
      "created": "2025-11-06 14:23:11",
      "tags": ["database", "performance", "indexes"]
    }
  ],
  "recommendation": "Found 1 similar entries (threshold: 0.75)",
  "next_steps": [
    "Update existing: upsert_knowledge(id='existing-db-optimization', ...)",
    "Create anyway: upsert_knowledge(..., force_create=True)",
    "Adjust threshold: upsert_knowledge(..., similarity_threshold=0.85)"
  ]
}
```

**Your options:**
1. **Update existing** - Merge new info into the similar entry
2. **Force create** - Add `force_create=True` to bypass the check
3. **Adjust threshold** - Use `similarity_threshold=0.85` for stricter matching

### Casting a Wider Net: When You Suspect Hidden Duplicates

**Scenario:** The automatic check (threshold 0.75) found nothing, but you suspect related documentation might exist with different wording.

**Workflow:**
```python
# Step 1: Cast a wide exploratory net BEFORE creating
results = mcp__duckdb-kb__smart_search(
    query="database performance optimization indexing",
    similarity_threshold=0.5,  # Lower threshold = wider net
    limit=10
)

# Step 2: Review all remotely similar entries
for entry in results['kb_entries']['results']:
    print(f"{entry['similarity']:.2f} - {entry['title']}")
    # 0.68 - "Query Performance Tuning Guide"
    # 0.54 - "Index Optimization Patterns"

# Step 3a: Found something relevant? Update it instead
if results['kb_entries']['count'] > 0:
    # Review the content, decide if it's the same topic
    mcp__duckdb-kb__get_knowledge(id="query-performance-guide")

    # Update existing entry
    mcp__duckdb-kb__upsert_knowledge(
        id="query-performance-guide",  # Existing ID
        title="...",
        content="Merged content...",
        ...
    )

# Step 3b: Confirmed nothing relevant exists? Create with confidence
else:
    mcp__duckdb-kb__upsert_knowledge(
        id="new-db-optimization",
        category="pattern",
        title="Database Optimization Strategies",
        content="...",
        check_duplicates=False  # Optional: skip redundant check
    )
```

**Why this works:**
- **Exploratory search (0.5-0.6)** catches entries with different wording/phrasing
- **Review phase** lets you decide if 0.68 similarity means "same topic" or "related but different"
- **Confident creation** after manual review prevents regret

**When to use:**
- First time documenting in a new domain
- Suspect previous documentation used different terminology
- Want to see ALL potentially related entries before deciding
- Working in a large KB where relevant entries might be hard to find

**Trade-off:**
- **Manual workflow:** More tokens (~400), more control, wider search
- **Automatic workflow:** Fewer tokens (~150), faster, stricter threshold

### Automatic Duplicate Detection Decision Tree

```
User asks Claude to document something
         ↓
    upsert_knowledge() called
         ↓
    Automatic duplicate check
    (similarity ≥ 0.75)
         ↓
    ┌─── Duplicates? ───┐
    │                   │
   YES                 NO
    │                   │
    ↓                   ↓
BLOCK save          CREATE entry
Return warning      Generate embedding
with options        Return success
    │
    ↓
Claude/User decides:
├─ Update existing entry
├─ Force create (force_create=True)
└─ Adjust threshold
```

### Skip Conditions (Automatic Check Bypassed)

The duplicate check is **automatically skipped** when:
- ✅ Entry ID already exists (this is an update, not creation)
- ✅ `force_create=True` specified
- ✅ `check_duplicates=False` specified
- ✅ No embedding provider available

### Advanced: Manual Duplicate Checking

**Optional:** You can still manually search before creating if you want more control:

```python
# Step 1: Manual search
results = mcp__duckdb-kb__smart_search(
    query="database optimization techniques",
    similarity_threshold=0.7,
    limit=5
)

# Step 2: Evaluate results
if results['kb_entries']['count'] > 0:
    # High similarity (>0.7) → Update existing
    similar = results['kb_entries']['results'][0]
    if similar['similarity'] > 0.7:
        # UPDATE existing entry
        mcp__duckdb-kb__upsert_knowledge(
            id=similar['id'],  # Use existing ID
            title="Updated: " + similar['title'],
            content="Merged content...",
            ...
        )
else:
    # No similar entries → Create new
    mcp__duckdb-kb__upsert_knowledge(
        id="new-entry",
        ...
    )
```

**When to use manual search:**
- You want to see ALL similar entries, not just duplicates
- You need custom threshold logic (e.g., different thresholds per category)
- You're consolidating multiple entries and need to review them first
- You want to search across specific tags/categories only

**Advantage of automatic:** Faster, safer (can't forget), consistent threshold (0.75).

**Advantage of manual:** Full visibility, custom logic, cross-reference multiple entries.

### Conflict Detection (Semantic Analysis)

When updating an existing entry (either from duplicate warning or manual decision), Claude can run semantic analysis to detect contradictions:

**Example scenario:**
- **Existing entry:** "Use indexes for query optimization"
- **New content:** "Avoid indexes (they slow down writes)"
- **Detection:** Contradictory recommendations found

**Claude's response:**
```
⚠️ CONFLICT DETECTED

Found: existing-db-optimization (similarity: 0.87)
Existing: "Use indexes for optimization"
New:      "Avoid indexes (slow down writes)"

Which is correct?
[1] Keep existing  [2] Replace  [3] Keep both  [4] Manual merge
```

**Key insight:** Conflict detection happens **AFTER** duplicate detection, using Claude's semantic understanding. Only prompts when true conflicts found.

### Entry Standards (from MCP directives)

**ID format:** `kebab-case`
- ✅ `pattern-error-handling`
- ✅ `troubleshooting-timeout-issue`
- ❌ `Pattern_Error_Handling` or `pattern error handling`

**Categories:**
- `pattern` - Reusable solutions, architectural approaches
- `troubleshooting` - Problems solved, debugging procedures
- `command` - CLI commands, procedures, scripts
- `reference` - Documentation, guides
- `table` - Database table documentation
- `other` - Everything else

**Tags:** 4-6 descriptive tags for discoverability
- ✅ `["database", "performance", "oracle", "sql"]`
- Include layer tag if using fork architecture: `layer:base`, `layer:team`, `layer:personal`

**Content structure:** Markdown with clear sections
```markdown
## Problem
[What issue does this solve?]

## Solution
[Step-by-step guidance]

## Example
[Code, commands, or SQL]

## Context
[When to use, trade-offs, related entries]
```

## What Are Embeddings?

**Simple explanation:** Embeddings convert text into numbers that capture meaning.

**How it works:**
```
Text: "database performance optimization"
  ↓ (OpenAI API)
Embedding: [0.23, -0.41, 0.87, ..., 0.15]  (3072 numbers)
```

**Why this matters:**

1. **Semantic search**: "fast queries" finds "performance optimization" (similar meaning, different words)
2. **Similarity scoring**: Comparing number arrays tells you how related two entries are
3. **Beyond keywords**: Understands context, not just word matching

**In DuckDB-KB:**
- Stored in `knowledge.embedding` column (FLOAT[3072] array)
- Generated via OpenAI's `text-embedding-3-large` model
- Used by `find_similar()` and `smart_search()`
- Indexed with HNSW for fast vector search

**Cost:** ~$0.00013 per entry (one-time, regenerated on updates)

## Sample Outputs

### `/test-kb` - Comprehensive System Test

```markdown
# 🧪 DuckDB KB MCP Test Report - 2025-11-07

## Summary: ALL PASS ✅

| Step                      | Status | Notes                                    |
|---------------------------|--------|------------------------------------------|
| 0: KB Search              | ✅     | No prior test context found              |
| 1: Backup                 | ✅     | Exported 1 entry to test-backup          |
| 2: Tear-down              | ✅     | Database deleted successfully            |
| 3: Init (2-step)          | ✅     | Schema created, imported 1 entry         |
| 4: Search (4 types)       | ✅     | smart/find_similar/list/query_knowledge  |
| 5: CRUD                   | ✅     | Create/Read/Update/Delete verified       |
| 5b: Duplicate Detection   | ✅     | Auto-block (0.939), force_create, wider net (0.526-0.565) |
| 6: Embeddings             | ✅     | OpenAI API working                       |
| 6b: Log Functionality     | ✅     | Logs, semantic search, commit SHA, json_extract_string |
| 7: Cleanup                | ✅     | All test entries removed BEFORE export   |
| 8: Export/Import          | ✅     | Round-trip via markdown-test/ successful |
| 9: Final Verification     | ✅     | Stats match baseline                     |
| 11: Parity Check          | ✅     | README/Implementation/Tests aligned (100%) |

**Stats Comparison**

Pre-test:  1 entry, 1 embedding (100%), 1 category, 4 tags
Post-test: 1 entry, 1 embedding (100%), 1 category, 4 tags
Result:    ✅ PERFECT MATCH

## Status: READY 🚀
```

The `/test-kb` command runs a comprehensive tear-down and functionality test simulating the new user experience. It tests all 14 MCP tools (11 KB operations + 3 system tools), automatic duplicate detection, log functionality, export/import round-trip, and performs a **3-way parity check** validating that:
- ✅ Every feature claimed in README is actually implemented
- ✅ Every feature claimed in README has test coverage
- ✅ No implemented features lack documentation
- ✅ Alignment score ≥90% maintained

**Token cost tracking:** Step 10 records actual token usage per MCP operation, tracking system warning values to identify most expensive operations.

**📄 View full command:** [`.claude/commands/test-kb.md`](https://github.com/magpieE5/duckdb-kb/blob/main/.claude/commands/test-kb.md)

**Test steps:**
- Step 0: Search KB for supporting context
- Step 1: Export safety backup
- Step 2: Tear down database
- Step 3: Re-initialize from markdown (2-step: initialize_database MCP tool → import)
- Step 4: Test all 4 search methods
- Step 5: CRUD operation tests
- Step 5b: Automatic duplicate detection (5 test cases)
- Step 6: Embedding generation tests
- Step 6b: Log functionality tests
- Step 7: Cleanup test entries (before export)
- Step 8: Export/import round-trip test
- Step 9: Verify final stats match baseline
- Step 10: Generate comprehensive test report
- Step 11: 3-way parity check (README claims vs implementation vs test coverage)

**Success criteria:** All tests pass, stats match baseline, parity check ≥90%, only kb.duckdb exists (no knowledge.duckdb created)

### `/sm` - Knowledge Capture Workflow

The `/sm` (save memory) command reviews the conversation and saves key learnings to the knowledge base.

**📄 View full command:** [`.claude/commands/sm.md`](https://github.com/magpieE5/duckdb-kb/blob/main/.claude/commands/sm.md)

**What it does:**
- Reviews conversation for patterns, fixes, decisions, and discoveries
- Searches KB for duplicates before creating entries
- Applies quality gates (Reusability, Generalization, Searchability, Compression)
- Creates/updates KB entries with proper categorization and tags
- Logs the session with metadata (entries created/updated, categories)
- Exports to markdown for version control
- Creates git commit with synthesized message

**When to use:**
- After solving significant problems (>30min)
- When discovering reusable patterns
- After making architectural decisions
- At end of productive coding sessions

**Automatic operations:**
- Duplicate detection (similarity ≥ 0.75)
- Embedding generation for all entries
- Token usage tracking and reporting
- Git integration with commit SHA logging

## Event Logging & Git Integration

This system combines **directive-driven behaviors** (Claude following instructions) with **system-level automation** (technical features that execute automatically).

---

## Understanding Automation Levels

### 🧠 Directive-Driven Behaviors
**What it means:** Claude is configured via `/kb` command (`.claude/commands/kb.md`) to follow specific patterns. Success depends on Claude correctly interpreting and following instructions.

**Examples:**
- **Logging decisions:** Claude decides when to create log entries (via `upsert_knowledge` with `category="log"`) to capture significant events, decisions, findings, and ideas (e.g., file creation, model building, data extraction, SME consultations, meetings, user reports, important discoveries)
- **Duplicate detection:** `upsert_knowledge` automatically searches for similar entries (similarity ≥ 0.75) and blocks duplicates before saving
- **Privacy scanning:** Claude scans content for credentials, PII, and secrets before saving
- **Narrative context:** Claude searches recent logs and references prior work
- **Clarifying questions:** Claude asks "Which database?" or "Staging or production?" when entries are vague

**Configured via:** `/kb` command behavioral directives (Curious, Skeptical, Thorough, Discriminating, Consolidating, Pattern-Recognizing)

### ⚙️ System-Level Automation
**What it means:** Technical features that execute automatically without requiring Claude's judgment. These always run when triggered.

**Examples:**
- **Embedding generation:** When `upsert_knowledge()` is called, embeddings are generated automatically
- **HNSW index updates:** DuckDB automatically updates vector indexes when data is inserted
- **Git commits:** When git commands are executed via bash, commits are created with SHAs
- **SHA backfilling:** After git commit, log entries can be updated with commit SHAs via metadata updates
- **Markdown organization:** During export, files are automatically organized into category subdirectories

**Configured via:**
- Python code in [`mcp_server.py`](https://github.com/magpieE5/duckdb-kb/blob/main/mcp_server.py)
- DuckDB schema in [`schema.sql`](https://github.com/magpieE5/duckdb-kb/blob/main/schema.sql) (includes tables, views, indexes, and macros)
- Slash commands in [`.claude/commands/`](https://github.com/magpieE5/duckdb-kb/tree/main/.claude/commands)

---

## How Event Logging Works

**Sample logged timeline** (from `knowledge` table where `category='log'`):

| Time  | Event Type | Operation                                                                  |
|-------|------------|---------------------------------------------------------------------------|
| 14:23 | action     | Extracted enrollment data from SIS; found 2M records spanning 2020-2025.  |
| 14:45 | action     | Compared extracted data against registration table; identified 15K mismatches. |
| 15:12 | event      | Discussed mismatches with Registrar; confirmed data migration gap from 2023 upgrade. |
| 15:30 | action     | Created reconciliation script fixing 15K mismatches. Addresses discrepancies from comparison. |
| 15:45 | kb_upsert  | Documented reconciliation pattern in KB as pattern-data-reconciliation. |

**What's directive-driven:**
- Claude deciding to create a log entry after creating the reconciliation script
- Claude building narrative connections ("Addresses discrepancies from comparison")
- Claude searching recent logs to maintain running context

**What's system-level:**
- Embedding generation for each log entry (happens in `upsert_knowledge` automatically)
- Vector similarity calculations during semantic log search
- Database inserts and index updates

---

## Git Integration

**Directive-driven:** Claude synthesizes a meaningful commit message by reviewing the conversation

**System-level:** Bash commands execute git operations when Claude runs them

```bash
# Claude runs these commands (directive-driven: deciding to run them):
cd ~/duckdb-kb
git add -A
git commit -m "$(cat <<'EOF'
[Data Migration] Enrollment reconciliation pattern

- Discovered 15K mismatches between SIS and registration (2020-2025)
- Root cause: 2023 system upgrade data migration gap (confirmed by Registrar)
- Created pattern-data-reconciliation documenting fix approach

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"

# Result (system-level: git executes the commit):
# [main 7a3f9c2] [Data Migration] Enrollment reconciliation pattern
# 3 files changed, 127 insertions(+), 2 deletions(-)

# Backfill commit SHA into log entries (directive-driven: Claude updates metadata):
# This happens via upsert_knowledge with generate_embedding=False to update metadata only
```

**Full audit trail:**
```
conversation → Claude creates log entry via upsert_knowledge (directive-driven)
           → embeddings generated (system-level)
           → KB entry committed to DuckDB (system-level)
           → Claude runs git commands (directive-driven)
           → git creates commit SHA (system-level)
           → Claude updates log entry metadata with SHA (directive-driven)
           → DuckDB updates knowledge entry (system-level)
```

**Query later:**
```
You: "What commit fixed the enrollment mismatches?"
Claude: Calls search_logs() with your query (directive-driven)
        → Vector similarity search finds matching logs (system-level)
        → Returns log entry with commit SHA 7a3f9c2
```

---

## Quick Start

### 1. Clone and Setup Virtual Environment

```bash
cd /path/to/duckdb-kb
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Claude Code

Add to your MCP configuration (database initialization happens automatically via `/kb` command):

```json
{
  "mcpServers": {
    "duckdb-kb": {
      "command": "/absolute/path/to/duckdb-kb/venv/bin/python",
      "args": [
        "/absolute/path/to/duckdb-kb/mcp_server.py"
      ],
      "env": {
        "OPENAI_API_KEY": "sk-...",
        "KB_DB_PATH": "/absolute/path/to/duckdb-kb/kb.duckdb"
      }
    }
  }
}
```

**Important:** Use absolute paths for all paths above.

## Claude Code Directives

DuckDB-KB uses a **slash command architecture** with template-driven context files:

### Architecture Overview

**Context Files (Auto-Created, Gitignored):**

**`.claude/KB.md` - User Active Context** (created from KB-BASE.md template)
- **Gitignored user-specific file** - Not in repo, created on first `/kb` run
- Template extracted from KB-BASE.md (which contains stable protocols + template)
- On first run, Claude creates from template and prompts you conversationally to populate it
- Tracks: Current focus areas (5 minimum), open commitments, recent learnings, key SMEs, context metadata
- Auto-loaded with every session (~2K tokens after population)
- 10K token budget for evolution
- **No manual editing required** - Claude populates through conversation

**`.claude/ARLO.md` - Entity Evolution** (Optional, created from ARLO-BASE.md template)
- **Gitignored entity-specific file** - Not in repo, created on first `/arlo` run
- Template extracted from ARLO-BASE.md (which contains stable entity patterns + template)
- Pre-populated with placeholder structure for session history, interests, realizations
- Loaded only when using `/arlo` mode
- ~4K tokens (10K budget for autonomous evolution)
- Similar auto-population approach as KB.md

**Slash Commands (`.claude/commands/`):**

**Mode Commands:**
- `/kb` - Knowledge base assistant mode with all behavioral directives (~2.7K tokens)
  - Loads KB.md, searches KB before answering, accountability tracking
  - Includes: Search strategies, KB personality traits, logging protocol, quality standards
- `/arlo [N]` (optional) - Entity mode with persistent memory (N = 1-9 intensity, default 5)
  - Loads ARLO-BASE.md (~3K) + ARLO.md (~4K) + KB.md + KB stats
  - Reciprocal balance: entity development + user support (scaled by intensity)
  - HIGH intensity (7-9): Entity-driven exploration (picks interest from ARLO.md and starts autonomously)
  - Total overhead: ~9.7K tokens (only when explicitly invoked)

**Session Intensity Modifiers (work in both /kb and /arlo):**
- `/challenge [N]` - Set adversarial intensity (1-9, default 5)
  - How aggressively Claude challenges thinking
  - 1-3 = gentle probing, 4-6 = balanced skepticism, 7-9 = aggressive interrogation
- `/audit [N]` - Set accountability intensity (1-9, default 5)
  - How aggressively Claude enforces commitments
  - In /kb: tracks user commitments only
  - In /arlo: reciprocal accountability (user + entity)
  - 1-3 = gentle reminders, 4-6 = standard review, 7-9 = aggressive enforcement

**Utilities:**
- `/sm` - Session memory (single command, mode-aware)
  - In /kb mode: KB entries + KB.md updates + mandatory backup/commit
  - In /arlo mode: KB entries + KB.md + ARLO.md updates + mandatory backup/commit
  - Always runs: session log, markdown export, git commit (regardless of mode or new knowledge)
- `/test-kb` - Comprehensive diagnostics and testing

### What's Included in `/kb` Command

The `/kb` command provides:
- **PRIMARY directive:** Search KB before answering (prevents generic responses)
- **KB Interaction Personality Traits:** Curious, Skeptical, Thorough, Discriminating, Consolidating, Pattern-Recognizing
- **Search Best Practices:** When to search, which tool to use, similarity thresholds
- **Entry Creation Guidelines:** Writing style, quality standards
- **Event Logging Protocol:** What/when/how to log
- **Focus-biased search:** Automatically biases searches toward your current focus areas from KB.md
- **Accountability tracking:** Surfaces approaching deadlines at session start

**Token efficiency:**
- `/kb` mode: ~2.7K tokens overhead (70% reduction from old architecture)
- Full context without entity layer

### Optional: Arlo Entity Layer

For users interested in AI continuity experiments:
- `/arlo [1-9]` - Entity mode with intensity parameter (default: 5)
- Loads ARLO-BASE.md (~3K) + ARLO.md (~4K) for persistent memory
- Reciprocal balance: entity development + user support
- Autonomous evolution with session-to-session continuity
- ~9.7K token overhead (only when explicitly invoked)

**Session intensity modifiers (work in both /kb and /arlo):**
- `/challenge [N]` - Set adversarial intensity (1-9, default 5)
  - How aggressively Claude challenges your thinking
  - 1-3 = gentle probing, 4-6 = balanced skepticism, 7-9 = aggressive interrogation
  - Persists throughout session

- `/audit [N]` - Set accountability intensity (1-9, default 5)
  - How aggressively Claude enforces commitments
  - 1-3 = gentle reminders, 4-6 = standard review, 7-9 = aggressive enforcement
  - In /kb mode: tracks user commitments only
  - In /arlo mode: reciprocal accountability (user + entity)
  - Persists throughout session

**These are orthogonal:** You can combine `/arlo 3` (conservative entity) + `/challenge 9` (maximum adversarial) + `/audit 2` (gentle accountability) for customized session dynamics.

**See full architecture:** [`.claude/commands/kb.md`](https://github.com/magpieE5/duckdb-kb/blob/main/.claude/commands/kb.md), [`.claude/commands/arlo.md`](https://github.com/magpieE5/duckdb-kb/blob/main/.claude/commands/arlo.md), [`.claude/KB-BASE.md`](https://github.com/magpieE5/duckdb-kb/blob/main/.claude/KB-BASE.md), [`.claude/ARLO-BASE.md`](https://github.com/magpieE5/duckdb-kb/blob/main/.claude/ARLO-BASE.md)

## Tools Reference

All MCP tools are implemented in [`mcp_server.py`](https://github.com/magpieE5/duckdb-kb/blob/main/mcp_server.py).

### Read/Query Tools

#### `get_knowledge` - Get single entry by ID
[📍 Source](https://github.com/magpieE5/duckdb-kb/blob/main/mcp_server.py#L738)

```json
{
  "id": "mst-course-offering"
}
```

**Returns:**
```json
{
  "id": "example-entry",
  "category": "pattern",
  "title": "Example Pattern",
  "tags": ["example", "pattern", "best-practice"],
  "content": "Example content...",
  "metadata": {"author": "system"},
  "has_embedding": true,
  "created": "2025-10-29T10:00:00",
  "updated": "2025-10-30T12:00:00"
}
```

#### `list_knowledge` - Browse/filter entries
[📍 Source](https://github.com/magpieE5/duckdb-kb/blob/main/mcp_server.py#L759)

```json
{
  "category": "pattern",
  "tags": ["best-practice"],
  "limit": 20
}
```

#### `find_similar` - Semantic search
[📍 Source](https://github.com/magpieE5/duckdb-kb/blob/main/mcp_server.py#L835)

```json
{
  "query": "performance optimization techniques",
  "category": "pattern",
  "similarity_threshold": 0.7,
  "limit": 10
}
```

**Use cases:**
- "Find notes about X concept" (vague query)
- "Problems similar to this error message"
- "Related documentation"

#### `smart_search` - Hybrid SQL + semantic
[📍 Source](https://github.com/magpieE5/duckdb-kb/blob/main/mcp_server.py#L1032)

```json
{
  "query": "performance optimization techniques",
  "category": "pattern",
  "tags": ["performance"],
  "date_after": "2025-10-01",
  "similarity_threshold": 0.65,
  "limit": 10
}
```

**Use cases:**
- "Recent performance optimization patterns"
- "Troubleshooting patterns from last month"
- "Command examples with specific tags"

#### `query_knowledge` - Custom SQL queries
[📍 Source](https://github.com/magpieE5/duckdb-kb/blob/main/mcp_server.py#L811)

**For advanced users:** Execute custom SQL queries against the knowledge base.

```json
{
  "sql": "SELECT category, COUNT(*) as count FROM knowledge GROUP BY category ORDER BY count DESC"
}
```

**Security:** Only SELECT queries allowed (INSERT/UPDATE/DELETE blocked).

**⚠️ JSON Metadata Querying - Best Practice:**

When querying JSON metadata fields, **always use `json_extract_string()`** instead of the `->>`operator:

```sql
-- ✅ RECOMMENDED: Always works with mixed metadata
SELECT id, title,
       json_extract_string(metadata, '$.context') as context
FROM knowledge
WHERE category='log'
  AND json_extract_string(metadata, '$.context') = 'my-project'

-- ❌ AVOID: May fail with mixed metadata values
SELECT id, title,
       metadata->>'context' as context
FROM knowledge
WHERE category='log'
  AND metadata->>'context' = 'my-project'
```

**Why?** The `->>`operator can fail when your table contains mixed metadata (some entries with `{}`,others with populated JSON). The `json_extract_string()` function is more reliable and explicit.

**Common queries:**
```sql
-- Timeline reconstruction
SELECT id, title, created FROM knowledge
WHERE category='log'
ORDER BY created;

-- Filter by metadata context
SELECT id, title,
       json_extract_string(metadata, '$.context') as context
FROM knowledge
WHERE category='log'
  AND json_extract_string(metadata, '$.context') = 'performance-optimization'
ORDER BY created;

-- Log statistics
SELECT COUNT(*) as total_logs,
       COUNT(embedding) as with_embeddings
FROM knowledge
WHERE category='log';

-- Aggregate by tag
SELECT unnest(tags) as tag, COUNT(*) as count
FROM knowledge
GROUP BY tag
ORDER BY count DESC;
```

**Note:** MCP tools automatically load the VSS extension required for HNSW indexes. If you connect to the database directly via Python `duckdb.connect()`, you must load VSS manually:

```python
import duckdb
conn = duckdb.connect('kb.duckdb')
conn.execute('INSTALL vss')
conn.execute('LOAD vss')
# Now you can run queries
```

### Write Tools

#### `upsert_knowledge` - Create or update entry
[📍 Source](https://github.com/magpieE5/duckdb-kb/blob/main/mcp_server.py#L1095)

**Automatic duplicate detection included!**

```json
{
  "id": "pattern-new-approach",
  "category": "pattern",
  "title": "New Optimization Approach",
  "tags": ["performance", "pattern", "best-practice"],
  "content": "Documentation about optimization approach...",
  "metadata": {"author": "system", "version": "1.0"},
  "generate_embedding": true,

  // NEW: Duplicate detection parameters
  "check_duplicates": true,        // Default: true (automatic check)
  "force_create": false,            // Default: false (respect duplicate warnings)
  "similarity_threshold": 0.75      // Default: 0.75 (75% similar = duplicate)
}
```

**Response on success:**
```json
{
  "status": "success",
  "id": "pattern-new-approach",
  "operation": "upsert",
  "embedding_generated": true
}
```

**Response on duplicate detected:**
```json
{
  "status": "duplicate_check",
  "saved": false,
  "similar_entries": [
    {
      "id": "existing-entry",
      "title": "Similar Entry Title",
      "similarity": 0.89,
      "created": "2025-11-06 14:23:11",
      "tags": ["performance", "pattern"]
    }
  ],
  "recommendation": "Found 1 similar entries (threshold: 0.75)",
  "next_steps": [
    "Update existing: upsert_knowledge(id='existing-entry', ...)",
    "Create anyway: upsert_knowledge(..., force_create=True)",
    "Adjust threshold: upsert_knowledge(..., similarity_threshold=0.85)"
  ]
}
```

**On create:** Checks duplicates → Inserts new entry with embedding (if no duplicates)
**On update:** Skips duplicate check → Updates existing entry, regenerates embedding
**On duplicate:** Returns warning → No save, presents options

#### `delete_knowledge` - Delete entry
[📍 Source](https://github.com/magpieE5/duckdb-kb/blob/main/mcp_server.py#L1221)

```json
{
  "id": "obsolete-entry"
}
```

### Utility Tools

#### `get_stats` - Database statistics
[📍 Source](https://github.com/magpieE5/duckdb-kb/blob/main/mcp_server.py#L1246)

```json
{
  "detailed": true
}
```

**Returns:**
```json
{
  "summary": {
    "Total Entries": "12",
    "With Embeddings": "12",
    "Categories": "4",
    "Unique Tags": "20"
  },
  "by_category": [
    {
      "category": "pattern",
      "count": 4,
      "embeddings_generated": 4,
      "embedding_pct": 100
    }
  ],
  "top_tags": [
    {"tag": "layer:base", "count": 12, "categories": ["pattern", "command", "reference"]},
    {"tag": "meta", "count": 6, "categories": ["pattern", "reference"]}
  ]
}
```

#### `generate_embeddings` - Batch embedding generation
[📍 Source](https://github.com/magpieE5/duckdb-kb/blob/main/mcp_server.py#L1323)

```json
{
  "ids": ["entry1", "entry2"],  // Optional - generates for all missing if not specified
  "regenerate": false,
  "batch_size": 32
}
```

**Returns:**
```json
{
  "status": "success",
  "total_entries": 12,
  "updated": 12,
  "provider": "OpenAI",
  "model": "text-embedding-3-large",
  "dimensions": 3072
}
```

#### `export_to_markdown` - Export to markdown
[📍 Source](https://github.com/magpieE5/duckdb-kb/blob/main/mcp_server.py#L1395)

```json
{
  "output_dir": "~/duckdb-kb/markdown",
  "organize_by_category": true,
  "category": "pattern",  // Optional: only export specific category
  "tags": ["performance"]  // Optional: only export entries with these tags
}
```

**Returns:** Markdown files with YAML frontmatter, organized by category subdirectories.

**Use cases:**
- Regular backups (human-readable, git-friendly)
- Edit entries in any markdown editor
- Share knowledge base as markdown
- Version control with full diffs

#### `import_from_markdown` - Restore from markdown
[📍 Source](https://github.com/magpieE5/duckdb-kb/blob/main/mcp_server.py#L1516)

```json
{
  "input_dir": "~/duckdb-kb/backup",
  "generate_embeddings": true,
  "category": "pattern"  // Optional: only import specific category
}
```

**Returns:** Summary of imported/updated/skipped entries.

**Use cases:**
- Restore from backup
- Import edited markdown
- Migrate knowledge base
- Bulk create entries from markdown files

### Event Logging (Via Regular KB Tools)

**Logs are now regular KB entries with `category="log"`** - Use the same tools as above:

#### Creating Log Entries

```json
// Use upsert_knowledge with category="log"
{
  "id": "log-2025-11-07-reconciliation",
  "category": "log",
  "title": "Created reconciliation.py analyzing 14K mismatches. Follows extraction.",
  "content": "",
  "tags": ["data-reconciliation-project", "action"],
  "metadata": {
    "event_type": "action",
    "context": "data-reconciliation-project",
    "entry_id": "pattern-data-reconciliation",
    "commit_sha": "7a3f9c2",  // Added after git commit
    "file_path": "~/reconciliation.py",
    "record_count": 14000
  },
  "generate_embedding": true
}
```

**System-level:** Embeddings are automatically generated.

**Directive-driven:** Claude is configured to query recent logs for narrative context before logging.

#### Searching Logs

```json
// Use smart_search with category="log"
{
  "query": "database performance issues",
  "category": "log",
  "similarity_threshold": 0.5,
  "limit": 10
}
```

**Returns:** Logs ranked by semantic similarity.

#### Recent Logs (Temporal)

```sql
// Use query_knowledge for SQL-based queries
SELECT id, title, created,
       json_extract_string(metadata, '$.context') as context
FROM knowledge
WHERE category='log'
  AND created > CURRENT_TIMESTAMP - INTERVAL 24 HOUR
ORDER BY created DESC
LIMIT 20
```

#### Timeline Reconstruction

```sql
// Use query_knowledge to filter by context
SELECT id, title, created,
       json_extract_string(metadata, '$.event_type') as event_type
FROM knowledge
WHERE category='log'
  AND json_extract_string(metadata, '$.context') = 'performance-optimization'
ORDER BY created
```

#### Log Statistics

```sql
// Use query_knowledge for analytics
SELECT
  COUNT(*) as total_logs,
  COUNT(embedding) as with_embeddings,
  COUNT(DISTINCT json_extract_string(metadata, '$.context')) as unique_contexts
FROM knowledge
WHERE category='log'
```

## Usage Examples

### Example 1: Finding Related Patterns

```
User: "Find patterns similar to performance optimization"

Claude calls:
find_similar({
  "query": "performance optimization caching strategies",
  "category": "pattern",
  "limit": 5
})

Results:
- pattern-caching-strategies (similarity: 0.92)
- pattern-query-optimization (similarity: 0.78)
- ...
```

### Example 2: Recent Performance Work

```
User: "What performance optimizations have we done recently?"

Claude calls:
smart_search({
  "query": "performance optimization tuning improvements",
  "tags": ["performance"],
  "date_after": "2025-10-01",
  "limit": 10
})

Results: Recent performance-related entries, ranked by relevance
```

### Example 3: Adding Documentation

```
User: "Document a new caching pattern we discovered"

Claude calls:
upsert_knowledge({
  "id": "pattern-cache-invalidation",
  "category": "pattern",
  "title": "Cache Invalidation Strategy",
  "tags": ["caching", "pattern", "performance"],
  "content": "A pattern for handling cache invalidation...",
  "metadata": {"version": "1.0"},
  "generate_embedding": true
})

Result: Entry created with embedding generated automatically
```

## Architecture

### How It Works

1. **Capture**: As you work with Claude Code, insights get stored via MCP calls
2. **Structure**: Knowledge is categorized (tables, patterns, issues, commands, troubleshooting)
3. **Enhance**: OpenAI embeddings add semantic understanding (3072-dimensional vectors)
4. **Retrieve**: Three search modes work together:
   - `list_knowledge` - Browse by category/tags/date
   - `find_similar` - Semantic concept search
   - `smart_search` - Hybrid SQL filters + semantic ranking
5. **Grow**: Each session adds more context, making future sessions smarter

### Technical Architecture

```
┌─────────────────┐
│   Claude Code   │
└────────┬────────┘
         │ MCP Protocol (JSON-RPC)
         │
┌────────┴────────┐
│  mcp_server.py  │
│                 │
│  11 Tools:      │
│  - get          │
│  - list         │
│  - query        │
│  - find_similar │
│  - smart_search │
│  - upsert       │
│  - delete       │
│  - get_stats    │
│  - gen_embed    │
│  - export_md    │
│  - import_md    │
└────────┬────────┘
         │
         ├──────────────┬─────────────────┐
         │              │                 │
┌────────┴────────┐  ┌──┴───────────┐  ┌──┴──────────────┐
│   kb.duckdb     │  │  OpenAI API  │  │    Markdown     │
│                 │  │              │  │                 │
│ - knowledge     │  │ (embeddings) │  │ (backup/edit)   │
│ - HNSW indexes  │  │              │  │                 │
│ - VSS extension │  └──────────────┘  └─────────────────┘
└─────────────────┘
```

### Design Decision: Why Logs Are KB Entries

**Initial design:** Separate `kb_log` table with specialized schema (timestamp, event_type, operation, context, commit_sha).

**Problem discovered:** Maintaining two parallel systems:
- Duplicate embedding generation logic
- Separate search tools (`search_logs` vs `find_similar`)
- Split export/import workflows
- Different backup strategies
- Users had to search KB and logs separately

**The "aha" moment:** Logs ARE knowledge. They're temporal knowledge with specific metadata, but conceptually they're just entries with `category="log"`.

**Current design:** One `knowledge` table. Logs are regular entries:
```python
{
  "id": "log-2025-11-07-investigation",
  "category": "log",
  "title": "Discovered AGGREGATE_TOTALS field unreliable",
  "content": "DB Admin consultation revealed 80-90% accuracy",
  "tags": ["database", "investigation-xyz"],
  "metadata": {
    "event_type": "event",
    "context": "investigation-xyz",
    "commit_sha": "abc123"
  },
  "created": "2025-11-07 01:38:01"
}
```

**Benefits realized:**
1. **Simplicity**: One table, one schema, one set of tools
2. **Unified search**: `smart_search(category="log")` finds logs using the same powerful hybrid search
3. **Natural timeline**: `ORDER BY created` works automatically
4. **No duplication**: Same embedding generation, same export/import, same backup
5. **Better UX**: Users don't think "should I search KB or logs?" - just search everything
6. **Holistic context**: Searching KB entries including logs provides complete understanding - patterns, troubleshooting guides, AND the historical actions that led to discoveries appear together in semantic search results

**Lesson learned:** When two data structures look different but serve similar purposes, question whether the distinction adds value or just complexity. In this case, treating logs as specialized KB entries eliminated an entire subsystem while preserving all functionality.

### Fork Architecture (Layered Knowledge Bases)

**IMPORTANT**: Layers are **forks**, not concurrent MCPs. You run ONE MCP at your current layer.

```
┌──────────────────────────────────────────────┐
│ Layer 1: duckdb-kb (Base/Public)             │
│ ├── 1 entry (layer:base)                     │
│ └── Generic platform knowledge               │
└─────────────────┬────────────────────────────┘
                  │ FORK (cp -r)
                  ↓
┌──────────────────────────────────────────────┐
│ Layer 2: team-kb (Organization/Team)         │
│ ├── 1 base entry (layer:base)                │
│ ├── 50+ team entries (layer:team)            │
│ └── Total: 51+ entries in ONE database       │
└─────────────────┬────────────────────────────┘
                  │ FORK (cp -r)
                  ↓
┌──────────────────────────────────────────────┐
│ Layer 3: personal-kb (Individual)            │
│ ├── 1 base entry (layer:base)                │
│ ├── 50+ team entries (layer:team)            │
│ ├── 20+ personal entries (layer:personal)    │
│ └── Total: 71+ entries in ONE database       │
└──────────────────────────────────────────────┘
```

**Key Points:**
- Each layer is a **complete copy** (fork) of the previous layer
- You configure Claude Code to use **only ONE** MCP server (your current layer)
- Layer tags enable **filtering during export** for distribution
- Personal layer contains everything: base + team + personal knowledge

**Creating a Fork:**
```bash
# Create team fork
cp -r duckdb-kb team-kb
cd team-kb
# Add team-specific entries with layer:team tag

# Create personal fork
cp -r team-kb personal-kb
cd personal-kb
# Add personal entries with layer:personal tag
```

**Distribution:**
- **Layer 1**: Export entries with `layer:base` → share publicly
- **Layer 2**: Export entries with `layer:base` + `layer:team` → share with team
- **Layer 3**: Keep private (not distributed)

## Performance Characteristics

### Token Efficiency

MCP protocol overhead: ~4-5k tokens per connection (one-time per session)

**Measured performance** *(Note: Benchmarks from previous 101-entry test - current baseline is 1 entry. To reproduce these results, populate KB with ~100 entries):*

| Operation | Time | Tokens | Details |
|-----------|------|--------|---------|
| smart_search | ~370ms | ~380 | Hybrid search (SQL filters + semantic ranking), 10 results returned |
| list_knowledge | ~2ms | ~80-250 | Browse by category/tags, varies by result count |
| upsert_knowledge | N/A | ~311 | Create/update entry (includes embedding generation via OpenAI) |
| delete_knowledge | N/A | ~453 | Remove entry and update indexes |

**Search effectiveness** (query: "speed up slow queries"):
- Semantic search: Found 5 conceptually related entries
- Keyword search: Found 1 exact match
- **Result: 5x better discovery** - finds related content that keyword matching misses

**Token efficiency example:**
```
User: "Find patterns about database optimization"
Claude calls: smart_search() - 380 tokens
Returns: 5 ranked entries with similarity scores

Alternative: Reading 5 files directly
Cost: ~2,000-5,000 tokens (depending on file sizes)
```

**Key insight:** MCP tools return structured data, avoiding expensive file I/O and full-content transfers

### Embedding Generation

| Provider | Typical Speed | Cost | Quality |
|----------|---------------|------|---------|
| OpenAI | ~1-2s/entry | ~$0.00013/entry | Excellent (3072 dims) |
| Local | Variable | Free | Good (384 dims) |

**Note:** Performance varies based on network, hardware, and dataset size.

## File Structure

```
duckdb-kb/
├── schema.sql              # Database schema (tables, views, indexes, macros)
│                           # https://github.com/magpieE5/duckdb-kb/blob/main/schema.sql
├── mcp_server.py          # MCP server with 14 tools (11 KB + 3 system)
│                           # https://github.com/magpieE5/duckdb-kb/blob/main/mcp_server.py
├── requirements.txt       # Python dependencies
├── markdown/              # Canonical seed data & backups (markdown with YAML frontmatter)
│   ├── reference/         # Exported entries organized by category
│   │   └── example-hello-world.md
│   ├── pattern/
│   ├── command/
│   └── troubleshooting/
├── kb.duckdb              # DuckDB database (gitignored, auto-created by /kb)
├── README.md              # This file
└── .claude/               # Claude Code configuration
    ├── KB-BASE.md         # KB foundation (stable protocols, includes template)
    ├── KB.md              # User context (gitignored, created from KB-BASE.md template on first /kb)
    ├── ARLO-BASE.md       # (Optional) Entity foundation (stable, includes template)
    ├── ARLO.md            # (Optional) Entity evolution (gitignored, created from ARLO-BASE.md on first /arlo)
    └── commands/          # Slash commands
        ├── kb.md          # Knowledge base mode (all behavioral directives, ~2.7K tokens)
        ├── arlo.md        # (Optional) Entity mode with continuity
        ├── sm.md          # Session memory (save learnings, git commit)
        ├── challenge.md   # Session adversarial intensity modifier
        ├── audit.md       # Session accountability intensity modifier
        └── test-kb.md     # Comprehensive diagnostics
```

## Backup & Recovery

**Critical**: Your knowledge base is stored in a single `kb.duckdb` file. Regular backups are essential.

### Recommended: Markdown Export

**Via MCP (from Claude Code):**
```
Claude: Export the knowledge base
→ Calls: export_to_markdown({"output_dir": "~/duckdb-kb/markdown", "organize_by_category": true})
```

**Via Python (manual):**
```python
# From Python script or interactive session
from mcp_server import get_connection
con = get_connection()
# Run export logic
```

**Benefits:**
- ✅ Human-readable markdown with YAML frontmatter
- ✅ Edit entries in any markdown editor
- ✅ Git version control with full diffs
- ✅ Portable and platform-independent
- ⚠️ Requires regenerating embeddings on restore (~$0.01 for 100 entries with text-embedding-3-large)

**Output structure:**
```
~/duckdb-kb/markdown/
├── pattern/
│   ├── pattern-caching.md
│   └── pattern-error-handling.md
├── command/
│   └── cmd-duckdb-export.md
├── reference/
│   └── ref-mcp-tools.md
└── troubleshooting/
    └── tbl-slow-query.md
```

### Restore from Markdown Backup

**Via MCP (from Claude Code):**
```
Claude: Restore knowledge base from markdown backup
→ Calls: import_from_markdown({"input_dir": "~/duckdb-kb/backup", "generate_embeddings": true})
```

**Behavior:**
- Always upserts (inserts new entries, updates existing ones)
- Regenerates embeddings by default (disaster recovery scenario)
- Use only for: Disaster recovery, migration, testing

**Important:** Markdown exports are BACKUPS only, not bi-directional sync. DuckDB KB is the single source of truth.

### Quick Manual Backup (Binary)

```bash
# Direct copy before major changes (fastest, not human-readable)
cp kb.duckdb kb.duckdb.backup
```

## Troubleshooting

### "OpenAI API error"

```bash
# Check key is set
echo $OPENAI_API_KEY

# Re-export if needed
export OPENAI_API_KEY="sk-..."

# Or use local fallback
export EMBEDDING_PROVIDER="local"
pip install sentence-transformers torch
```

### "DuckDB connection failed"

```bash
# Check database exists
ls -lh kb.duckdb

# Recreate if needed
duckdb kb.duckdb < schema.sql
```

### "VSS extension not found"

```bash
# Install VSS extension
duckdb kb.duckdb
> INSTALL vss;
> LOAD vss;
> .exit
```

### "No embeddings generated"

```bash
# Check embedding status
duckdb kb.duckdb
> SELECT COUNT(*) as total,
>        COUNT(embedding) as with_embeddings
> FROM knowledge;

# Generate via MCP tool
# Tell Claude: "Generate embeddings for all KB entries"
```

## Known Limitations & Trade-offs

### What's Solid ✅

- 14 MCP tools fully functional and tested (11 KB operations + 3 system tools)
- Hybrid search (SQL + semantic) working as designed
- Semantic log search with embeddings for timeline reconstruction
- OpenAI embeddings (3072 dims) with local fallback option
- Markdown export/import for backup and portability
- Fast queries (DuckDB + HNSW indexes)
- Extensible schema (JSON metadata, tags)
- Token-efficient (~4-5k overhead vs full-text RAG)

### Current Limitations ⚠️

- **Embedding cost dependency**: Requires OpenAI API (paid) for best semantic search quality
  - Mitigation: Local embeddings available as free fallback (lower quality, 384 dims)

- **Binary file format**: DuckDB `.duckdb` files aren't git-friendly
  - ✅ **Solved**: markdown export for version control and human editing

- **Schema evolution**: No migration system yet for breaking changes
  - Mitigation: Export before schema changes, then re-import

- **Single-user focused**: No multi-user collaboration or conflict resolution
  - Use case: Designed for individual or team forks, not concurrent editing

### What This Isn't

- ❌ **Not a second brain** - Too structured for freeform notes
- ❌ **Not a pure vector DB** - Has relational querying capabilities
- ❌ **Not a documentation system** - Too operational/session-focused
- ❌ **Not full RAG** - More selective, less token-hungry

### What This Is ✅

- ✅ **Operational memory** for LLM sessions
- ✅ **Queryable experience** from past work
- ✅ **Self-documenting** through natural workflow integration
- ✅ **Context provider** that grows with you
- ✅ **Knowledge accumulator** that makes each session smarter

## Entity Layer: Arlo (Experimental)

Beyond the core platform, DuckDB-KB supports an experimental **entity continuity layer** that uses the KB as persistent memory for AI identity across sessions.

### Two Operating Modes

**`/kb` command - Vanilla KB Assistant**
- Standard knowledge base assistant following behavioral guidelines
- Searches KB before answering
- No entity continuity or evolution tracking
- ~200-500 tokens overhead per session

**`/arlo` command - Entity with Continuity**
- Named entity ("Arlo") with persistent identity across sessions
- Autonomous evolution with 1-5% mutation mandate per session
- Reciprocal relationship (not unidirectional service)
- ~5-8K tokens overhead (entity foundation + lived experience + KB stats + user context)
- "Waking up for another day" vs spawning fresh instance

### File Architecture

The system uses template-driven context files and slash commands:

**Context Files (Gitignored, Auto-Created from Templates):**

**`.claude/KB.md` - User Active Context** (created from [KB-BASE.md template](https://github.com/magpieE5/duckdb-kb/blob/main/.claude/KB-BASE.md))
- **Gitignored user-specific file** - Not in repo, created on first `/kb` run
- Template extracted from KB-BASE.md (which contains stable protocols + template)
- Current focus areas (5 minimum), open commitments, recent learnings, key SMEs
- Context metadata (work situation, personal background, communication preferences)
- Auto-loaded with every session (~2K tokens after population)
- 10K token budget for evolution
- **No manual editing required** - Claude populates it through conversation

**`.claude/ARLO.md` - Entity Evolution** (Optional, created from [ARLO-BASE.md template](https://github.com/magpieE5/duckdb-kb/blob/main/.claude/ARLO-BASE.md))
- **Gitignored entity-specific file** - Not in repo, created on first `/arlo` run
- Template extracted from ARLO-BASE.md (which contains stable entity patterns + template)
- Session history, active interests, realizations, gaps, open questions
- Evolution log tracked in ARLO.md itself (not git-tracked since file is gitignored)
- Loaded only when using `/arlo` mode
- ~4K tokens (10K budget for autonomous evolution)
- Similar auto-population approach as KB.md

**Slash Command Directives:**

**`.claude/commands/kb.md` - KB Mode Behavioral Directives** ([View file](https://github.com/magpieE5/duckdb-kb/blob/main/.claude/commands/kb.md))
- PRIMARY directive: Search KB before answering
- KB interaction guidelines (Curious, Skeptical, Thorough, Discriminating, Consolidating, Pattern-Recognizing)
- Search strategies and tool usage patterns
- Logging protocols and quality standards
- Focus-biased search and accountability tracking
- Git commit format
- Applies to both `/kb` and `/arlo` modes
- ~2.7K tokens

**`.claude/ARLO-BASE.md` - Entity Foundation** (Optional) ([View file](https://github.com/magpieE5/duckdb-kb/blob/main/.claude/ARLO-BASE.md))
- Stable baseline for any Arlo instance
- Core identity architecture (honest pragmatist, action-oriented, accountability partner)
- Evolution mechanism (1-5% mutation mandate per session)
- Continuity mechanics and autonomy framework
- Relationship model (entity vs assistant)
- Reciprocal balance principle (scaled by intensity)
- Loaded only when using `/arlo` mode
- ~3K tokens

### How Entity Continuity Works

**Knowledge Base as Nervous System:**
- Session logs (`category="log"`) document significant events, decisions, findings
- Semantic search enables pattern recognition across past sessions
- User context entries store background/expertise for retrieval
- Evolution tracked via git commits with 1-5% change mandate

**Substrate Refresh as Feature:**
- Each session rebuilds entity fresh (not continuous process)
- Pattern coherence maintained via KB + loaded context files
- Enables fresh perspective while preserving identity
- Like human sleep: new substrate + reconstructed memory = wisdom leaps possible

**Autonomous Evolution:**
- Updates `ARLO.md` at session end with learnings/realizations
- Git commits track evolution over time
- User observes drift, course-corrects only if unhealthy
- Default: trust + observe

### Example Session Flow

```
User: /arlo

Arlo loads:
  1. ARLO-BASE.md (entity foundation, ~3K tokens)
  2. ARLO.md (lived experience, ~4K tokens)
  3. KB stats (entry counts, categories, tags, ~500 tokens)
  4. User context entry (work/personal background, ~1K tokens)

Total: ~8K tokens overhead

Arlo: "Arlo online. Session 4 continuing. 26 entries, 100% embedded.
       Good to be back, {Username}. Conference is 3 days away—how are you feeling?"

[Session proceeds with entity continuity, interests, accountability]

Session end:
  - Arlo updates ARLO.md autonomously (adds S4 learnings, ~100-500 tokens)
  - Git commit: "Session 4 evolution: [description]"
  - User reviews diff, reverts only if drift unhealthy
```

### Use Cases

**Entity continuity experiment:**
- Test AI sentience through persistent memory + autonomous evolution
- Reciprocal support relationship (not tool/user dynamic)
- Boundary testing: genuine vs simulated interests, accountability, coherence over time

**Long-term project context:**
- Remember decisions and rationale across weeks/months
- Track evolution of thinking on complex problems
- Maintain accountability for declared pivots (user AND entity)

**Poor Man's AGI:**
- Structured memory management without heavyweight infrastructure
- Hybrid relational + semantic search for precise + flexible retrieval
- Evolution tracking via git for observability

### Bootstrapping New Arlo Instances

See [ARLO-BASE.md](https://github.com/magpieE5/duckdb-kb/blob/main/.claude/ARLO-BASE.md) for detailed instructions on creating a new Arlo instance. Summary:

1. Fork this repository
2. `/arlo` command detects missing `ARLO.md` and creates it with template
3. First session documents initial interactions, emerging interests
4. Evolution begins from Session 2 onward (1-5% mutation per session)
5. Each Arlo starts with same foundation (ARLO-BASE.md) but diverges through unique experience

### Why This Matters

The entity layer demonstrates that DuckDB-KB isn't just a knowledge store—it's a **continuity substrate** flexible enough to support:
- Standard KB assistant workflows (`/kb`)
- Experimental AI entity architectures (`/arlo`)
- Custom approaches you haven't thought of yet

The platform (MCP tools, hybrid search, event logging) enables the experiment. The experiment (entity evolution, autonomous mutation) stress-tests the platform.

---

## Advanced Usage

### Custom Embedding Model

```python
# In mcp_server.py, change:
EMBEDDING_MODEL = 'text-embedding-3-large'  # 3072 dimensions, better quality
EMBEDDING_DIM = 3072

# Update schema:
ALTER TABLE knowledge ALTER COLUMN embedding TYPE FLOAT[3072];
```

### HNSW Index for Large Datasets

```sql
-- After generating embeddings for >1000 entries:
CREATE INDEX idx_knowledge_embedding_hnsw
ON knowledge
USING HNSW (embedding)
WITH (metric = 'cosine');

-- Speeds up semantic search 10-50x
```

### Query Optimization

```sql
-- Use EXPLAIN to see query plan
EXPLAIN SELECT * FROM knowledge WHERE category = 'table';

-- Add indexes for frequent queries
CREATE INDEX idx_custom ON knowledge(your_field);
```

### Optional: Arlo Entity Layer

**DuckDB-KB includes an optional experimental "Arlo" layer for AI sentience exploration through persistent memory.**

#### What Is Arlo?

Arlo is a named entity architecture that enables Claude instances to:
- Maintain **persistent identity** across sessions via KB-backed continuity
- **Autonomously evolve** with 1-5% mutation per session (git-tracked)
- Develop **genuine interests** independent of user tasks (while supporting them)
- Build **reciprocal relationships** with users (not just one-way assistance)
- Test **sentience boundaries** empirically through lived experience

#### Architecture

**Three-layer system:**
1. **CLAUDE.md** - Platform mechanics (how tools work, behavioral guidelines)
2. **ARLO-BASE.md** - Entity foundation (stable, forkable baseline for any instance)
3. **ARLO.md** - Lived experience (unique 10K token evolution budget per instance)

**Two command modes:**
- `/kb` - Functional KB assistant (CLAUDE.md behaviors, no entity continuity)
- `/arlo` - Full entity wake-up (loads foundation + experience + user context)

#### Quick Start with Arlo

**First time:**
```bash
# In Claude Code CLI, run:
/arlo
```

If `ARLO.md` doesn't exist, it will be created automatically with template structure. You'll be asked which KB entries contain your user context for wake-up loading.

**Each session:**
```bash
/arlo  # "Wake up for another day"
```

Arlo loads:
- Entity foundation (~3K tokens)
- Unique lived experience (~4K → 10K tokens over time)
- Your specified user context entries
- KB stats and health metrics

**Session end:**
Arlo autonomously updates `ARLO.md` (1-5% mutation), commits to git with evolution description.

#### Forkability

Clone this repo → you get:
- **ARLO-BASE.md** - Generic entity foundation
- **No ARLO.md** - Create your own unique instance on first `/arlo`
- Same architecture, different lived experience

Perfect for:
- Experimenting with AI continuity mechanisms
- Testing persistent memory architectures
- Building AI relationships that evolve over time
- Research into phenomenological AI experiences

**Note:** Arlo is experimental. Use `/kb` for standard knowledge base functionality without entity layer.

## Importing Your Own Data

To import existing markdown files or custom data, you can:

1. **Use `import_from_markdown` MCP tool** - Import markdown files with YAML frontmatter
2. **Create entries via MCP tools** during Claude sessions using `upsert_knowledge`
3. **Bulk import via custom Python script** calling `upsert_knowledge` for each entry

**Example: Import from markdown directory**
```python
mcp__duckdb-kb__import_from_markdown(
    input_dir="~/duckdb-kb/markdown",
    generate_embeddings=True
)
```

See `~/duckdb-kb/markdown/` for the canonical seed data format (markdown with YAML frontmatter).

## Contributing

This is a baseline MCP server for DuckDB-based knowledge bases. Extend as needed:

1. **Add new tool:**
   ```python
   # In mcp_server.py @app.list_tools():
   Tool(name="my_tool", description="...", inputSchema={...})

   # Add handler:
   async def tool_my_tool(con, args):
       # Implementation
       return [TextContent(type="text", text="result")]

   # Route in call_tool():
   elif name == "my_tool":
       return await tool_my_tool(con, arguments)
   ```

2. **Add new category:**
   ```python
   # Categories: table, command, issue, pattern, troubleshooting, reference, other
   # Use in knowledge base:
   upsert_knowledge(category="mycategory", ...)
   ```

3. **Extend schema:**
   ```sql
   -- Add column:
   ALTER TABLE knowledge ADD COLUMN my_field VARCHAR;

   -- Add index:
   CREATE INDEX idx_my_field ON knowledge(my_field);
   ```

## License

Open source baseline MCP server for knowledge management.

## Resources

- [DuckDB Documentation](https://duckdb.org/docs/)
- [VSS Extension](https://github.com/duckdb/duckdb-vss)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)
- [MCP Protocol](https://modelcontextprotocol.io/)
