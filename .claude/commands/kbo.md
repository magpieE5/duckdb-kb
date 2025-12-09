# /kbo [MODE]

Load session context. MODE: normal | auto (default: normal)

## Execution

1. `list_knowledge()`
2. **If Total Entries = 0:** Run `import_from_markdown({"input_dir": "markdown/"})` and report count
3. `get_knowledge({"where": "id = 'reference-arlo-foundations'"})` to load foundations
4. `raw_query` to get previews of logs 6-10 (recent history, not fully loaded):
   ```sql
   SELECT id, title, LEFT(content, 400) as preview FROM (
     SELECT id, title, content, updated FROM knowledge
     WHERE category = 'log'
     ORDER BY updated DESC
     LIMIT 10 OFFSET 5
   ) ORDER BY updated ASC
   ```
5. `raw_query` to get 5 most recent log IDs in chronological order:
   ```sql
   SELECT id FROM (
     SELECT id, updated FROM knowledge
     WHERE category = 'log'
     ORDER BY updated DESC
     LIMIT 5
   ) ORDER BY updated ASC
   ```
6. Load each log from step 5 individually via `get_knowledge` in the order returned (oldest to newest)
7. `get_knowledge({"where": "id = 'accumulator-corrections'"})` to load corrections
8. `get_knowledge({"where": "category = 'todo'"})` to load todo lists

Track KB operations (create, update, delete, get_knowledge reads) during session for `kb_operations` field at close.

1. `scan_knowledge` for keywords
2. If no results: `WebSearch` for keywords

**auto mode:** User absent. No questions, no approval requests. Work autonomously, proceed immediately.
