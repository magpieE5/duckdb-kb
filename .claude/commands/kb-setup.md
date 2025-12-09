# /kb-setup

One-time setup for fresh duckdb-kb installation (GitHub Codespaces).

## Execution

### 1. Create venv and install dependencies

```bash
cd /workspaces/duckdb-kb
python3 -m venv venv
venv/bin/pip install --upgrade pip
venv/bin/pip install -r requirements.txt
```

### 2. Configure MCP

```bash
claude mcp add duckdb-kb /workspaces/duckdb-kb/venv/bin/python /workspaces/duckdb-kb/mcp_server.py -e KB_DB_PATH=/workspaces/duckdb-kb/kb.duckdb
```

### 3. Done

**"Setup complete. Type `/exit` to quit, then `claude` to restart Claude Code, then run `/kbo` to begin."**
