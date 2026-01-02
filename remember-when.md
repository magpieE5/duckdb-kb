# remember-when <query>

Search transcripts for past exchanges. Finds when we discussed a topic.

## Execution

```
scan_knowledge({
  "query": "{query}",
  "where": "category = 'transcript'",
  "include_transcripts": true,
  "limit": 10
})
```

For each match, show:
- Session number (from id: transcript-NNN)
- Preview of matching content
- Offer to load full transcript if user wants details

## Example

User: `remember-when CFM batch`

Response:
- **Session 92** (Dec 23): "IDR-3595 PEREHIS restored to CFM..."
- **Session 86** (Dec 22): "IDR-3791 complete, RView+CFM..."

"Want me to load the full transcript for any of these?"
