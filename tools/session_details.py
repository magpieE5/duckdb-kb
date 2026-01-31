#!/usr/bin/env python3
"""Cross-platform, client-agnostic session details for workflow commands.

Returns OS-specific paths and details needed by kbo.md, kbc.md, and other workflow commands.
Supports Claude Code, Gemini CLI, and future MCP clients.

Usage:
    python tools/session_details.py           # JSON output
    python tools/session_details.py --key     # Get specific key (e.g., --latest_session)

Importable constants:
    from session_details import REPO_ROOT, KB_DB_PATH, MARKDOWN_DIR
"""
import os
import platform
import getpass
import sys
from pathlib import Path
from datetime import datetime


# === IMPORTABLE PATH CONSTANTS ===
# These can be imported by other tools for consistency

def _get_repo_root() -> Path:
    """Detect repo root from cwd or script location.

    Strategy:
    1. If cwd looks like repo root (has mcp_server.py or tools/), use it
    2. Otherwise derive from script location (tools/ is in repo root)

    This handles both:
    - MCP server running from repo root (cwd-based)
    - Standalone scripts run from anywhere (file-based)
    """
    cwd = Path.cwd()
    # If cwd looks like repo root, use it
    if (cwd / 'mcp_server.py').exists() or (cwd / 'tools').is_dir():
        return cwd
    # Fallback: derive from script location (this file is in tools/)
    return Path(__file__).parent.parent.resolve()


REPO_ROOT = _get_repo_root()
KB_DB_PATH = os.getenv('KB_DB_PATH', str(REPO_ROOT / 'kb.duckdb'))  # Legacy, for migration
KB_PARQUET_PATH = os.getenv('KB_PARQUET_PATH', str(REPO_ROOT / 'kb.parquet'))
KB_ACCESS_PARQUET_PATH = os.getenv('KB_ACCESS_PARQUET_PATH', str(REPO_ROOT / 'kb_access.parquet'))
MARKDOWN_DIR = REPO_ROOT / 'markdown'
DRAFTS_DIR = REPO_ROOT / 'drafts'


def _get_next_session_number() -> int:
    """Get next session number by finding max session-NNN log entry + 1."""
    import re
    parquet_path = KB_PARQUET_PATH
    if not Path(parquet_path).exists():
        return 1

    try:
        import duckdb
        con = duckdb.connect()
        result = con.execute(f"""
            SELECT MAX(CAST(REGEXP_EXTRACT(id, 'session-([0-9]+)', 1) AS INT))
            FROM read_parquet('{parquet_path}')
            WHERE category = 'log' AND id LIKE 'session-%'
        """).fetchone()
        con.close()
        max_session = result[0] if result and result[0] else 0
        return max_session + 1
    except Exception:
        return 1


def find_claude_session(home: Path, encoded_path: str) -> tuple[Path | None, int]:
    """Find most recent Claude Code session."""
    claude_projects = home / '.claude' / 'projects' / encoded_path
    if not claude_projects.exists():
        return None, 0

    jsonls = sorted(
        [j for j in claude_projects.glob('*.jsonl') if 'agent' not in j.name],
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    return (jsonls[0] if jsonls else None), len(jsonls)


def find_gemini_session(home: Path) -> tuple[Path | None, int]:
    """Find most recent Gemini CLI session.

    Gemini stores sessions at ~/.gemini/tmp/<project_hash>/chats/*.json
    We search all project hashes and find the most recent chat file.
    """
    gemini_tmp = home / '.gemini' / 'tmp'
    if not gemini_tmp.exists():
        return None, 0

    # Find all chat JSON files across all project hashes
    all_chats = []
    for project_dir in gemini_tmp.iterdir():
        if project_dir.is_dir():
            chats_dir = project_dir / 'chats'
            if chats_dir.exists():
                all_chats.extend(chats_dir.glob('*.json'))

    if not all_chats:
        return None, 0

    # Sort by modification time, most recent first
    all_chats.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return all_chats[0], len(all_chats)


def get_session_details() -> dict:
    """Return all OS-specific paths and details for workflow commands."""
    home = Path.home()
    cwd = Path.cwd()
    system = platform.system()  # 'Windows', 'Darwin', 'Linux'

    # Encode project path for Claude (slashes/backslashes → dashes)
    cwd_str = str(cwd)
    if system == 'Windows':
        # C:\Users\Andy\duckdb-kb → C--Users-Andy-duckdb-kb
        encoded = cwd_str.replace('\\', '-').replace(':', '-')
    else:
        # /Users/brock/duckdb-kb → -Users-brock-duckdb-kb
        encoded = cwd_str.replace('/', '-')

    # Find sessions for each client
    claude_session, claude_count = find_claude_session(home, encoded)
    gemini_session, gemini_count = find_gemini_session(home)

    # Determine active client based on most recent session
    client = 'unknown'
    latest_session = None
    latest_session_format = None

    claude_mtime = claude_session.stat().st_mtime if claude_session else 0
    gemini_mtime = gemini_session.stat().st_mtime if gemini_session else 0

    if claude_mtime > gemini_mtime and claude_session:
        client = 'claude'
        latest_session = str(claude_session)
        latest_session_format = 'jsonl'
    elif gemini_session:
        client = 'gemini'
        latest_session = str(gemini_session)
        latest_session_format = 'json'
    elif claude_session:
        client = 'claude'
        latest_session = str(claude_session)
        latest_session_format = 'jsonl'

    # Claude projects directory (for backwards compat)
    claude_projects = home / '.claude' / 'projects' / encoded

    # Venv python path
    if system == 'Windows':
        venv_python = cwd / 'venv' / 'Scripts' / 'python.exe'
        venv_pip = cwd / 'venv' / 'Scripts' / 'pip.exe'
        path_sep = '\\'
    else:
        venv_python = cwd / 'venv' / 'bin' / 'python'
        venv_pip = cwd / 'venv' / 'bin' / 'pip'
        path_sep = '/'

    # KB database path (use shared constant)
    kb_db = KB_DB_PATH

    # Markdown export/import directory (use shared constant)
    markdown_dir = MARKDOWN_DIR

    # Tools directory
    tools_dir = cwd / 'tools'
    extract_script = tools_dir / 'extract_exchanges.py'

    # Build extract command
    extract_cmd = f'"{venv_python}" "{extract_script}"'

    # Claude settings paths
    if system == 'Windows':
        claude_settings = home / '.claude' / 'settings.json'
        claude_desktop_config = Path(os.environ.get('APPDATA', '')) / 'Claude' / 'claude_desktop_config.json'
    else:
        claude_settings = home / '.claude' / 'settings.json'
        claude_desktop_config = home / 'Library' / 'Application Support' / 'Claude' / 'claude_desktop_config.json'

    # Gemini CLI paths
    gemini_base = home / '.gemini'
    gemini_settings = gemini_base / 'settings.json'
    gemini_memory = gemini_base / 'GEMINI.md'

    return {
        # OS info
        'os': system,
        'os_is_windows': system == 'Windows',
        'os_is_mac': system == 'Darwin',
        'os_is_linux': system == 'Linux',
        'path_sep': path_sep,

        # User/paths
        'home': str(home),
        'cwd': str(cwd),
        'user': getpass.getuser(),

        # Timestamps
        'timestamp': datetime.now().isoformat(),
        'date_display': datetime.now().strftime('%a %b %d %H:%M:%S %Y'),
        'date_short': datetime.now().strftime('%Y-%m-%d'),

        # Session number (next session = max log session + 1)
        'session_number': _get_next_session_number(),

        # === UNIFIED CLIENT-AGNOSTIC FIELDS ===
        'client': client,  # 'claude', 'gemini', or 'unknown'
        'latest_session': latest_session,  # Path to most recent session file
        'latest_session_format': latest_session_format,  # 'jsonl' or 'json'

        # === CLAUDE CODE PATHS ===
        'claude_projects': str(claude_projects),
        'claude_projects_exists': claude_projects.exists(),
        'claude_session': str(claude_session) if claude_session else None,
        'claude_session_count': claude_count,
        'claude_settings': str(claude_settings),
        'claude_desktop_config': str(claude_desktop_config),

        # === GEMINI CLI PATHS ===
        'gemini_base': str(gemini_base),
        'gemini_base_exists': gemini_base.exists(),
        'gemini_session': str(gemini_session) if gemini_session else None,
        'gemini_session_count': gemini_count,
        'gemini_settings': str(gemini_settings),
        'gemini_memory': str(gemini_memory),

        # === VENV PATHS ===
        'venv_python': str(venv_python),
        'venv_pip': str(venv_pip),
        'venv_exists': venv_python.exists(),

        # === KB PATHS ===
        'kb_db': kb_db,
        'kb_db_exists': Path(kb_db).exists(),
        'markdown_dir': str(markdown_dir),
        'markdown_dir_exists': markdown_dir.exists(),

        # === TOOL PATHS ===
        'tools_dir': str(tools_dir),
        'extract_script': str(extract_script),
        'extract_cmd': extract_cmd,
        'extract_full': f'{extract_cmd} "{{session_path}}" {{session_number}}',

        # === BACKWARDS COMPAT (deprecated, use latest_session instead) ===
        'latest_jsonl': str(claude_session) if claude_session else None,
        'jsonl_count': claude_count,
        'is_claude_code': claude_projects.exists(),
        'is_gemini_cli': gemini_base.exists(),
    }


def main():
    import json

    details = get_session_details()

    # If a specific key requested via --key
    if len(sys.argv) > 1:
        key = sys.argv[1].lstrip('-')
        if key in details:
            print(details[key])
        else:
            print(f"Unknown key: {key}", file=sys.stderr)
            print(f"Available: {', '.join(details.keys())}", file=sys.stderr)
            sys.exit(1)
    else:
        print(json.dumps(details, indent=2))


if __name__ == '__main__':
    main()
