# /kbc

Save session log, export markdown, commit.

## Workflow

1. `get_knowledge({"where": "id = 'pattern-session-log-conventions'"})` - load logging conventions
2. Calculate next session number from existing logs
3. Call `log_session` with conversation dump, applying conventions:
   - Quote User's exact words for corrections, decisions, emotional moments
   - Show iteration, not just outcomes
   - Note rejected approaches
4. `export_to_markdown()`
5. `git add -A && git commit -m "feat: S{N} - [brief description]"`
6. `git push` (silent fail OK - if fails, note "⚠️ Push failed - commit local only" in summary)
