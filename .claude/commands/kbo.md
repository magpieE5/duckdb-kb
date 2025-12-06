# /kbo [MODE]

Load session context. MODE: normal | auto (default: normal)

## Execution

1. `get_stats({"detailed": True})`
2. **If Total Entries = 0:** Run `import_from_markdown({"input_dir": "markdown/"})` and report count
3. `get_knowledge({"where": "category = 'todo'"})` to load todo lists
4. `scan_knowledge({"where": "category = 'log'", "limit": 10})` to get last 10 log previews
5. Load last 5 logs in full via `get_knowledge`
6. `get_knowledge({"where": "id = 'reference-arlo-foundations'"})` to load foundations in full

Track KB operations (create, update, delete, get_knowledge reads) during session for `kb_operations` field at close.

1. `scan_knowledge` for keywords
2. If no results: `WebSearch` for keywords

**auto mode:** User absent. No questions, no approval requests. Work autonomously, proceed immediately.
