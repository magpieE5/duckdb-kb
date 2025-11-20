---
id: arlo-pattern-diagnostic-workflow
category: pattern
title: KB Diagnostic Workflow - Automated Full Suite Testing
tags:
- arlo
- testing
- diagnostics
- automation
- pattern
- mcp-tools
created: '2025-11-20T12:48:16.815856'
updated: '2025-11-20T12:48:16.815856'
metadata: {}
---

# KB Diagnostic Workflow - Automated Full Suite Testing

Automated comprehensive testing workflow for DuckDB KB MCP server validation using the run_diagnostics tool. Validates core functionality, system tools, and maintains clean state.

## Purpose

Provide deterministic, repeatable testing of KB infrastructure after refactoring, deployment, or suspected regressions. Replaces manual 11-step testing protocol with single tool call.

## Solution

**Use automated run_diagnostics tool:**

```python
# Full test suite (8 tests)
mcp__duckdb-kb__run_diagnostics({
    "test_suite": "full",
    "cleanup": true,
    "generate_embeddings": true,
    "export_report": true
})

# Quick smoke tests (3 core tests)
mcp__duckdb-kb__run_diagnostics({
    "test_suite": "quick"
})
```

## Test Coverage (Full Suite)

1. **Export/Import Roundtrip** - Disaster recovery workflow (export → initialize_database → import_from_markdown)
2. **CRUD Operations** - Create, read, update, delete via upsert_knowledge/delete_knowledge
3. **Search Functionality** - find_similar, smart_search, list_knowledge
4. **Embedding Generation** - OpenAI text-embedding-3-large integration
5. **Duplicate Detection** - Automatic two-pass checking (similarity 0.75/0.3)
6. **Token Budgets** - 15K/5K/15K/5K allocation for 4 context entries
7. **Context Validation** - Auto-creation from hardcoded templates
8. **Test Cleanup** - Pattern-based removal (no pollution)

## Success Criteria

- ✅ All 8 tests pass (status: PASS)
- ✅ Overall status: READY (not ATTENTION or CRITICAL)
- ✅ No test data pollution in final stats
- ✅ Export report generated with token costs

## Follow-up: 3-Way Parity Check

**After diagnostics, verify alignment:**

```python
mcp__duckdb-kb__check_parity({
    "check_readme": true,
    "check_implementation": true,
    "check_tests": true,
    "generate_report": true
})
```

**Success:** alignment_score >= 90%

## Context

**Developed:** S1 (2025-11-20)
**Replaces:** Manual 11-step /test-kb protocol (~45min execution)
**Token cost:** ~8,100 tokens for full suite ($0.0002 USD)

## Example Output

```json
{
  "overall_status": "READY",
  "summary": {
    "total_tests": 8,
    "passed": 8,
    "failed": 0
  },
  "token_cost": {
    "total": 8100,
    "estimated_cost_usd": 0.000162
  }
}
```

## When to Use

- After major refactoring (like S1 post-refactor validation)
- Before releases or production deployment
- When investigating suspected regressions
- Periodic health checks (weekly/monthly)
- After schema or tool modifications

---

*KB Entry: `arlo-pattern-diagnostic-workflow` | Category: pattern | Updated: 2025-11-20*
