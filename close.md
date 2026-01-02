# close

Save session log, extract transcript, update state, export, commit.

## Workflow

### 0. Get Session Details (cross-platform, client-agnostic)

Run first to get paths:

```bash
python3 tools/session_details.py
```

Key fields:
- `client`: 'claude' or 'gemini' (auto-detected)
- `latest_session`: Path to most recent session file
- `extract_cmd`: Pre-built extraction command

Use these values below.

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

Upsert verbatim transcript to KB for `remember-when.md` FTS.

**Step 3a:** Run extractor to get JSON output:

```bash
{extract_cmd} "{latest_session}" {session_number}
```

Replace `{session_number}` with the number from step 2 (e.g., `114`).

The script outputs JSON to stdout with `id`, `category`, `title`, `tags`, `content`.

**Step 3b:** Call `upsert_knowledge` with the JSON values:

```
upsert_knowledge({
  "id": "transcript-{NNN}",
  "category": "transcript",
  "title": "Session {NNN} Transcript",
  "tags": ["transcript", "session-{NNN}"],
  "content": <content from script output>
})
```

This ensures the transcript goes through MCP and is immediately visible (not just persisted to parquet).

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
