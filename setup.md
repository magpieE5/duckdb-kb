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

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\pip.exe install --upgrade pip
.\venv\Scripts\pip.exe install -r requirements.txt
```

### 2. Configure MCP

Use the `venv_python` and `cwd` values from step 0.

```bash
claude mcp add duckdb-kb "{venv_python}" "{cwd}/mcp_server.py"
```

### 3. Copy templates

**macOS/Linux:**
```bash
mkdir -p markdown/reference markdown/transcript
cp markdown/seed/seed-template-foundations.md markdown/reference/reference-arlo-foundations.md
cp markdown/seed/seed-template-state.md markdown/reference/state-arlo.md
cp markdown/seed/seed-template-corrections.md markdown/reference/accumulator-corrections.md
```

**Windows (PowerShell):**
```powershell
New-Item -ItemType Directory -Force -Path markdown\reference, markdown\transcript
Copy-Item markdown\seed\seed-template-foundations.md markdown\reference\reference-arlo-foundations.md
Copy-Item markdown\seed\seed-template-state.md markdown\reference\state-arlo.md
Copy-Item markdown\seed\seed-template-corrections.md markdown\reference\accumulator-corrections.md
```

### 4. Done

Restart Claude Code and run `/open` to begin.
