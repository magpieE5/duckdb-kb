#!/usr/bin/env python3
"""
Extract verbatim exchanges from conversation files.
Supports Claude Code (JSONL) and Gemini CLI (JSON) formats.
Outputs formatted markdown for upsert via MCP tool.

Usage: extract_exchanges.py <session_file> <session_number> [max_exchanges]

Output: JSON with id, title, content for use with upsert_knowledge MCP tool.
"""

import json
import re
import sys
from pathlib import Path


# === CONTENT SUPPRESSION ===

def suppress_structured_content(text: str) -> str:
    """
    Mechanically suppress structured content to reduce transcript size.
    Replaces patterns with [TYPE: n unit] markers. No AI summarization.

    Suppressed: code blocks, JSON, XML, stack traces, diffs, long lists, base64
    Kept verbatim: natural language, SQL/table output, file listings
    """

    # 1. Code blocks: ```lang\n...```
    def replace_code_block(match):
        lang = match.group(1) or ''
        code = match.group(2)
        lines = len(code.strip().split('\n')) if code.strip() else 0
        lang_note = f" {lang}" if lang else ""
        return f"[CODE:{lang_note} {lines} lines]"

    text = re.sub(r'```(\w*)\n(.*?)```', replace_code_block, text, flags=re.DOTALL)

    # 2. JSON blobs: multiline content starting with { or [ with "key": patterns
    def replace_json(match):
        content = match.group(0)
        lines = len(content.strip().split('\n'))
        return f"[JSON: {lines} lines]"

    # Match { or [ at line start, with quoted keys, spanning multiple lines
    json_pattern = r'^\s*[\{\[]\s*\n(?:.*?"[^"]+"\s*:.*?\n)+\s*[\}\]]'
    text = re.sub(json_pattern, replace_json, text, flags=re.MULTILINE)

    # Simpler JSON: single objects/arrays with quotes and colons, 3+ lines
    def replace_simple_json(match):
        content = match.group(0)
        lines = len(content.strip().split('\n'))
        if lines >= 3:
            return f"[JSON: {lines} lines]"
        return content

    simple_json = r'\{[^{}]*"[^"]+"\s*:[^{}]+\}'
    text = re.sub(simple_json, replace_simple_json, text, flags=re.DOTALL)

    # 3. XML content: <tag>...</tag> spanning multiple lines
    def replace_xml(match):
        content = match.group(0)
        lines = len(content.strip().split('\n'))
        if lines >= 3:
            return f"[XML: {lines} lines]"
        return content

    xml_pattern = r'<(\w+)[^>]*>.*?</\1>'
    text = re.sub(xml_pattern, replace_xml, text, flags=re.DOTALL)

    # 4. Stack traces: Traceback or Error patterns with file/line refs
    def replace_stacktrace(match):
        content = match.group(0)
        lines = len(content.strip().split('\n'))
        return f"[STACKTRACE: {lines} lines]"

    # Python-style traceback
    stacktrace_pattern = r'Traceback \(most recent call last\):.*?(?=\n\n|\n[A-Z]|\Z)'
    text = re.sub(stacktrace_pattern, replace_stacktrace, text, flags=re.DOTALL)

    # Generic error with file:line patterns
    error_pattern = r'(?:Error|Exception).*?(?:at |in |File ").*?(?:\n\s+.*?){2,}'
    text = re.sub(error_pattern, replace_stacktrace, text, flags=re.DOTALL)

    # 5. Diff output: lines starting with +/- or @@ hunks
    def replace_diff(match):
        content = match.group(0)
        lines = len(content.strip().split('\n'))
        return f"[DIFF: {lines} lines]"

    # @@ hunk headers followed by +/- lines
    diff_pattern = r'@@[^@]+@@.*?(?=\n@@|\n\n|\n[^-+\s]|\Z)'
    text = re.sub(diff_pattern, replace_diff, text, flags=re.DOTALL)

    # Unified diff without @@ (just +/- blocks)
    plusminus_pattern = r'(?:^[-+].*\n){5,}'
    text = re.sub(plusminus_pattern, replace_diff, text, flags=re.MULTILINE)

    # 6. Long lists: >10 consecutive bullet or numbered items
    def replace_long_list(match):
        content = match.group(0)
        items = len(re.findall(r'^\s*(?:[-*]|\d+\.)\s+', content, re.MULTILINE))
        return f"[LIST: {items} items]"

    # Bullet lists (-, *)
    bullet_pattern = r'(?:^\s*[-*]\s+.+\n){11,}'
    text = re.sub(bullet_pattern, replace_long_list, text, flags=re.MULTILINE)

    # Numbered lists
    numbered_pattern = r'(?:^\s*\d+\.\s+.+\n){11,}'
    text = re.sub(numbered_pattern, replace_long_list, text, flags=re.MULTILINE)

    # 7. Base64/binary: long alphanumeric strings without spaces (>100 chars)
    def replace_binary(match):
        content = match.group(0)
        return f"[BINARY: {len(content)} chars]"

    binary_pattern = r'(?<![a-zA-Z0-9/+])[A-Za-z0-9+/=]{100,}(?![a-zA-Z0-9/+=])'
    text = re.sub(binary_pattern, replace_binary, text)

    # 8. Collapse multiple blank lines to one
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text


def detect_format(file_path: Path) -> str:
    """Detect file format: 'claude' (JSONL) or 'gemini' (JSON object)."""
    with open(file_path) as f:
        content = f.read()

    try:
        data = json.loads(content)
        if isinstance(data, dict) and 'sessionId' in data:
            return 'gemini'
    except json.JSONDecodeError:
        pass

    if content.strip().startswith('{'):
        return 'claude'

    raise ValueError("Unknown or malformed session file format")


# === CLAUDE CODE EXTRACTION ===

def get_user_text_claude(msg: dict) -> str | None:
    """Extract user text from Claude message, filtering out noise."""
    content = msg.get("message", {})

    if "content" in content:
        c = content["content"]

        if isinstance(c, str):
            if "<command-message>" in c:
                match = re.search(r"<command-message>(.+?)</command-message>", c)
                if match:
                    return f"/{match.group(1)}"
                return None
            return c

        if isinstance(c, list):
            for item in c:
                if isinstance(item, dict):
                    if item.get("type") == "tool_result":
                        return None
                    if item.get("type") == "text":
                        text = item.get("text", "")
                        if text.strip().startswith("# /"):
                            return None
                        return text

    if content.get("type") == "tool_result":
        return None

    if content.get("type") == "text":
        return content.get("text")

    return None


def extract_exchanges_claude(file_path: Path) -> list[dict]:
    """Extract exchanges from Claude JSONL file."""
    messages = []

    with open(file_path) as f:
        for line in f:
            msg = json.loads(line)
            if msg.get("type") in ("user", "assistant"):
                messages.append(msg)

    exchanges = []
    current_exchange = {"thinking": [], "said": [], "user": None}

    for msg in messages:
        if msg["type"] == "user":
            user_text = get_user_text_claude(msg)
            if user_text:
                if current_exchange["thinking"] or current_exchange["said"]:
                    exchanges.append(current_exchange)
                    current_exchange = {"thinking": [], "said": [], "user": None}
                current_exchange["user"] = user_text

        elif msg["type"] == "assistant":
            content = msg.get("message", {}).get("content", [])
            if isinstance(content, list):
                for block in content:
                    if block.get("type") == "thinking":
                        current_exchange["thinking"].append(block.get("thinking", ""))
                    elif block.get("type") == "text":
                        current_exchange["said"].append(block.get("text", ""))

    if current_exchange["thinking"] or current_exchange["said"] or current_exchange["user"]:
        exchanges.append(current_exchange)

    return exchanges


# === GEMINI CLI EXTRACTION ===

def extract_exchanges_gemini(file_path: Path) -> list[dict]:
    """Extract exchanges from Gemini JSON file."""
    with open(file_path) as f:
        data = json.load(f)

    messages = data.get("messages", [])

    if not isinstance(messages, list):
        raise ValueError("Gemini file should have a 'messages' key with a JSON array")

    exchanges = []
    current_exchange = {"thinking": [], "said": [], "user": None}

    for msg in messages:
        role = msg.get("type")
        text = msg.get("content")

        if role == "user" and text:
            if current_exchange["said"]:
                exchanges.append(current_exchange)
                current_exchange = {"thinking": [], "said": [], "user": None}
            current_exchange["user"] = text

        elif role == "gemini" and text:
            current_exchange["said"].append(text)

    if current_exchange["said"] or current_exchange["user"]:
        exchanges.append(current_exchange)

    return exchanges


# === COMMON ===

def extract_exchanges(file_path: Path) -> list[dict]:
    """Auto-detect format and extract exchanges."""
    fmt = detect_format(file_path)

    if fmt == 'claude':
        return extract_exchanges_claude(file_path)
    elif fmt == 'gemini':
        return extract_exchanges_gemini(file_path)
    else:
        raise ValueError(f"Unknown format: {fmt}")


def format_exchanges(exchanges: list[dict], max_exchanges: int = None, suppress: bool = True) -> str:
    """Format exchanges as markdown content.

    Args:
        exchanges: List of exchange dicts with user/thinking/said keys
        max_exchanges: Limit number of exchanges (None = all)
        suppress: Apply structured content suppression (default True)
    """
    output = ["## Exchanges\n"]

    for i, ex in enumerate(exchanges[:max_exchanges], 1):
        output.append(f"### {i}\n")

        if ex["user"]:
            user_text = suppress_structured_content(ex['user']) if suppress else ex['user']
            output.append(f"**User:**\n{user_text}\n")

        if ex["thinking"]:
            thinking = "\n\n".join(ex["thinking"])
            if suppress:
                thinking = suppress_structured_content(thinking)
            output.append(f"**Thinking:**\n{thinking}\n")

        if ex["said"]:
            said = "\n\n".join(ex["said"])
            if suppress:
                said = suppress_structured_content(said)
            output.append(f"**Said:**\n{said}\n")

        output.append("---\n")

    return "\n".join(output)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: extract_exchanges.py <session_file> <session_number> [max_exchanges] [--no-suppress]", file=sys.stderr)
        print("  Outputs JSON for upsert_knowledge MCP tool", file=sys.stderr)
        print("  --no-suppress: Keep all content verbatim (no structured content suppression)", file=sys.stderr)
        sys.exit(1)

    # Parse args
    args = sys.argv[1:]
    no_suppress = "--no-suppress" in args
    if no_suppress:
        args.remove("--no-suppress")

    session_path = Path(args[0])
    session_num = int(args[1])
    max_ex = int(args[2]) if len(args) > 2 else None

    fmt = detect_format(session_path)
    print(f"Detected format: {fmt}", file=sys.stderr)

    exchanges = extract_exchanges(session_path)
    print(f"Extracted {len(exchanges)} exchanges", file=sys.stderr)
    if not no_suppress:
        print("Suppressing structured content (code, JSON, XML, etc.)", file=sys.stderr)

    content = format_exchanges(exchanges, max_ex, suppress=not no_suppress)

    # Output JSON for MCP upsert_knowledge tool
    result = {
        "id": f"transcript-{session_num:03d}",
        "category": "transcript",
        "title": f"Session {session_num} Transcript",
        "tags": ["transcript", f"session-{session_num}"],
        "content": content
    }

    print(json.dumps(result))
