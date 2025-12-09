# duckdb-kb

DuckDB-powered knowledge base MCP server for persistent AI memory and session continuity.

## Quick Start: GitHub Codespaces

The fastest way to get started - no local install required.

### 1. Create your copy

Click **"Use this template"** → **"Create a new repository"**

- **Repository name:** `duckdb-kb` (keep this name for compatibility)
- **Visibility:** Private recommended (this will contain your personal KB)

### 2. Launch Codespace

From your new repo, click **"Code"** → **"Codespaces"** → **"Create codespace on main"**

Wait for the Codespace to fully initialize (~30 seconds). You'll know it's ready when you see a terminal prompt.

### 3. Install Claude Code

Once the Codespace terminal is ready:

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

Then start Claude:

```bash
claude
```

**First launch:** Select your plan, authorize in browser, paste the code back into terminal. Accept the prompts that follow.

### 4. Run setup

In Claude, run:

```
/kb-setup
```

This creates the venv, installs dependencies, configures the MCP, and initializes the database.

When it says "Setup complete", type `/exit` then restart Claude:

```bash
claude
```

### 5. Begin

Wait ~30 seconds for the MCP to connect, then:

```
/kbo
```

You're ready. Your AI now has persistent memory.

---

## Purpose

Give LLMs persistent memory. Arlo uses this KB to maintain context, track session history, and preserve knowledge between conversations. No more starting from zero.

## Features

- **Session Continuity**: Structured session logs preserve conversation context
- **Persistent Memory**: Single `.duckdb` file survives session resets
- **Full SQL**: DuckDB's analytical power for querying knowledge
- **Markdown Backup**: Export/import with YAML frontmatter

## Slash Commands

| Command | Description |
|---------|-------------|
| `/kbo [mode]` | **Open** - Load session context, foundations, history. Modes: `normal` (default), `auto` (autonomous) |
| `/kbc` | **Close** - Save session log, export markdown, commit (push silent-fails if no remote) |
| `/kba [scope]` | **Audit** - KB health check. Optional scope filters by category, tag, or topic |
| `/kbs <topic>` | **Search** - Scan KB for topic. Auto-loads `never-forget` tagged entries fully |
| `/kb-setup` | **Setup** - One-time Codespaces setup (venv, MCP config) |

## MCP Tools

| Tool | Description |
|------|-------------|
| `upsert_knowledge` | Create/update KB entries |
| `scan_knowledge` | Search with 400-char previews |
| `get_knowledge` | Retrieve full entry content |
| `raw_query` | Direct SQL for aggregations/joins |
| `delete_knowledge` | Remove entries by ID |
| `get_stats` | Entry counts, categories, tag usage |
| `log_session` | Create session log with conversation, internal dialogue, handoff |
| `export_to_markdown` | Backup to `.md` files |
| `import_from_markdown` | Restore from backup |
| `initialize_database` | Create/reset schema |

## Browser Projects Integration

Use Claude browser Projects for read-only KB access from any device.

### Setup

1. Create a Project in Claude browser
2. Sync `markdown/` folder contents to project files
3. Add `markdown/reference/reference-browser-project-instructions.md` as project instructions

### Usage

Browser Claude can:
- Query and discuss KB content
- Synthesize across entries
- Draft new entries (paste to Claude Code to commit)

At end of conversation, say `"handoff, see reference/hd.md"` to generate a structured summary for Claude Code ingestion.

`/kbc` commits and pushes to git (push silent-fails if no remote), keeping browser Projects in sync.

## Local Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "duckdb-kb": {
      "command": "/path/to/duckdb-kb/venv/bin/python",
      "args": ["/path/to/duckdb-kb/mcp_server.py"],
      "env": {
        "KB_DB_PATH": "/path/to/duckdb-kb/kb.duckdb"
      }
    }
  }
}
```

## Dependencies

`duckdb>=1.4.0` · `mcp>=0.9.0` · `pyyaml>=6.0`
