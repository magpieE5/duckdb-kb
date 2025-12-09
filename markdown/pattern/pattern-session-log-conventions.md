---
id: pattern-session-log-conventions
category: pattern
title: Session Log Conventions
tags: []
---

**How to use `log_session` tool correctly. The tool adds structure - pass content only, not headers. Preview is critical for searchability.**

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

## Preview Requirement

**Every conversation_dump MUST start with a ~400 character dense preview.** This is what `scan_knowledge` searches and what `/kbo` loads as preview.

```
**Preview:** [DATE] [MODE]. [2-3 sentence summary]. Key: [terms].

---

[Rest of conversation content...]
```

**Preview content should include:**
- Date and mode (interactive, auto, mixed)
- Main topics/work done (2-3 sentences max)
- Key terms for later identification
- Notable outcomes, corrections, or decisions

**Why this matters:** Preview-based search finds entries by their curated summary. A good preview makes the session findable; a weak preview makes it dark.

---

## Tags

Tags are optional. Use `["session", "session-N"]` as baseline. Add topic tags if useful for structured queries, but preview search handles findability.

Exception: `never-forget` tag has special behavior (auto-loads full content via /kbs).

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
