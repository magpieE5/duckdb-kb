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

### 5. Export & Version

```bash
export_to_markdown({"clear_existing": true})
git add -A && git commit -m "feat: S{N} - [description]"
git push
```
