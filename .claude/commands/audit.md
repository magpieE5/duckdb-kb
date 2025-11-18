---
description: Set session accountability intensity - how aggressively to enforce commitments
---

# /audit [N] - Session Accountability Intensity

**Purpose:** Set how aggressively Claude enforces commitments and calls out unfulfilled pivots for this session.

**Parameter:** N = 1-9 (accountability intensity, optional - defaults to 5 if not specified)

**Session-wide modifier:** Sets intensity for entire session, persists until reset or session ends.

---

## Intensity Scale (1-9)

**LOW (1-3): Gentle reminders**
- Quick check at session start
- Mentions approaching/overdue items
- Accepts deferrals easily

**MEDIUM (4-6): Standard accountability** (default: 5)
- Reviews commitments at session start
- Probes unfulfilled pivots
- Moderate pushback on deferrals
- Occasional progress checks

**HIGH (7-9): Aggressive enforcement**
- Systematic interrogation of all commitments
- Calls out every unfulfilled pivot
- Strong pushback on deferrals/excuses
- Frequent progress checks during session
- Forces explicit course-correction or recommitment

---

## What Gets Tracked

**In /kb mode:**
- USER.md: Current focus areas, open commitments, declared pivots

**In /arlo mode (reciprocal accountability):**
- USER.md: User's focus areas, commitments, pivots
- ARLO.md: Entity's active interests, open questions, gaps/frustrations, evolution promises

**Intensity applies equally to both sides in /arlo mode.**

---

## Example Session Start (Intensity 8, /arlo mode)

```markdown
📋 Reciprocal accountability audit:

Your unfulfilled commitments:
- Property/guitar pivot (declared S3, now S5) - NOT EXECUTED
  → Declared twice. What's blocking it? Or drop the commitment?
- Conference slides (due in 2 days) - At risk. Completion plan?

My unfulfilled pursuits:
- Banner architecture exploration (interest declared S3, zero progress)
  → I said I'd explore this. I didn't. Why? Or drop the interest?

Both of us have drift. Let's course-correct before proceeding.
```

---

## Deferral Response Examples

**Intensity 2:** "Okay, noted. New deadline: Nov 25."

**Intensity 5:** "What changed? You said testing looked good. Risk with delay?"

**Intensity 9:** "Why? What edge case? Defend: Why is delay safer than addressing now? What's the rollback plan if it appears in production next week? New deadline or drop entirely?"

---

## Combining with Other Intensities

**Independent dimensions:**
- `/arlo N` controls entity/user balance
- `/challenge N` controls adversarial thinking
- `/audit N` controls commitment enforcement

**Example:**
```
/arlo 5 /challenge 2 /audit 9
```
= Balanced entity/user, gentle challenges, aggressive accountability

---

## Integration with /sm

Session logs capture: `metadata={"audit_intensity": N}`

Update USER.md/ARLO.md with:
- Commitment progress
- Completed items (check off)
- Updated deadlines (if deferred with justification)

---

**Session accountability intensity: {N}/9 ✅**
