#!/usr/bin/env python3
"""
Shared repo scanner for duckdb-kb.

Parses .gitignore for shared repo paths and runs git operations.

Usage:
    python tools/shared_repos.py pull    # On /open - pull all shared repos
    python tools/shared_repos.py push    # On /close - push all shared repos
    python tools/shared_repos.py list    # Show configured shared repos
"""

import subprocess
import sys
from pathlib import Path

# Markers in .gitignore
START_MARKER = "# Shared DuckDB-KB MCP repos"
END_MARKER = "# ^ Shared DuckDB-KB MCP repos"

def get_kb_root() -> Path:
    """Get the duckdb-kb root directory."""
    return Path(__file__).parent.parent

def parse_shared_repos() -> list[Path]:
    """Parse .gitignore for shared repo paths between markers."""
    gitignore = get_kb_root() / ".gitignore"
    if not gitignore.exists():
        return []

    repos = []
    in_block = False

    for line in gitignore.read_text().splitlines():
        line = line.strip()

        if line == START_MARKER:
            in_block = True
            continue
        elif line == END_MARKER:
            in_block = False
            continue

        if in_block and line and not line.startswith("#"):
            # Remove trailing slash if present
            path = line.rstrip("/")
            repo_path = get_kb_root() / path
            if repo_path.exists() and (repo_path / ".git").exists():
                repos.append(repo_path)

    return repos

def run_git(repo: Path, *args) -> tuple[bool, str]:
    """Run git command in repo directory."""
    try:
        result = subprocess.run(
            ["git"] + list(args),
            cwd=repo,
            capture_output=True,
            text=True
        )
        output = result.stdout.strip() or result.stderr.strip()
        return result.returncode == 0, output
    except Exception as e:
        return False, str(e)

def pull_all():
    """Pull all shared repos."""
    repos = parse_shared_repos()
    if not repos:
        print("No shared repos configured")
        return

    for repo in repos:
        name = repo.name
        print(f"{name}: ", end="")

        # Get current branch
        ok, branch = run_git(repo, "rev-parse", "--abbrev-ref", "HEAD")
        if not ok:
            print(f"error getting branch: {branch}")
            continue

        # Pull
        ok, output = run_git(repo, "pull", "--ff-only")
        if ok:
            if "Already up to date" in output:
                print(f"up to date ({branch})")
            else:
                print(f"updated ({branch})")
        else:
            print(f"pull failed: {output}")

def push_all():
    """Push all shared repos (if there are changes)."""
    repos = parse_shared_repos()
    if not repos:
        print("No shared repos configured")
        return

    for repo in repos:
        name = repo.name
        print(f"{name}: ", end="")

        # Check for uncommitted changes
        ok, status = run_git(repo, "status", "--porcelain")
        if status:
            print(f"has uncommitted changes, skipping push")
            continue

        # Check if ahead of remote
        ok, output = run_git(repo, "status", "-sb")
        if "ahead" not in output:
            print("nothing to push")
            continue

        # Push
        ok, output = run_git(repo, "push")
        if ok:
            print("pushed")
        else:
            print(f"push failed: {output}")

def list_repos():
    """List configured shared repos."""
    repos = parse_shared_repos()
    if not repos:
        print("No shared repos configured")
        return

    for repo in repos:
        ok, branch = run_git(repo, "rev-parse", "--abbrev-ref", "HEAD")
        ok, remote = run_git(repo, "remote", "get-url", "origin")
        print(f"{repo.name}:")
        print(f"  path: {repo}")
        print(f"  branch: {branch}")
        print(f"  remote: {remote}")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "pull":
        pull_all()
    elif cmd == "push":
        push_all()
    elif cmd == "list":
        list_repos()
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()
