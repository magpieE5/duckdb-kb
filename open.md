# open [MODE]

Load session context. MODE: normal | auto (default: normal)

---

## Execution:

0. Get current date/time: `python3 tools/session_details.py --date_display`
1. `get_knowledge({"where": "id LIKE 'seed-%-foundations'"})` - universal principles
2. `get_knowledge({"where": "id LIKE 'reference-%-foundations'"})` - personal context
3. `get_knowledge({"where": "id = 'state-arlo'"})` - relationship/attention state
4. `raw_query` - previews of logs 8-10 (older history):
   ```sql
   SELECT id, title, LEFT(content, 400) as preview FROM (
     SELECT id, title, content, updated FROM knowledge
     WHERE category = 'log'
     ORDER BY updated DESC
     LIMIT 3 OFFSET 7
   ) ORDER BY updated ASC
   ```
5. `get_knowledge` - load logs 1-7 fully:
   ```
   {"where": "id IN (SELECT id FROM knowledge WHERE category = 'log' ORDER BY updated DESC LIMIT 7)"}
   ```
6. Load most recent transcript:
   ```sql
   raw_query({"sql": "SELECT id, title, content FROM knowledge WHERE category = 'transcript' ORDER BY id DESC LIMIT 1"})
   ```
7. `get_knowledge({"where": "id = 'accumulator-corrections'"})` - corrections
8. `get_knowledge({"where": "category = 'todo'"})` - todo lists

---

## Mode: auto

Work autonomously. No questions, no approval requests. Proceed immediately.

---

## During Session

- Use `todo_add` and `todo_complete` for todo modifications
- Track KB operations (create, update, delete, get_knowledge reads) for handoff at close
