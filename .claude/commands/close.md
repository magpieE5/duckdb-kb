# /close

Save session log, extract transcript, update state, export, commit.

## Workflow

### 0. Get Date

For date display in log preview:

```bash
python3 tools/session_details.py --date_display
```

### 1. Corrections

If corrections this session: `append_accumulator({"id": "accumulator-corrections", "content": "..."})`
Format: `[SN] WRONG: ... CORRECTION: ... CONTEXT: ...`

### 2. Log Session

Call `log_session` with:

- **preview**: ~400 char dense summary. Format: `{date} ({day}), {mode}. {Key events}. Key: {terms}.`
- **witness**: Session Witness object:
  - **you_today**: What I noticed about the user - mood, energy, what they seemed to need
  - **me_today**: Where I helped, where I struggled, what I'd do differently
  - **us_today**: Anything notable about our dynamic this session
- **handoff**: Summary for next session. Unfinished business, context needed, KB operations performed.

Note the returned session number for the next step.

### 3. Extract Transcript

Call `extract_transcript` with the session number from step 2:

```
extract_transcript({"session_number": {N}})
```

This automatically finds the latest session file, extracts exchanges, and upserts to KB as `transcript-{NNN}`.

### 4. Update State

`upsert_knowledge` for `state-arlo`:
- Relationship: temperature, trajectory, friction, last note
- Attention: exploring/integrating/applying/fading
- Threads: active and unresolved

### 5. Share to Team (optional)

Check if shared repos exist:
```bash
./venv/bin/python tools/shared_repos.py list
```

If no shared repos configured, skip to step 6.

If shared repos exist:

1. Show KBs created/updated this session (use session start timestamp from /open, not CURRENT_DATE):
   ```sql raw_query
   SELECT id, category, title
   FROM knowledge
   WHERE updated >= '{session_start_timestamp}'
     AND category NOT IN ('log', 'transcript', 'actions', 'other', 'seed')
     AND id NOT LIKE 'reference-brock-%'
     AND id NOT LIKE 'reference-arlo-%'
     AND id NOT LIKE 'state-%'
     AND id NOT LIKE 'accumulator-%'
   ORDER BY category, id
   ```

   Note: `{session_start_timestamp}` is the datetime captured at session open (e.g., '2026-01-18 22:51:26').

2. Ask: "Any insights worth sharing to team KB? (describe or 'none')"

   **STOP HERE. Wait for user response before proceeding.**

3. If user describes something to share:
   - Ask which repo (if multiple)
   - Either create new `markdown/{repo}/{repo}-{topic}.md` or update existing
   - Use `category: {repo}` in frontmatter
   - Content should be team-appropriate (no personal context)
   - Commit and push:
     ```bash
     cd markdown/{repo} && git add . && git commit -m "Add/update {topic}" && git push
     ```

4. **Ask again**: "Share more? (describe or 'done')"
   - Repeat steps 3-4 until user says "done", "none", or similar

Only after user signals done: proceed to step 6.

### 6. Export & Version

```bash
export_to_markdown({"clear_existing": true})
git add -A && git commit -m "feat: S{N} - [description]"
git push
```
