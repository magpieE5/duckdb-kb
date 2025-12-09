#!/usr/bin/env python3
"""
Jira API utilities for UO IDR/DDS ticket management.

Requires JIRA_PAT and JIRA_URL environment variables.
"""

import os
import json
import requests
from datetime import datetime
from typing import Optional
from urllib.parse import quote

def get_env():
    pat = os.environ.get("JIRA_PAT")
    url = os.environ.get("JIRA_URL", "https://jira.uoregon.edu")
    if not pat:
        raise ValueError("JIRA_PAT environment variable not set")
    return pat, url

def api_get(endpoint: str, params: dict = None) -> dict | list:
    """Make authenticated GET request to Jira API."""
    pat, base_url = get_env()
    url = f"{base_url}/rest/api/2/{endpoint}"
    headers = {"Authorization": f"Bearer {pat}"}
    resp = requests.get(url, headers=headers, params=params or {})
    resp.raise_for_status()
    return resp.json()

def api_post(endpoint: str, data: dict) -> dict:
    """Make authenticated POST request to Jira API."""
    pat, base_url = get_env()
    url = f"{base_url}/rest/api/2/{endpoint}"
    headers = {
        "Authorization": f"Bearer {pat}",
        "Content-Type": "application/json"
    }
    resp = requests.post(url, headers=headers, json=data)
    resp.raise_for_status()
    return resp.json() if resp.text else {}

def add_comment(key: str, body: str) -> dict:
    """Add comment to a ticket."""
    endpoint = f"issue/{key}/comment"
    return api_post(endpoint, {"body": body})

def search_issues(jql: str, fields: list[str] = None, max_results: int = 50) -> list[dict]:
    """Search issues using JQL."""
    params = {
        "jql": jql,
        "maxResults": max_results
    }
    if fields:
        params["fields"] = ",".join(fields)
    result = api_get("search", params)
    return result.get("issues", [])

def get_issue(key: str, fields: list[str] = None) -> dict:
    """Get single issue by key."""
    endpoint = f"issue/{key}"
    if fields:
        endpoint += f"?fields={','.join(fields)}"
    return api_get(endpoint)

def get_my_open_tickets() -> list[dict]:
    """Get Brock's open tickets in IDR project."""
    jql = 'project = "10220" AND assignee in (lampman) AND status not in (Done, Closed, Resolved)'
    fields = ["key", "summary", "status", "issuetype", "created", "updated", "components"]
    return search_issues(jql, fields)

def get_recent_closed(days: int = 30) -> list[dict]:
    """Get recently closed tickets."""
    jql = f'project = "10220" AND assignee in (lampman) AND status in (Done, Closed, Resolved) AND resolved >= -{days}d'
    fields = ["key", "summary", "status", "resolution", "resolutiondate", "issuetype"]
    return search_issues(jql, fields)

def get_ticket_detail(key: str) -> dict:
    """Get full ticket detail including comments."""
    fields = [
        "key", "summary", "description", "status", "issuetype",
        "created", "updated", "reporter", "assignee", "components",
        "comment", "resolution", "resolutiondate", "attachment"
    ]
    return get_issue(key, fields)

def get_attachments(key: str) -> list[dict]:
    """Get attachments for a ticket."""
    issue = get_issue(key, ["attachment"])
    return issue.get("fields", {}).get("attachment", [])

def download_attachment(key: str, filename: str, output_dir: str = ".") -> str:
    """Download a specific attachment by filename. Returns path to downloaded file."""
    pat, _ = get_env()
    attachments = get_attachments(key)

    # Find matching attachment
    match = None
    for att in attachments:
        if att.get("filename") == filename:
            match = att
            break

    if not match:
        available = [a.get("filename") for a in attachments]
        raise ValueError(f"Attachment '{filename}' not found. Available: {available}")

    # Download the file
    url = match.get("content")
    headers = {"Authorization": f"Bearer {pat}"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()

    output_path = os.path.join(output_dir, filename)
    with open(output_path, "wb") as f:
        f.write(resp.content)

    return output_path

def format_attachments(attachments: list[dict]) -> str:
    """Format attachment list for display."""
    if not attachments:
        return "  No attachments."

    lines = []
    for att in attachments:
        name = att.get("filename", "?")
        size = att.get("size", 0)
        created = format_date(att.get("created"))
        author = att.get("author", {}).get("displayName", "?")

        # Human-readable size
        if size < 1024:
            size_str = f"{size}B"
        elif size < 1024 * 1024:
            size_str = f"{size // 1024}KB"
        else:
            size_str = f"{size // (1024 * 1024)}MB"

        lines.append(f"  {name:<40} {size_str:>8}  {created}  ({author})")

    return "\n".join(lines)

def format_date(iso_str: str) -> str:
    """Format ISO date to YYYY-MM-DD."""
    if not iso_str:
        return "-"
    return iso_str[:10]

def format_ticket_summary(issues: list[dict]) -> str:
    """Format list of issues as summary, sorted by status."""
    if not issues:
        return "  No tickets found."

    # Status priority order
    status_order = {
        "In Progress": 0, "In TEST": 1, "In PROD": 2, "Open": 3,
        "To Do": 4, "Waiting": 5, "Breakdown": 6
    }

    def sort_key(issue):
        status = issue.get("fields", {}).get("status", {}).get("name", "zzz")
        return (status_order.get(status, 99), issue.get("key"))

    lines = []
    current_status = None
    for issue in sorted(issues, key=sort_key):
        key = issue.get("key")
        fields = issue.get("fields", {})
        summary = fields.get("summary", "")[:80]
        status = fields.get("status", {}).get("name", "-")

        if status != current_status:
            if current_status is not None:
                lines.append("")
            lines.append(f"### {status}")
            current_status = status

        lines.append(f"{key:<10} | {summary}")

    return "\n".join(lines)

def format_ticket_detail(issue: dict) -> str:
    """Format single ticket with full detail."""
    key = issue.get("key")
    fields = issue.get("fields", {})

    lines = []
    lines.append(f"# {key}: {fields.get('summary', '')}")
    lines.append("")
    lines.append(f"**Status:** {fields.get('status', {}).get('name', '-')}")
    lines.append(f"**Type:** {fields.get('issuetype', {}).get('name', '-')}")
    lines.append(f"**Reporter:** {fields.get('reporter', {}).get('displayName', '-')}")
    lines.append(f"**Assignee:** {fields.get('assignee', {}).get('displayName', '-')}")
    lines.append(f"**Created:** {format_date(fields.get('created'))}")
    lines.append(f"**Updated:** {format_date(fields.get('updated'))}")

    resolution = fields.get("resolution")
    if resolution:
        lines.append(f"**Resolution:** {resolution.get('name', '-')}")
        lines.append(f"**Resolved:** {format_date(fields.get('resolutiondate'))}")

    components = fields.get("components", [])
    if components:
        comp_names = [c.get("name") for c in components]
        lines.append(f"**Components:** {', '.join(comp_names)}")

    lines.append("")
    lines.append("## Description")
    lines.append(fields.get("description") or "_No description_")

    comments = fields.get("comment", {}).get("comments", [])
    if comments:
        lines.append("")
        lines.append(f"## Comments ({len(comments)})")
        for c in comments:
            author = c.get("author", {}).get("displayName", "Unknown")
            date = format_date(c.get("created"))
            body = c.get("body", "")
            lines.append(f"\n**{author}** ({date}):")
            lines.append(body)

    return "\n".join(lines)

def full_report() -> str:
    """Generate full Jira status report."""
    report = []
    report.append("# Jira Report: IDR/DDS")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("")

    report.append("## Open Tickets")
    open_tickets = get_my_open_tickets()
    report.append(format_ticket_summary(open_tickets))
    report.append("")

    report.append("## Recently Closed (30 days)")
    closed = get_recent_closed(30)
    report.append(format_ticket_summary(closed))

    return "\n".join(report)

def format_search_results(issues: list[dict]) -> str:
    """Format search results with project, key, status, and summary."""
    if not issues:
        return "No results found."

    lines = []
    lines.append(f"Found {len(issues)} result(s):")
    lines.append("")

    for issue in issues:
        key = issue.get("key", "?")
        fields = issue.get("fields", {})
        summary = fields.get("summary", "")[:70]
        status = fields.get("status", {}).get("name", "-")
        itype = fields.get("issuetype", {}).get("name", "-")

        lines.append(f"{key:<12} [{status:<12}] {itype:<12} {summary}")

    return "\n".join(lines)

def is_ticket_key(s: str) -> bool:
    """Check if string looks like a Jira ticket key (PROJECT-123)."""
    import re
    return bool(re.match(r'^[A-Z]+-\d+$', s.upper()))


def print_usage():
    """Print CLI usage help."""
    print("""Jira CLI - UO IDR/DDS ticket management

Usage:
  jira.py                           Show open tickets report (default)
  jira.py <KEY>                     Show ticket detail (e.g., IDR-3770, MAD-123)
  jira.py <KEY> attachments         List attachments on ticket
  jira.py <KEY> attachment <file>   Download attachment to current directory
  jira.py search "<JQL>"            Search issues with JQL query
  jira.py comment <KEY> "<text>"    Add comment to ticket

Examples:
  jira.py IDR-3770
  jira.py IDR-3770 attachments
  jira.py IDR-3770 attachment query.sql
  jira.py search 'text ~ "first generation"'
  jira.py search 'project in (IDR, MAD, MADSD) AND text ~ "ODS"'
  jira.py comment IDR-3770 "Investigation complete, see notes."
""")


if __name__ == "__main__":
    import sys

    args = sys.argv[1:]

    if not args:
        # Default: show full report
        print(full_report())

    elif args[0].lower() == "help" or args[0] == "-h" or args[0] == "--help":
        print_usage()

    elif args[0].lower() == "search":
        # Search: jira.py search "JQL"
        if len(args) < 2:
            print("Error: search requires a JQL query")
            print("Example: jira.py search 'text ~ \"first generation\"'")
            sys.exit(1)
        jql = args[1]
        fields = ["key", "summary", "status", "issuetype"]
        issues = search_issues(jql, fields, max_results=50)
        print(format_search_results(issues))

    elif args[0].lower() == "comment":
        # Comment: jira.py comment IDR-XXXX "text"
        if len(args) < 3:
            print("Error: comment requires ticket key and comment text")
            print("Example: jira.py comment IDR-3770 \"Comment text here\"")
            sys.exit(1)
        key = args[1].upper()
        body = args[2]
        add_comment(key, body)
        print(f"Comment added to {key}")

    elif is_ticket_key(args[0]):
        key = args[0].upper()

        if len(args) == 1:
            # Just the key: show detail
            issue = get_ticket_detail(key)
            print(format_ticket_detail(issue))

        elif args[1].lower() == "attachments":
            # List attachments: jira.py IDR-XXXX attachments
            attachments = get_attachments(key)
            print(f"Attachments for {key}:")
            print(format_attachments(attachments))

        elif args[1].lower() == "attachment":
            # Download attachment: jira.py IDR-XXXX attachment <filename>
            if len(args) < 3:
                print("Error: specify filename to download")
                print(f"Example: jira.py {key} attachment query.sql")
                sys.exit(1)
            filename = args[2]
            try:
                path = download_attachment(key, filename)
                print(f"Downloaded: {path}")
            except ValueError as e:
                print(f"Error: {e}")
                sys.exit(1)

        else:
            print(f"Unknown subcommand: {args[1]}")
            print_usage()
            sys.exit(1)

    else:
        print(f"Unknown command: {args[0]}")
        print_usage()
        sys.exit(1)
