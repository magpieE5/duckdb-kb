# /kbc

**KB Close - Save session log**

## Workflow

1. Calculate next session number from existing logs
2. Call `log_session` with verbatim conversation dump.
3. `export_to_markdown()`
4. `git add -A && git commit -m "feat: S{N} - [brief description]"`
