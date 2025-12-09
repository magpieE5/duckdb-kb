# /kbc

Save session log, export markdown, commit.

## Workflow

1. `get_knowledge({"where": "id = 'pattern-session-log-conventions'"})` - load logging conventions
2. **If any corrections occurred this session:** Update `accumulator-corrections` with new entries (format: `[SN] WRONG: ... CORRECTION: ... CONTEXT: ...`)
3. Calculate next session number from existing logs
4. Call `log_session` with conversation_dump, internal_dialogue, handoff:
   - conversation_dump starts with ~400 char preview (critical for searchability)
   - Quote User's exact words for corrections, decisions, emotional moments
   - Show iteration, not just outcomes
   - Note rejected approaches
   - Tags: `["session", "session-N"]` (additional tags optional)
5. `export_to_markdown()`
6. `git add -A && git commit -m "feat: S{N} - [brief description]"`
7. `git push` (silent fail OK - if fails, note "⚠️ Push failed - commit local only" in summary)
