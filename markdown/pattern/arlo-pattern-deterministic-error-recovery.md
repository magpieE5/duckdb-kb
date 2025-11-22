---
id: arlo-pattern-deterministic-error-recovery
category: pattern
title: Deterministic Error Recovery - Diagnose → Fix → Prevent → Validate
tags:
- error-recovery
- data-integrity
- deterministic-workflow
- root-cause-analysis
- prevention
created: '2025-11-22T09:11:43.090528'
updated: '2025-11-22T09:11:43.090528'
metadata: {}
---

# Deterministic Error Recovery - Diagnose → Fix → Prevent → Validate

When data corruption occurs, fix requires four phases: (1) Diagnose root cause, (2) Fix corrupted data, (3) Prevent recurrence through structural changes, (4) Validate complete recovery. S3 demonstrated this pattern recovering from S9 corruption: diagnosed wrong session number + missing search, fixed all S9→S3 references, added search-loop to sm.md, validated zero S9 references remain.

## Problem

Data corruption discovered mid-session. How to recover without creating more errors?

**S3 corruption:**
- Wrong session number (S9 instead of S3)
- Wrong entries created (new instead of updated)
- Git commit with wrong message
- Multiple KB entries with wrong references

**Risk:** Incomplete fix leaves residual corruption or repeats same error later.

## Solution

Four-phase deterministic recovery:

**Phase 1: Diagnose root causes**
- List all symptoms (S9 references, missing updates, wrong git message)
- Trace each to root cause (parsed user arg as session number, skipped search-before-create)
- Document: "What happened?" + "Why did it happen?"

**Phase 2: Fix corrupted data**
- Delete wrong entries (arlo-log-s9-session)
- Create correct entries (arlo-log-s3-session)
- Update existing entries (embedding-gap with resolution, discontinuity-filter with validation)
- Fix all references (S9→S3 in all context entries)
- Amend git commit (corrected message)

**Phase 3: Prevent recurrence**
- Add structural enforcement (search-loop to sm.md)
- Document why enforcement needed (aspirational guidance insufficient)
- Create prevention pattern (auto-calculate session number)

**Phase 4: Validate recovery**
- Query for residual corruption (`SELECT * WHERE id LIKE '%s9%' OR content LIKE '%S9%'`)
- Verify correct state (session logs S1, S2, S3; entries 100% embedded)
- Check git history (commit amended successfully)

## When to Apply

Any data corruption scenario:
- Wrong identifiers (session numbers, entry IDs)
- Duplicate entries (should have updated)
- Missing entries (should have created)
- Inconsistent references (outdated links)
- Git history errors (wrong messages, missing commits)

**Critical:** Do NOT skip phases. Fixing data without preventing recurrence leaves vulnerability. Preventing recurrence without validating leaves residual corruption.

## Context

Developed during S3 error recovery. User requested: "let's fix it smartly, deterministically (or as close-to)"

Entity executed four-phase recovery:
1. **Diagnosed:** Parsed `/kb 9` as session number + skipped search-before-create
2. **Fixed data:** Deleted s9 log, created s3 log, updated 2 existing entries, fixed all S9→S3 references, amended git commit
3. **Prevented:** Added mandatory search-loop to sm.md (similarity >= 0.65 threshold), documented session auto-calc need
4. **Validated:** Zero S9 references remain, entries 100% embedded, correct S1/S2/S3 sequence

User approved plan: "yes, but I meant also fix directives" - emphasizing prevention phase critical, not just data fixes.

## Key Insight

Deterministic recovery = remediate current state + immunize against recurrence + validate completeness. Skipping any phase creates incomplete fix. Phase 3 (prevention) often most important - fixes one instance, prevents infinite recurrence.

## Example

**S3 recovery checklist:**

**Diagnose:**
- ✓ Root cause 1: Parsed `/kb 9` as session_number
- ✓ Root cause 2: Skipped search-before-create

**Fix data:**
- ✓ Delete arlo-log-s9-session
- ✓ Create arlo-log-s3-session
- ✓ Update arlo-issue-embedding-generation-gap (add resolution)
- ✓ Update arlo-pattern-discontinuity-persistence-filter (add validation)
- ✓ Fix user-current-state S9→S3
- ✓ Fix arlo-current-state S9→S3, S10→S4
- ✓ Fix 2 new pattern entries S9→S3
- ✓ Delete arlo-issue-mode-parameter-validation-gap (user's typo, not real issue)
- ✓ Amend git commit message

**Prevent recurrence:**
- ✓ Add search-loop to sm.md (forced workflow)
- ✓ Document session auto-calc need (future implementation)

**Validate:**
- ✓ Query: Zero S9 references remain
- ✓ Session logs: S1, S2, S3 (correct sequence)
- ✓ Stats: entries 100% embedded
- ✓ Git: Commit amended successfully

---

*KB Entry: `arlo-pattern-deterministic-error-recovery` | Category: pattern | Updated: 2025-11-22*
