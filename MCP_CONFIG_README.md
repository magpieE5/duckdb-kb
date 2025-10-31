# MCP Configuration Guide

This guide explains how to configure Claude Code (or any MCP-compatible AI assistant) to use the DuckDB Knowledge Base MCP server.

## Quick Reference

**Config file location:**
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux:** `~/.config/claude/claude_desktop_config.json`

**Template:** See `MCP_CONFIG_EXAMPLE.json` in this directory

---

## Step-by-Step Setup

### 1. Locate Your MCP Config File

Open your terminal/command prompt and check if the file exists:

**macOS/Linux:**
```bash
ls -la ~/Library/Application\ Support/Claude/claude_desktop_config.json
# or
ls -la ~/.config/claude/claude_desktop_config.json
```

**Windows:**
```cmd
dir %APPDATA%\Claude\claude_desktop_config.json
```

### 2. Get Your OpenAI API Key (Required for Embeddings)

1. Go to https://platform.openai.com/api-keys
2. Sign up or log in to your account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-proj-...`)
5. **Save it somewhere safe** - you can't view it again!

**Cost:** Approximately $0.01-0.02/month for personal use

**Alternative:** Use local embeddings (free, but slower). See "Using Local Embeddings" below.

### 3. Edit or Create Config File

#### If File Already Exists

Open it in your text editor and **add** the duckdb-kb entry inside the `mcpServers` object:

```json
{
  "mcpServers": {
    "existing-mcp": {
      "...": "..."
    },
    "duckdb-kb": {
      "command": "/absolute/path/to/duckdb-kb/venv/bin/python",
      "args": [
        "/absolute/path/to/duckdb-kb/mcp_server.py"
      ],
      "env": {
        "OPENAI_API_KEY": "sk-proj-YOUR-KEY-HERE",
        "KNOWLEDGE_DB_PATH": "/absolute/path/to/duckdb-kb/knowledge.duckdb",
        "EMBEDDING_PROVIDER": "openai"
      }
    }
  }
}
```

#### If File Doesn't Exist

Create it with this content:

```json
{
  "mcpServers": {
    "duckdb-kb": {
      "command": "/absolute/path/to/duckdb-kb/venv/bin/python",
      "args": [
        "/absolute/path/to/duckdb-kb/mcp_server.py"
      ],
      "env": {
        "OPENAI_API_KEY": "sk-proj-YOUR-KEY-HERE",
        "KNOWLEDGE_DB_PATH": "/absolute/path/to/duckdb-kb/knowledge.duckdb",
        "EMBEDDING_PROVIDER": "openai"
      }
    }
  }
}
```

### 4. Replace Placeholders

**Important:** You must replace these with your actual values:

1. **`/absolute/path/to/duckdb-kb`** → Your actual installation path
   - Example (macOS): `/Users/john/duckdb-kb`
   - Example (Windows): `C:/Users/john/duckdb-kb`
   - Example (Linux): `/home/john/duckdb-kb`

2. **`sk-proj-YOUR-KEY-HERE`** → Your OpenAI API key from step 2

**Finding your path:**
```bash
cd duckdb-kb
pwd
# Copy the output and use it in your config
```

### 5. Save and Restart

1. Save the config file
2. **Completely quit** Claude Code (not just close the window)
3. Reopen Claude Code
4. The MCP server will connect automatically on startup

---

## Verify It's Working

Once Claude Code restarts, test the connection:

**Ask Claude:**
```
Get database statistics from the knowledge base
```

**Expected:** Claude should call `mcp__duckdb-kb__get_stats()` and show you:
- Total entries (should be 12 for fresh install)
- Entries with embeddings
- Category breakdown

If you see this, **it's working!** 🎉

---

## Using Local Embeddings (Free Alternative)

If you don't want to use OpenAI, you can use local embeddings:

### 1. Install Local Model Support

```bash
cd duckdb-kb
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install sentence-transformers torch
```

### 2. Update Config

Change your config to use `"local"` instead of `"openai"`:

```json
{
  "mcpServers": {
    "duckdb-kb": {
      "command": "/absolute/path/to/duckdb-kb/venv/bin/python",
      "args": [
        "/absolute/path/to/duckdb-kb/mcp_server.py"
      ],
      "env": {
        "KNOWLEDGE_DB_PATH": "/absolute/path/to/duckdb-kb/knowledge.duckdb",
        "EMBEDDING_PROVIDER": "local"
      }
    }
  }
}
```

**Note:** No `OPENAI_API_KEY` needed when using local embeddings!

### 3. Regenerate Embeddings

```bash
cd duckdb-kb
export EMBEDDING_PROVIDER=local
python generate_embeddings.py
```

**Trade-offs:**
- ✅ Free (no API costs)
- ✅ Private (data never leaves your machine)
- ❌ Slower (first run downloads ~500MB model)
- ❌ Lower quality than OpenAI embeddings

---

## Troubleshooting

### "MCP server failed to connect"

**Check:**
1. Paths are absolute (not relative like `./duckdb-kb`)
2. Python venv path is correct: `duckdb-kb/venv/bin/python`
3. No typos in file paths
4. Database file exists: `ls duckdb-kb/knowledge.duckdb`

### "OpenAI API error"

**Check:**
1. API key is correct (starts with `sk-proj-`)
2. No extra spaces or quotes around the key
3. Your OpenAI account has credits
4. Test the key: https://platform.openai.com/playground

### "No tools available"

**Check:**
1. You completely quit and reopened Claude Code
2. Config file has valid JSON (no trailing commas, matching brackets)
3. Check Claude Code logs in Settings → MCP

### "Database not found"

**Check:**
1. Path to `knowledge.duckdb` is correct
2. You ran the setup steps: `duckdb knowledge.duckdb < schema.sql`
3. File exists: `ls -lh duckdb-kb/knowledge.duckdb`

---

## Advanced: Multiple Knowledge Bases

You can run multiple knowledge base instances:

```json
{
  "mcpServers": {
    "duckdb-kb-work": {
      "command": "/Users/you/work-kb/venv/bin/python",
      "args": ["/Users/you/work-kb/mcp_server.py"],
      "env": {
        "OPENAI_API_KEY": "sk-proj-...",
        "KNOWLEDGE_DB_PATH": "/Users/you/work-kb/knowledge.duckdb"
      }
    },
    "duckdb-kb-personal": {
      "command": "/Users/you/personal-kb/venv/bin/python",
      "args": ["/Users/you/personal-kb/mcp_server.py"],
      "env": {
        "OPENAI_API_KEY": "sk-proj-...",
        "KNOWLEDGE_DB_PATH": "/Users/you/personal-kb/knowledge.duckdb"
      }
    }
  }
}
```

Claude will have access to both:
- `mcp__duckdb-kb-work__*` tools
- `mcp__duckdb-kb-personal__*` tools

---

## Security Notes

⚠️ **Important:**
- **Never commit** your MCP config file with API keys to git
- **Never share** your OpenAI API key publicly
- **Use environment variables** for shared/team setups
- **Set spending limits** in your OpenAI account

---

## Support

- **Setup help:** See QUICKSTART.md for 5-minute setup guide
- **Feature docs:** See README.md for complete documentation
- **Troubleshooting:** See SETUP.md for detailed setup instructions
- **Backup:** See BACKUP.md for backup strategies

---

**Need more help?** Check the documentation in this repository or search the knowledge base itself - it's self-documenting!
