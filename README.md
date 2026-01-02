# duckdb-kb

Persistent AI memory via Model Context Protocol. One Parquet file, thirteen tools, genuine continuity.

**[Read the Whitepaper (PDF)](whitepaper.pdf)** — Architecture, protocol, and design philosophy.

---

## Quick Start

### Prerequisites

**macOS:**
```bash
# Check if already installed
git --version && python3 --version

# If not, install via Homebrew (https://brew.sh)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install git python
```

**Linux (Debian/Ubuntu):**
```bash
sudo apt update && sudo apt install git python3 python3-venv
```

**Linux (Fedora/RHEL):**
```bash
sudo dnf install git python3
```

**Windows (PowerShell as Admin):**
```powershell
winget install Git.Git Python.Python.3.12
# Restart PowerShell after install
```

**GitHub Codespaces:** Nothing needed — Python and Git are pre-installed.

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

### 3. Install MCP Client

Choose one:

**Claude Code:**
```bash
# macOS / Linux / Codespaces
curl -fsSL https://claude.ai/install.sh | bash
```
```powershell
# Windows
irm https://claude.ai/install.ps1 | iex
```

**Gemini CLI:**
```bash
# macOS / Linux / Codespaces (requires Node.js 18+)
npm install -g @google/gemini-cli
```
```powershell
# Windows (install Node.js first: winget install OpenJS.NodeJS)
npm install -g @google/gemini-cli
```

### 4. Run Setup

Start your MCP client and tell it to run setup:

```
claude                              # or: gemini
> Read setup.md and execute it
```

Setup creates the venv, installs dependencies, configures the MCP, copies templates, and initializes the database.

**Restart your MCP client** when done (so the MCP loads).

### 5. Begin

```
> Read open.md and execute it
```

Tell the model who you are — name, role, background, what matters. It updates your foundations file. You're ready.

---

## What It Does

- **Continuity**: Session logs with witness sections tracking dynamics over time
- **Persistent Memory**: Single Parquet file with full-text search
- **Self-Correction**: Corrections accumulator tracks error patterns for behavioral learning
- **Human Audit Layer**: Bidirectional markdown export enables direct editing of all stored knowledge
- **Cross-Platform**: macOS, Windows, Linux, GitHub Codespaces
- **Model-Agnostic**: Works with Claude Code, Gemini CLI, or local models via Ollama

---

## Workflow Commands

Markdown files at repo root. Tell your model to read and execute them.

| File | Description |
|------|-------------|
| `open.md` | Load context: foundations, recent logs, transcript, corrections, todos |
| `close.md` | Save session: log, transcript, export, commit |
| `search.md <topic>` | Search KB for topic |
| `remember-when.md <topic>` | Search transcripts for exact exchanges |
| `audit.md` | KB health check |
| `setup.md` | One-time setup |

---

## MCP Tools

| Tool | Description |
|------|-------------|
| `upsert_knowledge` | Create/update KB entries |
| `get_knowledge` | Retrieve full entries by WHERE clause |
| `scan_knowledge` | Full-text search with previews |
| `delete_knowledge` | Remove entries |
| `list_knowledge` | List all entry IDs/titles |
| `raw_query` | Direct SQL |
| `log_session` | Create session log |
| `todo_add` / `todo_complete` | Manage todo lists |
| `append_accumulator` | Append-only entries (corrections, etc.) |
| `export_to_markdown` / `import_from_markdown` | Markdown sync |
| `initialize_database` | Create schema |

---

## The Session Pattern

Each session:

**Start:**
```
Read open.md and execute it
```
Loads: foundations → state → last 7 logs → last transcript → corrections → todos

**Work.** (whatever you're doing)

**End:**
```
Read close.md and execute it
```
Saves: corrections → session log → transcript → export → git commit

By session 10+, the model knows your context, recent trajectory, its own failure patterns, and has full verbatim of last session plus searchable history of all prior exchanges.

---

## Dependencies

`duckdb>=1.4.0` · `mcp>=0.9.0` · `pyyaml>=6.0`

---

## Full Tutorial

For a detailed walkthrough from clone to session 11 (steady state), see [TUTORIAL.md](TUTORIAL.md).
