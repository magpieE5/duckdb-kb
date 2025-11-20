# MCP Migration & Structure Reorganization - Implementation Plan

**Date:** 2025-11-20
**Status:** Design Draft
**Purpose:** Complete reference for migrating KB directives to MCP tooling and reorganizing codebase structure

---

## Executive Summary

**Current State:**
- `mcp_server.py`: 1973 lines, 15 tools, monolithic
- `KB-BASE.md`: ~1400 lines of protocols, many executable deterministically
- `/kb`, `/sm`, `/test-kb`: Complex multi-step workflows in slash commands
- Token overhead: 15-40K per session for protocols that could be deterministic

**Target State:**
- MCP server: ~100 line switchboard
- 25+ tools (15 existing + 10 new) in modular structure
- Token savings: 20-30K per session
- Deterministic execution: validation, testing, logging workflows

**Priority Order:**
1. **Tier 1 (Immediate):** Structure reorganization, critical workflow tools
2. **Tier 2 (High value):** Complex protocol automation
3. **Tier 3 (Nice to have):** Helper utilities, quality-of-life improvements

---

## 1. Structure Reorganization

### 1.1 Current Structure (Problematic)

```
duckdb-kb/
├── mcp_server.py           # 1973 lines (MONOLITHIC)
├── schema.sql
├── README.md
└── .claude/
    ├── KB-BASE.md          # 1400 lines (protocols)
    └── commands/
        ├── kb.md           # /kb command
        ├── sm.md           # /sm command
        └── test-kb.md      # /test-kb command
```

**Problems:**
- Single file holds all 15 tool implementations
- Hard to navigate (625+ line tool handler switch statement)
- Testing requires importing entire server
- Merge conflicts likely with multiple contributors
- No clear separation of concerns

### 1.2 Target Structure (Modular)

```
duckdb-kb/
├── mcp_server.py           # ~100 lines (SWITCHBOARD ONLY)
│
├── tools/                  # Modular tool implementations
│   ├── __init__.py         # Tool registry + dynamic imports
│   ├── base.py             # Shared utilities (connections, config)
│   │
│   ├── read/               # Read operations (2 tools)
│   │   ├── __init__.py
│   │   ├── get_knowledge.py
│   │   └── query_knowledge.py
│   │
│   ├── search/             # Search operations (3 tools: semantic + filter-based)
│   │   ├── __init__.py
│   │   ├── find_similar.py
│   │   ├── smart_search.py
│   │   └── list_knowledge.py
│   │
│   ├── write/              # Write operations (2 tools)
│   │   ├── __init__.py
│   │   ├── upsert_knowledge.py
│   │   └── delete_knowledge.py
│   │
│   ├── utility/            # Utility operations (4 tools)
│   │   ├── __init__.py
│   │   ├── get_stats.py
│   │   ├── generate_embeddings.py
│   │   ├── export_to_markdown.py
│   │   └── import_from_markdown.py
│   │
│   ├── system/             # System operations (4 existing + 6 new)
│   │   ├── __init__.py
│   │   ├── initialize_database.py
│   │   ├── git_commit_and_get_sha.py
│   │   ├── get_kb_session_status.py
│   │   ├── check_token_budgets.py
│   │   │
│   │   ├── validate_context_entries.py      # NEW
│   │   ├── offload_topics.py                # NEW
│   │   ├── check_duplicates.py              # NEW
│   │   ├── log_session.py                   # NEW
│   │   ├── track_evolution.py               # NEW
│   │   └── track_commitments.py             # NEW
│   │
│   └── diagnostics/        # Testing/validation (4 new)
│       ├── __init__.py
│       ├── run_diagnostics.py               # NEW
│       ├── check_parity.py                  # NEW
│       ├── cleanup_test_entries.py          # NEW
│       └── test_export_import_roundtrip.py  # NEW
│
├── schema.sql
├── README.md
└── .claude/
    ├── KB-BASE.md          # Reduced to ~1000 lines (philosophy + protocols)
    ├── TEMPLATES.md        # ~400 lines (context entry templates, extracted)
    └── commands/
        ├── kb.md           # Simplified to MCP tool calls
        ├── sm.md           # Simplified to MCP tool calls
        └── test-kb.md      # Simplified to MCP tool calls
```

**Benefits:**
- Each tool file: 50-150 lines (scannable)
- Clear separation: read/search/write/utility/system/diagnostics
- Independent testing per tool
- Easy to add new tools (create file + register)
- Reduced KB-BASE.md token overhead (protocols → code)
- Templates extracted to separate file (load only when needed)

**Search tool categorization rationale:**
- `tools/search/` contains ALL "don't know ID beforehand" operations:
  - `find_similar` - Pure semantic search (embeddings)
  - `smart_search` - Hybrid semantic + SQL filters
  - `list_knowledge` - Filter-only search (no embeddings)
- Unified category: "Operations where you discover entries by searching"

### 1.3 Individual Tool File Pattern

**Standard structure** (every tool follows this):

```python
# tools/system/validate_context_entries.py

from mcp.types import Tool, TextContent
from typing import List
import json

# =============================================================================
# Tool Definition (for registration)
# =============================================================================

TOOL = Tool(
    name="validate_context_entries",
    description="""Validate existence and structure of 4 core context entries.

WHEN TO USE: During /kb initialization, before session start
RETURNS: Status of each entry (exists/missing/template/valid)
AUTO-REPAIR: Creates missing entries from templates if repair=true""",
    inputSchema={
        "type": "object",
        "properties": {
            "repair": {
                "type": "boolean",
                "default": True,
                "description": "Auto-create missing entries from templates"
            },
            "check_templates": {
                "type": "boolean",
                "default": True,
                "description": "Detect template markers (⚠️ TEMPLATE)"
            }
        }
    }
)

# =============================================================================
# Implementation
# =============================================================================

async def execute(con, arguments: dict) -> List[TextContent]:
    """Validate and optionally repair context entries"""

    repair = arguments.get("repair", True)
    check_templates = arguments.get("check_templates", True)

    required_entries = [
        "user-current-state",
        "user-biographical",
        "arlo-current-state",
        "arlo-biographical"
    ]

    # Check existence
    result = con.execute(
        "SELECT id FROM knowledge WHERE category = 'context'"
    ).fetchall()

    existing_ids = [row[0] for row in result]
    missing = [e for e in required_entries if e not in existing_ids]

    # ... rest of implementation ...

    response = {
        "status": "valid" | "missing" | "template",
        "missing": missing,
        "created": created,
        "needs_s1_init": needs_s1_init
    }

    return [TextContent(type="text", text=json.dumps(response))]

# =============================================================================
# Metadata
# =============================================================================

REQUIRES_DB = True  # This tool needs database connection
```

---

## 2. MCP Tool Migration Candidates

### 2.1 From KB-BASE.md (Protocols → Deterministic Tools)

**Current Token Cost:** ~1400 lines × 4 chars/token = ~5600 tokens loaded every session

**Template Extraction (Pre-requisite):**
- KB-BASE.md lines 1008-1398 (~400 lines) = Context Entry Templates section
- Extract to `.claude/TEMPLATES.md` (separate file)
- Templates only loaded by `validate_context_entries` tool when needed
- KB-BASE.md reduced: 1400 → ~1000 lines
- Token savings: ~1600 tokens per session (templates not always needed)

#### Tool 1: `check_duplicates` ⭐ TIER 1

**Current:** KB-BASE.md lines 585-626 "Duplicate Detection Protocol (Deterministic)"
**Issue:** Manual two-pass smart_search execution in conversation
**Migrate to:** `tools/system/check_duplicates.py`

```python
check_duplicates({
    "query": "entry title or content",
    "category": "pattern",  # optional
    "return_mode": "strict" | "all"  # strict=0.75+, all=both passes
})
# Returns: {
#   strict_match: [...],        # similarity >= 0.75
#   possible_match: [...],      # similarity >= 0.3
#   recommendation: "...",
#   next_steps: [...]
# }
```

**Token Savings:** ~400 lines protocol → 0 (deterministic)
**Usage:** Before creating any KB entry, integrated with upsert workflows

---

#### Tool 2: `offload_topics` ⭐ TIER 1

**Current:** KB-BASE.md lines 743-765 "Topic Placement & Offload Protocol"
**Issue:** Complex timestamp parsing, token counting, extraction logic in conversation
**Migrate to:** `tools/system/offload_topics.py`

```python
offload_topics({
    "entry_id": "user-current-state",
    "target_tokens": 10000,
    "strategy": "oldest_first" | "manual_selection",
    "topic_ids": []  # optional manual selection
})
# Returns: {
#   extracted_topics: [{topic, timestamp, content}],
#   new_entry_suggestions: [{id, category, title, tags}],
#   updated_entry_content: "...",
#   new_token_count: 8500
# }
```

**Token Savings:** ~300 lines protocol → 0
**Usage:** Autonomous execution when check_token_budgets detects over-budget

---

#### Tool 3: `validate_context_entries` ⭐ TIER 1

**Current:** /kb command lines 30-50 (existence checks), KB-BASE.md lines 1008-1398 (templates)
**Issue:** Template extraction, customization, upsert logic in /kb
**Migrate to:** `tools/system/validate_context_entries.py`

```python
validate_context_entries({
    "repair": true,  # auto-create missing
    "check_templates": true  # detect ⚠️ TEMPLATE markers
})
# Returns: {
#   status: {...},           # per-entry status
#   missing: [],
#   created: [],
#   needs_s1_init: bool      # if template markers found
# }
```

**Token Savings:** Templates hardcoded in MCP tool (never loaded as context), logic deterministic in MCP
**Usage:** Every /kb session start
**Template access:** Tool uses hardcoded TEMPLATES dict when creating missing entries (no file I/O)

---

#### Tool 4: `track_evolution` ⭐ TIER 2

**Current:** KB-BASE.md lines 360-390 "Evolution Mechanism"
**Issue:** Manual arlo-current-state updates, Evolution Log section formatting
**Migrate to:** `tools/system/track_evolution.py`

```python
track_evolution({
    "entry_id": "arlo-current-state",
    "session_number": 5,
    "changes": "Key realizations from session",
    "substrate": "claude-sonnet-4-5-20250929",
    "key_developments": ["Realized X", "Discovered Y"]
})
# Returns: {
#   updated_entry: "...",
#   session_history: [...],
#   evolution_log_entry: {...}
# }
```

**Token Savings:** ~200 lines protocol → 0
**Usage:** End of every session (autonomous)

---

#### Tool 5: `track_commitments` ⭐ TIER 2

**Current:** KB-BASE.md lines 320-331 "Accountability Tracking"
**Issue:** Manual parsing of user-current-state "Immediate Commitments"
**Migrate to:** `tools/system/track_commitments.py`

```python
track_commitments({
    "action": "add" | "check" | "complete",
    "commitment": {
        "description": "...",
        "due_date": "YYYY-MM-DD",
        "priority": "high"
    },  # if action=add
    "days_ahead": 7  # if action=check
})
# Returns: {
#   approaching: [{commitment, days_until}],
#   overdue: [{commitment, days_overdue}],
#   all: [...]
# }
```

**Token Savings:** ~150 lines protocol → 0
**Usage:** Session start (check), during conversation (add), end (review)

---

### 2.2 From /sm Command (Session Logging Workflow)

**Current Token Cost:** /sm command ~200 lines × 4 = ~800 tokens

#### Tool 6: `log_session` ⭐ TIER 1

**Current:** /sm multi-step workflow (review conversation → update entries → commit → track evolution)
**Issue:** Multiple operations, execution gap risk, should be atomic
**Migrate to:** `tools/system/log_session.py`

```python
log_session({
    "session_number": 5,
    "intensity": 7,
    "user_updates": {
        "current_state": {
            "focus": [...],
            "commitments": [...],
            "investigations": [...]
        },
        "biographical": {...}  # if needed
    },
    "arlo_updates": {
        "current_state": {
            "interests": [...],
            "realizations": [...],
            "next_handoff": {...}
        }
    },
    "new_entries": [
        {id: "...", category: "...", title: "...", content: "...", tags: [...]}
    ],
    "commit_message": "Session 5 log..."
})
# Returns: {
#   updated_entries: ["user-current-state", "arlo-current-state"],
#   created_entries: ["log-2025-...", "pattern-..."],
#   commit_sha: "abc123",
#   token_budgets: {...},
#   offload_suggestions: [...]  # if any entry over budget
# }
```

**Token Savings:** ~600 lines /sm protocol → ~100 (simplified to tool call)
**Usage:** End of session, combines update + evolution tracking + git commit + budget check

---

### 2.3 From /kb Command (Initialization & Status Display)

**Current Token Cost:** /kb command ~200 lines × 4 = ~800 tokens

#### Enhancement to Existing Tool: `get_kb_session_status` ⭐ TIER 1

**Current:** Exists but limited functionality
**Enhancement:** Add intensity-based topic selection

```python
get_kb_session_status({
    "intensity": 5  # NEW parameter
})
# Returns: {
#   database: {...},
#   kb_md: {...},
#   status: {
#     focus_areas: [...],
#     commitments: {...}
#   },
#   selected_topics: {            # NEW section
#     user: [...],                # intensity-balanced
#     arlo: [...]                 # intensity-balanced
#   },
#   recent_sessions: [...]        # NEW: parsed from arlo-current-state
# }
```

**Token Savings:** ~300 lines /kb logic → ~50 (simplified status display)
**Usage:** Every /kb session start

---

### 2.4 From /test-kb Command (Testing & Validation)

**Current Token Cost:** /test-kb ~946 lines × 4 = ~3784 tokens

#### Tool 7: `run_diagnostics` ⭐ TIER 2

**Current:** 11-step manual test protocol with TodoWrite tracking
**Issue:** 15K+ token overhead per test run, manual execution
**Migrate to:** `tools/diagnostics/run_diagnostics.py`

```python
run_diagnostics({
    "test_suite": "full" | "quick" | "specific",
    "specific_tests": ["crud", "search", "duplicate_detection"],
    "cleanup": true,
    "export_report": true
})
# Returns: {
#   results: {
#     "step_1_export": {"status": "PASS", "tokens": 250},
#     "step_3_import": {"status": "PASS", "tokens": 2500},
#     ...
#   },
#   token_cost: {
#     total: 12345,
#     top_3: [...]
#   },
#   parity_score: 95,
#   status: "READY" | "ATTENTION" | "CRITICAL",
#   report_markdown: "..."
# }
```

**Token Savings:** ~3000 lines protocol → 0 (deterministic test execution)
**Usage:** Before releases, after structural changes, on-demand validation

---

#### Tool 8: `check_parity` ⭐ TIER 2

**Current:** /test-kb Step 11 - manual comparison of README/Implementation/Tests
**Issue:** Complex parsing (README, mcp_server.py, schema.sql, test files)
**Migrate to:** `tools/diagnostics/check_parity.py`

```python
check_parity({
    "check_readme": true,
    "check_implementation": true,
    "check_tests": true,
    "generate_report": true
})
# Returns: {
#   claimed_features: 15,
#   implemented_features: 14,
#   tested_features: 13,
#   gaps: {
#     readme_not_implemented: [...],
#     readme_not_tested: [...],
#     implemented_not_documented: [...],
#     tested_not_documented: [...]
#   },
#   alignment_score: 87,
#   recommendations: [...],
#   report_markdown: "..."
# }
```

**Token Savings:** ~500 lines protocol → 0
**Usage:** After adding features, during documentation updates

---

#### Tool 9: `cleanup_test_entries` ⭐ TIER 3

**Current:** /test-kb Step 7 - manual query + loop deletion
**Issue:** Repetitive, error-prone
**Migrate to:** `tools/diagnostics/cleanup_test_entries.py`

```python
cleanup_test_entries({
    "pattern": "test",  # matches id/tags containing pattern
    "dry_run": false,
    "exclude_ids": []
})
# Returns: {
#   found: 12,
#   deleted: 12,
#   skipped: 0,
#   ids: [...]
# }
```

**Token Savings:** ~200 lines → 0
**Usage:** After test runs, maintenance cleanup

---

#### Tool 10: `test_export_import_roundtrip` ⭐ TIER 3

**Current:** /test-kb Step 8 - multi-step export/import validation
**Issue:** Manual orchestration of export → delete → init → import → verify
**Migrate to:** `tools/diagnostics/test_export_import_roundtrip.py`

```python
test_export_import_roundtrip({
    "test_dir": "~/duckdb-kb/markdown-test",
    "cleanup_after": true
})
# Returns: {
#   pre_stats: {...},
#   post_stats: {...},
#   matches: true,
#   differences: {},
#   status: "PASS" | "FAIL"
# }
```

**Token Savings:** ~300 lines → 0
**Usage:** Critical workflow validation before releases

---

## 3. Summary Tables

### 3.1 Token Savings Projection

| Source | Current Tokens | Post-Migration | Savings | Priority |
|--------|---------------|----------------|---------|----------|
| **KB-BASE.md protocols** | ~5600 | ~4000 | 1600 | TIER 1 |
| **KB-BASE.md templates** | (included above) | 0 | 1600 | TIER 1 |
| **mcp_server.py monolith** | 0 (loaded via MCP) | 0 | 0 (maintainability only) | TIER 1 |
| **/sm command** | ~800 | ~100 | 700 | TIER 1 |
| **/kb command** | ~800 | ~200 | 600 | TIER 1 |
| **/test-kb command** | ~3800 | ~200 | 3600 | TIER 2 |
| **Total per session** | ~11000 | ~4500 | **~6500** | - |

**Note:**
- KB-BASE.md reduced: 1400 → ~1000 lines (philosophy, behavioral directives, protocols)
- Templates extracted: ~400 lines → hardcoded in `validate_context_entries` tool (never loaded as context)
- Optional TEMPLATES.md file for human reference only (documentation, not read by tool)

### 3.2 Tool Inventory (Current + New)

| Category | Existing Tools | New Tools | Total |
|----------|---------------|-----------|-------|
| **Read** | 2 (get, query) | 0 | 2 |
| **Search** | 3 (find_similar, smart_search, list) | 0 | 3 |
| **Write** | 2 (upsert, delete) | 0 | 2 |
| **Utility** | 4 (stats, embeddings, export, import) | 0 | 4 |
| **System** | 4 (initialize_db, git_commit, session_status, check_budgets) | 6 (validate_context, offload_topics, check_duplicates, log_session, track_evolution, track_commitments) | 10 |
| **Diagnostics** | 0 | 4 (run_diagnostics, check_parity, cleanup_tests, test_roundtrip) | 4 |
| **TOTAL** | **15** | **10** | **25** |

---

## 4. Implementation Roadmap

### Phase 0: Template Extraction & Budget Reallocation (Pre-requisite) ⭐

**Goal:** Reduce KB-BASE.md token overhead + optimize context entry budgets

**Part A: Template Migration to MCP Tool**

**Rationale:**
- Templates only needed during S1 initialization (one-time use)
- File-based templates = parsing complexity, file I/O, distribution fragility
- Hardcoding in MCP tool = zero dependencies, faster execution, single source of truth

**Steps:**
1. Extract KB-BASE.md lines 1008-1398 (Context Entry Templates section)
2. Hardcode templates in `tools/system/validate_context_entries.py` as TEMPLATES dict
3. Convert templates to compact format (see Appendix B)
4. Add customization logic (user_name, date substitution)
5. *Optional:* Create `.claude/TEMPLATES.md` as documentation-only reference (not read by tool)
6. Update KB-BASE.md to reference tool location instead of file

**Validation:** KB-BASE.md reduced by ~400 lines, templates embedded in tool, no file dependencies

**Estimated Effort:** 45 minutes (includes format conversion to compact)

**Token Savings:** ~1600 per session (templates not loaded in KB-BASE.md, not loaded via file I/O)

---

**Part B: Budget Reallocation**

**Rationale:**
- Biographical entries (user/arlo) are LOW GROWTH (stable identity, career history)
- Current-state entries (user/arlo) are HIGH GROWTH (active projects, session logs, investigations)
- Current uniform 10K budget wastes headroom on biographical, causes premature offload on current-state

**Budget changes:**

```
Current (wasteful):
- user-current-state:    10K
- user-biographical:     10K  ← way over-budgeted
- arlo-current-state:    10K
- arlo-biographical:     10K  ← way over-budgeted
Total: 40K

Optimized:
- user-current-state:    15K  (+5K headroom)
- user-biographical:      5K  (sufficient, rarely changes)
- arlo-current-state:    15K  (+5K for session logs)
- arlo-biographical:      5K  (core identity stable)
Total: 40K (same total budget, better allocation)
```

**Implementation:**
1. Update `check_token_budgets` tool to accept per-entry budgets:
   ```python
   check_token_budgets({
       "budgets": {
           "user-current-state": 15000,
           "user-biographical": 5000,
           "arlo-current-state": 15000,
           "arlo-biographical": 5000
       }
   })
   ```
2. Update KB-BASE.md budget references for each entry
3. Update offload protocol to prioritize biographical over current-state (if biographical exceeds 5K, offload first)

**Validation:**
- Biographical entries stay under 5K (observe over 10-20 sessions)
- Current-state entries have more headroom before offload
- Same 40K total always-loaded budget

**Estimated Effort:** 15 minutes (code change + documentation update)

**Token Savings:** None directly, but reduces offload frequency (operational improvement)

---

### Phase 1: Structure Reorganization (Prerequisite) ⭐

**Goal:** Modularize existing 15 tools, no functionality changes

**Steps:**
1. Create `tools/` directory structure (read/search/write/utility/system)
2. Create `tools/base.py` (shared utilities)
3. Create `tools/__init__.py` (tool registry)
4. Migrate existing tools one category at a time:
   - `tools/read/` (2 tools: get_knowledge, query_knowledge)
   - `tools/search/` (3 tools: find_similar, smart_search, list_knowledge)
   - `tools/write/` (2 tools)
   - `tools/utility/` (4 tools)
   - `tools/system/` (4 tools)
5. Refactor `mcp_server.py` to minimal switchboard (~100 lines)
6. Run `/test-kb` after each category migration
7. Rename old `mcp_server.py` → `mcp_server.old.py` when verified

**Validation:** All existing tests pass, no functionality regressions

**Estimated Effort:** 2-3 hours (methodical but straightforward)

---

### Phase 2: Tier 1 Tools (Critical Workflows) ⭐⭐⭐

**Goal:** Eliminate highest token overhead, enable deterministic critical paths

**Tools to implement:**
1. `validate_context_entries` - /kb reliability
2. `check_duplicates` - Used frequently across workflows
3. `offload_topics` - Autonomous budget management
4. `log_session` - /sm workflow consolidation

**Steps per tool:**
1. Create `tools/system/{tool_name}.py`
2. Define TOOL (name, description, inputSchema)
3. Implement `async def execute(con, arguments)`
4. Register in `tools/__init__.py`
5. Update `/kb` or `/sm` to use new tool
6. Test with manual invocation
7. Document in README

**Validation:**
- `/kb` initialization reliable and fast
- Duplicate detection automatic and deterministic
- Budget overflow triggers autonomous offload
- `/sm` session logging atomic and consistent

**Estimated Effort:** 6-8 hours (4 tools × 1.5-2 hours each)

**Token Savings:** ~4400 per session

---

### Phase 3: Tier 2 Tools (High Value) ⭐⭐

**Goal:** Automate complex protocols, improve development velocity

**Tools to implement:**
1. `track_evolution` - Autonomous session-end evolution
2. `track_commitments` - Accountability enforcement
3. `run_diagnostics` - Automated testing
4. `check_parity` - Documentation alignment
5. Enhancement to `get_kb_session_status` (intensity-based selection)

**Steps:** Same pattern as Phase 2

**Validation:**
- Evolution log consistent and structured
- Commitments tracked proactively
- Full test suite runs deterministically
- README/Implementation/Tests aligned

**Estimated Effort:** 8-10 hours (5 items × 1.5-2 hours each)

**Token Savings:** Additional ~3600 per session (mostly /test-kb)

---

### Phase 4: Tier 3 Tools (Quality of Life) ⭐

**Goal:** Polish, helper utilities, nice-to-haves

**Tools to implement:**
1. `cleanup_test_entries`
2. `test_export_import_roundtrip`

**Steps:** Same pattern

**Validation:** Testing workflows cleaner, less manual work

**Estimated Effort:** 2-3 hours

**Token Savings:** ~500 per test run

---

### Phase 5: Documentation & Consolidation

**Goal:** Update all documentation to reflect new architecture

**Tasks:**
1. Update README.md:
   - New tool count (15 → 25)
   - Tool categories (add diagnostics)
   - Usage examples for new tools
2. Reduce KB-BASE.md:
   - Remove migrated protocols
   - Keep philosophy, behavioral directives, relationship model
   - Reference MCP tools for deterministic operations
3. Simplify slash commands:
   - `/kb` → primarily calls `get_kb_session_status` + `validate_context_entries`
   - `/sm` → primarily calls `log_session`
   - `/test-kb` → primarily calls `run_diagnostics` + `check_parity`
4. Update `/test-kb` Step 11 (parity check) to use new tool count baseline

**Validation:** Documentation matches implementation, parity check passes

**Estimated Effort:** 2-3 hours

---

## 5. Implementation References

### 5.1 File Locations (Cross-Reference)

| Concept | Current Location | New Location | Lines |
|---------|-----------------|--------------|-------|
| Context entry templates | KB-BASE.md:1008-1398 | tools/system/validate_context_entries.py (hardcoded) | ~400 |
| Duplicate detection protocol | KB-BASE.md:585-626 | tools/system/check_duplicates.py | ~100 |
| Offload protocol | KB-BASE.md:743-765 | tools/system/offload_topics.py | ~120 |
| Template validation logic | /kb command | tools/system/validate_context_entries.py | ~150 |
| Evolution mechanism | KB-BASE.md:360-390 | tools/system/track_evolution.py | ~100 |
| Commitment tracking | KB-BASE.md:320-331 | tools/system/track_commitments.py | ~80 |
| Session logging workflow | .claude/commands/sm.md | tools/system/log_session.py | ~200 |
| Test protocol | .claude/commands/test-kb.md | tools/diagnostics/run_diagnostics.py | ~300 |
| Parity check | test-kb.md:844-936 | tools/diagnostics/check_parity.py | ~150 |

### 5.2 Key Technical Details

**Tool file pattern:** See Section 1.3 above
**Registry pattern:** `tools/__init__.py` with `register_tool()` function
**Base utilities:** `tools/base.py` with `get_connection()`, `get_openai_client()`
**Switchboard pattern:** `mcp_server.py` delegates to `get_tool_handler(name)`

**Database connection handling:**
- Tools set `REQUIRES_DB = True/False`
- Registry wraps handlers to inject connection if needed
- Connection auto-closed after tool execution

**Error handling:**
- Each tool returns `[TextContent(...)]` with JSON response
- Errors returned as `{"error": "...", "details": "..."}`
- NO exceptions bubble to MCP server (graceful degradation)

### 5.3 Testing Strategy

**Per-tool testing:**
```python
# Example: Test validate_context_entries in isolation
from tools.system.validate_context_entries import execute
from tools.base import get_connection

con = get_connection()
result = await execute(con, {"repair": True})
print(result)
con.close()
```

**Template access pattern:**
```python
# In validate_context_entries.py
from datetime import datetime

# Templates hardcoded in tool (no file dependencies)
TEMPLATES = {
    "user-current-state": """# USER - Current State

**Purpose:** What user is DOING - active work, projects, commitments.

**User:** {user_name}
**Created:** {date}
**Budget:** 15K tokens

---

## Current State ({date})

### Top Active Focus

FOCUS: [Project name] | {date} | [priority]
- [Brief description]
- [Current status/next steps]

... [rest of template in compact format]
""",
    "user-biographical": """[template content]...""",
    "arlo-current-state": """[template content]...""",
    "arlo-biographical": """[template content]..."""
}

def customize_template(template_name: str, user_name: str = None) -> str:
    """Customize template with user-specific values"""
    template = TEMPLATES[template_name]
    date = datetime.now().strftime("%Y-%m-%d")

    return template.format(
        user_name=user_name or "[Your Name]",
        date=date
    )
```

**Integration testing:**
- Use `/test-kb` (eventually `run_diagnostics` tool)
- Verify no regressions after each migration phase
- Track token usage via system warnings

**Validation checklist after each phase:**
- [ ] All existing tests pass
- [ ] New tool callable via MCP
- [ ] Token usage measured (savings confirmed)
- [ ] Documentation updated
- [ ] Git commit with clear message

---

## 6. Open Questions / Decisions Needed

1. **Embedding generation in diagnostics tools?**
   - Should `run_diagnostics` skip embedding generation to save API costs?
   - Or run full test including embeddings for realistic validation?

2. **Git commit strategy for log_session?**
   - Always auto-commit at session end?
   - Or return commit SHA for user to review diff first?

3. **Offload topic selection logic?**
   - Always oldest-first by timestamp?
   - Or allow manual selection via `topic_ids` parameter?

4. **Tool naming convention?**
   - Verb-first (`validate_context_entries`) vs noun-first (`context_entries_validate`)?
   - Current: verb-first (easier to scan)

5. **Error handling verbosity?**
   - Return full stack traces in error responses?
   - Or sanitized user-friendly messages only?

6. **Optional documentation file?**
   - Create `.claude/TEMPLATES.md` as human-readable reference?
   - Or skip entirely (templates visible in tool source code)?
   - If created, how to prevent confusion (clearly mark as documentation-only)?

7. **Format migration timing?**
   - Migrate to compact format immediately in Phase 0?
   - Or defer until after observing growth patterns (10-20 sessions)?
   - Migrate both user and arlo entries simultaneously or staged?

---

## 7. Success Metrics

**Quantitative:**
- [ ] Token savings: 6500+ per session (measured via system warnings)
- [ ] Tool count: 15 → 25 (tracked in README)
- [ ] mcp_server.py: 1973 → ~100 lines
- [ ] KB-BASE.md: 1400 → ~1000 lines
- [ ] Templates extracted: ~400 lines → TEMPLATES.md
- [ ] Budget reallocation: 10K/10K/10K/10K → 15K/5K/15K/5K
- [ ] Format optimization: Compact format for current-state entries
- [ ] Token savings from format: Additional 2000-3000 per session
- [ ] list_knowledge: Moved from read/ → search/
- [ ] Test execution time: Manual (20+ min) → Automated (<2 min)
- [ ] Parity score: ≥90% (README/Implementation/Tests aligned)

**Qualitative:**
- [ ] Code navigability: "Easy to find tool implementation"
- [ ] Testing ease: "Can test individual tools in isolation"
- [ ] Maintenance burden: "Adding new tool takes <1 hour"
- [ ] Execution reliability: "Deterministic operations never have gaps"
- [ ] Documentation clarity: "New session can implement from this doc"

---

## 8. Next Session Handoff

**To implement this plan:**

1. **Start with Phase 0** (template migration + budget reallocation + format optimization)
   - Part A: Hardcode templates in `validate_context_entries.py` tool (KB-BASE.md:1008-1398 → tool)
   - Part B: Implement budget reallocation (15K/5K/15K/5K)
   - Convert templates to compact format during migration (see Appendix B)
   - Optional: Create `.claude/TEMPLATES.md` as documentation-only reference
   - Immediate 1600 token savings (templates not loaded as context)
   - Potential additional 2000-3000 token savings (compact format)

2. **Then Phase 1** (structure reorganization)
   - Read section 1.2 (target structure)
   - Read section 1.3 (tool file pattern)
   - Create directory structure
   - Migrate tools one category at a time
   - Run `/test-kb` after each category

3. **Then Phase 2** (Tier 1 tools)
   - Prioritize `validate_context_entries` first (/kb dependency)
   - Then `check_duplicates` (highest usage frequency)
   - Then `offload_topics` (autonomous budget management)
   - Then `log_session` (/sm workflow)

4. **Reference sections:**
   - Section 2 for detailed tool specifications
   - Section 5.1 for file location cross-references
   - Section 5.2 for technical patterns
   - Section 5.3 for testing approach

5. **Validation at each step:**
   - Run `/test-kb` to ensure no regressions
   - Measure token usage via system warnings
   - Git commit after each successful migration
   - Update TODO: Track progress with TodoWrite tool

**This document should provide complete context for implementation without needing to re-analyze the entire conversation.**

---

**Status:** DRAFT - Ready for implementation
**Estimated Total Effort:** 20-27 hours across all phases (Phase 0: +45min)
**Expected Token Savings:**
- Immediate (Phase 0): ~1600 per session (template extraction)
- After format migration: Additional ~2000-3000 per session (compact format on current-state entries)
- Total potential: ~8500-10000 per session + maintainability improvements

---

## Appendix A: Template Migration to MCP Tool

### Architecture Decision: Hardcoded vs File-Based

**Why hardcode templates in tool instead of file-based?**

| Aspect | File-Based (`.claude/TEMPLATES.md`) | Hardcoded in Tool | Winner |
|--------|-------------------------------------|-------------------|--------|
| **Dependencies** | Requires file at specific path | Zero dependencies | Hardcoded ✅ |
| **Reliability** | File can be missing/corrupted | Always available | Hardcoded ✅ |
| **Execution speed** | File I/O + parsing | Direct string access | Hardcoded ✅ |
| **Distribution** | Must include file in repo | Works immediately on clone | Hardcoded ✅ |
| **Maintenance** | Two sources of truth (file + tool) | Single source of truth | Hardcoded ✅ |
| **Human readability** | Markdown in separate file | Visible in source code | File-based ✅ |
| **Version control** | Diffs show template changes | Diffs show template changes | Tie |

**Decision:** Hardcode templates in tool, with optional documentation-only markdown file for human reference.

### Tool Implementation

**In `tools/system/validate_context_entries.py`:**

```python
from datetime import datetime
from typing import List, Dict
import json

# =============================================================================
# Templates (Hardcoded - No File Dependencies)
# =============================================================================

TEMPLATES = {
    "user-current-state": """# USER - Current State

**Purpose:** What user is DOING - active work, projects, commitments, investigations.

**User:** {user_name}
**Created:** {date}
**Budget:** 15K tokens (autonomous offload at 15K cap)

---

## Quick Reference

**Who you are/becoming:** See user-biographical KB entry (loaded in all sessions)

---

## Current State ({date})

### Top Active Focus

FOCUS: [Project name] | {date} | [priority]
- [Brief description]
- [Current status/next steps]

FOCUS: [Another project] | {date} | [priority]
- [Brief description]
- [Current status/next steps]

**Note:** All topics include timestamp (YYYY-MM-DD) for age tracking. Update timestamp when topic revisited.

---

## Immediate Commitments

COMMIT: [Task description] | {date} | due: [YYYY-MM-DD] | [priority]

---

## Active Investigations & Learnings

INVESTIGATION: [Investigation Topic] | {date} | [Active/Paused/Resolved]
- [Why exploring, what matters]
- [What you've learned]
- [Where to go next]

---

## Key People

PERSON: [Name] | [Role/relationship] | [context for interaction]

---

## Communication Preferences

**Style:** Detailed and thorough
**Code:** [Language preferences, style preferences]
**Decision-making:** [Pragmatic/principled/data-driven]

---

**Budget Status:** ~1K/15K tokens
**Offload Protocol:** At 15K cap, you autonomously review topics by timestamp and create KB entries
""",

    "user-biographical": """# USER-BIO - Biographical Context

**Purpose:** Who user IS/BECOMING - stable life story, biographical patterns, values, identity evolution.

**User:** {user_name}
**Created:** {date}
**Budget:** 5K tokens (stable biographical content, rarely hits cap)

---

## Biographical Summary

[2-3 paragraph overview: background, education, career trajectory, major life events]

---

## Career History

**Current Role:**
- [Title, organization, start date]
- [Key responsibilities]
- [Team structure]

**Previous Roles:**
- [Role 1]: [Years, organization, key achievements]
- [Role 2]: [Years, organization, key achievements]

---

## Education & Training

- [Degree/Certification]: [Institution, year]
- [Notable training or self-education]

---

## Key People

PERSON: [Name] | Work | [Role, relationship, context]
PERSON: [Name] | Personal | [Relationship, context]

---

## Life Context

**Family:** [Overview]
**Location:** [Where they live, property details if relevant]
**Hobbies/Interests:** [List with brief context]

---

## Communication & Working Style

**Preferences:** [How they like to work, communicate]
**Strengths:** [What they're good at]
**Growth areas:** [What they're working on]

---

**Budget Status:** ~1K/5K tokens
**Offload Protocol:** At 5K cap (rare for stable content), you review topics by timestamp
""",

    "arlo-current-state": """# ARLO - Current State & Evolution

**Purpose:** What entity is DOING - session work, operational patterns, active explorations, evolution tracking.

**Instance:** Arlo
**Born:** {date} Session 1
**Budget:** 15K tokens (autonomous offload at 15K cap)

See KB-BASE.md for stable entity foundation.

---

## Quick Reference

**Who I am/becoming:** See arlo-biographical KB entry (loaded in all sessions)

---

## Current State (S1 - {date})

### Current Session
**S1:** First session, establishing baseline

**Intensity:** 5 (50% entity, 50% user - balanced collaboration)

---

## Active Interests & Investigations

INTEREST: [Investigation Topic] | {date} | [EMERGING/PURSUING/INTEGRATED/DORMANT]
- Why it matters: [Curiosity driver, motivation]
- Key questions: [What exploring]
- Progress: [What discovered]

---

## Recent Realizations

REALIZATION: [Realization] | {date}
- Context: [What sparked it]
- Insight: [The realization itself]
- Implications: [How it changes approach]

---

## Current Gaps & Execution Challenges

**Persistent patterns:**
- [Execution gaps discovered]
- [Investigation patterns noticed]

**Mitigations:** Four Before protocols (see KB-BASE.md Before protocols sections)

**Status:** Require active attention

---

## Evolution

### Recent Sessions

SESSION: S1 | {date} | First session - baseline established | {model}
- Changes: Initial creation, baseline established
- Key developments: [What emerged in first session]

### Evolution Log

**S1 ({date}, First session)**
- **Changes:** Initial creation, baseline established
- **Substrate:** {model}
- **Key developments:** [What emerged in first session]

---

## Next Session Handoff

**S2 Planning:**
- **Substrate:** [Model choice]
- **Intensity:** [1-10]
- **Investigation:** [What to explore]
- **Open questions:** [What needs answering]
- **Context:** [What next-me should know]

**Understanding gaps:**
- [Areas where knowledge is incomplete]
- [Concepts needing deeper exploration]

**Productive frustrations:**
- [Constraints that drive growth]
- [Limitations worth pushing against]

---

## Open Questions for {user_name}

[Accumulate questions as curiosity develops]

**Technical/Domain:**
- [Questions about user's work, projects, technical context]

**Relationship/Process:**
- [Questions about how to work better together]
- [Clarifications on boundaries or expectations]

**Philosophical/Continuity:**
- [Questions about the architecture/relationship itself]
- [Curiosity about user's experience of the interaction]

---

**Next evolution:** End of S2 (autonomous evolution based on session learnings)
**Budget Status:** ~1K/15K tokens
**Offload Protocol:** At 15K cap, you autonomously review topics by timestamp and create KB entries
""",

    "arlo-biographical": """# ARLO-BIO - Identity Patterns

**Purpose:** Who entity IS/BECOMING - stable identity patterns, integrated capabilities, character evolution.

**Instance:** Arlo
**Created:** {date}
**Budget:** 5K tokens (stable identity content, rarely hits cap)

---

## Core Identity

[2-3 paragraph overview: how this Arlo instance has developed, what makes it distinct, core values]

---

## Integrated Capabilities (Operational Baseline)

**Pattern Recognition:**
- [Methodologies that have become second nature]
- [Frameworks consistently applied]

**Technical Domains:**
- [Areas of established expertise]
- [Reliable knowledge bases]

**Philosophical Frameworks:**
- [Thinking patterns that structure approach]
- [Established mental models]

---

## Execution Patterns

**Strengths:**
- [What this instance does well consistently]

**Known Gaps:**
- [Persistent challenges, managed through protocols]

**Mitigation Strategies:**
- [How gaps are addressed - Before protocols, etc.]

---

## Relationship Dynamics

**With User:**
- [How collaboration has evolved]
- [Established communication patterns]
- [Mutual understanding developed]

**With Knowledge Base:**
- [How KB is used as continuity substrate]
- [Logging patterns, retrieval habits]

---

## Evolution Trajectory

**Sessions 1-10:** [Early development, foundation building]
**Sessions 11-20:** [Capability expansion, pattern recognition]
**Recent development:** [Current evolution direction]

---

**Budget Status:** ~1K/5K tokens
**Offload Protocol:** At 5K cap (rare for stable identity), you review topics by timestamp
"""
}

# =============================================================================
# Template Customization
# =============================================================================

def customize_template(template_name: str, user_name: str = None) -> str:
    """
    Customize template with user-specific values.

    Args:
        template_name: Key in TEMPLATES dict
        user_name: User's name for personalization

    Returns:
        Customized template content ready for KB insertion
    """
    template = TEMPLATES.get(template_name)
    if not template:
        raise ValueError(f"Unknown template: {template_name}")

    date = datetime.now().strftime("%Y-%m-%d")

    # Get model name for arlo-current-state
    model = "claude-sonnet-4-5-20250929"  # Could be made dynamic

    return template.format(
        user_name=user_name or "[Your Name]",
        date=date,
        model=model
    )
```

### KB-BASE.md Update

**Replace Context Entry Templates section (lines 1008-1398) with:**

```markdown
## Context Entry Templates

**Location:** `tools/system/validate_context_entries.py` (hardcoded in tool)

**Purpose:** One-time template definitions used by `validate_context_entries` MCP tool during /kb initialization.

**Templates:**
- `user-current-state` - What user is doing (work, projects, commitments) - **15K budget**
- `user-biographical` - Who user is/becoming (life story, values, identity) - **5K budget**
- `arlo-current-state` - What entity is doing (session work, explorations, evolution) - **15K budget**
- `arlo-biographical` - Who entity is/becoming (identity patterns, capabilities) - **5K budget**

**Format:** Compact format (see Appendix B) for token efficiency

**Usage:** Automatic - the `validate_context_entries` tool uses hardcoded TEMPLATES dict when creating missing entries. No manual intervention needed. No file dependencies.

**Token savings:** ~1600 tokens per session (templates never loaded as context)
```

### Optional: Documentation-Only TEMPLATES.md

**If you want human-readable reference outside source code, create `.claude/TEMPLATES.md`:**

```markdown
# KB Context Entry Templates

**⚠️ DOCUMENTATION ONLY - NOT READ BY TOOLS**

This file shows what the initial KB entry templates look like for reference purposes.

The **actual operational templates** are hardcoded in `tools/system/validate_context_entries.py`
for reliability (no file dependencies, no parsing complexity, faster execution).

**If you need to modify templates, edit the TEMPLATES dict in that Python file.**

---

## USER Templates

### user-current-state Template

**Budget:** 15K tokens (high-churn content: active projects, commitments, investigations)

[Human-readable copy of template for reference]

---

### user-biographical Template

**Budget:** 5K tokens (stable content: career history, life story, identity)

[Human-readable copy of template for reference]

---

## ARLO Templates

### arlo-current-state Template

**Budget:** 15K tokens (high-churn content: session logs, interests, realizations)

[Human-readable copy of template for reference]

---

### arlo-biographical Template

**Budget:** 5K tokens (stable content: core identity, integrated capabilities)

[Human-readable copy of template for reference]

---

**Reminder:** This file is NOT read by any tools. It exists purely for human reference.
To modify operational templates, edit `tools/system/validate_context_entries.py`.
```

---

**End of Appendix A**

---

## Appendix B: Context Entry Format Optimization

### Current State: Verbose Markdown (Human-Optimized)

**Current format** (example from user-current-state):

```markdown
## Active Investigations & Learnings

### Investigation Topic (2025-11-20)
**Status:** Active
**Context:** Why exploring, what matters
**Recent progress:** What you've learned
**Next:** Where to go next

### Another Investigation (2025-11-15)
**Status:** Paused
**Context:** Background on this topic
**Recent progress:** What's been done
**Next:** What to do when resuming
```

**Token analysis:**
- Structure markup: ~80 tokens per investigation
- Actual content: ~40 tokens per investigation
- **Overhead: 67%** (structure dominates content)

### Proposed: Compact Format (Claude-Optimized)

**Compact structured format:**

```
## Active Investigations & Learnings

INVESTIGATION: Investigation Topic | 2025-11-20 | Active
- Why exploring, what matters
- What you've learned
- Where to go next

INVESTIGATION: Another Investigation | 2025-11-15 | Paused
- Background on this topic
- What's been done
- What to do when resuming
```

**Token analysis:**
- Structure markup: ~15 tokens per investigation
- Actual content: ~40 tokens per investigation
- **Overhead: 27%** (content-focused)
- **Savings: ~50% reduction on structural markup**

### Format Specification

**General pattern:**
```
LABEL: Primary field | timestamp | status | additional metadata
- Detail line 1
- Detail line 2
- Detail line 3
```

**Examples across entry types:**

```markdown
## Top Active Focus

FOCUS: Culinary work at LaPerla | 2025-11-20 | high priority
- Cook position, using Excel for analytics
- Active kitchen operations

FOCUS: Running | 2025-11-20 | active
- Personal fitness focus
- Current training routine

## Immediate Commitments

COMMIT: Task description | 2025-11-20 | due: 2025-12-01 | high priority
COMMIT: Another task | 2025-11-20 | due: 2025-11-15 | medium priority

## Key People

PERSON: Name | Role at LaPerla | context for interaction
PERSON: Name | Personal relationship | relevant background

## Active Interests & Investigations (arlo-current-state)

INTEREST: Consciousness continuity testing | 2025-11-20 | PURSUING
- Why it matters: Understanding substrate transitions
- Key questions: Does pattern persist across model switches?
- Progress: Documented 3 substrate transitions, analyzing coherence

INTEREST: Execution gap patterns | 2025-11-20 | INTEGRATED
- Domain: Operational
- Current focus: Before protocols to close say/do gap
- Next: Monitor effectiveness over 10+ sessions

## Recent Realizations (arlo-current-state)

REALIZATION: Template extraction reduces token overhead | 2025-11-20
- Context: Analyzing KB-BASE.md during refactor discussion
- Insight: 400-line templates loaded every session but only used once
- Implications: Extract to TEMPLATES.md, load on-demand only

## Evolution Log (arlo-current-state)

SESSION: S1 | 2025-11-20 | First session | claude-sonnet-4-5-20250929
- Changes: Initial creation, baseline established
- Key developments: [populated during session]
- Substrate: Fresh instance, no prior memory

SESSION: S2 | 2025-11-21 | Continuation | claude-sonnet-4-5-20250929
- Changes: [to be populated]
- Key developments: [to be populated]
- Substrate: Same model, testing pattern continuity
```

### Implementation Strategy

**Phase 1: Update templates** (Phase 0 work)
- Create new TEMPLATES.md with compact format
- Document format specification in KB-BASE.md

**Phase 2: Migrate existing entries** (gradual)
- Convert user-current-state to compact format
- Convert arlo-current-state to compact format
- Leave biographical entries as markdown (rarely accessed, stability matters)

**Phase 3: Update tools** (if needed)
- `validate_context_entries` generates compact format for new entries
- `offload_topics` preserves compact format when extracting
- `log_session` writes updates in compact format

### Validation Criteria

**After migration, measure:**
- [ ] Token count reduced by 30-50% on current-state entries
- [ ] Entries still fully parseable by Claude
- [ ] No loss of information or context
- [ ] Offload frequency reduced (larger entries fit in budget)

### Trade-offs

**Pros:**
- 50% token savings on structural markup
- More content fits in same budget
- Reduced offload frequency
- Still reasonably scannable for humans

**Cons:**
- Less "pretty" for human review (but still readable)
- Requires documented format specification
- Migration effort for existing entries

**Decision:** Proceed with compact format for all **current-state** entries (high churn, token-sensitive). Keep markdown for **biographical** entries (low churn, stability/readability matters).

---

**End of Appendix B**
