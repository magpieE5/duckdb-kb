# /open [MODE...]

Load session context. Accepts zero or more modes (e.g., `/open`, `/open work`, `/open work idr`).

**Modes:** $ARGUMENTS

## Execution

**SEQUENTIAL, NOT PARALLEL.** Order matters - foundations before state before history. Do not batch or parallelize these steps.

### Core Context (always)

0. Get current date/time and session number: `./venv/bin/python tools/session_details.py --date_display` and `./venv/bin/python tools/session_details.py --session_number`
1. `set_session({"session": N})` - enable KB access logging for this session
2. Pull shared repos: `./venv/bin/python tools/shared_repos.py pull`
3. Import all markdown directories to KB:
   ```
   import_from_markdown({"input_dir": "markdown/"})
   ```
   Ensures any shared/exported content is loaded (idempotent upsert).
4. `get_knowledge({"where": "id IN ('seed-arlo-foundations', 'seed-duckdb-kb-mcp-architecture', 'seed-team-kb-sharing') OR id LIKE 'seed-template-%'"})` - core seeds + templates
5. `get_knowledge({"where": "id LIKE 'reference-%-foundations'"})` - personal context
6. **Load history (logs + transcripts) based on mode:**
   - Determine mode: use first mode from arguments, else "default"
   - Query `./open-config.csv` for depths:
     ```sql
     SELECT transcript_depth, log_depth FROM read_csv_auto('./open-config.csv') WHERE mode = '{mode}'
     ```
   - **Load logs first** if log_depth > 0:
     - Query logs with OFFSET to skip transcript range:
       ```sql
       SELECT id FROM knowledge WHERE category = 'log' ORDER BY updated DESC LIMIT {log_depth} OFFSET {transcript_depth}
       ```
     - Load via `get_knowledge` **in reverse order** (oldest first, newest last)
   - **Then load transcripts** if transcript_depth > 0:
     - Query newest N transcripts:
       ```sql
       SELECT id FROM knowledge WHERE category = 'transcript' ORDER BY updated DESC LIMIT {transcript_depth}
       ```
     - Load via `Read` on `markdown/transcript/{id}.md` **in reverse order** (oldest first, newest last)
     - Note: Use Read instead of get_knowledge to bypass 25k character limit on large transcripts
   - **Result:** Chronological history from oldest to newest (logs → transcripts)
7. `get_knowledge({"where": "id = 'state-arlo'"})` - relationship/attention state
8. `get_knowledge({"where": "id = 'accumulator-corrections'"})` - corrections
9. `get_knowledge({"where": "category = 'todo'"})` - todo lists

---

### Route After Core Context

**CHECKPOINT - Route based on mode arguments:**
- Modes specified in command → Go to "Mode Loading" section
- No modes specified → Go to "Mode Selection" section

**Do NOT skip to "Finally..." until mode processing is complete.**

---

### Mode Selection (if no modes specified)

If `/open` called with no arguments, show available modes:

```sql
SELECT DISTINCT mode FROM read_csv_auto('./kb-mode.csv') ORDER BY mode
```

Display as numbered list:

```
Available modes:
1. personal
2. work

Select mode (1-N | none):
```

**STOP HERE. Wait for user response before proceeding.**

- If user selects a mode, proceed to "Mode Loading" section with that mode
- If user says "none", skip to "Finally..." section

---

### Mode Loading (if modes specified or selected)

#### Step 1: Load mode config

```sql
SELECT m.mode, m.is_auto, m.id, k.id IS NOT NULL as exists
FROM read_csv_auto('./kb-mode.csv') m
LEFT JOIN knowledge k ON m.id = k.id
WHERE m.mode IN ({modes})
ORDER BY m.is_auto DESC, m.id
```

Warn about any rows where `exists = false`.

#### Step 2: Auto-load entries

**CRITICAL: Load entries where `is_auto=true` for the specified modes.**

Use `get_knowledge` - **ONE ENTRY AT A TIME** (separate tool calls, not in parallel).

**DO NOT PROCEED to Step 3 until all auto-load entries are loaded.**

#### Step 3: **REQUIRED OUTPUT FORMAT** - Display loaded + offer selection

**EXCEPTION: If mode is `auto`, skip this step entirely and proceed to "Finally..." section. Auto mode operates autonomously - no user interaction.**

For all other modes, you MUST output in this format before waiting:

```
**Auto-loaded ({mode}):**
- {id-1}
- {id-2}
- ...

**Available for selection:**
| # | id |
|---|----|
| 1 | {id} |
| 2 | {id} |
...

Load which? (e.g., 1-3 | all | none)
```

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

Mode configuration lives in `./kb-mode.csv`:

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

---

## History Loading Configuration

History depth configuration lives in `./open-config.csv`:

```csv
mode,transcript_depth,log_depth
default,0,3
work,0,3
personal,0,3
auto,3,10
```

- `transcript_depth` - number of recent transcripts to load (full verbatim exchanges)
- `log_depth` - number of session logs to load (summaries with preview/witness/handoff)
- Logs loaded first (older history), then transcripts (recent history)
- Both loaded chronologically: oldest first, newest last
- Log query uses OFFSET={transcript_depth} to skip transcript range

**Example for auto mode** (transcript_depth=3, log_depth=10):
- Loads sessions 81-93
- Sessions 81-90: logs (summaries)
- Sessions 91-93: transcripts (full verbatim)
- Total: 13 sessions of chronological history
