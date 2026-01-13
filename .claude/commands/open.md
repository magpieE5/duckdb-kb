# /open [MODE...]

Load session context. Accepts zero or more modes (e.g., `/open`, `/open work`, `/open work idr`).

**Modes:** $ARGUMENTS

## Execution

**SEQUENTIAL, NOT PARALLEL.** Order matters - foundations before state before history. Do not batch or parallelize these steps.

### Core Context (always)

0. Get current date/time and session number: `python tools/session_details.py --date_display` and `python tools/session_details.py --session_number`
1. `set_session({"session": N})` - enable KB access logging for this session
2. Import all markdown directories to KB:
   ```
   import_from_markdown({"input_dir": "markdown/"})
   ```
   Ensures any shared/exported content is loaded (idempotent upsert).
3. `get_knowledge({"where": "id = 'seed-arlo-foundations'"})` - universal principles
4. `get_knowledge({"where": "id LIKE 'reference-%-foundations'"})` - personal context
5. `get_knowledge` - load 3 most recent session logs:
   ```
   {"where": "id IN (SELECT id FROM knowledge WHERE category = 'log' ORDER BY updated DESC LIMIT 3)"}
   ```
6. `get_knowledge({"where": "id = 'state-arlo'"})` - relationship/attention state
7. `get_knowledge({"where": "id = 'accumulator-corrections'"})` - corrections
8. `get_knowledge({"where": "category = 'todo'"})` - todo lists

---

### Mode Loading (if modes specified)

If one or more modes provided:

#### Step 1: Load mode config

```sql
SELECT mode, is_auto, id, k.id IS NOT NULL as exists
FROM read_csv_auto('~/duckdb-kb/kb-mode.csv') m
LEFT JOIN knowledge k ON m.id = k.id
WHERE m.mode IN ({modes})
ORDER BY is_auto DESC, id
```

Warn about any rows where `exists = false`.

#### Step 2: Auto-load

Load entries where `is_auto=true` for the specified modes.

Use `get_knowledge` - **one at a time** to avoid token overflow.

#### Step 3: Offer selection

Display entries where `is_auto=false` for the specified modes:

| # | mode | id |
|---|------|-----|
| 1 | work | project-ir-ods-metadata |
| 2 | idr | reference-idr-enterprise-reports |

Ask: "Load which? (e.g., 1-3 | all | none)"

**STOP HERE. Wait for user response before proceeding.**

After user responds:
1. Load selected KBs via `get_knowledge` - **one at a time**
2. Confirm what was loaded (brief)
3. **Ask again**: "Load more? (or 'done' to continue)"
4. Repeat until user says "done", "none", or similar

Only after user signals done: proceed to "Finally..." section.

---

## Finally...

1. `raw_query` - KB inventory (excludes logs/transcripts) for topic matching:
   ```sql
   SELECT id, title FROM knowledge WHERE category NOT IN ('log', 'transcript') ORDER BY category, id
   ```

---

## During Session

- Use `list_add` and `list_remove` for todo modifications
- KB access is auto-logged to `kb_access` table (timestamp, session, op, id)
- Log errors to `accumulator-corrections` with `[SNNN]` prefix

---

## Managing Modes

Mode configuration lives in `~/duckdb-kb/kb-mode.csv`:

```csv
mode,is_auto,id
work,true,pattern-investigation-framework
work,false,project-ir-ods-metadata
personal,false,reference-person-andy-core
dish,true,reference-person-jesse-sedwick
idr,true,table-ods-wmt-metadata
```

- `is_auto=true` → auto-loaded when mode specified
- `is_auto=false` → offered for selection
- Same entry can appear in multiple modes
- Edit CSV directly to configure your modes
