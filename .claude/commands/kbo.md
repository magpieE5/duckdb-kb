# /kbo [MODE]

Load session context. MODE: normal | auto (default: normal)

## Execution

1. `get_stats({"detailed": True})`
2. `get_knowledge({"where": "category = 'todo'"})` to load todo lists
3. `scan_knowledge({"where": "category = 'log'"})` to get log IDs
4. Take the **last 10** log IDs (most recent by updated timestamp)
5. For each ID, `get_knowledge({"where": "id = '{id}'"})` in order

Track KB operations (create, update, delete, get_knowledge reads) during session for `kb_operations` field at close.

**auto mode:** User absent. No questions, no approval requests. Work autonomously, proceed immediately.
