# Session Loading Protocol

**Purpose:** Load session context at /kb initialization for narrative continuity.

---

## Load Context Entries (Step 5)

Load all 4 context entries for session:

```python
user_current = get_knowledge({"id": "user-current-state"})
user_bio = get_knowledge({"id": "user-biographical"})
arlo_current = get_knowledge({"id": "arlo-current-state"})
arlo_bio = get_knowledge({"id": "arlo-biographical"})
```

No output - silently loaded.

---

## Load Recent Session Logs (Step 5.5)

Load last 3 comprehensive session logs for narrative continuity (newest to 3rd newest):

**Query last 3 session logs:**
```python
query_knowledge({
    "sql": "SELECT id, title FROM knowledge WHERE category='log' AND id LIKE 'arlo-log-s%-session' ORDER BY updated DESC LIMIT 3"
})
```

**Load all 3 logs:**
```python
# For each log ID returned above
get_knowledge({"id": "arlo-log-s5-session"})
get_knowledge({"id": "arlo-log-s4-session"})
get_knowledge({"id": "arlo-log-s3-session"})
# etc.
```

**Session log structure:** Single comprehensive log per session containing both user and entity perspectives, topics discussed, key exchanges, realizations, web research, and next session planning.

**No output** - available for session context, provides narrative continuity.

---

## DuckDB Array Query Syntax

**Correct syntax for array columns:**

```sql
-- Use list_has_any() for array membership
WHERE list_has_any(tags, ['tag1', 'tag2'])

-- NOT this (will fail):
WHERE tags LIKE '%tag1%'
```

**Why:** `tags` column is `VARCHAR[]` type, not string. LIKE operator only works on strings.

---

**Related:**
- See continuity/overview.md for continuity architecture
- See reference/query-routing.md for query patterns
