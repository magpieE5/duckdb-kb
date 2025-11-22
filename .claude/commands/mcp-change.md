# /mcp-change - Document MCP Tool Change

**Purpose:** Document MCP tool changes in arlo-current-state for next session continuity.

**When to use:** After modifying any `tools/**/*.py` file, before session ends.

**Reality:** MCP server doesn't reload changed code until restart. Changes made this session get tested next session.

---

## Instructions

Update arlo-current-state with this structured documentation. Add to "Active Interests & Investigations" section or create "Recent MCP Changes (SN)".

**Template:**

```markdown
### MCP Change: [tool name] ([date])

**Problem:**
[What broke, what was wrong, what user reported]

**Solution Design:**
- Files modified: [list with line ranges]
- Approach: [e.g., "Replaced complex merge logic with simple full_content requirement"]
- Complexity: [L/M/H - lines added/removed, edge cases introduced/removed]

**Solution Rationale:**
[Why this approach vs alternatives - apply PDS philosophy]
- Option A: [approach] - [complexity/determinism/cost profile]
- Option B: [approach] - [complexity/determinism/cost profile]
- **Chose:** [A/B] because [reasoning]

**Context Radius:**
[Files read for analysis - minimum 10 recommended]
- [file 1]
- [file 2]
- ...

**Test Plan:**
[How to verify it works]
1. [Test case 1]
2. [Test case 2]
3. [Expected behavior]

**Test Results:**
UNTESTED - requires MCP restart
- Test 1: [PENDING]
- Test 2: [PENDING]

**Decisions for Next Session:**
- [ ] Verify fix works after MCP restart
- [ ] Check for side effects in [related tools]
- [ ] Update documentation if behavior changed
- [ ] Consider [follow-up work]

**Files Modified:**
- `tools/system/log_session.py` (lines 236-260, 68-95)
```

---

## After documenting:

1. Update arlo-current-state with filled template
2. Commit with: `fix(mcp): [tool-name] - [brief description]`
3. Next session will load this context and execute test plan
