# /audit

KB health check and curation.

## Execution

Run all checks, surface top issues for discussion.

**1. Stats**
- Entry count by category
- Recent updates
- Largest entries

**2. Staleness**
- Entries not updated in 30+ days that aren't reference material

**3. Orphans**
- Entries with no tags, or tags that match nothing else

**4. Fragmentation**
- Similar titles/content that could be consolidated

**5. Mode hygiene**

Analyze access patterns from `kb_access` table:
```sql raw_query
-- Top loaded entries (last 30 days)
SELECT id, COUNT(*) as loads
FROM kb_access
WHERE op = 'get' AND timestamp >= CURRENT_DATE - 30
GROUP BY id
ORDER BY loads DESC
LIMIT 20

-- Entries loaded but not in any mode
SELECT a.id, a.loads
FROM (SELECT id, COUNT(*) as loads FROM kb_access WHERE op = 'get' GROUP BY id) a
LEFT JOIN read_csv_auto('./kb-mode.csv') m ON a.id = m.id
WHERE m.id IS NULL AND a.loads >= 5
ORDER BY a.loads DESC
```

Cross-reference with `kb-mode.csv`:
- Frequently loaded but not in any mode? → Consider adding to relevant mode
- In mode with `is_auto=true` but rarely accessed? → Maybe demote to `is_auto=false`
- Never loaded but `is_auto=true`? → Wasted context, demote or remove

Mode configuration (`kb-mode.csv`):
- `is_auto=true`: Auto-loads on `/open {mode}` - keep small, high-value
- `is_auto=false`: Offered for selection after auto-load
- Not in CSV: Loaded via search or explicit request only

**6. Corrections**

Load `accumulator-corrections`. For each:
- What was wrong?
- Is the source KB entry still wrong, or was it fixed?
- Is this a pattern (how I fail) or a fact (what's true)?
- If pattern: discuss, then delete - the conversation is the fix
- If fact: update the source KB, then delete the correction

Goal: empty accumulator.

**7. Logs**

Load recent 5 session logs. Look for:
- Recurring handoff items that never resolve → Might need a project entry
- Repeated witness themes → Pattern worth capturing
- KB entries mentioned across multiple sessions → Mode candidates

---

## How to work through issues

1. **Surface** - Query and display issues
2. **Discuss** - One issue at a time
3. **Fix** - Update KB in-session, don't defer
4. **Verify** - Confirm fix addresses the issue
5. **Next** - Move to next issue or close

A thorough audit of 3 issues beats a shallow pass over 30.
