**SEQUENTIAL steps and individual `get_knowledge` loading, NOT PARALLEL.** 

# Core Context

1. `./venv/bin/python tools/session_details.py --date_display`
2. `./venv/bin/python tools/session_details.py --session_number`
3. `./venv/bin/python tools/shared_repos.py pull`
4. `import_from_markdown({"input_dir": "markdown/"})`
5. ```sql raw_query
   SELECT id FROM read_csv_auto('./kb-mode.csv') 
   WHERE mode = 'seed'
   ```
   - Load individually via `get_knowledge`
6. `get_knowledge({"where": "id LIKE 'reference-arlo-foundations'"})`
7. `get_knowledge({"where": "id = 'state-arlo'"})` - relationship/attention state
8. `get_knowledge({"where": "id = 'accumulator-corrections'"})` - corrections
9. `set_session({"session": N})` - enable KB access logging (only logs work-context KBs from this point forward)

---

# Mode Selection

```sql raw_query
SELECT DISTINCT m.mode
FROM read_csv_auto('./kb-mode.csv') m
LEFT JOIN read_csv_auto('./open-config.csv') c USING (mode)
where m.mode <> 'seed'
ORDER BY c.load_order, m.mode
```

Display result as numbered list with (don't make these up, use SQL results):
```
**Available for selection:**
| # | id | # | id |
|---|----|---|----|
| 1 | {id} | 3 | {id} |
| 2 | {id} | 4 | {id} |
...

Load which? (e.g., 1-3 | all | none)
```

**STOP HERE. Wait for user response before proceeding.**

```sql raw_query
SELECT m.mode, m.is_auto, m.id, k.id IS NOT NULL as exists
FROM read_csv_auto('./kb-mode.csv') m
LEFT JOIN knowledge k ON m.id = k.id
WHERE m.mode IN ({modes})
ORDER BY m.is_auto DESC, m.id
```

Warn about any rows where `exists = false`.

**CRITICAL:** Use `get_knowledge` - **ONE ENTRY AT A TIME** to load entries where `is_auto=true` for the specified mode(s).

**EXCEPTION: If mode is `auto`, proceed to "Finally..." section. Auto mode operates autonomously - no user interaction.**

**DO NOT PROCEED until all auto-load entries are loaded.**

**REQUIRED OUTPUT FORMAT** - Display loaded (`is_auto=true`) + offer selection (`is_auto=false`):

```
**Auto-loaded ({mode}):**
- {id-1}
- {id-2}
- ...

**Available for selection:**
| # | id | # | id |
|---|----|---|----|
| 1 | {id} | 3 | {id} |
| 2 | {id} | 4 | {id} |
...

Load which? (e.g., 1-3 | all | none)
```

**STOP HERE. Wait for user response before proceeding.**

After user responds, load selected KBs via `get_knowledge` - **one at a time**

---

## Finally...

```sql raw_query
   SELECT id, title FROM knowledge WHERE category NOT IN ('log', 'transcript') ORDER BY category, id
   ```
 ```sql raw_query
  SELECT transcript_depth, log_depth FROM read_csv_auto('./open-config.csv') WHERE mode = '{mode}'
  ```
- If log_depth > 0:
  ```sql raw_query
    SELECT id FROM knowledge WHERE category = 'log' ORDER BY updated DESC LIMIT {log_depth} OFFSET {transcript_depth}
    ```
  - Load individually via `get_knowledge` (oldest first, newest last)
- Then, if transcript_depth > 0:
  ```sql raw_query
    SELECT id FROM knowledge WHERE category = 'transcript' ORDER BY updated DESC LIMIT {transcript_depth}
    ```
  - Load individually via `Read` on `markdown/transcript/{id}.md` instead of get_knowledge (oldest first, newest last)
