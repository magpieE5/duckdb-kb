# setup

One-time setup for fresh duckdb-kb installation.

## Execution

### 0. Get OS-specific paths (cross-platform)

```bash
python3 tools/session_details.py
```

Note `venv_python`, `venv_pip`, `cwd`, and `os` from output. Use these values below.

### 1. Create venv and install dependencies

**macOS/Linux:**
```bash
python3 -m venv venv
venv/bin/pip install --upgrade pip
venv/bin/pip install -r requirements.txt
```

**Windows (works in PowerShell, CMD, or Git Bash):**
```bash
python -m venv venv
venv/Scripts/python -m pip install --upgrade pip
venv/Scripts/python -m pip install -r requirements.txt
```

Note: Use forward slashes - they work on Windows and avoid escaping issues in bash.

### 2. Configure MCP

Use the `venv_python` and `cwd` values from step 0.

```bash
claude mcp add duckdb-kb "{venv_python}" "{cwd}/mcp_server.py"
```

### 3. Copy templates

```bash
mkdir -p markdown/reference markdown/transcript
cp markdown/seed/seed-template-foundations.md markdown/reference/reference-arlo-foundations.md
cp markdown/seed/seed-template-state.md markdown/reference/state-arlo.md
cp markdown/seed/seed-template-corrections.md markdown/reference/accumulator-corrections.md
```

Note: These Unix commands work on all platforms (Claude Code uses Git Bash on Windows).

### 4. Done

Restart Claude Code and run `/open` to begin.
