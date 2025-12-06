# /kbs <topic>

Search KB for topic. Auto-loads never-forget tagged entries fully.

## Execution

1. `scan_knowledge` for topic
2. If no results: `WebSearch` for topic
3. `get_knowledge` for any matches tagged `never-forget` (load full content)
