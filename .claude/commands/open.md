# /open [MODE]

Load session context. MODE: normal | work | personal | dish (default: normal).

**Mode:** $ARGUMENTS

## Execution: normal (base for all modes)

**SEQUENTIAL, NOT PARALLEL.** Order matters - foundations before state before history. Do not batch or parallelize these steps.

0. Get current date/time and session number: `./venv/bin/python tools/session_details.py --date_display` and `./venv/bin/python tools/session_details.py --session_number`
1. `set_session({"session": N})` - enable KB access logging for this session
2. `get_knowledge({"where": "id = 'seed-arlo-foundations'"})` - universal principles
3. `get_knowledge({"where": "id LIKE 'reference-%-foundations'"})` - personal context
4. `get_knowledge` - load 3 most recent session logs:
   ```
   {"where": "id IN (SELECT id FROM knowledge WHERE category = 'log' ORDER BY updated DESC LIMIT 3)"}
   ```

5. `get_knowledge({"where": "id = 'state-arlo'"})` - relationship/attention state
6. `get_knowledge({"where": "id = 'accumulator-corrections'"})` - corrections
7. `get_knowledge({"where": "category = 'todo'"})` - todo lists

---

## Mode: work | personal | dish

After normal execution:

### Step 1: Auto-load core mode KBs

Load all `mode-{MODE}-load` tagged entries automatically:

```sql
SELECT id, title FROM knowledge WHERE 'mode-{MODE}-load' = ANY(tags) ORDER BY category, id
```

Load each via `get_knowledge` - **one at a time** to avoid token overflow.

### Step 2: Offer selective loading of additional mode KBs

Query remaining `mode-{MODE}` tagged entries (not `-load`):

```sql
SELECT id, title FROM knowledge WHERE 'mode-{MODE}' = ANY(tags) AND NOT ('mode-{MODE}-load' = ANY(tags)) ORDER BY category, id
```

If results exist, display numbered table with titles, ask: "Load which? (e.g., 1-3 | all | none)"

**STOP HERE. Wait for user response before proceeding.**

After user responds:
1. Load selected KBs via `get_knowledge` - **one at a time**
2. Confirm what was loaded (brief)
3. **Ask again**: "Load more? (or 'done' to continue)"
4. Repeat until user says "done", "none", or similar

Only after user signals done: proceed to "Finally..." section.

**dish tone:** Warm, playful, opinionated. Match energy. No hedging. Push back. Banter welcomed.

---

## Finally...

1. `raw_query` - KB inventory (excludes logs/transcripts) for topic matching:
   ```sql
   SELECT id, title FROM knowledge WHERE category NOT IN ('log', 'transcript') ORDER BY category, id
   ```

---

## During Session

- Use `todo_add` and `todo_complete` for todo modifications
- KB access is auto-logged to `accumulator-kb-access` (format: `SESSION|OP|ids`)
- Log errors to `accumulator-corrections` with `[SNNN]` prefix
- To add a KB to a mode:
  - `mode-{mode}-load` tag → auto-loaded on `/open {mode}`
  - `mode-{mode}` tag → offered for selection on `/open {mode}`
