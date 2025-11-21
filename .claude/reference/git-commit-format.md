# Git Commit Format

When creating git commits (via git_commit_and_get_sha MCP tool or manually), use this format:

```
<type>: <short description>

<detailed explanation if needed>

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Types:** `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

**Examples:**
- `feat: Add pattern for API error handling`
- `fix: Correct SQL query in log aggregation`
- `docs: Document KB duplicate detection protocol`
- `refactor: Consolidate authentication entries`
