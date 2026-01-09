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

Analyze access patterns from `accumulator-kb-access`:
```sql
-- Parse access log: SESSION|OP|id1,id2,id3
SELECT id, COUNT(*) as loads FROM (
  SELECT UNNEST(STRING_SPLIT(SPLIT_PART(line, '|', 3), ',')) as id
  FROM (SELECT UNNEST(STRING_SPLIT(content, E'\n')) as line
        FROM knowledge WHERE id = 'accumulator-kb-access')
) GROUP BY id ORDER BY loads DESC
```

Cross-reference with current mode tags:
- Frequently loaded but not `mode-{x}-load`? → Suggest tagging
- Tagged `mode-{x}-load` but rarely accessed? → Maybe demote to `mode-{x}`
- Never loaded but seems relevant? → Surface for discussion

Mode hierarchy:
- `mode-{mode}-load`: Auto-loads on `/open {mode}` - keep small, high-value
- `mode-{mode}`: Offered for selection - broader, optional
- Untagged: Loaded via search or explicit request only

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
