"""Convert markdown drafts to PDF using weasyprint."""
from typing import List
from pathlib import Path
import markdown
from weasyprint import HTML, CSS
from mcp.types import Tool, TextContent

from .base import text_response

try:
    from .session_details import DRAFTS_DIR
except ImportError:
    from session_details import DRAFTS_DIR

TOOL_DEF = Tool(
    name="drafts_to_pdf",
    description="Convert markdown files in drafts/ to PDF. Lists available drafts if no file specified.",
    inputSchema={
        "type": "object",
        "properties": {
            "file": {
                "type": "string",
                "description": "Filename to convert (e.g., 'report.md'), 'all' for all files, or omit to list available drafts"
            }
        },
        "required": []
    }
)

REQUIRES_DB = False

# Clean, professional CSS for PDF output
PDF_CSS = """
@page {
    size: letter;
    margin: 1in;
}
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    font-size: 11pt;
    line-height: 1.5;
    color: #333;
}
h1 {
    font-size: 24pt;
    font-weight: 600;
    margin-top: 0;
    margin-bottom: 0.5em;
    color: #111;
    border-bottom: 2px solid #333;
    padding-bottom: 0.3em;
}
h2 {
    font-size: 18pt;
    font-weight: 600;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
    color: #222;
}
h3 {
    font-size: 14pt;
    font-weight: 600;
    margin-top: 1.2em;
    margin-bottom: 0.4em;
    color: #333;
}
p {
    margin: 0.8em 0;
}
ul, ol {
    margin: 0.8em 0;
    padding-left: 1.5em;
}
li {
    margin: 0.3em 0;
}
code {
    font-family: "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", Consolas, monospace;
    font-size: 10pt;
    background: #f5f5f5;
    padding: 0.1em 0.3em;
    border-radius: 3px;
}
pre {
    font-family: "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", Consolas, monospace;
    font-size: 9pt;
    background: #f5f5f5;
    padding: 1em;
    border-radius: 5px;
    overflow-x: auto;
    line-height: 1.4;
}
pre code {
    background: none;
    padding: 0;
}
blockquote {
    border-left: 4px solid #ddd;
    margin: 1em 0;
    padding-left: 1em;
    color: #666;
}
table {
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
}
th, td {
    border: 1px solid #ddd;
    padding: 0.5em;
    text-align: left;
}
th {
    background: #f5f5f5;
    font-weight: 600;
}
hr {
    border: none;
    border-top: 1px solid #ddd;
    margin: 2em 0;
}
a {
    color: #0066cc;
    text-decoration: none;
}
strong {
    font-weight: 600;
}
"""


def list_drafts() -> List[str]:
    """List all markdown files in drafts directory."""
    if not DRAFTS_DIR.exists():
        return []
    return sorted([f.name for f in DRAFTS_DIR.glob("*.md")])


def convert_to_pdf(md_file: Path) -> Path:
    """Convert a markdown file to PDF, return output path."""
    content = md_file.read_text(encoding="utf-8")

    # Convert markdown to HTML
    md = markdown.Markdown(extensions=["tables", "fenced_code", "toc"])
    html_content = md.convert(content)

    # Wrap in HTML document
    html_doc = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{md_file.stem}</title>
</head>
<body>
{html_content}
</body>
</html>"""

    # Generate PDF
    pdf_path = md_file.with_suffix(".pdf")
    HTML(string=html_doc).write_pdf(pdf_path, stylesheets=[CSS(string=PDF_CSS)])

    return pdf_path


async def execute(con, args: dict) -> List[TextContent]:
    file_arg = args.get("file")

    # List mode - no file specified
    if not file_arg:
        drafts = list_drafts()
        if not drafts:
            return text_response(f"No markdown files in {DRAFTS_DIR}")

        listing = "Available drafts:\n" + "\n".join(f"  - {d}" for d in drafts)
        listing += f"\n\nUse file='filename.md' to convert, or file='all' for all"
        return text_response(listing)

    # Convert all
    if file_arg.lower() == "all":
        drafts = list_drafts()
        if not drafts:
            return text_response(f"No markdown files in {DRAFTS_DIR}")

        results = []
        for draft in drafts:
            md_path = DRAFTS_DIR / draft
            try:
                pdf_path = convert_to_pdf(md_path)
                results.append(f"✓ {draft} → {pdf_path.name}")
            except Exception as e:
                results.append(f"✗ {draft}: {str(e)}")

        return text_response(f"Converted {len(drafts)} files:\n" + "\n".join(results))

    # Convert single file
    md_path = DRAFTS_DIR / file_arg
    if not md_path.exists():
        # Try adding .md if not present
        if not file_arg.endswith(".md"):
            md_path = DRAFTS_DIR / f"{file_arg}.md"

    if not md_path.exists():
        return text_response(f"File not found: {md_path}\n\nAvailable: {', '.join(list_drafts())}")

    try:
        pdf_path = convert_to_pdf(md_path)
        return text_response(f"Created: {pdf_path}")
    except Exception as e:
        return text_response(f"Error converting {md_path.name}: {str(e)}")
