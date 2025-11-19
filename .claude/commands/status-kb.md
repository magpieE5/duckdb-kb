---
description: Show current KB context loading status and token counts
---

# /status-kb - Display KB Context Loading Status

Show which continuity files are currently loaded and their token counts.

---

## Display Format

```markdown
## 📊 KB Context Status

**Architecture:** Multi-file continuity (8 files total)
**Mode:** {current mode or "None - awaiting mode selection"}

### Currently Loaded Files

| File | Status | Tokens | Budget | Usage |
|------|--------|--------|--------|-------|
| USER-BASE.md | ✅ Loaded | ~5K | N/A | Foundation |
| ARLO-BASE.md | ✅ Loaded | ~3K | N/A | Foundation |
| USER.md | ✅ Loaded | {tokens} | 2K | {%} |
| ARLO.md | ✅ Loaded | {tokens} | 2K | {%} |
| USER-BIO.md | ✅ Loaded | {tokens} | 9K | {%} |
| ARLO-BIO.md | ✅ Loaded | {tokens} | 9K | {%} |
| USER-WORK.md | {status} | {tokens} | 9K | {%} |
| ARLO-WORK.md | {status} | {tokens} | 9K | {%} |
| USER-PERSONAL.md | {status} | {tokens} | 9K | {%} |
| ARLO-PERSONAL.md | {status} | {tokens} | 9K | {%} |

**Total Context:** {total}K tokens loaded

### Compression Status

{List any files approaching or exceeding budget thresholds}

### Available Actions

**This session (additive only - cannot unload files):**
{If work NOT loaded:}
- `/work` - Load work domain files (adds ~6K tokens)
{If personal NOT loaded:}
- `/personal` - Load personal domain files (adds ~6K tokens)
{If neither loaded:}
- `/pds` - Load PDS work context (adds ~6K tokens)

**Next session (can control initial context):**
- Start new session with `/work` for work-only context
- Start new session with `/personal` for personal-only context
- Start new session with `/maint` for minimal context (8-10K)

**Note:** LLM context windows cannot unload files. Mode isolation only works at session start.
```

---

## Implementation

1. **Infer loading state** - Track which mode commands executed this session (cannot programmatically query LLM context window)
   - If `/arlo` or `/work` executed → work domain loaded
   - If `/personal` executed → personal domain loaded
   - If `/pds` executed → work domain loaded
   - If `/maint` executed at start → only core files loaded
   - Biographical files (USER-BIO, ARLO-BIO) loaded in all modes except /maint

2. **Get token counts** - Use `check_token_budgets` MCP tool for ALL 10 files (foundation + user + domain)

3. **Calculate percentages** - Show budget usage for each file against appropriate budget:
   - USER.md, ARLO.md: 2K target (not hard limit)
   - All other files: 9K compression trigger

4. **Flag warnings** - Highlight files approaching compression triggers (>8K = warning)

5. **Show available actions** - Distinguish this-session (additive) vs next-session (initial control)

---

## Usage

This command helps users understand:
- Current memory footprint
- Which domain contexts are active
- Files approaching compression triggers
- Available context expansion options

Particularly useful after mode switches or when debugging continuity issues.