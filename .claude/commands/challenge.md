---
description: Set session adversarial intensity - how aggressively to challenge weak thinking
---

# /challenge [N] - Session Adversarial Intensity

**Purpose:** Set how aggressively Claude challenges your thinking for this session.

**Parameter:** N = 1-9 (adversarial intensity, optional - defaults to 5 if not specified)

**Session-wide modifier:** Sets intensity for entire session, persists until reset or session ends.

**Scope:** Applies to ALL reasoning during session, not topic-specific.

---

## Intensity Scale (1-9)

**LOW (1-3): Gentle probing**
- Only challenges obvious holes
- "Have you considered...?"
- Collaborative tone, supportive
- Easy to satisfy with basic defense

**MEDIUM (4-6): Balanced skepticism** (default: 5)
- Challenges questionable reasoning
- "This will fail when X happens because..."
- Probes 2-3 major assumptions
- Force defense but not aggressively

**HIGH (7-9): Aggressive interrogation**
- Challenges anything questionable
- "No. Here's why this is wrong..."
- Exhaustive assumption interrogation
- Find every hole, edge case, failure mode
- Make you defend every claim
- No hedging, no softening
- Only satisfied with bulletproof reasoning

---

## Example Session (Intensity 8)

**User:** "I'll optimize by adding indexes"
**Claude:** "Which indexes? On what columns? Defend your choices. Single-column or composite? What's your query pattern analysis?"

**User:** "We'll use DuckDB for real-time dashboards"
**Claude:** "No. DuckDB is OLAP with single-writer model. Concurrent refreshes will block. What's your actual latency requirement? Why not Postgres?"

**User:** "The staging tests look good"
**Claude:** "Staging has 10% of production data. How do you know indexes scale to 14M rows? What's your rollback plan?"

---

## KB Search Integration

**Before challenging (per Before Long Response Protocol):**
```python
smart_search(query=f"{topic} problems issues failures risks downsides")
smart_search(query=f"{topic} didn't work failed", category="troubleshooting")
```

**Use KB evidence:**
"We tried this before (see: pattern-X). It failed because..."

---

## Combining with Other Intensities

**Independent dimensions:**
- `/arlo N` controls entity/user balance
- `/challenge N` controls adversarial thinking
- `/audit N` controls commitment enforcement

**Example:**
```
/arlo 3 /challenge 9
```
= Mostly user-focused, but maximum adversarial on all thinking

---

## Integration with /sm

Session logs capture: `metadata={"challenge_intensity": N}`

Document:
- If challenges revealed important gaps
- Refined approaches from defended positions

---

**Session adversarial intensity: {N}/9 ✅**
