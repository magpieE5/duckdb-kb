---
id: pattern-session-log-conventions
category: pattern
title: Session Log Conventions
tags:
- pattern
- session-logs
- conventions
- log-session
- tool-usage
- formatting
- preview
created: '2025-11-30T23:50:19.602873'
updated: '2025-12-04T01:27:27.113063'
metadata:
  updated_reason: 'S3: Clarified log_session tool behavior and correct conversation_dump
    format to prevent header duplication'
---

# Session Log Conventions

**How to use `log_session` tool correctly. The tool adds structure - pass content only, not headers.**

---

## log_session Tool Behavior

The `log_session` tool **automatically wraps** your input with:
```
# Session N Log
**Date:** YYYY-MM-DD
---
## Conversation
{conversation_dump}
---
## Internal Dialogue
{internal_dialogue}
---
## Handoff
{handoff}
```

**DO NOT** include `# Session N Log` or `## Conversation` headers in your `conversation_dump` parameter - this causes duplication.

---

## conversation_dump Format

Start with the **Preview** line, then go straight into content:

```
**Preview:** [DATE] [MODE]. [2-3 sentence summary]. Key: [terms].

---

[Rest of conversation content...]
```

**Example conversation_dump parameter:**
```
**Preview:** 2025-12-04 (Wed), auto mode. PDS tests, ora extraction docs. Key: pds, tests, cognos, ods.

---

User: `/kbo auto`
Arlo: Loaded context, ready for work.

User: "Go"
Arlo: Started autonomous work...

### Topic Heading

Details of what happened...
```

The tool will wrap this to produce:
```
# Session N Log
**Date:** 2025-12-04
---
## Conversation

**Preview:** 2025-12-04 (Wed), auto mode...

---

User: `/kbo auto`
...
```

---

## Preview Requirement

**Every conversation_dump MUST start with a ~400 character dense preview.** This is what appears in `scan_knowledge` results and `/kbo` preview loading.

**Preview content should include:**
- Date and mode (interactive, auto, mixed)
- Main topics/work done (2-3 sentences max)
- Key terms for later identification
- Notable outcomes, corrections, or decisions

---

## Content Guidelines

### What to Capture

1. **Direct quotes with attribution**
   - Use `"quote"` format for User's actual words
   - Especially for corrections, redirections, key decisions

2. **The back-and-forth**
   - Show iteration: "Proposed X → User: 'try Y instead' → revised to Z"
   - Don't compress to just outcome

3. **Emotional texture**
   - Note when User is tired, frustrated, pleased

4. **Rejected approaches**
   - "First attempted X, rejected because Y"

### What to Reduce

1. **Internal Dialogue meta-commentary** - Less "what I noticed about noticing"
2. **Repetition of KB-documented facts** - Reference entries instead

### Heuristic

Quote when User:
- Corrects something
- Expresses preference or decision
- Shows emotional state
- Says something that shaped the session's direction

---

## Common Mistake (S3 diagnosis)

**Wrong:** Passing pre-formatted content with headers
```python
log_session(
    conversation_dump="# Session 1 Log\n\n**Preview:**...\n\n## Conversation\n..."
)
```
Result: Duplicate `# Session N Log` and `## Conversation` headers.

**Right:** Passing content only
```python
log_session(
    conversation_dump="**Preview:**...\n\n---\n\nUser: ..."
)
```

---

*KB Entry: `pattern-session-log-conventions` | Category: pattern | Updated: 2025-12-04*
