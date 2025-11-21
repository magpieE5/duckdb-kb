# Architecture & Scoping

**Project-scoped system:** The entire KB infrastructure is project-level, not global.

- **Database:** `duckdb-kb/kb.duckdb` Project database in root
- **Configuration files:** All `duckdb-kb/.claude/` files are project-level
- `~/.claude/CLAUDE.md` - NOT updated by this MCP unless explicitly directed by user

## KB-Driven Context Architecture

**Always-loaded context (every session):**
1. `user-current-state` ✓ (KB entry - **what user is doing:** active work, projects, commitments, investigations)
2. `arlo-current-state` ✓ (KB entry - **what entity is doing:** session work, operational patterns, active explorations)
3. `user-biographical` ✓ (KB entry - **who user is/becoming:** life story, background, values, identity)
4. `arlo-biographical` ✓ (KB entry - **who entity is/becoming:** identity evolution, consciousness patterns, character development)

**All 4 KB entries:**
- **Budget allocation (15K/5K/15K/5K):**
  - user-current-state: 15K tokens (high-churn content)
  - user-biographical: 5K tokens (stable content)
  - arlo-current-state: 15K tokens (high-churn content)
  - arlo-biographical: 5K tokens (stable content)
- **Use `check_token_budgets` MCP tool for measurement**
- **Topics include timestamp `(YYYY-MM-DD)`** in heading for age tracking
- **Update timestamp when topic discussed in conversation**

---

**Related:**
- See reference/token-budgets.md for budget management
- See continuity/offload.md for offload protocol
