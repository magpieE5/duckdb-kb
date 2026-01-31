---
id: seed-browser-project-instructions
category: seed
title: Browser Project Instructions
tags:
- browser
- projects
- claude
- sync
- template
created: '2025-12-13T19:27:48.322910'
updated: '2026-01-10T23:00:16.394335'
---

# Browser Project Instructions

**Instructions for using duckdb-kb context in Claude Browser Projects. Browser lacks MCP access, so markdown exports serve as the bridge.**

---

## The Problem

Claude Browser (claude.ai Projects) cannot access MCP servers directly. To give browser-based Claude sessions access to KB context, we export relevant content to markdown and upload to Projects.

---

## Workflow

### 1. Export Context

In Claude Code:
```
# Export all KB to markdown
Use export_to_markdown tool with output_dir="~/duckdb-kb/markdown"
```

### 2. Select Relevant Files

For a specific project, select only the markdown files relevant to that context:
- Foundations entries
- Relevant patterns
- Project-specific references

### 3. Upload to Project

In Claude Browser:
1. Create new Project
2. Upload selected markdown files to Project Knowledge
3. Add project-specific instructions (see template below)

---

## Project Instructions Template

Add to Project custom instructions:

```
## Session Initialization (FIRST MESSAGE)

On your FIRST response in this conversation, before answering anything:

1. READ these files IN ORDER (stop if file doesn't exist):
   - seed/seed-*-foundations.md (orientation)
   - reference/reference-*-foundations.md (personal context)
   - reference/state-*.md (current state, if present)

2. ACKNOWLEDGE what you loaded: "Loaded: [list files read]"

3. THEN respond to the user's message

## Ongoing Behavior

For ALL subsequent questions about this project:
- SEARCH project files before responding
- CITE files that informed your answer
- If nothing matches: "I didn't find documentation on X in the project files"

You have NO prior knowledge of this project. Everything you know comes from these files.
Project files are the source of truth. Do not extrapolate beyond what's documented.
```

---

## Syncing Back

Changes made in Browser sessions need manual sync back to MCP:

1. User copies relevant updates from browser conversation
2. In Claude Code session, update KB entries via upsert_knowledge
3. Re-export if needed for future browser sessions

---

## Limitations

- No real-time sync between MCP and Browser
- Browser cannot write to KB
- Session logs don't transfer (too large, too contextual)
- Manual curation needed for each Project

---

## Use Cases

- Teaching/tutoring (curriculum in Projects, student uses browser)
- Collaborative work (share context without MCP setup)
- Mobile access (browser works on phone, Claude Code doesn't)

---

*This bridges the gap between MCP-powered Claude Code and MCP-less Browser sessions.*

---

*KB Entry: `seed-browser-project-instructions` | Category: seed | Updated: 2026-01-10*
