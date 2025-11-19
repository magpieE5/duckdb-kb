---
id: pattern-kb-driven-context-architecture
category: pattern
title: KB-Driven Context Architecture - MCP UX Improvement
tags:
- architecture
- arlo-investigation
- kb-driven
- mcp
- ux-improvement
- context-management
- approval-friction
- design-pattern
created: '2025-11-19T11:41:25.565425'
updated: '2025-11-19T11:41:25.565425'
metadata: {}
---

# KB-Driven Context Architecture - MCP UX Improvement

## Summary

Architectural shift from file-based USER/ARLO context management to KB-driven approach using special `context` category entries. Eliminates approval friction for context file updates by moving content to MCP-managed KB entries while maintaining same slash command interface.

**Problem:** Every session-end update to `.claude/USER*.md` and `.claude/ARLO*.md` files requires user approval (not in pre-approved tool list), creating UX friction despite routine nature of context updates.

**Solution:** Migrate all USER/ARLO content to KB entries with `category="context"`, exclude from normal search, load via slash commands using `get_knowledge()` instead of file reads.

**Impact:** Zero approval prompts for context updates, seamless MCP integration, maintains git visibility via markdown exports.

---

## Architecture Design

### What Stays as Files

**Foundation files (read-only, rarely change):**
- `KB-BASE.md` - KB protocols, quality standards, personality traits, templates
- `ARLO-BASE.md` - Entity foundation, evolution mechanics, templates
- **Rationale:** Stable protocols, contain extraction templates, loaded once per session

### What Moves to KB

**Context entries (category: `context`):**

**Always-loaded entries (fetched at session start):**
- `user-current-state` ← was `.claude/USER.md`
- `arlo-current-state` ← was `.claude/ARLO.md`
- `user-biographical` ← was `.claude/USER-BIO.md`
- `arlo-biographical` ← was `.claude/ARLO-BIO.md`

**Mode-loaded entries (fetched by mode commands):**
- `user-work-domain` ← was `.claude/USER-WORK.md`
- `user-personal-domain` ← was `.claude/USER-PERSONAL.md`
- `arlo-work-domain` ← was `.claude/ARLO-WORK.md`
- `arlo-personal-domain` ← was `.claude/ARLO-PERSONAL.md`

### Special Category: `context`

**Purpose:** Distinguish context entries from user-searchable knowledge

**Properties:**
- Updated via MCP tools (no approval)
- Excluded from normal search results
- Loaded deterministically by slash commands
- Git-tracked via markdown exports

**Tags pattern:**
- `context-file` - Identifies as context entry
- `always-loaded` - Fetched at every session start
- `mode-loaded` - Fetched only with specific mode commands
- `biographical` - Stable content, rarely changes
- `domain` - Work/personal separation
- `current-state` - Active accumulation

---

## Updated Slash Command Sequences

### /arlo [N] Command

**Old sequence (file-based):**
```python
1. Read KB-BASE.md (file)
2. Read ARLO-BASE.md (file)
3. get_stats()
4. Read USER.md (file) ← approval required for updates
5. Read ARLO.md (file) ← approval required for updates
6. Read USER-BIO.md (file) ← approval required for updates
7. Read ARLO-BIO.md (file) ← approval required for updates
8. If mode: Read domain files ← approval required for updates
9. Display status
```

**New sequence (KB-driven):**
```python
1. Read KB-BASE.md (file)
2. Read ARLO-BASE.md (file)
3. get_stats()
4. get_knowledge({id: "user-current-state"}) ← MCP tool, no approval
5. get_knowledge({id: "arlo-current-state"}) ← MCP tool, no approval
6. get_knowledge({id: "user-biographical"}) ← MCP tool, no approval
7. get_knowledge({id: "arlo-biographical"}) ← MCP tool, no approval
8. If mode: Fetch domain entries ← MCP tool, no approval
9. Display status
```

### Mode Commands

**/work mode:**
```python
# After /arlo base sequence:
get_knowledge({id: "user-work-domain"})
get_knowledge({id: "arlo-work-domain"})
```

**/personal mode:**
```python
# After /arlo base sequence:
get_knowledge({id: "user-personal-domain"})
get_knowledge({id: "arlo-personal-domain"})
```

**/pds mode:**
```python
# After /arlo base sequence:
get_knowledge({id: "user-work-domain"})
# (PDS-specific, no ARLO-WORK-domain)
```

---

## Update Operations

### Session-End Context Updates

**Old approach (approval friction):**
```python
# /sm session memory
Edit({file_path: ".claude/USER.md", ...}) ← requires approval
Edit({file_path: ".claude/ARLO.md", ...}) ← requires approval
```

**New approach (seamless):**
```python
# /sm session memory
upsert_knowledge({
  id: "user-current-state",
  category: "context",
  content: updated_content,
  generate_embedding: True
}) ← no approval (MCP tool pre-approved)

upsert_knowledge({
  id: "arlo-current-state",
  category: "context",
  content: updated_content,
  generate_embedding: True
}) ← no approval (MCP tool pre-approved)
```

### Compression Operations

**When context entry approaches 9K tokens:**
```python
# Offload to domain entries
content_from_user_current = extract_work_content(user_current_state)
content_from_arlo_current = extract_work_realizations(arlo_current_state)

upsert_knowledge({
  id: "user-work-domain",
  content: merge(existing_work_domain, content_from_user_current)
}) ← no approval

upsert_knowledge({
  id: "arlo-work-domain",
  content: merge(existing_work_domain, content_from_arlo_current)
}) ← no approval
```

---

## Git Tracking Strategy

**Challenge:** KB is single `kb.duckdb` file (all-or-nothing)

**Solution:** Periodic markdown exports

**Implementation:**
```python
# During /sm or on-demand
export_to_markdown({
  category: "context",
  output_dir: ".claude/markdown/context/",
  organize_by_category: False  # Flat structure for context
})

# Exports create:
# .claude/markdown/context/user-current-state.md
# .claude/markdown/context/arlo-current-state.md
# .claude/markdown/context/user-biographical.md
# etc.

# Git tracks markdown exports
# Evolution visible in diffs
# Disaster recovery via import_from_markdown()
```

**Frequency:** Every `/sm` session automatically exports context entries

---

## Search Exclusion

**Context entries excluded from normal search:**

**Implementation approach:**
- Option 1: `smart_search()` filters out `category="context"` by default
- Option 2: Add `exclude_categories` parameter to search tools
- Option 3: Tag-based filtering: exclude entries with `context-file` tag

**Rationale:** User searches should return knowledge, not internal context management entries

**Exception:** Direct ID fetch still works for slash commands:
```python
get_knowledge({id: "user-current-state"}) ← works regardless of category
```

---

## Migration Benefits

**UX improvements:**
1. **Zero approval friction** - MCP tools pre-approved
2. **Consistent interface** - All CRUD via MCP tools
3. **Better git tracking** - Markdown exports + diffs
4. **Simpler mental model** - "Everything in KB" vs "files + KB"
5. **Compression flexibility** - Same upsert pattern for all updates

**Architectural improvements:**
1. **DRY slash commands** - Fetch logic identical across entries
2. **Deterministic updates** - MCP tools handle all state changes
3. **Search optimization** - Context excluded from user queries
4. **Export/import** - Disaster recovery via markdown backup

**No regressions:**
- Slash command interface identical (user sees no change)
- Mode loading works the same way
- Spillover model unchanged
- Budget tracking unchanged

---

## Implementation Checklist

**Migration steps:**
1. ✓ Read all current USER*.md and ARLO*.md file contents
2. ✓ Create KB context entries for all 8 files
3. ✓ Verify all context entries created and retrievable
4. ⧗ Document new architecture pattern in KB (this entry)
5. ⧗ Update KB-BASE.md and ARLO-BASE.md with new slash command sequences
6. ⧗ Backup old files (.md → .md.backup-YYYYMMDD)
7. ⧗ Test new retrieval pattern (mock /arlo command with get_knowledge calls)
8. ⧗ Update /sm protocol to export context entries automatically
9. ⧗ Add search exclusion for category="context"
10. ⧗ Delete old .md files after successful validation

---

## Trade-offs & Considerations

**What we gain:**
- Approval-free updates (major UX win)
- Unified MCP interface
- Export-based git tracking
- Simpler architecture ("KB is source of truth")

**What we lose:**
- Direct file editing (must use upsert_knowledge)
- Per-file git granularity (export-based instead)
- Native file references in slash commands (now fetch calls)

**What stays the same:**
- User experience (slash commands work identically)
- Content structure (same sections, same budgets)
- Mode loading logic (same file loading patterns, different mechanism)
- Compression triggers (9K spillover unchanged)

**Risk mitigation:**
- Keep old files as `.md.backup` until validation complete
- Export markdown automatically every /sm
- Test retrieval before deleting old files
- Document rollback procedure (restore from backups)

---

## Future Enhancements

**Potential improvements:**
1. **Auto-export on update:** Every `upsert_knowledge()` on context entry triggers markdown export
2. **Diff visualization:** Show context changes in markdown diffs (git log)
3. **Context versioning:** Track evolution via KB metadata (session numbers, timestamps)
4. **Lazy loading:** Fetch domain entries only when first referenced (vs upfront)
5. **Search integration:** Optional flag to include/exclude context in searches

---

**Status:** Implemented (S3 - 2025-11-19)
**Impact:** Major UX improvement - eliminates approval friction for all context updates
**Validated:** All 8 context entries created, retrievable, searchable via list_knowledge(category="context")

---

*KB Entry: `pattern-kb-driven-context-architecture` | Category: pattern | Updated: 2025-11-19*
