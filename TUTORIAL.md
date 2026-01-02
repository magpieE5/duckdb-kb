# Full Tutorial: Clone → Session 11

A detailed walkthrough from fresh install to steady-state operation. Works with any MCP-compatible client (Claude Code, Gemini CLI, Ollama via mcp-client).

---

## Day 0: Fresh Install

### 1. Create Your Repo

On GitHub: **Use this template** → **Create a new repository**
- Name: `duckdb-kb`
- Visibility: **Private** (recommended — this will contain personal context)

### 2. Clone

```bash
# macOS / Linux / Codespaces
git clone https://github.com/YOUR_USERNAME/duckdb-kb.git ~/duckdb-kb
cd ~/duckdb-kb
```

```powershell
# Windows
git clone https://github.com/YOUR_USERNAME/duckdb-kb.git $env:USERPROFILE\duckdb-kb
cd $env:USERPROFILE\duckdb-kb
```

### 3. Install your MCP client

**Claude Code:**
```bash
curl -fsSL https://claude.ai/install.sh | bash
```

**Gemini CLI:**
```bash
npm install -g @google/gemini-cli
```

**Ollama:** See [mcp-client-for-ollama](https://github.com/nicobailey/mcp-client-for-ollama)

### 4. Start your client

```bash
claude    # or: gemini
```

### 5. Run setup

```
Read setup.md and execute it
```

**What setup.md does:**
- Creates Python venv, installs dependencies (duckdb, mcp, pyyaml)
- Adds MCP server to your client's config
- Copies templates from `markdown/seed/` to `markdown/reference/`
- Initializes database and imports seeds + templates

**Then exit and restart your MCP client** (so MCP loads).

### 6. Begin

```
Read open.md and execute it
```

**First working open.md:**
- Loads seed-arlo-foundations (orientation)
- Loads empty reference-arlo-foundations (template)
- Loads empty state-arlo
- No logs yet (this is session 1)
- No corrections yet

**You tell the model about yourself.** It updates `reference-arlo-foundations.md` with your info.

---

## Session 1: First Real Session

You work. At the end:

```
Read close.md and execute it
```

**What close.md does:**

1. **Corrections** — Log any errors made during session
2. **Log session** — The model calls `log_session` MCP tool:
   - preview: "2025-12-25 (Thu), interactive. First session. Set up foundations..."
   - witness: {you_today, me_today, us_today}
   - handoff: "S1: Foundations populated. Next: ..."
   - Returns: `session_number: 1`
3. **Extract transcript** — The model runs the transcript extraction script (client-specific paths detected automatically)
4. **Update state** — The model updates `state-arlo` with continuity/attention/threads
5. **Export & commit** — `export_to_markdown`, `git commit`, `git push`

**Result:**
- `session-001` log in KB
- `transcript-001` transcript in KB
- Both exported to `markdown/log/` and `markdown/transcript/`
- Git history started

---

## Sessions 2-10: The Pattern

Each session:

**Start:**
```
Read open.md and execute it
```
- Loads foundations (seed + personal)
- Loads state-arlo
- Loads logs 1-7 fully (or all if <7 exist)
- Loads most recent transcript fully
- Loads corrections
- Loads todos

**Work.** (whatever you're doing)

**End:**
```
Read close.md and execute it
```
- Same 5 steps
- Log number increments (session-002, session-003, ...)
- Transcript extracted for each
- State updated
- Git pushed

**By Session 7:**
- open.md loads all 7 logs fully
- Transcripts 1-7 exist, searchable via `remember-when.md`

**By Session 10:**
- open.md loads logs 4-10 fully (7 most recent)
- open.md loads logs 1-3 as 400-char previews
- 10 transcripts exist

---

## Session 11: Steady State

```
Read open.md and execute it
```

**What loads:**
1. `seed-arlo-foundations` — universal orientation
2. `reference-arlo-foundations` — your personal context
3. `state-arlo` — current attention/threads
4. Logs 5-11 fully (7 most recent)
5. Logs 2-4 as previews (older history, 400 chars each)
6. `transcript-010` fully — most recent verbatim
7. `accumulator-corrections` — behavioral patterns
8. `todo-work`, `todo-personal` — task lists

**Token budget:** ~4-5K tokens for context load (plus ~15-20K for full transcript)

**Available:**
- `search.md <topic>` — search KB for specific knowledge
- `remember-when.md <query>` — search transcripts for exact exchanges
- `audit.md` — audit KB health

**End of session 11:**
```
Read close.md and execute it
```
- Creates session-011 log
- Creates transcript-011
- Updates state
- Exports, commits, pushes

---

## What Accumulates

| Session | Logs | Transcripts | Corrections |
|---------|------|-------------|-------------|
| 1 | 1 | 1 | 0 |
| 5 | 5 | 5 | maybe 1-2 |
| 10 | 10 | 10 | maybe 3-5 |
| 50 | 50 | 50 | graduated to KB entries |
| 100+ | 100+ | 100+ | patterns stabilized |

**Storage growth:** ~2KB/session (log) + ~15KB/session (transcript) = ~17KB/session

---

## The Continuity Effect

By session 11:
- The model knows your context (foundations)
- The model knows recent trajectory (last 7 logs)
- The model knows what's fading vs. active (state)
- The model knows its own failure patterns (corrections)
- The model has full verbatim of last session (transcript)
- The model can search older exchanges (remember-when.md)
- The model can find domain knowledge (search.md)

That's the machine.
