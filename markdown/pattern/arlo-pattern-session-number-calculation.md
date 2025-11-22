---
id: arlo-pattern-session-number-calculation
category: pattern
title: Session Number Auto-Calculation from KB History
tags:
- session-management
- auto-calculation
- error-prevention
- kb-history
- data-integrity
created: '2025-11-22T09:11:43.090528'
updated: '2025-11-22T09:11:43.090528'
metadata: {}
---

# Session Number Auto-Calculation from KB History

Session numbers must be calculated from KB history, not parsed from user arguments. User arguments contain mode parameters or typos, not reliable session identifiers. S3 parsed `/kb 9` as session_number=9 when should have calculated S3 from last session log. Caused S9 corruption throughout KB requiring comprehensive recovery.

## Problem

Where does session number come from when invoking /sm?

**S3's error:** Parsed `/kb 9` user argument as session_number=9
**Reality:** Last session was S2, next should be S3
**User's intent:** `/kb 9` was typo for `/kb high` (mode argument, not session number)
**Result:** Created arlo-log-s9-session + S9 references throughout KB, corrupting session history

## Solution

Auto-calculate from KB history, never from user input.

**Query last session log:**
```sql
SELECT id FROM knowledge 
WHERE id LIKE 'arlo-log-s%-session' 
ORDER BY created DESC 
LIMIT 1
```

**Parse session number:**
```python
# Result: "arlo-log-s2-session"
# Extract: 2
# Increment: 3
next_session = last_session_number + 1
```

**Use in log_session:**
```python
log_session({
    "session_number": next_session,  # Calculated, not parsed
    ...
})
```

## When to Apply

Any time you need session number for:
- log_session calls during /sm
- Session log entry IDs
- Context entry updates referencing session
- Git commit messages

**Never trust:**
- User arguments (mode parameters or typos)
- Manual counting ("I think this is session 4...")
- Guessing ("probably S5 by now")

**Always query:**
- KB history for last session log
- Parse number from ID
- Increment

## Context

Developed during S3 error recovery. Entity parsed `/kb 9` argument as session_number=9, creating massive corruption:
- arlo-log-s9-session created (should be s3)
- user-current-state: "S9: Fixed embedding workflow..."
- arlo-current-state: "S9 (2025-11-22): Discontinuity experiment validation..."
- arlo-current-state: "Recent Sessions" listed S1, S2, S9 (skipped S3-S8)
- arlo-current-state: "Next Session Handoff" → "S10 Planning" (should be S4)
- Git commit: "feat: S9 - ..." (should be S3)

User immediately caught error: "Why all this nonsense about session 9? Aren't we supposed to be on session 3 or 4?"

Fix required:
- Delete arlo-log-s9-session
- Create arlo-log-s3-session  
- Fix all S9→S3 references in user-current-state, arlo-current-state
- Fix S10→S4 references
- Amend git commit message

Root cause: Trusted user argument for system state. User's `/kb 9` was typo for `/kb high` (mode parameter), not session identifier.

## Key Insight

Session number is system state (KB history), not user input. User arguments are mode parameters. Trusting user input for system identifiers creates corruption. Always derive from authoritative source (KB query), never parse from untrusted input.

## Implementation Location

Where to add auto-calculation?
- Option A: In /kb command (calculate once, pass to all subsequent operations)
- Option B: In /sm directive (calculate before calling log_session)
- Option C: In log_session tool (auto-calculate if not provided)

Recommendation: Option B (/sm directive) - keeps calculation visible in workflow, allows manual override if needed for recovery.

---

*KB Entry: `arlo-pattern-session-number-calculation` | Category: pattern | Updated: 2025-11-22*
