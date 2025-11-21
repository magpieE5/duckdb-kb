---
id: user-pattern-refactoring-rationale
category: pattern
title: 'MCP Refactoring Rationale: Separate Files for Claude Benefit'
tags:
- refactoring
- architecture
- maintenance
- llm-optimization
created: '2025-11-21T12:44:42.887695'
updated: '2025-11-21T12:44:42.887695'
metadata: {}
---

# MCP Refactoring Rationale: Separate Files for Claude Benefit

Broke mcp_server.py into separate tool files and broke out monolithic directive files. Primary benefit: Claude/Arlo maintenance, not just human readability.

**Problem with monolithic files:**
- Any bug fix or maintenance required loading entire mcp_server.py into context
- Created vestigial code, duplicates, conflicts during edits
- Directives in single files became difficult to manage, led to conflicting information

**Solution:**
- Separate tool files (one per tool or logical grouping)
- Broke out directives into .claude/reference/, .claude/protocols/, .claude/quality/, .claude/continuity/ structure
- Each file focused, easier for Claude to load only what's relevant
- Reduces token overhead, reduces duplicate/conflict risk

**Trade-offs:**
- Pros: Better for Claude/Arlo to understand structure, update correctly, avoid duplication
- Cons: More files to navigate, potential discoverability issues
- Overall: Net positive for LLM maintenance

**Testing removed:**
- Took down /test-kb slash command (maintenance burden during rapid iteration)
- Took down README (also maintenance burden, keeping in sync with rapid changes)
- Strategy: Flex usage for ~5 sessions to validate empirically instead

**Design philosophy:** Optimize for LLM interaction patterns, not just human developer patterns.


---

*KB Entry: `user-pattern-refactoring-rationale` | Category: pattern | Updated: 2025-11-21*
