# test-kb: DuckDB KB MCP Comprehensive Diagnostics

Run a full tear-down and functionality test of the duckdb-kb MCP server.

**Recommended:** Use `run_diagnostics` MCP tool for automated testing:
```python
run_diagnostics({"suite": "full"})  # Comprehensive test suite
run_diagnostics({"suite": "quick"})  # Fast smoke tests
```

**Manual testing below** provides detailed step-by-step validation when needed.

**Purpose:** Simulate new user experience after cloning repo and running setup.

---

## ⚠️ IMPORTANT NOTES

1. **Backup is SAFETY ONLY** - Not used for restoration
2. **Markdown is canonical seed format** - Restore uses 2-step process: initialize_database MCP tool → import_from_markdown()
3. **Export/Import round-trip test is REQUIRED** - Tests disaster recovery workflow
4. **This is a GLOBAL command** - Lives in ~/.claude/commands/ and works across all KB-enabled projects

---

## 🧪 Testing Protocol

**CRITICAL: Always use MCP tools for database operations:**

✅ **DO:**
- Use `mcp__duckdb-kb__upsert_knowledge()` to create/update entries
- Use `mcp__duckdb-kb__delete_knowledge()` to remove entries
- Use `mcp__duckdb-kb__query_knowledge()` for custom SQL queries

❌ **DO NOT:**
- Use direct Python scripts with `duckdb.connect()` and INSERT/UPDATE/DELETE
- Exception: Read-only queries for debugging are OK if VSS loaded first

**Why:** MCP tools automatically load the VSS extension required for HNSW indexes.

**JSON Metadata Queries:**
- ✅ Use `json_extract_string(metadata, '$.key')` for reliability
- ❌ Avoid `metadata->>'key'` operator (fails with mixed metadata values)

**Export/Import Testing:**
- Export to `markdown-test/` for round-trip testing (not `markdown/`)
- This keeps `markdown/` canonical and prevents test data pollution
- Delete `markdown-test/` after testing

---

## Execution Steps

Use TodoWrite to track progress through ALL steps below.

### Step 0: Search KB for Supporting Context

**BEFORE starting tests, search KB for relevant information:**

```python
# Search for test-related patterns and troubleshooting
mcp__duckdb-kb__smart_search(
    query="test initialization troubleshooting regression",
    similarity_threshold=0.6,
    limit=5
)

# Search for any test-kb specific entries
mcp__duckdb-kb__smart_search(
    query="test-kb slash command",
    similarity_threshold=0.6,
    limit=3
)
```

**Review results** for:
- Known issues with initialization sequence
- Previous test failures and fixes
- Updated procedures or workarounds
- Deprecated flags or commands

If relevant entries found, incorporate their guidance into test execution.

---

### Step 1: Export Safety Backup
```python
mcp__duckdb-kb__export_to_markdown(output_dir="~/duckdb-kb/test-backup")
mcp__duckdb-kb__get_stats(detailed=true)
```
**Record:** Pre-test statistics (entries, embeddings, categories, tags)

---

### Step 2: Tear Down Database
```bash
rm -f ~/duckdb-kb/kb.duckdb
ls -la ~/duckdb-kb/ | grep kb.duckdb  # Verify deletion
```

---

### Step 3: Re-initialize from Markdown (Canonical 2-Step Process)

**Step 3a: Initialize empty database**
```python
mcp__duckdb-kb__initialize_database(force=True)
```
**Verify:** Tool returns success=true, vss_available=true, and stats showing empty tables

**Note:** This tests the `initialize_database` system tool (one of 3 new tools added for deterministic /kb and /sm workflows)

**Step 3b: Import from canonical markdown seed data**
```python
mcp__duckdb-kb__import_from_markdown(
    input_dir="~/duckdb-kb/markdown",
    generate_embeddings=True
)
```
**Verify:** Import completes, shows "Updated N entries"

**Step 3c: Verify stats**
```python
mcp__duckdb-kb__get_stats(detailed=True)
```
**Verify:** Stats match pre-test baseline (N entries, 100% embeddings, etc.)

---

### Step 4: Search Functionality Tests

Run ALL four search methods in parallel:

**A. smart_search()** - Hybrid SQL + semantic
```python
mcp__duckdb-kb__smart_search(
    query="knowledge base patterns",
    similarity_threshold=0.3,
    limit=3
)
```

**B. find_similar()** - Pure semantic
```python
mcp__duckdb-kb__find_similar(
    query="embedding generation troubleshooting",
    similarity_threshold=0.5,
    limit=5
)
```

**C. list_knowledge()** - Category filtering
```python
mcp__duckdb-kb__list_knowledge(
    category="pattern",
    limit=5
)
```

**D. query_knowledge()** - Custom SQL
```python
mcp__duckdb-kb__query_knowledge(
    sql="SELECT category, COUNT(*) as count FROM knowledge GROUP BY category ORDER BY count DESC"
)
```

**Success:** All return expected results, no errors

---

### Step 5: CRUD Operation Tests

**Create:**
```python
mcp__duckdb-kb__upsert_knowledge(
    id="test-entry-crud",
    category="pattern",
    title="Test CRUD Entry",
    content="Test content",
    tags=["test", "crud", "layer:base"],
    generate_embedding=True
)
```

**Read:**
```python
mcp__duckdb-kb__get_knowledge(id="test-entry-crud")
```
**Verify:** All fields match what was created

**Update:**
```python
mcp__duckdb-kb__upsert_knowledge(
    id="test-entry-crud",
    category="pattern",
    title="Test CRUD Entry (UPDATED)",
    content="Updated content",
    tags=["test", "crud", "updated", "layer:base"],
    generate_embedding=True
)
mcp__duckdb-kb__get_knowledge(id="test-entry-crud")
```
**Verify:** Title, content, tags changed; `updated` timestamp changed; `created` unchanged

**Delete:**
```python
mcp__duckdb-kb__delete_knowledge(id="test-entry-crud")
mcp__duckdb-kb__get_knowledge(id="test-entry-crud")
```
**Verify:** Returns "Entry not found"

---

### Step 5b: Automatic Duplicate Detection Tests

Test the automatic duplicate detection built into `upsert_knowledge`.

**Test 1: Automatic Detection Blocks Duplicate (Default Threshold 0.75)**
```python
# Create seed entry
mcp__duckdb-kb__upsert_knowledge(
    id="test-duplicate-detection",
    category="pattern",
    title="Database Performance Optimization",
    content="Techniques for optimizing database queries using indexes and query planning.",
    tags=["test", "database", "performance", "layer:base"],
    generate_embedding=True
)

# Try to create similar entry (should be blocked automatically)
mcp__duckdb-kb__upsert_knowledge(
    id="test-duplicate-similar",
    category="pattern",
    title="Database Query Performance Tuning",
    content="Strategies for improving database performance through index optimization and query planning techniques.",
    tags=["test", "database", "optimization", "layer:base"],
    generate_embedding=True
    # check_duplicates=True (default)
    # similarity_threshold=0.75 (default)
)
```
**Verify:**
- ✅ Returns `"status": "duplicate_check"`
- ✅ `"saved": false` (entry NOT created)
- ✅ `"similar_entries"` contains test-duplicate-detection with similarity ≥ 0.75
- ✅ `"next_steps"` includes 4 options:
  - Update existing entry
  - Create anyway (force_create=True)
  - Stricter match (similarity_threshold=0.85)
  - Cast wider net (smart_search with threshold=0.55)

**Test 2: Force Create Bypasses Check**
```python
# Force create despite duplicate warning
mcp__duckdb-kb__upsert_knowledge(
    id="test-duplicate-similar",
    category="pattern",
    title="Database Query Performance Tuning",
    content="Strategies for improving database performance through index optimization.",
    tags=["test", "database", "optimization", "layer:base"],
    generate_embedding=True,
    force_create=True  # Bypass duplicate check
)
```
**Verify:**
- ✅ Returns `"status": "success"`
- ✅ `"saved": true` (entry created despite similarity)
- ✅ Entry exists in database

**Test 3: Update Existing Entry Skips Check**
```python
# Update the first entry (should skip duplicate check)
mcp__duckdb-kb__upsert_knowledge(
    id="test-duplicate-detection",  # Existing ID
    category="pattern",
    title="Database Performance Optimization (Updated)",
    content="Updated content with more details...",
    tags=["test", "database", "performance", "updated", "layer:base"],
    generate_embedding=True
)
```
**Verify:**
- ✅ Returns `"status": "success"` (no duplicate check ran)
- ✅ Entry updated successfully
- ✅ `updated` timestamp changed

**Test 4: Cast Wider Net Workflow (No Automatic Hits)**
```python
# Scenario: Automatic check finds nothing, but suspect duplicates exist

# Create entry with specific wording
mcp__duckdb-kb__upsert_knowledge(
    id="test-wider-net-seed",
    category="pattern",
    title="REST API Rate Limiting Strategies",
    content="Implementing token bucket and sliding window algorithms for API throttling.",
    tags=["test", "api", "rate-limiting", "layer:base"],
    generate_embedding=True
)

# Try creating with different wording (automatic check threshold 0.75)
# This should NOT trigger duplicate warning (different enough wording)
mcp__duckdb-kb__upsert_knowledge(
    id="test-wider-net-new",
    category="pattern",
    title="HTTP Request Throttling Patterns",
    content="Techniques for controlling request frequency in web services.",
    tags=["test", "http", "throttling", "layer:base"],
    generate_embedding=True
)
# Expected: Creates successfully (similarity likely 0.6-0.7, below 0.75)

# NOW: Cast wider net manually to find loosely related entries
mcp__duckdb-kb__smart_search(
    query="API throttling rate control request limiting",
    similarity_threshold=0.5,  # Lower threshold
    limit=10
)
```
**Verify:**
- ✅ First entry created (no warning)
- ✅ Second entry created (similarity below 0.75)
- ✅ Manual search at 0.5 finds BOTH entries (0.5-0.7 range)
- ✅ Demonstrates "wider net" catches entries automatic check missed

**Test 5: Custom Threshold (Stricter Matching)**
```python
# Try with stricter threshold (0.85)
mcp__duckdb-kb__upsert_knowledge(
    id="test-stricter-threshold",
    category="pattern",
    title="Database Performance Best Practices",
    content="Optimize database queries using proper indexing strategies.",
    tags=["test", "database", "performance", "layer:base"],
    generate_embedding=True,
    similarity_threshold=0.85  # Stricter than default 0.75
)
```
**Verify:**
- ✅ May or may not block (depends on similarity to test-duplicate-detection)
- ✅ If similarity is 0.75-0.84: Allows creation (below new threshold)
- ✅ If similarity is ≥0.85: Blocks with duplicate warning

**Success Criteria:**
- ✅ Automatic detection blocks duplicates (≥0.75 similarity)
- ✅ Response includes `similar_entries` and `next_steps`
- ✅ `force_create=True` bypasses check
- ✅ Updating existing entry skips check (no wasted API calls)
- ✅ "Cast wider net" workflow finds entries automatic check missed
- ✅ Custom `similarity_threshold` parameter works

---

### Step 6: Embedding Tests

**Create entry without embedding:**
```python
mcp__duckdb-kb__upsert_knowledge(
    id="test-embedding",
    category="pattern",
    title="Test Embedding",
    content="Embedding test",
    tags=["test", "embedding-test", "layer:base"],
    generate_embedding=False
)
mcp__duckdb-kb__get_knowledge(id="test-embedding")
```
**Verify:** `has_embedding: false`

**Generate embeddings:**
```python
mcp__duckdb-kb__generate_embeddings(regenerate=False)
mcp__duckdb-kb__get_knowledge(id="test-embedding")
```
**Verify:** `has_embedding: true`, `updated` timestamp changed

---

### Step 6b: Log Functionality Tests

Test logging via regular KB entries with category="log".

**Create test logs as KB entries (using MCP tools):**
```python
# Log 1: Action
mcp__duckdb-kb__upsert_knowledge(
    id="log-2025-test-action",
    category="log",
    title="Created test file analyzing performance metrics",
    content="",
    tags=["test-log-analytics", "action"],
    metadata={
        "event_type": "action",
        "context": "test-log-analytics",
        "file_path": "test.py",
        "lines": 150
    },
    generate_embedding=True
)

# Log 2: Event
mcp__duckdb-kb__upsert_knowledge(
    id="log-2025-test-event",
    category="log",
    title="Discussed performance bottleneck with senior engineer; identified N+1 query issue",
    content="",
    tags=["test-log-analytics", "event"],
    metadata={
        "event_type": "event",
        "context": "test-log-analytics"
    },
    generate_embedding=True
)

# Log 3: KB operation with commit SHA
mcp__duckdb-kb__upsert_knowledge(
    id="log-2025-test-commit",
    category="log",
    title="Documented N+1 query pattern as test-log-pattern",
    content="",
    tags=["test-log-analytics", "kb-operation"],
    metadata={
        "event_type": "kb_upsert",
        "context": "test-log-analytics",
        "entry_id": "test-log-pattern",
        "commit_sha": "abc12345"  # Simulated commit SHA
    },
    generate_embedding=True
)
```
**Verify:** All 3 logs created with embeddings

**Test log search (semantic):**
```python
mcp__duckdb-kb__smart_search(
    query="performance optimization database queries",
    category="log",
    similarity_threshold=0.3,
    limit=5
)
```
**Verify:** Finds logs semantically (e.g., "N+1 query" without exact keyword match)

**Test log timeline (temporal):**
```python
# Use json_extract_string for JSON metadata queries (DuckDB best practice)
mcp__duckdb-kb__query_knowledge(
    sql="SELECT id, title, created FROM knowledge WHERE category='log' ORDER BY created"
)
```
**Verify:** Returns 3+ logs in chronological order (may include existing logs)

**Test log stats:**
```python
mcp__duckdb-kb__query_knowledge(
    sql="SELECT COUNT(*) as total_logs, COUNT(embedding) as with_embeddings FROM knowledge WHERE category='log'"
)
```
**Verify:** Returns accurate counts

**Test commit SHA retrieval (using json_extract_string):**
```python
# Note: Use json_extract_string for reliability with mixed metadata values
mcp__duckdb-kb__query_knowledge(
    sql="SELECT id, title, json_extract_string(metadata, '$.commit_sha') as commit_sha FROM knowledge WHERE category='log' AND json_extract_string(metadata, '$.commit_sha') IS NOT NULL"
)
```
**Verify:** Log 3 has commit SHA = "abc12345"

**Success Criteria:**
- ✅ Log entries created as regular KB entries with category="log"
- ✅ Embeddings generated automatically
- ✅ Semantic search finds logs via smart_search(category="log")
- ✅ Timeline reconstruction via SQL ORDER BY created
- ✅ Commit SHA can be added/updated via metadata
- ✅ JSON metadata queries work using json_extract_string()
- ✅ Logs integrated with regular KB search (holistic context)

---

### Step 6c: System Tools Tests

Test the 3 system tools supporting deterministic /kb and /sm workflows.

**Note:** `initialize_database` already tested in Step 3a.

**Test 1: git_commit_and_get_sha**
```python
# Create test entry to commit
mcp__duckdb-kb__upsert_knowledge(
    id="test-git-commit",
    category="pattern",
    title="Test Git Commit Tool",
    content="Testing git_commit_and_get_sha MCP tool",
    tags=["test", "git", "layer:base"],
    generate_embedding=False
)

# Test git commit with SHA retrieval
mcp__duckdb-kb__git_commit_and_get_sha(
    message="test: Verify git_commit_and_get_sha MCP tool\n\n🤖 Generated with [Claude Code](https://claude.com/claude-code)\n\nCo-Authored-By: Claude <noreply@anthropic.com>"
)
```
**Verify:**
- ✅ Returns `"success": true`
- ✅ Returns `"sha"` field with commit hash (40-char hex string)
- ✅ Returns `"message"` confirming commit created
- ✅ Can retrieve commit via `git log -1 --oneline`

**Test 2: get_kb_session_status**
```python
# Test session status retrieval
mcp__duckdb-kb__get_kb_session_status()
```
**Verify:**
- ✅ Returns `"database"` object with `"action"` field
  - Should be "check_empty" (database exists, has entries)
- ✅ Returns `"kb_md"` object with `"action"` field
  - Will be "ready" if USER.md exists, "setup_kb_md" if template
- ✅ Returns `"status"` object with:
  - `"focus_areas"` (list) - Parsed from USER.md if exists
  - `"commitments"` (object) - all/approaching/overdue from USER.md
- ✅ No errors, valid JSON structure

**Test 3: check_token_budgets**
```python
# Test token budget checking for 4 context entries (15K/5K/15K/5K budgets)
mcp__duckdb-kb__check_token_budgets(
    entry_ids=[
        "user-current-state",     # 15K budget
        "user-biographical",      # 5K budget
        "arlo-current-state",     # 15K budget
        "arlo-biographical"       # 5K budget
    ]
)
```
**Verify:**
- ✅ Returns `"overall_status"` ("ok" or "over_budget")
- ✅ Returns `"entries"` array with entry for each KB entry checked
- ✅ Each entry contains:
  - `"entry_id"` - KB entry ID
  - `"tokens"` - Token count (integer, using len(content) // 4)
  - `"budget"` - Budget limit (15K for current-state, 5K for biographical)
  - `"headroom"` - Tokens remaining before budget
  - `"status"` - "ok" or "over_budget"
  - `"needs_offload"` - Boolean (true if over budget)
- ✅ Returns `"timestamp"` - ISO timestamp of check
- ✅ Returns `"note"` - Reference to offloading protocol
- ✅ Handles missing entries gracefully (skip)
- ✅ Applies default budgets: 15K/5K/15K/5K

**Success Criteria:**
- ✅ `git_commit_and_get_sha` creates commit and returns SHA
- ✅ `get_kb_session_status` returns database/kb_md/status structure
- ✅ `check_token_budgets` checks 4 KB context entries
- ✅ Token measurement uses simple approximation (len // 4)
- ✅ Budget status correctly identifies ok/over_budget (no "warning" state)
- ✅ All 3 system tools functional and tested

---

### Step 6d: Token Budget Overflow & Offloading Tests (Rinsable)

Test budget overflow detection and offloading workflow using git commit/reset for cleanup.

**Setup: Create test commit point**
```bash
git add -A && git commit -m "test: Pre-budget-test checkpoint"
```

**Test 1: Detect Over-Budget Entry**
```python
# Create oversized entry (>15K tokens = ~60K chars for user-current-state)
dummy_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 1100  # ~61.6K chars ≈ 15.4K tokens

mcp__duckdb-kb__upsert_knowledge(
    id="user-current-state",
    category="context",
    title="USER - Current State (OVERSIZED TEST)",
    content=dummy_text,
    tags=["user", "current-state", "test"],
    generate_embedding=False
)

# Check budget (15K for user-current-state)
result = mcp__duckdb-kb__check_token_budgets(
    entry_ids=["user-current-state"]
)
```
**Verify:**
- ✅ Returns `"overall_status": "over_budget"`
- ✅ `"status": "over_budget"` for user-current-state
- ✅ `"needs_offload": true`
- ✅ `"budget": 15000` (15K default for user-current-state)
- ✅ Token count ≈ 15.4K

**Test 2: Offload to New KB Entry**
```python
# Simulate offloading oldest topic to new KB entry
mcp__duckdb-kb__upsert_knowledge(
    id="pattern-offloaded-topic-test",
    category="pattern",
    title="Offloaded Topic from user-current-state (Test)",
    content="[Oldest topic content extracted from user-current-state - simulated]",
    tags=["offload", "test", "layer:base"],
    generate_embedding=False
)

# Update user-current-state (remove offloaded content, now under budget)
reduced_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 900  # ~50.4K chars ≈ 12.6K tokens

mcp__duckdb-kb__upsert_knowledge(
    id="user-current-state",
    category="context",
    title="USER - Current State",
    content=reduced_text,
    tags=["user", "current-state"],
    generate_embedding=False
)

# Check budget again (15K for user-current-state)
result = mcp__duckdb-kb__check_token_budgets(
    entry_ids=["user-current-state"]
)
```
**Verify:**
- ✅ Returns `"overall_status": "ok"`
- ✅ `"status": "ok"` for user-current-state
- ✅ `"needs_offload": false`
- ✅ `"budget": 15000` (15K default)
- ✅ New KB entry "pattern-offloaded-topic-test" exists
- ✅ user-current-state now under 15K budget

**Test 3: Offload with Duplicate Detection**
```python
# Create another oversized entry
mcp__duckdb-kb__upsert_knowledge(
    id="arlo-current-state",
    category="context",
    title="ARLO - Current State (OVERSIZED TEST)",
    content=dummy_text,  # Reuse from Test 1
    tags=["arlo", "current-state", "test"],
    generate_embedding=False
)

# Try to offload topic but check for duplicates first
# Simulate smart_search for duplicates
mcp__duckdb-kb__smart_search(
    query="offloaded topic user current state",
    similarity_threshold=0.7,
    limit=5
)

# If duplicate found (pattern-offloaded-topic-test), update existing instead
mcp__duckdb-kb__upsert_knowledge(
    id="pattern-offloaded-topic-test",
    category="pattern",
    title="Offloaded Topics from Context Entries (Test)",
    content="[Combined content from user-current-state and arlo-current-state offloads]",
    tags=["offload", "test", "consolidated", "layer:base"],
    generate_embedding=False
)

# Reduce arlo-current-state
mcp__duckdb-kb__upsert_knowledge(
    id="arlo-current-state",
    category="context",
    title="ARLO - Current State",
    content=reduced_text,  # Reuse from Test 2
    tags=["arlo", "current-state"],
    generate_embedding=False
)
```
**Verify:**
- ✅ Duplicate detection workflow tested (smart_search before create)
- ✅ Existing entry updated instead of creating duplicate
- ✅ arlo-current-state now under 10K budget
- ✅ Demonstrates standard KB workflow integration

**Cleanup: Reset to test commit**
```bash
git reset --hard HEAD~1
```
**Verify:**
- ✅ All test changes reverted
- ✅ Database restored to pre-test state
- ✅ No test pollution in KB

**Success Criteria:**
- ✅ check_token_budgets correctly detects over-budget entries with 15K/5K budgets
- ✅ Offloading workflow creates new KB entries for extracted content
- ✅ Reduced context entries pass budget check after offload
- ✅ Duplicate detection integrated (smart_search before create)
- ✅ Rinsable test via git commit/reset
- ✅ No test data pollution after cleanup
- ✅ Default budgets applied: 15K/5K/15K/5K

---

### Step 7: Cleanup Test Entries

**IMPORTANT: Run cleanup BEFORE export/import to prevent test data pollution.**

Remove all test entries created during testing:
```python
# Query for test entries
mcp__duckdb-kb__query_knowledge(
    sql="SELECT id FROM knowledge WHERE id LIKE '%test%' OR tags::TEXT LIKE '%test%'"
)

# Delete each test entry found
mcp__duckdb-kb__delete_knowledge(id="test-embedding")
mcp__duckdb-kb__delete_knowledge(id="test-duplicate-detection")
mcp__duckdb-kb__delete_knowledge(id="test-duplicate-similar")
mcp__duckdb-kb__delete_knowledge(id="test-wider-net-seed")
mcp__duckdb-kb__delete_knowledge(id="test-wider-net-new")
mcp__duckdb-kb__delete_knowledge(id="test-stricter-threshold")
mcp__duckdb-kb__delete_knowledge(id="log-2025-test-action")
mcp__duckdb-kb__delete_knowledge(id="log-2025-test-event")
mcp__duckdb-kb__delete_knowledge(id="log-2025-test-commit")
mcp__duckdb-kb__delete_knowledge(id="test-git-commit")
```

**Verify cleanup complete:**
```python
mcp__duckdb-kb__get_stats(detailed=False)
```
**Success:** Stats match pre-test baseline (1 entry, 1 embedding, 1 category, 4 tags)

---

### Step 8: Export/Import Round-Trip Test

**Export to test directory (NOT canonical markdown/):**
```python
mcp__duckdb-kb__export_to_markdown(
    output_dir="~/duckdb-kb/markdown-test",
    organize_by_category=True
)
```
**Verify:** Check files created in `~/duckdb-kb/markdown-test/`

**Record pre-import stats:**
```python
mcp__duckdb-kb__get_stats(detailed=False)
```

**Delete database and reinitialize:**
```bash
rm -f ~/duckdb-kb/kb.duckdb
```
```python
mcp__duckdb-kb__initialize_database(force=False)
```

**Import from test directory:**
```python
mcp__duckdb-kb__import_from_markdown(
    input_dir="~/duckdb-kb/markdown-test",
    generate_embeddings=True
)
```

**Verify post-import stats:**
```python
mcp__duckdb-kb__get_stats(detailed=False)
```
**Success:** All stats match pre-import (entries, embeddings, categories, tags)

**Cleanup test directory:**
```bash
rm -rf ~/duckdb-kb/markdown-test
```

---

### Step 9: Verify Final Stats

**Verify database restored to seed baseline:**
```python
mcp__duckdb-kb__get_stats(detailed=False)
```
**Success:** 1 entry, 1 embedding (100%), 1 category, 4 tags

---

### Step 10: Token Cost Tracking & Test Report

**Track token usage from system warnings after each MCP call. Record actual counts:**

| Step | Operation | Token Cost |
|------|-----------|------------|
| 0 | smart_search (context) | {N} |
| 1 | export_to_markdown | {N} |
| 1 | get_stats | {N} |
| 3 | import_from_markdown | {N} |
| 3 | get_stats | {N} |
| 4A | smart_search | {N} |
| 4B | find_similar | {N} |
| 4C | list_knowledge | {N} |
| 4D | query_knowledge | {N} |
| 5 | upsert (create) | {N} |
| 5 | get_knowledge | {N} |
| 5 | upsert (update) | {N} |
| 5 | delete_knowledge | {N} |
| 5b | upsert (dup check) | {N} |
| 6 | generate_embeddings | {N} |
| 6b | log tests (upserts x3) | {N} |
| 6c | git_commit_and_get_sha | {N} |
| 6c | get_kb_session_status | {N} |
| 6c | check_token_budgets | {N} |
| 7 | delete (cleanup x10) | {N} each |
| 8 | export + import | {N} |

**Total test cost:** {N} tokens

**Report format:**

```markdown
# 🧪 Test Report - {DATE}

| Step | Status | Tokens |
|------|--------|--------|
| All steps | ✅/❌ | {total} |

**Top 3 costs:** {op} ({N}), {op} ({N}), {op} ({N})

## Stats Comparison

**Pre-test:** {N} entries, {N} embeddings ({%}%), {N} categories, {N} tags
**Post-test:** {N} entries, {N} embeddings ({%}%), {N} categories, {N} tags
**Result:** ✅ Match / ❌ Mismatch

## Success Criteria

✅/❌ All tests pass
✅/❌ Stats match baseline
✅/❌ Export/import preserves data
✅/❌ Canonical markdown/ untouched
✅/❌ No test data pollution
✅/❌ JSON queries use json_extract_string
✅/❌ Backup preserved
✅/❌ Parity check ≥90% (README/Implementation/Tests aligned)

## Status: [READY 🚀 | ATTENTION ⚠️ | CRITICAL 🚨]

{Brief summary + action items if any}
```

---

### Step 11: 3-Way Parity Check

**Verify alignment between README claims, actual implementation, and test coverage.**

**Step 11a: Extract README Feature Claims**
```python
# Read README and identify all advertised features
```

Read `~/duckdb-kb/README.md` and extract:
- **Advertised MCP Tools** (section listing all tools)
- **Advertised Features** (semantic search, duplicate detection, export/import, etc.)
- **Advertised Capabilities** (JSON metadata, commit SHA tracking, log functionality, etc.)

**Step 11b: Verify Implementation**

For each README claim, verify actual implementation exists:
1. Check MCP server code (`mcp_server.py`) for tool definitions
   - Should advertise **15 MCP tools** (11 KB operations + 4 system tools)
   - System tools: initialize_database, git_commit_and_get_sha, get_kb_session_status, check_token_budgets
2. Check database schema (`schema.sql`) for required tables/indexes
3. Check utility modules for supporting functionality

Use Grep/Read tools to verify:
```bash
# Example: Verify all 15 tools are registered
grep -n "name=" ~/duckdb-kb/mcp_server.py | grep "Tool("
# Should return 15 matches
```

**Step 11c: Verify Test Coverage**

Compare `/test-kb` steps against README features:

| Feature (README) | Implemented? | Tested in /test-kb? | Gap? |
|------------------|--------------|---------------------|------|
| smart_search() | ✅ mcp_server.py:123 | ✅ Step 4A | - |
| Auto duplicate detection | ✅ mcp_server.py:456 | ✅ Step 5b | - |
| Export/import markdown | ✅ mcp_server.py:789 | ✅ Step 8 | - |
| JSON metadata queries | ✅ schema.sql:45 | ✅ Step 6b | - |
| ... | ... | ... | ... |

**Step 11d: Generate Parity Report**

```markdown
# 📊 3-Way Parity Check Report - {DATE}

## Summary: [ALIGNED ✅ | GAPS FOUND ⚠️]

### MCP Tools: 15 (11 KB operations + 4 system tools)
### Features Claimed in README: {N}
### Features Implemented: {N}
### Features Tested: {N}

## Gaps Detected

### 1. README Claims Not Implemented
- [ ] Feature X (claimed in README section Y, no code found)

### 2. README Claims Not Tested
- [ ] Feature Z (implemented in file.py:123, missing from /test-kb)

### 3. Implemented Features Not Documented
- [ ] Tool ABC (exists in mcp_server.py:456, not in README)

### 4. Tested Features Not Documented
- [ ] Test for XYZ (in /test-kb Step 5, not mentioned in README)

## Recommendations

1. **Update README:** Add documentation for {features}
2. **Add Tests:** Create test coverage for {features}
3. **Remove Claims:** Delete README sections for unimplemented {features}
4. **Add Implementation:** Code missing features {features}

## Alignment Score: {X}%
({implemented_and_tested} / {total_claimed} features)

## Status: [ALIGNED ✅ | MINOR GAPS ⚠️ | MAJOR GAPS 🚨]
```

**Success Criteria:**
- ✅ All README-claimed features are implemented
- ✅ All README-claimed features are tested
- ✅ All implemented features are documented
- ✅ All test steps map to documented features
- ✅ Alignment score ≥ 90%

**Action Items if Gaps Found:**
1. Update README to match implementation
2. Add missing test coverage
3. Implement missing advertised features
4. Remove obsolete documentation

---

**Notes:**
- Use `detailed=False` for `get_stats()` to save tokens (except where specified)
- Run search tests in parallel when possible
- Verify each operation before proceeding
- Track with TodoWrite
- Always use MCP tools for CRUD operations (VSS extension auto-loaded)
- Use `json_extract_string(metadata, '$.key')` for JSON queries
